/**
 * AIDE-OS Content Script
 * Extracts product data from Amazon.in and Flipkart.com product pages.
 * Injects a floating AIDE-OS badge and stores extracted data for the popup.
 */

(() => {
  "use strict";

  const PLATFORM = detectPlatform();

  function detectPlatform() {
    const host = window.location.hostname;
    if (host.includes("amazon.in")) return "amazon";
    if (host.includes("flipkart.com")) return "flipkart";
    return null;
  }

  // ── Amazon.in Extraction ──────────────────────────────────────────

  function extractAmazon() {
    const data = { platform: "amazon", url: window.location.href };

    // Title
    const titleEl =
      document.querySelector("#productTitle") ||
      document.querySelector("h1.a-size-large span") ||
      document.querySelector("#title span");
    data.title = titleEl?.textContent?.trim() || null;

    // Price — try multiple selectors for resilience
    const priceEl =
      document.querySelector("span.a-price span.a-offscreen") ||
      document.querySelector("#priceblock_ourprice") ||
      document.querySelector("#priceblock_dealprice") ||
      document.querySelector(".a-price-whole") ||
      document.querySelector("#price_inside_buybox");
    if (priceEl) {
      const raw = priceEl.textContent.trim();
      const match = raw.match(/[\d,]+/);
      data.price = match ? `₹${match[0]}` : raw;
    } else {
      data.price = null;
    }

    // Image
    const imgEl =
      document.querySelector("#landingImage") ||
      document.querySelector("#imgBlkFront") ||
      document.querySelector("#main-image") ||
      document.querySelector("img.a-dynamic-image");
    data.image =
      imgEl?.getAttribute("data-old-hires") ||
      imgEl?.getAttribute("data-dynamic-image") ||
      imgEl?.src ||
      null;

    // ASIN — extract from URL first, fall back to meta/data attributes
    const urlMatch = window.location.pathname.match(/\/dp\/([A-Z0-9]{10})/);
    if (urlMatch) {
      data.product_id = urlMatch[1];
    } else {
      const asinEl =
        document.querySelector("input[name='ASIN']") ||
        document.querySelector("#ASIN");
      data.product_id = asinEl?.value || asinEl?.textContent?.trim() || null;
    }

    return data;
  }

  // ── Flipkart Extraction ───────────────────────────────────────────

  function extractFlipkart() {
    const data = { platform: "flipkart", url: window.location.href };

    // Title
    const titleEl =
      document.querySelector("span.VU-ZEz") ||
      document.querySelector("span._6NESgj") ||
      document.querySelector("h1.B_NuCI");
    data.title = titleEl?.textContent?.trim() || null;

    // Price
    const priceEl =
      document.querySelector("div.Nx9bqj.CxhGGd") ||
      document.querySelector("div._30jeq3._16Jk6d") ||
      document.querySelector("div._30jeq3");
    if (priceEl) {
      const raw = priceEl.textContent.trim();
      data.price = raw.startsWith("₹") ? raw : `₹${raw}`;
    } else {
      data.price = null;
    }

    // Image
    const imgEl =
      document.querySelector("div._396cs4 img._2r_T1I") ||
      document.querySelector("img._2r_T1I") ||
      document.querySelector("div.YsxTmg img");
    data.image = imgEl?.src || null;

    // Flipkart product ID — from URL like /p/itme123456
    const urlMatch = window.location.pathname.match(/\/p\/(itm[a-zA-Z0-9]+)/i);
    data.product_id = urlMatch ? urlMatch[1] : null;

    return data;
  }

  // ── Store data & inject badge ─────────────────────────────────────

  function storeAndNotify(data) {
    if (!data.title && !data.price) return; // not a product page

    chrome.storage.local.set({ currentProduct: data });

    // Notify background script
    chrome.runtime.sendMessage({ type: "PRODUCT_EXTRACTED", data });
  }

  function injectBadge() {
    if (document.getElementById("aide-os-badge")) return;

    const badge = document.createElement("div");
    badge.id = "aide-os-badge";
    badge.innerHTML = `
      <div id="aide-os-badge-inner">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"/>
          <path d="M2 17l10 5 10-5"/>
          <path d="M2 12l10 5 10-5"/>
        </svg>
        <span>AIDE-OS</span>
      </div>
    `;

    const style = document.createElement("style");
    style.textContent = `
      #aide-os-badge {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 2147483647;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      }
      #aide-os-badge-inner {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 14px;
        background: #0f1117;
        color: #c4c7d4;
        border: 1px solid #1e2130;
        border-radius: 10px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        cursor: pointer;
        box-shadow: 0 4px 16px rgba(0,0,0,0.35);
        transition: all 0.2s ease;
      }
      #aide-os-badge-inner:hover {
        background: #161926;
        border-color: #6366f1;
        color: #ffffff;
        box-shadow: 0 4px 20px rgba(99,102,241,0.25);
      }
      #aide-os-badge-inner svg {
        flex-shrink: 0;
        opacity: 0.7;
      }
      #aide-os-badge-inner:hover svg {
        opacity: 1;
        stroke: #6366f1;
      }
    `;

    document.head.appendChild(style);
    document.body.appendChild(badge);

    badge.addEventListener("click", () => {
      chrome.runtime.sendMessage({ type: "OPEN_POPUP" });
    });
  }

  // ── Main ──────────────────────────────────────────────────────────

  function main() {
    if (!PLATFORM) return;

    let data;
    if (PLATFORM === "amazon") {
      data = extractAmazon();
    } else if (PLATFORM === "flipkart") {
      data = extractFlipkart();
    }

    if (data) {
      storeAndNotify(data);
      injectBadge();
    }

    // Re-extract on SPA navigation (Amazon sometimes loads dynamically)
    const observer = new MutationObserver(() => {
      const newData =
        PLATFORM === "amazon" ? extractAmazon() : extractFlipkart();
      if (newData && newData.title) {
        storeAndNotify(newData);
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", main);
  } else {
    main();
  }
})();
