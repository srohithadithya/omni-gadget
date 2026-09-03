/**
 * AIDE-OS Background Service Worker
 * Manages watchlist, communicates with content script & popup,
 * and fetches chipflation data from the AIDE-OS backend API.
 */

const DEFAULT_API_URL = "http://localhost:8000";

// ── Helpers ────────────────────────────────────────────────────

async function getApiUrl() {
  const { apiUrl } = await chrome.storage.local.get("apiUrl");
  return apiUrl || DEFAULT_API_URL;
}

// ── Message Router ─────────────────────────────────────────────

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  const { type, data } = message;

  switch (type) {
    case "PRODUCT_EXTRACTED":
      // Content script extracted product data — store it
      handleProductExtracted(data);
      break;

    case "CHECK_CHIPFLATION":
      handleChipflation(data).then(sendResponse);
      return true; // keep message channel open for async response

    case "TOGGLE_WATCHLIST":
      handleToggleWatchlist(data).then(sendResponse);
      return true;

    case "GET_WATCHLIST":
      handleGetWatchlist().then(sendResponse);
      return true;

    case "OPEN_POPUP":
      // Badge clicked — we can't programmatically open the popup,
      // but we can ensure the action icon is highlighted
      if (_sender.tab?.id) {
        chrome.action.openPopup({ windowId: _sender.tab.windowId }).catch(() => {});
      }
      break;

    case "UPDATE_API_URL":
      chrome.storage.local.set({ apiUrl: data.url });
      break;

    default:
      break;
  }
});

// ── Product Extraction Handler ─────────────────────────────────

async function handleProductExtracted(data) {
  if (!data || !data.title) return;

  // Store the latest extracted product
  await chrome.storage.local.set({ currentProduct: data });

  // Update badge text with platform indicator
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab?.id) {
      const badgeText = data.platform === "amazon" ? "AMZ" : "FKP";
      chrome.action.setBadgeText({ text: badgeText, tabId: tab.id });
      chrome.action.setBadgeBackgroundColor({ color: "#6366f1", tabId: tab.id });
    }
  } catch (_) {
    // Tab context might be unavailable
  }
}

// ── Chipflation API ────────────────────────────────────────────

async function handleChipflation(productData) {
  const baseUrl = await getApiUrl();

  try {
    const response = await fetch(`${baseUrl}/api/v1/chipflation-index`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        product_id: productData.product_id,
        platform: productData.platform,
        title: productData.title,
        price: productData.price,
        url: productData.url,
      }),
    });

    if (!response.ok) {
      const text = await response.text();
      return { error: `API error ${response.status}: ${text}` };
    }

    const result = await response.json();
    return { data: result };
  } catch (err) {
    return {
      error: `Connection failed — is the AIDE-OS backend running at ${baseUrl}? (${err.message})`,
    };
  }
}

// ── Watchlist Management ───────────────────────────────────────

async function handleToggleWatchlist(productData) {
  const { watchlist = [] } = await chrome.storage.local.get("watchlist");
  const key = `${productData.platform}:${productData.product_id}`;
  const idx = watchlist.findIndex((w) => `${w.platform}:${w.product_id}` === key);

  if (idx >= 0) {
    watchlist.splice(idx, 1);
    await chrome.storage.local.set({ watchlist });
    return { removed: true, watchlist };
  } else {
    watchlist.push({
      ...productData,
      addedAt: Date.now(),
    });
    await chrome.storage.local.set({ watchlist });
    return { added: true, watchlist };
  }
}

async function handleGetWatchlist() {
  const { watchlist = [] } = await chrome.storage.local.get("watchlist");
  return { watchlist };
}

// ── Periodic Watchlist Check (every 30 minutes) ───────────────

chrome.alarms.create("watchlist-check", { periodInMinutes: 30 });

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name !== "watchlist-check") return;

  const { watchlist = [] } = await chrome.storage.local.get("watchlist");
  if (watchlist.length === 0) return;

  const baseUrl = await getApiUrl();

  for (const item of watchlist) {
    try {
      const response = await fetch(`${baseUrl}/api/v1/chipflation-index`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: item.product_id,
          platform: item.platform,
          title: item.title,
          price: item.price,
          url: item.url,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        // Store the latest analysis with the watchlist item
        item.lastAnalysis = result;
        item.lastChecked = Date.now();
      }
    } catch (_) {
      // Skip failed checks silently
    }
  }

  await chrome.storage.local.set({ watchlist });
});

// ── Settings API ───────────────────────────────────────────────

// Allow the user to configure the API URL via storage
chrome.runtime.onInstalled.addListener(async () => {
  const { apiUrl } = await chrome.storage.local.get("apiUrl");
  if (!apiUrl) {
    await chrome.storage.local.set({ apiUrl: DEFAULT_API_URL });
  }
});
