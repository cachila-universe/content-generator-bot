/**
 * Dashboard JS: handles Chart.js rendering, log polling, stat refresh, bot controls.
 */

// ── Bot Control ─────────────────────────────────────────────────────────────

function botStart() {
  fetch('/api/bot/start', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.ok) updateBotUI(true);
    })
    .catch(err => console.error('Start failed:', err));
}

function botStop() {
  if (!confirm('Stop the bot? Scheduled jobs will pause until you start it again.')) return;
  fetch('/api/bot/stop', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      if (data.ok) updateBotUI(false);
    })
    .catch(err => console.error('Stop failed:', err));
}

function updateBotUI(running) {
  // Sidebar dot
  const dot = document.getElementById('statusDot');
  const txt = document.getElementById('statusText');
  if (dot) {
    dot.className = 'status-dot ' + (running ? 'running' : 'stopped');
  }
  if (txt) txt.textContent = running ? 'Running' : 'Stopped';

  // Top-bar buttons
  const btnStart = document.getElementById('btnStart');
  const btnStop = document.getElementById('btnStop');
  if (btnStart) btnStart.style.display = running ? 'none' : '';
  if (btnStop) btnStop.style.display = running ? '' : 'none';

  // Status banner (index page)
  const banner = document.getElementById('statusBanner');
  if (banner) {
    banner.className = 'status-banner ' + (running ? 'status-running' : 'status-stopped');
  }
  const bannerDot = document.getElementById('bannerDot');
  if (bannerDot) {
    bannerDot.className = 'status-dot-lg ' + (running ? 'dot-green' : 'dot-red');
  }
  const bannerText = document.getElementById('bannerText');
  if (bannerText) bannerText.textContent = 'Bot is ' + (running ? 'RUNNING' : 'STOPPED');
}

function pollBotState() {
  fetch('/api/bot/state')
    .then(r => r.json())
    .then(state => {
      updateBotUI(state.bot_running);

      // Update banner detail if present
      const detail = document.getElementById('bannerDetail');
      if (detail && state.schedule) {
        detail.textContent = (state.posts_today || 0) + ' posts today · Max ' +
          state.schedule.max_posts_per_day + '/day';
      }
    })
    .catch(() => {});
}

// ── Niche & Platform Toggles ────────────────────────────────────────────────

function toggleNiche(nicheId, enabled) {
  fetch('/api/niche/' + nicheId + '/toggle', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enabled: enabled }),
  })
    .then(r => r.json())
    .then(data => {
      if (!data.ok) return;
      const card = document.getElementById('niche-' + nicheId);
      if (card) {
        if (enabled) card.classList.remove('niche-disabled');
        else card.classList.add('niche-disabled');
      }
    })
    .catch(err => console.error('Toggle niche failed:', err));
}

function togglePlatform(platform, enabled) {
  fetch('/api/platform/' + platform + '/toggle', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enabled: enabled }),
  })
    .then(r => r.json())
    .then(() => {})
    .catch(err => console.error('Toggle platform failed:', err));
}

// ── Schedule Settings ───────────────────────────────────────────────────────

function updateSchedule() {
  const maxPosts = document.getElementById('maxPostsPerDay');
  const cooldown = document.getElementById('cooldownHours');
  const jitter = document.getElementById('randomizeMinutes');
  if (!maxPosts || !cooldown || !jitter) return;

  fetch('/api/schedule/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      max_posts_per_day: parseInt(maxPosts.value) || 3,
      cooldown_hours: parseInt(cooldown.value) || 20,
      randomize_minutes: parseInt(jitter.value) || 15,
    }),
  })
    .then(r => r.json())
    .then(data => {
      if (data.ok) {
        // Brief visual feedback
        const btn = document.querySelector('.btn-save');
        if (btn) {
          const orig = btn.textContent;
          btn.textContent = '✅ Saved!';
          setTimeout(() => btn.textContent = orig, 2000);
        }
      }
    })
    .catch(err => console.error('Schedule update failed:', err));
}

