"use strict";

const $ = id => document.getElementById(id);
const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const copy = value => JSON.parse(JSON.stringify(value));
const state = {view:"analyze", status:null, active:null, revision:0, runRevision:null, analysis:null, search:null, sweep:null, manifest:null, pinned:[]};
const labels = {queued:"Đang chờ",running:"Đang chạy",succeeded:"Thành công",failed:"Thất bại",cancelled:"Đã hủy",interrupted:"Bị gián đoạn"};
const fields = [
  ["pi","π · P(Y=1)","1/2","model"], ["a","a · Độ chính xác Z","7/10","model"], ["b","b · Độ chính xác X","4/5","model"],
  ["costs[0]","c_A · Chi phí A","1/20","model"], ["costs[1]","c_B · Chi phí B","1/20","model"], ["costs[2]","c_C · Chi phí C","1/20","model"],
  ["f","f · Reward cơ bản","0","reward"], ["lambda","λ · Hệ số RBTS","1","reward"], ["fixed_reward","F · Fixed reward","2","reward"],
  ["reward_budget","B · Trần ngân sách","6","reward"], ["payout_value","V · Giá trị payout","1","reward"], ["operating_cost","Operating cost","0","reward"]
];
const fieldId = name => "field-" + name.replace(/[^a-zA-Z0-9]/g,"-");
const decimal = value => value && typeof value === "object" && "exact" in value ? (value.decimal == null ? value.exact : Number(value.decimal).toLocaleString("vi-VN",{maximumFractionDigits:8})) : String(value ?? "—");
const numeric = value => value && typeof value === "object" && "exact" in value ? `<span>${esc(decimal(value))}</span><span class="exact">${esc(value.exact)}</span>` : esc(value ?? "—");
const badge = status => `<span class="status-badge status-${esc(status)}">${esc(labels[status] || status)}</span>`;
const jsonBlock = value => `<pre class="code">${esc(JSON.stringify(value,null,2))}</pre>`;
const table = (headers, rows, tall=false) => `<div class="table-wrap ${tall?"scroll-tall":""}" tabindex="0" role="region" aria-label="Bảng dữ liệu cuộn ngang"><table><thead><tr>${headers.map(h=>`<th scope="col">${esc(h)}</th>`).join("")}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(cell=>`<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;

function setupForms() {
  fields.forEach(([name,label,value,group])=>{
    const wrapper=document.createElement("div");
    wrapper.innerHTML=`<label for="${fieldId(name)}">${esc(label)}</label><input type="text" id="${fieldId(name)}" data-field="${esc(name)}" value="${esc(value)}" aria-describedby="${fieldId(name)}-error"><span class="field-error" id="${fieldId(name)}-error"></span>`;
    $(group+"-fields").append(wrapper);
  });
  for (const z of [0,1]) {
    const row=document.createElement("div"); row.className="profile-row";
    row.innerHTML=`<span class="help">Z=${z}</span>`+["A","B","C"].map((judge,i)=>`<div><label for="action-${z}-${i}">${judge}</label><select id="action-${z}-${i}">${["L0","L1","H00","H01","H10","H11"].map(a=>`<option ${a==="H01"?"selected":""}>${a}</option>`).join("")}</select></div>`).join("");
    $("profile-editor").append(row);
  }
  for (const axis of ["pi","a","b","c","lambda"]) {
    const row=document.createElement("div"); row.className="axis-row";
    row.innerHTML=`<label class="check" for="axis-${axis}-enabled"><input type="checkbox" id="axis-${axis}-enabled" ${axis==="lambda"?"checked":""}>${axis}</label><input type="text" id="axis-${axis}" aria-label="Giá trị axis ${axis}" value="${axis==="lambda"?"0, 1/2, 1, 2":"1/2, 4/5"}">`;
    $("sweep-axes").append(row);
  }
  for (let i=1;i<=32;i++) {
    const id="T"+String(i).padStart(2,"0"); const label=document.createElement("label"); label.className="check";
    label.innerHTML=`<input type="checkbox" value="${id}" ${i<=5?"checked":""}>${id}`; $("test-ids").append(label);
  }
}

