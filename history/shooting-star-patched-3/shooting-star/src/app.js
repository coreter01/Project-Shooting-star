const { invoke } = window.__TAURI__.tauri;
const { open: openDialog } = window.__TAURI__.dialog;
const { convertFileSrc } = window.__TAURI__.tauri;

let config = null;
let history = []; // [{role, text}]

// ---------- cầu nối tới Python qua Rust ----------
async function callCore(cmd, params = {}) {
  const requestJson = JSON.stringify({ cmd, ...params });
  const resultJson = await invoke("call_core", { requestJson });
  const result = JSON.parse(resultJson);
  if (!result.ok) throw new Error(result.error || t("unknownCoreError"));
  return result.data;
}

// ---------- áp dụng config lên UI ----------
function applyConfigToUI() {
  document.documentElement.setAttribute("data-theme", config.theme || "catppuccin_mocha");
  document.documentElement.style.setProperty("--bg-opacity", config.background_opacity ?? 0.35);
  document.documentElement.style.setProperty("--blur", `${config.glass_blur ?? 18}px`);

  const bg = document.getElementById("bgLayer");
  bg.style.backgroundImage = config.background_image ? `url("${convertFileSrc(config.background_image)}")` : "none";

  document.getElementById("brainSelect").value = config.default_brain || "ollama";

  // form settings
  document.getElementById("keyGemini").value = config.api_keys?.gemini || "";
  document.getElementById("geminiModel").value = config.gemini_model || "gemini-3.6-flash";
  document.getElementById("keyOpenAI").value = config.api_keys?.openai || "";
  document.getElementById("keyAnthropic").value = config.api_keys?.anthropic || "";
  document.getElementById("ollamaUrl").value = config.ollama_url || "";
  document.getElementById("ollamaModel").value = config.ollama_model || "llama3";
  document.getElementById("defaultBrain").value = config.default_brain || "ollama";
  document.getElementById("themeSelect").value = config.theme || "catppuccin_mocha";
  document.getElementById("languageSelect").value = config.language || "vi";
  document.getElementById("bgOpacity").value = Math.round((config.background_opacity ?? 0.35) * 100);
  document.getElementById("glassBlur").value = config.glass_blur ?? 18;

  applyLanguage(config.language || "vi");
  renderShortcuts();
}

function renderShortcuts() {
  const ul = document.getElementById("shortcutList");
  ul.innerHTML = "";
  Object.entries(config.shortcuts || {}).forEach(([kw, path]) => {
    const li = document.createElement("li");
    li.innerHTML = `<span>${kw} → ${path}</span><button data-kw="${kw}">✕</button>`;
    li.querySelector("button").onclick = () => {
      delete config.shortcuts[kw];
      renderShortcuts();
    };
    ul.appendChild(li);
  });
}

// ---------- clock ----------
setInterval(() => {
  document.getElementById("clock").textContent = new Date().toLocaleTimeString();
}, 1000);

// ---------- chat bubbles ----------
function addBubble(text, kind, who) {
  const box = document.getElementById("messages");
  const empty = box.querySelector(".empty-state");
  if (empty) empty.remove();

  const div = document.createElement("div");
  div.className = `msg ${kind}`;
  const label = who ? `<div class="who">${who}</div>` : "";
  div.innerHTML = `${label}<div>${escapeHtml(text)}</div>`;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}
function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// ---------- gửi tin ----------
async function onSend() {
  const input = document.getElementById("chatInput");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  addBubble(text, "user");
  history.push({ role: "user", text });

  // 1) khử mò folder trước — không tốn AI call
  try {
    const path = await callCore("match_shortcut", { text });
    if (path) {
      addBubble(t("foundShortcut", path), "system");
      const argv = await callCore("build_argv", { action: { type: "open_path", target: path } });
      await callCore("run_async", { argv });
      return;
    }
  } catch (e) { /* im lặng bỏ qua, đi tiếp qua AI */ }

  // 2) gọi AI
  let raw;
  try {
    raw = await callCore("ask_ai", { brain: document.getElementById("brainSelect").value, history });
  } catch (e) {
    addBubble(t("aiCallError", e.message), "danger");
    return;
  }

  const parsed = await callCore("parse_ai_response", { raw });
  addBubble(parsed.reply, "ai", document.getElementById("brainSelect").value.toUpperCase());
  history.push({ role: "assistant", text: parsed.reply });

  if (parsed.action) await handleAction(parsed.action);
}

