# Miễn trừ trách nhiệm — Project Shooting Star

Đọc file này trước khi cài hoặc build. Cài đặt tức là bạn đã đọc và đồng ý các điều dưới.

## 1. Phần mềm cung cấp "NGUYÊN TRẠNG" (AS-IS)

Không có bảo hành dưới bất kỳ hình thức nào, dù công khai hay ngụ ý — bao gồm nhưng
không giới hạn khả năng sử dụng cho mục đích cụ thể, không lỗi, hay an toàn tuyệt đối.
Tác giả **không chịu trách nhiệm** cho bất kỳ thiệt hại nào (mất dữ liệu, hỏng hệ thống,
lộ thông tin, tổn thất khác) phát sinh từ việc dùng phần mềm này, kể cả khi đã được
cảnh báo trước về khả năng xảy ra thiệt hại đó.

## 2. App này thực thi lệnh trên máy bạn — cần hiểu rõ trước khi dùng

- App cho AI đề xuất hành động (mở đường dẫn, chạy lệnh xem-thông-tin, cài gói phần
  mềm) và **luôn yêu cầu bạn xác nhận thủ công** (YES/NO) trước khi chạy — trừ khi bạn
  tự tắt bước xác nhận đi (không khuyến khích).
- `run_command` giới hạn bằng **whitelist** cố định (`ls`, `df`, `ps`...), không chạy
  lệnh tự do. Danh sách này nằm trong `core/security.py` — bạn nên tự đọc qua trước khi
  tin tưởng, đặc biệt nếu tải bản build từ người khác thay vì tự build từ source.
- `install_package` gọi `pkexec` (dialog mật khẩu **hệ thống**, do polkit vẽ, không
  phải app tự vẽ). **Chỉ nhập mật khẩu vào đúng dialog polkit gốc** — không bao giờ vào
  ô nhập nằm trong cửa sổ app. Nếu thấy prompt mật khẩu lạ bên trong giao diện app, đó
  là dấu hiệu bản build đã bị chỉnh sửa độc hại — dừng lại, không nhập gì.
- Không có cơ chế nào đảm bảo bản build bạn đang chạy khớp 100% với source công khai
  trừ khi bạn tự build từ source hoặc tự verify checksum.

## 3. Dữ liệu gửi ra ngoài (bên thứ 3)

Khi dùng não Gemini / OpenAI / Anthropic: nội dung chat (kể cả lịch sử hội thoại) được
gửi tới máy chủ của các bên đó theo API key riêng của bạn — chịu điều khoản/chính sách
bảo mật của từng bên, tác giả không kiểm soát và không chịu trách nhiệm cách họ xử lý
dữ liệu. Dùng não Ollama (local) thì không có dữ liệu nào rời khỏi máy.

**Không nhập vào chat bất cứ thông tin nào bạn không muốn gửi lên máy chủ AI ngoài**
(mật khẩu, khóa API khác, nội dung file nhạy cảm...) khi đang dùng não cloud.

## 4. Chi phí

Gemini/OpenAI/Anthropic tính phí theo lượng dùng của tài khoản bạn tự đăng ký — tác giả
không chịu trách nhiệm cho bất kỳ chi phí nào phát sinh.

## 5. Không liên kết với các bên thứ 3

Project này không được Anthropic, Google, OpenAI, hay Ollama chứng thực hay tài trợ.
Tên các bên trên chỉ dùng để mô tả tính năng tích hợp.

## 6. Giấy phép

Xem file `LICENSE` (nếu có) để biết điều khoản sử dụng/sao chép/sửa đổi mã nguồn.
