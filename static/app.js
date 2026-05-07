let currentSessionId = null;
let currentPlan = null;

// Load sidebar sessions on page load
async function loadSessions() {
    try {
        const resp = await fetch('/api/sessions');
        const sessions = await resp.json();
        const list = document.getElementById('sessionList');
        list.innerHTML = '';
        sessions.forEach(s => {
            const div = document.createElement('div');
            div.className = 'session-item' + (s.id === currentSessionId ? ' active' : '');
            div.innerHTML = `<div class="session-name">${s.name}</div><div class="session-status">${s.status}</div>`;
            div.onclick = () => loadSession(s.id);
            list.appendChild(div);
        });
    } catch(e) { console.error(e); }
}

async function loadSession(sid) {
    const resp = await fetch(`/api/session/${sid}`);
    if (!resp.ok) return;
    const data = await resp.json();
    currentSessionId = data.id;
    currentPlan = data.plan;
    // Update UI based on status
    if (data.plan) {
        showPlan(data.plan);
        document.getElementById('sectionDescribe').classList.add('hidden');
    } else {
        showDescribe();
    }
    loadSessions(); // highlight active
}

function newProject() {
    currentSessionId = null;
    currentPlan = null;
    document.getElementById('projectDescription').value = '';
    showDescribe();
    loadSessions();
}

function showDescribe() {
    document.getElementById('sectionDescribe').classList.remove('hidden');
    document.getElementById('sectionPlan').classList.add('hidden');
    document.getElementById('sectionProgress').classList.add('hidden');
    document.getElementById('sectionPush').classList.add('hidden');
}

function showPlan(plan) {
    document.getElementById('sectionPlan').classList.remove('hidden');
    document.getElementById('sectionDescribe').classList.add('hidden');
    let html = `<p><strong>Type:</strong> ${plan.project_type}</p>`;
    html += `<p><strong>Files:</strong> ${plan.total_files}</p>`;
    html += '<ul>';
    plan.files.forEach(f => { html += `<li>${f.name} - ${f.description}</li>`; });
    html += '</ul>';
    document.getElementById('planContent').innerHTML = html;
}

async function analyzeProject() {
    const msg = document.getElementById('projectDescription').value.trim();
    if (!msg) return alert('Please describe your project');
    const form = new FormData();
    form.append('message', msg);
    try {
        const resp = await fetch('/api/analyze', { method:'POST', body:form });
        const data = await resp.json();
        currentSessionId = data.session_id;
        currentPlan = data.plan;
        showPlan(data.plan);
        loadSessions();
    } catch(e) { alert('Error: ' + e.message); }
}

async function confirmAndGenerate() {
    if (!currentSessionId) return;
    document.getElementById('sectionPlan').classList.add('hidden');
    document.getElementById('sectionProgress').classList.remove('hidden');
    const form = new FormData();
    form.append('session_id', currentSessionId);
    const response = await fetch('/api/generate-code', { method:'POST', body:form });
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, {stream: true});
        const lines = buffer.split('\n');
        buffer = lines.pop(); // remainder
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try { handleProgress(JSON.parse(line.slice(6))); } catch(e) {}
            }
        }
    }
}

function handleProgress(data) {
    const fill = document.getElementById('progressFill');
    const text = document.getElementById('progressText');
    const list = document.getElementById('fileList');
    if (data.type === 'progress') {
        fill.style.width = data.percentage + '%';
        text.textContent = `Generating ${data.filename}... (${data.current}/${data.total})`;
        list.innerHTML += `<div class="file-item" id="f-${data.filename}"><div class="spinner"></div>${data.filename}</div>`;
    } else if (data.type === 'file_complete') {
        fill.style.width = data.percentage + '%';
        text.textContent = `${data.filename} completed!`;
        const el = document.getElementById('f-'+data.filename);
        if (el) { el.classList.add('completed'); el.querySelector('.spinner').remove(); }
    } else if (data.type === 'complete') {
        fill.style.width = '100%';
        text.textContent = 'All files generated!';
        document.getElementById('completionMessage').innerHTML = `✅ Successfully generated ${data.files.length} files.`;
        setTimeout(() => {
            document.getElementById('sectionProgress').classList.add('hidden');
            document.getElementById('sectionPush').classList.remove('hidden');
        }, 1500);
    }
}

async function pushToGitHub() {
    const name = document.getElementById('repoName').value.trim();
    if (!name) return alert('Enter repo name');
    const form = new FormData();
    form.append('session_id', currentSessionId);
    form.append('repo_name', name);
    const btn = document.getElementById('pushBtn');
    btn.disabled = true; btn.textContent = 'Pushing...';
    try {
        const resp = await fetch('/api/push-to-github', { method:'POST', body:form });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Push failed');
        document.getElementById('pushStatus').innerHTML = `✅ Pushed! <a href="${data.repo_url}" target="_blank">${data.repo_url}</a>`;
        btn.textContent = 'Done';
        loadSessions();
    } catch(e) {
        document.getElementById('pushStatus').innerHTML = `❌ ${e.message}`;
        btn.disabled = false; btn.textContent = 'Retry';
    }
}

function resetToDescribe() {
    currentSessionId = null;
    currentPlan = null;
    showDescribe();
}

document.getElementById('newProjectBtn').addEventListener('click', newProject);
loadSessions();