/**
 * app.js
 * ─────────────────────────────────────────────────────
 * Rendering components + page routing in one file.
 * Every page sets <body data-page="home|category|search|article">
 * so the router at the bottom can call the right init function.
 * ─────────────────────────────────────────────────────
 */

// ──────────────────────────────────────────────────────
//  Utilities
// ──────────────────────────────────────────────────────

function esc(str) {
  return String(str || "").replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
  );
}

function formatDate(str) {
  const d = new Date(str);
  if (isNaN(d)) return str || "";
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

/** Resolve category metadata from an article (using _categoryKey tag or category label). */
function catMeta(article) {
  return (
    (article._catKey && getCategoryByKey(article._catKey)) ||
    getCategoryByLabel(article.category) ||
    { key: "news", apiLabel: article.category || "News", label: article.category || "News",
      icon: "bi-newspaper", color: "#6B7280" }
  );
}

/** Deterministic placeholder image seeded by category + article id. */


function articleUrl(article) {
  const m = catMeta(article);
  return `article.html?cat=${m.key}&id=${article.id}`;
}

// ──────────────────────────────────────────────────────
//  Badge components
// ──────────────────────────────────────────────────────

function categoryBadge(article) {
  const m = catMeta(article);
  return `<a class="badge-cat" style="--c:${m.color}" href="category.html?cat=${m.key}">
    <i class="bi ${m.icon}"></i>${esc(m.label)}
  </a>`;
}

const SENTIMENT = {
  positive: { cls: "sent-pos", icon: "bi-arrow-up-circle-fill", label: "Positive" },
  negative: { cls: "sent-neg", icon: "bi-arrow-down-circle-fill", label: "Negative" },
  neutral:  { cls: "sent-neu", icon: "bi-dash-circle-fill",      label: "Neutral"  },
};

function sentimentBadge(article) {
  const s = SENTIMENT[(article.sentiment || "").toLowerCase()] || SENTIMENT.neutral;
  return `<span class="badge-sent ${s.cls}"><i class="bi ${s.icon}"></i>${s.label}</span>`;
}

// ──────────────────────────────────────────────────────
//  Confidence ring (signature AI-data element on article page)
// ──────────────────────────────────────────────────────

function confidenceRing(value, label) {
  const pct = Math.round((value || 0) * 100);
  const r = 20, cx = 24, size = 48, sw = 4;
  const circ = 2 * Math.PI * r;
  const dash = circ * (pct / 100);
  return `<div class="conf-ring-wrap">
    <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <circle cx="${cx}" cy="${cx}" r="${r}" class="ring-track" stroke-width="${sw}" fill="none"/>
      <circle cx="${cx}" cy="${cx}" r="${r}" class="ring-val" stroke-width="${sw}" fill="none"
        stroke-dasharray="${dash.toFixed(1)} ${circ.toFixed(1)}"
        transform="rotate(-90 ${cx} ${cx})"/>
    </svg>
    <span class="ring-pct">${pct}<small>%</small></span>
    <span class="ring-label">${esc(label)}</span>
  </div>`;
}

// ──────────────────────────────────────────────────────
//  News card (used in grids)
// ──────────────────────────────────────────────────────

function renderCard(article) {
  const imageUrl =
    article.image_url ||
    article.image ||
    article.thumbnail ||
    `https://picsum.photos/seed/${article.id}/600/400`;

  return `
    <a class="news-card" href="${articleUrl(article)}">
      <img
        class="card-img"
        src="${imageUrl}"
        alt="${esc(article.title)}"
        loading="lazy"
        onerror="this.src='https://picsum.photos/600/400'"
      />

      <div class="card-content">
        <div class="badge-row">
          ${categoryBadge(article)}
          ${sentimentBadge(article)}
        </div>

        <h3 class="card-title">${esc(article.title)}</h3>
        <p class="card-desc">${esc(article.description || "")}</p>

        <div class="card-foot">
          <span class="card-source">${esc(article.source || "")}</span>
          <span class="card-date">${formatDate(article.published_date)}</span>
        </div>
      </div>
    </a>
  `;
}

// ──────────────────────────────────────────────────────
//  Hero (featured article, full-width)
// ──────────────────────────────────────────────────────

function renderHero(article) {
  if (!article) return "";
  return `<a class="hero" href="${articleUrl(article)}">
  <img
  class="hero-img"
  src="https://picsum.photos/1200/500"
  alt="News Image"
/>
    <div class="hero-body">
      <span class="hero-eyebrow">Featured Story</span>
      <div class="badge-row">${categoryBadge(article)}${sentimentBadge(article)}</div>
      <h2 class="hero-title">${esc(article.title)}</h2>
      <p class="hero-desc">${esc(article.description || "")}</p>
      <div class="hero-meta">
        <span>${esc(article.source || "")}</span>
        <span class="sep">·</span>
        <span>${formatDate(article.published_date)}</span>
      </div>
    </div>
  </a>`;
}

// ──────────────────────────────────────────────────────
//  Compact row item (used in category-preview rows on home)
// ──────────────────────────────────────────────────────

function renderRowItem(article) {
  const imageUrl =
    article.image_url ||
    article.image ||
    article.thumbnail ||
    `https://picsum.photos/seed/row${article.id}/300/200`;

  return `
    <a class="row-item" href="${articleUrl(article)}">
      <img
        class="row-item-img"
        src="${imageUrl}"
        alt="${esc(article.title)}"
        loading="lazy"
        onerror="this.src='https://picsum.photos/300/200'"
      />

      <div class="row-item-body">
        <h4 class="row-item-title">${esc(article.title)}</h4>

        <div class="row-item-foot">
          ${sentimentBadge(article)}
          <span class="card-date">
            ${formatDate(article.published_date)}
          </span>
        </div>
      </div>
    </a>
  `;
}

// ──────────────────────────────────────────────────────
//  Pagination
// ──────────────────────────────────────────────────────

function renderPagination(current, total) {
  if (total <= 1) return "";
  let html = `<nav class="pagination">
    <button class="pg-btn" data-page="${current - 1}" ${current === 1 ? "disabled" : ""}>
      <i class="bi bi-chevron-left"></i>
    </button>`;
  for (let p = 1; p <= total; p++) {
    html += `<button class="pg-btn ${p === current ? "active" : ""}" data-page="${p}">${p}</button>`;
  }
  html += `<button class="pg-btn" data-page="${current + 1}" ${current === total ? "disabled" : ""}>
      <i class="bi bi-chevron-right"></i>
    </button></nav>`;
  return html;
}

// ──────────────────────────────────────────────────────
//  State helpers
// ──────────────────────────────────────────────────────

function renderLoading(msg) {
  return `<div class="state-box"><div class="spinner"></div><p>${esc(msg || "Loading…")}</p></div>`;
}

function renderEmpty(icon, title, msg) {
  return `<div class="state-box">
    <i class="bi ${icon || "bi-inbox"} state-icon"></i>
    <h3>${esc(title || "Nothing here yet")}</h3>
    <p>${esc(msg || "")}</p>
  </div>`;
}

function renderError(msg) {
  return `<div class="state-box error-state">
    <i class="bi bi-exclamation-circle state-icon"></i>
    <h3>Something went wrong</h3>
    <p>${esc(msg || "Check that the backend is running on port 8000.")}</p>
  </div>`;
}

// ──────────────────────────────────────────────────────
//  Shell: sidebar links, hamburger, active nav
// ──────────────────────────────────────────────────────

function initShell() {
  // Inject category links
  const linksEl = document.getElementById("categoryLinks");
  if (linksEl) {
    linksEl.innerHTML = CATEGORIES.map(c =>
      `<a class="nav-link" data-cat="${c.key}" href="category.html?cat=${c.key}">
        <i class="bi ${c.icon}" style="color:${c.color}"></i>
        <span>${esc(c.label)}</span>
      </a>`
    ).join("");
  }

  // Hamburger drawer (mobile)
  const hamburger = document.getElementById("hamburger");
  const sidebar   = document.getElementById("sidebar");
  const overlay   = document.getElementById("overlay");
  if (hamburger && sidebar && overlay) {
    const openSidebar  = () => { sidebar.classList.add("open"); overlay.classList.add("show"); };
    const closeSidebar = () => { sidebar.classList.remove("open"); overlay.classList.remove("show"); };
    hamburger.addEventListener("click", openSidebar);
    overlay.addEventListener("click", closeSidebar);
    sidebar.querySelectorAll(".nav-link").forEach(a =>
      a.addEventListener("click", closeSidebar)
    );
  }

  // Mark active link
  const params  = new URLSearchParams(location.search);
  const page    = document.body.dataset.page;
  const catKey  = params.get("cat");

  document.querySelectorAll(".nav-link[data-page-link]").forEach(a => {
    a.classList.toggle("active", a.dataset.pageLink === page);
  });
  if (catKey) {
    document.querySelectorAll(".nav-link[data-cat]").forEach(a => {
      a.classList.toggle("active", a.dataset.cat === catKey);
    });
  }
}

// ──────────────────────────────────────────────────────
//  HOME PAGE
// ──────────────────────────────────────────────────────

async function initHome() {
  const heroSlot   = document.getElementById("heroSlot");
  const latestSlot = document.getElementById("latestSlot");
  const rowsSlot   = document.getElementById("categoryRowsSlot");

  heroSlot.innerHTML   = renderLoading("Fetching latest stories…");
  latestSlot.innerHTML = "";

  let articles;
  try {
    articles = await fetchAllNews();
  } catch (e) {
    heroSlot.innerHTML = renderError(e.message);
    return;
  }

  if (!articles.length) {
    heroSlot.innerHTML = renderEmpty("bi-newspaper", "No articles yet", "Run the backend and let the modules fetch some news.");
    return;
  }

  // Tag each article with its category key for proper badge colors
  articles.forEach(a => {
    const m = getCategoryByLabel(a.category);
    if (m) a._catKey = m.key;
  });

  heroSlot.innerHTML   = renderHero(articles[0]);
  latestSlot.innerHTML = articles.slice(1, 10).map(renderCard).join("");

  // Per-category preview rows
  const byCategory = {};
  CATEGORIES.forEach(c => { byCategory[c.key] = []; });
  articles.forEach(a => {
    const m = getCategoryByLabel(a.category);
    if (m && byCategory[m.key]) byCategory[m.key].push(a);
  });

  rowsSlot.innerHTML = CATEGORIES.map(c => {
    const items = byCategory[c.key].slice(0, 3);
    if (!items.length) return "";
    return `<section class="cat-row">
      <div class="cat-row-header">
        <span class="cat-row-title">
          <i class="bi ${c.icon}" style="color:${c.color}"></i>${esc(c.label)}
        </span>
        <a href="category.html?cat=${c.key}" class="view-all-link">
          View all <i class="bi bi-arrow-right"></i>
        </a>
      </div>
      <div class="row-items">${items.map(renderRowItem).join("")}</div>
    </section>`;
  }).join("");
}

// ──────────────────────────────────────────────────────
//  CATEGORY PAGE
// ──────────────────────────────────────────────────────

async function initCategory() {
  const params = new URLSearchParams(location.search);
  const key    = params.get("cat");
  const meta   = getCategoryByKey(key);

  const titleEl  = document.getElementById("catTitle");
  const iconEl   = document.getElementById("catIcon");
  const gridEl   = document.getElementById("catGrid");
  const pagerEl  = document.getElementById("catPager");
  const filterEl = document.getElementById("sentimentFilter");

  if (!meta) {
    gridEl.innerHTML = renderEmpty("bi-question-circle", "Unknown category", "Select one from the sidebar.");
    return;
  }

  document.title        = `${meta.label} · News`;
  titleEl.textContent   = meta.label;
  iconEl.className      = `bi ${meta.icon}`;
  iconEl.style.color    = meta.color;

  gridEl.innerHTML = renderLoading(`Loading ${meta.label} news…`);

  let articles;
  try {
    articles = await fetchCategoryNews(meta.apiLabel);
  } catch (e) {
    gridEl.innerHTML = renderError(e.message);
    return;
  }

  articles.forEach(a => { a._catKey = meta.key; });

  const PAGE_SIZE    = 9;
  let currentPage    = 1;
  let activeSentiment = "all";

  function renderPage() {
    const filtered = activeSentiment === "all"
      ? articles
      : articles.filter(a => (a.sentiment || "").toLowerCase() === activeSentiment);

    const total = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
    currentPage = Math.min(currentPage, total);
    const slice = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

    gridEl.innerHTML = slice.length
      ? slice.map(renderCard).join("")
      : renderEmpty("bi-filter-circle", "No results", "Try a different sentiment filter.");

    pagerEl.innerHTML = renderPagination(currentPage, total);
  }

  renderPage();

  // Sentiment filter
  filterEl.addEventListener("click", e => {
    const btn = e.target.closest("[data-sent]");
    if (!btn) return;
    activeSentiment = btn.dataset.sent;
    currentPage     = 1;
    filterEl.querySelectorAll("[data-sent]").forEach(b =>
      b.classList.toggle("active", b === btn)
    );
    renderPage();
  });

  // Pagination
  pagerEl.addEventListener("click", e => {
    const btn = e.target.closest("[data-page]");
    if (!btn || btn.disabled) return;
    currentPage = Number(btn.dataset.page);
    renderPage();
    gridEl.scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

// ──────────────────────────────────────────────────────
//  SEARCH PAGE
// ──────────────────────────────────────────────────────

async function initSearch() {
  const input    = document.getElementById("searchInput");
  const resultsEl= document.getElementById("searchResults");
  const countEl  = document.getElementById("resultCount");

  // Focus the input immediately
  input.focus();

  // Pre-fill from URL ?q=...
  const params = new URLSearchParams(location.search);
  const q0     = params.get("q");
  if (q0) { input.value = q0; runSearch(q0); }

  let debounceTimer;
  input.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    const q = input.value.trim();
    if (!q) {
      countEl.textContent = "";
      resultsEl.innerHTML = renderEmpty("bi-search", "Search anything", "Type a topic, team name, keyword, or person.");
      return;
    }
    resultsEl.innerHTML = renderLoading("Searching all categories…");
    debounceTimer = setTimeout(() => runSearch(q), 350);
  });

  async function runSearch(q) {
    try {
      const results = await searchNews(q);
      results.forEach(a => {
        const m = getCategoryByLabel(a.category);
        if (m) a._catKey = m.key;
      });
      countEl.textContent = results.length
        ? `${results.length} result${results.length === 1 ? "" : "s"}`
        : "";
      resultsEl.innerHTML = results.length
        ? results.map(renderCard).join("")
        : renderEmpty("bi-emoji-frown", "No results", `Nothing found for "${q}". Try different keywords.`);
    } catch (e) {
      resultsEl.innerHTML = renderError(e.message);
    }
  }
}

// ──────────────────────────────────────────────────────
//  ARTICLE PAGE
// ──────────────────────────────────────────────────────

async function initArticle() {
  const params  = new URLSearchParams(location.search);
  const catKey  = params.get("cat");
  const id      = params.get("id");
  const wrapEl  = document.getElementById("articleWrap");

  const meta = getCategoryByKey(catKey);
  if (!meta || !id) {
    wrapEl.innerHTML = renderEmpty("bi-exclamation-triangle", "Article not found", "The link is missing required details.");
    return;
  }

  wrapEl.innerHTML = renderLoading("Loading article…");

  let article;
  try {
    article = await fetchArticle(meta.apiLabel, id);
  } catch (e) {
    wrapEl.innerHTML = renderError(e.message);
    return;
  }

  article._catKey = meta.key;
  document.title  = `${article.title} · News`;

  wrapEl.innerHTML = `
    
    <div class="article-body">
      <div class="badge-row">${categoryBadge(article)}${sentimentBadge(article)}</div>
      <h1 class="article-title">${esc(article.title)}</h1>
      <div class="article-meta">
        <span class="article-source">${esc(article.source || "")}</span>
        <span class="sep">·</span>
        <span>${formatDate(article.published_date)}</span>
      </div>
      <div class="ai-confidence">
        ${confidenceRing(article.category_confidence, "Category confidence")}
        ${confidenceRing(article.sentiment_confidence, "Sentiment confidence")}
      </div>
      <div class="article-text">
        <p>${esc(article.content || article.description || "No content available.")}</p>
      </div>
      ${article.url ? `<a class="read-original-btn" href="${esc(article.url)}" target="_blank" rel="noopener">
        Read original source <i class="bi bi-box-arrow-up-right"></i>
      </a>` : ""}
    </div>
    <div id="moreSlot"></div>
  `;

  // Load "more from this category" section
  try {
    const more = (await fetchCategoryNews(meta.apiLabel))
      .filter(a => String(a.id) !== String(id))
      .slice(0, 3);
    if (more.length) {
      more.forEach(a => { a._catKey = meta.key; });
      document.getElementById("moreSlot").innerHTML = `
        <section class="cat-row more-section">
          <div class="cat-row-header">
            <span class="cat-row-title">
              <i class="bi ${meta.icon}" style="color:${meta.color}"></i>More from ${esc(meta.label)}
            </span>
          </div>
          <div class="news-grid">${more.map(renderCard).join("")}</div>
        </section>`;
    }
  } catch (_) { /* silently skip if extra fetch fails */ }
}

// ──────────────────────────────────────────────────────
//  Router
// ──────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  initShell();
  const page = document.body.dataset.page;
  if      (page === "home")     initHome();
  else if (page === "category") initCategory();
  else if (page === "search")   initSearch();
  else if (page === "article")  initArticle();
});