// ── Manual Trigger Safety ───────────────────────────────────────────────────

var _triggerArmed = false;
var _triggerTimeout = null;

function armTrigger() {
  _triggerArmed = true;
  const fireBtn = document.getElementById('btnTriggerFire');
  const armBtn = document.getElementById('btnTriggerArm');
  if (fireBtn) {
    fireBtn.disabled = false;
    fireBtn.classList.add('armed');
  }
  if (armBtn) {
    armBtn.textContent = '🔒 Armed (10s)';
    armBtn.disabled = true;
  }
  // Auto-disarm after 10 seconds
  if (_triggerTimeout) clearTimeout(_triggerTimeout);
  _triggerTimeout = setTimeout(disarmTrigger, 10000);
}

function disarmTrigger() {
  _triggerArmed = false;
  const fireBtn = document.getElementById('btnTriggerFire');
  const armBtn = document.getElementById('btnTriggerArm');
  if (fireBtn) {
    fireBtn.disabled = true;
    fireBtn.classList.remove('armed');
  }
  if (armBtn) {
    armBtn.textContent = '🔓 Arm Trigger';
    armBtn.disabled = false;
  }
}

function fireTrigger() {
  if (!_triggerArmed) return;
  const nicheSelect = document.getElementById('triggerNiche');
  const subtopicSelect = document.getElementById('triggerSubtopic');
  const status = document.getElementById('triggerStatus');
  if (!nicheSelect || !nicheSelect.value) {
    if (status) {
      status.textContent = '⚠ Select a niche first.';
      status.className = 'trigger-status error';
    }
    return;
  }

  // Gather platforms
  var platforms = [];
  if (document.getElementById('trigBlog') && document.getElementById('trigBlog').checked) platforms.push('blog');
  if (document.getElementById('trigShorts') && document.getElementById('trigShorts').checked) platforms.push('youtube_shorts');
  if (document.getElementById('trigTwitter') && document.getElementById('trigTwitter').checked) platforms.push('twitter');
  if (document.getElementById('trigPinterest') && document.getElementById('trigPinterest').checked) platforms.push('pinterest');
  if (platforms.length === 0) platforms.push('blog');

  var payload = {
    confirm: 'CONFIRM_TRIGGER',
    niche_id: nicheSelect.value,
    platforms: platforms,
  };

  // Include subtopic if selected
  if (subtopicSelect && subtopicSelect.value) {
    payload.subtopic_id = subtopicSelect.value;
  }

  fetch('/api/trigger', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
    .then(r => r.json())
    .then(data => {
      if (data.ok) {
        if (status) {
          status.textContent = '✅ ' + data.message;
          status.className = 'trigger-status success';
        }
      } else {
        if (status) {
          status.textContent = '⚠ ' + (data.error || 'Unknown error');
          status.className = 'trigger-status error';
        }
      }
      disarmTrigger();
    })
    .catch(err => {
      if (status) {
        status.textContent = '⚠ Request failed: ' + err.message;
        status.className = 'trigger-status error';
      }
      disarmTrigger();
    });
}

// ── Subtopic Dropdown for Manual Trigger ────────────────────────────────────

function updateSubtopicDropdown() {
  var nicheSelect = document.getElementById('triggerNiche');
  var subtopicSelect = document.getElementById('triggerSubtopic');
  if (!nicheSelect || !subtopicSelect) return;

  // Clear existing options
  subtopicSelect.innerHTML = '<option value="">Auto-select subtopic (least covered)</option>';

  var selectedOption = nicheSelect.options[nicheSelect.selectedIndex];
  if (!selectedOption || !selectedOption.value) return;

  try {
    var subtopics = JSON.parse(selectedOption.getAttribute('data-subtopics') || '{}');
    for (var stId in subtopics) {
      if (subtopics.hasOwnProperty(stId)) {
        var opt = document.createElement('option');
        opt.value = stId;
        opt.textContent = subtopics[stId].name || stId;
        subtopicSelect.appendChild(opt);
      }
    }
  } catch (e) {
    console.debug('Failed to parse subtopics:', e);
  }
}

// ── Mobile Sidebar ──────────────────────────────────────────────────────────

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (sidebar) sidebar.classList.toggle('open');
}

