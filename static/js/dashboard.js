/* DiagCar — Dashboard JS: Charts + History + Stats */
'use strict';

document.addEventListener('DOMContentLoaded', () => {
  loadStats();
  loadHistory();
  updateSubUI();
});

// ── Subscription UI sync ──────────────────────────────────────────────
function updateSubUI() {
  const sub = window.DiagCarSub;
  if (!sub) return;
  const used = sub.getUsed();
  const rem  = sub.getRemaining();
  const el   = document.getElementById('dashSubUsed');
  if (el) el.textContent = `${used} / 7 used — ${rem} remaining`;
  const dotsEl = document.getElementById('dashSubDots');
  if (dotsEl) {
    dotsEl.innerHTML = '';
    for (let i=0;i<7;i++){
      const d=document.createElement('span');
      d.className='diag-dot '+(i<used?'used':i===used?'active':'available');
      dotsEl.appendChild(d);
    }
  }
}

// ── Load Stats ────────────────────────────────────────────────────────
async function loadStats() {
  try {
    const res  = await fetch('/api/stats');
    const data = await res.json();
    const tot  = data.total || 0;

    document.getElementById('totalDiag').textContent   = tot;
    const crit = (data.by_severity || {})['حرج'] || 0;
    document.getElementById('criticalCount').textContent = crit;

    // Vehicle health score
    const health = tot === 0 ? '—' :
      crit >= 3 ? '⚠️ Poor' :
      crit >= 1 ? '🟡 Fair' : '✅ Good';
    document.getElementById('vehicleHealth').textContent = health;

    // Last scan
    const hist  = await fetch('/api/history');
    const hdata = await hist.json();
    if (hdata && hdata.length > 0) {
      const d = new Date(hdata[0].created_at);
      document.getElementById('lastScan').textContent =
        isNaN(d) ? '—' : d.toLocaleDateString();
    }

    // Render charts
    renderSeverityChart(data.by_severity || {});
    renderFaultsChart(data.top_faults || []);

  } catch(e) {
    console.log('Stats unavailable:', e.message);
    renderSeverityChart({});
    renderFaultsChart([]);
  }
}

// ── Severity Doughnut ─────────────────────────────────────────────────
function renderSeverityChart(byS) {
  const ctx = document.getElementById('chartSeverity');
  if (!ctx || !window.Chart) return;
  const labels  = ['Critical حرج','High عالي','Medium متوسط','Low منخفض'];
  const vals    = [byS['حرج']||0, byS['عالي']||0, byS['متوسط']||0, byS['منخفض']||0];
  const total   = vals.reduce((a,b)=>a+b,0);
  if (total === 0) { vals[2]=1; }   // placeholder

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets:[{
        data: vals,
        backgroundColor:['#ef444466','#f5b30166','#3b82f666','#22c55e66'],
        borderColor:    ['#ef4444','#f5b301','#3b82f6','#22c55e'],
        borderWidth: 2,
      }],
    },
    options:{
      responsive:true, maintainAspectRatio:true,
      plugins:{
        legend:{ labels:{ color:'#b3c6d6', font:{size:11} } },
        tooltip:{ callbacks:{ label: ctx => ` ${ctx.label}: ${ctx.raw}` } },
      },
    },
  });
}

// ── Top Faults Bar ────────────────────────────────────────────────────
function renderFaultsChart(topFaults) {
  const ctx = document.getElementById('chartFaults');
  if (!ctx || !window.Chart) return;

  // Use real data or demo data
  const data = topFaults.length > 0 ? topFaults : [
    {fault:'Engine Overheat', count:3},
    {fault:'Injector Fault',  count:2},
    {fault:'Battery Issue',   count:2},
    {fault:'ABS Fault',       count:1},
    {fault:'Brake Issue',     count:1},
  ];

  const labels = data.map(d => d.fault.substring(0,20));
  const vals   = data.map(d => d.count);

  new Chart(ctx, {
    type: 'bar',
    data:{
      labels,
      datasets:[{
        label:'Occurrences',
        data: vals,
        backgroundColor:'rgba(24,200,255,.25)',
        borderColor:'#18c8ff',
        borderWidth:2,
        borderRadius:8,
      }],
    },
    options:{
      responsive:true, maintainAspectRatio:true,
      indexAxis:'y',
      plugins:{ legend:{ display:false } },
      scales:{
        x:{ ticks:{ color:'#7f97b2' }, grid:{ color:'rgba(255,255,255,.05)' } },
        y:{ ticks:{ color:'#b3c6d6', font:{size:11} }, grid:{ display:false } },
      },
    },
  });
}

// ── Load History ──────────────────────────────────────────────────────
async function loadHistory() {
  const el = document.getElementById('historyList');
  if (!el) return;
  try {
    const res  = await fetch('/api/history');
    const data = await res.json();
    if (!data || !data.length) {
      el.innerHTML = `<div style="text-align:center;color:#7f97b2;padding:40px 0">
        No diagnostics yet. <a href="/diagnostic" style="color:#18c8ff">Start your first one →</a></div>`;
      return;
    }
    el.innerHTML = data.slice(0,10).map(d => {
      const sev   = d.severity || '';
      const prob  = d.probability ? `${parseFloat(d.probability).toFixed(0)}%` : '';
      const date  = d.created_at ? new Date(d.created_at).toLocaleString() : '';
      const sClass= sev.includes('حرج')||sev.toLowerCase().includes('crit') ? 'critical' :
                    sev.includes('عالي')||sev.toLowerCase().includes('high') ? 'high' :
                    sev.toLowerCase().includes('med') ? 'medium' : 'low';
      return `<div class="history-item">
        <h4 class="fault-title">${escHtml(d.top_fault||'Unknown fault')}</h4>
        <p class="fault-desc">${escHtml((d.input_text||'').substring(0,90))}${(d.input_text||'').length>90?'…':''}</p>
        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
          <span class="prob-badge">${prob}</span>
          <span class="sev-badge ${sClass}">${sev||'—'}</span>
          <span style="font-size:.76rem;color:#7f97b2;margin-right:auto">${date}</span>
          <a href="/diagnostic" style="font-size:.78rem;color:#18c8ff;text-decoration:none">Re-diagnose →</a>
        </div>
      </div>`;
    }).join('');
  } catch(e) {
    el.innerHTML = `<div style="color:#7f97b2;text-align:center;padding:30px">
      History unavailable — <a href="/diagnostic" style="color:#18c8ff">start a new diagnosis</a></div>`;
  }
}

async function clearHistory() {
  if (!confirm('Clear all diagnostic history?')) return;
  try {
    await fetch('/api/history', {method:'DELETE'});
  } catch(e) {}
  document.getElementById('historyList').innerHTML =
    `<div style="text-align:center;color:#7f97b2;padding:30px">History cleared.</div>`;
}

function escHtml(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