function readDraft() {
  const config={model_version:"ceav-m1-v1.0",costs:[]};
  for (const [name] of fields) {
    const value=$(fieldId(name)).value.trim();
    if (name.startsWith("costs")) config.costs[Number(name[6])]=value; else config[name]=value;
  }
  const profile={}; for(const z of [0,1]) profile[z]=[0,1,2].map(i=>$("action-"+z+"-"+i).value);
  return {config,profile,mechanism:$("mechanism").value};
}
function putDraft(config,profile,mechanism) {
  for(const [name] of fields) $(fieldId(name)).value=name.startsWith("costs")?config.costs[Number(name[6])]:config[name]??"0";
  for(const z of [0,1]) for(let i=0;i<3;i++) $("action-"+z+"-"+i).value=profile[z][i];
  if(mechanism) $("mechanism").value=mechanism;
  changed();
}
function changed() {state.revision++; $("stale").hidden=state.runRevision==null||state.revision===state.runRevision;}
function clearErrors() {
  $("errors").hidden=true; $("errors").textContent="";
  document.querySelectorAll("[aria-invalid]").forEach(el=>el.removeAttribute("aria-invalid"));
  document.querySelectorAll(".field-error").forEach(el=>el.textContent="");
}
function showError(error) {
  const messages=error.payload?.errors||[{message:error.message||String(error)}];
  $("errors").textContent=messages.map(e=>(e.field?e.field+": ":"")+e.message).join(" · "); $("errors").hidden=false;
  for(const message of messages) {
    const input=$(fieldId(message.field||""));
    if(input) {input.setAttribute("aria-invalid","true"); $(fieldId(message.field)+"-error").textContent=message.message;}
  }
  $("errors").focus();
}
async function api(path,body) {
  const response=await fetch(path,body===undefined?{}:{method:"POST",headers:{"Content-Type":"application/json","X-CEAV-Token":state.status.token},body:JSON.stringify(body)});
  const data=await response.json();
  if(!response.ok){const error=new Error(data.error||data.errors?.map(e=>e.message).join("; ")||"Lỗi API");error.payload=data;throw error;}
  return data;
}
function switchView(view) {
  state.view=view;
  document.querySelectorAll("[data-panel]").forEach(el=>el.hidden=el.dataset.panel!==view);
  document.querySelectorAll("[data-view]").forEach(el=>{if(el.dataset.view===view)el.setAttribute("aria-current","page");else el.removeAttribute("aria-current");});
  $("draft").hidden=["tests","history"].includes(view); $("layout").classList.toggle("full",$("draft").hidden);
  if(view==="history") refreshHistory().catch(showError);
  if(view==="compare") renderPinned().catch(showError);
  if(view==="tests") api("/api/browser-evidence").then(data=>{
    $("browser-evidence").innerHTML=data.records.length?data.records.map(record=>`<p><a href="${artifactURL(record.run_id,"browser_results.json",true)}">${esc(record.scenario)}</a> · ${esc(record.status)} · source engine/web/presets ${record.source_matches?"khớp":"đã thay đổi"} · ${esc(record.browser)} · ${esc(record.viewport.width)}×${esc(record.viewport.height)}</p>`).join(""):"Chưa có evidence trình duyệt. Các nhóm chưa chạy không được tính là pass.";
  }).catch(showError);
}
function readAxes() {
  const axes={}; for(const key of ["pi","a","b","c","lambda"]) if($("axis-"+key+"-enabled").checked) axes[key]=$("axis-"+key).value.split(",").map(v=>v.trim()).filter(Boolean);
  return axes;
}
function previewGrid() {const axes=readAxes(); const count=Object.keys(axes).length?Object.values(axes).reduce((a,b)=>a*b.length,1):0;$("grid-preview").textContent=`${count} điểm · profile và cơ chế giữ cố định.`;}
function updateJob(job) {
  $("job-state").textContent=labels[job.status]||job.status;
  $("job-detail").textContent=`${job.request.operation} · ${job.run_id}${job.cancel_requested?" · Đang dừng tiến trình…":""}${job.error?" · "+job.error:""}`;
  const progress=job.progress; $("progress").hidden=!progress;
  if(progress?.total){$("progress").max=progress.total;$("progress").value=progress.completed;$("job-detail").textContent+=` · ${progress.completed}/${progress.total}`;}else $("progress").removeAttribute("value");
  const running=["queued","running"].includes(job.status);
  document.querySelectorAll(".run").forEach(b=>b.disabled=running); $("cancel").disabled=!running||job.cancel_requested;
}
async function submit(operation) {
  clearErrors();
  const request=operation==="tests"?{operation,suite:$("suite").value,test_ids:[...$("test-ids").querySelectorAll("input:checked")].map(e=>e.value),failure_fixture:$("suite").value==="selected"&&$("failure-fixture").checked}:{operation,...readDraft()};
  if(operation==="sweep")request.axes=readAxes();
  if(operation==="equilibria")delete request.profile;
  const job=await api("/api/runs",request); state.active=job.job_id; state.pendingRevision=state.revision; updateJob(job); poll(job.job_id);
}
async function poll(identity) {
  try {
    const job=await api("/api/jobs/"+encodeURIComponent(identity)); updateJob(job);
    if(["queued","running"].includes(job.status)){setTimeout(()=>poll(identity),400);return;}
    state.active=null; await openRun(job.run_id); state.runRevision=state.pendingRevision; $("stale").hidden=state.revision===state.runRevision; await refreshHistory();
  }catch(error){showError(error);setTimeout(()=>poll(identity),1500);}
}
const artifactURL=(run,name,download=false)=>`/api/runs/${encodeURIComponent(run)}/artifacts/${encodeURIComponent(name)}${download?"?download=1":""}`;
async function artifact(run,name){return api(artifactURL(run,name));}
function labelResult(manifest,target) {
  if(!target)return;
  const note=document.createElement("p");note.className="run-note run-context";
  note.textContent=`${manifest.operation==="compare"?"fixed / rbts":manifest.mechanism||manifest.operation} · model ${manifest.model_version} · profile ${manifest.profile_hash||"theo phạm vi tác vụ"} · run ${manifest.run_id}`;
  target.prepend(note);
}
function renderMetadata(manifest) {
  const names=["manifest.json",...manifest.artifacts.map(a=>a.name)];
  $("run-metadata").innerHTML=`<details open><summary>Run ${esc(manifest.run_id)} · ${badge(manifest.status)}</summary><p class="run-note">${esc(manifest.operation)} · model ${esc(manifest.model_version)} · spec ${esc(manifest.spec?.revision)} · freeze ${esc(manifest.spec?.freeze_status)}<br>engine/source ${esc(manifest.engine_revision)}<br>config ${esc(manifest.config_hash||"—")} · profile ${esc(manifest.profile_hash||"—")}</p><div class="downloads">${names.map(name=>`<a href="${artifactURL(manifest.run_id,name,true)}">${esc(name)}</a>`).join("")}</div><div class="button-row"><button data-load-run="${esc(manifest.run_id)}">Nạp input run vào bản nháp</button><button data-pin="${esc(manifest.run_id)}">Ghim run để đối chiếu</button></div><details><summary>Config, profile và lệnh tái lập</summary>${jsonBlock({config:manifest.config,profile:manifest.profile,argv:manifest.argv,documents:manifest.documents})}</details></details>`;
}
async function openRun(run) {
  const manifest=await api("/api/runs/"+encodeURIComponent(run)); state.manifest=manifest;
  const operation=manifest.operation; if(["analyze","equilibria","sweep","compare","tests"].includes(operation))switchView(operation);
  renderMetadata(manifest);
  const names=manifest.artifacts.map(a=>a.name);
  if(operation==="tests"&&names.includes("test_results.json")){renderTests(await artifact(run,"test_results.json"),run);labelResult(manifest,$("tests-result"));$("tests-result").dataset.runId=run;return;}
  if(manifest.status!=="succeeded") {
    const target=$(operation+"-result"); if(target){target.innerHTML=`<p class="notice">${esc(labels[manifest.status]||manifest.status)}. Run này không được dùng làm certificate hoàn chỉnh. Log và artifact còn lại có thể tải ở bên dưới.</p>`;labelResult(manifest,target);target.dataset.runId=run;}
    return;
  }
  if(operation==="analyze") {
    const summary=await artifact(run,"summary.json"), responses=await artifact(run,"best_responses.json");
    state.analysis={...summary,best_responses:responses};renderAnalysis(state.analysis);
    const response=await fetch(artifactURL(run,"states.csv"));state.csv=parseCSV(await response.text());renderStates();
  }else if(operation==="equilibria"){state.search=await artifact(run,"equilibria.json");renderSearch();}
  else if(operation==="sweep"){state.sweep=await artifact(run,"sweep.json");state.sweepProfile=manifest.profile;renderSweep();}
  else if(operation==="compare")renderComparison(await artifact(run,"summary.json"));
  const target=$(operation+"-result");if(target){labelResult(manifest,target);target.dataset.runId=run;}
}
function metric(label,value,definition) {return `<div class="metric"><div class="label">${esc(label)}</div><div class="value">${esc(decimal(value))}</div><span class="exact">${esc(value?.exact||"")}</span><span class="help">${esc(definition)}</span></div>`;}
function branchDetails(branch,withWitness=false) {
  const observationRows=[];
  for(const [label,key] of [["L","low"],["H","high"]]) for(const obs of branch[key].observations) observationRows.push([label,esc(obs.observation.join(",")),numeric(obs.probability_given_z),numeric(obs.information_by_report[0]),numeric(obs.information_by_report[1]),esc(obs.optimal_reports.join(" / ")),numeric(obs.optimal_prediction)]);
  return `<details class="certificate"><summary><span>Judge ${esc(branch.judge)} · Z=${branch.z} · ${esc(branch.candidate_action)}</span><span>Regret ${esc(decimal(branch.regret))} · Effort tốt nhất ${esc(branch.best_efforts.join(" / "))}</span></summary>${table(["Candidate utility","Utility L tối ưu","Utility H tối ưu","Delta H−L","Regret"],[[numeric(branch.candidate.utility),numeric(branch.low.utility),numeric(branch.high.utility),numeric(branch.delta_utility),numeric(branch.regret)]])}<p class="help">Optimal actions: ${esc(branch.optimal_actions.join(", "))}. Prediction: ${esc(branch.prediction_optimum)}; report: ${esc(branch.report_optimum)}.</p>${table(["Effort","Observation","P(I|Z)","Info r=0","Info r=1","Optimal reports / ties","Optimal prediction"],observationRows)}${branch.witness?`<h3>Deviation witness</h3>${jsonBlock(branch.witness)}${withWitness?`<button data-witness="${branch.judge}-${branch.z}">Lấy deviation làm candidate mới</button><p class="help">Run mới dựng lại Bayesian predictions cho profile mới. Gain witness thuộc peer tables của run gốc.</p>`:""}`:"<p class='help'>Không có deviation sinh utility cao hơn tại nhánh này.</p>"}<details><summary>Toàn bộ certificate và peer tables đã freeze</summary>${jsonBlock(branch)}</details></details>`;
}
function renderAnalysis(result) {
  const m=result.metrics, good=result.equilibrium_status==="exact_pure_equilibrium";
  $("analyze-result").innerHTML=`<div class="verdict ${good?"":"bad"}"><strong>${good?"Cân bằng thuần trong game M1":"Candidate không phải cân bằng"}</strong>${badge(good?"succeeded":"failed")}</div><p class="help">Kiểm tra đủ 3 Judge × 2 nhánh Z · max regret ${esc(decimal(result.max_regret))}. Phạm vi chỉ pure strategy; không dự đoán cân bằng được chọn.</p><div class="metrics">${metric("Giải ngân sai kỳ vọng",m.wrong_payout_value,"V × P(Y=0,D=1)")}${metric("False approval",m.false_approval_rate,"P(D=1 | Y=0)")}${metric("Accuracy",m.accuracy,"P(D=Y)")}${metric("Cash review cost",m.cash_review_cost,"Reward + operating cost")}</div><h3>Accounting của candidate</h3>${table(["Judge","Expected score","Reward thực chi","Effort cost","Utility"],result.judges.map((r,i)=>["ABC"[i],numeric(r.score),numeric(r.reward),numeric(r.effort_cost),numeric(r.utility)]))}<p>Reward thực chi tổng: <strong>${esc(decimal(m.expected_reward_total))}</strong> · Maximum reward: ${esc(decimal(result.reward_cap))} · Budget: ${esc(decimal(result.reward_budget))}.</p><details><summary>Toàn bộ decision metrics và prediction tables</summary>${jsonBlock({metrics:m,predictions:result.predictions,prediction_semantics:result.prediction_semantics})}</details><h3>Best response theo từng Judge / Z</h3>${result.best_responses.map(b=>branchDetails(b,true)).join("")}<h3>32 trạng thái</h3><div class="filters">${["y","z","decision"].map(key=>`<label>${key}<select id="state-${key}"><option value="">Tất cả</option><option>0</option><option>1</option></select></label>`).join("")}</div><div id="states-table"></div>`;
  ["y","z","decision"].forEach(key=>$("state-"+key).addEventListener("change",renderStates));
}
function parseCSV(text) {
  const rows=[];let row=[],cell="",quoted=false;
  for(let i=0;i<text.length;i++){const c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){cell+='"';i++;}else quoted=!quoted;}else if(c===","&&!quoted){row.push(cell);cell="";}else if(c==="\n"&&!quoted){row.push(cell.replace(/\r$/,""));rows.push(row);row=[];cell="";}else cell+=c;}
  if(cell||row.length){row.push(cell.replace(/\r$/,""));rows.push(row);}const headers=rows.shift()||[];return {headers,rows:rows.map(r=>Object.fromEntries(headers.map((h,i)=>[h,r[i]])))};
}
function renderStates() {
  if(!state.csv||!$("states-table"))return;
  const headers=state.csv.headers,rows=state.csv.rows.filter(row=>["y","z","decision"].every(key=>!$("state-"+key).value||row[key]===$("state-"+key).value));
  $("states-table").innerHTML=`<p class="help">${rows.length}/32 trạng thái. Cột _exact là nguồn số chính xác; _decimal để xem.</p>`+table(headers,rows.map(r=>headers.map(h=>esc(r[h]))),true);
}
function renderSearch() {
  const result=state.search;
  $("equilibria-result").innerHTML=`<div class="verdict"><strong>${result.full_equilibrium_count} tổ hợp cân bằng thuần</strong><span class="tag">432 / 432 branch candidates</span></div><p class="help">Z=0: ${result.branches["0"].equilibrium_count}; Z=1: ${result.branches["1"].equilibrium_count}. ${esc(result.prediction_semantics)}. Prediction có thể là continuum khi thưởng hằng số.</p><fieldset><legend>Chọn hai nhánh để xem full profile</legend>${[0,1].map(z=>`<label for="chosen-z${z}">Z=${z}</label><select id="chosen-z${z}">${result.branches[z].candidates.filter(r=>r.accepted).map(r=>`<option value="${esc(r.id)}">${esc(r.actions.join(" / "))}</option>`).join("")}</select>`).join("")}<div class="button-row"><button id="analyze-combination">Mở tổ hợp để phân tích</button></div></fieldset><div class="filters"><label>Z<select id="search-z"><option value="">Cả hai</option><option>0</option><option>1</option></select></label><label>Trạng thái<select id="search-accepted"><option value="">Tất cả</option><option value="true">Cân bằng</option><option value="false">Bị bác</option></select></label>${["A","B","C"].map(j=>`<label>Action ${j}<select id="search-${j}"><option value="">Tất cả</option>${state.status.actions.map(a=>`<option>${a}</option>`).join("")}</select></label>`).join("")}<label>Effort<select id="search-effort"><option value="">Tất cả</option><option value="all_h">Cả ba H</option><option value="all_l">Cả ba L</option><option value="mixed">Có cả L và H</option>${["A","B","C"].flatMap(j=>["L","H"].map(e=>`<option value="${j}_${e}">${j}=${e}</option>`)).join("")}</select></label></div><div id="search-table"></div><div id="search-certificate"></div>`;
  ["z","accepted","A","B","C","effort"].forEach(key=>$("search-"+key).addEventListener("change",renderSearchTable));
  $("analyze-combination").addEventListener("click",()=>{const p={};for(const z of [0,1])p[z]=result.branches[z].candidates.find(r=>r.id===$("chosen-z"+z).value).actions;putDraft(result.config,p,result.mechanism);switchView("analyze");$("job-detail").textContent="Đã nạp tổ hợp vào bản nháp. Chạy analyze để lấy decision metrics của full profile.";});
  renderSearchTable();
}
function renderSearchTable() {
  const records=Object.values(state.search.branches).flatMap(b=>b.candidates).filter(r=>{
    if($("search-z").value!==""&&String(r.z)!==$("search-z").value)return false;
    if($("search-accepted").value!==""&&String(r.accepted)!==$("search-accepted").value)return false;
    if(!["A","B","C"].every((j,i)=>!$("search-"+j).value||r.actions[i]===$("search-"+j).value))return false;
    const effort=$("search-effort").value;if(!effort)return true;if(effort==="mixed")return new Set(r.actions.map(a=>a[0])).size===2;if(effort.startsWith("all_"))return r.actions.every(a=>a[0]===(effort==="all_h"?"H":"L"));return r.actions["ABC".indexOf(effort[0])][0]===effort[2];
  });
  $("search-table").innerHTML=`<p class="help">${records.length}/432 candidates trong bộ lọc.</p>`+table(["Z","A","B","C","Kết luận","Certificate / witness"],records.map(r=>[r.z,...r.actions.map(esc),badge(r.accepted?"succeeded":"failed"),`<button data-certificate="${esc(r.id)}">Xem chứng cứ</button>`]),true);
}
function renderSweep() {
  const result=state.sweep,axes=Object.keys(result.axes),metrics=["wrong_payout_value","A_z0_delta_utility","A_z1_delta_utility","A_z0_regret","A_z1_regret","expected_reward_total"];
  $("sweep-result").innerHTML=`<p class="run-note">${esc(state.manifest.mechanism)} · run ${esc(state.manifest.run_id)} · profile ${esc(state.manifest.profile_hash)} · ${esc(state.manifest.model_version)}</p><div class="filters"><label>Trục X<select id="chart-x">${axes.map(a=>`<option>${esc(a)}</option>`).join("")}</select></label><label>Trục phân nhóm<select id="chart-series"><option value="">Không</option>${axes.map(a=>`<option>${esc(a)}</option>`).join("")}</select></label><label>Metric<select id="chart-metric">${metrics.map(a=>`<option>${a}</option>`).join("")}</select></label></div><div id="chart-fixed" class="filters"></div><div id="sweep-chart"></div><p class="help">Không nội suy miền chưa tính. Hàng invalid không có metric để vẽ và vẫn được giữ trong bảng.</p>${table(["Điểm",...axes,"Trạng thái","Wrong payout","Delta A Z=0","Delta A Z=1","Candidate","Tái lập"],result.rows.map((r,i)=>[i,...axes.map(a=>numeric(r[a])),esc(r.status+(r.error?": "+r.error:"")),numeric(r.wrong_payout_value),numeric(r.A_z0_delta_utility),numeric(r.A_z1_delta_utility),esc(r.equilibrium_status||"—"),r.status==="valid"?`<button data-sweep-point="${i}">Phân tích điểm</button>`:"—"]),true)}`;
  ["chart-x","chart-series"].forEach(id=>$(id).addEventListener("change",setupChartFilters));$("chart-metric").addEventListener("change",drawChart);setupChartFilters();
}
function axisValue(row,key) {const config=JSON.parse(row.config_json);return key==="c"?config.costs[0]:config[key];}
function setupChartFilters() {
  const x=$("chart-x").value,series=$("chart-series").value;
  $("chart-fixed").innerHTML=Object.entries(state.sweep.axes).filter(([key])=>key!==x&&key!==series).map(([key,values])=>`<label>${esc(key)} cố định<select data-fixed-axis="${key}">${values.map(v=>`<option>${esc(v)}</option>`).join("")}</select></label>`).join("");
  document.querySelectorAll("[data-fixed-axis]").forEach(el=>el.addEventListener("change",drawChart));drawChart();
}
function drawChart() {
  const xkey=$("chart-x").value,ykey=$("chart-metric").value,series=$("chart-series").value;
  const rows=state.sweep.rows.filter(r=>r.status==="valid"&&[...document.querySelectorAll("[data-fixed-axis]")].every(el=>axisValue(r,el.dataset.fixedAxis)===el.value));
  const points=rows.map(r=>({x:r[xkey]?.decimal,y:r[ykey]?.decimal,r})).filter(p=>Number.isFinite(p.x)&&Number.isFinite(p.y));
  if(!points.length){$("sweep-chart").innerHTML='<p class="empty">Không có điểm hợp lệ trong lựa chọn này.</p>';return;}
  const xs=points.map(p=>p.x),ys=points.map(p=>p.y),xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(0,...ys),ymax=Math.max(0,...ys),groups=[...new Set(points.map(p=>series?axisValue(p.r,series):"Tất cả"))],colors=["#20573e","#9a2925","#284e9b","#735213"];
  const px=x=>60+(x-xmin)/(xmax-xmin||1)*590,py=y=>245-(y-ymin)/(ymax-ymin||1)*200;
  $("sweep-chart").innerHTML=`<div class="chart"><svg viewBox="0 0 710 295" role="img" aria-label="${esc(ykey)} theo ${esc(xkey)}; bảng số liệu bên dưới"><line x1="60" y1="35" x2="60" y2="245" stroke="#9cae9d"/><line x1="60" y1="245" x2="660" y2="245" stroke="#9cae9d"/><line x1="60" y1="${py(0)}" x2="660" y2="${py(0)}" stroke="#d7dfd5" stroke-dasharray="4 4"/><text x="4" y="38">${esc(ymax.toFixed(4))}</text><text x="4" y="245">${esc(ymin.toFixed(4))}</text><text x="60" y="275">${esc(xmin)}</text><text x="620" y="275">${esc(xmax)}</text><text x="330" y="292">${esc(xkey)}</text>${points.map(p=>{const group=groups.indexOf(series?axisValue(p.r,series):"Tất cả");return `<circle cx="${px(p.x)}" cy="${py(p.y)}" r="5" fill="${colors[group%colors.length]}"><title>${esc(xkey)}=${esc(p.r[xkey].exact)}; ${esc(ykey)}=${esc(p.r[ykey].exact)}</title></circle><text x="${px(p.x)+8}" y="${py(p.y)-8}">${group+1}</text>`;}).join("")}</svg><p class="help">${groups.map((g,i)=>`${i+1}: ${esc(series||"Series")}=${esc(g)}`).join(" · ")}</p></div>`;
}
function renderComparison(result) {
  const fixed=result.mechanisms.fixed,rbts=result.mechanisms.rbts;
  const keys=["accuracy","false_approval_rate","wrong_payout_value","expected_reward_total","expected_effort_cost","cash_review_cost"];
  $("compare-result").innerHTML=`<p class="notice">Cùng maximum reward ${esc(decimal(result.reward_cap))}. Đây là so sánh candidate cố định, không phải toàn bộ cân bằng.</p>`+table(["Metric","Fixed","RBTS"],keys.map(key=>[key,numeric(fixed.metrics[key]),numeric(rbts.metrics[key])]).concat([["max_regret",numeric(fixed.max_regret),numeric(rbts.max_regret)],["equilibrium_status",esc(fixed.equilibrium_status),esc(rbts.equilibrium_status)]]));
}
function renderTests(result,run) {
  $("tests-result").innerHTML=`<div class="verdict ${result.status==="passed"?"":"bad"}"><strong>${esc(result.status)}</strong><span class="tag">${esc(result.suite)}${result.failure_fixture?" · FIXTURE LỖI CÔNG KHAI":""}</span></div><p>${Object.entries(result.counts).map(([key,value])=>`${esc(key)}: <strong>${value}</strong>`).join(" · ")}</p><p class="help">Thời gian ${result.duration_seconds==null?"không có":result.duration_seconds.toFixed(3)+"s"}. Browser acceptance executed: ${esc(result.browser_acceptance_executed)}.</p>${table(["T-ID","Test thực thi","Trạng thái","Thời gian","Assertion / evidence"],result.records.map(r=>[esc(r.test_id||"fixture"),esc(r.unittest_id||"reference / unavailable"),badge(r.status),esc(r.duration_seconds?.toFixed(3)||"—"),r.assertion_or_error||r.evidence?`<details><summary>Xem</summary>${jsonBlock({assertion:r.assertion_or_error,evidence:r.evidence})}</details>`:"—"]))}<a href="${artifactURL(run,"test_log.txt",true)}">Tải test_log.txt thật</a>`;
  if(result.reference_results)$("tests-result").insertAdjacentHTML("beforeend",`<details><summary>Kết quả reference mới từ checker</summary>${jsonBlock(result.reference_results)}</details><a href="${artifactURL(run,"reference_results.json",true)}">Tải reference_results.json của run này</a>`);
}
async function refreshHistory() {
  const {runs}=await api("/api/runs");
  $("history-result").innerHTML=runs.length?table(["Run / UTC","Tác vụ","Cơ chế","Trạng thái","Config hash","Thao tác"],runs.map(r=>[`${esc(r.run_id)}<br><span class="help">${esc(r.created_at_utc)}</span>`,esc(r.operation),esc(r.mechanism||"—"),badge(r.status),`<span class="exact">${esc(r.config_hash||"—")}</span>`,`<button data-open-run="${esc(r.run_id)}">Mở</button> <button data-pin="${esc(r.run_id)}">${state.pinned.includes(r.run_id)?"Bỏ ghim":"Ghim"}</button>`]),true):'<p class="empty">Chưa có run được lưu.</p>';
}
async function renderPinned() {
  if(state.pinned.length!==2){$("pinned-result").innerHTML=`<p class="empty">Đã ghim ${state.pinned.length}/2 run.</p>`;return;}
  const manifests=await Promise.all(state.pinned.map(id=>api("/api/runs/"+encodeURIComponent(id))));
  const differences=["model_version","config_hash","profile_hash"].filter(k=>manifests[0][k]!==manifests[1][k]);
  const summaries=await Promise.all(manifests.map(m=>m.status==="succeeded"&&m.artifacts.some(a=>a.name==="summary.json")?artifact(m.run_id,"summary.json"):null));
  const rows=["accuracy","false_approval_rate","wrong_payout_value","expected_reward_total"].map(key=>[key,...summaries.map(s=>s?.metrics?numeric(s.metrics[key]):"Không có metric analyze")]);
  $("pinned-result").innerHTML=`<p class="notice">${differences.length?"Các run khác "+esc(differences.join(", "))+"; không gắn nhãn so sánh có kiểm soát.":"Cùng model/config/profile. Kiểm tra cơ chế và trạng thái trước khi diễn giải."}</p>${table(["Metric",...manifests.map(m=>m.run_id+" · "+m.mechanism)],rows)}<details><summary>Khác biệt input và phiên bản</summary>${jsonBlock(manifests.map(m=>({run_id:m.run_id,model:m.model_version,config:m.config,profile:m.profile,status:m.status,mechanism:m.mechanism})))}</details>`;
}
async function handleClick(event) {
  const button=event.target.closest("button");if(!button)return;
  try {
    if(button.dataset.view){switchView(button.dataset.view);return;}
    if(button.dataset.operation){await submit(button.dataset.operation);return;}
    if(button.dataset.openRun){await openRun(button.dataset.openRun);return;}
    if(button.dataset.loadRun){const m=await api("/api/runs/"+encodeURIComponent(button.dataset.loadRun));if(!m.config||!m.profile)throw new Error("Run này không có full config/profile để nạp.");putDraft(m.config,m.profile,m.mechanism);switchView("analyze");return;}
    if(button.dataset.pin){const id=button.dataset.pin;state.pinned=state.pinned.includes(id)?state.pinned.filter(r=>r!==id):[...state.pinned.slice(-1),id];await refreshHistory();await renderPinned();return;}
    if(button.dataset.witness){const [judge,z]=button.dataset.witness.split("-");const b=state.analysis.best_responses.find(r=>r.judge===judge&&String(r.z)===z);const p=copy(state.analysis.profile);p[z]["ABC".indexOf(judge)]=b.witness.action;putDraft(state.analysis.config,p,state.analysis.mechanism);$("job-detail").textContent="Đã nạp deviation. Run mới sẽ dựng prediction của candidate mới; witness gốc vẫn giữ nguyên.";return;}
    if(button.dataset.certificate){const r=Object.values(state.search.branches).flatMap(b=>b.candidates).find(r=>r.id===button.dataset.certificate);$("search-certificate").innerHTML=`<h3>${esc(r.id)} · ${r.accepted?"Cân bằng":"Bị bác"}</h3>`+r.certificates.map(c=>branchDetails(c)).join("");$("search-certificate").scrollIntoView({block:"start"});return;}
    if(button.dataset.sweepPoint!==undefined){const row=state.sweep.rows[Number(button.dataset.sweepPoint)];putDraft(JSON.parse(row.config_json),state.sweepProfile,state.manifest.mechanism);switchView("analyze");return;}
    if(button.id==="cancel"&&state.active){button.disabled=true;updateJob(await api("/api/jobs/"+encodeURIComponent(state.active)+"/cancel",{}));return;}
    if(button.id==="validate"){clearErrors();await api("/api/validate",{operation:"analyze",...readDraft()});$("job-detail").textContent="Đầu vào hợp lệ theo validator của engine.";return;}
    if(button.id==="equal-cap"){const response=await api("/api/validate",{operation:"analyze",...readDraft()});$(fieldId("fixed_reward")).value=response.comparison_fixed_reward;changed();$("job-detail").textContent="Đã chủ động đặt F=f+2λ theo kết quả exact từ engine.";return;}
    if(button.id==="export"){const link=document.createElement("a");const url=URL.createObjectURL(new Blob([JSON.stringify(readDraft(),null,2)],{type:"application/json"}));link.href=url;link.download="ceav-m1-inputs.json";link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);return;}
    if(button.id==="refresh-history")await refreshHistory();
  }catch(error){showError(error);}
}

