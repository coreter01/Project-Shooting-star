# Disclaimer — Project Shooting Star

Read this file before installing or building. Installing means you have read and agree to the terms below.

## 1. Software provided "AS-IS"

No warranty of any kind, express or implied — including but not limited to fitness for
a particular purpose, freedom from bugs, or absolute safety. The author **is not liable**
for any damages (data loss, system damage, information disclosure, or other losses)
arising from the use of this software, even if advised in advance of the possibility of
such damages.

## 2. This app executes commands on your machine — understand this before using

- The app lets AI suggest actions (opening paths, running read-only inspection commands,
  installing packages) and **always requires your manual confirmation** (YES/NO) before
  running them — unless you disable the confirmation step yourself (not recommended).
- `run_command` is restricted by a fixed **whitelist** (`ls`, `df`, `ps`, ...); it does
  not run arbitrary commands. This list lives in `core/security.py` — you should read it
  yourself before trusting it, especially if you downloaded a prebuilt binary from
  someone else instead of building it from source yourself.
- `install_package` calls `pkexec` (a **system** password dialog drawn by polkit, not
  drawn by the app itself). **Only enter your password into the genuine polkit dialog** —
  never into an input field inside the app's window. If you see an unfamiliar password
  prompt inside the app's UI, that's a sign the build has been maliciously modified —
  stop, and don't type anything.
- There is no mechanism guaranteeing that the build you're running matches the public
  source 100% unless you build it from source yourself or verify the checksum yourself.

## 3. Data sent externally (third parties)

When using the Gemini / OpenAI / Anthropic "brain": chat content (including conversation
history) is sent to those providers' servers using your own API key — subject to each
provider's terms/privacy policy, which the author does not control and is not
responsible for. Using the Ollama (local) brain means no data leaves your machine.

**Do not enter into the chat any information you don't want sent to an external AI
server** (passwords, other API keys, sensitive file contents, etc.) while using a cloud
brain.

## 4. Costs

Gemini/OpenAI/Anthropic charge based on usage under your own account — the author is not
responsible for any costs incurred.

## 5. No affiliation with third parties

This project is not endorsed or sponsored by Anthropic, Google, OpenAI, or Ollama. The
names of these parties are used solely to describe integrated features.

## 6. License

See the `LICENSE` file (if present) for terms of use/copying/modification of the source
code.
