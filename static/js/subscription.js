/**
 * DiagCar — Subscription & 7-Attempt Limit Manager
 * =================================================
 * • Tracks free diagnostic uses in localStorage
 * • MAX_FREE = 7  attempts per account
 * • On attempt 8+: shows paywall modal BEFORE calling API
 * • Updates counter bar + sidebar dots in real time
 */

const MAX_FREE = 7;
const STORAGE_KEY = 'diagcar_free_used';

// ── Read / Write ─────────────────────────────────
function getUsedCount() {
  return parseInt(localStorage.getItem(STORAGE_KEY) || '0', 10);
}
function setUsedCount(n) {
  localStorage.setItem(STORAGE_KEY, String(n));
}
function incrementUsed() {
  const next = getUsedCount() + 1;
  setUsedCount(next);
  return next;
}
function getRemainingCount() {
  return Math.max(0, MAX_FREE - getUsedCount());
}
function isSubscribed() {
  // Future: check session token / server flag
  // For now: localStorage flag set after "subscribing"
  return localStorage.getItem('diagcar_subscribed') === '1';
}
function setSubscribed() {
  localStorage.setItem('diagcar_subscribed', '1');
}

// ── Render Dots ──────────────────────────────────
function renderDots(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const used = getUsedCount();
  container.innerHTML = '';
  for (let i = 0; i < MAX_FREE; i++) {
    const dot = document.createElement('span');
    dot.className = 'diag-dot ' + (
      i < used ? 'used' :
      i === used ? 'active' : 'available'
    );
    dot.title = i < used ? 'Used' : 'Available';
    container.appendChild(dot);
  }
}

// ── Update Counter Bar ───────────────────────────
function updateCounterUI() {
  const used = getUsedCount();
  const left = getRemainingCount();
  const sub  = isSubscribed();

  // Top counter bar
  const bar        = document.getElementById('diagCounterBar');
  const usedEl     = document.getElementById('counterUsed');
  const leftEl     = document.getElementById('counterLeft');

  if (bar) {
    bar.style.display = sub ? 'none' : 'flex';
  }
  if (usedEl) usedEl.textContent = Math.min(used, MAX_FREE);
  if (leftEl) {
    leftEl.textContent = sub ? '∞ unlimited' : `${left} remaining`;
    leftEl.style.color = left <= 2 ? '#ef4444' : left <= 4 ? '#f5b301' : '#22c55e';
  }
  renderDots('counterDots');

  // Sidebar
  const sideUsed = document.getElementById('sidebarUsed');
  if (sideUsed) sideUsed.textContent = Math.min(used, MAX_FREE);
  renderDots('sidebarDots');
}

// ── Gate: call before every diagnosis ────────────
function checkDiagnosisAllowed() {
  if (isSubscribed()) return true;
  const used = getUsedCount();
  if (used >= MAX_FREE) {
    // Show paywall
    if (window.openSubscriptionModal) {
      window.openSubscriptionModal('pro', true);
    }
    return false;
  }
  return true;
}

// ── Called after a successful AI response ────────
function recordDiagnosisUsed() {
  if (isSubscribed()) return;
  const newCount = incrementUsed();
  updateCounterUI();

  // Show soft warning at 5 and 6 uses
  if (newCount === 5 || newCount === 6) {
    const left = MAX_FREE - newCount;
    showDiagLimitWarning(left);
  }
  // Auto-open modal when limit hit
  if (newCount >= MAX_FREE) {
    setTimeout(() => {
      if (window.openSubscriptionModal) {
        window.openSubscriptionModal('pro', true);
      }
    }, 1800);
  }
}

// ── Soft warning banner ──────────────────────────
function showDiagLimitWarning(remaining) {
  const existing = document.getElementById('diagLimitWarn');
  if (existing) existing.remove();

  const bar = document.createElement('div');
  bar.id = 'diagLimitWarn';
  bar.style.cssText = `
    background:rgba(245,179,1,.12);border:1px solid rgba(245,179,1,.3);
    border-radius:14px;padding:12px 18px;margin-bottom:16px;
    display:flex;align-items:center;justify-content:space-between;gap:12px;
    animation: fadeInDown .4s ease;
  `;
  bar.innerHTML = `
    <span style="color:#f5b301;font-size:.88rem">
      ⚠️ <strong>${remaining} free diagnostic${remaining > 1 ? 's' : ''} remaining</strong>
      — upgrade for unlimited access.
    </span>
    <button onclick="window.openSubscriptionModal && window.openSubscriptionModal('pro',false)"
      style="background:linear-gradient(135deg,#18c8ff,#0b74ff);color:#fff;border:none;border-radius:10px;padding:6px 14px;font-size:.8rem;font-weight:700;cursor:pointer">
      💎 Upgrade
    </button>
  `;
  const chatBox = document.querySelector('.chat-box');
  if (chatBox) chatBox.insertAdjacentElement('beforebegin', bar);
}

// ── Init on page load ────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updateCounterUI();

  // If already at limit, disable send button immediately
  if (!isSubscribed() && getUsedCount() >= MAX_FREE) {
    const sendBtn = document.getElementById('sendBtn');
    if (sendBtn) {
      sendBtn.textContent = '🔒 Upgrade to Continue';
      sendBtn.style.background = 'rgba(255,255,255,.1)';
      sendBtn.addEventListener('click', (e) => {
        e.stopImmediatePropagation();
        if (window.openSubscriptionModal) window.openSubscriptionModal('pro', true);
      }, true);
    }
    showDiagLimitWarning(0);
  }
});

// ── Export for diagnostic.js ─────────────────────
window.DiagCarSub = {
  checkAllowed:     checkDiagnosisAllowed,
  recordUsed:       recordDiagnosisUsed,
  updateUI:         updateCounterUI,
  isSubscribed,
  setSubscribed,
  getUsed:          getUsedCount,
  getRemaining:     getRemainingCount,
};