setupForms();previewGrid();
document.addEventListener("click",handleClick);
$("config-form").addEventListener("submit",event=>event.preventDefault());
$("config-form").addEventListener("input",changed);$("config-form").addEventListener("change",changed);$("mechanism").addEventListener("change",changed);
$("sweep-axes").addEventListener("input",previewGrid);$("sweep-axes").addEventListener("change",previewGrid);
$("suite").addEventListener("change",()=>$("test-selection").hidden=$("suite").value!=="selected");
$("preset").addEventListener("change",()=>{const name=$("preset").value;const profileName=name==="golden_g2"?"all_z":name==="asymmetric"?"asymmetric_profile":"all_high";putDraft(state.status.presets[name],state.status.presets[profileName],"rbts");$("quick-profile").value=profileName;});
$("quick-profile").addEventListener("change",()=>putDraft(readDraft().config,state.status.presets[$("quick-profile").value],readDraft().mechanism));
$("import").addEventListener("change",async event=>{
  try{clearErrors();const file=event.target.files[0];if(!file)return;const input=JSON.parse(await file.text());const current=readDraft();const wrapper="config" in input; if(wrapper&&Object.keys(input).some(k=>!["config","profile","mechanism"].includes(k)))throw new Error("Field không được hỗ trợ trong input wrapper.");const config=wrapper?input.config:input["0"]?current.config:input;const profile=wrapper?(input.profile||current.profile):input["0"]?input:current.profile;const mechanism=input.mechanism||current.mechanism;await api("/api/validate",{operation:"analyze",config,profile,mechanism});putDraft(config,profile,mechanism);$("job-detail").textContent="Đã nhập JSON hợp lệ; các chuỗi số được giữ nguyên.";}catch(error){showError(error);}finally{event.target.value="";}
});
api("/api/status").then(status=>{state.status=status;$("connection").textContent=`Engine sẵn sàng · ${status.model_version}`;putDraft(status.presets.golden_g1,status.presets.all_high,"rbts");state.runRevision=null;$("stale").hidden=true;document.querySelectorAll(".run").forEach(b=>b.disabled=false);if(status.active_job){state.active=status.active_job.job_id;updateJob(status.active_job);poll(state.active);}}).catch(error=>{$("connection").textContent="Không kết nối được engine";showError(error);});
