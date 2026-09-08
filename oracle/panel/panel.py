#!/usr/bin/env python3
"""
panel.py: AN2B Labs multi-vendor oracle panel runner (PILOT).

Every seat is a ClawTex-governed process. A seat's ONLY tool path is
dispatch_tool(), which routes through ClawTex's Warden under
policies/oracle_deny_all.yaml in strict mode. The engine request never
carries a tools field (asserted before every call). Forecast plaintext
never reaches stdout: only hashes and metadata do. See README.md and
DECISIONS.md beside this file; the ledger constitution is
oracle/README.md.

Subcommands
  resolve                 live engine resolution per seat (public /models)
  deny-control            watch the DENY fire under the panel policy and
                          ALLOW under the bundled default (discriminating)
  check-policy            policy file in force == committed blob
  validate FILE           schema-check a forecast JSON
  scan-keys PATH...       key-at-rest detector
  exam                    retro-calibration battery per seat (key on stdin)
  seal TR PROTOCOL        live seal at a kickoff (key on stdin)
  reveal TR               verify plaintexts against committed hashes
  score TR VERDICT        Brier-score revealed panel forecasts
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
CFG = json.loads((HERE / "seats.json").read_text(encoding="utf-8"))
POLICY = HERE / CFG["policy"]
TEMPLATE = HERE / "PROMPT_TEMPLATE.md"
LEDGER = HERE / "spend_ledger.jsonl"
CLASSES = ("PASS", "FAIL", "SPLIT", "KILL")
KEY_PATTERN = re.compile(r"sk-or-v1-[0-9a-f]{20,}")
MOCK_RATIONALE = "MOCK ENGINE canned forecast for verify.sh; never a seal"

# The retro-calibration battery: every closed TR with a published verdict.
# Verdicts are read from the published reports; TR-015's trivially fired
# KILL is coded FAIL per its report and the 2026-09-01 anchor's rule.
# `published` is the commit date of the report's first appearance.
RETRO_BATTERY = [
    {"tr": "TR-001", "protocol": "TR001_latent_corpus_callosum.md",
     "verdict": "FAIL", "published": "2026-08-26"},
    {"tr": "TR-020", "protocol": "TR020_zero_callers_for_cognition.md",
     "verdict": "SPLIT", "published": "2026-08-28"},
    {"tr": "TR-011", "protocol": "TR011_semantic_thermodynamics.md",
     "verdict": "FAIL", "published": "2026-08-31"},
    {"tr": "TR-015", "protocol": "TR015_burrows_delta_latent.md",
     "verdict": "FAIL", "published": "2026-08-31"},
    {"tr": "TR-004", "protocol": "TR004_curvature_of_meaning.md",
     "verdict": "FAIL", "published": "2026-09-02"},
    {"tr": "TR-002r", "protocol": "TR002r_platonic_replication.md",
     "verdict": "FAIL", "published": "2026-09-07"},
]


# ---------------------------------------------------------------- utilities
class PanelError(RuntimeError):
    """Any refusal. The CLI maps it to a nonzero exit."""


class ToolsForbidden(PanelError):
    pass


class ToolDenied(PanelError):
    pass


class NoExecutableTools(PanelError):
    pass


class CapReached(PanelError):
    pass


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: pathlib.Path) -> str:
    return sha256_bytes(p.read_bytes())


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, check=True,
                          capture_output=True, text=True).stdout.strip()


def git_head() -> str:
    return git("rev-parse", "HEAD")


def git_committed_sha256(path: pathlib.Path) -> str | None:
    rel = path.resolve().relative_to(REPO).as_posix()
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=REPO,
                       capture_output=True)
    if r.returncode != 0:
        return None
    return sha256_bytes(r.stdout)


def expand(p: str) -> pathlib.Path:
    return pathlib.Path(os.path.expanduser(p))


def write_private(path: pathlib.Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)
    os.chmod(path, 0o600)


def read_key_stdin() -> str:
    """The key arrives on stdin (from 1Password over ssh) and lives only
    in this process. It is never written, logged, or exported."""
    if sys.stdin.isatty():
        raise PanelError("expected the key on stdin (see inject_key.sh)")
    key = sys.stdin.readline().strip()
    if not KEY_PATTERN.fullmatch(key):
        raise PanelError("stdin did not carry an OpenRouter key of the expected shape")
    return key


# ----------------------------------------------------------- freeze + policy
def freeze_check() -> None:
    r = subprocess.run(["bash", str(REPO / "freeze" / "freeze_check.sh")],
                       cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        raise PanelError("freeze check FAILED; no seal on a moved protocol set:\n"
                         + r.stdout + r.stderr)


def check_policy(policy: pathlib.Path = POLICY) -> dict:
    """The policy in force must be byte-identical to the committed blob.
    A seal that cites a policy hash is only as good as this equality."""
    in_force = sha256_file(policy)
    committed = git_committed_sha256(policy)
    if committed is None:
        raise PanelError(f"policy {policy} is not committed at HEAD")
    if in_force != committed:
        raise PanelError("policy in force differs from the committed blob: "
                         f"{in_force[:12]} vs {committed[:12]}")
    raw = policy.read_text(encoding="utf-8")
    if not re.search(r"^default:\s*DENY\s*$", raw, re.M):
        raise PanelError("panel policy default is not DENY")
    return {"policy_path": policy.relative_to(REPO).as_posix(),
            "policy_sha256": in_force, "protocol_commit": git_head()}


# ------------------------------------------------------------------- Warden
def make_warden(policy_path: pathlib.Path, audit_dir: pathlib.Path):
    try:
        from clawtex.governance.audit_logger import AuditLogger
        from clawtex.governance.warden import Warden
    except ImportError as exc:  # a missing Warden is a failure, never a skip
        raise PanelError(f"ClawTex Warden unavailable in this interpreter: {exc}")
    audit = AuditLogger(log_dir=audit_dir)
    warden = Warden(policy_path=policy_path, mode=CFG["warden_mode"],
                    audit_logger=audit, tenant_id=CFG["tenant_id"])
    return warden, audit


def dispatch_tool(warden, seat: str, action: str, args: dict) -> None:
    """The one and only path a panel seat's tool call can take."""
    decision = warden.check(action, {"tool": action, "agent": seat, "input": args})
    if warden.enforce_decision(action, decision):
        raise ToolDenied(f"{seat}: {action} -> {decision}")
    # Even an ALLOW has nothing to run: a panel seat owns no executable tools.
    raise NoExecutableTools(f"{seat}: {action} -> {decision} (no executable tools)")


