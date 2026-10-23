async page => {
  const scenario="__SCENARIO__",output="__OUTPUT_DIR__",base="__BASE_URL__",steps=[],errors=[],network=[];
  page.on("pageerror",error=>errors.push(error.message));
  page.on("request",request=>network.push({url:request.url(),method:request.method()}));
  const check=(condition,message,observed)=>{steps.push({step:message,status:condition?"pass":"fail",observed});if(!condition)throw new Error(message+": "+JSON.stringify(observed));};
  const read=async path=>{const response=await page.request.get(base+path);if(response.status()!==200)throw new Error("GET "+path+": "+response.status());return response.json();};
  const shot=async name=>page.screenshot({path:output+"/"+name+".png",fullPage:false});
  try {
    await page.setViewportSize({width:1366,height:768});
    await page.goto(base);
    await page.locator("#connection").filter({hasText:"Engine sẵn sàng"}).waitFor();
    await page.locator("#model-version").selectOption("ceav-m1-v2.0");
    await page.locator('[data-view="incentives"]').click();
    check(await page.locator("#model-version").inputValue()==="ceav-m1-v2.0","Diagnostics uses V2 draft",await page.locator("#model-version").inputValue());
    check((await page.locator('[data-panel="incentives"]').innerText()).includes("Threshold λ là kết quả cục bộ"),"UI distinguishes conditional threshold from global search",true);
    await page.locator("#incentive-axis-lambda-enabled").uncheck();
    check((await page.locator("#incentive-grid-preview").innerText()).includes("1 điểm")&&(await page.locator("#incentive-grid-preview").innerText()).includes("432"),"Base run previews one exhaustive landscape",await page.locator("#incentive-grid-preview").innerText());
    const pending=page.waitForResponse(r=>r.url()===base+"/api/runs"&&r.request().method()==="POST");
    await page.locator('[data-operation="incentives"]').click();
    const response=await pending;
    check(response.status()===202,"UI submits incentive diagnostics through worker",response.status());
    const job=await response.json();
    await page.waitForFunction(id=>document.querySelector("#incentives-result")?.dataset.runId===id,job.run_id,{timeout:90000});
    const manifest=await read("/api/runs/"+job.run_id);
    const diagnostics=await read(`/api/runs/${job.run_id}/artifacts/incentive_diagnostics.json`);
    const sweep=await read(`/api/runs/${job.run_id}/artifacts/incentive_sweep.json`);
    check(manifest.status==="succeeded"&&manifest.operation==="incentives","Diagnostics reaches immutable succeeded run",{status:manifest.status,operation:manifest.operation});
    check(await page.locator(".diagnostic-card").count()===6,"UI renders all six Judge by Z diagnostics",await page.locator(".diagnostic-card").count());
    check(diagnostics.branches.length===6&&diagnostics.warning.includes("not global equilibrium"),"Artifact preserves conditional warning and six branches",diagnostics.warning);
    check(sweep.points.length===1&&sweep.points[0].landscape.branch_candidate_count===432&&sweep.points[0].landscape.enumeration_completed,"Valid point contains exhaustive pure search",sweep.points[0].landscape);
    const text=await page.locator("#incentives-result").innerText();
    check(text.includes("Equilibrium landscape")&&text.includes("432")&&text.includes("Có Low"),"UI renders global landscape separately",text.slice(-600));
    await shot("incentives-desktop");
    await page.setViewportSize({width:390,height:844});
    await page.locator("#incentives-result").scrollIntoViewIfNeeded();
    const overflow=await page.evaluate(()=>({document:document.documentElement.scrollWidth,viewport:innerWidth}));
    check(overflow.document<=overflow.viewport+1,"No page-wide overflow on mobile",overflow);
    check(await page.locator(".diagnostic-card").first().isVisible(),"Diagnostic cards remain visible on mobile",true);
    await page.keyboard.press("Tab");
    check((await page.evaluate(()=>document.activeElement?.tagName))!=="BODY","Keyboard focus remains available",await page.evaluate(()=>document.activeElement?.tagName));
    await shot("incentives-mobile");
    check(errors.length===0,"No JavaScript runtime errors",errors);
    return {scenario,status:"passed",browser:page.context().browser().version(),viewport:page.viewportSize(),steps,network,errors,run_id:job.run_id};
  } catch(error) {
    return {scenario,status:"failed",browser:page.context().browser().version(),viewport:page.viewportSize(),steps,error:error.stack,network,errors};
  }
}
