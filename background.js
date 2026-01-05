const LINE_HOSTS = ["chat.line.biz", "manager.line.biz"];

function isLineUrl(url) {
  try {
    const parsed = new URL(url);
    return LINE_HOSTS.includes(parsed.hostname);
  } catch (error) {
    return false;
  }
}

function sendToggleSidebar(tabId) {
  return new Promise((resolve, reject) => {
    chrome.tabs.sendMessage(
      tabId,
      { type: "AUTOTAG_UI", action: "TOGGLE_SIDEBAR" },
      (response) => {
        const lastError = chrome.runtime.lastError;
        if (lastError) {
          reject(lastError);
          return;
        }
        resolve(response);
      }
    );
  });
}

async function injectContentScript(tabId) {
  await chrome.scripting.executeScript({
    target: { tabId },
    files: ["content.js"]
  });
}

chrome.action.onClicked.addListener(async (tab) => {
  if (!tab.id || !tab.url) {
    console.log("[AutoTag PRO] No active tab to inject.");
    return;
  }

  if (!isLineUrl(tab.url)) {
    console.log("[AutoTag PRO] Unsupported URL:", tab.url);
    return;
  }

  if (chrome.sidePanel) {
    console.log("[AutoTag PRO] chrome.sidePanel available but using in-page sidebar.");
  }

  try {
    await sendToggleSidebar(tab.id);
    console.log("[AutoTag PRO] Sidebar toggled via existing content script.");
  } catch (error) {
    console.log("[AutoTag PRO] Message failed, injecting content script.", error);
    try {
      await injectContentScript(tab.id);
      await sendToggleSidebar(tab.id);
      console.log("[AutoTag PRO] Sidebar toggled after injection.");
    } catch (injectError) {
      console.log("[AutoTag PRO] Failed to inject content script.", injectError);
    }
  }
});
