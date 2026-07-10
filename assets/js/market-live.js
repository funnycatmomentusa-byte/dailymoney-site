(function() {
  'use strict';

  var LS_KEY = 'dm_market_data_v6';
  var REFRESH_MS = 30 * 1000;
  var COINGECKO_API = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true';

  var DEFAULTS = {
    'BTC': { price: 63067, change: -1.45 },
    'ETH': { price: 1777, change: -1.17 },
    'IHSG': { price: 5986, change: 1.19 },
    'XAU': { price: 4120, change: -0.89 },
    'USDIDR': { price: 17983, change: -0.06 }
  };

  var cache = {};
  var lastFetch = 0;

  function persistCache() {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify({ data: cache, ts: Date.now() }));
    } catch (e) {}
  }

  function loadCacheFromStorage() {
    try {
      var saved = localStorage.getItem(LS_KEY);
      if (saved) {
        var parsed = JSON.parse(saved);
        if (parsed && parsed.data) {
          Object.assign(cache, parsed.data);
          updateUI();
        }
      }
    } catch (e) {}
  }

  function flashElement(el, isUp) {
    if (!el) return;
    var cls = el.className;
    el.className = cls + ' price-flash-' + (isUp ? 'up' : 'down');
    setTimeout(function() { el.className = cls; }, 1200);
  }

  function formatPrice(price, symbol) {
    var num = Number(price);
    if (isNaN(num)) return '—';
    if (symbol === 'IHSG') return num.toLocaleString('id-ID', { maximumFractionDigits: 1 });
    if (symbol === 'USDIDR') return 'Rp' + num.toLocaleString('id-ID', { maximumFractionDigits: 0 });
    if (symbol === 'XAU' || symbol === 'BTC' || symbol === 'ETH')
      return '$' + num.toLocaleString('en-US', { maximumFractionDigits: 0 });
    return num.toLocaleString('id-ID', { maximumFractionDigits: 1 });
  }

  function formatChange(val) {
    var num = Number(val);
    if (isNaN(num)) return '—';
    return (num >= 0 ? '+' : '') + num.toFixed(2) + '%';
  }

  /* Update hero market stats (homepage) */
  function updateHeroStats() {
    var cards = document.querySelectorAll('.hero-market-stat');
    cards.forEach(function(card) {
      var sym = card.getAttribute('data-symbol');
      if (!sym) return;
      var data = cache[sym];
      if (!data || data.price == null) return;
      var numEl = card.querySelector('.stat-num');
      var lblEl = card.querySelector('.stat-lbl');
      if (numEl) {
        var newVal = formatPrice(data.price, sym);
        if (numEl.textContent !== newVal) flashElement(numEl, data.change >= 0);
        numEl.textContent = newVal;
        numEl.className = 'stat-num' + (data.change >= 0 ? ' up' : ' down');
      }
      if (lblEl) {
        lblEl.textContent = formatChange(data.change);
        lblEl.className = 'stat-lbl' + (data.change >= 0 ? ' up' : ' down');
      }
    });
  }

  /* Update sidebar market items (Pasar Live) */
  function updateSidebar() {
    document.querySelectorAll('.dm-market-item').forEach(function(el) {
      var rawId = el.id ? el.id.replace('market-', '') : '';
      if (!rawId) return;
      var sym = rawId === 'usdidr' ? 'USDIDR' : rawId.toUpperCase();
      var data = cache[sym];
      if (!data || data.price == null) return;
      var priceEl = el.querySelector('.dm-market-price');
      var pctEl = el.querySelector('.dm-market-pct');
      if (priceEl) priceEl.textContent = formatPrice(data.price, sym);
      if (pctEl && data.change !== null && data.change !== undefined) {
        pctEl.textContent = formatChange(data.change);
        pctEl.className = 'dm-market-pct ' + (data.change >= 0 ? 'up' : 'down');
      }
    });
  }

  /* Update ticker bar */
  function updateTicker() {
    document.querySelectorAll('.dm-ticker-item').forEach(function(item) {
      var symEl = item.querySelector('.dm-ticker-symbol');
      if (!symEl) return;
      var sym = symEl.textContent.trim();
      var data = cache[sym];
      if (!data || data.price == null) return;
      var priceEl = item.querySelector('.ticker-price');
      var changeEl = item.querySelector('.ticker-change');
      if (priceEl) priceEl.textContent = formatPrice(data.price, sym);
      if (changeEl && data.change !== null && data.change !== undefined) {
        changeEl.textContent = formatChange(data.change);
        changeEl.className = 'ticker-change ' + (data.change >= 0 ? 'up' : 'down');
      }
    });
  }

  /* Update stock comparison table */
  function updateStocks() {
    document.querySelectorAll('[data-stock]').forEach(function(el) {
      var sym = el.getAttribute('data-stock');
      if (!sym) return;
      var data = cache[sym];
      if (!data || data.price == null) return;
      var priceEl = document.getElementById('stock-' + sym);
      var changeEl = document.getElementById('change-' + sym);
      if (priceEl) {
        var newV = 'Rp' + Math.round(data.price).toLocaleString('id-ID');
        if (priceEl.textContent !== newV) flashElement(priceEl, data.change >= 0);
        priceEl.textContent = newV;
      }
      if (changeEl && data.change !== null && data.change !== undefined) {
        changeEl.textContent = formatChange(data.change);
        changeEl.className = 'cmp-schange ' + (data.change === 0 ? 'cmp-neutral' : (data.change > 0 ? 'cmp-up' : 'cmp-down'));
      }
    });
  }

  /* Update compact IHSG widget */
  function updateCompactIHSG() {
    var data = cache['IHSG'];
    var pEl = document.getElementById('cmp-ihsg-price');
    var cEl = document.getElementById('cmp-ihsg-change');
    if (!data || data.price == null || !pEl) return;
    var newV = Number(data.price).toLocaleString('id-ID', { maximumFractionDigits: 1 });
    if (pEl.textContent !== newV) flashElement(pEl, data.change >= 0);
    pEl.textContent = newV;
    pEl.className = 'cmp-price ' + (data.change >= 0 ? 'up' : 'down');
    if (cEl && data.change !== null) {
      cEl.textContent = formatChange(data.change);
      cEl.className = 'cmp-change ' + (data.change >= 0 ? 'up' : 'down');
    }
  }

  /* Update crypto cards */
  function updateCryptoCard() {
    ['BTC', 'ETH'].forEach(function(sym) {
      var el = document.getElementById('crypto-' + sym.toLowerCase());
      var data = cache[sym];
      if (!el || !data || data.price == null) return;
      var newV = '$' + Number(data.price).toLocaleString('en-US', { maximumFractionDigits: 0 });
      if (el.textContent !== newV) flashElement(el, data.change >= 0);
      el.textContent = newV;
    });
  }

  function updateUI() {
    updateHeroStats();
    updateSidebar();
    updateTicker();
    updateStocks();
    updateCompactIHSG();
    updateCryptoCard();
  }

  /* Fetch from local price data endpoint */
  function fetchAll() {
    fetch('/_price_data.json?_=' + Date.now())
      .then(function(resp) { return resp.json(); })
      .then(function(json) {
        if (json && json.data) {
          Object.keys(json.data).forEach(function(k) {
            var v = json.data[k];
            if (v && v.price != null) {
              cache[k] = v;
            }
          });
          updateUI();
          persistCache();
          lastFetch = Date.now();
        }
      })
      .catch(function() {})
      .then(function() {
        Object.keys(DEFAULTS).forEach(function(k) {
          if (!cache[k] || cache[k].price == null) cache[k] = DEFAULTS[k];
        });
        updateUI();
      });
  }

  /* Fetch crypto from CoinGecko (non-blocking) */
  function fetchCryptoAPI() {
    fetch(COINGECKO_API)
      .then(function(r) { return r.json(); })
      .then(function(d) {
        if (d && d.bitcoin && d.bitcoin.usd != null) {
          cache['BTC'] = {
            price: d.bitcoin.usd,
            change: d.bitcoin.usd_24h_change || (cache['BTC'] ? cache['BTC'].change : 0)
          };
        }
        if (d && d.ethereum && d.ethereum.usd != null) {
          cache['ETH'] = {
            price: d.ethereum.usd,
            change: d.ethereum.usd_24h_change || (cache['ETH'] ? cache['ETH'].change : 0)
          };
        }
        updateUI();
        persistCache();
      })
      .catch(function() {});
  }

  /* Apply embedded __INITIAL_DATA from page */
  function applyEmbeddedData() {
    if (!window.__INITIAL_DATA || !window.__INITIAL_DATA.prices) return false;
    var count = 0;
    Object.keys(window.__INITIAL_DATA.prices).forEach(function(k) {
      var v = window.__INITIAL_DATA.prices[k];
      if (v && v.price != null) {
        cache[k] = v;
        count++;
      }
    });
    if (count > 0) {
      updateUI();
      return true;
    }
    return false;
  }

  function init() {
    var hasEmbedded = applyEmbeddedData();
    if (!hasEmbedded) loadCacheFromStorage();

    /* Fill any missing symbols with defaults */
    Object.keys(DEFAULTS).forEach(function(k) {
      if (!cache[k] || cache[k].price == null) cache[k] = DEFAULTS[k];
    });
    updateUI();

    fetchCryptoAPI();
    fetchAll();

    setInterval(function() {
      fetchCryptoAPI();
      fetchAll();
    }, REFRESH_MS);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
