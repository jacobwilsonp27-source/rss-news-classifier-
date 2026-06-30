/**
 * config.js
 * ─────────────────────────────────────────────
 * Single source of truth for API + category data.
 * Only this file needs updating when you deploy.
 * ─────────────────────────────────────────────
 */

// Change this to your server address when deploying.
const API_BASE = "https://your-backend.onrender.com";

// One entry per category. `apiLabel` must exactly match
// what the backend models write into the `category` column.
const CATEGORIES = [
  { key: "politics",      apiLabel: "Politics",             label: "Politics",           icon: "bi-bank",           color: "#2563EB" },
  { key: "business",      apiLabel: "Business and Economy", label: "Business & Economy", icon: "bi-graph-up-arrow", color: "#7C3AED" },
  { key: "technology",    apiLabel: "Technology",           label: "Technology",         icon: "bi-cpu",            color: "#0891B2" },
  { key: "science",       apiLabel: "Science",              label: "Science",            icon: "bi-flask",          color: "#4F46E5" },
  { key: "health",        apiLabel: "Health",               label: "Health",             icon: "bi-heart-pulse",    color: "#16A34A" },
  { key: "sports",        apiLabel: "Sports",               label: "Sports",             icon: "bi-trophy",         color: "#EA580C" },
  { key: "entertainment", apiLabel: "Entertainment",        label: "Entertainment",      icon: "bi-film",           color: "#DB2777" },
  { key: "lifestyle",     apiLabel: "Lifestyle",            label: "Lifestyle",          icon: "bi-flower1",        color: "#0D9488" },
  { key: "international", apiLabel: "International",        label: "International",      icon: "bi-globe2",         color: "#1E40AF" },
  { key: "education",     apiLabel: "Education",            label: "Education",          icon: "bi-mortarboard",    color: "#92400E" },
  { key: "weather",       apiLabel: "Weather",              label: "Weather",            icon: "bi-cloud-sun",      color: "#0284C7" },
];

/** Find category metadata by slug key (used in URLs). */
function getCategoryByKey(key) {
  return CATEGORIES.find(c => c.key === key) || null;
}

/** Find category metadata by the exact apiLabel string from backend JSON. */
function getCategoryByLabel(label) {
  return CATEGORIES.find(
    c => c.apiLabel.toLowerCase() === (label || "").toLowerCase()
  ) || null;
}
