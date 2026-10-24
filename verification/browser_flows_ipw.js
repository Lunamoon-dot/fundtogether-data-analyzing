async page => {
  const scenario="__SCENARIO__",output="__OUTPUT_DIR__",base="__BASE_URL__",steps=[],errors=[],network=[];
  page.on("pageerror",error=>errors.push(error.message));
  page.on("request",request=>network.push({url:request.url(),method:request.method()}));
  const check=(condition,message,observed)=>{steps.push({step:message,status:condition?"pass":"fail",observed});if(!condition)throw new Error(message+": "+JSON.stringify(observed));};
  const shot=async name=>page.screenshot({path:output+"/"+name+".png",fullPage:false});
  const read=async path=>{const response=await page.request.get(base+path);if(response.status()!==200)throw new Error("GET "+path+": "+response.status());return response.json();};
  try {
    if(scenario!=="IPW-B01")throw new Error("Unknown IPW browser scenario: "+scenario);
    await page.setViewportSize({width:1366,height:768});
    await page.goto(base);
    await page.locator("#connection").filter({hasText:"Engine sẵn sàng"}).waitFor();
    await page.locator("#model-version").selectOption("ceav-m1-v3.3");
    check(await page.locator("#model-version").inputValue()==="ceav-m1-v3.3","UI selects the V3.3 model",await page.locator("#model-version").inputValue());
    check(await page.locator("#mechanism").inputValue()==="hybrid_anchor","V3.3 keeps the hybrid mechanism",await page.locator("#mechanism").inputValue());
    const q0=await page.locator("#field-verification-anchor-audit-probability-by-report-0").inputValue();
    const q1=await page.locator("#field-verification-anchor-audit-probability-by-report-1").inputValue();
    const budget=await page.locator("#field-reward-budget").inputValue();
    check(q0==="1/4"&&q1==="3/4"&&budget==="24","V3.3 input shows q0, q1 and shared reward budget",{q0,q1,budget});
    await page.locator('[data-view="ipw"]').click();
    await page.locator("#ipw-study").selectOption("full");
    check((await page.locator('[data-panel="ipw"]').innerText()).includes("54 point"),"IPW full study advertises 54 points",await page.locator('[data-panel="ipw"]').innerText());
    const listing=await read("/api/runs");
    const existing=(listing.runs||[]).filter(run=>run.operation==="ipw"&&run.status==="succeeded"&&run.model_version==="ceav-m1-v3.3").sort((left,right)=>String(right.created_at_utc).localeCompare(String(left.created_at_utc)))[0];
    let job,manifest,reused=false;
    if(existing){
      reused=true;
      await page.locator('[data-view="history"]').click();
      await page.waitForFunction(id=>document.querySelector("#history-result")?.innerText.includes(id),existing.run_id,{timeout:30000});
      await page.locator(`[data-open-run="${existing.run_id}"]`).click();
      await page.waitForFunction(id=>document.querySelector("#ipw-result")?.dataset.runId===id,existing.run_id,{timeout:30000});
      job={run_id:existing.run_id};
      steps.push({step:"UI reopened a succeeded full IPW worker run",status:"pass",observed:{run_id:existing.run_id,created_at_utc:existing.created_at_utc}});
    }else{
      const pending=page.waitForResponse(r=>r.url()===base+"/api/runs"&&r.request().method()==="POST");
      await page.locator('[data-operation="ipw"]').click();
      const response=await pending;
      check(response.status()===202,"UI submitted IPW study",response.status());
      job=await response.json();
      await page.waitForFunction(id=>document.querySelector("#run-metadata").textContent.includes(id),job.run_id,{timeout:1800000});
      await page.waitForFunction(id=>document.querySelector("#ipw-result")?.dataset.runId===id,job.run_id,{timeout:1800000});
    }
    manifest=await read("/api/runs/"+job.run_id);
    check(manifest.status==="succeeded","IPW worker reached succeeded",manifest.status);
    const artifact=await read("/api/runs/"+job.run_id+"/artifacts/ipw.json");
    check(artifact.model_version==="ceav-m1-v3.3"&&artifact.grid.total_points===54&&artifact.grid.policy_count===3&&artifact.grid.scenario_count_per_policy===18,"Worker artifact is the declared 3×18 V3.3 study",artifact.grid);
    check(artifact.points.length===54&&artifact.points.every(point=>point.branch_candidate_count===432&&point.enumeration_completed),"All 54 points completed exhaustive 432-candidate search",{points:artifact.points.length,complete:artifact.points.every(point=>point.enumeration_completed),counts:[...new Set(artifact.points.map(point=>point.branch_candidate_count))]});
    check(artifact.policies.every(policy=>policy.point_count===18&&policy.pass_count===0&&policy.robust===false),"Artifact preserves exact 0/18 policy results",artifact.policies.map(policy=>({id:policy.policy_id,pass:policy.pass_count,total:policy.point_count,robust:policy.robust})));
    const first=artifact.points[0],config=first.config,anchor=config.verification_anchor,diagnostic=first.equilibrium_diagnostics[0],policy=artifact.policies[0];
    const qMin=(Number(anchor.audit_probability_by_report["0"].split("/")[0])/Number(anchor.audit_probability_by_report["0"].split("/")[1]))<(Number(anchor.audit_probability_by_report["1"].split("/")[0])/Number(anchor.audit_probability_by_report["1"].split("/")[1]))?anchor.audit_probability_by_report["0"]:anchor.audit_probability_by_report["1"];
    const ui=await page.locator("#ipw-result").innerText();
    check(ui.includes(anchor.audit_probability_by_report["0"])&&ui.includes(anchor.audit_probability_by_report["1"])&&ui.includes(qMin)&&ui.includes(anchor.audit_reward_mode)&&ui.includes(config.reward_budget),"UI displays q0, q1, q_min, IPW mode and reward budget from artifact",ui.slice(0,2200));
    for(const metric of [diagnostic.report_one_rate[0],policy.worst.false_approval_rate,policy.worst.wrong_payout_value,diagnostic.anchor_reward_variance[0]]) check(ui.includes(metric.exact),"UI matches artifact exact metric "+metric.exact,metric);
    const witness=first.failure_witnesses[0];
    check(witness&&ui.includes(witness.witness.delta_utility.exact),"UI exposes an artifact failure witness",{judge:witness.judge,point_id:witness.point_id,delta_utility:witness.witness.delta_utility});
    await page.locator("#ipw-result details").click();
    const expandedUI=await page.locator("#ipw-result").innerText();
    const panelText=await page.locator('[data-panel="ipw"]').innerText();
    check(panelText.includes("Synthetic/assumption")&&expandedUI.includes("grid_only_no_interpolation"),"UI preserves the synthetic/assumption and grid-only disclaimer",expandedUI.slice(-1600));
    await shot("ipw-full-study");
    check(errors.length===0,"No JavaScript runtime errors",errors);
    return {scenario,status:"passed",browser:page.context().browser().version(),viewport:page.viewportSize(),steps,network,errors,runs:{ipw:job.run_id,reused},artifact:{total_points:artifact.grid.total_points,policy_results:artifact.policies.map(policy=>({policy_id:policy.policy_id,pass_count:policy.pass_count,point_count:policy.point_count,robust:policy.robust})),q0:anchor.audit_probability_by_report["0"],q1:anchor.audit_probability_by_report["1"],q_min:qMin}};
  } catch(error) {
    return {scenario,status:"failed",browser:page.context().browser().version(),viewport:page.viewportSize(),steps,error:error.stack,network,errors};
  }
}
