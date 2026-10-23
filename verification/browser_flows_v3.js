async page => {
  const scenario="__SCENARIO__",output="__OUTPUT_DIR__",base="__BASE_URL__",steps=[],errors=[],network=[];
  page.on("pageerror",error=>errors.push(error.message));
  page.on("request",request=>network.push({url:request.url(),method:request.method()}));
  const check=(condition,message,observed)=>{steps.push({step:message,status:condition?"pass":"fail",observed});if(!condition)throw new Error(message+": "+JSON.stringify(observed));};
  const shot=async name=>page.screenshot({path:output+"/"+name+".png",fullPage:false});
  const read=async path=>{const response=await page.request.get(base+path);if(response.status()!==200)throw new Error("GET "+path+": "+response.status());return response.json();};
  const runUI=async (operation,timeout=90000)=>{
    const pending=page.waitForResponse(r=>r.url()===base+"/api/runs"&&r.request().method()==="POST");
    await page.locator(`[data-operation="${operation}"]`).click();
    const response=await pending;
    check(response.status()===202,"UI submitted "+operation,response.status());
    const job=await response.json();
    await page.waitForFunction(id=>document.querySelector("#run-metadata").textContent.includes(id),job.run_id,{timeout});
    await page.waitForFunction(({id,operation})=>document.querySelector("#"+operation+"-result")?.dataset.runId===id,{id:job.run_id,operation},{timeout});
    const manifest=await read("/api/runs/"+job.run_id);
    check(manifest.status==="succeeded",operation+" reached succeeded",manifest.status);
    return {job,manifest};
  };
  try {
    if(scenario!=="V3-B01")throw new Error("Unknown V3 browser scenario: "+scenario);
    await page.setViewportSize({width:1366,height:768});
    await page.goto(base);
    await page.locator("#connection").filter({hasText:"Engine sẵn sàng"}).waitFor();
    check(await page.locator("#model-version").inputValue()==="ceav-m1-v3.0","New form defaults to V3",await page.locator("#model-version").inputValue());
    check(await page.locator("#mechanism").inputValue()==="hybrid_anchor","V3 locks the hybrid mechanism",await page.locator("#mechanism").inputValue());
    const groups=await page.locator("#model-fields .model-group").evaluateAll(items=>items.map(item=>({title:item.querySelector("legend")?.textContent,fields:[...item.querySelectorAll("[data-field]")].map(field=>field.dataset.field)})));
    check(groups.length===5&&groups[4].title.includes("Verification anchor")&&groups[4].fields.length===4,"V3 separates public, private and post-report verification inputs",groups);
    check(await page.locator("#field-verification-anchor-audit-probability").inputValue()==="1/5"&&await page.locator("#field-verification-anchor-cost-per-audit").inputValue()==="0"&&await page.locator("#field-anchor-weight").inputValue()==="4/5","V3 exact anchor and audit-cost defaults are visible",true);
    check(await page.locator('#preset option[value="anchor_dominant_q50"]').count()===1,"Experimental equilibrium-improving preset is available",await page.locator("#preset").innerText());
    await page.locator("#preset").selectOption("anchor_dominant_q50");
    check(await page.locator("#field-verification-anchor-audit-probability").inputValue()==="1/2"&&await page.locator("#field-lambda-peer").inputValue()==="0"&&await page.locator("#field-anchor-weight").inputValue()==="19/10","Experimental preset keeps exact q, peer and anchor allocation",true);
    await page.locator("#preset").selectOption("heterogeneous_anchor");
    await page.locator("#validate").click();
    await page.locator("#job-detail").filter({hasText:"Đầu vào hợp lệ"}).waitFor();
    const diagnostics=await page.locator("#signal-diagnostics").innerText();
    check(diagnostics.includes("verification_anchor")&&diagnostics.includes("audit_probability"),"Validation renders verification diagnostics",diagnostics.slice(-500));

    const pendingDownload=page.waitForEvent("download");
    await page.locator("#export").click();
    const download=await pendingDownload;
    await download.saveAs(output+"/v3-export.json");
    await page.locator("#field-anchor-weight").fill("1/3");
    await page.locator("#import").setInputFiles(output+"/v3-export.json");
    await page.locator("#job-detail").filter({hasText:"Đã nhập JSON hợp lệ"}).waitFor();
    check(await page.locator("#field-anchor-weight").inputValue()==="4/5","V3 import/export preserves exact anchor weight","4/5");

    const analysis=await runUI("analyze");
    const summary=await read(`/api/runs/${analysis.job.run_id}/artifacts/summary.json`);
    check(analysis.manifest.model_version==="ceav-m1-v3.0"&&analysis.manifest.mechanism==="hybrid_anchor","Analyze manifest pins V3 hybrid identity",{model:analysis.manifest.model_version,mechanism:analysis.manifest.mechanism});
    check(summary.metrics.expected_anchor_reward_total.exact==="44/125"&&summary.metrics.expected_peer_reward_total.exact&&summary.metrics.expected_audit_cost.exact==="0","Analysis exposes exact peer, anchor and audit-cost accounting",summary.metrics);
    check((await page.locator("#expected-anchor-reward-total").innerText()).includes(summary.metrics.expected_anchor_reward_total.exact),"UI anchor total matches artifact exactly",await page.locator("#expected-anchor-reward-total").innerText());
    check(summary.state_support_size===128&&await page.locator("#states-table tbody tr").count()===128,"V3 renders all 128 potential states",{artifact:summary.state_support_size,ui:await page.locator("#states-table tbody tr").count()});
    const analysisText=await page.locator("#analyze-result").innerText();
    check(analysisText.includes("report khóa")&&analysisText.includes("Anchor reward")&&analysisText.includes("128 potential"),"UI explains timing and decomposed reward",analysisText.slice(0,1000));
    check(analysisText.includes("Accuracy của candidate cố định")&&analysisText.includes("nếu ép")&&summary.metrics.accuracy.exact==="1791/2000","UI labels 89.55% as forced non-equilibrium candidate accuracy",{text:analysisText.slice(0,1200),accuracy:summary.metrics.accuracy});
    await shot("v3-analysis-desktop");

    await page.locator('[data-view="equilibria"]').click();
    const search=await runUI("equilibria",120000);
    const equilibria=await read(`/api/runs/${search.job.run_id}/artifacts/equilibria.json`);
    check(equilibria.branch_candidate_count===432&&equilibria.enumeration_completed,"V3 exhaustive pure search covers 432 branch candidates",{count:equilibria.branch_candidate_count,complete:equilibria.enumeration_completed});
    check(await page.locator("#search-table tbody tr").count()===432,"V3 search renders all candidates",await page.locator("#search-table tbody tr").count());
    check((await page.locator("#analyze-combination").innerText()).includes("accuracy của cân bằng"),"Search tells the user how to compute equilibrium accuracy",await page.locator("#analyze-combination").innerText());
    await page.locator("#analyze-combination").click();
    const equilibriumAnalysis=await runUI("analyze");
    const equilibriumSummary=await read(`/api/runs/${equilibriumAnalysis.job.run_id}/artifacts/summary.json`);
    const equilibriumText=await page.locator("#analyze-result").innerText();
    check(equilibriumSummary.equilibrium_status==="exact_pure_equilibrium"&&equilibriumSummary.metrics.accuracy.exact==="7/10"&&equilibriumText.includes("Accuracy của cân bằng đang phân tích"),"Selected equilibrium is analyzed separately at 70% accuracy",{status:equilibriumSummary.equilibrium_status,accuracy:equilibriumSummary.metrics.accuracy,text:equilibriumText.slice(0,1200)});

    await page.locator('[data-view="sweep"]').click();
    await page.locator("#preset").selectOption("anchor_dominant_q50");
    await page.locator("#axis-anchor-weight-enabled").check();
    await page.locator("#axis-anchor-weight").fill("19/10, 2");
    const sweep=await runUI("sweep");
    const sweepArtifact=await read(`/api/runs/${sweep.job.run_id}/artifacts/sweep.json`);
    check(sweepArtifact.rows.length===2&&sweepArtifact.rows.some(point=>point.status==="invalid_budget"),"V3 anchor sweep keeps valid and over-budget rows",sweepArtifact.rows.map(point=>({status:point.status,anchor_weight:point.anchor_weight})));
    const validSweepPoint=sweepArtifact.rows.find(point=>point.status==="valid");
    const sweepText=await page.locator("#sweep-result").innerText();
    check(sweepArtifact.scope==="candidate_analysis_plus_exhaustive_pure_equilibrium_landscape"&&validSweepPoint.landscape.branch_candidate_count===432&&validSweepPoint.equilibrium_accuracy_min.exact==="1813/2000"&&validSweepPoint.equilibrium_accuracy_max.exact==="1813/2000"&&sweepText.includes("Equilibrium accuracy min")&&sweepText.includes("1813/2000"),"V3 sweep exposes exact equilibrium accuracy separately from candidate accuracy",{scope:sweepArtifact.scope,landscape:validSweepPoint.landscape,text:sweepText.slice(0,1600)});
    check(await page.locator("#sweep-result tbody tr").count()===2,"V3 sweep renders both rows",await page.locator("#sweep-result tbody tr").count());

    for(const viewport of [{width:1366,height:768},{width:390,height:844}]){
      await page.setViewportSize(viewport);
      const overflow=await page.evaluate(()=>({document:document.documentElement.scrollWidth,viewport:innerWidth}));
      check(overflow.document<=overflow.viewport+1,"No page-wide overflow at "+viewport.width,overflow);
      await page.locator("#model-version").focus();
      check(await page.locator("#model-version").evaluate(el=>el===document.activeElement),"Keyboard focus reaches model selector at "+viewport.width,true);
      await shot(viewport.width===390?"v3-mobile":"v3-desktop");
    }
    check(errors.length===0,"No JavaScript runtime errors",errors);
    return {scenario,status:"passed",browser:page.context().browser().version(),viewport:page.viewportSize(),steps,network,errors,runs:{analyze:analysis.job.run_id,equilibrium_analyze:equilibriumAnalysis.job.run_id,equilibria:search.job.run_id,sweep:sweep.job.run_id}};
  } catch(error) {
    return {scenario,status:"failed",browser:page.context().browser().version(),viewport:page.viewportSize(),steps,error:error.stack,network,errors};
  }
}
