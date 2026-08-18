"""
Thực thi hành động — bản vá bỏ hẳn `sh -c` + chuỗi tự do.

TRƯỚC (lỗ hổng): run_command nhận 1 string tự do, đẩy qua `sh -c "..."`.
Shell tự diễn giải &&, ;, | — nên "ls && rm -rf ~" chỉ bị blacklist chặn
nếu check đúng token "rm", còn AI/injection có thể lách bằng cách mã hoá,
chèn biến môi trường, hoặc nối lệnh theo cách blacklist chưa lường tới.

SAU (bản vá): mọi lệnh chạy qua subprocess.Popen(argv_list, shell=False).
Không có shell nào đứng giữa để diễn giải &&, ;, | — gõ 3 ký tự đó vào
target/args chỉ là ký tự thường vô hại, KHÔNG có ý nghĩa nối lệnh.
run_command bị giới hạn vào WHITELIST binary cố định (xem security.py),
không còn nhận "lệnh tự do" nữa.
"""
import subprocess
import shutil


def build_argv(action: dict) -> list[str]:
    """Chuyển action đã được duyệt (whitelist + blacklist đã pass) thành argv list."""
    atype = action["type"]
    target = action["target"]

    if atype == "open_path":
        return ["xdg-open", target]

    if atype == "run_command":
        args = action.get("args") or []
        # ép kiểu string cho từng phần tử, KHÔNG join thành 1 chuỗi shell
        return [target] + [str(a) for a in args]

    if atype == "install_package":
        pm = detect_package_manager()
        table = {
            "apt": ["pkexec", "apt-get", "install", "-y", target],
            "dnf": ["pkexec", "dnf", "install", "-y", target],
            "pacman": ["pkexec", "pacman", "-S", "--noconfirm", target],
            "zypper": ["pkexec", "zypper", "install", "-y", target],
        }
        return table.get(pm, ["echo", "Không nhận diện được trình quản lý gói trên máy này."])

    raise ValueError(f"Loại action không hợp lệ: {atype}")


def detect_package_manager() -> str:
    for pm in ("apt", "dnf", "pacman", "zypper"):
        if shutil.which(pm):
            return pm
    return "unknown"


def run_async(argv: list[str]):
    """Dùng cho open_path / install_package: không cần đọc kết quả, không chờ."""
    subprocess.Popen(
        argv,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def run_sync(argv: list[str], timeout: int = 10) -> dict:
    """Dùng cho run_command (lệnh xem-thông-tin, nhanh, whitelist-only):
    chờ và bắt output để hiển thị cho người dùng — nếu không thì chạy xong
    mà không ai biết kết quả gì, coi như vô nghĩa."""
    try:
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout[-4000:],  # giới hạn tránh spam UI nếu output khổng lồ
            "stderr": result.stderr[-2000:],
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": f"Lệnh chạy quá {timeout}s, đã bị hủy.", "exit_code": -1}
    except OSError as e:
        return {"stdout": "", "stderr": str(e), "exit_code": -1}