// ── Bot Mode Control ────────────────────────────────────────────────────────

function setBotMode(mode) {
  fetch('/api/bot/mode', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode: mode }),
  })
    .then(r => r.json())
    .then(data => {
      if (data.ok) {
        // Update button states
        ['paused', 'scheduled', 'manual'].forEach(m => {
          const btn = document.getElementById('btn' + m.charAt(0).toUpperCase() + m.slice(1));
          if (btn) {
            btn.className = 'btn ' + (m === data.bot_mode ? 'btn-mode-active' : 'btn-mode');
          }
        });
        // Update status text
        const status = document.getElementById('modeStatus');
        if (status) status.innerHTML = 'Current mode: <strong>' + data.bot_mode + '</strong>';
        // Show/hide Run All section
        const runAll = document.getElementById('runAllSection');
        if (runAll) {
          runAll.classList.toggle('hidden', data.bot_mode !== 'manual');
        }
        // Update banner
        updateBotUI(true);
        const bannerText = document.getElementById('bannerText');
        if (bannerText) {
          var suffix = data.bot_mode === 'paused' ? ' (PAUSED)' : '';
          bannerText.textContent = 'Bot is RUNNING' + suffix;
        }
      }
    })
    .catch(err => console.error('Set mode failed:', err));
}

// ── Run All Pipeline ────────────────────────────────────────────────────────

var _runAllArmed = false;
var _runAllTimeout = null;

function armRunAll() {
  _runAllArmed = true;
  const fireBtn = document.getElementById('btnRunAllFire');
  const armBtn = document.getElementById('btnRunAllArm');
  if (fireBtn) { fireBtn.disabled = false; fireBtn.classList.add('armed'); }
  if (armBtn) { armBtn.textContent = '🔒 Armed (15s)'; armBtn.disabled = true; }
  if (_runAllTimeout) clearTimeout(_runAllTimeout);
  _runAllTimeout = setTimeout(disarmRunAll, 15000);
}

function disarmRunAll() {
  _runAllArmed = false;
  const fireBtn = document.getElementById('btnRunAllFire');
  const armBtn = document.getElementById('btnRunAllArm');
  if (fireBtn) { fireBtn.disabled = true; fireBtn.classList.remove('armed'); }
  if (armBtn) { armBtn.textContent = '🔓 Arm Pipeline'; armBtn.disabled = false; }
}

function fireRunAll() {
  if (!_runAllArmed) return;
  const status = document.getElementById('runAllStatus');
  const fireBtn = document.getElementById('btnRunAllFire');
  if (fireBtn) { fireBtn.disabled = true; fireBtn.textContent = '⏳ Running pipeline...'; }
  if (status) { status.textContent = 'Running all tasks in dependency order...'; status.className = 'trigger-status'; }

  fetch('/api/pipeline/run-all', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ confirm: 'CONFIRM_RUN_ALL' }),
  })
    .then(r => r.json())
    .then(data => {
      if (data.ok) {
        const s = data.summary;
        if (status) {
          status.textContent = '✅ Pipeline complete: ' + s.steps_completed + ' steps, ' + (s.errors || []).length + ' errors';
          status.className = 'trigger-status success';
        }
      } else {
        if (status) {
          status.textContent = '❌ ' + (data.error || 'Unknown error');
          status.className = 'trigger-status error';
        }
      }
      disarmRunAll();
      if (fireBtn) fireBtn.textContent = '🚀 Run All Tasks';
    })
    .catch(err => {
      if (status) {
        status.textContent = '❌ Request failed: ' + err.message;
        status.className = 'trigger-status error';
      }
      disarmRunAll();
      if (fireBtn) fireBtn.textContent = '🚀 Run All Tasks';
    });
}

// ── Helpers ────────────────────────────────────────────────────────────────

