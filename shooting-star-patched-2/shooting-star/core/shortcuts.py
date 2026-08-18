"""
Khử mò folder: nếu câu người dùng gõ chứa từ khóa đã map sẵn trong config,
mở thẳng bằng xdg-open, KHÔNG tốn lệnh gọi AI nào. Check này luôn chạy trước
khi có ý định gửi gì lên AI.
"""
import os


def match_shortcut(text: str, shortcuts: dict) -> str | None:
    """Trả về path đã match (đã expanduser) hoặc None."""
    t = text.lower().strip()
    best_key = None
    for key in shortcuts:
        k = key.lower().strip()
        if k and k in t:
            # ưu tiên khóa dài nhất khớp (tránh "mc" match nhầm khi có "server mc" cụ thể hơn)
            if best_key is None or len(k) > len(best_key):
                best_key = key
    if best_key is None:
        return None
    return os.path.expanduser(shortcuts[best_key])
