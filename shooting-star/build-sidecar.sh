#!/usr/bin/env bash
# Đóng core/bridge.py (+ toàn bộ core/*.py) thành 1 binary tự chứa bằng PyInstaller,
# đặt đúng tên/định dạng Tauri sidecar yêu cầu: bin/bridge-<target-triple>[.exe]
#
# CHẠY TRƯỚC "npm run build". Cần mạng để tải PyInstaller + requests lần đầu.
set -euo pipefail

cd "$(dirname "$0")"

# 1) venv riêng để build, tránh lẫn với Python hệ thống
python3 -m venv .build-venv
source .build-venv/bin/activate
pip install --upgrade pip
pip install -r core/requirements.txt
pip install pyinstaller

# 2) đóng thành 1 file duy nhất (--onefile), gộp toàn bộ core/*.py vào cùng
pyinstaller --onefile --name bridge \
  --paths core \
  core/bridge.py

# 3) Tauri yêu cầu tên sidecar có hậu tố target-triple của máy build
TRIPLE="$(rustc -Vv | grep host | cut -d' ' -f2)"
mkdir -p src-tauri/bin
cp dist/bridge "src-tauri/bin/bridge-${TRIPLE}"
chmod +x "src-tauri/bin/bridge-${TRIPLE}"

echo "OK: src-tauri/bin/bridge-${TRIPLE} — giờ chạy 'npm run build' để đóng gói app."

deactivate
rm -rf build dist bridge.spec .build-venv
