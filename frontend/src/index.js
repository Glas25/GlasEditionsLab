import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

// Suppress errors from Chrome extensions (like frame_ant)
// These are not actual app errors and shouldn't show the error overlay
const originalConsoleError = console.error;
console.error = (...args) => {
  const errorString = args.join(' ');
  // Suppress Chrome extension errors
  if (
    errorString.includes('chrome-extension://') ||
    errorString.includes('Response body is already used') ||
    errorString.includes('frame_ant')
  ) {
    return; // Silently ignore extension errors
  }
  originalConsoleError.apply(console, args);
};

// Global error handler to prevent extension errors from crashing the app
window.addEventListener('error', (event) => {
  if (
    event.filename?.includes('chrome-extension://') ||
    event.message?.includes('Response body is already used')
  ) {
    event.preventDefault();
    event.stopPropagation();
    return false;
  }
});

window.addEventListener('unhandledrejection', (event) => {
  const reason = event.reason?.toString() || '';
  if (
    reason.includes('chrome-extension://') ||
    reason.includes('Response body is already used')
  ) {
    event.preventDefault();
    event.stopPropagation();
    return false;
  }
});

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
