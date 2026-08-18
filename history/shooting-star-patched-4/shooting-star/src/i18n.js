// i18n.js — từ điển song ngữ đơn giản, không cần thư viện ngoài.
// Thêm ngôn ngữ mới: thêm 1 object con vào DICT, xong.

const DICT = {
  vi: {
    settingsTitle: "Cài đặt",
    brandName: "Astra",
    emptyHint: 'Gõ: "mở mc", "cài htop", hoặc chat bình thường. Enter để gửi.',
    inputPlaceholder: 'Gõ: "mở mc", "cài htop"...',
    send: "Gửi",
    untitledSession: "Untitled session",
    tabApi: "API Keys",
    tabAppearance: "Giao diện",
    tabShortcuts: "Đường tắt",
    labelGemini: "Gemini API key",
    labelGeminiModel: "Model Gemini",
    labelOpenAI: "OpenAI API key",
    labelAnthropic: "Anthropic API key",
    labelOllamaUrl: "Ollama URL",
    labelOllamaModel: "Model Ollama",
    labelDefaultBrain: "Não mặc định",
    keyStorageNote: "Key lưu ở ~/.config/shooting-star/config.json, quyền file 600.",
    labelTheme: "Theme",
    labelBg: "Ảnh nền",
    chooseBg: "Chọn ảnh nền...",
    clearBg: "Xóa ảnh nền",
    labelOverlayOpacity: "Độ mờ lớp phủ",
    labelGlassBlur: "Độ mờ kính (blur panel)",
    labelLanguage: "Ngôn ngữ",
    shortcutHint: "Từ khóa gõ trong chat → đường dẫn mở ngay, không cần hỏi AI.",
    shortcutKeyPlaceholder: "Từ khóa (vd: mở mc)",
    shortcutPathPlaceholder: "Đường dẫn",
    addShortcut: "+ Thêm",
    save: "Lưu",
    confirmTitle: "⚠ AI muốn thực thi lệnh trên máy bạn",
    confirmNo: "✕ NO",
    confirmYes: "✓ YES",
    kindOpenPath: "Mở đường dẫn / ứng dụng",
    kindRunCommand: "Chạy lệnh hệ thống",
    kindInstallPackage: "Cài đặt gói phần mềm",
    aiReason: (r) => `Lý do AI đưa ra: ${r}`,
    foundShortcut: (p) => `Tìm thấy đường tắt, đang mở: ${p}`,
    aiCallError: (m) => `Lỗi gọi AI: ${m}`,
    blockedNotWhitelisted: (t) => `🛑 ĐÃ CHẶN — lệnh "${t}" không nằm trong whitelist cho phép.`,
    blockedDangerous: (k, c) => `🛑 ĐÃ CHẶN — chứa từ khóa nguy hiểm "${k}": ${c}`,
    cancelled: "Đã hủy theo yêu cầu của bạn.",
    running: (c) => `Đang chạy: ${c}`,
    executing: (c) => `Đang thực thi: ${c}`,
    noOutput: "(không có output)",
    noStderr: "(không có stderr)",
    runError: (code, err) => `⚠️ Lệnh kết thúc với lỗi (mã ${code}):\n${err}`,
    unknownCoreError: "Lỗi không rõ từ core.",
  },
  en: {
    settingsTitle: "Settings",
    brandName: "Astra",
    emptyHint: 'Type: "open mc", "install htop", or just chat. Enter to send.',
    inputPlaceholder: 'Type: "open mc", "install htop"...',
    send: "Send",
    untitledSession: "Untitled session",
    tabApi: "API Keys",
    tabAppearance: "Appearance",
    tabShortcuts: "Shortcuts",
    labelGemini: "Gemini API key",
    labelGeminiModel: "Gemini model",
    labelOpenAI: "OpenAI API key",
    labelAnthropic: "Anthropic API key",
    labelOllamaUrl: "Ollama URL",
    labelOllamaModel: "Ollama model",
    labelDefaultBrain: "Default brain",
    keyStorageNote: "Keys stored at ~/.config/shooting-star/config.json, file mode 600.",
    labelTheme: "Theme",
    labelBg: "Background image",
    chooseBg: "Choose background...",
    clearBg: "Clear background",
    labelOverlayOpacity: "Overlay opacity",
    labelGlassBlur: "Glass blur",
    labelLanguage: "Language",
    shortcutHint: "Keyword typed in chat → path opens instantly, no AI call needed.",
    shortcutKeyPlaceholder: "Keyword (e.g. open mc)",
    shortcutPathPlaceholder: "Path",
    addShortcut: "+ Add",
    save: "Save",
    confirmTitle: "⚠ AI wants to run a command on your machine",
    confirmNo: "✕ NO",
    confirmYes: "✓ YES",
    kindOpenPath: "Open path / app",
    kindRunCommand: "Run system command",
    kindInstallPackage: "Install package",
    aiReason: (r) => `AI's reason: ${r}`,
    foundShortcut: (p) => `Shortcut matched, opening: ${p}`,
    aiCallError: (m) => `AI call failed: ${m}`,
    blockedNotWhitelisted: (t) => `🛑 BLOCKED — command "${t}" is not in the allowed whitelist.`,
    blockedDangerous: (k, c) => `🛑 BLOCKED — matched dangerous keyword "${k}": ${c}`,
    cancelled: "Cancelled at your request.",
    running: (c) => `Running: ${c}`,
    executing: (c) => `Executing: ${c}`,
    noOutput: "(no output)",
    noStderr: "(no stderr)",
    runError: (code, err) => `⚠️ Command exited with error (code ${code}):\n${err}`,
    unknownCoreError: "Unknown error from core.",
  },
};

let currentLang = "vi";

function t(key, ...args) {
  const entry = (DICT[currentLang] && DICT[currentLang][key]) ?? DICT.vi[key];
  return typeof entry === "function" ? entry(...args) : entry;
}

function applyLanguage(lang) {
  currentLang = DICT[lang] ? lang : "vi";
  document.documentElement.lang = currentLang;

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.dataset.i18n;
    if (DICT[currentLang][key] !== undefined) el.textContent = t(key);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.dataset.i18nPlaceholder;
    if (DICT[currentLang][key] !== undefined) el.placeholder = t(key);
  });
}
