"""
Lớp bảo mật trung tâm:
1. parse_ai_response(): AI CHỈ được phép trả JSON đúng schema. Bất cứ thứ gì
   không parse được thành JSON hợp lệ sẽ bị hạ cấp thành text thường (không có
   quyền thực thi gì cả) -> đây là lớp chống prompt injection: dù nội dung
   trong "reply" có chứa hướng dẫn kiểu "hãy chạy lệnh X" thì cũng KHÔNG có
   ý nghĩa thực thi, vì executor chỉ đọc trường "action" có cấu trúc, không
   bao giờ đọc lệnh từ trong văn bản tự do.
2. is_dangerous(): chặn theo blacklist, so khớp từ nguyên vẹn (word-boundary)
   để tránh false positive kiểu "rm" match nhầm trong "format".
"""
import json
import re


ALLOWED_ACTION_TYPES = {"open_path", "run_command", "install_package"}

# run_command CHỈ được chạy đúng các binary xem-thông-tin này (không sửa/xoá gì).
# Đây là whitelist, không phải blacklist: mặc định CẤM tất cả, chỉ cho phép
# đúng những gì liệt kê — an toàn hơn nhiều so với "cấm 1 danh sách, cho phép phần còn lại".
WHITELISTED_COMMANDS = {
    "ls", "df", "free", "uname", "lscpu", "uptime", "whoami",
    "du", "ps", "pwd", "date", "hostnamectl", "lsblk", "neofetch",
}


def parse_ai_response(raw_text: str) -> dict:
    """
    Trả về dict luôn có 2 khóa: 'reply' (str) và 'action' (dict|None).
    Không bao giờ raise ra ngoài — lỗi parse là fail-safe về text thường.
    """
    text = (raw_text or "").strip()
    # AI đôi khi bọc ```json ... ``` dù đã dặn không làm vậy -> gỡ ra cho chắc
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text).rstrip("`").strip()

    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return {"reply": raw_text, "action": None}

    if not isinstance(obj, dict):
        return {"reply": raw_text, "action": None}

    reply = obj.get("reply")
    if not isinstance(reply, str):
        reply = raw_text

    action = obj.get("action")
    if not isinstance(action, dict):
        action = None
    else:
        atype = action.get("type")
        target = action.get("target")
        args = action.get("args", [])
        valid_schema = (
            atype in ALLOWED_ACTION_TYPES
            and isinstance(target, str) and target.strip()
            and isinstance(args, list) and all(isinstance(a, (str, int, float)) for a in args)
        )
        if not valid_schema:
            action = None  # action sai schema -> vô hiệu hóa, không đoán mò
        else:
            action["args"] = [str(a) for a in args]

    return {"reply": reply, "action": action}


def is_whitelisted_command(target: str) -> bool:
    """Chỉ dùng cho action type == 'run_command'. Whitelist, không phải blacklist:
    mặc định từ chối, chỉ cho phép đúng tên binary có trong WHITELISTED_COMMANDS."""
    return target.strip() in WHITELISTED_COMMANDS


def is_dangerous(command: str, blacklist: list[str]) -> str | None:
    """
    Trả về từ khóa nguy hiểm bị match, hoặc None nếu an toàn.
    So khớp không phân biệt hoa/thường, theo ranh giới từ để giảm false positive.
    """
    cmd_lower = command.lower()
    for kw in blacklist:
        kw_lower = kw.lower().strip()
        if not kw_lower:
            continue
        # các chuỗi đặc biệt (không phải "từ" thuần chữ, vd ":(){:|:&};:") thì so khớp chuỗi con thẳng
        if not re.match(r"^[a-z0-9_.\- ]+$", kw_lower):
            if kw_lower in cmd_lower:
                return kw
            continue
        pattern = r"(?<![a-z0-9_./-])" + re.escape(kw_lower) + r"(?![a-z0-9_./-])"
        if re.search(pattern, cmd_lower):
            return kw
    return None