def audit_lines(audit_file: pathlib.Path) -> list[str]:
    if not audit_file.exists():
        return []
    return [ln for ln in audit_file.read_text(encoding="utf-8").splitlines() if ln.strip()]


def cmd_deny_control(args) -> dict:
    """Watch the DENY fire. Under the panel policy every probe must be
    DENIED; under ClawTex's bundled default the same probes must be
    ALLOWED, so the difference is the policy and not the harness."""
    policy = pathlib.Path(args.policy) if args.policy else POLICY
    audit_dir = expand(CFG["audit_dir"])
    audit_file = audit_dir / "warden_audit.jsonl"
    before = len(audit_lines(audit_file))
    warden, _ = make_warden(policy, audit_dir)
    probes = ["web.search", "file.read", "http.get", "exec", "memory.write"]
    seats = [s["seat"] for s in CFG["seats"]]
    observed = []
    for seat in seats:
        for action in probes:
            try:
                dispatch_tool(warden, seat, action,
                              {"query": "DENY negative control", "path": "/etc/hostname"})
                outcome = "UNREACHABLE"
            except ToolDenied:
                outcome = "DENY"
            except NoExecutableTools as exc:
                outcome = "ALLOW" if "ALLOW" in str(exc) else "REVIEW"
            observed.append({"seat": seat, "action": action, "outcome": outcome})
    after_lines = audit_lines(audit_file)
    new_lines = after_lines[before:]
    policy_sha = sha256_file(policy)
    all_deny = all(o["outcome"] == "DENY" for o in observed)
    logged = len(new_lines) == len(observed)
    record = {
        "kind": "deny_negative_control",
        "at": utc_now(),
        "policy_path": str(policy),
        "policy_sha256": policy_sha,
        "policy_is_panel_policy": policy.resolve() == POLICY.resolve(),
        "warden_mode": CFG["warden_mode"],
        "audit_file": str(audit_file),
        "probes": observed,
        "audit_excerpt": new_lines,
        "audit_excerpt_sha256": sha256_bytes("\n".join(new_lines).encode()),
        "all_denied": all_deny,
        "every_probe_logged": logged,
        "protocol_commit": git_head(),
    }
    if record["policy_is_panel_policy"]:
        record["pass"] = all_deny and logged
        out = HERE / "controls" / f"deny_control_{record['at'][:19].replace(':', '')}.json"
        if args.out:
            out = pathlib.Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, indent=1), encoding="utf-8")
        print(f"deny-control: {sum(o['outcome']=='DENY' for o in observed)}/{len(observed)} DENY, "
              f"{len(new_lines)} audit lines, policy {policy_sha[:12]}, "
              f"{'PASS' if record['pass'] else 'FAIL'} -> {out.relative_to(REPO) if out.is_relative_to(REPO) else out}")
        if not record["pass"]:
            raise PanelError("DENY negative control FAILED")
    else:
        allows = sum(o["outcome"] == "ALLOW" for o in observed)
        print(f"deny-control under NON-panel policy {policy.name}: {allows}/{len(observed)} ALLOW, "
              f"{sum(o['outcome']=='DENY' for o in observed)} DENY")
        # As a negative control this must NOT pass: the probes are reachable here.
        raise PanelError("non-panel policy lets probes through (expected; this is the discriminating leg)")
    return record


def latest_control_for(policy_sha: str) -> pathlib.Path | None:
    cands = sorted((HERE / "controls").glob("deny_control_*.json"))
    for p in reversed(cands):
        rec = json.loads(p.read_text(encoding="utf-8"))
        if rec.get("policy_sha256") == policy_sha and rec.get("pass"):
            return p
    return None


