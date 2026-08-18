# Project Shooting Star

Trợ Lý Siêu Lười — bản Tauri. Vỏ giao diện + đóng gói app thật (Tauri/Rust), não xử lý vẫn là Python (`core/`) gần như giữ nguyên từ bản PySide6 trước, không viết lại từ đầu.

## 1. Kiến trúc — vì sao tách vậy?

```
Frontend (HTML/CSS/JS, kính mờ + animation)
        │  invoke("call_core", {...})
Rust (src-tauri/) — CHỈ làm vỏ, không có logic nghiệp vụ
        │  spawn: python3 core/bridge.py '<json>'
Python (core/) — toàn bộ não: AI client, bảo mật, executor, config
```

Mỗi lần frontend cần làm gì (hỏi AI, kiểm tra lệnh có nguy hiểm không, chạy 1 hành động...), Rust chạy `python3 core/bridge.py '<json request>'` như **1 tiến trình con ngắn hạn** — không phải server sống lâu, không có port nào mở, đúng tinh thần "không chạy ngầm" từ đầu.

Vì sao không viết lại logic bảo mật bằng Rust/JS? Vì `core/security.py`, `core/executor.py` đã test kỹ ở bản PySide6 (whitelist, blacklist, JSON schema chống injection) — giữ nguyên để không phải test lại từ đầu, chỉ đổi lớp hiển thị.

## 2. Đã thêm so với bản Qt

- **Cài như 1 app thật** (`npm run build` ra `.deb`/AppImage) — không còn phải tự tạo file `.desktop` thủ công, không còn dính lỗi GNOME "Allow Launching" vì app cài qua gói hệ thống được tin cậy sẵn.
- **Sidebar Cài đặt trượt từ trái** (CSS transform, animation mượt) thay vì mở cửa sổ Settings riêng như Qt.
- **Kính mờ (glassmorphism)**: các khung chat/panel dùng `backdrop-filter: blur()` phủ trên ảnh nền, độ mờ (blur px) và độ tối overlay chỉnh được trong Cài đặt.
  - Lưu ý: đây là kính mờ **trong app** (blur ảnh nền do app tự vẽ), KHÔNG phải kính mờ xuyên thấu desktop thật (kiểu Windows Acrylic) — Linux/GTK không hỗ trợ ổn định việc đó qua mọi compositor, nên không làm để tránh vỡ giao diện tùy máy.
- Icon riêng (ngôi sao băng), không còn icon mặc định Qt.

## 3. Bảo mật — giữ nguyên 100% từ bản trước

- AI chỉ trả JSON đúng schema (`core/security.py::parse_ai_response`) — text tự do không có quyền thực thi.
- `run_command` chỉ chạy đúng whitelist lệnh xem-thông-tin, không nhận lệnh tự do.
- Chạy qua `subprocess.Popen(argv_list, shell=False)` — không qua `sh -c`, nên `&&`/`;`/`|` không có ý nghĩa nối lệnh.
- Blacklist làm lớp phòng vệ thứ 2 cho `install_package`.
- `config.json` tự `chmod 600`, tự sửa nếu quyền bị nới lỏng.
- Chặn dính blacklist/không whitelist → cảnh báo đỏ ngay, KHÔNG hỏi xác nhận.
- Lệnh hợp lệ vẫn luôn cần bấm YES/NO thủ công (modal kính mờ, không phải popup hệ thống xấu).

## 4. Cài & chạy (dev)

```bash
# Rust + Cargo
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Thư viện hệ thống cho Tauri (Debian/Ubuntu/Zorin)
sudo apt update && sudo apt install -y libwebkit2gtk-4.1-dev build-essential curl wget file \
  libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev pkexec python3

npm install
./build-sidecar.sh   # đóng core/ thành sidecar — chạy 1 lần, cần mạng lần đầu
npm run dev
```

## 5. Build ra app cài thật

```bash
npm run build
```
Ra file trong `src-tauri/target/release/bundle/` (`.deb`, `.AppImage`...). Cài bằng `sudo dpkg -i ...deb` hoặc chạy thẳng AppImage — sẽ tự có icon trong menu ứng dụng, không cần script `.desktop` thủ công nữa.

**Cập nhật: đã chuyển sang sidecar.** `core/` giờ được PyInstaller đóng thành 1 binary tự chứa (`src-tauri/bin/bridge-<target-triple>`), Rust gọi thẳng binary này thay vì `python3` qua PATH. Máy người dùng **không cần cài Python 3** nữa, và không còn rủi ro PATH hijacking (binary giả tên `python3` chèn trước trong PATH). Chạy `./build-sidecar.sh` **một lần trước khi** `npm run dev` hoặc `npm run build` (script `build` đã tự gọi sẵn). Cần build riêng cho từng kiến trúc CPU nếu phát hành đa nền tảng (chạy `build-sidecar.sh` trên đúng máy/kiến trúc đích, hoặc dùng CI matrix).

## 6. Còn thiếu / nên biết trước khi release

- Chưa test build thật (`npm run build`) trên máy có màn hình — chỉ mới test logic Python qua bridge.py và cú pháp Rust/HTML/CSS/JS.
- Python core chưa được bundle sẵn (xem lưu ý mục 5) — cần `python3` + `pip install -r requirements` trên máy chạy.
- Chưa có xử lý lỗi rõ ràng nếu `python3` không tồn tại trên máy — hiện chỉ trả lỗi text chung chung.
- Ảnh nền dùng `convertFileSrc` — cần test thật trên Tauri dev để chắc đường dẫn ảnh load đúng (khác cơ chế so với web thường).
- Animation hiện mới có ở: sidebar trượt, bubble chat "rise" nhẹ khi xuất hiện, hover nút. Có thể thêm nếu bạn muốn mượt hơn nữa.
