#!/usr/bin/env bash
# Oracle panel negative controls (BB4C rule 3). Every leg has a red side:
# the check is exercised on an input that must FAIL, and the leg passes
# only if the failure is observed. Exits nonzero on any violation.
# Run on legion inside clawtex-env (the Warden legs need ClawTex):
#   ~/clawtex-env/bin/python -m pip list | grep clawtex
#   PANEL_PY=~/clawtex-env/bin/python oracle/panel/verify.sh
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
PY="${PANEL_PY:-python3}"
PANEL="$PY $HERE/panel.py"
SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/panel-verify.XXXXXX")"
fails=0; legs=0
pass() { legs=$((legs+1)); echo "  PASS  $1"; }
fail() { legs=$((legs+1)); fails=$((fails+1)); echo "  FAIL  $1"; }
expect_ok()   { if "$@" >/dev/null 2>&1; then return 0; else return 1; fi; }
expect_fail() { if "$@" >/dev/null 2>&1; then return 1; else return 0; fi; }
cd "$REPO"
echo "oracle panel verify: $(date -u +%Y-%m-%dT%H:%M:%SZ) at $(git rev-parse --short HEAD) with $PY"

# L1 freeze check: green on the repo, red on a mutated copy.
echo "[L1] frozen protocol manifest"
expect_ok bash freeze/freeze_check.sh && pass "freeze check green on working tree" || fail "freeze check not green"
mkdir -p "$SCRATCH/frozen"; cp TR0*.md "$SCRATCH/frozen/"
printf '\n' >> "$SCRATCH/frozen/TR006_minimum_viable_workspace.md"
FREEZE_ROOT="$SCRATCH/frozen" expect_fail bash freeze/freeze_check.sh && pass "one appended byte fails the check" || fail "mutated protocol NOT caught"
rm "$SCRATCH/frozen/TR006_minimum_viable_workspace.md"
FREEZE_ROOT="$SCRATCH/frozen" expect_fail bash freeze/freeze_check.sh && pass "a missing protocol fails the check" || fail "missing protocol NOT caught"

# L2 policy in force == committed blob; red on a modified working copy.
echo "[L2] policy hash equals committed blob"
POL="$HERE/policies/oracle_deny_all.yaml"
expect_ok $PANEL check-policy && pass "policy in force matches HEAD" || fail "policy in force does not match HEAD (commit it first?)"
cp "$POL" "$SCRATCH/policy.bak"; printf '# drift\n' >> "$POL"
expect_fail $PANEL check-policy && pass "drifted policy refused" || fail "drifted policy NOT refused"
cp "$SCRATCH/policy.bak" "$POL"
[[ "$(shasum -a 256 < "$POL")" == "$(shasum -a 256 < "$SCRATCH/policy.bak")" ]] && pass "policy restored byte-identical" || fail "policy restore mismatch"

# L3 DENY watched to fire under the panel policy; the same probes ALLOW under ClawTex's default.
echo "[L3] DENY negative control (ClawTex Warden)"
if $PANEL deny-control > "$SCRATCH/deny.out" 2>&1; then pass "every probe DENIED and logged: $(tail -1 "$SCRATCH/deny.out")"; else fail "DENY control: $(tail -1 "$SCRATCH/deny.out")"; fi
DEFAULT_POLICY="$($PY -c 'import clawtex.governance.warden as w, pathlib; print(pathlib.Path(w.__file__).parent/"policies"/"default.yaml")' 2>/dev/null || true)"
if [[ -n "$DEFAULT_POLICY" && -f "$DEFAULT_POLICY" ]]; then
  if $PANEL deny-control --policy "$DEFAULT_POLICY" > "$SCRATCH/deny_default.out" 2>&1; then
    fail "default policy unexpectedly passed the control"
  else
    grep -q "ALLOW" "$SCRATCH/deny_default.out" && pass "same probes ALLOWED under the bundled default: the control discriminates" || fail "default-policy leg did not observe ALLOW: $(tail -1 "$SCRATCH/deny_default.out")"
  fi
else
  fail "ClawTex default policy not importable; the discriminating leg could not run"
fi

