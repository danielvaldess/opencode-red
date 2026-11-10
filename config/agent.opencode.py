#!/usr/bin/env python3
"""
agent.py — the engine's LLM dispatch, adapted for OpenCode.

Backends:
  - claude   : `claude -p ... --output-format json` (original behaviour)
  - opencode : `opencode run --format json --auto ...`

Select with BUGHUNTER_AGENT=claude|opencode|auto (default: auto).
OpenCode model: BUGHUNTER_OPENCODE_MODEL=provider/model (otherwise the
OpenCode default model). Optional agent: BUGHUNTER_OPENCODE_AGENT=<id>.

Agents must end with a ```json``` block; extract_json() parses it.
"""
import json
import os
import re
import shutil
import subprocess
import time

ENGINE = os.path.dirname(os.path.abspath(__file__))
MCP_CONFIG = os.path.join(ENGINE, "burp-mcp.json")
ALLOWED_TOOLS = " ".join([
    "mcp__burp__send_http1_request", "mcp__burp__send_http2_request",
    "mcp__burp__get_collaborator_interactions", "mcp__burp__generate_collaborator_payload",
    "Bash(curl:*)", "Bash(python3:*)", "Bash(jq:*)", "Bash(openssl:*)", "Bash(base64:*)",
])


def _backend() -> str:
    b = os.environ.get("BUGHUNTER_AGENT", "auto").strip().lower()
    if b in ("claude", "opencode"):
        return b
    if shutil.which("claude"):
        return "claude"
    if shutil.which("opencode"):
        return "opencode"
    return "none"


def _run_opencode(task, model, timeout):
    cmd = ["opencode", "run", "--format", "json", "--auto"]
    m = os.environ.get("BUGHUNTER_OPENCODE_MODEL") or model
    if m and "/" in m:                      # OpenCode requires provider/model
        cmd += ["-m", m]
    agent = os.environ.get("BUGHUNTER_OPENCODE_AGENT")
    if agent:
        cmd += ["--agent", agent]
    cmd.append(task)
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"result": "", "error": "timeout", "duration_s": round(time.time() - t0, 1)}
    except (FileNotFoundError, OSError) as e:
        return {"result": "", "error": f"exec:{e}", "duration_s": round(time.time() - t0, 1)}

    texts, cost, turns, last_error = [], 0.0, 0, None
    for line in (p.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        et = ev.get("type")
        part = ev.get("part") or {}
        if et == "text" and part.get("type") == "text":
            texts.append(part.get("text") or "")
        elif et == "step_finish":
            cost += float(ev.get("cost") or 0.0)
            turns += 1
        elif et == "error":
            last_error = str(ev.get("error") or ev)[:300]
    result = "\n".join(t for t in texts if t).strip()
    if last_error and not result:
        return {"result": "", "error": f"opencode:{last_error}", "duration_s": round(time.time() - t0, 1)}
    if not result and p.returncode != 0:
        return {"result": "", "error": f"exec:rc={p.returncode} {(p.stderr or '')[:200]}",
                "duration_s": round(time.time() - t0, 1)}
    low = result.lower()
    if "usage limit" in low or "session limit" in low:
        return {"result": result, "error": "rate-limited", "duration_s": round(time.time() - t0, 1)}
    return {"result": result, "cost_usd": round(cost, 6), "num_turns": turns,
            "error": None, "duration_s": round(time.time() - t0, 1)}


def _run_claude(task, skills_on, model, max_turns, timeout):
    cmd = ["claude", "-p", task,
           "--mcp-config", MCP_CONFIG, "--strict-mcp-config",
           "--permission-mode", "bypassPermissions",
           "--allowedTools", ALLOWED_TOOLS,
           "--max-turns", str(max_turns), "--model", model,
           "--output-format", "json"]
    if not skills_on:
        cmd.append("--disable-slash-commands")
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"result": "", "error": "timeout", "duration_s": round(time.time() - t0, 1)}
    except (FileNotFoundError, OSError) as e:
        return {"result": "", "error": f"exec:{e}", "duration_s": round(time.time() - t0, 1)}
    try:
        d = json.loads(p.stdout)
        res = d.get("result") or ""
        if "usage limit" in res.lower() or "session limit" in res.lower():
            return {"result": res, "error": "rate-limited", "duration_s": round(time.time() - t0, 1)}
        return {"result": res, "cost_usd": d.get("total_cost_usd"),
                "num_turns": d.get("num_turns"), "error": None,
                "duration_s": round(time.time() - t0, 1)}
    except Exception as e:
        return {"result": p.stdout[:300], "error": f"parse:{e}", "duration_s": round(time.time() - t0, 1)}


def run_agent(task, skills_on=False, model="claude-sonnet-4-6", max_turns=40, timeout=600):
    backend = _backend()
    if backend == "opencode":
        return _run_opencode(task, model, timeout)
    if backend == "claude":
        return _run_claude(task, skills_on, model, max_turns, timeout)
    return {"result": "", "error": "exec:no agent CLI (claude/opencode) found",
            "duration_s": 0}


def extract_json(text):
    """Pull the last valid JSON array/object out of an agent reply."""
    if not text:
        return None
    blocks = re.findall(r"```json\s*(.*?)```", text, re.S)
    blocks += re.findall(r"```\s*(\[.*?\]|\{.*?\})\s*```", text, re.S)
    for b in reversed(blocks):
        try:
            return json.loads(b.strip())
        except Exception:
            pass
    for b in reversed(re.findall(r"(\[.*\]|\{.*\})", text, re.S)):
        try:
            return json.loads(b)
        except Exception:
            pass
    return None


if __name__ == "__main__":
    assert extract_json('blah ```json\n[{"a":1}]\n``` end') == [{"a": 1}]
    assert extract_json('text {"x": "y"} more') == {"x": "y"}
    assert extract_json("no json here") is None
    assert extract_json('first {"a":1} then ```json\n{"b":2}\n```') == {"b": 2}
    print("agent.py extractor self-test: PASS")
