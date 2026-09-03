# AIDE-OS Chrome Extension

AI Decision Engine for Indian e-commerce — real-time chipflation risk analysis on **Amazon.in** and **Flipkart.com** product pages.

## Features

- **Auto-extract** product title, price, image, and ID (ASIN / Flipkart ID) from product pages
- **Chipflation Risk Analysis** — sends product data to the AIDE-OS backend and displays a Decision Index score with risk level, price trend, and market signal
- **Watchlist** — save products to a local watchlist for periodic re-analysis
- **Floating Badge** — AIDE-OS badge on product pages for quick access
- **Dark Theme** — matches the AIDE-OS design system (#0f1117 background, #6366f1 indigo primary)

## Prerequisites

- AIDE-OS backend running at `http://localhost:8000` (or your configured URL)
- Google Chrome 88+ (Manifest V3 support)
- Developer mode enabled in Chrome Extensions

## Loading the Extension

1. **Open Chrome Extensions page**
   - Navigate to `chrome://extensions/`
   - Or click the three-dot menu → More tools → Extensions

2. **Enable Developer Mode**
   - Toggle the "Developer mode" switch in the top-right corner

3. **Load unpacked extension**
   - Click "Load unpacked" in the top-left
   - Navigate to the `extension/` folder in this project
   - Select the folder and click "Select Folder"

4. **Pin the extension** (optional but recommended)
   - Click the puzzle-piece icon in the Chrome toolbar
   - Find "AIDE-OS" and click the pin icon

## Usage

1. Navigate to a product page on **Amazon.in** or **Flipkart.com**
2. The AIDE-OS badge appears in the bottom-right corner of the page
3. Click the AIDE-OS icon in the toolbar (or the badge) to open the popup
4. The popup displays the extracted product info
5. Click **"Check Chipflation Risk"** to analyze the product
6. Click **"Add to Watchlist"** to save the product for periodic monitoring

## Configuration

The backend API URL defaults to `http://localhost:8000`. To change it:

```javascript
// In the Chrome DevTools console for the extension:
chrome.storage.local.set({ apiUrl: "http://your-server:8000" });
```

Or use the background service worker message:

```javascript
chrome.runtime.sendMessage({ type: "UPDATE_API_URL", data: { url: "http://your-server:8000" } });
```

## API Endpoint

The extension calls:

```
POST /api/v1/chipflation-index
```

With body:

```json
{
  "product_id": "B09V3KXJPB",
  "platform": "amazon",
  "title": "Product Name",
  "price": "₹1,999",
  "url": "https://www.amazon.in/dp/..."
}
```

Expected response:

```json
{
  "decision_index": 67.5,
  "risk_level": "Moderate",
  "price_trend": "Rising",
  "market_signal": "Bullish",
  "summary": "Product shows moderate chipflation risk..."
}
```

## File Structure

```
extension/
├── manifest.json      # Manifest V3 config
├── background.js      # Service worker (API calls, watchlist)
├── content.js         # Content script (DOM extraction, badge)
├── popup.html         # Extension popup UI
├── popup.js           # Popup logic
├── popup.css          # Dark theme styles
├── icons/             # Extension icons (16, 48, 128px)
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md          # This file
```

## Notes

- Icons in `icons/` are not included by default — add your own PNG icons at the specified sizes or remove the icon entries from `manifest.json`
- The extension uses `chrome.storage.local` for all data persistence (no external storage)
- Watchlist items are re-analyzed every 30 minutes when the browser is running
- The content script auto-detects DOM changes on SPA-style pages (Amazon loads some content dynamically)
