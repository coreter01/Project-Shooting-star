// Project Shooting Star — vỏ Tauri.
// Rust KHÔNG chứa logic nghiệp vụ hay bảo mật nào — toàn bộ nằm ở core/*.py (Python),
// đã được PyInstaller đóng thành 1 binary tự chứa (sidecar) trong bước build.
//
// TẠI SAO SIDECAR THAY VÌ GỌI "python3" QUA PATH:
// 1. Không phụ thuộc máy người dùng có cài Python 3 + đúng package hay không.
// 2. Không bị PATH hijacking: gọi "python3" tin vào bất cứ binary nào đứng đầu
//    trong $PATH của user — nếu máy bị chèn 1 "python3" giả trước trong PATH,
//    app sẽ vô tình chạy code độc hại đó. Sidecar do Tauri resolve theo đường dẫn
//    tuyệt đối cố định trong resource đã bundle, không tra cứu PATH.
// 3. Không còn lỗi PATH rút gọn khi launch từ GUI (double-click) khác PATH terminal.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows_subsystem")]

use tauri::api::process::Command;

#[tauri::command]
fn call_core(request_json: String) -> Result<String, String> {
    let output = Command::new_sidecar("bridge")
        .map_err(|e| format!("Không tạo được sidecar 'bridge': {}", e))?
        .args([request_json])
        .output()
        .map_err(|e| format!("Không chạy được sidecar bridge: {}", e))?;

    if !output.status.success() {
        return Err(format!("bridge lỗi: {}", output.stderr));
    }
    Ok(output.stdout.trim().to_string())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![call_core])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
