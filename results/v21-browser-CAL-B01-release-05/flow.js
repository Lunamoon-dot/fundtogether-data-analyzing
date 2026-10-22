async page => {
  const scenario="CAL-B01",output="C:/Users/dell/Desktop/fundtogether_data_analyzing/results/v21-browser-CAL-B01-release-05",base="http://127.0.0.1:8877",steps=[],errors=[],network=[];
  page.on("pageerror",error=>errors.push(error.message));
  page.on("request",request=>network.push({url:request.url(),method:request.method()}));
  const check=(condition,message,observed)=>{steps.push({step:message,status:condition?"pass":"fail",observed});if(!condition)throw new Error(message+": "+JSON.stringify(observed));};
  const read=async path=>{const response=await page.request.get(base+path);if(response.status()!==200)throw new Error("GET "+path+": "+response.status());return response.json();};
  const shot=async name=>page.screenshot({path:output+"/"+name+".png",fullPage:false});
  try {
    await page.setViewportSize({width:1366,height:768});
    await page.goto(base);
    await page.locator("#connection").filter({hasText:"Engine sẵn sàng"}).waitFor();
    await page.locator('[data-view="calibration"]').click();
    check(await page.locator("#draft").isHidden(),"Calibration is a separate full-width data view",true);
    await page.locator("#load-calibration-sample").click();
    await page.locator("#calibration-file-status").filter({hasText:"synthetic_v2_calibration.csv"}).waitFor();
    check(await page.locator("#calibration-provenance").inputValue()==="synthetic","Sample is explicitly labeled synthetic",await page.locator("#calibration-provenance").inputValue());
    const pending=page.waitForResponse(r=>r.url()===base+"/api/runs"&&r.request().method()==="POST");
    await page.locator('[data-operation="calibrate"]').click();
    const response=await pending;
    check(response.status()===202,"UI submits calibration through worker",response.status());
    const job=await response.json();
    await page.waitForFunction(id=>document.querySelector("#calibrate-result")?.dataset.runId===id,job.run_id,{timeout:30000});
    const manifest=await read("/api/runs/"+job.run_id);
    const result=await read(`/api/runs/${job.run_id}/artifacts/calibration.json`);
    check(manifest.status==="succeeded"&&manifest.operation==="calibrate","Calibration reaches immutable succeeded run",{status:manifest.status,operation:manifest.operation});
    check(result.row_count===40&&result.class_counts["0"]===20&&result.class_counts["1"]===20,"UI run calibrates all 40 labeled cases",result.class_counts);
    check(result.estimates.public_signal.sensitivity.value==="4/5"&&result.estimates.public_signal.specificity.value==="3/5","Public estimates match independent fixture",result.estimates.public_signal);
    check(result.estimates.judges.B.private_signal.specificity.value==="19/20","Heterogeneous Judge estimate is preserved",result.estimates.judges.B);
    const visible=await page.locator("#calibrate-result").innerText();
    check(visible.includes("40 case")&&visible.toLowerCase().includes("synthetic")&&visible.includes("Nạp config vào Phân tích"),"Result explains scope and explicit apply action",visible.slice(0,500));
    await shot("calibration-desktop");
    await page.locator("#apply-calibration").click();
    check(await page.locator("#model-version").inputValue()==="ceav-m1-v2.0","Apply selects V2 model",await page.locator("#model-version").inputValue());
    check(await page.locator("#field-public-signal-sensitivity").inputValue()==="4/5"&&await page.locator("#field-judges-B-private-signal-specificity").inputValue()==="19/20","Generated exact config is loaded into analysis draft",true);
    check((await page.locator("#job-detail").innerText()).includes("Đã nạp config calibration"),"UI requires explicit apply before analysis",await page.locator("#job-detail").innerText());
    await page.setViewportSize({width:390,height:844});
    const overflow=await page.evaluate(()=>({document:document.documentElement.scrollWidth,viewport:innerWidth}));
    check(overflow.document<=overflow.viewport+1,"No page-wide overflow on mobile",overflow);
    await shot("calibration-mobile-applied");
    check(errors.length===0,"No JavaScript runtime errors",errors);
    return {scenario,status:"passed",browser:page.context().browser().version(),viewport:page.viewportSize(),steps,network,errors,run_id:job.run_id};
  } catch(error) {
    return {scenario,status:"failed",browser:page.context().browser().version(),viewport:page.viewportSize(),steps,error:error.stack,network,errors};
  }
}