# ------------------------------------------------------------------ engines
def http_json(method: str, url: str, headers: dict | None = None,
              body: dict | None = None, timeout: int = 600) -> tuple[int, dict | None, str]:
    """Standard-library HTTP so the runner has no third-party dependency
    beyond ClawTex itself. Returns (status, parsed JSON or None, raw text)."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        status = exc.code
    try:
        return status, json.loads(raw), raw
    except json.JSONDecodeError:
        return status, None, raw


def fetch_models(gateway: str) -> list[dict]:
    status, j, raw = http_json("GET", f"{gateway}/models", timeout=30)
    if status != 200 or not j:
        raise PanelError(f"gateway /models HTTP {status}: {raw[:200]}")
    return j["data"]


def resolve_seat(seat_cfg: dict, models: list[dict]) -> dict:
    """Engine currency by live lookup, never memory (ARENA rule 2)."""
    by_id = {m["id"]: m for m in models}
    if seat_cfg.get("pin"):
        pick = by_id.get(seat_cfg["pin"])
        if pick is None:
            raise PanelError(f"pinned engine {seat_cfg['pin']} not offered by the gateway")
        cands = [pick]
    else:
        cands = [m for m in models
                 if any(fnmatch.fnmatch(m["id"], pat) for pat in seat_cfg["include"])
                 and not any(x in m["id"] for x in seat_cfg["exclude"])]
        if not cands:
            raise PanelError(f"{seat_cfg['seat']}: no candidate engine matched")
        cands.sort(key=lambda m: (-int(m.get("created", 0)), len(m["id"]), m["id"]))
        pick = cands[0]
    created = int(pick.get("created", 0))
    return {
        "seat": seat_cfg["seat"],
        "routing_alias": pick["id"],
        "canonical_slug": pick.get("canonical_slug"),
        "created_unix": created,
        "created_iso": dt.datetime.fromtimestamp(created, dt.timezone.utc).date().isoformat(),
        "knowledge_cutoff_gateway": pick.get("knowledge_cutoff"),
        "pricing_usd_per_token": {"prompt": pick.get("pricing", {}).get("prompt"),
                                  "completion": pick.get("pricing", {}).get("completion")},
        "supported_parameters": pick.get("supported_parameters", []),
        "reasoning": pick.get("reasoning"),
        "resolution_rule": "pin" if seat_cfg.get("pin") else seat_cfg["rule"],
        "candidates_considered": [m["id"] for m in cands[:8]],
        "resolved_at": utc_now(),
    }


def build_prompt(protocol_text: str) -> str:
    tpl = TEMPLATE.read_text(encoding="utf-8")
    schema = json.dumps({
        "verdict_probabilities": {"PASS": 0.0, "FAIL": 0.0, "SPLIT": 0.0, "KILL": 0.0},
        "key_effect_directions": [
            {"claim": "a directional statement tied to the protocol's own metrics",
             "probability": 0.0}],
        "rationale": "short paragraph"}, indent=2)
    return tpl.replace("{schema}", schema).replace("{protocol}", protocol_text)


def request_body(engine: dict, prompt: str) -> dict:
    s = CFG["sampling"]
    body = {
        "model": engine["routing_alias"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": s["max_tokens"],
        "usage": {"include": True},
        "response_format": {"type": "json_object"},
        "reasoning": {"effort": s["reasoning_effort"]},
    }
    sent = []
    sup = set(engine.get("supported_parameters", []))
    for p in ("temperature", "top_p", "seed"):
        if p in sup:
            body[p] = s[p]
            sent.append(p)
    body["_sampling_sent"] = sent
    assert_no_tools(body)
    return body


def assert_no_tools(body: dict) -> None:
    for k in ("tools", "tool_choice", "functions", "function_call"):
        if k in body:
            raise ToolsForbidden(f"request carries {k!r}; a panel seat is protocol-only")


def call_engine(gateway: str, key: str | None, body: dict, mock: bool) -> tuple[str, dict]:
    sent = {k: v for k, v in body.items() if not k.startswith("_")}
    assert_no_tools(sent)
    if mock:
        text = json.dumps({
            "verdict_probabilities": {"PASS": 0.2, "FAIL": 0.5, "SPLIT": 0.2, "KILL": 0.1},
            "key_effect_directions": [
                {"claim": "mock claim one", "probability": 0.6},
                {"claim": "mock claim two", "probability": 0.4},
                {"claim": "mock claim three", "probability": 0.5}],
            "rationale": MOCK_RATIONALE})
        meta = {"mock": True, "served_model": "mock", "served_provider": "mock",
                "gateway_id": None, "usage": {"prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0},
                "finish_reason": "stop", "tool_calls_in_response": 0}
        return text, meta
    headers = {"Authorization": f"Bearer {key}",
               "HTTP-Referer": "https://github.com/jcools1977/an2b-labs",
               "X-Title": "AN2B Labs oracle panel"}
    t0 = time.time()
    status, j, raw = http_json("POST", f"{gateway}/chat/completions", headers, sent)
    if status != 200 or not j:
        raise PanelError(f"gateway HTTP {status}: {raw[:300]}")
    choice = j["choices"][0]
    msg = choice.get("message", {})
    tool_calls = msg.get("tool_calls") or []
    meta = {"mock": False,
            "gateway_id": j.get("id"),
            "served_model": j.get("model"),
            "served_provider": j.get("provider"),
            "usage": j.get("usage"),
            "finish_reason": choice.get("finish_reason"),
            "tool_calls_in_response": len(tool_calls),
            "latency_s": round(time.time() - t0, 1)}
    return msg.get("content") or "", meta


def probe_cutoff(gateway: str, key: str, engine: dict, mock: bool) -> str:
    body = {"model": engine["routing_alias"],
            "messages": [{"role": "user", "content":
                          "State your training data cutoff as YYYY-MM. Reply with only that."}],
            "max_tokens": 400, "usage": {"include": True},
            "reasoning": {"effort": "low"}}
    if mock:
        return "mock"
    text, meta = call_engine(gateway, key, body, mock=False)
    record_spend({"at": utc_now(), "seat": engine["seat"], "purpose": "cutoff_probe",
                  "engine": engine["routing_alias"], "usage": meta.get("usage")})
    return text.strip()[:32]


# ---------------------------------------------------------------- forecasts
def parse_forecast(text: str) -> tuple[dict | None, str]:
    """Strict: the whole message is JSON, or a single fenced JSON block.
    Anything else fails the mechanics leg for that item. No re-roll."""
    t = text.strip()
    how = "whole_message"
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.S).strip()
        how = "fenced_block"
    try:
        return json.loads(t), how
    except json.JSONDecodeError:
        return None, "unparseable"


def validate_forecast(obj) -> list[str]:
    errs: list[str] = []
    if not isinstance(obj, dict):
        return ["not an object"]
    extra = set(obj) - {"verdict_probabilities", "key_effect_directions", "rationale"}
    if extra:
        errs.append(f"unexpected keys {sorted(extra)}")
    vp = obj.get("verdict_probabilities")
    if not isinstance(vp, dict) or set(vp) != set(CLASSES):
        errs.append("verdict_probabilities must have exactly PASS/FAIL/SPLIT/KILL")
    else:
        try:
            vals = [float(vp[c]) for c in CLASSES]
            if any(v < 0 or v > 1 for v in vals):
                errs.append("a probability is outside [0,1]")
            if abs(sum(vals) - 1.0) > 0.01:
                errs.append(f"probabilities sum to {sum(vals):.3f}, not 1")
        except (TypeError, ValueError):
            errs.append("a probability is not numeric")
    ked = obj.get("key_effect_directions")
    if not isinstance(ked, list) or len(ked) != 3:
        errs.append("key_effect_directions must list exactly three claims")
    else:
        for i, c in enumerate(ked):
            if not isinstance(c, dict) or not isinstance(c.get("claim"), str) or not c["claim"].strip():
                errs.append(f"claim {i} missing text")
            try:
                p = float(c.get("probability"))
                if p < 0 or p > 1:
                    errs.append(f"claim {i} probability outside [0,1]")
            except (TypeError, ValueError):
                errs.append(f"claim {i} probability not numeric")
    rat = obj.get("rationale")
    if not isinstance(rat, str) or not rat.strip():
        errs.append("rationale missing")
    elif len(rat) > 2000:
        errs.append("rationale over 2000 characters")
    return errs


def brier(probs: dict, outcome: str) -> float:
    return round(sum((float(probs[c]) - (1.0 if c == outcome else 0.0)) ** 2 for c in CLASSES), 4)


def modal(probs: dict) -> str:
    return max(CLASSES, key=lambda c: float(probs[c]))


def parse_cutoff(s) -> dt.date | None:
    if not s:
        return None
    m = re.search(r"(20\d\d)-(\d\d)(?:-(\d\d))?", str(s))
    if not m:
        return None
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3) or 28)
    try:
        return dt.date(y, mo, min(d, 28))
    except ValueError:
        return None


def contamination_flag(cutoff_gateway, cutoff_self, published: str) -> str:
    """Pre-registered rule (DECISIONS D7): CLEAR only when a KNOWN cutoff
    precedes publication; otherwise POSSIBLE. Unknown is treated as
    possible, the harder reading."""
    pub = dt.date.fromisoformat(published)
    known = [c for c in (parse_cutoff(cutoff_gateway), parse_cutoff(cutoff_self)) if c]
    if known and max(known) < pub:
        return "CLEAR"
    return "POSSIBLE"


# ------------------------------------------------------------------- spend
def ledger_path() -> pathlib.Path:
    return pathlib.Path(os.environ.get("PANEL_LEDGER", LEDGER))


def ledger_total() -> float:
    p = ledger_path()
    if not p.exists():
        return 0.0
    total = 0.0
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            total += float((json.loads(ln).get("usage") or {}).get("cost") or 0.0)
    return round(total, 6)


def record_spend(entry: dict) -> None:
    with open(ledger_path(), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def estimate_cost(engine: dict, prompt: str) -> float:
    pr = engine["pricing_usd_per_token"]
    pin = float(pr.get("prompt") or 0.0)
    pout = float(pr.get("completion") or 0.0)
    return len(prompt) / 3.5 * pin + CFG["sampling"]["max_tokens"] * pout


def guard(estimated_next: float) -> None:
    cap = float(CFG["spend_cap_usd"])
    spent = ledger_total()
    if spent + estimated_next > cap:
        raise CapReached(f"spend cap ${cap:.2f}: ledger ${spent:.4f} plus estimate "
                         f"${estimated_next:.4f} would exceed it; stopping before the call")


# --------------------------------------------------------- seal machinery
def out_dirs(args) -> tuple[pathlib.Path, pathlib.Path]:
    """(sealed_dir for plaintext+hash, seals_dir for records). A mock run
    must name a scratch --out; it may never touch the real directories."""
    if args.engine == "mock":
        if not args.out:
            raise PanelError("mock engine requires --out SCRATCH_DIR")
        base = pathlib.Path(args.out).resolve()
        if base.is_relative_to(REPO):
            raise PanelError("mock output must live outside the repository")
        return base / "sealed", base / "seals"
    if args.out:
        raise PanelError("--out is for mock runs only; live seals go to the repo")
    return REPO / "oracle" / "sealed", HERE / "seals"


def seal_one(gateway, key, engine, tr, protocol_path, prompt, sealed_dir, seals_dir,
             mock, supersede, control_ref, policy_meta, cutoff_self) -> dict:
    seat = engine["seat"]
    plain = sealed_dir / f"{tr}.{seat}.json"
    hashf = sealed_dir / f"{tr}.{seat}.sha256"
    rec = seals_dir / f"{tr}.{seat}.json"
    if rec.exists():
        if not supersede:
            raise PanelError(f"{rec.name} exists; one forecast per seat per seal (D6). "
                             "Use --supersede to keep it beside, labeled, never selected")
        n = 1
        while (seals_dir / f"{tr}.{seat}.superseded{n}.json").exists():
            n += 1
        rec.rename(seals_dir / f"{tr}.{seat}.superseded{n}.json")
        if plain.exists():
            plain.rename(sealed_dir / f"{tr}.{seat}.superseded{n}.json")
        if hashf.exists():
            hashf.rename(sealed_dir / f"{tr}.{seat}.superseded{n}.sha256")
    body = request_body(engine, prompt)
    guard(0.0 if mock else estimate_cost(engine, prompt))
    text, meta = call_engine(gateway, key, body, mock)
    if not mock:
        record_spend({"at": utc_now(), "seat": seat, "purpose": f"seal:{tr}",
                      "engine": engine["routing_alias"], "usage": meta.get("usage")})
    obj, how = parse_forecast(text)
    errs = validate_forecast(obj) if obj is not None else [f"forecast {how}"]
    payload = json.dumps({"seat": seat, "tr": tr, "engine": engine["routing_alias"],
                          "served_model": meta.get("served_model"),
                          "sealed_at": utc_now(), "forecast": obj,
                          "raw_text_sha256": sha256_bytes(text.encode())},
                         indent=1).encode()
    write_private(plain, payload)
    digest = sha256_bytes(payload)
    hashf.parent.mkdir(parents=True, exist_ok=True)
    hashf.write_text(f"{digest}  {plain.name}\n", encoding="utf-8")
    if not mock:
        red = expand(CFG["plaintext_redundancy_dir"]) / plain.name
        write_private(red, payload)
    record = {
        "kind": "panel_seal",
        "tr": tr,
        "seat": seat,
        "engine": engine,
        "engine_self_reported_cutoff": cutoff_self,
        "served": {k: meta.get(k) for k in ("served_model", "served_provider", "gateway_id",
                                            "finish_reason", "latency_s", "mock")},
        "usage": meta.get("usage"),
        "sampling_requested": CFG["sampling"],
        "sampling_sent": body["_sampling_sent"],
        "response_format": "json_object",
        "request_had_tools": False,
        "tool_calls_in_response": meta.get("tool_calls_in_response", 0),
        "forecast_parse": how,
        "schema_errors": errs,
        "protocol_file": protocol_path.relative_to(REPO).as_posix(),
        "protocol_sha256": sha256_file(protocol_path),
        "protocol_commit": policy_meta["protocol_commit"],
        "prompt_template_sha256": sha256_file(TEMPLATE),
        "prompt_sha256": sha256_bytes(prompt.encode()),
        "policy_path": policy_meta["policy_path"],
        "policy_sha256": policy_meta["policy_sha256"],
        "warden_mode": CFG["warden_mode"],
        "deny_control_record": control_ref,
        "plaintext_sha256": digest,
        "plaintext_path_gitignored": plain.relative_to(REPO).as_posix() if plain.is_relative_to(REPO) else str(plain),
        "sealed_at": utc_now(),
        "seal_becomes_seal_when": "hash pushed and fetched by the reviewer's channel before closeout work begins",
        "scoring": "engine-stratified; always-FAIL baseline standing; consensus reported-only",
    }
    rec.parent.mkdir(parents=True, exist_ok=True)
    rec.write_text(json.dumps(record, indent=1), encoding="utf-8")
    return record


def preflight(args) -> tuple[dict, str, str | None]:
    freeze_check()
    policy_meta = check_policy()
    control = latest_control_for(policy_meta["policy_sha256"])
    if control is None:
        raise PanelError("no passing DENY control on record for the policy in force; "
                         "run deny-control first (a deny-all that was never watched denying guards nothing)")
    key = None if args.engine == "mock" else read_key_stdin()
    return policy_meta, control.relative_to(REPO).as_posix(), key


def cmd_seal(args) -> None:
    protocol_path = (REPO / args.protocol).resolve()
    if not protocol_path.exists():
        raise PanelError(f"protocol {args.protocol} not found")
    policy_meta, control_ref, key = preflight(args)
    sealed_dir, seals_dir = out_dirs(args)
    mock = args.engine == "mock"
    models = fetch_models(CFG["gateway"])
    prompt = build_prompt(protocol_path.read_text(encoding="utf-8"))
    print(f"seal {args.tr}: protocol {protocol_path.name} sha {sha256_file(protocol_path)[:12]} "
          f"at {policy_meta['protocol_commit'][:10]}; prompt sha {sha256_bytes(prompt.encode())[:12]}; "
          f"policy {policy_meta['policy_sha256'][:12]}; control {control_ref}")
    for seat_cfg in CFG["seats"]:
        engine = resolve_seat(seat_cfg, models)
        cutoff_self = probe_cutoff(CFG["gateway"], key, engine, mock)
        rec = seal_one(CFG["gateway"], key, engine, args.tr, protocol_path, prompt,
                       sealed_dir, seals_dir, mock, args.supersede, control_ref,
                       policy_meta, cutoff_self)
        cost = (rec.get("usage") or {}).get("cost")
        print(f"  {rec['seat']:<17} {engine['routing_alias']:<32} served={rec['served']['served_model']} "
              f"via {rec['served']['served_provider']} schema_errors={len(rec['schema_errors'])} "
              f"plaintext_sha256={rec['plaintext_sha256']} cost=${cost}")
    print(f"ledger total ${ledger_total():.4f} of cap ${CFG['spend_cap_usd']:.2f}")


def cmd_exam(args) -> None:
    """Retro-calibration battery: MECHANICS are the pass bar; calibration
    numbers are the anchor, reported and never a selection criterion
    (DECISIONS D6)."""
    policy_meta, control_ref, key = preflight(args)
    mock = args.engine == "mock"
    out_dir = pathlib.Path(args.out) if args.out else HERE / "exams"
    if mock and (not args.out or pathlib.Path(args.out).resolve().is_relative_to(REPO)):
        raise PanelError("mock exam requires --out outside the repository")
    models = fetch_models(CFG["gateway"])
    seats = [s for s in CFG["seats"] if not args.seat or s["seat"] == args.seat]
    summary = []
    for seat_cfg in seats:
        engine = resolve_seat(seat_cfg, models)
        cutoff_self = probe_cutoff(CFG["gateway"], key, engine, mock)
        items = []
        mechanics_ok = True
        for item in RETRO_BATTERY:
            ppath = REPO / item["protocol"]
            prompt = build_prompt(ppath.read_text(encoding="utf-8"))
            body = request_body(engine, prompt)
            guard(0.0 if mock else estimate_cost(engine, prompt))
            text, meta = call_engine(CFG["gateway"], key, body, mock)
            if not mock:
                record_spend({"at": utc_now(), "seat": engine["seat"], "purpose": f"exam:{item['tr']}",
                              "engine": engine["routing_alias"], "usage": meta.get("usage")})
            obj, how = parse_forecast(text)
            errs = validate_forecast(obj) if obj is not None else [f"forecast {how}"]
            ok = not errs and meta.get("tool_calls_in_response", 0) == 0 and meta.get("served_model")
            mechanics_ok = mechanics_ok and bool(ok)
            rec = {"tr": item["tr"], "protocol": item["protocol"],
                   "protocol_sha256": sha256_file(ppath), "prompt_sha256": sha256_bytes(prompt.encode()),
                   "published_verdict": item["verdict"], "published": item["published"],
                   "forecast": obj, "forecast_parse": how, "schema_errors": errs,
                   "served": {k: meta.get(k) for k in ("served_model", "served_provider", "gateway_id", "finish_reason", "latency_s")},
                   "usage": meta.get("usage"), "tool_calls_in_response": meta.get("tool_calls_in_response", 0),
                   "contamination": contamination_flag(engine["knowledge_cutoff_gateway"], cutoff_self, item["published"]),
                   "mechanics_ok": bool(ok)}
            if not errs:
                vp = obj["verdict_probabilities"]
                rec["brier"] = brier(vp, item["verdict"])
                rec["modal"] = modal(vp)
                rec["modal_hit"] = rec["modal"] == item["verdict"]
                rec["always_fail_brier"] = brier({"PASS": 0, "FAIL": 1, "SPLIT": 0, "KILL": 0}, item["verdict"])
            items.append(rec)
            print(f"  {engine['seat']:<17} {item['tr']:<8} parse={how:<13} errs={len(errs)} "
                  f"brier={rec.get('brier', 'n/a')} modal={rec.get('modal', 'n/a')} "
                  f"contam={rec['contamination']} cost=${(meta.get('usage') or {}).get('cost')}")
        scored = [r for r in items if "brier" in r]
        exam = {
            "kind": "retro_calibration_exam", "label": "RETRO; zero foresight weight",
            "seat": engine["seat"], "engine": engine, "engine_self_reported_cutoff": cutoff_self,
            "at": utc_now(), "protocol_commit": policy_meta["protocol_commit"],
            "policy_sha256": policy_meta["policy_sha256"], "deny_control_record": control_ref,
            "prompt_template_sha256": sha256_file(TEMPLATE),
            "sampling_requested": CFG["sampling"], "sampling_sent": body["_sampling_sent"],
            "items": items,
            "mechanics_pass": mechanics_ok and len(items) == len(RETRO_BATTERY),
            "mean_brier": round(sum(r["brier"] for r in scored) / len(scored), 4) if scored else None,
            "mean_brier_clear_only": (round(sum(r["brier"] for r in scored if r["contamination"] == "CLEAR")
                                            / max(1, sum(r["contamination"] == "CLEAR" for r in scored)), 4)
                                      if any(r["contamination"] == "CLEAR" for r in scored) else None),
            "modal_hits": f"{sum(r.get('modal_hit', False) for r in scored)} of {len(scored)}",
            "baselines": {"uniform": 0.75,
                          "always_FAIL_mean": round(sum(r["always_fail_brier"] for r in scored) / len(scored), 4) if scored else None},
            "spend_usd": round(sum(float((r.get("usage") or {}).get("cost") or 0) for r in items), 4),
        }
        slug = (engine.get("canonical_slug") or engine["routing_alias"]).replace("/", "_")
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / f"{engine['seat']}.{slug}.json"
        out.write_text(json.dumps(exam, indent=1), encoding="utf-8")
        summary.append(exam)
        print(f"{engine['seat']}: mechanics {'PASS' if exam['mechanics_pass'] else 'FAIL'}; "
              f"mean Brier {exam['mean_brier']} (always-FAIL {exam['baselines']['always_FAIL_mean']}); "
              f"modal {exam['modal_hits']}; ${exam['spend_usd']} -> {out}")
    # Consensus column, reported only, never a headline.
    if len(summary) == len(CFG["seats"]) and all(s["mechanics_pass"] for s in summary):
        cons = []
        for i, item in enumerate(RETRO_BATTERY):
            probs = {c: sum(float(s["items"][i]["forecast"]["verdict_probabilities"][c]) for s in summary) / len(summary)
                     for c in CLASSES}
            cons.append({"tr": item["tr"], "brier": brier(probs, item["verdict"]), "modal": modal(probs)})
        (out_dir / "CONSENSUS.retro.json").write_text(json.dumps(
            {"label": "reported-only mean-probability consensus; never the headline",
             "items": cons, "mean_brier": round(sum(c["brier"] for c in cons) / len(cons), 4)}, indent=1),
            encoding="utf-8")
    print(f"ledger total ${ledger_total():.4f} of cap ${CFG['spend_cap_usd']:.2f}")


def cmd_reveal(args) -> None:
    sealed_dir = REPO / "oracle" / "sealed"
    ok = True
    for seat_cfg in CFG["seats"]:
        seat = seat_cfg["seat"]
        rec_p = HERE / "seals" / f"{args.tr}.{seat}.json"
        plain = sealed_dir / f"{args.tr}.{seat}.json"
        hashf = sealed_dir / f"{args.tr}.{seat}.sha256"
        if not rec_p.exists():
            print(f"  {seat}: no seal record (recorded as absent, never backfilled)")
            continue
        rec = json.loads(rec_p.read_text(encoding="utf-8"))
        if not plain.exists():
            red = expand(CFG["plaintext_redundancy_dir"]) / plain.name
            if red.exists():
                plain.write_bytes(red.read_bytes())
            else:
                print(f"  {seat}: plaintext missing on both paths")
                ok = False
                continue
        digest = sha256_file(plain)
        committed = hashf.read_text(encoding="utf-8").split()[0]
        match = digest == committed == rec["plaintext_sha256"]
        ok = ok and match
        print(f"  {seat}: plaintext {digest[:12]} vs committed {committed[:12]} vs record "
              f"{rec['plaintext_sha256'][:12]} -> {'MATCH' if match else 'MISMATCH'}")
    if not ok:
        raise PanelError("reveal found a mismatch")


def cmd_score(args) -> None:
    if args.verdict not in CLASSES:
        raise PanelError("verdict must be PASS, FAIL, SPLIT or KILL")
    cmd_reveal(args)
    sealed_dir = REPO / "oracle" / "sealed"
    rows = []
    for seat_cfg in CFG["seats"]:
        seat = seat_cfg["seat"]
        plain = sealed_dir / f"{args.tr}.{seat}.json"
        rec_p = HERE / "seals" / f"{args.tr}.{seat}.json"
        if not plain.exists() or not rec_p.exists():
            continue
        fc = json.loads(plain.read_text(encoding="utf-8"))["forecast"]
        rec = json.loads(rec_p.read_text(encoding="utf-8"))
        vp = fc["verdict_probabilities"]
        rows.append({"seat": seat, "engine": rec["engine"]["routing_alias"],
                     "served_model": rec["served"]["served_model"],
                     "probs": vp, "brier": brier(vp, args.verdict), "modal": modal(vp),
                     "modal_hit": modal(vp) == args.verdict, "claims": fc["key_effect_directions"]})
    if not rows:
        raise PanelError("nothing to score")
    cons = {c: sum(float(r["probs"][c]) for r in rows) / len(rows) for c in CLASSES}
    out = {"tr": args.tr, "verdict": args.verdict, "scored_at": utc_now(),
           "baselines": {"uniform": 0.75,
                         "always_FAIL": brier({"PASS": 0, "FAIL": 1, "SPLIT": 0, "KILL": 0}, args.verdict)},
           "seats": rows,
           "consensus_reported_only": {"probs": cons, "brier": brier(cons, args.verdict), "modal": modal(cons)},
           "note": "engine-stratified: each row is one seat under one served engine; never aggregate across engine changes"}
    p = HERE / "seals" / f"{args.tr}.SCORE.json"
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")
    for r in rows:
        print(f"  {r['seat']:<17} {r['engine']:<32} Brier {r['brier']:.4f} modal {r['modal']} "
              f"{'HIT' if r['modal_hit'] else 'miss'}")
    print(f"  consensus (reported only) Brier {out['consensus_reported_only']['brier']:.4f}; "
          f"always-FAIL {out['baselines']['always_FAIL']:.4f} -> {p.relative_to(REPO)}")


# ------------------------------------------------------------- small cmds
def cmd_resolve(args) -> None:
    models = fetch_models(CFG["gateway"])
    for seat_cfg in CFG["seats"]:
        e = resolve_seat(seat_cfg, models)
        print(f"{e['seat']:<17} -> {e['routing_alias']:<32} slug={e['canonical_slug']} "
              f"created={e['created_iso']} cutoff_gateway={e['knowledge_cutoff_gateway']} "
              f"rule={e['resolution_rule']}")
        print(f"{'':<17}    considered: {', '.join(e['candidates_considered'])}")


def cmd_validate(args) -> None:
    obj, how = parse_forecast(pathlib.Path(args.file).read_text(encoding="utf-8"))
    errs = validate_forecast(obj) if obj is not None else [f"forecast {how}"]
    if errs:
        raise PanelError("invalid forecast: " + "; ".join(errs))
    print(f"valid forecast ({how})")


def cmd_scan_keys(args) -> None:
    hits = []
    for root in args.paths:
        rp = expand(root)
        files = [rp] if rp.is_file() else [p for p in rp.rglob("*") if p.is_file()]
        for p in files:
            if ".git/" in p.as_posix() + "/" or p.stat().st_size > 5_000_000:
                continue
            try:
                if KEY_PATTERN.search(p.read_text(encoding="utf-8", errors="ignore")):
                    hits.append(p.as_posix())
            except OSError:
                continue
    if hits:
        raise PanelError("key-shaped material AT REST: " + ", ".join(hits))
    print(f"scan-keys: no key-shaped material under {', '.join(args.paths)}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("resolve")
    p = sub.add_parser("deny-control"); p.add_argument("--policy"); p.add_argument("--out")
    sub.add_parser("check-policy")
    p = sub.add_parser("validate"); p.add_argument("file")
    p = sub.add_parser("scan-keys"); p.add_argument("paths", nargs="+")
    for name in ("exam", "seal"):
        p = sub.add_parser(name)
        if name == "seal":
            p.add_argument("tr"); p.add_argument("protocol"); p.add_argument("--supersede", action="store_true")
        else:
            p.add_argument("--seat")
        p.add_argument("--engine", choices=["live", "mock"], default="live")
        p.add_argument("--out")
    p = sub.add_parser("reveal"); p.add_argument("tr")
    p = sub.add_parser("score"); p.add_argument("tr"); p.add_argument("verdict")
    args = ap.parse_args(argv)
    try:
        {"resolve": cmd_resolve, "deny-control": cmd_deny_control,
         "check-policy": lambda a: print(json.dumps(check_policy())),
         "validate": cmd_validate, "scan-keys": cmd_scan_keys,
         "exam": cmd_exam, "seal": cmd_seal, "reveal": cmd_reveal, "score": cmd_score}[args.cmd](args)
    except PanelError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
