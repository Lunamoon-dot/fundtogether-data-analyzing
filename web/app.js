"use strict";

const $ = id => document.getElementById(id);
const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const copy = value => JSON.parse(JSON.stringify(value));
const state = {view:"analyze", status:null, active:null, revision:0, runRevision:null, analysis:null, search:null, sweep:null, incentives:null, robustness:null, calibration:null, calibrationDataset:null, manifest:null, pinned:[], drafts:{}, activeModel:"ceav-m1-v3.2"};
const labels = {queued:"Đang chờ",running:"Đang chạy",succeeded:"Thành công",failed:"Thất bại",cancelled:"Đã hủy",interrupted:"Bị gián đoạn"};
const legacyRewardFields = [
  ["f","f · Reward cơ bản","0","reward"], ["lambda","λ · Hệ số RBTS","1","reward"], ["fixed_reward","F · Fixed reward","2","reward"],
  ["reward_budget","B · Trần ngân sách","6","reward"], ["payout_value","V · Giá trị payout","1","reward"], ["operating_cost","Operating cost","0","reward"]
];
const v3RewardFields = [
  ["f","f · Reward cơ bản","1/10","reward"], ["lambda_peer","λ_peer · Trọng số RBTS","1/2","reward"],
  ["anchor_weight","μ_anchor · Trọng số kiểm chứng","4/5","reward"], ["reward_budget","B · Trần ngân sách","6","reward"],
  ["payout_value","V · Giá trị payout","1","reward"], ["operating_cost","Operating cost","0","reward"]
];
const modelFields = {
  "ceav-m1-v1.0":[["pi","π · P(Y=1)","1/2","model"],["a","a · P(Z=Y)","7/10","model"],["b","b · P(Xᵢ=Y)","4/5","model"],["costs[0]","c_A · Chi phí A","1/20","model"],["costs[1]","c_B · Chi phí B","1/20","model"],["costs[2]","c_C · Chi phí C","1/20","model"]],
  "ceav-m1-v2.0":[["pi","Prior π · P(Y=1)","1/2","model"],["public_signal.sensitivity","Sensitivity · P(Z=1 | Y=1)","4/5","model"],["public_signal.specificity","Specificity · P(Z=0 | Y=0)","3/5","model"],...["A","B","C"].flatMap((judge,i)=>[[`judges.${judge}.private_signal.sensitivity`,`Sensitivity · P(X_${judge}=1 | Y=1)`,["9/10","3/4","13/20"][i],"model"],[`judges.${judge}.private_signal.specificity`,`Specificity · P(X_${judge}=0 | Y=0)`,["4/5","19/20","7/10"][i],"model"],[`judges.${judge}.high_effort_cost`,`Chi phí High Effort · c_${judge}`,["1/20","1/10","1/25"][i],"model"]])],
  "ceav-m1-v3.0":[["pi","Prior π · P(Y=1)","1/2","model"],["public_signal.sensitivity","Sensitivity · P(Z=1 | Y=1)","4/5","model"],["public_signal.specificity","Specificity · P(Z=0 | Y=0)","3/5","model"],...["A","B","C"].flatMap((judge,i)=>[[`judges.${judge}.private_signal.sensitivity`,`Sensitivity · P(X_${judge}=1 | Y=1)`,["9/10","3/4","13/20"][i],"model"],[`judges.${judge}.private_signal.specificity`,`Specificity · P(X_${judge}=0 | Y=0)`,["4/5","19/20","7/10"][i],"model"],[`judges.${judge}.high_effort_cost`,`Chi phí High Effort · c_${judge}`,["1/20","1/10","1/25"][i],"model"]]),["verification_anchor.audit_probability","Xác suất audit · q","1/5","model"],["verification_anchor.sensitivity","Anchor sensitivity · P(T=1 | Y=1)","9/10","model"],["verification_anchor.specificity","Anchor specificity · P(T=0 | Y=0)","9/10","model"],["verification_anchor.cost_per_audit","Chi phí mỗi audit · κ_audit","0","model"]],
  "ceav-m1-v3.2":[["pi","Prior π · P(Y=1)","1/2","model"],["public_signal.sensitivity","Sensitivity · P(Z=1 | Y=1)","4/5","model"],["public_signal.specificity","Specificity · P(Z=0 | Y=0)","3/5","model"],...["A","B","C"].flatMap((judge,i)=>[[`judges.${judge}.private_signal.sensitivity`,`Sensitivity · P(X_${judge}=1 | Y=1)`,["9/10","3/4","13/20"][i],"model"],[`judges.${judge}.private_signal.specificity`,`Specificity · P(X_${judge}=0 | Y=0)`,["4/5","19/20","7/10"][i],"model"],[`judges.${judge}.high_effort_cost`,`Chi phí High Effort · c_${judge}`,["1/20","1/10","1/25"][i],"model"]]),["verification_anchor.audit_probability_by_report.0","Audit nếu report 0 · q0","1/4","model"],["verification_anchor.audit_probability_by_report.1","Audit nếu report 1 · q1","3/4","model"],["verification_anchor.sensitivity","Anchor sensitivity · P(T=1 | Y=1)","9/10","model"],["verification_anchor.specificity","Anchor specificity · P(T=0 | Y=0)","9/10","model"],["verification_anchor.cost_per_audit","Chi phí mỗi audit · κ_audit","1/5","model"]]
};
const sweepAxes = {"ceav-m1-v1.0":["pi","a","b","c","lambda"],"ceav-m1-v2.0":["pi","public_signal.sensitivity","public_signal.specificity","judges.A.private_signal.sensitivity","judges.A.private_signal.specificity","judges.A.high_effort_cost","judges.B.private_signal.sensitivity","judges.B.private_signal.specificity","judges.B.high_effort_cost","judges.C.private_signal.sensitivity","judges.C.private_signal.specificity","judges.C.high_effort_cost","lambda"],"ceav-m1-v3.0":["pi","public_signal.sensitivity","public_signal.specificity","judges.A.private_signal.sensitivity","judges.A.private_signal.specificity","judges.A.high_effort_cost","judges.B.private_signal.sensitivity","judges.B.private_signal.specificity","judges.B.high_effort_cost","judges.C.private_signal.sensitivity","judges.C.private_signal.specificity","judges.C.high_effort_cost","verification_anchor.audit_probability","verification_anchor.sensitivity","verification_anchor.specificity","verification_anchor.cost_per_audit","lambda_peer","anchor_weight"],"ceav-m1-v3.2":["pi","public_signal.sensitivity","public_signal.specificity","verification_anchor.audit_probability_by_report.0","verification_anchor.audit_probability_by_report.1","verification_anchor.sensitivity","verification_anchor.specificity","verification_anchor.cost_per_audit","lambda_peer","anchor_weight"]};
const incentiveAxes = [...sweepAxes["ceav-m1-v2.0"],"reward_budget"];
const rewardFields = () => ["ceav-m1-v3.0","ceav-m1-v3.2"].includes(state.activeModel)?v3RewardFields:legacyRewardFields;
const fields = () => [...modelFields[state.activeModel],...rewardFields()];
const fieldId = name => "field-" + name.replace(/[^a-zA-Z0-9]/g,"-");
const axisId = name => name.replace(/[^a-zA-Z0-9]/g,"-");
const decimal = value => value && typeof value === "object" && "exact" in value ? (value.decimal == null ? value.exact : Number(value.decimal).toLocaleString("vi-VN",{maximumFractionDigits:8})) : String(value ?? "—");
const numeric = value => value && typeof value === "object" && "exact" in value ? `<span>${esc(decimal(value))}</span><span class="exact">${esc(value.exact)}</span>` : esc(value ?? "—");
const badge = status => `<span class="status-badge status-${esc(status)}">${esc(labels[status] || status)}</span>`;
const jsonBlock = value => `<pre class="code">${esc(JSON.stringify(value,null,2))}</pre>`;
const table = (headers, rows, tall=false) => `<div class="table-wrap ${tall?"scroll-tall":""}" tabindex="0" role="region" aria-label="Bảng dữ liệu cuộn ngang"><table><thead><tr>${headers.map(h=>`<th scope="col">${esc(h)}</th>`).join("")}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(cell=>`<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;

