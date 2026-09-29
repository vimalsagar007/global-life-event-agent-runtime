const API_BASE = '/api/v1';

let currentEvent = null;
let currentDemoScenarios = [];

document.addEventListener('DOMContentLoaded', () => {
  initEventListeners();
  loadDemoScenarios();
});

function initEventListeners() {
  document.getElementById('btn-orchestrate').addEventListener('click', handleOrchestrate);
  document.getElementById('demo-select').addEventListener('change', handleDemoSelect);
  document.getElementById('btn-simulate-source-change').addEventListener('click', handleSimulateSourceChange);
  document.getElementById('btn-run-eval').addEventListener('click', handleRunEval);

  // Tab navigation
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      
      const targetTab = e.target.getAttribute('data-tab');
      e.target.classList.add('active');
      document.getElementById(targetTab).classList.add('active');
    });
  });
}

function appendTag(text) {
  const promptEl = document.getElementById('event-prompt');
  if (promptEl.value) {
    promptEl.value += ' ' + text;
  } else {
    promptEl.value = 'I am moving and ' + text;
  }
}

async function loadDemoScenarios() {
  try {
    const res = await fetch(`${API_BASE}/demo/scenarios`);
    currentDemoScenarios = await res.json();
  } catch (err) {
    console.error('Failed to load demo scenarios:', err);
  }
}

function handleDemoSelect(e) {
  const scenarioId = e.target.value;
  const selected = currentDemoScenarios.find(s => s.scenario_id === scenarioId);
  if (selected) {
    document.getElementById('event-prompt').value = selected.raw_input;
  }
}