function renderLineChart(canvasId, labels, data, label, color) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  if (canvas._chartInstance) canvas._chartInstance.destroy();

  const ctx = canvas.getContext('2d');
  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: label,
        data: data,
        borderColor: color || '#00ff88',
        backgroundColor: hexToRgba(color || '#00ff88', 0.08),
        borderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 5,
        fill: true,
        tension: 0.4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#21262d',
          borderColor: '#30363d',
          borderWidth: 1,
          titleColor: '#e6edf3',
          bodyColor: '#8b949e',
        },
      },
      scales: {
        x: {
          ticks: { color: '#8b949e', maxRotation: 45 },
          grid: { color: 'rgba(48,54,61,0.5)' },
        },
        y: {
          ticks: { color: '#8b949e' },
          grid: { color: 'rgba(48,54,61,0.5)' },
          beginAtZero: true,
        },
      },
    },
  });
  canvas._chartInstance = chart;
  return chart;
}

function renderBarChart(canvasId, labels, data, label, color) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  if (canvas._chartInstance) canvas._chartInstance.destroy();

  const ctx = canvas.getContext('2d');
  const chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: label,
        data: data,
        backgroundColor: hexToRgba(color || '#58a6ff', 0.6),
        borderColor: color || '#58a6ff',
        borderWidth: 1,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#21262d',
          borderColor: '#30363d',
          borderWidth: 1,
          titleColor: '#e6edf3',
          bodyColor: '#8b949e',
        },
      },
      scales: {
        x: {
          ticks: { color: '#8b949e', maxRotation: 30 },
          grid: { color: 'rgba(48,54,61,0.5)' },
        },
        y: {
          ticks: { color: '#8b949e' },
          grid: { color: 'rgba(48,54,61,0.5)' },
          beginAtZero: true,
        },
      },
    },
  });
  canvas._chartInstance = chart;
  return chart;
}

