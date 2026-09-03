/**
 * AIDE-OS Popup Script
 * Displays product info and provides chipflation analysis + watchlist actions.
 */

(() => {
  "use strict";

  // ── DOM refs ───────────────────────────────────────────────────

  const $ = (sel) => document.querySelector(sel);

  const productSection = $("#product-section");
  const emptyState = $("#empty-state");
  const actions = $("#actions");
  const resultSection = $("#result-section");
  const statusEl = $("#status");
  const loadingEl = $("#loading");

  const productImage = $("#product-image");
  const productTitle = $("#product-title");
  const productPrice = $("#product-price");
  const productId = $("#product-id");
  const productPlatform = $("#product-platform");

  const resultScore = $("#result-score");
  const resultBar = $("#result-bar");
  const resultSummary = $("#result-summary");
  const metricRisk = $("#metric-risk");
  const metricTrend = $("#metric-trend");
  const metricSignal = $("#metric-signal");

  const btnChipflation = $("#btn-chipflation");
  const btnWatchlist = $("#btn-watchlist");

  // ── State ──────────────────────────────────────────────────────

  let currentProduct = null;
  let apiBaseUrl = "http://localhost:8000";

  // ── Init ───────────────────────────────────────────────────────

  async function init() {
    // Load API URL from storage
    const { apiUrl } = await chrome.storage.local.get("apiUrl");
    if (apiUrl) apiBaseUrl = apiUrl;

    // Get current product from content script
    const { currentProduct: product } = await chrome.storage.local.get("currentProduct");

    if (product && product.title) {
      currentProduct = product;
      showProduct(product);
      checkWatchlistStatus(product);
    } else {
      // Ask content script to re-extract
      try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab?.id) {
          chrome.tabs.sendMessage(tab.id, { type: "REQUEST_PRODUCT" });
        }
      } catch (_) {
        // Content script might not be loaded on this page
      }
    }

    // Listen for messages from content script / background
    chrome.runtime.onMessage.addListener((msg) => {
      if (msg.type === "PRODUCT_EXTRACTED" && msg.data?.title) {
        currentProduct = msg.data;
        showProduct(msg.data);
        checkWatchlistStatus(msg.data);
      }
      if (msg.type === "API_URL_UPDATED" && msg.url) {
        apiBaseUrl = msg.url;
      }
    });

    // Button handlers
    btnChipflation.addEventListener("click", handleChipflation);
    btnWatchlist.addEventListener("click", handleWatchlist);
  }

  // ── UI Updates ─────────────────────────────────────────────────

  function showProduct(data) {
    emptyState.classList.add("hidden");
    productSection.classList.remove("hidden");
    actions.classList.remove("hidden");

    productTitle.textContent = data.title;
    productPrice.textContent = data.price || "Price unavailable";

    if (data.image) {
      productImage.src = data.image;
      productImage.alt = data.title;
    } else {
      productImage.style.display = "none";
    }

    if (data.product_id) {
      const idPrefix = data.platform === "amazon" ? "ASIN" : "FK ID";
      productId.textContent = `${idPrefix}: ${data.product_id}`;
    } else {
      productId.textContent = "";
    }

    // Platform badge
    productPlatform.textContent = data.platform;
    productPlatform.className = `platform-badge ${data.platform}`;
  }

  function showStatus(message, type = "success") {
    statusEl.textContent = message;
    statusEl.className = `status ${type}`;
    statusEl.classList.remove("hidden");
    setTimeout(() => statusEl.classList.add("hidden"), 4000);
  }

  function showLoading(show) {
    loadingEl.classList.toggle("hidden", !show);
    btnChipflation.disabled = show;
  }

  function showResult(data) {
    resultSection.classList.remove("hidden");

    const score = data.decision_index ?? data.score ?? 0;
    const riskLevel = data.risk_level ?? data.risk ?? "Unknown";
    const trend = data.price_trend ?? data.trend ?? "N/A";
    const signal = data.market_signal ?? data.signal ?? "N/A";
    const summary = data.summary ?? data.analysis ?? "";

    // Score color
    let scoreColor = "#34d399"; // green (low risk)
    if (score > 70) scoreColor = "#f87171"; // red
    else if (score > 40) scoreColor = "#fbbf24"; // yellow

    resultScore.textContent = typeof score === "number" ? score.toFixed(1) : score;
    resultScore.style.color = scoreColor;

    // Bar
    const pct = typeof score === "number" ? Math.min(score, 100) : 50;
    resultBar.style.width = `${pct}%`;
    resultBar.style.background = scoreColor;

    metricRisk.textContent = riskLevel;
    metricRisk.style.color = scoreColor;
    metricTrend.textContent = trend;
    metricSignal.textContent = signal;
    resultSummary.textContent = summary || "No additional analysis available.";
  }

  // ── Watchlist ──────────────────────────────────────────────────

  async function checkWatchlistStatus(product) {
    const { watchlist = [] } = await chrome.storage.local.get("watchlist");
    const key = `${product.platform}:${product.product_id}`;
    const inList = watchlist.some((w) => `${w.platform}:${w.product_id}` === key);

    if (inList) {
      btnWatchlist.classList.add("in-watchlist");
      btnWatchlist.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2">
          <path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/>
        </svg>
        In Watchlist
      `;
    } else {
      btnWatchlist.classList.remove("in-watchlist");
      btnWatchlist.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/>
        </svg>
        Add to Watchlist
      `;
    }
  }

  // ── Event Handlers ─────────────────────────────────────────────

  async function handleChipflation() {
    if (!currentProduct) {
      showStatus("No product data available.", "error");
      return;
    }

    showLoading(true);
    resultSection.classList.add("hidden");

    try {
      const response = await chrome.runtime.sendMessage({
        type: "CHECK_CHIPFLATION",
        data: currentProduct,
      });

      if (response?.error) {
        showStatus(response.error, "error");
      } else if (response?.data) {
        showResult(response.data);
        showStatus("Analysis complete", "success");
      }
    } catch (err) {
      showStatus(`Error: ${err.message}`, "error");
    } finally {
      showLoading(false);
    }
  }

  async function handleWatchlist() {
    if (!currentProduct) {
      showStatus("No product data available.", "error");
      return;
    }

    try {
      const response = await chrome.runtime.sendMessage({
        type: "TOGGLE_WATCHLIST",
        data: currentProduct,
      });

      if (response?.added) {
        showStatus("Added to watchlist", "success");
      } else if (response?.removed) {
        showStatus("Removed from watchlist", "success");
      }

      checkWatchlistStatus(currentProduct);
    } catch (err) {
      showStatus(`Error: ${err.message}`, "error");
    }
  }

  // ── Boot ───────────────────────────────────────────────────────

  init();
})();
