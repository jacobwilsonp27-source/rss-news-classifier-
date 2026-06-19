/**
 * api.js
 * ───────────────────────────────────────────────
 * Thin wrapper around the four combined-backend endpoints.
 * All functions return parsed JSON or throw on error.
 * ───────────────────────────────────────────────
 */

async function apiFetch(path) {
  const res = await fetch(API_BASE + path);
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json();
}

/** GET /news — all articles from all 11 modules, sorted newest first. */
async function fetchAllNews(limit = 200) {
  return apiFetch(`/news?limit=${limit}`);
}

/** GET /news/category/{apiLabel} — one category's articles. */
async function fetchCategoryNews(apiLabel, limit = 100) {
  return apiFetch(`/news/category/${encodeURIComponent(apiLabel)}?limit=${limit}`);
}

/**
 * GET /news/search?q=... — full-text across all 11 databases.
 * Works for multi-word queries like "brazil vs morocco".
 */
async function searchNews(query, limit = 100) {
  return apiFetch(`/news/search?q=${encodeURIComponent(query)}&limit=${limit}`);
}

/**
 * GET /news/{category}/{id} — single article.
 * Both params required because IDs are only unique within one module.
 */
async function fetchArticle(apiLabel, id) {
  return apiFetch(`/news/${encodeURIComponent(apiLabel)}/${encodeURIComponent(id)}`);
}