// ---------- xử lý action ----------
async function handleAction(action) {
  const target = action.target;
  const args = action.args || [];
  const displayCmd = [target, ...args].join(" ");

  if (action.type === "run_command") {
    const whitelisted = await callCore("is_whitelisted", { target });
    if (!whitelisted) {
      addBubble(t("blockedNotWhitelisted", target), "danger");
      await callCore("log_security_event", { event: `BLOCKED (not whitelisted): ${displayCmd}` });
      return;
    }
  }

  const dangerKw = await callCore("is_dangerous", { command: displayCmd });
  if (dangerKw) {
    addBubble(t("blockedDangerous", dangerKw, displayCmd), "danger");
    await callCore("log_security_event", { event: `BLOCKED: ${displayCmd} (matched: ${dangerKw})` });
    return;
  }

  const approved = await askConfirm(action);
  if (!approved) {
    addBubble(t("cancelled"), "system");
    return;
  }
  const argv = await callCore("build_argv", { action });

  if (action.type === "run_command" || action.type === "open_path") {
    if (action.type === "run_command") addBubble(t("running", displayCmd), "system");
    const result = await callCore("run_sync", { argv });
    if (result.exit_code !== 0) {
      addBubble(t("runError", result.exit_code, result.stderr || t("noStderr")), "danger");
    } else if (action.type === "run_command") {
      addBubble(result.stdout || t("noOutput"), "system");
    } else {
      addBubble(t("executing", displayCmd), "system");
    }
    return;
  }

  await callCore("run_async", { argv });
  addBubble(t("executing", displayCmd), "system");
}

// ---------- confirm dialog (glass modal, không phải window mới) ----------
function askConfirm(action) {
  return new Promise((resolve) => {
    const overlay = document.getElementById("confirmOverlay");
    const kindMap = { open_path: t("kindOpenPath"), run_command: t("kindRunCommand"), install_package: t("kindInstallPackage") };
    document.getElementById("confirmKind").textContent = kindMap[action.type] || action.type;
    document.getElementById("confirmTarget").textContent = [action.target, ...(action.args || [])].join(" ");
    document.getElementById("confirmReason").textContent = action.reason ? t("aiReason", action.reason) : "";
    overlay.classList.remove("hidden");

    const yes = document.getElementById("confirmYes");
    const no = document.getElementById("confirmNo");
    const cleanup = (result) => {
      overlay.classList.add("hidden");
      yes.onclick = null; no.onclick = null;
      resolve(result);
    };
    yes.onclick = () => cleanup(true);
    no.onclick = () => cleanup(false);
  });
}

// ---------- settings panel ----------
function toggleSettings(open) {
  document.getElementById("settingsPanel").classList.toggle("open", open);
  document.getElementById("settingsOverlay").classList.toggle("hidden", !open);
}

function initSettingsTabs() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.onclick = () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
    };
  });
}

async function saveSettings() {
  config.api_keys = {
    gemini: document.getElementById("keyGemini").value.trim(),
    openai: document.getElementById("keyOpenAI").value.trim(),
    anthropic: document.getElementById("keyAnthropic").value.trim(),
  };
  config.ollama_url = document.getElementById("ollamaUrl").value.trim() || "http://localhost:11434";
  config.ollama_model = document.getElementById("ollamaModel").value.trim() || "llama3";
  config.gemini_model = document.getElementById("geminiModel").value.trim() || "gemini-3.6-flash";
  config.default_brain = document.getElementById("defaultBrain").value;
  config.theme = document.getElementById("themeSelect").value;
  config.language = document.getElementById("languageSelect").value;
  config.background_opacity = document.getElementById("bgOpacity").value / 100;
  config.glass_blur = parseInt(document.getElementById("glassBlur").value, 10);

  for (const key of ["api_keys", "ollama_url", "ollama_model", "gemini_model", "default_brain", "theme", "language", "background_image", "background_opacity", "glass_blur", "shortcuts"]) {
    await callCore("set_config", { key, value: config[key] });
  }
  applyConfigToUI();
  toggleSettings(false);
}

// ---------- boot ----------
async function boot() {
  config = await callCore("get_config");
  applyConfigToUI();
  initSettingsTabs();

  document.getElementById("inputBar").addEventListener("submit", (e) => { e.preventDefault(); onSend(); });
  document.getElementById("menuBtn").addEventListener("click", () => toggleSettings(true));
  document.getElementById("closeSettings").addEventListener("click", () => toggleSettings(false));
  document.getElementById("settingsOverlay").addEventListener("click", () => toggleSettings(false));
  document.getElementById("saveSettings").addEventListener("click", saveSettings);

  document.getElementById("brainSelect").addEventListener("change", (e) => {
    config.default_brain = e.target.value;
    callCore("set_config", { key: "default_brain", value: e.target.value });
  });

  document.getElementById("languageSelect").addEventListener("change", (e) => {
    applyLanguage(e.target.value); // đổi ngay lập tức, không cần bấm Lưu mới thấy
  });

  document.getElementById("bgUpload").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    config.background_image = file.path || URL.createObjectURL(file);
    applyConfigToUI();
  });
  document.getElementById("clearBg").addEventListener("click", () => {
    config.background_image = "";
    applyConfigToUI();
  });

  document.getElementById("addShortcut").addEventListener("click", () => {
    const kw = document.getElementById("newShortcutKey").value.trim();
    const path = document.getElementById("newShortcutPath").value.trim();
    if (!kw || !path) return;
    config.shortcuts = config.shortcuts || {};
    config.shortcuts[kw] = path;
    document.getElementById("newShortcutKey").value = "";
    document.getElementById("newShortcutPath").value = "";
    renderShortcuts();
  });
}

boot();
