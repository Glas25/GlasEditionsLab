import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

// =============================================================================
// Suppress Chrome extension errors (frame_ant, etc.)
// These extensions intercept fetch responses and cause "Response body already used" errors
// =============================================================================

// Helper to check if error is from Chrome extension
const isExtensionError = (str) => {
  if (!str) return false;
  const s = String(str).toLowerCase();
  return (
    s.includes('chrome-extension://') ||
    s.includes('response body is already used') ||
    s.includes('frame_ant') ||
    s.includes('hoklmmgfnpapgjgcpechhaamimifchmp')
  );
};

// Override console.error to suppress extension errors
const originalConsoleError = console.error;
console.error = (...args) => {
  const errorString = args.map(a => String(a)).join(' ');
  if (isExtensionError(errorString)) {
    return; // Silently ignore
  }
  originalConsoleError.apply(console, args);
};

// Global error handler
window.addEventListener('error', (event) => {
  if (isExtensionError(event.filename) || isExtensionError(event.message)) {
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();
    return false;
  }
}, true);

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
  const reason = event.reason?.message || event.reason?.toString() || '';
  if (isExtensionError(reason)) {
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();
    return false;
  }
}, true);

// Remove React error overlay for extension errors (development mode)
// This runs after the DOM is loaded to hide the overlay if it appears
if (process.env.NODE_ENV === 'development' || true) {
  const hideErrorOverlay = () => {
    // Try to find and remove React error overlay
    const overlays = document.querySelectorAll('iframe[style*="position: fixed"]');
    overlays.forEach(overlay => {
      if (overlay.style.zIndex > 1000) {
        const iframeDoc = overlay.contentDocument || overlay.contentWindow?.document;
        if (iframeDoc) {
          const text = iframeDoc.body?.innerText || '';
          if (isExtensionError(text)) {
            overlay.remove();
          }
        }
      }
    });
    
    // Also check for error overlay div
    const errorOverlays = document.querySelectorAll('[class*="error-overlay"], [id*="error-overlay"]');
    errorOverlays.forEach(overlay => {
      const text = overlay.innerText || '';
      if (isExtensionError(text)) {
        overlay.remove();
      }
    });
  };

  // Run periodically to catch any overlays that appear
  setInterval(hideErrorOverlay, 100);
  
  // Also run on DOM changes
  const observer = new MutationObserver(hideErrorOverlay);
  observer.observe(document.documentElement, { childList: true, subtree: true });
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
