const $ = id => document.getElementById(id);
let searchTimer;
// The list endpoint caps a page at 50 rows (default limit 50, max
// 100), but the dashboard used to fetch one page only — with more
// than 50 students the rest were unreachable from the UI. Track the
// page here and ask for the next slice explicitly.
let page = 0;
const PAGE_SIZE = 50;

async function api(url, options = {}) {
  const response = await fetch(url, {
    headers: {"Content-Type":"application/json", ...(options.headers || {})},
    ...options
  });
  let data = {};
  try { data = await response.json(); } catch (_) {}
  if (!response.ok) throw new Error(data.detail || "Request failed");
  return data;
}

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
}

function notice(message, error=false) {
  $("notice").className = "notice" + (error ? " error" : "");
  $("notice").textContent = message;
  setTimeout(() => { $("notice").className=""; $("notice").textContent=""; }, 3000);
}

async function loadStats() {
  const s = await api("/api/stats");
  $("totalStudents").textContent = s.total_students;
  $("activeStudents").textContent = s.active_students;
  $("averageGpa").textContent = Number(s.average_gpa).toFixed(2);
  $("majorCount").textContent = s.majors;
}

async function loadStudents() {
  const params = new URLSearchParams();
  if ($("searchInput").value.trim()) params.set("search", $("searchInput").value.trim());
  if ($("statusFilter").value) params.set("status", $("statusFilter").value);
  // Ask for one row more than a page holds: a full page of exactly
  // PAGE_SIZE rows used to leave Next enabled even when there was no
  // next page (e.g. exactly 50 students), and clicking it fetched an
  // empty page and bounced straight back. The extra row is only a
  // "there is more" signal — it is never shown.
  params.set("limit", PAGE_SIZE + 1);
  params.set("offset", page * PAGE_SIZE);
  try {
    const fetched = await api("/api/students?" + params.toString());
    const hasMore = fetched.length > PAGE_SIZE;
    const students = fetched.slice(0, PAGE_SIZE);
    // Deleting the last student on a page must not strand the user
    // on an empty page when earlier pages still have rows.
    if (!students.length && page > 0) {
      page -= 1;
      await loadStudents();
      return;
    }
    $("studentRows").innerHTML = students.map(s => `
      <tr>
        <td><div class="studentName">${esc(s.first_name)} ${esc(s.last_name)}</div><div class="email">${esc(s.email)}</div></td>
        <td>${esc(s.student_number)}</td><td>${esc(s.major)}</td><td>${Number(s.gpa).toFixed(2)}</td>
        <td><span class="badge">${esc(s.status)}</span></td>
        <td><div class="actions"><button onclick="editStudent(${s.id})">Edit</button><button class="danger" onclick="deleteStudent(${s.id})">Delete</button></div></td>
      </tr>`).join("");
    $("emptyState").style.display = students.length ? "none" : "block";
    // Next is enabled only when the over-fetch found a row past
    // this page — a full page alone no longer implies there is more.
    $("prevPage").disabled = page === 0;
    $("nextPage").disabled = !hasMore;
    $("pageInfo").textContent = students.length ? `Page ${page + 1}` : "";
  } catch(e) { notice(e.message, true); }
}

function openModal(student=null) {
  $("studentForm").reset();
  $("studentId").value = student?.id || "";
  $("modalTitle").textContent = student ? "Edit Student" : "Add Student";
  $("firstName").value = student?.first_name || "";
  $("lastName").value = student?.last_name || "";
  $("studentNumber").value = student?.student_number || "";
  $("email").value = student?.email || "";
  $("major").value = student?.major || "Computer Science";
  $("gpa").value = student?.gpa ?? "3.50";
  $("status").value = student?.status || "Active";
  $("studentModal").classList.remove("hidden");
}

function closeModal(){ $("studentModal").classList.add("hidden"); }

async function editStudent(id) {
  try { openModal(await api(`/api/students/${id}`)); }
  catch(e){ notice(e.message,true); }
}

async function deleteStudent(id) {
  if (!confirm("Delete this student record?")) return;
  try {
    await api(`/api/students/${id}`, {method:"DELETE"});
    notice("Student deleted.");
    await Promise.all([loadStudents(), loadStats()]);
  } catch(e){ notice(e.message,true); }
}

$("studentForm").addEventListener("submit", async e => {
  e.preventDefault();
  const id = $("studentId").value;
  const payload = {
    first_name:$("firstName").value.trim(), last_name:$("lastName").value.trim(),
    student_number:$("studentNumber").value.trim(), email:$("email").value.trim(),
    major:$("major").value.trim(), gpa:Number($("gpa").value), status:$("status").value
  };
  try {
    await api(id ? `/api/students/${id}` : "/api/students", {
      method:id ? "PUT" : "POST", body:JSON.stringify(payload)
    });
    closeModal(); notice(id ? "Student updated." : "Student added.");
    await Promise.all([loadStudents(), loadStats()]);
  } catch(e){ notice(e.message,true); }
});

$("newStudentBtn").onclick=()=>openModal();
$("closeModal").onclick=closeModal;
$("cancelBtn").onclick=closeModal;
$("statusFilter").onchange=()=>{page=0;loadStudents();};
$("searchInput").oninput=()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{page=0;loadStudents();},250)};
$("prevPage").onclick=()=>{if(page>0){page-=1;loadStudents();}};
$("nextPage").onclick=()=>{if(!$("nextPage").disabled){page+=1;loadStudents();}};
$("studentModal").addEventListener("click", e=>{if(e.target===$("studentModal"))closeModal()});
Promise.all([loadStudents(), loadStats()]);
