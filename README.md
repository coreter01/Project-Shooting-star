Project Shooting Star

Naming (to avoid confusion when reading the code/repository):

Project/codebase name (repo, folder, Cargo/npm package): Shooting Star — unchanged.

Official name displayed to users (title bar, application menu, .deb): Astra Assistant.

Bundle identifier: com.astaronova.astra-assistant.

AI/persona name in chat: Astra (system prompt in core/ai_client.py).

Internal snapshot/prototype name (during development, not released yet): Trợ Lý Ảo, numbered proto0, proto1, ... — does not appear in the official release.

Lazy Assistant — Tauri version. The UI shell + actual app packaging are handled by Tauri/Rust, while the processing brain is still Python (core/), kept almost entirely unchanged from the previous PySide6 version instead of being rewritten from scratch.

1. Architecture — why is it separated this way?

Frontend (HTML/CSS/JS, glassmorphism + animation)
        │  invoke("call_core", {...})
Rust (src-tauri/) — ONLY handles the shell, no business logic
        │  spawn: python3 core/bridge.py '<json>'
Python (core/) — the entire brain: AI client, security, executor, config

Whenever the frontend needs to do something (ask the AI, check whether a command is dangerous, run an action, etc.), Rust runs python3 core/bridge.py '<json request>' as a short-lived child process — not a long-running server, with no open ports, staying true to the original "does not run in the background" design.

Why not rewrite the security logic in Rust/JS? Because core/security.py and core/executor.py have already been thoroughly tested in the PySide6 version (whitelist, blacklist, JSON schema to prevent injection). Keeping them means we do not have to test everything again from scratch; we only change the presentation layer.

2. Added compared to the Qt version

Installs as a real app (npm run build produces .deb/AppImage) — no longer requires manually creating a .desktop file, and no longer suffers from the GNOME "Allow Launching" issue because the app is installed through a trusted system package.

Sliding Settings sidebar from the left (CSS transform, smooth animation) instead of opening a separate Settings window like Qt.

Glassmorphism: chat/panel frames use backdrop-filter: blur() over the background image; the blur amount (px) and overlay darkness can be adjusted in Settings.

Note: this is in-app glassmorphism (the app itself blurs the background image), NOT true transparent desktop glassmorphism (like Windows Acrylic) — Linux/GTK does not reliably support this across all compositors, so it is not used to avoid breaking the UI depending on the machine.

Custom icon (shooting star), instead of the default Qt icon.

3. Security — kept 100% from the previous version

The AI only returns JSON matching the correct schema (core/security.py::parse_ai_response) — free-form text has no execution privileges.

run_command only runs commands from the information-viewing whitelist; it does not accept arbitrary commands.

Runs through subprocess.Popen(argv_list, shell=False) — it does not go through sh -c, so &&/;/| cannot be used to chain commands.

The blacklist provides a second layer of protection for install_package.

config.json automatically uses chmod 600 and fixes its permissions if they are loosened.

Blacklisted / non-whitelisted commands are blocked → an immediate red warning is shown, with NO confirmation prompt.

Valid commands still always require manually pressing YES/NO (glassmorphism modal, not an ugly system popup).

4. Install & run (dev)

# Rust + Cargo
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# System libraries for Tauri (Debian/Ubuntu/Zorin)
sudo apt update && sudo apt install -y libwebkit2gtk-4.1-dev build-essential curl wget file \
  libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev pkexec python3

npm install
./build-sidecar.sh   # package core/ into a sidecar — run once, requires network access the first time
npm run dev

5. Build a real installable app

npm run build

The files will be generated in src-tauri/target/release/bundle/ (.deb, .AppImage, etc.). Install with sudo dpkg -i ...deb or run the AppImage directly — it will automatically have an icon in the application menu, so there is no need for a manual .desktop script anymore.

Update: switched to a sidecar. core/ is now packaged by PyInstaller into a self-contained binary (src-tauri/bin/bridge-<target-triple>), and Rust calls this binary directly instead of using python3 through PATH. The user's machine does not need Python 3 installed anymore, and there is no longer a PATH hijacking risk (a fake python3 binary being placed earlier in PATH). Run ./build-sidecar.sh once before npm run dev or npm run build (the build script already calls it automatically). A separate build is required for each CPU architecture if releasing for multiple platforms (run build-sidecar.sh on the correct target machine/architecture, or use a CI matrix).

6. Missing / things to know before release

The real build (npm run build) has not yet been tested on a machine with a display — only the Python logic through bridge.py and Rust/HTML/CSS/JS syntax have been tested.

The Python core is not bundled by default (see the note in section 5) — python3 + pip install -r requirements is required on the machine running it.

There is no clear error handling yet if python3 does not exist on the machine — it currently only returns a generic error message.

The background image uses convertFileSrc — it needs to be tested properly in Tauri dev to make sure the image path loads correctly (the mechanism differs from normal web applications).

Animation currently only exists for: the sliding sidebar, a slight "rise" animation when chat bubbles appear, and button hover effects. More can be added if you want it to feel even smoother.
