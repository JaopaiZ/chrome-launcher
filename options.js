const STORAGE_KEYS = {
  templates: "autotag_templates",
  autoSave: "autotag_auto_save"
};

const DEFAULT_TEMPLATES = {
  NF: "NF{DD}",
  YT: "YT{DD}",
  PROMO: "โปรจับคู่ {DD}/{MM}"
};

function getStorage(keys) {
  return new Promise((resolve) => {
    chrome.storage.sync.get(keys, resolve);
  });
}

function setStorage(values) {
  return new Promise((resolve) => {
    chrome.storage.sync.set(values, resolve);
  });
}

function byId(id) {
  return document.getElementById(id);
}

async function loadSettings() {
  const stored = await getStorage([STORAGE_KEYS.templates, STORAGE_KEYS.autoSave]);
  const templates = {
    ...DEFAULT_TEMPLATES,
    ...(stored[STORAGE_KEYS.templates] || {})
  };

  byId("template-nf").value = templates.NF || "";
  byId("template-yt").value = templates.YT || "";
  byId("template-promo").value = templates.PROMO || "";
  byId("auto-save").checked = Boolean(stored[STORAGE_KEYS.autoSave]);
}

async function saveSettings() {
  const templates = {
    NF: byId("template-nf").value.trim() || DEFAULT_TEMPLATES.NF,
    YT: byId("template-yt").value.trim() || DEFAULT_TEMPLATES.YT,
    PROMO: byId("template-promo").value.trim() || DEFAULT_TEMPLATES.PROMO
  };
  const autoSave = byId("auto-save").checked;

  await setStorage({
    [STORAGE_KEYS.templates]: templates,
    [STORAGE_KEYS.autoSave]: autoSave
  });

  const status = byId("status");
  status.textContent = "บันทึกเรียบร้อยแล้ว";
  setTimeout(() => {
    status.textContent = "";
  }, 2000);
}

byId("save").addEventListener("click", saveSettings);

loadSettings();
