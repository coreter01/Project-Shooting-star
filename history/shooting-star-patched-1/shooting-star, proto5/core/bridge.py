#!/usr/bin/env python3
"""
Cầu nối giữa Tauri (Rust) và core logic Python.
Giao thức: mỗi lần gọi là 1 tiến trình con ngắn hạn (không phải server sống lâu):
  python3 bridge.py '<json request>'
In ra đúng 1 dòng JSON kết quả rồi thoát — giữ đúng tinh thần "không chạy ngầm".

request: {"cmd": "<tên lệnh>", ...tham số...}
Các cmd hỗ trợ:
  - get_config           -> trả toàn bộ config hiện tại
  - set_config            {key, value}
  - match_shortcut        {text}
  - ask_ai                {history: [...]}  (dùng brain/keys/url lấy từ config)
  - parse_ai_response     {raw}
  - is_whitelisted        {target}
  - is_dangerous          {command}
  - build_argv            {action}
  - run_async             {argv}
  - detect_pkg_manager    {}
  - log_security_event    {event}
"""
import sys
import json
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from core_dispatch import dispatch  # noqa: E402 (định nghĩa bên dưới trong cùng thư mục)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "Thiếu tham số JSON."}))
        return
    try:
        request = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "error": f"JSON đầu vào không hợp lệ: {e}"}))
        return

    config = ConfigManager()
    result = dispatch(request, config)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
