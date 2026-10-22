async page => {
  const scenario="B08", output="C:/Users/dell/Desktop/fundtogether_data_analyzing/results/v21-browser-B08-release-05", base="http://127.0.0.1:8877";
  const steps=[],errors=[],network=[];
  page.on("pageerror",error=>errors.push(error.message));
  page.on("request",request=>network.push({url:request.url(),method:request.method()}));
  const check=(condition,message,observed)=>{steps.push({step:message,status:condition?"pass":"fail",observed});if(!condition)throw new Error(message+": "+JSON.stringify(observed));};
  const shot=async name=>{await page.screenshot({path:output+"/"+name+".png",fullPage:false});};
  const read=async path=>{const r=await page.request.get(base+path);if(r.status()!==200)throw new Error("GET "+path+": "+r.status());return r.json();};
  const runUI=async (selector,operation,timeout=30000)=>{
    const pending=page.waitForResponse(r=>r.url()===base+"/api/runs"&&r.request().method()==="POST");
    await page.locator(selector).click();const response=await pending;
    check(response.status()===202,"UI submitted "+operation,response.status());
    const job=await response.json();
    await page.waitForFunction(id=>document.querySelector("#run-metadata").textContent.includes(id),job.run_id,{timeout});
    await page.waitForFunction(({id,operation})=>document.querySelector("#"+operation+"-result")?.dataset.runId===id,{id:job.run_id,operation:job.request.operation},{timeout});
    const manifest=await read("/api/runs/"+job.run_id);
    check(!["queued","running"].includes(manifest.status),"UI observed terminal run",{id:job.run_id,status:manifest.status});
    return {job,manifest};
  };
  try {
    await page.setViewportSize({width:1366,height:768});
    await page.goto(base);await page.locator("#connection").filter({hasText:"Engine sẵn sàng"}).waitFor({state:"attached"});
    await page.locator("#model-version").selectOption("ceav-m1-v1.0");
    if(scenario==="B01") {
      await page.context().route("**/*",route=>route.request().url().startsWith(base)?route.continue():route.abort());
      await page.reload();await page.locator("#connection").filter({hasText:"Engine sẵn sàng"}).waitFor({state:"attached"});
      for(const view of ["analyze","equilibria","sweep","compare","tests","history"]){await page.locator(`[data-view="${view}"]`).click();check(await page.locator(`[data-panel="${view}"]`).isVisible(),"Navigation opens "+view,true);}
      await page.locator('[data-view="analyze"]').click();
      check(network.every(r=>r.url.startsWith(base)),"No external network dependency",network);
      await shot("desktop-initial");await page.context().unroute("**/*");
    } else if(scenario==="B02") {
      const values={pi:"2/3",a:"3/5",b:"4/5","costs[0]":"0","costs[1]":"1/50","costs[2]":"3/20",f:"1/10",lambda:"3/4",fixed_reward:"8/5",reward_budget:"6",payout_value:"2",operating_cost:"1/10"};
      for(const [name,value] of Object.entries(values))await page.locator(`[data-field="${name}"]`).fill(value);
      const actions=["L0","L1","H00","H01","H10","H11"];
      for(let z=0;z<2;z++)for(let i=0;i<3;i++)await page.locator(`#action-${z}-${i}`).selectOption(actions[3*z+i]);
      await page.locator("#validate").click();await page.locator("#job-detail").filter({hasText:"Đầu vào hợp lệ"}).waitFor();
      const pending=page.waitForEvent("download");await page.locator("#export").click();const download=await pending;await download.saveAs(output+"/exported-inputs.json");
      const invalid={model_version:"ceav-m1-v1.0",...values,costs:["0","1/50","3/20"],pi:0.5};delete invalid["costs[0]"];delete invalid["costs[1]"];delete invalid["costs[2]"];
      await page.locator("#import").setInputFiles({name:"invalid.json",mimeType:"application/json",buffer:Buffer.from(JSON.stringify(invalid))});
      await page.locator("#errors").waitFor({state:"visible"});check(await page.locator("#field-pi").getAttribute("aria-invalid")==="true","Invalid import names exact field","pi");await shot("invalid-import");
      await page.locator("#import").setInputFiles(output+"/exported-inputs.json");await page.locator("#job-detail").filter({hasText:"Đã nhập JSON hợp lệ"}).waitFor();
      check(await page.locator("#field-pi").inputValue()==="2/3","Import/export preserves rational strings","2/3");
      check(await page.locator("#action-1-2").inputValue()==="H11","All six action fields editable","H11");await shot("valid-import");
      await page.locator("#quick-profile").selectOption("all_inverted");check((await page.locator("#profile-editor select").evaluateAll(elements=>elements.map(el=>el.value))).every(action=>action==="H10"),"Named all-H inverse-report profile is available",true);
    } else if(scenario==="B03") {
      const records=[];
      for(const number of [1,2,3,4]){
        await page.locator("#preset").selectOption("golden_g"+number);
        const {job,manifest}=await runUI('[data-operation="analyze"]',"analyze");
        const summary=await read(`/api/runs/${job.run_id}/artifacts/summary.json`),certificates=await read(`/api/runs/${job.run_id}/artifacts/best_responses.json`);
        check(manifest.status==="succeeded","G"+number+" engine run completed",manifest.status);
        check(summary.equilibrium_status===([1,2].includes(number)?"exact_pure_equilibrium":"not_equilibrium"),"G"+number+" equilibrium verdict",summary.equilibrium_status);
        check(await page.locator("#analyze-result > .certificate").count()===6,"G"+number+" renders six judge/Z certificates",certificates.length);
        records.push({golden:"G"+number,run_id:job.run_id,config_hash:manifest.config_hash,profile_hash:manifest.profile_hash,accuracy:summary.metrics.accuracy.exact,verdict:summary.equilibrium_status});
        if(number===1){await page.locator("#state-y").selectOption("0");check(await page.locator("#states-table tbody tr").count()===16,"State table filters ground-truth label",16);await page.locator("#state-z").selectOption("0");check(await page.locator("#states-table tbody tr").count()===8,"State table combines Y/Z filters",8);await page.locator("#state-decision").selectOption("1");check(await page.locator("#states-table tbody tr").count()===4,"State table filters majority decision",4);for(const key of ["y","z","decision"])await page.locator("#state-"+key).selectOption("");await page.locator("#analyze-result > .certificate").first().locator("summary").first().click();await page.getByText("3611/2500",{exact:true}).first().waitFor({state:"visible"});await shot("G1-exact-certificate");}
        if(number===4){
          const branch=page.locator("#analyze-result > .certificate").filter({has:page.locator('[data-witness="A-1"]')});await branch.locator("summary").first().click();
          await page.locator('[data-witness="A-1"]').waitFor({state:"visible"});await shot("G4-deviation");
          const before=JSON.stringify(manifest);await page.locator('[data-witness="A-1"]').click();check((await page.locator("#action-1-0").inputValue()).startsWith("L"),"Witness loaded as new candidate branch",true);
          const clone=await runUI('[data-operation="analyze"]',"analyze-clone");check(clone.job.run_id!==job.run_id,"Clone creates a distinct run",clone.job.run_id);check(JSON.stringify(await read("/api/runs/"+job.run_id))===before,"Original G4 run unchanged after clone",job.run_id);
        }
      }
      steps.push({step:"Golden run identities",status:"pass",observed:records});
    } else if(scenario==="B04") {
      await page.locator('[data-view="equilibria"]').click();const {job}=await runUI('[data-operation="equilibria"]',"equilibria");
      check(await page.locator("#search-table tbody tr").count()===432,"Search renders all branch candidates",432);
      await page.locator("#search-effort").selectOption("A_L");check(await page.locator("#search-table tbody tr").count()===144,"Effort filter works for an individual Judge",144);await page.locator("#search-effort").selectOption("");
      await page.locator("#search-accepted").selectOption("false");await page.locator("[data-certificate]").first().click();
      check((await page.locator("#search-certificate").innerText()).includes("Bị bác"),"Rejected candidate exposes witness",true);await shot("search-rejected-certificate");
      const search=await read(`/api/runs/${job.run_id}/artifacts/equilibria.json`);check(search.branch_candidate_count===432,"Backend counted all candidates",search.branch_candidate_count);
      const chosen={};for(const z of [0,1])chosen[z]=(await page.locator("#chosen-z"+z+" option").first().textContent()).split(" / ");
      await page.locator("#analyze-combination").click();check(await page.locator('[data-panel="analyze"]').isVisible(),"Combination opens analyze",true);
      for(const z of [0,1])for(let i=0;i<3;i++)check(await page.locator(`#action-${z}-${i}`).inputValue()===chosen[z][i],"Combination profile preserved "+z+"/"+i,chosen[z][i]);
      const analysis=await runUI('[data-operation="analyze"]',"selected full profile");steps.push({step:"Search and full analysis IDs",status:"pass",observed:{search:job.run_id,analyze:analysis.job.run_id}});
    } else if(scenario==="B05") {
      await page.locator('[data-view="sweep"]').click();const sweep=await runUI('[data-operation="sweep"]',"sweep");
      check(await page.locator("#sweep-result tbody tr").count()===4,"Sweep preserves all four grid rows",4);
      check((await page.locator("#sweep-result").innerText()).includes("invalid_budget"),"Sweep shows invalid budget row",true);
      check(await page.locator("#sweep-chart circle").count()===3,"Chart contains only the three computed valid points",3);await shot("sweep-with-invalid-budget");
      await page.locator('[data-sweep-point="1"]').click();check(await page.locator("#field-lambda").inputValue()==="1/2","Sweep point loads exact config","1/2");await runUI('[data-operation="analyze"]',"replay sweep point");
      await page.locator("#preset").selectOption("golden_g1");await page.locator('[data-view="sweep"]').click();
      await page.locator("#axis-pi-enabled").check();await page.locator("#axis-pi").fill("1/2, 4/5");await page.locator("#axis-a-enabled").check();await page.locator("#axis-a").fill("3/5, 7/10");await page.locator("#axis-lambda").fill("0, 1");
      await runUI('[data-operation="sweep"]',"multi-axis sweep");await page.locator("#chart-x").selectOption("pi");await page.locator("#chart-series").selectOption("lambda");await page.locator('[data-fixed-axis="a"]').selectOption("7/10");
      check(await page.locator("#sweep-result tbody tr").count()===8,"Multi-axis sweep keeps Cartesian grid",8);check(await page.locator("#sweep-chart circle").count()===4,"Two plotted axes with remaining axis fixed",4);await shot("multi-axis-sweep");
      await page.locator("#preset").selectOption("golden_g1");await page.locator('[data-view="compare"]').click();await page.locator("#field-fixed-reward").fill("1");
      await page.locator('[data-operation="compare"]').click();await page.locator("#errors").waitFor({state:"visible"});check((await page.locator("#errors").innerText()).includes("fixed_reward"),"Comparison rejects unequal cap",true);
      await page.locator("#equal-cap").click();await page.waitForFunction(()=>document.querySelector("#field-fixed-reward").value==="2");const compared=await runUI('[data-operation="compare"]',"compare");
      const summary=await read(`/api/runs/${compared.job.run_id}/artifacts/summary.json`);check(summary.mechanisms.fixed.metrics.expected_reward_total.exact!==summary.mechanisms.rbts.metrics.expected_reward_total.exact,"Equal cap does not imply equal actual spend",summary);await shot("comparison-actual-spend");
      const comparisonText=await page.locator("#compare-result").innerText();
      check(comparisonText.includes("Cùng một candidate/profile")&&comparisonText.includes("không tự chuyển Fixed sang Low Effort"),"Comparison explains why effort cost can match for a non-equilibrium Fixed candidate",comparisonText);
      check((await page.locator("#compare-result").innerText()).includes(compared.job.run_id),"Comparison table labels the actual run and model",compared.job.run_id);
      for(const name of ["fixed/states.csv","rbts/states.csv"]){const pending=page.waitForEvent("download");await page.locator("#run-metadata a").filter({hasText:name}).click();const download=await pending;await download.saveAs(output+"/"+name.replace("/","-"));}
      steps.push({step:"Comparison artifact source",status:"pass",observed:{run_id:compared.job.run_id,manifest:compared.manifest}});
    } else if(scenario==="B06") {
      await page.locator('[data-view="tests"]').click();
      const runs=[];
      for(const suite of ["reference","goldens"]){await page.locator("#suite").selectOption(suite);const r=await runUI('[data-operation="tests"]',suite);const data=await read(`/api/runs/${r.job.run_id}/artifacts/test_results.json`);check(data.status==="passed",suite+" executes through UI",data.counts);if(suite==="reference"){const fresh=await read(`/api/runs/${r.job.run_id}/artifacts/reference_results.json`);check(fresh.G1.accuracy.exact==="112/125","Reference exposes newly computed exact results",fresh.G1.accuracy);}runs.push(r.job.run_id);}
      await page.locator("#suite").selectOption("selected");for(const checkbox of await page.locator("#test-ids input").all())await checkbox.uncheck();
      await page.locator('#test-ids input[value="T29"]').check();const selected=await runUI('[data-operation="tests"]',"selected T29");
      const selectedData=await read(`/api/runs/${selected.job.run_id}/artifacts/test_results.json`);
      check(selectedData.records.some(r=>r.evidence?.missing_discovery_fixture?.counts.not_run===1),"Missing-discovery fixture preserves not_run and runner error",selectedData.counts);
      for(const checkbox of await page.locator("#test-ids input").all())await checkbox.uncheck();await page.locator("#failure-fixture").check();
      const failure=await runUI('[data-operation="tests"]',"explicit failure fixture");const data=await read(`/api/runs/${failure.job.run_id}/artifacts/test_results.json`);
      check(failure.manifest.status==="failed"&&data.counts.fail===1,"Intentional fixture yields actual failed run",data.counts);await shot("test-failure-fixture");
      const downloadPromise=page.waitForEvent("download");await page.locator('#tests-result a').click();const download=await downloadPromise;await download.saveAs(output+"/failure-test-log.txt");
      await page.locator("#failure-fixture").uncheck();for(const checkbox of await page.locator('#test-ids input[value^="T"]').all())if(await checkbox.getAttribute("value")!=="T32")await checkbox.check();
      const pending=page.waitForResponse(r=>r.url()===base+"/api/runs"&&r.request().method()==="POST");await page.locator('[data-operation="tests"]').click();const response=await pending;check(response.status()===202,"Full engine/API suite submitted through browser",response.status());const all=await response.json();
      return {scenario,status:"pending_all",browser:page.context().browser().version(),viewport:page.viewportSize(),steps,network,errors,all_job:all.job_id,all_run:all.run_id};
    } else if(scenario==="B07") {
      await page.locator('[data-view="equilibria"]').click();const pending=page.waitForResponse(r=>r.url()===base+"/api/runs"&&r.request().method()==="POST");await page.locator('[data-operation="equilibria"]').click();const submitted=await pending;const job=await submitted.json();
      await page.locator("#job-state").filter({hasText:"Đang chạy"}).waitFor();
      const status=await read("/api/status");const duplicate=await page.request.post(base+"/api/runs",{headers:{Origin:base,"X-CEAV-Token":status.token},data:job.request});check(duplicate.status()===409,"Backend rejects duplicate submit while UI disables controls",duplicate.status());
      check(await page.locator('[data-operation="analyze"]').isDisabled(),"Run buttons disabled during active task",true);
      await page.locator('[data-view="analyze"]').click();await page.locator("#field-pi").fill("4/5");
      const original=await read("/api/jobs/"+job.job_id);check(original.request.config.pi==="1/2","Editing draft does not change active request snapshot",original.request.config.pi);
      await page.locator("#cancel").click();await page.locator("#job-state").filter({hasText:"Đã hủy"}).waitFor();await page.waitForFunction(id=>document.querySelector("#equilibria-result")?.dataset.runId===id,job.run_id);
      check((await read("/api/runs/"+job.run_id)).status==="cancelled","Cancelled task never publishes succeeded",true);await shot("cancelled-search");
      await page.locator('[data-view="tests"]').click();await page.locator("#suite").selectOption("selected");for(const checkbox of await page.locator("#test-ids input").all())await checkbox.uncheck();await page.locator('#test-ids input[value="T14"]').check();
      const restartPending=page.waitForResponse(r=>r.url()===base+"/api/runs"&&r.request().method()==="POST");await page.locator('[data-operation="tests"]').click();const restartJob=await (await restartPending).json();
      await page.waitForFunction(()=>document.querySelector("#job-state").textContent==="Đang chạy");const active=await read("/api/jobs/"+restartJob.job_id);
      return {scenario,status:"pending_restart",browser:page.context().browser().version(),viewport:page.viewportSize(),steps,network,errors,restart_job:restartJob.job_id,restart_run:restartJob.run_id,worker_pid:active.worker_pid,cancelled_run:job.run_id};
    } else if(scenario==="B08") {
      await page.locator('[data-view="history"]').click();await page.locator("#history-result tbody tr").first().waitFor();
      const history=await read("/api/runs");const candidates=history.runs.filter(r=>r.operation==="analyze"&&r.status==="succeeded");check(candidates.length>=2,"History contains completed real analysis runs",candidates.length);
      const chosen=candidates[0],other=candidates.find(r=>r.config_hash!==chosen.config_hash)||candidates[1];
      await page.locator(`[data-open-run="${chosen.run_id}"]`).click();await page.waitForFunction(id=>document.querySelector("#analyze-result").dataset.runId===id,chosen.run_id);
      const manifest=await read("/api/runs/"+chosen.run_id);check((await page.locator("#run-metadata").innerText()).includes(manifest.spec.revision),"History displays actual spec and freeze versions",manifest.spec);
      for(const name of ["manifest.json","config.json","profile.json","summary.json","best_responses.json","states.csv","report.md"]){const pending=page.waitForEvent("download");await page.locator(`#run-metadata a`).filter({hasText:name}).filter({visible:true}).first().click();const download=await pending;await download.saveAs(output+"/download-"+name);}
      await page.locator(`#run-metadata [data-pin="${chosen.run_id}"]`).click();await page.locator('[data-view="history"]').click();await page.locator(`#history-result [data-pin="${other.run_id}"]`).click();await page.locator('[data-view="compare"]').click();await page.locator("#pinned-result table").waitFor();
      check((await page.locator("#pinned-result").innerText()).includes("config_hash"),"Pinned run differences are explicitly disclosed",{first:chosen.run_id,second:other.run_id});await shot("history-pinned-differences");
      steps.push({step:"Downloaded artifact source",status:"pass",observed:{run_id:chosen.run_id,manifest}});
    } else if(scenario==="B09") {
      const focusSamples=[];
      const tabTo=async selector=>{for(let i=0;i<180;i++){if(await page.locator(selector).evaluate(el=>el===document.activeElement)){const style=await page.locator(selector).evaluate(el=>({width:parseFloat(getComputedStyle(el).outlineWidth),style:getComputedStyle(el).outlineStyle,color:getComputedStyle(el).outlineColor}));focusSamples.push({selector,...style});if(style.width<2||style.style==="none")throw new Error("Keyboard focus is not visible: "+selector);return;}await page.keyboard.press("Tab");}throw new Error("Keyboard cannot reach "+selector);};
      const activate=async selector=>{await tabTo(selector);await page.keyboard.press("Enter");};
      const keyRun=async operation=>{const pending=page.waitForResponse(r=>r.url()===base+"/api/runs"&&r.request().method()==="POST");await activate(`[data-operation="${operation}"]`);const response=await pending;check(response.status()===202,"Keyboard submits "+operation,response.status());const job=await response.json();await page.waitForFunction(({id,op})=>document.querySelector("#"+op+"-result")?.dataset.runId===id,{id:job.run_id,op:operation},{timeout:30000});return job;};
      for(const viewport of [{width:1366,height:768},{width:390,height:844}]){
        await page.setViewportSize(viewport);await page.goto(base);await page.locator("#connection").filter({hasText:"Engine sẵn sàng"}).waitFor({state:"attached"});await page.locator("#model-version").selectOption("ceav-m1-v1.0");
        await tabTo("#field-pi");await page.keyboard.press("ControlOrMeta+A");await page.keyboard.type("1");await activate("#validate");await page.locator("#errors").waitFor({state:"visible"});
        check(await page.locator("#field-pi").getAttribute("aria-invalid")==="true","Keyboard validation names field at "+viewport.width,true);
        await tabTo("#field-pi");await page.keyboard.press("ControlOrMeta+A");await page.keyboard.type("1/2");
        await keyRun("analyze");check((await page.locator("#analyze-result .verdict").innerText()).includes("Cân bằng thuần"),"Keyboard analysis completes at "+viewport.width,true);
        const overflow=await page.evaluate(()=>({document:document.documentElement.scrollWidth,viewport:innerWidth}));check(overflow.document<=overflow.viewport+1,"No document-wide overflow at "+viewport.width,overflow);
        const labels=await page.locator("input:visible, select:visible").evaluateAll(elements=>elements.filter(el=>!el.labels?.length&&!el.getAttribute("aria-label")).map(el=>el.id));check(labels.length===0,"Visible controls have attached labels",labels);
        await tabTo("#states-table .table-wrap");const before=await page.locator("#states-table .table-wrap").evaluate(el=>el.scrollLeft);for(let i=0;i<8;i++)await page.keyboard.press("ArrowRight");await page.waitForFunction(before=>document.querySelector("#states-table .table-wrap").scrollLeft>before,before,{timeout:3000});const after=await page.locator("#states-table .table-wrap").evaluate(el=>el.scrollLeft);check(after>before,"Keyboard scrolls wide state table at "+viewport.width,{before,after});
        await page.locator("#content").scrollIntoViewIfNeeded();await shot(viewport.width===390?"mobile-analysis":"desktop-analysis");
        await activate('[data-view="equilibria"]');await keyRun("equilibria");await activate("#analyze-combination");await keyRun("analyze");
        await activate('[data-view="sweep"]');await keyRun("sweep");
        await activate('[data-view="compare"]');await keyRun("compare");
        await activate('[data-view="tests"]');await keyRun("tests");
        await activate('[data-view="history"]');check(await page.locator("#history-result table").isVisible(),"Keyboard reaches history at "+viewport.width,true);
        await page.locator("#content").scrollIntoViewIfNeeded();await shot(viewport.width===390?"mobile-history":"desktop-history");
      }
      const scans=[];
      for(const viewport of [{width:1366,height:768},{width:390,height:844}]){await page.setViewportSize(viewport);for(const view of ["analyze","equilibria","sweep","compare","tests","history"]){await page.locator(`[data-view="${view}"]`).click();const measurement=await page.evaluate(()=>{
        const rgb=value=>(value.match(/[\d.]+/g)||[]).map(Number);const luminance=c=>c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
        const failures=[],samples=[];for(const el of document.querySelectorAll("p,label,button,summary,th,td,a,span,h1,h2,h3,input,select,svg text")){
          const rect=el.getBoundingClientRect();if(!rect.width||!rect.height||el.closest("[hidden]")||el.matches(":disabled")||(!el.matches("input,select")&&![...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())))continue;
          const style=getComputedStyle(el);let parent=el,bg=[255,255,255];while(parent){const c=rgb(getComputedStyle(parent).backgroundColor);if(c.length===3||c[3]===1){bg=c;break;}parent=parent.parentElement;}
          const fg=rgb(el.matches("svg text")?style.fill:style.color),a=luminance(fg),b=luminance(bg),ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05),large=parseFloat(style.fontSize)>=24||(parseFloat(style.fontSize)>=18.66&&Number(style.fontWeight)>=700),required=large?3:4.5;
          const sample={text:el.textContent.trim().slice(0,50),ratio,required,foreground:style.color,background:bg};samples.push(sample);if(ratio+.001<required)failures.push(sample);
        }return {samples,failures};
      });scans.push({viewport,view,...measurement});}}
      const contrast={samples:scans.flatMap(s=>s.samples),failures:scans.flatMap(s=>s.failures),scopes:scans.map(s=>({viewport:s.viewport,view:s.view,samples:s.samples.length}))};
      check(contrast.failures.length===0,"Measured visible text contrast meets 4.5:1 / 3:1",contrast);
      steps.push({step:"Desktop/mobile keyboard flows",status:"pass",observed:{viewports:[{width:1366,height:768},{width:390,height:844}],operations:["analyze","equilibria","branch combination","sweep","compare","reference tests","history"],focus:"tab navigation and Enter activation completed without trap"}});
      steps.push({step:"Visible keyboard focus measurements",status:"pass",observed:focusSamples});
    } else {
      throw new Error("Scenario not implemented yet: "+scenario);
    }
    check(errors.length===0,"No JavaScript runtime errors",errors);
    return {scenario,status:"passed",browser:page.context().browser().version(),viewport:page.viewportSize(),steps,network,errors};
  }catch(error){return {scenario,status:"failed",browser:page.context().browser().version(),viewport:page.viewportSize(),steps,error:error.stack,network,errors};}
}