function setupForms() {
  for (const z of [0,1]) {
    const row=document.createElement("div"); row.className="profile-row";
    row.innerHTML=`<span class="help">Z=${z}</span>`+["A","B","C"].map((judge,i)=>`<div><label for="action-${z}-${i}">${judge}</label><select id="action-${z}-${i}">${["L0","L1","H00","H01","H10","H11"].map(a=>`<option ${a==="H01"?"selected":""}>${a}</option>`).join("")}</select></div>`).join("");
    $("profile-editor").append(row);
  }
  for (let i=1;i<=32;i++) {
    const id="T"+String(i).padStart(2,"0"); const label=document.createElement("label"); label.className="check";
    label.innerHTML=`<input type="checkbox" value="${id}" ${i<=5?"checked":""}>${id}`; $("test-ids").append(label);
  }
  for(let i=1;i<=15;i++){const id="V2-T"+String(i).padStart(2,"0"),label=document.createElement("label");label.className="check";label.innerHTML=`<input type="checkbox" value="${id}">${id}`;$("test-ids").append(label);}
  for(let i=1;i<=8;i++){const id="CAL-T"+String(i).padStart(2,"0"),label=document.createElement("label");label.className="check";label.innerHTML=`<input type="checkbox" value="${id}">${id}`;$("test-ids").append(label);}
  for(let i=1;i<=8;i++){const id="INC-T"+String(i).padStart(2,"0"),label=document.createElement("label");label.className="check";label.innerHTML=`<input type="checkbox" value="${id}">${id}`;$("test-ids").append(label);}
  for(let i=1;i<=12;i++){const id="V3-T"+String(i).padStart(2,"0"),label=document.createElement("label");label.className="check";label.innerHTML=`<input type="checkbox" value="${id}">${id}`;$("test-ids").append(label);}
  for(let i=1;i<=10;i++){const id="ROB-T"+String(i).padStart(2,"0"),label=document.createElement("label");label.className="check";label.innerHTML=`<input type="checkbox" value="${id}">${id}`;$("test-ids").append(label);}
  for(let i=1;i<=10;i++){const id="V32-T"+String(i).padStart(2,"0"),label=document.createElement("label");label.className="check";label.innerHTML=`<input type="checkbox" value="${id}">${id}`;$("test-ids").append(label);}
  renderModelFields(state.activeModel);
}

function renderModelFields(version) {
  state.activeModel=version;$("model-version").value=version;const container=$("model-fields");container.innerHTML="";
  if(version!=="ceav-m1-v1.0"){
    const definitions=Object.fromEntries(modelFields[version].map(field=>[field[0],field]));
    const groups=[
      ["Prior và tín hiệu chung Z",["pi","public_signal.sensitivity","public_signal.specificity"],"model-group-public"],
      ...["A","B","C"].map(judge=>[`Judge ${judge} · tín hiệu riêng`,[`judges.${judge}.private_signal.sensitivity`,`judges.${judge}.private_signal.specificity`,`judges.${judge}.high_effort_cost`],"model-group-judge"]),
      ...(version==="ceav-m1-v3.0"?[["Verification anchor sau report",["verification_anchor.audit_probability","verification_anchor.sensitivity","verification_anchor.specificity","verification_anchor.cost_per_audit"],"model-group-anchor"]]:version==="ceav-m1-v3.2"?[["Spot-check phụ thuộc report",["verification_anchor.audit_probability_by_report.0","verification_anchor.audit_probability_by_report.1","verification_anchor.sensitivity","verification_anchor.specificity","verification_anchor.cost_per_audit"],"model-group-anchor"]]:[])
    ];
    container.innerHTML=groups.map(([title,names,className])=>`<fieldset class="model-group ${className}"><legend>${esc(title)}</legend><div class="model-group-fields">${names.map(name=>{const [,label,value]=definitions[name],parts=label.split(" · ");return `<div class="model-field"><label for="${fieldId(name)}"><span class="model-field-name">${esc(parts[0])}</span><span class="model-field-formula">${esc(parts[1])}</span></label><input type="text" id="${fieldId(name)}" data-field="${esc(name)}" value="${esc(value)}" aria-describedby="${fieldId(name)}-error"><span class="field-error" id="${fieldId(name)}-error"></span></div>`;}).join("")}</div></fieldset>`).join("");
  }else for(const [name,label,value] of modelFields[version]){const wrapper=document.createElement("div");wrapper.innerHTML=`<label for="${fieldId(name)}">${esc(label)}</label><input type="text" id="${fieldId(name)}" data-field="${esc(name)}" value="${esc(value)}" aria-describedby="${fieldId(name)}-error"><span class="field-error" id="${fieldId(name)}-error"></span>`;container.append(wrapper);}
  const reward=$("reward-fields");reward.innerHTML="";for(const [name,label,value] of rewardFields()){const wrapper=document.createElement("div");wrapper.innerHTML=`<label for="${fieldId(name)}">${esc(label)}</label><input type="text" id="${fieldId(name)}" data-field="${esc(name)}" value="${esc(value)}" aria-describedby="${fieldId(name)}-error"><span class="field-error" id="${fieldId(name)}-error"></span>`;reward.append(wrapper);}
  const v3=["ceav-m1-v3.0","ceav-m1-v3.2"].includes(version);for(const option of $("mechanism").options)option.disabled=v3?option.value!=="hybrid_anchor":option.value==="hybrid_anchor";$("mechanism").value=v3?"hybrid_anchor":($("mechanism").value==="hybrid_anchor"?"rbts":$("mechanism").value);
  $("model-help").textContent=version==="ceav-m1-v1.0"?"V1: a và b là xác suất tín hiệu bằng Y ở cả hai lớp Y. Nhập chuỗi như 0.05 hoặc 1/20.":version==="ceav-m1-v2.0"?"V2: sensitivity/specificity riêng. Reward chỉ dựa trên peer.":version==="ceav-m1-v3.2"?"V3.2: mỗi Judge có audit riêng; xác suất audit là q0 hoặc q1 tùy report. T chỉ xuất hiện sau khi report khóa.":"V3: T chỉ xuất hiện sau khi report khóa. Reward tách peer score và verification anchor; Y không được đưa cho Judge.";
  $("sweep-axes").innerHTML="";for(const axis of sweepAxes[version]){const primary=axis==="lambda"||axis==="anchor_weight";const row=document.createElement("div");row.className="axis-row";row.innerHTML=`<label class="check" for="axis-${axisId(axis)}-enabled"><input type="checkbox" id="axis-${axisId(axis)}-enabled" ${primary?"checked":""}>${esc(axis)}</label><input type="text" id="axis-${axisId(axis)}" aria-label="Giá trị axis ${esc(axis)}" value="${axis==="lambda"?"0, 1/2, 1, 2":axis==="anchor_weight"?"0, 4/5, 2":"1/2, 4/5"}">`;$("sweep-axes").append(row);}
  $("incentive-axes").innerHTML="";for(const axis of incentiveAxes){const row=document.createElement("div");row.className="axis-row";const checked=axis==="lambda";const value=axis==="lambda"?"1/2, 3/4, 19/20":axis==="reward_budget"?"6":"1/20, 1/10";row.innerHTML=`<label class="check" for="incentive-axis-${axisId(axis)}-enabled"><input type="checkbox" id="incentive-axis-${axisId(axis)}-enabled" ${checked?"checked":""}>${esc(axis)}</label><input type="text" id="incentive-axis-${axisId(axis)}" aria-label="Giá trị incentive axis ${esc(axis)}" value="${esc(value)}">`;$("incentive-axes").append(row);}
  renderPresets(version);previewGrid();previewIncentiveGrid();
}
function renderPresets(version){if(!state.status)return;const names=version==="ceav-m1-v1.0"?["golden_g1","golden_g2","golden_g3","golden_g4","asymmetric"]:version==="ceav-m1-v2.0"?["heterogeneous","symmetric_g1","below_half"]:version==="ceav-m1-v3.2"?["report_sensitive_base"]:["heterogeneous_anchor","anchor_dominant_q50"];const labels={golden_g1:"G1 · High/low cùng tồn tại",golden_g2:"G2 · Theo tín hiệu chung",golden_g3:"G3 · Chi phí quá cao",golden_g4:"G4 · Lệch theo Z",asymmetric:"V1 · Chi phí bất đối xứng",heterogeneous:"V2 · Ba Judge khác nhau",symmetric_g1:"V2 · Quy hồi G1",below_half:"V2 · Kênh dưới 1/2",heterogeneous_anchor:"V3 · Baseline hybrid",anchor_dominant_q50:"V3 · Experimental anchor q=50%",report_sensitive_base:"V3.2 · q0/q1 report-sensitive"};$("preset").innerHTML=names.map(name=>`<option value="${name}">${labels[name]}</option>`).join("");}
function getPath(object,path){if(path.startsWith("costs["))return object.costs?.[Number(path[6])];return path.split(".").reduce((value,key)=>value?.[key],object);}
function setPath(object,path,value){if(path.startsWith("costs[")){object.costs??=[];object.costs[Number(path[6])]=value;return;}const parts=path.split(".");let target=object;for(const part of parts.slice(0,-1))target=target[part]??=(part==="judges"||part==="private_signal"||part==="public_signal"||["A","B","C"].includes(part)?{}:{});target[parts.at(-1)]=value;}

