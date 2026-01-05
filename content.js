(() => {
  const STORAGE_KEYS = {
    templates: "autotag_templates",
    autoSave: "autotag_auto_save"
  };

  const DEFAULT_TEMPLATES = {
    NF: "NF{DD}",
    YT: "YT{DD}",
    PROMO: "โปรจับคู่ {DD}/{MM}",
    CUSTOM: ""
  };

  const SERVICE_OPTIONS = [
    { value: "NF", label: "Netflix (NF)" },
    { value: "YT", label: "YouTube (YT)" },
    { value: "PROMO", label: "โปรจับคู่ (PROMO)" },
    { value: "CUSTOM", label: "CUSTOM (พิมพ์แท็กเอง)" }
  ];

  let sidebarRoot = null;
  let sidebarVisible = false;
  let currentTemplates = { ...DEFAULT_TEMPLATES };
  let autoSaveEnabled = false;

  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

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

  function formatToken(value) {
    return value.toString().padStart(2, "0");
  }

  function applyTemplate(template, date) {
    const dd = formatToken(date.getDate());
    const mm = formatToken(date.getMonth() + 1);
    const yyyy = date.getFullYear().toString();
    const yy = yyyy.slice(-2);
    const d = date.getDate().toString();
    const m = (date.getMonth() + 1).toString();

    return template
      .replaceAll("{DD}", dd)
      .replaceAll("{MM}", mm)
      .replaceAll("{YYYY}", yyyy)
      .replaceAll("{YY}", yy)
      .replaceAll("{D}", d)
      .replaceAll("{M}", m);
  }

  function normalizeText(text) {
    return text.replace(/\s+/g, " ").trim();
  }

  function findModal() {
    return (
      document.querySelector('[role="dialog"]') ||
      document.querySelector('.modal') ||
      document.querySelector('.ReactModal__Content')
    );
  }

  async function waitFor(fn, { timeout = 8000, interval = 200 } = {}) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
      const result = fn();
      if (result) {
        return result;
      }
      await wait(interval);
    }
    return null;
  }

  function findEditTagButton() {
    const candidates = Array.from(
      document.querySelectorAll('button, a, [role="button"]')
    );
    const labels = ["edit tags", "แก้ไขแท็ก", "edit tag", "แท็ก"];

    return candidates.find((el) => {
      const label = normalizeText(
        (el.getAttribute("aria-label") || "") +
          " " +
          (el.getAttribute("title") || "") +
          " " +
          (el.textContent || "")
      ).toLowerCase();
      return labels.some((keyword) => label.includes(keyword));
    });
  }

  function findTagInput(modal) {
    return (
      modal.querySelector('input[name="edit-tag-suggestions"].tt-input') ||
      modal.querySelector('input[placeholder*="Add tag" i]') ||
      modal.querySelector('input[placeholder*="เพิ่มแท็ก" i]') ||
      modal.querySelector('input[placeholder*="แท็ก" i]') ||
      modal.querySelector('input[aria-label*="Add tag" i]') ||
      modal.querySelector('input[aria-label*="เพิ่มแท็ก" i]') ||
      modal.querySelector('input[aria-label*="tag" i]')
    );
  }

  function findSaveButton(modal) {
    const primary = modal.querySelector('button.btn.btn-primary');
    if (primary) {
      return primary;
    }
    const buttons = Array.from(modal.querySelectorAll('button'));
    return buttons.find((button) => {
      const text = normalizeText(button.textContent || "").toLowerCase();
      return (
        text.includes("save") ||
        text.includes("บันทึก") ||
        text.includes("ยืนยัน")
      );
    });
  }

  function findTagInModal(modal, tag) {
    const normalizedTag = normalizeText(tag).toLowerCase();
    const items = Array.from(
      modal.querySelectorAll('button, span, div, li')
    );
    return items.find((item) => {
      const text = normalizeText(item.textContent || "").toLowerCase();
      return text === normalizedTag;
    });
  }

  function tagChipExists(modal, tag) {
    const normalizedTag = normalizeText(tag).toLowerCase();
    const chips = Array.from(
      modal.querySelectorAll('.kv-tag, .tag, .tag-item, [data-tag]')
    );
    return chips.some((chip) => {
      const text = normalizeText(chip.textContent || "").toLowerCase();
      return text === normalizedTag;
    });
  }

  async function createTag(modal, tag) {
    const input = findTagInput(modal);
    if (!input) {
      throw new Error("ไม่พบช่องเพิ่มแท็ก (Add tag)");
    }

    input.removeAttribute("readonly");
    input.removeAttribute("disabled");
    input.focus();
    input.value = tag;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
    input.dispatchEvent(
      new KeyboardEvent("keydown", { bubbles: true, key: "Enter" })
    );
    input.dispatchEvent(
      new KeyboardEvent("keyup", { bubbles: true, key: "Enter" })
    );

    const chip = await waitFor(() => tagChipExists(modal, tag), {
      timeout: 5000,
      interval: 200
    });

    if (!chip) {
      throw new Error("เพิ่มแท็กไม่สำเร็จ โปรดลองอีกครั้ง");
    }
  }

  async function clickSave(modal) {
    const saveButton = findSaveButton(modal);
    if (!saveButton) {
      throw new Error("ไม่พบปุ่ม Save");
    }
    saveButton.click();
    await waitFor(() => !findModal(), { timeout: 8000, interval: 200 });
  }

  async function applyTag(tag, autoSave) {
    const editButton = findEditTagButton();
    if (!editButton) {
      throw new Error("ไม่พบปุ่มแก้ไขแท็กในโปรไฟล์ลูกค้า");
    }
    editButton.click();

    const modal = await waitFor(findModal, { timeout: 8000, interval: 200 });
    if (!modal) {
      throw new Error("ไม่พบหน้าต่าง Edit tags");
    }

    const existing = findTagInModal(modal, tag);
    if (existing) {
      existing.click();
    } else {
      await createTag(modal, tag);
    }

    if (autoSave) {
      await clickSave(modal);
    }
  }

  function buildSidebar() {
    if (sidebarRoot) {
      return sidebarRoot;
    }

    const style = document.createElement("style");
    style.textContent = `
      #autotag-pro-sidebar {
        position: fixed;
        top: 0;
        right: 0;
        width: 360px;
        height: 100vh;
        background: #ffffff;
        border-left: 1px solid #e2e2e2;
        box-shadow: -2px 0 12px rgba(0, 0, 0, 0.12);
        z-index: 999999;
        display: flex;
        flex-direction: column;
        font-family: "Segoe UI", system-ui, sans-serif;
      }

      #autotag-pro-sidebar.hidden {
        display: none;
      }

      #autotag-pro-header {
        padding: 16px;
        border-bottom: 1px solid #f0f0f0;
        background: #f8f8f8;
      }

      #autotag-pro-header h2 {
        margin: 0 0 8px;
        font-size: 18px;
      }

      #autotag-pro-header p {
        margin: 0;
        font-size: 12px;
        color: #666;
      }

      #autotag-pro-content {
        padding: 16px;
        overflow-y: auto;
        flex: 1;
      }

      #autotag-pro-content label {
        display: block;
        margin-bottom: 6px;
        font-weight: 600;
        font-size: 13px;
      }

      #autotag-pro-content select,
      #autotag-pro-content input[type="date"],
      #autotag-pro-content input[type="text"] {
        width: 100%;
        padding: 8px 10px;
        border: 1px solid #d0d0d0;
        border-radius: 6px;
        font-size: 14px;
        box-sizing: border-box;
        margin-bottom: 12px;
      }

      #autotag-pro-content .hint {
        font-size: 12px;
        color: #555;
        margin-bottom: 12px;
      }

      #autotag-pro-preview {
        padding: 10px;
        background: #f5f7ff;
        border-radius: 6px;
        font-size: 14px;
        margin-bottom: 12px;
        word-break: break-all;
      }

      #autotag-pro-actions {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      #autotag-pro-apply {
        background: #2f6feb;
        border: none;
        color: #fff;
        padding: 10px;
        border-radius: 6px;
        font-size: 15px;
        cursor: pointer;
      }

      #autotag-pro-apply:disabled {
        background: #a8c2ff;
        cursor: not-allowed;
      }

      #autotag-pro-status {
        margin-top: 10px;
        font-size: 12px;
        color: #444;
        min-height: 18px;
      }

      #autotag-pro-autosave {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 10px;
      }

      #autotag-pro-resizer {
        position: absolute;
        left: 0;
        top: 0;
        width: 6px;
        height: 100%;
        cursor: ew-resize;
        background: transparent;
      }
    `;

    document.head.appendChild(style);

    const sidebar = document.createElement("div");
    sidebar.id = "autotag-pro-sidebar";
    sidebar.classList.add("hidden");

    const resizer = document.createElement("div");
    resizer.id = "autotag-pro-resizer";
    sidebar.appendChild(resizer);

    const header = document.createElement("div");
    header.id = "autotag-pro-header";
    header.innerHTML = `
      <h2>AutoTag PRO</h2>
      <p>เลือกบริการ + วันที่ แล้วกด “ติดแท็ก” เพื่อช่วยมือใหม่ทำงานเร็วขึ้น</p>
    `;

    const content = document.createElement("div");
    content.id = "autotag-pro-content";

    const serviceLabel = document.createElement("label");
    serviceLabel.textContent = "บริการ";
    const serviceSelect = document.createElement("select");
    serviceSelect.id = "autotag-pro-service";
    SERVICE_OPTIONS.forEach((service) => {
      const option = document.createElement("option");
      option.value = service.value;
      option.textContent = service.label;
      serviceSelect.appendChild(option);
    });

    const customLabel = document.createElement("label");
    customLabel.textContent = "พิมพ์แท็กเอง (เมื่อเลือก CUSTOM)";
    const customInput = document.createElement("input");
    customInput.type = "text";
    customInput.id = "autotag-pro-custom";
    customInput.placeholder = "พิมพ์ชื่อแท็กที่ต้องการ";

    const dateLabel = document.createElement("label");
    dateLabel.textContent = "วันที่";
    const dateInput = document.createElement("input");
    dateInput.type = "date";
    dateInput.id = "autotag-pro-date";

    const hint = document.createElement("div");
    hint.className = "hint";
    hint.textContent = "Tip: ถ้าไม่มีแท็ก ระบบจะสร้างให้เองโดยอัตโนมัติ";

    const previewLabel = document.createElement("label");
    previewLabel.textContent = "Preview";
    const preview = document.createElement("div");
    preview.id = "autotag-pro-preview";

    const autoSaveWrap = document.createElement("label");
    autoSaveWrap.id = "autotag-pro-autosave";
    const autoSaveCheckbox = document.createElement("input");
    autoSaveCheckbox.type = "checkbox";
    autoSaveCheckbox.id = "autotag-pro-auto-save";
    const autoSaveText = document.createElement("span");
    autoSaveText.textContent = "Auto Save (กด Save ให้อัตโนมัติ)";
    autoSaveWrap.appendChild(autoSaveCheckbox);
    autoSaveWrap.appendChild(autoSaveText);

    const actions = document.createElement("div");
    actions.id = "autotag-pro-actions";
    const applyButton = document.createElement("button");
    applyButton.id = "autotag-pro-apply";
    applyButton.textContent = "✅ ติดแท็ก";

    const status = document.createElement("div");
    status.id = "autotag-pro-status";

    actions.appendChild(applyButton);

    content.appendChild(serviceLabel);
    content.appendChild(serviceSelect);
    content.appendChild(customLabel);
    content.appendChild(customInput);
    content.appendChild(dateLabel);
    content.appendChild(dateInput);
    content.appendChild(hint);
    content.appendChild(previewLabel);
    content.appendChild(preview);
    content.appendChild(autoSaveWrap);
    content.appendChild(actions);
    content.appendChild(status);

    sidebar.appendChild(header);
    sidebar.appendChild(content);
    document.body.appendChild(sidebar);

    setupResizer(sidebar, resizer);

    loadSettings().then(() => {
      autoSaveCheckbox.checked = autoSaveEnabled;
      dateInput.valueAsDate = new Date();
      updatePreview();
    });

    function updatePreview() {
      const selectedService = serviceSelect.value;
      const date = dateInput.valueAsDate || new Date();
      const template =
        selectedService === "CUSTOM"
          ? customInput.value.trim()
          : currentTemplates[selectedService] || "";
      const previewText = template
        ? applyTemplate(template, date)
        : "(กรุณากรอกแท็ก)";
      preview.textContent = previewText;
    }

    serviceSelect.addEventListener("change", () => {
      updatePreview();
    });

    dateInput.addEventListener("change", () => {
      updatePreview();
    });

    customInput.addEventListener("input", () => {
      updatePreview();
    });

    autoSaveCheckbox.addEventListener("change", async () => {
      autoSaveEnabled = autoSaveCheckbox.checked;
      await setStorage({ [STORAGE_KEYS.autoSave]: autoSaveEnabled });
    });

    applyButton.addEventListener("click", async () => {
      const selectedService = serviceSelect.value;
      const date = dateInput.valueAsDate || new Date();
      const rawTemplate =
        selectedService === "CUSTOM"
          ? customInput.value.trim()
          : currentTemplates[selectedService] || "";

      const tag = rawTemplate ? applyTemplate(rawTemplate, date).trim() : "";

      if (!tag) {
        status.textContent = "กรุณาใส่ชื่อแท็กก่อน";
        return;
      }

      applyButton.disabled = true;
      status.textContent = "กำลังติดแท็ก...";
      try {
        await applyTag(tag, autoSaveEnabled);
        status.textContent = "ติดแท็กสำเร็จ ✅";
      } catch (error) {
        status.textContent = `ผิดพลาด: ${error.message}`;
      } finally {
        applyButton.disabled = false;
      }
    });

    sidebarRoot = sidebar;
    return sidebar;
  }

  function setupResizer(sidebar, resizer) {
    let isResizing = false;
    let startX = 0;
    let startWidth = 360;

    const onMouseMove = (event) => {
      if (!isResizing) {
        return;
      }
      const delta = startX - event.clientX;
      const newWidth = Math.min(Math.max(startWidth + delta, 260), 520);
      sidebar.style.width = `${newWidth}px`;
    };

    const onMouseUp = () => {
      if (!isResizing) {
        return;
      }
      isResizing = false;
      document.body.style.userSelect = "";
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
    };

    resizer.addEventListener("mousedown", (event) => {
      isResizing = true;
      startX = event.clientX;
      startWidth = sidebar.getBoundingClientRect().width;
      document.body.style.userSelect = "none";
      document.addEventListener("mousemove", onMouseMove);
      document.addEventListener("mouseup", onMouseUp);
    });
  }

  async function loadSettings() {
    const stored = await getStorage([
      STORAGE_KEYS.templates,
      STORAGE_KEYS.autoSave
    ]);
    currentTemplates = {
      ...DEFAULT_TEMPLATES,
      ...(stored[STORAGE_KEYS.templates] || {})
    };
    autoSaveEnabled = Boolean(stored[STORAGE_KEYS.autoSave]);
  }

  function toggleSidebar() {
    const sidebar = buildSidebar();
    sidebarVisible = !sidebarVisible;
    sidebar.classList.toggle("hidden", !sidebarVisible);
  }

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message?.type === "AUTOTAG_UI" && message.action === "TOGGLE_SIDEBAR") {
      toggleSidebar();
      sendResponse({ ok: true });
      return true;
    }
    return false;
  });
})();
