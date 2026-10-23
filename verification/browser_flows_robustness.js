async page => {
  const scenario="__SCENARIO__",output="__OUTPUT_DIR__",base="__BASE_URL__",steps=[],errors=[],network=[];
  page.on("pageerror",error=>errors.push(error.message));
  page.on("request",request=>network.push({url:request.url(),method:request.method()}));
  const check=(condition,message,observed)=>{steps.push({step:message,status:condition?"pass":"fail",observed});if(!condition)throw new Error(message+": "+JSON.stringify(observed));};
  const read=async path=>{const response=await page.request.get(base+path);if(response.status()!==200)throw new Error("GET "+path+": "+response.status());return response.json();};
  try {
    if(scenario!=="ROB-B01")throw new Error("Unknown robustness browser scenario: "+scenario);
    await page.setViewportSize({width:1366,height:768});
    await page.goto(base);
    await page.locator("#connection").filter({hasText:"Engine sẵn sàng"}).waitFor();
    await page.locator('[data-view="robustness"]').click();
    const intro=await page.locator('[data-panel="robustness"]').innerText();
    check(intro.includes("V3 giữ nguyên")&&intro.includes("Latency chưa được mô hình hóa")&&intro.includes("không nội suy"),"UI states unchanged game, discrete grid and latency limitation",intro);
    check(await page.locator("#robustness-study").inputValue()==="acceptance","Acceptance study is the safe UI default",await page.locator("#robustness-study").inputValue());
    const pending=page.waitForResponse(r=>r.url()===base+"/api/runs"&&r.request().method()==="POST");
    await page.locator('[data-operation="robustness"]').click();
    const response=await pending;
    check(response.status()===202,"UI submitted robustness",response.status());
    const job=await response.json();
    await page.waitForFunction(id=>document.querySelector("#robustness-result")?.dataset.runId===id,job.run_id,{timeout:120000});
    const manifest=await read("/api/runs/"+job.run_id);
    const artifact=await read(`/api/runs/${job.run_id}/artifacts/robustness.json`);
    check(manifest.status==="succeeded"&&manifest.operation==="robustness"&&manifest.analysis.version==="ceav-m1-v3.1-robustness","Manifest pins V3.1 analysis identity",manifest);
    check(artifact.grid.total_points===1&&artifact.points[0].branch_candidate_count===432&&artifact.points[0].enumeration_completed,"Acceptance point completed exhaustive pure search",artifact.grid);
    const text=await page.locator("#robustness-result").evaluate(element=>element.textContent);
    check(text.includes("Worst false approval")&&text.includes("Worst wrongly paid")&&text.includes("Accuracy chỉ là diagnostic"),"UI prioritizes risk metrics and labels accuracy as diagnostic",text);
    check(text.includes("latency_not_modeled")&&text.includes("reference_only_not_equal_resources")&&text.includes("forced_candidate_not_equilibrium_claim"),"UI preserves baseline and latency caveats",text);
    check(artifact.classification==="isolated_robust_point"&&artifact.robust_policy_ids.length===1&&artifact.points[0].failure_reasons.length===0,"Artifact exposes robust classification and failure reasons",{classification:artifact.classification,ids:artifact.robust_policy_ids,reasons:artifact.points[0].failure_reasons});
    await page.screenshot({path:output+"/robustness-desktop.png",fullPage:true});
    await page.setViewportSize({width:390,height:844});
    const overflow=await page.evaluate(()=>({document:document.documentElement.scrollWidth,viewport:innerWidth}));
    check(overflow.document<=overflow.viewport+1,"No page-wide mobile overflow",overflow);
    await page.screenshot({path:output+"/robustness-mobile.png",fullPage:false});
    check(errors.length===0,"No JavaScript runtime errors",errors);
    return {scenario,status:"passed",browser:page.context().browser().version(),viewport:page.viewportSize(),steps,network,errors,runs:{robustness:job.run_id}};
  } catch(error) {
    return {scenario,status:"failed",browser:page.context().browser().version(),viewport:page.viewportSize(),steps,error:error.stack,network,errors};
  }
}
