"""Tách riêng dispatch table khỏi bridge.py cho dễ test/đọc."""
import ai_client
import security
import executor
import shortcuts as shortcuts_mod


def dispatch(req: dict, config) -> dict:
    cmd = req.get("cmd")
    try:
        if cmd == "get_config":
            return {"ok": True, "data": config.data}

        if cmd == "set_config":
            config.set(req["key"], req["value"])
            return {"ok": True}

        if cmd == "match_shortcut":
            path = shortcuts_mod.match_shortcut(req["text"], config.get("shortcuts", {}))
            return {"ok": True, "data": path}

        if cmd == "ask_ai":
            brain = req.get("brain") or config.get("default_brain", "ollama")
            raw = ai_client.ask(
                brain,
                config.get("api_keys", {}),
                config.get("ollama_url", ""),
                req["history"],
                config.get("ollama_model", "llama3"),
                config.get("gemini_model", "gemini-3.6-flash"),
            )
            return {"ok": True, "data": raw}

        if cmd == "parse_ai_response":
            return {"ok": True, "data": security.parse_ai_response(req["raw"])}

        if cmd == "is_whitelisted":
            return {"ok": True, "data": security.is_whitelisted_command(req["target"])}

        if cmd == "is_dangerous":
            kw = security.is_dangerous(req["command"], config.get("blacklist", []))
            return {"ok": True, "data": kw}

        if cmd == "build_argv":
            return {"ok": True, "data": executor.build_argv(req["action"])}

        if cmd == "run_async":
            executor.run_async(req["argv"])
            return {"ok": True}

        if cmd == "run_sync":
            data = executor.run_sync(req["argv"])
            return {"ok": True, "data": data}

        if cmd == "detect_pkg_manager":
            return {"ok": True, "data": executor.detect_package_manager()}

        if cmd == "log_security_event":
            config.log_security_event(req["event"])
            return {"ok": True}

        return {"ok": False, "error": f"cmd không hợp lệ: {cmd}"}

    except Exception as e:  # bridge phải luôn trả JSON, không bao giờ để Python traceback lọt ra stdout
        return {"ok": False, "error": str(e)}