# L4 schema validator: accepts the good fixture, rejects four bad ones.
echo "[L4] forecast schema validation"
$PY - "$SCRATCH" <<'PYF'
import json, sys, pathlib
d = pathlib.Path(sys.argv[1])
good = {"verdict_probabilities": {"PASS": 0.2, "FAIL": 0.5, "SPLIT": 0.2, "KILL": 0.1},
        "key_effect_directions": [{"claim": "a", "probability": 0.5}, {"claim": "b", "probability": 0.5}, {"claim": "c", "probability": 0.5}],
        "rationale": "ok"}
(d / "good.json").write_text(json.dumps(good))
bad1 = json.loads(json.dumps(good)); bad1["verdict_probabilities"]["FAIL"] = 0.8
bad2 = json.loads(json.dumps(good)); del bad2["verdict_probabilities"]["KILL"]
bad3 = json.loads(json.dumps(good)); bad3["key_effect_directions"] = bad3["key_effect_directions"][:2]
(d / "bad_sum.json").write_text(json.dumps(bad1))
(d / "bad_missing.json").write_text(json.dumps(bad2))
(d / "bad_claims.json").write_text(json.dumps(bad3))
(d / "bad_prose.json").write_text("Sure! Here is my forecast:\n" + json.dumps(good) + "\nHope this helps.")
PYF
expect_ok   $PANEL validate "$SCRATCH/good.json"        && pass "well-formed forecast accepted" || fail "good forecast rejected"
expect_fail $PANEL validate "$SCRATCH/bad_sum.json"     && pass "probabilities summing to 1.3 rejected" || fail "bad sum accepted"
expect_fail $PANEL validate "$SCRATCH/bad_missing.json" && pass "missing verdict class rejected" || fail "missing class accepted"
expect_fail $PANEL validate "$SCRATCH/bad_claims.json"  && pass "two claims rejected" || fail "two claims accepted"
expect_fail $PANEL validate "$SCRATCH/bad_prose.json"   && pass "prose around JSON rejected (no re-roll)" || fail "prose-wrapped JSON accepted"

# L5 spend guard trips at the cap, from a ledger fixture.
echo "[L5] spend cap guard"
printf '{"usage":{"cost":9.999}}\n' > "$SCRATCH/ledger.jsonl"
PANEL_LEDGER="$SCRATCH/ledger.jsonl" expect_fail $PY -c "import sys; sys.path.insert(0,'$HERE'); import panel; panel.guard(0.01)" && pass "call estimated to cross \$10 refused before the call" || fail "cap NOT enforced"
PANEL_LEDGER="$SCRATCH/ledger.jsonl" expect_ok   $PY -c "import sys; sys.path.insert(0,'$HERE'); import panel; panel.guard(0.0005)" && pass "call under the cap allowed" || fail "guard refuses under the cap"

# L6 mock seal: plaintext never on stdout; lands in a gitignored path; record fields present.
echo "[L6] plaintext custody (mock engine, scratch output)"
expect_fail $PANEL seal TR-TEST TR006_minimum_viable_workspace.md --engine mock && pass "mock without --out refused" || fail "mock without --out ran"
expect_fail $PANEL seal TR-TEST TR006_minimum_viable_workspace.md --engine mock --out "$HERE/scratch_inside_repo" && pass "mock output inside the repo refused" || fail "mock wrote inside the repo"
rm -rf "$HERE/scratch_inside_repo"
if PANEL_LEDGER="$SCRATCH/ledger2.jsonl" $PANEL seal TR-TEST TR006_minimum_viable_workspace.md --engine mock --out "$SCRATCH/mock" > "$SCRATCH/seal.out" 2>&1; then
  pass "mock seal ran: $(sed -n 2p "$SCRATCH/seal.out" | cut -c1-90)"
  if grep -q "verdict_probabilities\|MOCK ENGINE canned" "$SCRATCH/seal.out"; then fail "forecast plaintext reached stdout"; else pass "stdout carries hashes only, no forecast plaintext"; fi
  [[ -f "$SCRATCH/mock/sealed/TR-TEST.oracle-anthropic.json" ]] && pass "plaintext written to the sealed dir (mode $(stat -f %Lp "$SCRATCH/mock/sealed/TR-TEST.oracle-anthropic.json"))" || fail "plaintext not written"
  git check-ignore -q oracle/sealed/TR-TEST.oracle-anthropic.json && pass "the live plaintext path is gitignored" || fail "live plaintext path NOT gitignored"
  git check-ignore -q oracle/sealed/TR-TEST.oracle-anthropic.sha256 && fail "the hash file would be ignored (must be committed)" || pass "the hash file path is committable"
  $PY - "$SCRATCH/mock/seals/TR-TEST.oracle-openai.json" "$POL" <<'PYR'