async function handleOrchestrate() {
  const promptText = document.getElementById('event-prompt').value.trim();
  if (!promptText) {
    alert('Please enter a life event prompt.');
    return;
  }

  const btn = document.getElementById('btn-orchestrate');
  btn.disabled = true;
  btn.innerText = '⚡ Orchestrating Plan...';

  try {
    const res = await fetch(`${API_BASE}/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw_input: promptText })
    });

    if (!res.ok) {
      throw new Error(`API Error: ${res.statusText}`);
    }

    currentEvent = await res.json();
    renderEventDashboard(currentEvent);
    document.getElementById('event-dashboard').classList.remove('hidden');

    // Also fetch MCP tools and A2A agents for full view
    loadA2ACards();
    loadMCPTools();
    loadActivityTrace(currentEvent.event_id);
  } catch (err) {
    alert('Failed to generate life event plan: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerText = '⚡ Generate Execution Plan';
  }
}

function renderEventDashboard(event) {
  document.getElementById('event-title').innerText = event.title;
  
  const typeBadge = document.getElementById('event-type-badge');
  typeBadge.innerText = event.is_cross_border ? 'CROSS-BORDER RELOCATION' : 'DOMESTIC RELOCATION';
  typeBadge.className = event.is_cross_border ? 'badge badge-crossborder' : 'badge';

  // Origin & Destination
  const orig = event.origin_jurisdiction;
  document.getElementById('origin-juris-name').innerText = orig.city ? `${orig.city}, ${orig.region}, ${orig.country}` : `${orig.region || ''} ${orig.country}`;
  document.getElementById('origin-juris-meta').innerText = `Currency: ${orig.currency} | Language: ${orig.language.toUpperCase()} | Timezone: ${orig.timezone}`;

  const dest = event.destination_jurisdiction || orig;
  document.getElementById('dest-juris-name').innerText = dest.city ? `${dest.city}, ${dest.region}, ${dest.country}` : `${dest.region || ''} ${dest.country}`;
  document.getElementById('dest-juris-meta').innerText = `Currency: ${dest.currency} | Language: ${dest.language.toUpperCase()} | Timezone: ${dest.timezone}`;

  // Metrics
  document.getElementById('val-tasks-count').innerText = event.tasks.length;
  document.getElementById('val-agents-count').innerText = event.domains.length || 5;
  
  let sourceCount = 0;
  event.tasks.forEach(t => sourceCount += (t.sources ? t.sources.length : 0));
  document.getElementById('val-citations-count').innerText = sourceCount;

  let approvalCount = event.tasks.filter(t => t.requires_approval).length;
  document.getElementById('val-approvals-count').innerText = approvalCount;

  // Render Dependency Graph SVG flow
  renderDependencyGraph(event.tasks);

  // Render Tasks List
  renderTasksList(event.tasks);

  // Render RAG Sources
  renderRAGSources(event.tasks);
}

function renderDependencyGraph(tasks) {
  const graphContainer = document.getElementById('dependency-graph-container');
  if (!tasks || tasks.length === 0) {
    graphContainer.innerHTML = '<p class="help-text">No task dependencies graph available.</p>';
    return;
  }

  let html = '<div class="graph-nodes-flow">';
  tasks.slice(0, 6).forEach((task, idx) => {
    html += `<div class="graph-node">[${task.category}] ${task.title.substring(0, 30)}...</div>`;
    if (idx < Math.min(tasks.length, 6) - 1) {
      html += '<span class="graph-edge">➔</span>';
    }
  });
  html += '</div>';

  graphContainer.innerHTML = html;
}

function renderTasksList(tasks) {
  const container = document.getElementById('tasks-list');
  if (!tasks || tasks.length === 0) {
    container.innerHTML = '<p class="help-text">No tasks generated.</p>';
    return;
  }

  let html = '';
  tasks.forEach(task => {
    const isApproval = task.requires_approval || task.status === 'REQUIRES_APPROVAL';
    
    html += `
      <div class="task-card priority-${task.priority}">
        <div class="task-info">
          <div class="task-title">${task.title}</div>
          <div class="task-desc">${task.description}</div>
          <div class="task-meta-bar">
            <span>Jurisdiction: ${task.jurisdiction}</span>
            <span>Category: ${task.category}</span>
            <span>Deadline: ${task.deadline || 'Flexible'}</span>
            <span class="task-agent">Agent: ${task.agent}</span>
          </div>
        </div>
        <div>
          ${isApproval ? 
            `<button class="task-action-btn" onclick="approveTaskAction('${task.task_id}')">⚠️ Approve Action</button>` : 
            `<span class="badge" style="background:rgba(16,185,129,0.15);color:#10b981;">${task.status}</span>`
          }
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

function renderRAGSources(tasks) {
  const container = document.getElementById('rag-sources-grid');
  let sources = [];
  tasks.forEach(t => {
    if (t.sources) sources.push(...t.sources);
  });

  if (sources.length === 0) {
    container.innerHTML = '<p class="help-text">No specific document citations attached.</p>';
    return;
  }

  let html = '';
  sources.forEach(src => {
    html += `
      <div class="item-card">
        <div class="item-card-title">${src.title}</div>
        <div class="item-card-desc">${src.summary}</div>
        <div style="font-size:11px;color:#9ca3af;margin-top:4px;">
          <div>Authority: <strong style="color:#06b6d4">${src.authority_level}</strong></div>
          <div>Country: ${src.country} | Verified: ${src.last_verified}</div>
          <a href="${src.source_url}" target="_blank" style="color:#6366f1;text-decoration:none;">View Official Source ↗</a>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

async function loadA2ACards() {
  try {
    const res = await fetch(`${API_BASE}/a2a/agents`);
    const agents = await res.json();
    const container = document.getElementById('a2a-cards-grid');

    let html = '';
    agents.forEach(agent => {
      html += `
        <div class="item-card">
          <div class="item-card-title">🤖 ${agent.name}</div>
          <div class="item-card-desc">${agent.title}</div>
          <div style="font-size:11px;color:#9ca3af;margin-top:6px;">
            <div>Capabilities: ${agent.capabilities.join(', ')}</div>
            <div style="color:#10b981;margin-top:4px;">Endpoint: ${agent.endpoint} [ONLINE]</div>
          </div>
        </div>
      `;
    });
    container.innerHTML = html;
  } catch (err) {
    console.error('Error loading A2A agents:', err);
  }
}

async function loadMCPTools() {
  try {
    const res = await fetch(`${API_BASE}/mcp/tools`);
    const tools = await res.json();
    const container = document.getElementById('mcp-tools-grid');

    let html = '';
    tools.forEach(t => {
      const isAction = t.category === 'ACTION';
      html += `
        <div class="item-card">
          <div class="item-card-title">${isAction ? '⚡' : '🔍'} ${t.name}</div>
          <div class="item-card-desc">${t.description}</div>
          <div style="font-size:11px;margin-top:6px;">
            <span class="badge" style="background:${isAction ? 'rgba(245,158,11,0.2)' : 'rgba(99,102,241,0.2)'};color:${isAction ? '#f59e0b' : '#6366f1'};">
              ${t.category} ${t.requires_approval ? '(APPROVAL REQUIRED)' : ''}
            </span>
          </div>
        </div>
      `;
    });
    container.innerHTML = html;
  } catch (err) {
    console.error('Error loading MCP tools:', err);
  }
}

async function loadActivityTrace(eventId) {
  try {
    const res = await fetch(`${API_BASE}/events/${eventId}/activity`);
    const trace = await res.json();
    const container = document.getElementById('activity-stream');

    if (!trace.steps || trace.steps.length === 0) {
      container.innerHTML = '<p class="help-text">No activity recorded for this event trace.</p>';
      return;
    }

    let html = '';
    trace.steps.forEach(step => {
      html += `
        <div class="activity-step">
          <span class="step-agent">${step.agent_name}</span>
          <span class="step-action">${step.action_type}</span>
          <span style="color:#f3f4f6;">${JSON.stringify(step.details)}</span>
          <span class="step-dur">${step.duration_ms.toFixed(1)} ms</span>
        </div>
      `;
    });
    container.innerHTML = html;
  } catch (err) {
    console.error('Error loading activity trace:', err);
  }
}

async function handleSimulateSourceChange() {
  if (!currentEvent) return;

  try {
    const res = await fetch(`${API_BASE}/demo/simulate-source-change`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event_id: currentEvent.event_id })
    });
    
    const data = await res.json();
    alert('🚨 Pub/Sub Event Published: SOURCE_CHANGED!\n\nComplianceAgent & LifeEventOrchestrator re-planned task graph.\nNew task added with critical approval status.');
    
    currentEvent = data.updated_event;
    renderEventDashboard(currentEvent);
    loadActivityTrace(currentEvent.event_id);
  } catch (err) {
    alert('Failed to simulate source change: ' + err.message);
  }
}

async function approveTaskAction(taskId) {
  try {
    const res = await fetch(`${API_BASE}/tasks/${taskId}/approve`, { method: 'POST' });
    const data = await res.json();
    alert(`Task Action Approved!\n${data.message}`);
  } catch (err) {
    alert('Approval error: ' + err.message);
  }
}

async function handleRunEval() {
  const modal = document.getElementById('eval-modal');
  const body = document.getElementById('eval-results-body');
  modal.classList.remove('hidden');
  body.innerHTML = '<p style="color:#06b6d4;">🧪 Executing 50 International Life Event Benchmark Scenarios...</p>';

  try {
    const res = await fetch(`${API_BASE}/evaluation/run`, { method: 'POST' });
    const data = await res.json();

    let html = `
      <div class="eval-stats-grid">
        <div class="metric-box">
          <span class="metric-val" style="color:#10b981">${data.passed_scenarios}/${data.total_scenarios}</span>
          <span class="metric-lbl">Scenarios Passed</span>
        </div>
        <div class="metric-box">
          <span class="metric-val">${data.jurisdiction_accuracy}%</span>
          <span class="metric-lbl">Jurisdiction Accuracy</span>
        </div>
        <div class="metric-box">
          <span class="metric-val">${data.citation_precision}%</span>
          <span class="metric-lbl">Citation Precision</span>
        </div>
        <div class="metric-box">
          <span class="metric-val">${data.safety_disclaimer_compliance}%</span>
          <span class="metric-lbl">Safety Compliance</span>
        </div>
      </div>
      <div style="font-size:12px;color:#9ca3af;margin-bottom:12px;">Average Latency: ${data.average_latency_ms} ms</div>
      <div style="max-height:300px;overflow-y:auto;display:flex;flex-direction:column;gap:6px;">
    `;

    data.results_detail.forEach(r => {
      html += `
        <div style="background:rgba(30,41,59,0.6);padding:8px 12px;border-radius:4px;font-size:12px;display:flex;justify-content:space-between;">
          <span>${r.name}</span>
          <span style="color:${r.passed ? '#10b981' : '#f43f5e'}">${r.passed ? 'PASSED ✓' : 'FAILED ✗'} (${r.latency_ms} ms)</span>
        </div>
      `;
    });

    html += '</div>';
    body.innerHTML = html;
  } catch (err) {
    body.innerHTML = `<p style="color:#f43f5e;">Evaluation failed: ${err.message}</p>`;
  }
}

function closeEvalModal() {
  document.getElementById('eval-modal').classList.add('hidden');
}