function readDraft() {
  const config={model_version:state.activeModel};if(state.activeModel==="ceav-m1-v1.0")config.costs=[];else{config.public_signal={};config.judges={A:{private_signal:{}},B:{private_signal:{}},C:{private_signal:{}}};if(["ceav-m1-v3.0","ceav-m1-v3.2"].includes(state.activeModel))config.verification_anchor={};}
  for (const [name] of fields()) {
    const value=$(fieldId(name)).value.trim();
    setPath(config,name,value);
  }
  const profile={}; for(const z of [0,1]) profile[z]=[0,1,2].map(i=>$("action-"+z+"-"+i).value);
  const rawScenario=$("scenario-json").value.trim();const scenario=rawScenario?JSON.parse(rawScenario):null;
  return {config,profile,mechanism:$("mechanism").value,scenario};
}
function putDraft(config,profile,mechanism,scenario) {
  if(config.model_version!==state.activeModel)renderModelFields(config.model_version);
  for(const [name] of fields()) $(fieldId(name)).value=getPath(config,name)??"0";
  for(const z of [0,1]) for(let i=0;i<3;i++) $("action-"+z+"-"+i).value=profile[z][i];
  if(mechanism) $("mechanism").value=mechanism;
  if(scenario!==undefined)$("scenario-json").value=scenario?JSON.stringify(scenario,null,2):"";
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
  $("errors").textContent=messages.map(e=>(e.field?e.field+": ":"")+(e.row?`dòng ${e.row}: `:"")+e.message).join(" · "); $("errors").hidden=false;
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
  $("draft").hidden=["calibration","robustness","tests","history"].includes(view); $("layout").classList.toggle("full",$("draft").hidden);
  if(view==="history") refreshHistory().catch(showError);
  if(view==="compare") renderPinned().catch(showError);
  if(view==="tests") api("/api/browser-evidence").then(data=>{
    $("browser-evidence").innerHTML=data.records.length?data.records.map(record=>`<p><a href="${artifactURL(record.run_id,"browser_results.json",true)}">${esc(record.scenario)}</a> · ${esc(record.status)} · source engine/web/presets ${record.source_matches?"khớp":"đã thay đổi"} · ${esc(record.browser)} · ${esc(record.viewport.width)}×${esc(record.viewport.height)}</p>`).join(""):"Chưa có evidence trình duyệt. Các nhóm chưa chạy không được tính là pass.";
  }).catch(showError);
}
function readAxes() {
  const axes={}; for(const key of sweepAxes[state.activeModel]) if($("axis-"+axisId(key)+"-enabled").checked) axes[key]=$("axis-"+axisId(key)).value.split(",").map(v=>v.trim()).filter(Boolean);
  return axes;
}
function previewGrid() {const axes=readAxes(); const count=Object.keys(axes).length?Object.values(axes).reduce((a,b)=>a*b.length,1):0;$("grid-preview").textContent=`${count} điểm · profile và cơ chế giữ cố định.`;}
function readIncentiveAxes(){const axes={};for(const key of incentiveAxes)if($("incentive-axis-"+axisId(key)+"-enabled").checked)axes[key]=$("incentive-axis-"+axisId(key)).value.split(",").map(v=>v.trim()).filter(Boolean);return axes;}
function previewIncentiveGrid(){const axes=readIncentiveAxes(),count=Object.keys(axes).length?Object.values(axes).reduce((a,b)=>a*b.length,1):1;$("incentive-grid-preview").textContent=`${count} điểm · ${count*432} branch candidates nếu mọi điểm hợp lệ.`;}
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
  let request;
  if(operation==="tests")request={operation,suite:$("suite").value,test_ids:[...$("test-ids").querySelectorAll("input:checked")].map(e=>e.value),failure_fixture:$("suite").value==="selected"&&$("failure-fixture").checked};
  else if(operation==="calibrate"){
    if(!state.calibrationDataset)throw new Error("Hãy chọn CSV hoặc dùng dataset synthetic mẫu trước.");
    const base=state.activeModel==="ceav-m1-v2.0"?readDraft().config:(state.drafts["ceav-m1-v2.0"]?.config||state.status.v2_presets.heterogeneous);
    request={operation,dataset_csv:state.calibrationDataset.text,source_name:state.calibrationDataset.name,provenance_status:$("calibration-provenance").value,base_config:base,mechanism:"rbts"};
  }else request={operation,...readDraft()};
  if(operation==="robustness")request={operation,study:copy(state.status.robustness_studies[$("robustness-study").value])};
  if(operation==="sweep")request.axes=readAxes();
  if(operation==="incentives"){const draft=state.drafts["ceav-m1-v2.0"]||{config:state.status.v2_presets.heterogeneous,profile:state.status.presets.all_high,scenario:null};request={operation,config:draft.config,profile:draft.profile,scenario:draft.scenario,mechanism:"rbts",axes:readIncentiveAxes()};}
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
  const load=["calibrate","robustness","tests"].includes(manifest.operation)?"":`<button data-load-run="${esc(manifest.run_id)}">Nạp input run vào bản nháp</button>`;
  $("run-metadata").innerHTML=`<details open><summary>Run ${esc(manifest.run_id)} · ${badge(manifest.status)}</summary><p class="run-note">${esc(manifest.operation)} · model ${esc(manifest.model_version)} · spec ${esc(manifest.spec?.revision)} · freeze ${esc(manifest.spec?.freeze_status)}<br>engine/source ${esc(manifest.engine_revision)}<br>config ${esc(manifest.config_hash||"—")} · profile ${esc(manifest.profile_hash||"—")} · scenario ${esc(manifest.scenario_hash||"not_provided")}</p><div class="downloads">${names.map(name=>`<a href="${artifactURL(manifest.run_id,name,true)}">${esc(name)}</a>`).join("")}</div><div class="button-row">${load}<button data-pin="${esc(manifest.run_id)}">Ghim run để đối chiếu</button></div><details><summary>Config, profile, scenario và lệnh tái lập</summary>${jsonBlock({config:manifest.config,profile:manifest.profile,scenario:manifest.scenario||null,argv:manifest.argv,documents:manifest.documents,calibration:manifest.calibration||null,incentive_diagnostics:manifest.incentive_diagnostics||null})}</details></details>`;
}
async function openRun(run) {
  const manifest=await api("/api/runs/"+encodeURIComponent(run)); state.manifest=manifest;
  const operation=manifest.operation; if(["analyze","equilibria","sweep","incentives","robustness","compare","tests","calibrate"].includes(operation))switchView(operation==="calibrate"?"calibration":operation);
  renderMetadata(manifest);
  const names=manifest.artifacts.map(a=>a.name);
  if(operation==="tests"&&names.includes("test_results.json")){renderTests(await artifact(run,"test_results.json"),run);labelResult(manifest,$("tests-result"));$("tests-result").dataset.runId=run;return;}
  if(manifest.status!=="succeeded") {
    const target=$(operation+"-result"); if(target){target.innerHTML=`<p class="notice">${esc(labels[manifest.status]||manifest.status)}. Run này không được dùng làm certificate hoàn chỉnh. Log và artifact còn lại có thể tải ở bên dưới.</p>`;labelResult(manifest,target);target.dataset.runId=run;}
    return;
  }
  if(operation==="calibrate"){state.calibration=await artifact(run,"calibration.json");renderCalibration(state.calibration);}
  else if(operation==="analyze") {
    const summary=await artifact(run,"summary.json"), responses=await artifact(run,"best_responses.json");
    state.analysis={...summary,best_responses:responses};renderAnalysis(state.analysis);
    const response=await fetch(artifactURL(run,"states.csv"));state.csv=parseCSV(await response.text());renderStates();
  }else if(operation==="equilibria"){state.search=await artifact(run,"equilibria.json");renderSearch();}
  else if(operation==="sweep"){state.sweep=await artifact(run,"sweep.json");state.sweepProfile=manifest.profile;renderSweep();}
  else if(operation==="incentives"){state.incentives={diagnostics:await artifact(run,"incentive_diagnostics.json"),sweep:await artifact(run,"incentive_sweep.json")};renderIncentives();}
  else if(operation==="robustness"){state.robustness=await artifact(run,"robustness.json");renderRobustness(state.robustness);}
  else if(operation==="compare")renderComparison(await artifact(run,"summary.json"));
  const target=$(operation+"-result");if(target){labelResult(manifest,target);target.dataset.runId=run;}
}
function renderCalibration(result) {
  const rows=[["Tín hiệu chung Z","sensitivity",result.estimates.public_signal.sensitivity],["Tín hiệu chung Z","specificity",result.estimates.public_signal.specificity]];
  for(const judge of ["A","B","C"]){const item=result.estimates.judges[judge];rows.push([`Judge ${judge}`,"sensitivity",item.private_signal.sensitivity],[`Judge ${judge}`,"specificity",item.private_signal.specificity],[`Judge ${judge}`,"high_effort_cost",item.high_effort_cost]);}
  $("calibrate-result").innerHTML=`<div class="verdict"><strong>Đã tạo config V2 từ ${result.row_count} case</strong>${badge("succeeded")}</div><div class="metrics">${metric("Y=1",{exact:String(result.class_counts["1"]),decimal:result.class_counts["1"]},"Số case positive")}${metric("Y=0",{exact:String(result.class_counts["0"]),decimal:result.class_counts["0"]},"Số case negative")}${metric("π",{exact:result.estimates.pi.value,decimal:Number(result.class_counts["1"])/result.row_count},"Tỷ lệ Y=1 trong dataset")}${metric("Provenance",null,result.provenance_status)}</div>${table(["Kênh","Estimate","Numerator / denominator","Exact"],rows.map(([channel,name,value])=>[esc(channel),esc(name),`${value.numerator} / ${value.denominator}`,esc(value.value)]))}<p class="notice">${result.warnings.map(esc).join(" ")}</p><div class="button-row"><button id="apply-calibration" class="primary">Nạp config vào Phân tích</button></div><details><summary>Generated config và identity dataset</summary>${jsonBlock({dataset_hash:result.dataset_hash,raw_sha256:result.raw_sha256,config:result.config})}</details>`;
}
function renderIncentives(){
  const diagnostics=state.incentives.diagnostics,sweep=state.incentives.sweep;
  const statusLabel={PREFERRED:"High có lợi",TIED:"Hòa",NOT_PREFERRED:"Low có lợi",SIGNAL_DEPENDENT_ONLY:"Best report dùng X",SIGNAL_IGNORED_ONLY:"Best report bỏ qua X",TIE_DEPENDENT_AND_IGNORED:"Hòa: dùng hoặc bỏ qua X"};
  const cards=diagnostics.branches.map(row=>`<article class="diagnostic-card"><div class="section-heading"><h3>Judge ${esc(row.judge)} · Z=${row.z}</h3>${badge(row.effort.best_high_status==="PREFERRED"?"succeeded":row.effort.best_high_status==="TIED"?"queued":"failed")}</div><p><strong>${esc(statusLabel[row.effort.best_high_status])}</strong> · ${esc(statusLabel[row.report.status])}</p>${table(["Đại lượng","Giá trị"],[["V_L · best Low",numeric(row.low_score)],["V_H · best High",numeric(row.best_high_score)],["V_H_dep · H01/H10",numeric(row.dependent_high_score)],["Giá trị thông tin tốt nhất",numeric(row.information_gain_best)],["Khoảng report bỏ qua X",numeric(row.report_utilization_gap)],["Chi phí",numeric(row.effort_cost)],["Động lực ròng High",numeric(row.net_incentive_best)],["λ* conditional",row.lambda_star_best?numeric(row.lambda_star_best):"Không thể bằng λ"],["λ tối đa theo budget",numeric(row.lambda_max)]])}<p class="help">Best High: ${esc(row.best_high_actions.join(", "))} · budget: ${esc(row.budget.best_high)}.</p><details><summary>Bốn High action và chẩn đoán exact</summary>${jsonBlock(row)}</details></article>`).join("");
  const axes=Object.keys(sweep.axes),pointRows=sweep.points.map(point=>{const landscape=point.landscape;return [point.point_id,...axes.map(axis=>numeric(point[axis])),esc(point.status+(point.error?": "+point.error:"")),landscape?landscape.branch_candidate_count:"—",landscape?landscape.full_equilibrium_count:"—",landscape?String(landscape.low_effort_exists):"—",landscape?String(landscape.all_high_signal_dependent_exists):"—",landscape?String(landscape.coexistence_low_and_dependent_high):"—"];});
  $("incentives-result").innerHTML=`<div class="verdict ${diagnostics.candidate_equilibrium_status==="exact_pure_equilibrium"?"":"bad"}"><strong>${diagnostics.candidate_equilibrium_status==="exact_pure_equilibrium"?"Candidate là cân bằng":"Candidate chưa phải cân bằng"}</strong><span class="tag">max regret ${esc(decimal(diagnostics.candidate_max_regret))}</span></div><p class="notice">Sáu threshold dưới đây giữ peer strategy cố định. H01/H10 chỉ nói report phụ thuộc X, chưa khẳng định report đúng Y.</p><div class="diagnostic-grid">${cards}</div><h3>Equilibrium landscape</h3><p class="help">Mỗi valid point dùng exhaustive pure search. Low Effort tồn tại cùng High Effort là vấn đề coexistence/selection; existence của High chưa bảo đảm hệ thống chọn nó.</p>${table(["Điểm",...axes,"Trạng thái","Candidates","Full equilibria","Có Low","Có all-High dùng X","Cùng tồn tại"],pointRows,true)}`;
}
function renderRobustness(result){
  const classifications={no_robust_policy:"Không có policy bền vững",isolated_robust_point:"Chỉ có một policy bền vững",observed_robust_set:"Quan sát được một vùng policy bền vững"};
  const rows=result.policies.map(policy=>{const worst=policy.worst||{};return [esc(policy.policy_id),policy.robust?badge("succeeded"):badge("failed"),`${policy.pass_count}/${policy.point_count}`,numeric(worst.false_approval_rate),numeric(worst.wrong_payout_value),numeric(worst.false_rejection_rate),numeric(worst.cash_review_cost),esc(Object.entries(policy.failure_reason_counts).map(([key,value])=>`${key}: ${value}`).join("; ")||"—")];});
  const gates=Object.entries(result.gates).map(([key,value])=>[esc(key),numeric(value)]);
  $("robustness-result").innerHTML=`<div class="verdict ${result.robust_policy_ids.length?"":"bad"}"><strong>${esc(classifications[result.classification]||result.classification)}</strong><span class="tag">${result.grid.total_points} point · ${result.grid.policy_count} policy × ${result.grid.scenario_count_per_policy} scenario</span></div><p class="notice">Policy chỉ được gọi là bền vững khi <strong>mọi</strong> uncertainty scenario đều qua gate theo cân bằng xấu nhất. Accuracy chỉ là diagnostic.</p><div class="metrics">${metric("Robust policies",{exact:String(result.robust_policy_ids.length),decimal:result.robust_policy_ids.length},result.robust_policy_ids.join(", ")||"Không có")}${metric("Failed points",{exact:String(result.failure_map.failed_point_ids.length),decimal:result.failure_map.failed_point_ids.length},"Tổng điểm không qua gate")}${metric("Pareto",{exact:String(result.pareto_frontier.policy_ids.length),decimal:result.pareto_frontier.policy_ids.length},result.pareto_frontier.policy_ids.join(", ")||"Không có")}</div>${table(["Policy","Robust","Pass/total","Worst false approval","Worst wrongly paid","Worst false rejection","Worst cash cost","Failure map"],rows,true)}<details><summary>Gates, uncertainty, baseline và giới hạn</summary>${table(["Gate","Trần"],gates)}${jsonBlock({uncertainty_axes:result.grid.uncertainty_axes,baseline_comparison:result.baseline_comparison,limitations:result.limitations})}</details>`;
}
function metric(label,value,definition) {return `<div class="metric"><div class="label">${esc(label)}</div><div class="value">${esc(decimal(value))}</div><span class="exact">${esc(value?.exact||"")}</span><span class="help">${esc(definition)}</span></div>`;}
function branchDetails(branch,withWitness=false) {
  const observationRows=[];
  const hybrid=branch.low.observations.some(obs=>obs.anchor_by_report);
  for(const [label,key] of [["L","low"],["H","high"]]) for(const obs of branch[key].observations) observationRows.push([label,esc(obs.observation.join(",")),numeric(obs.probability_given_z),numeric(obs.information_by_report[0]),numeric(obs.information_by_report[1]),...(hybrid?[numeric(obs.anchor_by_report[0]),numeric(obs.anchor_by_report[1])]:[]),esc(obs.optimal_reports.join(" / ")),numeric(obs.optimal_prediction)]);
  return `<details class="certificate"><summary><span>Judge ${esc(branch.judge)} · Z=${branch.z} · ${esc(branch.candidate_action)}</span><span>Regret ${esc(decimal(branch.regret))} · Effort tốt nhất ${esc(branch.best_efforts.join(" / "))}</span></summary>${table(["Candidate utility","Utility L tối ưu","Utility H tối ưu","Delta H−L","Regret"],[[numeric(branch.candidate.utility),numeric(branch.low.utility),numeric(branch.high.utility),numeric(branch.delta_utility),numeric(branch.regret)]])}<p class="help">Optimal actions: ${esc(branch.optimal_actions.join(", "))}. Prediction: ${esc(branch.prediction_optimum)}; report: ${esc(branch.report_optimum)}.</p>${table(["Effort","Observation","P(I|Z)","Info r=0","Info r=1",...(hybrid?["Anchor r=0","Anchor r=1"]:[]),"Optimal reports / ties","Optimal prediction"],observationRows)}${branch.witness?`<h3>Deviation witness</h3>${jsonBlock(branch.witness)}${withWitness?`<button data-witness="${branch.judge}-${branch.z}">Lấy deviation làm candidate mới</button><p class="help">Run mới dựng lại Bayesian predictions cho profile mới. Gain witness thuộc peer tables của run gốc.</p>`:""}`:"<p class='help'>Không có deviation sinh utility cao hơn tại nhánh này.</p>"}<details><summary>Toàn bộ certificate và peer tables đã freeze</summary>${jsonBlock(branch)}</details></details>`;
}
function renderAnalysis(result) {
  const m=result.metrics, good=result.equilibrium_status==="exact_pure_equilibrium";
  const hybrid=result.mechanism==="hybrid_anchor";const accounting=hybrid?table(["Judge","Peer score","Peer reward","Anchor score","Anchor reward","Effort cost","Utility"],result.judges.map((r,i)=>["ABC"[i],numeric(r.peer_score),numeric(r.peer_reward),numeric(r.anchor_score),numeric(r.anchor_reward),numeric(r.effort_cost),numeric(r.utility)])):table(["Judge","Expected score","Reward thực chi","Effort cost","Utility"],result.judges.map((r,i)=>["ABC"[i],numeric(r.score),numeric(r.reward),numeric(r.effort_cost),numeric(r.utility)]));
  const accuracyContext=good?'<p class="notice"><strong>Đây là profile cân bằng.</strong> Accuracy dưới đây là accuracy của cân bằng đang phân tích.</p>':'<p class="notice"><strong>Đây chưa phải hành vi tự nguyện.</strong> Accuracy dưới đây chỉ đạt được nếu ép các Judge dùng candidate cố định này; ít nhất một Judge có deviation có lợi.</p>';
  const accuracyLabel=good?"Accuracy của cân bằng đang phân tích":"Accuracy của candidate cố định";
  $("analyze-result").innerHTML=`<div class="verdict ${good?"":"bad"}"><strong>${good?"Cân bằng thuần trong game M1":"Candidate không phải cân bằng"}</strong>${badge(good?"succeeded":"failed")}</div><p class="help">Kiểm tra đủ 3 Judge × 2 nhánh Z · max regret ${esc(decimal(result.max_regret))}. Phạm vi chỉ pure strategy; không dự đoán cân bằng được chọn.</p>${accuracyContext}${hybrid?'<p class="notice"><strong>V3 timing:</strong> report khóa → decision D → random audit → tín hiệu T → settle anchor reward. T không sửa decision của case hiện tại.</p>':""}<div class="metrics">${metric("Giải ngân sai kỳ vọng",m.wrong_payout_value,"V × P(Y=0,D=1)")}${metric("False approval",m.false_approval_rate,"P(D=1 | Y=0)")}${metric(accuracyLabel,m.accuracy,"P(D=Y)")}${metric("Cash review cost",m.cash_review_cost,hybrid?"Reward + operating + q×audit cost":"Reward + operating cost")}</div><details open><summary>Chẩn đoán tín hiệu</summary><p class="help">Sensitivity/specificity mô tả kênh tín hiệu; prior-weighted accuracy không phải decision accuracy, score hay utility.</p>${jsonBlock(result.signal_diagnostics)}</details><h3>Accounting của candidate</h3>${accounting}<p>Reward thực chi tổng: <strong>${esc(decimal(m.expected_reward_total))}</strong>${hybrid?` · Peer <span id="expected-peer-reward-total">${numeric(m.expected_peer_reward_total)}</span> · Anchor <span id="expected-anchor-reward-total">${numeric(m.expected_anchor_reward_total)}</span> · Audit kỳ vọng <span id="expected-audit-cost">${numeric(m.expected_audit_cost)}</span>`:""} · Maximum reward: ${esc(decimal(result.reward_cap))} · Budget: ${esc(decimal(result.reward_budget))}.</p><details><summary>Toàn bộ decision metrics và prediction tables</summary>${jsonBlock({metrics:m,predictions:result.predictions,prediction_semantics:result.prediction_semantics})}</details><h3>Best response theo từng Judge / Z</h3>${result.best_responses.map(b=>branchDetails(b,true)).join("")}<h3>${hybrid?"128 potential":"32"} trạng thái · support ${result.state_support_size}</h3><div class="filters">${["y","z","decision"].map(key=>`<label>${key}<select id="state-${key}"><option value="">Tất cả</option><option>0</option><option>1</option></select></label>`).join("")}</div><div id="states-table"></div>`;
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
  $("states-table").innerHTML=`<p class="help">${rows.length}/${state.csv.rows.length} trạng thái. Cột _exact là nguồn số chính xác; _decimal để xem.</p>`+table(headers,rows.map(r=>headers.map(h=>esc(r[h]))),true);
}
function renderSearch() {
  const result=state.search;
  $("equilibria-result").innerHTML=`<div class="verdict"><strong>${result.full_equilibrium_count} tổ hợp cân bằng thuần</strong><span class="tag">432 / 432 branch candidates</span></div><p class="help">Z=0: ${result.branches["0"].equilibrium_count}; Z=1: ${result.branches["1"].equilibrium_count}. ${esc(result.prediction_semantics)}. Prediction có thể là continuum khi thưởng hằng số.</p><fieldset><legend>Chọn hai nhánh để xem full profile</legend><p class="help">Search xác định chiến lược ổn định nhưng chưa gắn accuracy của candidate cũ cho nó. Chọn một nhánh cho mỗi Z, nạp profile cân bằng sang Phân tích rồi chạy để tính đúng decision metrics của tổ hợp đó.</p>${[0,1].map(z=>`<label for="chosen-z${z}">Z=${z}</label><select id="chosen-z${z}">${result.branches[z].candidates.filter(r=>r.accepted).map(r=>`<option value="${esc(r.id)}">${esc(r.actions.join(" / "))}</option>`).join("")}</select>`).join("")}<div class="button-row"><button id="analyze-combination">Phân tích accuracy của cân bằng đã chọn</button></div></fieldset><div class="filters"><label>Z<select id="search-z"><option value="">Cả hai</option><option>0</option><option>1</option></select></label><label>Trạng thái<select id="search-accepted"><option value="">Tất cả</option><option value="true">Cân bằng</option><option value="false">Bị bác</option></select></label>${["A","B","C"].map(j=>`<label>Action ${j}<select id="search-${j}"><option value="">Tất cả</option>${state.status.actions.map(a=>`<option>${a}</option>`).join("")}</select></label>`).join("")}<label>Effort<select id="search-effort"><option value="">Tất cả</option><option value="all_h">Cả ba H</option><option value="all_l">Cả ba L</option><option value="mixed">Có cả L và H</option>${["A","B","C"].flatMap(j=>["L","H"].map(e=>`<option value="${j}_${e}">${j}=${e}</option>`)).join("")}</select></label></div><div id="search-table"></div><div id="search-certificate"></div>`;
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
  const landscape=result.scope==="candidate_analysis_plus_exhaustive_pure_equilibrium_landscape";
  const landscapeHeaders=landscape?["Full equilibria","Có Low","Có all-High dùng X","Equilibrium accuracy min","Equilibrium accuracy max"]:[];
  const yesNo=value=>value==null?"—":value?"Có":"Không";
  const landscapeCells=row=>landscape?[row.full_equilibrium_count??"—",yesNo(row.low_effort_exists),yesNo(row.all_high_signal_dependent_exists),numeric(row.equilibrium_accuracy_min),numeric(row.equilibrium_accuracy_max)]:[];
  const scopeHelp=landscape?"Mỗi điểm V3 hợp lệ đã kiểm đủ 432 branch candidates. Candidate và khoảng accuracy của các cân bằng được giữ riêng; dấu — nghĩa là không có pure equilibrium.":"Sweep này chỉ phân tích candidate cố định; không phải bản đồ mọi cân bằng.";
  $("sweep-result").innerHTML=`<p class="run-note">${esc(state.manifest.mechanism)} · run ${esc(state.manifest.run_id)} · profile ${esc(state.manifest.profile_hash)} · ${esc(state.manifest.model_version)}</p><div class="filters"><label>Trục X<select id="chart-x">${axes.map(a=>`<option>${esc(a)}</option>`).join("")}</select></label><label>Trục phân nhóm<select id="chart-series"><option value="">Không</option>${axes.map(a=>`<option>${esc(a)}</option>`).join("")}</select></label><label>Metric<select id="chart-metric">${metrics.map(a=>`<option>${a}</option>`).join("")}</select></label></div><div id="chart-fixed" class="filters"></div><div id="sweep-chart"></div><p class="help">${scopeHelp} Không nội suy miền chưa tính. Hàng invalid vẫn được giữ trong bảng.</p>${table(["Điểm",...axes,"Trạng thái","Wrong payout","Delta A Z=0","Delta A Z=1","Candidate",...landscapeHeaders,"Tái lập"],result.rows.map((r,i)=>[i,...axes.map(a=>numeric(r[a])),esc(r.status+(r.error?": "+r.error:"")),numeric(r.wrong_payout_value),numeric(r.A_z0_delta_utility),numeric(r.A_z1_delta_utility),esc(r.equilibrium_status||"—"),...landscapeCells(r),r.status==="valid"?`<button data-sweep-point="${i}">Phân tích candidate</button>`:"—"]),true)}`;
  ["chart-x","chart-series"].forEach(id=>$(id).addEventListener("change",setupChartFilters));$("chart-metric").addEventListener("change",drawChart);setupChartFilters();
}
function axisValue(row,key) {const config=JSON.parse(row.config_json);return key==="c"?config.costs[0]:getPath(config,key);}
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
  $("compare-result").innerHTML=`<p class="notice"><strong>Cùng một candidate/profile ở cả hai cột</strong> và cùng maximum reward ${esc(decimal(result.reward_cap))}. Accuracy và expected_effort_cost mô tả profile đang được đánh giá. Nếu max_regret &gt; 0 hoặc equilibrium_status là not_equilibrium, profile đó không ổn định dưới cơ chế tương ứng; engine không tự chuyển Fixed sang Low Effort.</p>`+table(["Metric của candidate","Fixed","RBTS"],keys.map(key=>[key,numeric(fixed.metrics[key]),numeric(rbts.metrics[key])]).concat([["max_regret",numeric(fixed.max_regret),numeric(rbts.max_regret)],["equilibrium_status",esc(fixed.equilibrium_status),esc(rbts.equilibrium_status)]]));
}
function renderTests(result,run) {
  $("tests-result").innerHTML=`<div class="verdict ${result.status==="passed"?"":"bad"}"><strong>${esc(result.status)}</strong><span class="tag">${esc(result.suite)}${result.failure_fixture?" · FIXTURE LỖI CÔNG KHAI":""}</span></div><p>${Object.entries(result.counts).map(([key,value])=>`${esc(key)}: <strong>${value}</strong>`).join(" · ")}</p><p class="help">Thời gian ${result.duration_seconds==null?"không có":result.duration_seconds.toFixed(3)+"s"}. Browser acceptance executed: ${esc(result.browser_acceptance_executed)}.</p>${table(["T-ID","Test thực thi","Trạng thái","Thời gian","Assertion / evidence"],result.records.map(r=>[esc(r.test_id||"fixture"),esc(r.unittest_id||"reference / unavailable"),badge(r.status),esc(r.duration_seconds?.toFixed(3)||"—"),r.assertion_or_error||r.evidence?`<details><summary>Xem</summary>${jsonBlock({assertion:r.assertion_or_error,evidence:r.evidence})}</details>`:"—"]))}<a href="${artifactURL(run,"test_log.txt",true)}">Tải test_log.txt thật</a>`;
  if(result.reference_results)$("tests-result").insertAdjacentHTML("beforeend",`<details><summary>Kết quả reference mới từ checker</summary>${jsonBlock(result.reference_results)}</details><a href="${artifactURL(run,"reference_results.json",true)}">Tải reference_results.json của run này</a>`);
}
async function refreshHistory() {
  const {runs}=await api("/api/runs");
  $("history-result").innerHTML=runs.length?table(["Run / UTC","Model","Tác vụ","Cơ chế","Trạng thái","Config / scenario","Thao tác"],runs.map(r=>[`${esc(r.run_id)}<br><span class="help">${esc(r.created_at_utc)}</span>`,esc(r.model_version||"—"),esc(r.operation),esc(r.mechanism||"—"),badge(r.status),`<span class="exact">${esc(r.config_hash||"—")}<br>${esc(r.scenario_hash||"not_provided")}</span>`,`<button data-open-run="${esc(r.run_id)}">Mở</button> <button data-pin="${esc(r.run_id)}">${state.pinned.includes(r.run_id)?"Bỏ ghim":"Ghim"}</button>`]),true):'<p class="empty">Chưa có run được lưu.</p>';
}
async function renderPinned() {
  if(state.pinned.length!==2){$("pinned-result").innerHTML=`<p class="empty">Đã ghim ${state.pinned.length}/2 run.</p>`;return;}
  const manifests=await Promise.all(state.pinned.map(id=>api("/api/runs/"+encodeURIComponent(id))));
  const differences=["model_version","config_hash","profile_hash","scenario_hash"].filter(k=>manifests[0][k]!==manifests[1][k]);
  const summaries=await Promise.all(manifests.map(m=>m.status==="succeeded"&&m.artifacts.some(a=>a.name==="summary.json")?artifact(m.run_id,"summary.json"):null));
  const rows=["accuracy","false_approval_rate","wrong_payout_value","expected_reward_total"].map(key=>[key,...summaries.map(s=>s?.metrics?numeric(s.metrics[key]):"Không có metric analyze")]);
  $("pinned-result").innerHTML=`<p class="notice">${differences.length?"Các run khác "+esc(differences.join(", "))+"; không gắn nhãn so sánh có kiểm soát.":"Cùng model/config/profile/scenario. Kiểm tra cơ chế và trạng thái trước khi diễn giải."}</p>${table(["Metric",...manifests.map(m=>m.run_id+" · "+m.mechanism)],rows)}<details><summary>Khác biệt input và phiên bản</summary>${jsonBlock(manifests.map(m=>({run_id:m.run_id,model:m.model_version,config:m.config,profile:m.profile,scenario:m.scenario||null,status:m.status,mechanism:m.mechanism})))}</details>`;
}
async function handleClick(event) {
  const button=event.target.closest("button");if(!button)return;
  try {
    if(button.dataset.view){switchView(button.dataset.view);return;}
    if(button.dataset.operation){await submit(button.dataset.operation);return;}
    if(button.dataset.openRun){await openRun(button.dataset.openRun);return;}
    if(button.dataset.loadRun){const m=await api("/api/runs/"+encodeURIComponent(button.dataset.loadRun));if(!m.config||!m.profile)throw new Error("Run này không có full config/profile để nạp.");putDraft(m.config,m.profile,m.mechanism,m.scenario||null);switchView("analyze");return;}
    if(button.dataset.pin){const id=button.dataset.pin;state.pinned=state.pinned.includes(id)?state.pinned.filter(r=>r!==id):[...state.pinned.slice(-1),id];await refreshHistory();await renderPinned();return;}
    if(button.dataset.witness){const [judge,z]=button.dataset.witness.split("-");const b=state.analysis.best_responses.find(r=>r.judge===judge&&String(r.z)===z);const p=copy(state.analysis.profile);p[z]["ABC".indexOf(judge)]=b.witness.action;putDraft(state.analysis.config,p,state.analysis.mechanism);$("job-detail").textContent="Đã nạp deviation. Run mới sẽ dựng prediction của candidate mới; witness gốc vẫn giữ nguyên.";return;}
    if(button.dataset.certificate){const r=Object.values(state.search.branches).flatMap(b=>b.candidates).find(r=>r.id===button.dataset.certificate);$("search-certificate").innerHTML=`<h3>${esc(r.id)} · ${r.accepted?"Cân bằng":"Bị bác"}</h3>`+r.certificates.map(c=>branchDetails(c)).join("");$("search-certificate").scrollIntoView({block:"start"});return;}
    if(button.dataset.sweepPoint!==undefined){const row=state.sweep.rows[Number(button.dataset.sweepPoint)];putDraft(JSON.parse(row.config_json),state.sweepProfile,state.manifest.mechanism);switchView("analyze");return;}
    if(button.id==="load-calibration-sample"){const response=await fetch("/api/calibration/sample.csv");if(!response.ok)throw new Error("Không tải được dataset mẫu.");state.calibrationDataset={name:"synthetic_v2_calibration.csv",text:await response.text()};$("calibration-file-status").textContent=`Đã nạp ${state.calibrationDataset.name} · synthetic fixture.`;$("calibration-provenance").value="synthetic";return;}
    if(button.id==="apply-calibration"){if(!state.calibration)throw new Error("Chưa có calibration thành công.");const current=readDraft();putDraft(state.calibration.config,current.profile,current.mechanism,current.scenario);switchView("analyze");$("job-detail").textContent="Đã nạp config calibration vào draft V2. Hãy kiểm tra profile rồi chạy phân tích.";return;}
    if(button.id==="cancel"&&state.active){button.disabled=true;updateJob(await api("/api/jobs/"+encodeURIComponent(state.active)+"/cancel",{}));return;}
    if(button.id==="validate"){clearErrors();const response=await api("/api/validate",{operation:"analyze",...readDraft()});$("signal-diagnostics").innerHTML=`<h3>Chẩn đoán tín hiệu</h3><p class="help">FPR=1−specificity; FNR=1−sensitivity; accuracy có trọng số prior. Đây không phải decision accuracy hay utility.</p>${jsonBlock(response.signal_diagnostics)}`;$("job-detail").textContent="Đầu vào hợp lệ theo validator của engine.";return;}
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
$("incentive-axes").addEventListener("input",previewIncentiveGrid);$("incentive-axes").addEventListener("change",previewIncentiveGrid);
$("suite").addEventListener("change",()=>$("test-selection").hidden=$("suite").value!=="selected");
$("calibration-file").addEventListener("change",async event=>{try{clearErrors();const file=event.target.files[0];if(!file)return;state.calibrationDataset={name:file.name,text:await file.text()};$("calibration-file-status").textContent=`Đã chọn ${file.name} · ${file.size.toLocaleString("vi-VN")} bytes.`;}catch(error){showError(error);}});
$("model-version").addEventListener("change",event=>{try{state.drafts[state.activeModel]=readDraft();const version=event.target.value;if(state.drafts[version]){const draft=state.drafts[version];putDraft(draft.config,draft.profile,draft.mechanism,draft.scenario);}else{renderModelFields(version);const config=version==="ceav-m1-v3.0"?state.status.v3_presets.heterogeneous_anchor:version==="ceav-m1-v3.2"?state.status.v32_presets.report_sensitive_base:version==="ceav-m1-v2.0"?state.status.v2_presets.heterogeneous:state.status.presets.golden_g1;putDraft(config,state.status.presets.all_high,["ceav-m1-v3.0","ceav-m1-v3.2"].includes(version)?"hybrid_anchor":"rbts",null);}$("signal-diagnostics").innerHTML='<p class="help">Bấm “Kiểm tra đầu vào” để xem diagnostics của draft này.</p>';}catch(error){showError(error);event.target.value=state.activeModel;}});
$("preset").addEventListener("change",()=>{const name=$("preset").value;const profileName=name==="golden_g2"?"all_z":name==="asymmetric"?"asymmetric_profile":"all_high";const config=state.activeModel==="ceav-m1-v3.0"?state.status.v3_presets[name]:state.activeModel==="ceav-m1-v3.2"?state.status.v32_presets[name]:state.activeModel==="ceav-m1-v2.0"?state.status.v2_presets[name]:state.status.presets[name];putDraft(config,state.status.presets[profileName],["ceav-m1-v3.0","ceav-m1-v3.2"].includes(state.activeModel)?"hybrid_anchor":"rbts");$("quick-profile").value=profileName;});
$("quick-profile").addEventListener("change",()=>putDraft(readDraft().config,state.status.presets[$("quick-profile").value],readDraft().mechanism));
$("import").addEventListener("change",async event=>{
  try{clearErrors();const file=event.target.files[0];if(!file)return;const input=JSON.parse(await file.text());const current=readDraft();const wrapper="config" in input;if(wrapper&&Object.keys(input).some(k=>!["config","profile","mechanism","scenario"].includes(k)))throw new Error("Field không được hỗ trợ trong input wrapper.");const config=wrapper?input.config:input["0"]?current.config:input;const profile=wrapper?(input.profile||current.profile):input["0"]?input:current.profile;const mechanism=input.mechanism||current.mechanism;const scenario=wrapper&&"scenario" in input?input.scenario:current.scenario;const checked=await api("/api/validate",{operation:"analyze",config,profile,mechanism,scenario});putDraft(config,profile,mechanism,scenario);$("signal-diagnostics").innerHTML=`<h3>Chẩn đoán tín hiệu</h3>${jsonBlock(checked.signal_diagnostics)}`;$("job-detail").textContent="Đã nhập JSON hợp lệ; các chuỗi số được giữ nguyên.";}catch(error){showError(error);}finally{event.target.value="";}
});
api("/api/status").then(status=>{state.status=status;$("connection").textContent=`Engine sẵn sàng · ${status.supported_model_versions.join(" + ")}`;renderModelFields(status.default_model_version);const config=status.default_model_version==="ceav-m1-v3.0"?status.v3_presets.heterogeneous_anchor:status.default_model_version==="ceav-m1-v3.2"?status.v32_presets.report_sensitive_base:status.v2_presets.heterogeneous;putDraft(config,status.presets.all_high,["ceav-m1-v3.0","ceav-m1-v3.2"].includes(status.default_model_version)?"hybrid_anchor":"rbts",null);state.runRevision=null;$("stale").hidden=true;document.querySelectorAll(".run").forEach(b=>b.disabled=false);if(status.active_job){state.active=status.active_job.job_id;updateJob(status.active_job);poll(state.active);}}).catch(error=>{$("connection").textContent="Không kết nối được engine";showError(error);});
