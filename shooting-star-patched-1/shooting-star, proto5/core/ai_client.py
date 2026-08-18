"""
Gọi các "Não" AI khác nhau bằng 1 giao diện chung: ask(brain, api_keys, ollama_url, history) -> str (raw text)
Việc parse/validate JSON nằm ở core/security.py, không làm ở đây — tách trách nhiệm rõ.

QUAN TRỌNG (chống prompt injection): system prompt buộc model CHỈ trả JSON thuần,
không markdown, không lời dẫn. Model không được tự quyết định "tự nhiên ngôn ngữ" —
nếu không tuân theo, security.parse_ai_response() sẽ tự động hạ cấp toàn bộ output
xuống thành text hiển thị, không có quyền hành động.
"""
import json
import requests

SYSTEM_PROMPT = """Bạn là trợ lý dòng lệnh cho Linux, tên "Trợ Lý Siêu Lười".
LUÔN LUÔN trả lời bằng DUY NHẤT một object JSON hợp lệ, không kèm markdown, không kèm text ngoài JSON.
Schema bắt buộc:
{
  "reply": "<câu trả lời/tóm tắt hiển thị cho người dùng, ngôn ngữ tự nhiên>",
  "action": null
}
Nếu người dùng muốn mở file/app, chạy lệnh xem thông tin, hoặc cài phần mềm, đặt "action" thành:
{"type": "open_path"|"run_command"|"install_package", "target": "<path, tên lệnh, hoặc tên gói>", "args": [<tham số dạng chuỗi, có thể để mảng rỗng>], "reason": "<vì sao>"}

QUAN TRỌNG cho type "run_command": "target" CHỈ được là một trong các lệnh sau
(không được là lệnh khác, không được ghép nhiều lệnh, không dùng &&, ;, |, >, <):
ls, df, free, uname, lscpu, uptime, whoami, du, ps, pwd, date, hostnamectl, lsblk, neofetch
Tham số đi kèm đặt trong mảng "args", ví dụ {"type":"run_command","target":"df","args":["-h"]}.
Nếu người dùng muốn thứ gì đó ngoài các lệnh trên (sửa file, xoá, đổi quyền...), KHÔNG đặt action,
chỉ trả lời qua "reply" giải thích rằng việc đó ngoài khả năng được phép của app.

Nếu không cần hành động gì, "action" phải là null. Không tự thêm khóa nào khác ngoài "reply" và "action".
Không bao giờ bọc JSON trong ```."""


def _history_to_plain(history):
    """history: list[{'role': 'user'|'assistant', 'text': str}]"""
    return [{"role": h["role"], "content": h["text"]} for h in history]


def ask(brain: str, api_keys: dict, ollama_url: str, history: list, ollama_model: str = "") -> str:
    if brain == "gemini":
        return _ask_gemini(api_keys.get("gemini", ""), history)
    if brain == "openai":
        return _ask_openai(api_keys.get("openai", ""), history)
    if brain == "anthropic":
        return _ask_anthropic(api_keys.get("anthropic", ""), history)
    if brain == "ollama":
        return _ask_ollama(ollama_url, history, ollama_model)
    return json.dumps({"reply": f"Não '{brain}' không hợp lệ.", "action": None})


def _ask_anthropic(key: str, history: list) -> str:
    if not key:
        return json.dumps({"reply": "Chưa có Anthropic API key. Vào Cài đặt để nhập.", "action": None})
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 1024,
                "system": SYSTEM_PROMPT,
                "messages": _history_to_plain(history),
            },
            timeout=30,
        )
        data = r.json()
        if "error" in data:
            return json.dumps({"reply": f"Lỗi Anthropic: {data['error'].get('message')}", "action": None})
        text = "".join(b.get("text", "") for b in data.get("content", []))
        return text
    except requests.RequestException as e:
        return json.dumps({"reply": f"Lỗi kết nối Anthropic: {e}", "action": None})


def _ask_openai(key: str, history: list) -> str:
    if not key:
        return json.dumps({"reply": "Chưa có OpenAI API key. Vào Cài đặt để nhập.", "action": None})
    try:
        msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + _history_to_plain(history)
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "content-type": "application/json"},
            json={"model": "gpt-4o-mini", "messages": msgs, "response_format": {"type": "json_object"}},
            timeout=30,
        )
        data = r.json()
        if "error" in data:
            return json.dumps({"reply": f"Lỗi OpenAI: {data['error'].get('message')}", "action": None})
        return data["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        return json.dumps({"reply": f"Lỗi kết nối OpenAI: {e}", "action": None})


def _ask_gemini(key: str, history: list) -> str:
    if not key:
        return json.dumps({"reply": "Chưa có Gemini API key. Vào Cài đặt để nhập.", "action": None})
    try:
        contents = [{"role": "user" if h["role"] == "user" else "model", "parts": [{"text": h["text"]}]} for h in history]
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}",
            json={
                "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "contents": contents,
                "generationConfig": {"response_mime_type": "application/json"},
            },
            timeout=30,
        )
        data = r.json()
        if "error" in data:
            return json.dumps({"reply": f"Lỗi Gemini: {data['error'].get('message')}", "action": None})
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (requests.RequestException, KeyError, IndexError) as e:
        return json.dumps({"reply": f"Lỗi kết nối Gemini: {e}", "action": None})


def _ask_ollama(url: str, history: list, model: str = "") -> str:
    url = (url or "http://localhost:11434").rstrip("/")
    model = model or "llama3"
    try:
        msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + _history_to_plain(history)
        r = requests.post(
            f"{url}/api/chat",
            json={"model": model, "messages": msgs, "stream": False, "format": "json"},
            timeout=60,
        )
        data = r.json()
        if "error" in data:
            return json.dumps({
                "reply": f"Ollama báo lỗi: {data['error']}. Kiểm tra đã 'ollama pull {model}' chưa, "
                         f"hoặc đổi tên model đúng trong Cài đặt.",
                "action": None,
            })
        content = data.get("message", {}).get("content", "")
        if not content:
            return json.dumps({
                "reply": f"Ollama trả về rỗng (model '{model}' có thể chưa tải về). "
                         f"Chạy 'ollama list' để xem model đã có.",
                "action": None,
            })
        return content
    except requests.RequestException as e:
        return json.dumps({
            "reply": f"Không kết nối được Ollama tại {url}: {e}. Chạy 'ollama serve' trước đã.",
            "action": None,
        })
