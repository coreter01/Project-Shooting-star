"""
Quản lý config.json:
- Lưu ở ~/.config/tro-ly-sieu-luoi/config.json (chuẩn XDG, không nằm trong thư mục cài app).
- Sau mỗi lần ghi, chmod 600 (chỉ user sở hữu đọc/ghi được).
- Khi load, nếu phát hiện quyền file bị mở quá rộng (group/other có quyền đọc),
  tự động siết lại về 600 và cảnh báo — vì API key coi như đã có nguy cơ lộ.
"""
import json
import os
import stat
from pathlib import Path

APP_DIR_NAME = "shooting-star"

DEFAULT_CONFIG = {
    "api_keys": {
        "gemini": "",
        "openai": "",
        "anthropic": "",
    },
    "ollama_url": "http://localhost:11434",
    "ollama_model": "llama3",    # tên model đúng như 'ollama list' hiển thị
    "default_brain": "ollama",   # gemini | openai | anthropic | ollama
    "theme": "catppuccin_mocha",  # catppuccin_mocha | dracula
    "background_image": "",
    "background_opacity": 0.35,
    "glass_blur": 18,
    "shortcuts": {
        "mc": "~/.local/share/PrismLauncher/instances/minecraft/1.20/.minecraft",
        "server mc": "~/PinecordMC",
    },
    "blacklist": [
        "rm", "dd", "mkfs", "chmod", "chown", "shutdown", "reboot",
        "mkfs.ext4", "fdisk", "parted", "kill -9 1", "iptables -f",
        ":(){:|:&};:", "> /dev/sda", "wipefs"
    ],
    "security_log": [],
}


class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / APP_DIR_NAME
        self.config_path = self.config_dir / "config.json"
        self.data = DEFAULT_CONFIG.copy()
        self._load_or_create()

    # ---------- I/O ----------
    def _load_or_create(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        # thư mục config cũng nên kín, chỉ user truy cập
        os.chmod(self.config_dir, stat.S_IRWXU)

        if not self.config_path.exists():
            self.save()
            return

        self._check_and_fix_permissions()
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(loaded)
            self.data = merged
        except (json.JSONDecodeError, OSError):
            # config hỏng -> giữ default, không ghi đè ngay để tránh mất dữ liệu người dùng
            # có thể log việc này ra security_log
            self.data = DEFAULT_CONFIG.copy()

    def _check_and_fix_permissions(self):
        """Nếu group/other có quyền đọc/ghi file config -> siết lại 600 ngay."""
        try:
            mode = stat.S_IMODE(os.stat(self.config_path).st_mode)
            if mode & (stat.S_IRWXG | stat.S_IRWXO):
                os.chmod(self.config_path, stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass

    def save(self):
        tmp_path = self.config_path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        os.chmod(tmp_path, stat.S_IRUSR | stat.S_IWUSR)  # 600 trước khi replace, tránh cửa sổ hở quyền
        tmp_path.replace(self.config_path)

    # ---------- helpers ----------
    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def log_security_event(self, event: str):
        log = self.data.get("security_log", [])
        log.append(event)
        self.data["security_log"] = log[-200:]  # giữ tối đa 200 dòng gần nhất
        self.save()
