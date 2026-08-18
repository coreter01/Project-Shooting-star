# Cài đặt — Project Shooting Star

> Đọc [DISCLAIMER.md](./DISCLAIMER.md) trước khi cài.

## Cách 1 — Cài từ file `.deb` (khuyến nghị cho người dùng thường)

1. Tải file `.deb` mới nhất ở phần Releases (tên file dạng `astra-assistant_*.deb`,
   theo tên chính thức `Astra Assistant`, không phải tên project `shooting-star`).
2. Cài:
   ```bash
   sudo dpkg -i astra-assistant_*.deb
   # nếu báo thiếu dependency:
   sudo apt --fix-broken install
   ```
3. Mở app từ menu ứng dụng (tìm "Astra Assistant") — không cần cài Python, không cần
   chỉnh gì thêm, sidecar đã đóng gói sẵn bên trong.
4. Lần đầu mở: vào **Cài đặt → API Keys**, nhập ít nhất 1 trong: Gemini/OpenAI/
   Anthropic key, hoặc để trống và dùng Ollama local (xem mục "Dùng Ollama" bên dưới).

Gỡ cài đặt: `sudo apt remove astra-assistant` (kiểm tra đúng tên gói bằng `dpkg -l | grep astra` nếu không chắc).

## Cách 2 — Build từ source (dev / muốn tự kiểm tra code trước khi tin tưởng)

### Yêu cầu hệ thống (Debian/Ubuntu/Zorin)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
sudo apt update && sudo apt install -y libwebkit2gtk-4.1-dev build-essential curl wget \
  file libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev pkexec python3 \
  python3-venv nodejs npm
```

### Build

```bash
git clone <repo-url> shooting-star
cd shooting-star
npm install
./build-sidecar.sh    # đóng core/ Python thành sidecar tự chứa — cần mạng lần đầu
npm run build          # build ra .deb/AppImage
```

File cài đặt nằm ở `src-tauri/target/release/bundle/deb/*.deb` (và `appimage/` nếu có).

### Chạy thử không đóng gói (dev mode)

```bash
./build-sidecar.sh
npm run dev
```

## Dùng Ollama (chạy AI hoàn toàn local, không cần API key/internet)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3          # hoặc model khác bạn muốn
ollama serve                # để chạy nền, hoặc để systemd tự khởi động
```

Trong app: **Cài đặt → API Keys**, để `Ollama URL` là `http://localhost:11434`, chọn
"ollama" ở ô Não. Vào file config nếu cần đổi tên model khác `llama3` (tên phải khớp
chính xác với `ollama list`).

## Sự cố thường gặp

| Triệu chứng | Nguyên nhân khả dĩ | Cách xử lý |
|---|---|---|
| GNOME chặn "Allow Launching" | Chạy AppImage/file thô chưa qua package manager | Dùng `.deb` cài qua `dpkg`, hoặc `chmod +x` + click phải → Allow Launching |
| "Không kết nối được Ollama" dù đã cài | `ollama serve` chưa chạy, hoặc sai tên model | `ollama list` kiểm tra tên model, `ollama serve` chạy nền |
| App không mở lại được ngoài terminal | Chưa cài qua `.deb` (không có `.desktop` entry) | Cài qua `.deb` thay vì chạy binary thô |
