/**
 * ╔══════════════════════════════════════════════════════╗
 * ║  naomi-api.js — Frontend ↔ Backend connector        ║
 * ║  Include this in index.html after the main script   ║
 * ║  to make the blog fetch live data from Flask.       ║
 * ╚══════════════════════════════════════════════════════╝
 *
 * When running with Flask backend, add this to index.html:
 *   <script src="/static/js/naomi-api.js"></script>
 *
 * This overrides the static DATA object with live API data.
 */

(async function connectToBackend() {
  'use strict';

  // ── Detect if we're running with a backend ─────────────
  // If the API responds, we're in backend mode. Otherwise
  // we fall back to the embedded static DATA in index.html.
  let backendAvailable = false;
  try {
    const check = await fetch('/api/settings', { signal: AbortSignal.timeout(2000) });
    backendAvailable = check.ok;
  } catch (_) {
    console.info('[Naomi] Running in static mode (no backend).');
    return; // stop — use embedded DATA
  }

  if (!backendAvailable) return;
  console.info('[Naomi] 💜 Backend connected — loading live data.');

  // ── Helper ─────────────────────────────────────────────
  async function api(path) {
    try {
      const r = await fetch(path);
      if (!r.ok) throw new Error(r.status);
      return r.json();
    } catch (e) {
      console.warn('[Naomi] API error:', path, e);
      return null;
    }
  }

  // ── Load settings into DATA ────────────────────────────
  const settings = await api('/api/settings');
  if (settings) {
    window.DATA = window.DATA || {};
    Object.assign(DATA, {
      reasons:          settings.reasons          || DATA.reasons,
      typingMessages:   settings.love_messages    || DATA.typingMessages,
      surprises:        settings.surprise_messages || DATA.surprises,
    });
    // Update anniversary date
    if (settings.anniversary_date) {
      DATA.anniversaryDate = new Date(settings.anniversary_date + 'T00:00:00');
    }
  }

  // ── Load playlist ──────────────────────────────────────
  const playlistData = await api('/api/playlist');
  if (playlistData?.playlist) {
    DATA.playlist = playlistData.playlist.map(s => ({
      title:  s.title,
      artist: s.artist,
      emoji:  s.emoji,
      url:    s.url || '',
      pinned: s.pinned,
    }));
  }

  // ── Load blog posts ────────────────────────────────────
  const postsData = await api('/api/posts');
  if (postsData?.posts) {
    // Map backend posts to frontend format
    const catClassMap = {
      'Love Notes':    'cat-love-notes',
      'Memories':      'cat-memories',
      'Poems':         'cat-poems',
      'Daily Thoughts':'cat-daily',
      'Future Dreams': 'cat-dreams',
      'Photos':        'cat-photos',
    };
    DATA.blogPosts = postsData.posts.map(p => ({
      id:       p.id,
      pinned:   p.pinned,
      category: p.category,
      catClass: catClassMap[p.category] || 'cat-daily',
      date:     new Date(p.date).toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric'}),
      title:    p.title,
      excerpt:  p.excerpt,
      content:  p.content,
    }));
  }

  // ── Load memories / timeline ───────────────────────────
  const memories = await api('/api/memories');
  if (memories) {
    DATA.timeline = memories;
  }

  // ── Override countdown with live data ─────────────────
  const countdown = await api('/api/countdown');
  if (countdown) {
    // Patch the stat display if already rendered
    const daysEl = document.getElementById('days-together');
    if (daysEl) daysEl.textContent = countdown.days_together.toLocaleString();
  }

  // ── Re-render all dynamic sections ────────────────────
  // Wait for initSite to have already run, then refresh
  setTimeout(() => {
    // Re-render reasons
    const reasonsGrid = document.getElementById('reasons-grid');
    if (reasonsGrid) {
      reasonsGrid.innerHTML = '';
      DATA.reasons.forEach((r, i) => {
        const card = document.createElement('div');
        card.className = 'reason-card reveal';
        card.innerHTML = `
          <div class="reason-number">✦ ${String(i+1).padStart(2,'0')}</div>
          <div class="reason-icon">${r.icon}</div>
          <div class="reason-text">${r.text}</div>
        `;
        reasonsGrid.appendChild(card);
      });
      document.querySelectorAll('.reveal').forEach(el => {
        if (window.observer) observer.observe(el);
      });
    }

    // Re-render blog
    renderBlog?.('All');

    // Re-render timeline
    const tl = document.getElementById('timeline');
    if (tl) {
      tl.innerHTML = '';
      DATA.timeline.forEach(item => {
        const el = document.createElement('div');
        el.className = 'timeline-item reveal';
        el.innerHTML = `
          <div class="timeline-dot"></div>
          <div class="timeline-content">
            <div class="timeline-date">${item.date}</div>
            <div class="timeline-emoji">${item.emoji}</div>
            <div class="timeline-title">${item.title}</div>
            <div class="timeline-desc">${item.desc}</div>
          </div>
        `;
        tl.appendChild(el);
      });
    }

    // Add reaction counts to blog cards (live from backend)
    document.querySelectorAll('.reaction-btn').forEach(async btn => {
      const card   = btn.closest('.blog-card');
      const postId = card?.dataset.postId;
      if (!postId) return;
      const rxn = await api(`/api/reactions/${postId}`);
      if (rxn) {
        const emoji = btn.dataset.r;
        if (rxn[emoji] > 0) btn.textContent = `${emoji} ${rxn[emoji]}`;
      }
    });

  }, 600);

})();
