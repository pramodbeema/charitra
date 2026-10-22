/**
 * CHARITRA Content Script
 * Reports page title back to background for vault entries.
 */
(function () {
  // Wait for page to have a title
  function reportTitle() {
    const title = document.title || location.hostname;
    chrome.runtime.sendMessage({
      type: 'UPDATE_TITLE',
      url: location.href,
      title
    }).catch(() => {});
  }

  // Report immediately and also after DOMContentLoaded
  reportTitle();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', reportTitle);
  }

  // Watch for SPA title changes
  const observer = new MutationObserver(() => {
    reportTitle();
  });
  const titleEl = document.querySelector('title');
  if (titleEl) {
    observer.observe(titleEl, { childList: true });
  }
})();