function hexToRgba(hex, alpha) {
  const clean = hex.replace('#', '');
  const r = parseInt(clean.substring(0, 2), 16);
  const g = parseInt(clean.substring(2, 4), 16);
  const b = parseInt(clean.substring(4, 6), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function animateCounter(el, target, prefix, suffix) {
  prefix = prefix || '';
  suffix = suffix || '';
  const start = 0;
  const duration = 800;
  const startTime = performance.now();

  function update(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(start + (target - start) * eased);
    el.textContent = prefix + current.toLocaleString() + suffix;
    if (progress < 1) requestAnimationFrame(update);
    else el.textContent = prefix + target.toLocaleString() + suffix;
  }
  requestAnimationFrame(update);
}

function updateTimestamp() {
  const el = document.getElementById('updateTime');
  if (el) el.textContent = new Date().toLocaleTimeString();
}

// ── Index page ──────────────────────────────────────────────────────────────

function initIndexPage() {
  if (!document.getElementById('postsChart') && !document.getElementById('incomeChart')) return;

  function loadStats() {
    fetch('/api/stats')
      .then(r => r.json())
      .then(stats => {
        // Update metric cards
        const postsEl = document.getElementById('totalPosts');
        if (postsEl) animateCounter(postsEl, stats.total_posts);

        const videosEl = document.getElementById('totalVideos');
        if (videosEl) animateCounter(videosEl, stats.total_videos);

        const incomeEl = document.getElementById('estIncome');
        if (incomeEl) incomeEl.textContent = '$' + stats.estimated_income.toFixed(2);

        const clicksEl = document.getElementById('totalClicks');
        if (clicksEl) animateCounter(clicksEl, stats.total_clicks);

        updateTimestamp();
      })
      .catch(() => {});
  }

  function loadPostsChart() {
    fetch('/api/posts-chart')
      .then(r => r.json())
      .then(data => renderBarChart('postsChart', data.labels, data.data, 'Posts', '#58a6ff'))
      .catch(() => {});
  }

  function loadIncomeChart() {
    fetch('/api/income-chart')
      .then(r => r.json())
      .then(data => renderLineChart('incomeChart', data.labels, data.data, 'Income ($)', '#00ff88'))
      .catch(() => {});
  }

  loadStats();
  loadPostsChart();
  loadIncomeChart();

  // Auto-refresh stats every 60 seconds
  const refreshSeconds = (window.AUTO_REFRESH_SECONDS || 60) * 1000;
  setInterval(loadStats, refreshSeconds);
}

// ── Analytics page ──────────────────────────────────────────────────────────

function initAnalyticsPage() {
  if (!document.getElementById('postsPerNicheChart')) return;

  const nicheStats = window.nicheStats || [];
  const labels = nicheStats.map(s => s.niche_name || s.niche_id);
  const posts = nicheStats.map(s => s.total_posts || 0);
  const income = nicheStats.map(s => parseFloat(s.estimated_income) || 0);
  const clicks = nicheStats.map(s => s.total_clicks || 0);

  renderBarChart('postsPerNicheChart', labels, posts, 'Posts', '#58a6ff');
  renderBarChart('incomePerNicheChart', labels, income, 'Income ($)', '#00ff88');
  renderBarChart('clicksPerNicheChart', labels, clicks, 'Clicks', '#e3b341');

  updateTimestamp();
}

// ── Logs page ───────────────────────────────────────────────────────────────

function initLogsPage() {
  const container = document.getElementById('logContainer');
  if (!container) return;

  function levelClass(level) {
    const map = { INFO: 'info', SUCCESS: 'success', ERROR: 'error', WARNING: 'warning' };
    return map[level] || 'info';
  }

  function buildLogEntry(log) {
    const div = document.createElement('div');
    div.className = `log-entry log-${levelClass(log.level)}`;
    div.dataset.level = log.level;

    const badge = `<span class="log-level badge badge-${levelClass(log.level)}">${log.level}</span>`;
    const ts = `<span class="log-timestamp">${log.timestamp || ''}</span>`;
    const niche = log.niche_id ? `<span class="log-niche">[${log.niche_id}]</span>` : '';
    const action = `<span class="log-action">${log.action || ''}</span>`;
    const sep = `<span class="log-sep">—</span>`;
    const msg = `<span class="log-message">${log.message || ''}</span>`;
    const err = log.error ? `<div class="log-error">⚠ ${log.error}</div>` : '';
    div.innerHTML = badge + ts + niche + action + sep + msg + err;

    // Apply current filter
    const currentFilter = window._logFilter || 'ALL';
    if (currentFilter !== 'ALL' && log.level !== currentFilter) {
      div.style.display = 'none';
    }
    return div;
  }

  let lastLogId = 0;

  function pollLogs() {
    fetch('/api/logs?limit=200')
      .then(r => r.json())
      .then(logs => {
        if (!logs || !logs.length) return;

        const newestId = logs[0].id || 0;
        if (newestId === lastLogId) return;
        lastLogId = newestId;

        // Clear and repopulate
        container.innerHTML = '';
        const frag = document.createDocumentFragment();
        logs.forEach(log => frag.appendChild(buildLogEntry(log)));
        container.appendChild(frag);

        const countEl = document.getElementById('logCount');
        if (countEl) countEl.textContent = `${logs.length} entries`;

        updateTimestamp();
      })
      .catch(() => {});
  }

  // Store filter state globally so buildLogEntry can access it
  window._logFilter = 'ALL';
  const origFilterLogs = window.filterLogs;
  window.filterLogs = function(level, btn) {
    window._logFilter = level;
    if (origFilterLogs) origFilterLogs(level, btn);
    // Re-apply filter to current entries
    document.querySelectorAll('.log-entry').forEach(el => {
      el.style.display = (level === 'ALL' || el.dataset.level === level) ? '' : 'none';
    });
  };

  pollLogs();
  setInterval(pollLogs, 5000);
}

// ── DOMContentLoaded ────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function () {
  updateTimestamp();
  initIndexPage();
  initAnalyticsPage();
  initLogsPage();

  // Poll bot state every 10 seconds (works on all pages)
  pollBotState();
  setInterval(pollBotState, 10000);
});
