# Installation — Project Shooting Star

> Read [DISCLAIMER.md](./DISCLAIMER.md) before installing.

## Option 1 — Install from a `.deb` file (recommended for regular users)

1. Download the latest `.deb` file from the Releases section.
2. Install:
   ```bash
   sudo dpkg -i shooting-star_*.deb
   # if it reports missing dependencies:
   sudo apt --fix-broken install
   ```
3. Open the app from the application menu (search "Shooting Star") — no need to install
   Python, no need to configure anything else, the sidecar is already bundled inside.
4. On first launch: go to **Settings → API Keys**, enter at least one of: Gemini/OpenAI/
   Anthropic key, or leave it blank and use local Ollama instead (see "Using Ollama"
   below).

To uninstall: `sudo apt remove shooting-star` (or the corresponding package name).

## Option 2 — Build from source (for devs / if you want to review the code yourself before trusting it)

### System requirements (Debian/Ubuntu/Zorin)

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
./build-sidecar.sh    # bundles core/ Python into a self-contained sidecar — needs network the first time
npm run build          # builds the .deb/AppImage
```

The installer will be located at `src-tauri/target/release/bundle/deb/*.deb` (and
`appimage/` if applicable).

### Run without packaging (dev mode)

```bash
./build-sidecar.sh
npm run dev
```

## Using Ollama (run AI fully locally, no API key/internet needed)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3          # or another model of your choice
ollama serve                # run in the foreground, or let systemd start it automatically
```

In the app: **Settings → API Keys**, set `Ollama URL` to `http://localhost:11434`, and
select "ollama" in the Brain field. Edit the config file if you need to change the model
name from `llama3` (the name must exactly match what `ollama list` shows).

## Common issues

| Symptom | Possible cause | Fix |
|---|---|---|
| GNOME blocks "Allow Launching" | Running the AppImage/raw file without going through the package manager | Use the `.deb` installed via `dpkg`, or `chmod +x` + right-click → Allow Launching |
| "Cannot connect to Ollama" even though it's installed | `ollama serve` isn't running, or the model name is wrong | Check the model name with `ollama list`, run `ollama serve` in the background |
| App won't reopen outside the terminal | Not installed via `.deb` (no `.desktop` entry) | Install via `.deb` instead of running the raw binary |