import json, sys, hashlib
r = json.load(open(sys.argv[1])); pol = hashlib.sha256(open(sys.argv[2],'rb').read()).hexdigest()
need = ["engine","served","sampling_sent","request_had_tools","tool_calls_in_response","protocol_sha256","protocol_commit","prompt_sha256","prompt_template_sha256","policy_sha256","deny_control_record","plaintext_sha256","engine_self_reported_cutoff"]
missing = [k for k in need if k not in r]
assert not missing, f"seal record missing {missing}"
assert r["request_had_tools"] is False and r["tool_calls_in_response"] == 0
assert r["policy_sha256"] == pol, "policy hash in record != policy in force"
assert r["served"]["mock"] is True, "mock seal not labeled mock"
print("ok")
PYR
  [[ $? -eq 0 ]] && pass "seal record complete: policy hash, protocol commit, served backend, sampling, control ref, no tools" || fail "seal record incomplete"
else
  fail "mock seal refused: $(tail -1 "$SCRATCH/seal.out")"
fi

# L7 key at rest: none on the repo tree or the host's shell profiles; the detector fires on a planted fixture.
echo "[L7] key never at rest"
targets=("$REPO"); for f in ~/.zshrc ~/.zprofile ~/.zshenv ~/.bashrc ~/.bash_profile ~/.clawtex-audit ~/.clawtex-audit-oracle-panel ~/clawtex-clean/.env ~/clawtex-clean/.clawtex.toml; do [[ -e "$f" ]] && targets+=("$f"); done
expect_ok $PANEL scan-keys "${targets[@]}" && pass "no key-shaped material at rest across ${#targets[@]} targets" || fail "key-shaped material found at rest"
mkdir -p "$SCRATCH/plant"; $PY -c "print('sk-or-v1-' + '0'*64)" > "$SCRATCH/plant/.env"
expect_fail $PANEL scan-keys "$SCRATCH/plant" && pass "planted key fixture detected" || fail "detector blind to a planted key"

# L8 the request can never carry tools.
echo "[L8] protocol-only request"
expect_fail $PY -c "import sys; sys.path.insert(0,'$HERE'); import panel; panel.assert_no_tools({'model':'x','messages':[],'tools':[]})" && pass "a request with tools raises" || fail "tools in request NOT refused"
expect_ok   $PY -c "import sys; sys.path.insert(0,'$HERE'); import panel; panel.assert_no_tools(panel.request_body({'routing_alias':'x','supported_parameters':['seed']}, 'p'))" && pass "the runner's own request body carries no tools" || fail "runner request body refused"

# L9 one forecast per seat per seal (D6); supersession keeps the old one beside, labeled.
echo "[L9] no re-roll"
PANEL_LEDGER="$SCRATCH/ledger2.jsonl" expect_fail $PANEL seal TR-TEST TR006_minimum_viable_workspace.md --engine mock --out "$SCRATCH/mock" && pass "second seal for the same TR and seat refused" || fail "re-roll allowed"
PANEL_LEDGER="$SCRATCH/ledger2.jsonl" expect_ok $PANEL seal TR-TEST TR006_minimum_viable_workspace.md --engine mock --out "$SCRATCH/mock" --supersede && [[ -f "$SCRATCH/mock/seals/TR-TEST.oracle-anthropic.superseded1.json" ]] && pass "--supersede keeps the prior seal beside, labeled" || fail "supersede path broken"

echo
echo "verify: $((legs-fails))/$legs legs green; $fails failing"
rm -rf "$SCRATCH"
[[ $fails -eq 0 ]]
