/* ============================================
   DailyMoney — Main Application Script v3.0
   Ultimate Edition — Zero Bug
   ============================================ */
(function () {
  'use strict';

  const isEN = window.location.pathname.startsWith('/en/');
  const grid = document.getElementById('article-grid');
  const backBtn = document.getElementById('backToTop');

  // ==============================
  // 1. HAMBURGER MENU
  // ==============================
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.getElementById('navLinks');
  const overlay = document.getElementById('navOverlay');

  function toggleNav() {
    hamburger.classList.toggle('active');
    navLinks.classList.toggle('open');
    if (overlay) overlay.classList.toggle('active');
    document.body.style.overflow = navLinks.classList.contains('open') ? 'hidden' : '';
  }

  if (hamburger) {
    hamburger.addEventListener('click', toggleNav);
    if (overlay) overlay.addEventListener('click', toggleNav);
  }

  // Close nav on link click
  if (navLinks) {
    navLinks.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        if (navLinks.classList.contains('open')) toggleNav();
      });
    });
  }

  // ==============================
  // 2. BACK TO TOP
  // ==============================
  if (backBtn) {
    window.addEventListener('scroll', function () {
      backBtn.classList.toggle('visible', window.scrollY > 400);
    });
    backBtn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ==============================
  // 3. ARTICLE GRID RENDER
  // ==============================
  function renderArticles() {
    if (!grid || !window.__ARTICLES) return;

    var articles = window.__ARTICLES;
    if (!articles.length) {
      grid.innerHTML = '<div class="empty-state"><div class="icon">📰</div><h3>' +
        (isEN ? 'No Articles Yet' : 'Belum Ada Artikel') + '</h3><p>' +
        (isEN ? 'New articles coming soon. Stay tuned!' : 'Artikel baru akan segera hadir. Pantau terus!') +
        '</p></div>';
      return;
    }

    // Show loading spinner
    grid.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';

    // Use requestAnimationFrame for smooth render
    requestAnimationFrame(function () {
      var html = '';
      articles.forEach(function (a, i) {
        var link = isEN ? '/en/articles/' : '/articles/';
        link += a.slug + '.html';

        var imgHtml = '';
        if (a.image_url) {
          imgHtml = '<img src="' + a.image_url + '" alt="' + a.judul.replace(/"/g, '&quot;') + '" loading="' + (i < 2 ? 'eager' : 'lazy') + '" onerror="this.parentElement.innerHTML=\'<div class=\\\'article-card-gradient\\\'></div>\'">';
        }

        var tag = a.tags ? a.tags.split(',')[0].trim() : (isEN ? 'Finance' : 'Keuangan');
        var excerpt = a.meta_desc ? a.meta_desc.substring(0, 120) : '';

        var langBadge = '';
        if (a.lang && a.lang === 'en') {
          langBadge = '<span class="lang-badge en">EN</span>';
        } else if (a.lang && a.lang === 'id') {
          langBadge = '<span class="lang-badge id">ID</span>';
        }

        html += '<a href="' + link + '" class="article-card' + (i === 0 ? ' featured' : '') + '" data-index="' + i + '">';
        html += '<div class="article-card-visual">' + imgHtml + '<div class="article-card-gradient"></div></div>';
        html += '<div class="article-card-body">';
        html += '<div class="article-card-top">';
        html += '<span class="tag">' + tag + langBadge + '</span>';
        html += '<h3>' + a.judul + '</h3>';
        html += '<p class="excerpt">' + excerpt + '</p>';
        html += '</div>';
        html += '<div class="meta"><span>📅 ' + a.date + '</span></div>';
        html += '</div></a>';
      });

      grid.innerHTML = html;
    });
  }

  // ==============================
  // 4. SEARCH
  // ==============================
  var searchInput = document.getElementById('searchInput');
  var searchBtn = document.getElementById('searchBtn');

  function performSearch() {
    if (!searchInput || !window.__ARTICLES) return;
    var q = searchInput.value.toLowerCase().trim();
    if (!q) {
      renderArticles();
      return;
    }
    var results = window.__ARTICLES.filter(function (a) {
      return a.judul.toLowerCase().indexOf(q) !== -1 ||
             a.meta_desc.toLowerCase().indexOf(q) !== -1 ||
             (a.tags && a.tags.toLowerCase().indexOf(q) !== -1);
    });
    if (!grid) return;
    if (!results.length) {
      grid.innerHTML = '<div class="empty-state"><div class="icon">🔍</div><h3>' +
        (isEN ? 'No Results' : 'Tidak Ditemukan') + '</h3><p>' +
        (isEN ? 'Try a different keyword' : 'Coba kata kunci lain') +
        '</p></div>';
      return;
    }
    // Temporarily override __ARTICLES for render
    var orig = window.__ARTICLES;
    window.__ARTICLES = results;
    renderArticles();
    window.__ARTICLES = orig;
  }

  if (searchBtn) {
    searchBtn.addEventListener('click', performSearch);
  }
  if (searchInput) {
    searchInput.addEventListener('keyup', function (e) {
      if (e.key === 'Enter') performSearch();
    });
  }

  // ==============================
  // 5. SOCIAL SHARE
  // ==============================
  var shareUrl = window.location.href;
  var shareTitle = document.title || 'DailyMoney';

  document.querySelectorAll('.share-btn').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var platform = btn.dataset.platform || '';
      var url = '';
      switch (platform) {
        case 'twitter':
          url = 'https://twitter.com/intent/tweet?text=' + encodeURIComponent(shareTitle) + '&url=' + encodeURIComponent(shareUrl);
          break;
        case 'facebook':
          url = 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(shareUrl);
          break;
        case 'whatsapp':
          url = 'https://wa.me/?text=' + encodeURIComponent(shareTitle + ' ' + shareUrl);
          break;
        case 'copy':
          navigator.clipboard.writeText(shareUrl).then(function () {
            btn.textContent = '✅ Copied!';
            setTimeout(function () { btn.textContent = '📋 Copy Link'; }, 2000);
          });
          return;
      }
      if (url) window.open(url, '_blank', 'width=600,height=400');
    });
  });

  // ==============================
  // 6. PWA INSTALL PROMPT
  // ==============================
  var deferredPrompt = null;
  var pwaPrompt = document.getElementById('pwaPrompt');

  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferredPrompt = e;
    if (pwaPrompt) pwaPrompt.classList.add('show');
  });

  var installBtn = document.getElementById('pwaInstallBtn');
  var dismissBtn = document.getElementById('pwaDismissBtn');

  if (installBtn) {
    installBtn.addEventListener('click', function () {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(function () {
          deferredPrompt = null;
          if (pwaPrompt) pwaPrompt.classList.remove('show');
        });
      }
    });
  }
  if (dismissBtn) {
    dismissBtn.addEventListener('click', function () {
      if (pwaPrompt) pwaPrompt.classList.remove('show');
    });
  }

  // ==============================
  // 7. DARK MODE DETECTION LOG
  // ==============================
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    console.log('🌙 Dark mode active');
  }

  // ==============================
  // 8. NEWSLETTER FORM
  // ==============================
  var newsletterForm = document.getElementById('newsletterForm');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var email = newsletterForm.querySelector('input').value.trim();
      if (email) {
        // Store in localStorage for now (MVP approach)
        var subs = JSON.parse(localStorage.getItem('dm_subs') || '[]');
        if (subs.indexOf(email) === -1) {
          subs.push(email);
          localStorage.setItem('dm_subs', JSON.stringify(subs));
        }
        newsletterForm.innerHTML = '<p style="color:var(--red);font-weight:600;">✅ ' +
          (isEN ? 'Thank you for subscribing!' : 'Terima kasih telah berlangganan!') + '</p>';
      }
    });
  }

  // ==============================
  // 9. ARTICLE TABLE TOUCH FIX
  // ==============================
  // Ensure tables are scrollable on touch devices
  if ('ontouchstart' in window) {
    document.querySelectorAll('.table-wrapper').forEach(function (wrapper) {
      wrapper.style.WebkitOverflowScrolling = 'touch';
    });
  }

  // ==============================
  // 10. INIT
  // ==============================
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderArticles);
  } else {
    renderArticles();
  }

  // Initialize share URL for article pages
  if (document.querySelector('.article-page')) {
    document.querySelectorAll('.share-btn').forEach(function (btn) {
      if (!btn.dataset.platform) return;
      // Already handled above
    });
  }

  console.log('📰 DailyMoney v3.0 loaded');
})();

// --- Register Service Worker ---
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('sw.js').catch(function() {});
  });
}
