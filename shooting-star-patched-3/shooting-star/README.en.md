# Project Shooting Star

> **About the naming** (to avoid confusion when reading the code/repo):
> - **Project/codebase name** (repo, folder, Cargo/npm package): `Shooting Star` — unchanged.
> - **Official name shown to users** (title bar, application menu, .deb): `Astra Assistant`.
> - **Bundle identifier**: `com.astaronova.astra-assistant`.
> - **AI/persona name in chat**: `Astra` (system prompt in `core/ai_client.py`).
> - **Internal dev snapshot/prototype name** (during development, not yet released): `Trợ Lý Ảo`, numbered `proto0`, `proto1`, ... — does not appear in the official release.

Trợ Lý Siêu Lười — Tauri edition. A real app shell + packaging (Tauri/Rust), with the processing "brain" still in Python (`core/`), kept nearly unchanged from the previous PySide6 version rather than rewritten from scratch.

## 1. Architecture — why split it this way?

```
Frontend (HTML/CSS/JS, frosted glass + animation)
        │  invoke("call_core", {...})
Rust (src-tauri/) — SHELL ONLY, no business logic
        │  spawn: python3 core/bridge.py '<json>'
Python (core/) — the entire brain: AI client, security, executor, config
```

Every time the frontend needs to do something (ask the AI, check whether a command is
dangerous, run an action, etc.), Rust runs `python3 core/bridge.py '<json request>'` as
**one short-lived child process** — not a long-running server, no open ports, staying
true to the "nothing runs in the background" principle from the start.

Why not rewrite the security logic in Rust/JS? Because `core/security.py` and
`core/executor.py` were already thoroughly tested in the PySide6 version (whitelist,
blacklist, JSON schema against injection) — they're kept as-is so they don't need to be
re-tested from scratch; only the display layer changes.

## 2. What's new compared to the Qt version

- **Installs as a real app** (`npm run build` produces a `.deb`/AppImage) — no more
  manually creating a `.desktop` file, and no more GNOME "Allow Launching" issue since
  the app is installed through a trusted system package.
- **Settings sidebar slides in from the left** (CSS transform, smooth animation)
  instead of opening a separate Settings window like in Qt.
- **Frosted glass (glassmorphism)**: chat/panel frames use `backdrop-filter: blur()`
  over a background image, with blur amount (px) and overlay darkness adjustable in
  Settings.
  - Note: this is frosted glass **within the app** (blurring a background image the app
    draws itself), NOT true desktop-level see-through blur (like Windows Acrylic) —
    Linux/GTK doesn't reliably support that across every compositor, so it was left out
    to avoid breaking the UI depending on the machine.
- Custom icon (a shooting star), no longer the default Qt icon.

## 3. Security — kept 100% unchanged from the previous version

- The AI only returns JSON matching a fixed schema (`core/security.py::parse_ai_response`)
  — free-form text has no execution rights.
- `run_command` only runs commands from a fixed whitelist of read-only inspection
  commands; it does not accept arbitrary commands.
- Execution goes through `subprocess.Popen(argv_list, shell=False)` — not through
  `sh -c`, so `&&`/`;`/`|` have no command-chaining meaning.
- A blacklist acts as a second line of defense for `install_package`.
- `config.json` is automatically `chmod 600`'d, and self-corrected if its permissions
  are loosened.
- Anything matching the blacklist or not on the whitelist → an immediate red warning,
  with NO confirmation prompt (it's simply blocked).
- Valid commands still always require a manual YES/NO click (a frosted-glass modal, not
  an ugly system popup).

## 4. Install & run (dev)

```bash
# Rust + Cargo
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# System libraries for Tauri (Debian/Ubuntu/Zorin)
sudo apt update && sudo apt install -y libwebkit2gtk-4.1-dev build-essential curl wget file \
  libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev pkexec python3

npm install
./build-sidecar.sh   # bundles core/ into a sidecar — run once, needs network the first time
npm run dev
```

## 5. Build a real installable app

```bash
npm run build
```
Output files appear in `src-tauri/target/release/bundle/` (`.deb`, `.AppImage`, etc.).
Install with `sudo dpkg -i ...deb` or run the AppImage directly — it will automatically
have an icon in the application menu, no manual `.desktop` script needed anymore.

**Update: switched to a sidecar.** `core/` is now packaged by PyInstaller into a single
self-contained binary (`src-tauri/bin/bridge-<target-triple>`), and Rust calls this
binary directly instead of `python3` via PATH. End users **no longer need to install
Python 3**, and there's no longer a PATH-hijacking risk (a fake binary named `python3`
inserted earlier in PATH). Run `./build-sidecar.sh` **once before** `npm run dev` or
`npm run build` (the `build` script already calls it automatically). You'll need to
build separately for each CPU architecture if releasing cross-platform (run
`build-sidecar.sh` on the matching target machine/architecture, or use a CI matrix).

## 6. Still missing / good to know before release

- Real build (`npm run build`) hasn't been tested yet on a machine with a display —
  only the Python logic via bridge.py and the Rust/HTML/CSS/JS syntax have been tested
  so far.
- The Python core isn't bundled yet (see note in section 5) — `python3` +
  `pip install -r requirements` are still required on the machine running it.
- There's no clear error handling yet if `python3` doesn't exist on the machine — it
  currently just returns a generic text error.
- Background images use `convertFileSrc` — needs real testing in Tauri dev to make sure
  image paths load correctly (the mechanism differs from a regular web app).
- Animations currently only cover: sidebar sliding, a light "rise" effect on chat
  bubbles when they appear, and button hover. More can be added if you want it smoother.
