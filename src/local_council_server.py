"""HACK-008: localhost-only interactive evidence-gated FAITH scientific council.

Usage:
  python -X utf8 src/local_council_server.py --evidence <local-evidence.json>
Open printed localhost URL in Edge. This serves only 127.0.0.1.

- 0 model calls on page load, question preparation and evidence inspection.
- Each real run requires an explicit consent checkbox, a server-side key, and a
  locally bound anti-CSRF token. At most 4 calls per run (2 Spark perspectives,
  1 Wonder critique, 1 Spark synthesis).
- Every answer must pass independent FSDC gates before any later call.
- Durable private run checkpoints after every attempt; no auto retry.
- No browser access to API keys or arbitrary local files.
"""
import argparse
import datetime as dt
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import re
from pathlib import Path
import secrets
import sys
import threading
import traceback
from urllib.parse import urlparse, parse_qs

from council import SPARK, WONDER, meta_call
from verified_council import PROMPT, prepare
from verification import verify_submission

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
UI = ROOT / "ui" / "hack008.html"
QUESTION_LIMIT = 1800
MAX_BODY = 8192
AGENT_LIMIT = 2

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def make_plan(question, evidence):
    job = prepare(question, evidence, "mining", "Boké, Guinea")
    return job

def safe_text(raw):
    if not isinstance(raw, str):
        raise ValueError("Model did not return text")
    return raw

def save_trace(trace, directory):
    """Write full local-only trace with model answers, never credentials."""
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (trace["run_id"] + ".json")
    staging = directory / (trace["run_id"] + ".tmp")
    staging.write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    staging.replace(target)
    return target

def perform_run(question, evidence, key, run_id, out_dir, caller=meta_call, on_update=None):
    job = make_plan(question, evidence)
    trace = {
        "run_id": run_id, "started_utc": now(), "question": question,
        "geography": "Boké, Guinea", "sector": "mining",
        "status": "PREPARING", "evidence_sha256": job["gate"]["evidence_sha256"],
        "scientific_status": job["gate"]["status"],
        "source_ids": [e["evidence_id"] for e in job["gate"]["evidence"]],
        "selected_agents": job["proposers"][:AGENT_LIMIT],
        "human_review_required": True, "calls_attempted": 0,
        "steps": [], "warnings": [
            "Only two agent perspectives executed; not a complete eight-stakeholder council.",
            "Exploratory, NOT_FIELD_VALIDATED evidence cannot justify impact or investment approval.",
            "Exact citation matching is not external scientific verification.",
        ]
    }
    def update(status):
        trace["status"] = status
        trace["updated_utc"] = now()
        save_trace(trace, out_dir)
        if on_update:
            on_update(json.loads(json.dumps(trace, ensure_ascii=False)))
    update("STARTED")
    if not job["gate"]["evidence"]:
        update("ABSTAIN_NO_USABLE_EVIDENCE")
        return trace
    if not key:
        update("BLOCKED_MISSING_MODEL_API_KEY")
        return trace
    base = {
        "question": question, "geography": "Boké, Guinea",
        "sector": "mining", "evidence": job["gate"]["evidence"],
        "evidence_sha256": job["gate"]["evidence_sha256"],
        "warning": "Exploratory evidence; no verified causal impacts or investment approval."
    }
    def call(role, model, payload):
        trace["calls_attempted"] += 1
        index = trace["calls_attempted"]
        step = {"role": role, "model": model, "status": "REQUEST_STARTED",
                "started_utc": now(), "call_index": index}
        trace["steps"].append(step)
        update("RUNNING_" + role.upper())
        instruction = PROMPT + "\nAnalytical role: " + role + (
            "\nYou must challenge weaknesses in the other positions, preserve uncertainty and abstentions."
            if role == "scientific_critic" else
            "\nProvide decision-support investigations and abstentions, not an investment approval."
        )
        try:
            raw = safe_text(caller(model, instruction, payload, key))
        except Exception as exc:
            step["status"] = "CALL_FAILED_DO_NOT_RETRY_BLINDLY"
            step["error_type"] = type(exc).__name__
            step["error_message"] = str(exc)[:180]
            update("STOPPED_CALL_FAILURE")
            return None
        step["raw_model_text"] = raw
        verdict = verify_submission(raw, job["gate"]["evidence"], job["gate"]["evidence_sha256"])
        step["verification_status"] = verdict["status"]
        step["verification_issues"] = verdict["issues"]
        step["status"] = "ACCEPTED_STRUCTURAL_ONLY" if verdict["verified"] else "BLOCKED_BY_VERIFIER"
        step["checked_publication"] = verdict.get("publication")
        step["finished_utc"] = now()
        update("CHECKED_" + role.upper())
        if not verdict["verified"]:
            update("STOPPED_VERIFICATION_BLOCK")
            return None
        return verdict["publication"]
    positions = []
    for role in job["proposers"][:AGENT_LIMIT]:
        p = call(role, SPARK, base)
        if p is None:
            return trace
        positions.append({"role": role, "checked_publication": p})
    critique = call("scientific_critic", WONDER, {**base, "verified_positions": positions})
    if critique is None:
        return trace
    revision = call("final_synthesis", SPARK, {
        **base, "verified_positions": positions, "verified_critique": critique
    })
    if revision is None:
        return trace
    trace["decision_support"] = revision
    update("COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED")
    return trace

class App(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, port, evidence, out_dir, caller=meta_call):
        super().__init__(("127.0.0.1", port), Handler)
        self.evidence = evidence
        self.out_dir = out_dir
        self.caller = caller
        self.token = secrets.token_urlsafe(32)
        self.jobs = {}
        self.job_lock = threading.Lock()
        self.running = False

def read_session_file(directory, run_id):
    if not re.fullmatch(r"HACK008-[A-Za-z0-9_-]{10,80}", run_id):
        return None
    path = directory / (run_id + ".json")
    if not path.is_file() or path.stat().st_size > 2_000_000:
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) and value.get("run_id") == run_id else None
    except (OSError, ValueError, UnicodeDecodeError):
        return None

class Handler(BaseHTTPRequestHandler):
    server: App
    def log_message(self, fmt, *args):
        # avoid printing URLs/questions/private values to terminal
        return
    def send_json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def same_origin(self):
        origin = self.headers.get("Origin")
        return origin in (None, f"http://127.0.0.1:{self.server.server_port}")
    def do_GET(self):
        route = urlparse(self.path)
        if route.path == "/":
            page = UI.read_text(encoding="utf-8").replace("__SESSION_TOKEN__", self.server.token)
            data = page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self'; media-src blob:; base-uri 'none'; form-action 'none'")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif route.path == "/api/status":
            if self.headers.get("X-Terra-Token") != self.server.token:
                return self.send_json(403, {"error": "token_required"})
            run_id = parse_qs(route.query).get("id", [""])[0]
            with self.server.job_lock:
                trace = self.server.jobs.get(run_id)
                payload = json.loads(json.dumps(trace)) if trace else None
            if payload is None:
                payload = read_session_file(self.server.out_dir, run_id)
            self.send_json(200 if payload else 404, payload or {"error": "unknown_run"})
        elif route.path == "/api/sessions":
            if self.headers.get("X-Terra-Token") != self.server.token:
                return self.send_json(403, {"error": "token_required"})
            items = []
            if self.server.out_dir.is_dir():
                for item in sorted(self.server.out_dir.glob("HACK008-*.json"),
                                   key=lambda f: f.stat().st_mtime, reverse=True)[:25]:
                    trace = read_session_file(self.server.out_dir, item.stem)
                    if trace:
                        items.append({"run_id": trace["run_id"], "status": trace.get("status"),
                                      "question": trace.get("question", ""),
                                      "calls_attempted": trace.get("calls_attempted", 0)})
            self.send_json(200, {"sessions": items})
        elif route.path == "/api/pdf":
            if self.headers.get("X-Terra-Token") != self.server.token:
                return self.send_json(403, {"error": "token_required"})
            run_id = parse_qs(route.query).get("id", [""])[0]
            with self.server.job_lock:
                trace = self.server.jobs.get(run_id)
                snapshot = json.loads(json.dumps(trace)) if trace else None
            if snapshot is None:
                snapshot = read_session_file(self.server.out_dir, run_id)
            if not snapshot or snapshot.get("status") != "COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED":
                return self.send_json(409, {"error": "complete_verified_session_required"})
            try:
                from export_decision_pdf import validate_session
                from executive_brief_v3 import export_v3, VERSION
                record = validate_session(snapshot, self.server.evidence)
                target = self.server.out_dir / (run_id + "-Executive-Brief-V3.pdf")
                if not target.exists():
                    export_v3(record, target)
                content = target.read_bytes()
            except (ValueError, RuntimeError, OSError, ImportError, KeyError, TypeError) as exc:
                return self.send_json(500, {"error": "pdf_generation_failed", "detail": str(exc)[:170]})
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", "attachment; filename=TerraCouncil-Executive-Brief-V3.pdf")
            self.send_header("X-Terra-Pdf-Version", VERSION)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif route.path == "/api/chamber":
            if self.headers.get("X-Terra-Token") != self.server.token:
                return self.send_json(403, {"error": "token_required"})
            run_id = parse_qs(route.query).get("id", [""])[0]
            with self.server.job_lock:
                trace = self.server.jobs.get(run_id)
                snapshot = json.loads(json.dumps(trace)) if trace else None
            if snapshot is None:
                snapshot = read_session_file(self.server.out_dir, run_id)
            if not snapshot or snapshot.get("status") != "COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED":
                return self.send_json(409, {"error": "complete_verified_session_required"})
            try:
                from chamber_visuals import visual_cues
                data = visual_cues(snapshot, self.server.evidence)
            except (ValueError, KeyError, TypeError, ImportError) as exc:
                return self.send_json(422, {"error": "chamber_unavailable", "detail": str(exc)[:180]})
            return self.send_json(200, data)
        elif route.path in ("/api/voice-status", "/api/voice-audio", "/api/voice-timing"):
            if self.headers.get("X-Terra-Token") != self.server.token:
                return self.send_json(403, {"error":"token_required"})
            run_id=parse_qs(route.query).get("id",[""])[0]
            snapshot=read_session_file(self.server.out_dir,run_id)
            if not snapshot or snapshot.get("status")!="COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED":
                return self.send_json(409, {"error":"complete_saved_session_required"})
            from voice_workflow import status,read_audio
            try:
                if route.path=="/api/voice-status":
                    state=status(self.server.out_dir,run_id)
                    state["key_available"]=bool(os.environ.get("ELEVENLABS_API_KEY"))
                    return self.send_json(200,state)
                content=read_audio(self.server.out_dir,run_id,
                    "audio" if route.path=="/api/voice-audio" else "timing")
            except (ValueError,OSError) as exc:
                return self.send_json(409,{"error":"voice_unavailable","detail":str(exc)[:120]})
            media="audio/mpeg" if route.path=="/api/voice-audio" else "application/json; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type",media)
            self.send_header("Cache-Control","no-store")
            self.send_header("Content-Length",str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif route.path == "/api/oral-draft":
            if self.headers.get("X-Terra-Token") != self.server.token:
                return self.send_json(403, {"error": "token_required"})
            run_id = parse_qs(route.query).get("id", [""])[0]
            with self.server.job_lock:
                trace = self.server.jobs.get(run_id)
                snapshot = json.loads(json.dumps(trace)) if trace else None
            if snapshot is None:
                snapshot = read_session_file(self.server.out_dir, run_id)
            if not snapshot or snapshot.get("status") != "COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED":
                return self.send_json(409, {"error": "complete_verified_session_required"})
            try:
                from natural_french_dialogue import oral_storyboard
                draft = oral_storyboard(snapshot, self.server.evidence)
            except (ValueError, KeyError, TypeError, ImportError) as exc:
                return self.send_json(422, {"error": "oral_draft_unavailable", "detail": str(exc)[:180]})
            return self.send_json(200, draft)
        elif route.path == "/api/oral-manifest":
            if self.headers.get("X-Terra-Token") != self.server.token:
                return self.send_json(403, {"error": "token_required"})
            run_id = parse_qs(route.query).get("id", [""])[0]
            with self.server.job_lock:
                trace = self.server.jobs.get(run_id)
                snapshot = json.loads(json.dumps(trace)) if trace else None
            if snapshot is None:
                snapshot = read_session_file(self.server.out_dir, run_id)
            if not snapshot or snapshot.get("status") != "COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED":
                return self.send_json(409, {"error": "complete_verified_session_required"})
            try:
                from natural_french_dialogue import oral_storyboard
                manifest = oral_storyboard(snapshot, self.server.evidence)
            except (ValueError, KeyError, TypeError, ImportError) as exc:
                return self.send_json(422, {"error": "oral_manifest_not_available", "detail": str(exc)[:150]})
            content = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=TerraCouncil-Oral-Draft.json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif route.path == "/api/oral-review":
            if self.headers.get("X-Terra-Token") != self.server.token:
                return self.send_json(403, {"error": "token_required"})
            run_id = parse_qs(route.query).get("id", [""])[0]
            with self.server.job_lock:
                trace = self.server.jobs.get(run_id)
                snapshot = json.loads(json.dumps(trace)) if trace else None
            if snapshot is None:
                snapshot = read_session_file(self.server.out_dir, run_id)
            if not snapshot or snapshot.get("status") != "COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED":
                return self.send_json(409, {"error": "complete_verified_session_required"})
            try:
                from natural_french_dialogue import oral_storyboard
                manifest = oral_storyboard(snapshot, self.server.evidence)
                parts = [
                    "TERRACOUNCIL — SCRIPT ORAL À RELIRE",
                    "Reconstruction éditoriale en français, NON VERBATIM.",
                    "Aucune génération audio ou validation scientifique implicite.",
                    "Session : " + manifest["session_id"], ""
                ]
                for turn in manifest["turns"]:
                    parts.extend([turn["speaker"].upper(), turn["text_to_review"], ""])
                parts.append("Relecture humaine obligatoire avant tout appel ElevenLabs.")
                content = ("\n".join(parts) + "\n").encode("utf-8")
            except (ValueError, KeyError, TypeError, ImportError) as exc:
                return self.send_json(422, {"error": "oral_script_not_available", "detail": str(exc)[:150]})
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=TerraCouncil-Oral-Review.txt")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif route.path == "/api/context":
            if self.headers.get("X-Terra-Token") != self.server.token:
                return self.send_json(403, {"error": "token_required"})
            sample = make_plan("Quelles investigations prioriser à Boké ?", self.server.evidence)
            self.send_json(200, {
                "status": sample["status"], "evidence_sha256": sample["gate"]["evidence_sha256"],
                "evidence": sample["gate"]["evidence"], "available_agents": sample["proposers"],
                "executed_agents_per_run": sample["proposers"][:AGENT_LIMIT],
                "planned_calls_per_run": min(AGENT_LIMIT, len(sample["proposers"])) + 2 if sample["gate"]["evidence"] else 0,
                "api_key_available": bool(os.environ.get("MODEL_API_KEY")),
                "model_calls": 0
            })
        else:
            self.send_json(404, {"error": "not_found"})
    def do_POST(self):
        if self.path == "/api/voice-start":
            if not self.same_origin() or self.headers.get("X-Terra-Token")!=self.server.token:
                return self.send_json(403,{"error":"origin_or_token_rejected"})
            if self.headers.get("Content-Type","").split(";")[0].strip()!="application/json":
                return self.send_json(415,{"error":"json_required"})
            try:
                n=int(self.headers.get("Content-Length","0"))
            except ValueError:
                n=0
            if not 1<=n<=4000:
                return self.send_json(413,{"error":"invalid_request_size"})
            try:
                request_data=json.loads(self.rfile.read(n))
            except (ValueError,UnicodeDecodeError):
                return self.send_json(400,{"error":"bad_json"})
            if not isinstance(request_data,dict) or request_data.get("approve_cost_and_sharing") is not True:
                return self.send_json(403,{"error":"separate_paid_voice_consent_required"})
            run_id=request_data.get("run_id")
            if not isinstance(run_id,str):
                return self.send_json(400,{"error":"invalid_session"})
            trace=read_session_file(self.server.out_dir,run_id)
            if not trace or trace.get("status")!="COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED":
                return self.send_json(409,{"error":"complete_saved_session_required"})
            from voice_workflow import status,verified_approval,attempt
            try:
                if status(self.server.out_dir,run_id)["state"]!="NOT_REQUESTED":
                    return self.send_json(409,{"error":"voice_attempt_already_recorded_do_not_retry"})
                verified_approval(self.server.out_dir,run_id,trace,self.server.evidence)
                key=os.environ.get("ELEVENLABS_API_KEY","")
                spark_voice=os.environ.get("TERRA_VOICE_SPARK","")
                wonder_voice=os.environ.get("TERRA_VOICE_WONDER","")
                if not key or not spark_voice or not wonder_voice:
                    return self.send_json(409,{"error":"voice_credentials_missing_restart_server_with_key"})
                # Single run at a time. No repeat if user double-clicks.
                with self.server.job_lock:
                    if getattr(self.server,"voice_running",False):
                        return self.send_json(409,{"error":"voice_generation_in_progress"})
                    self.server.voice_running=True
                def worker():
                    try:
                        attempt(self.server.out_dir,run_id,trace,self.server.evidence,
                                key,spark_voice,wonder_voice)
                    finally:
                        with self.server.job_lock:
                            self.server.voice_running=False
                threading.Thread(target=worker,daemon=True).start()
                return self.send_json(202,{"state":"ATTEMPT_ACCEPTED","session_id":run_id,
                                           "max_paid_voice_calls":1})
            except (ValueError,TypeError,KeyError,OSError) as exc:
                return self.send_json(422,{"error":"voice_not_started","detail":str(exc)[:150]})
        if self.path == "/api/oral-approve":
            if not self.same_origin() or self.headers.get("X-Terra-Token") != self.server.token:
                return self.send_json(403, {"error": "origin_or_token_rejected"})
            if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                return self.send_json(415, {"error": "json_required"})
            try:
                count = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                count = 0
            if not 1 <= count <= 14000:
                return self.send_json(413, {"error": "invalid_request_size"})
            try:
                request_data = json.loads(self.rfile.read(count))
            except (ValueError, UnicodeDecodeError):
                return self.send_json(400, {"error": "bad_json"})
            if not isinstance(request_data, dict) or request_data.get("reviewed_meaning") is not True:
                return self.send_json(403, {"error": "explicit_human_review_required"})
            run_id = request_data.get("run_id", "")
            if not isinstance(run_id, str):
                return self.send_json(400, {"error": "invalid_session"})
            with self.server.job_lock:
                trace = self.server.jobs.get(run_id)
                snapshot = json.loads(json.dumps(trace)) if trace else None
            if snapshot is None:
                snapshot = read_session_file(self.server.out_dir, run_id)
            if not snapshot or snapshot.get("status") != "COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED":
                return self.send_json(409, {"error": "complete_session_required"})
            try:
                from approve_oral_script import reviewed_manifest
                manifest = reviewed_manifest(request_data.get("draft"), snapshot, self.server.evidence)
                target_dir = self.server.out_dir / "Approved-Oral-Reviews"
                target_dir.mkdir(parents=True, exist_ok=True)
                target = target_dir / (run_id + "-" + manifest["script_sha256"][:16] + "-approved.json")
                if target.exists():
                    return self.send_json(409, {"error": "already_approved", "script_sha256": manifest["script_sha256"]})
                with target.open("x", encoding="utf-8") as output:
                    json.dump(manifest, output, ensure_ascii=False, indent=2)
                    output.write(chr(10))
                return self.send_json(201, {
                    "status": "EDITORIAL_APPROVED_NOT_FIELD_VALIDATED",
                    "session_id": run_id,
                    "script_sha256": manifest["script_sha256"],
                    "saved_filename": target.name,
                    "external_api_calls": 0
                })
            except (ValueError, KeyError, TypeError, OSError) as exc:
                return self.send_json(422, {"error": "oral_approval_failed", "detail": str(exc)[:170]})
        if self.path != "/api/run":
            return self.send_json(404, {"error": "not_found"})
        if not self.same_origin() or self.headers.get("X-Terra-Token") != self.server.token:
            return self.send_json(403, {"error": "origin_or_token_rejected"})
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            return self.send_json(415, {"error": "json_required"})
        try:
            n = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            n = 0
        if n < 1 or n > MAX_BODY:
            return self.send_json(413, {"error": "invalid_request_size"})
        try:
            request_data = json.loads(self.rfile.read(n))
        except (ValueError, UnicodeDecodeError):
            return self.send_json(400, {"error": "bad_json"})
        if not isinstance(request_data, dict):
            return self.send_json(400, {"error": "json_object_required"})
        question = request_data.get("question", "")
        if not isinstance(question, str) or not question.strip() or len(question) > QUESTION_LIMIT:
            return self.send_json(400, {"error": "question_invalid"})
        if request_data.get("consent") is not True or request_data.get("reviewed_sharing") is not True:
            return self.send_json(403, {"error": "explicit_meta_and_data_sharing_approval_required"})
        job = make_plan(question, self.server.evidence)
        if not job["gate"]["evidence"]:
            return self.send_json(422, {"error": "no_usable_evidence"})
        key = os.environ.get("MODEL_API_KEY", "")
        if not key:
            return self.send_json(409, {"error": "MODEL_API_KEY_not_set_restart_server_after_loading_key"})
        with self.server.job_lock:
            if self.server.running:
                return self.send_json(409, {"error": "another_run_in_progress"})
            self.server.running = True
            run_id = "HACK008-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + secrets.token_hex(4)
            self.server.jobs[run_id] = {"run_id": run_id, "status": "QUEUED", "calls_attempted": 0, "steps": []}
        def worker():
            def on_update(value):
                with self.server.job_lock:
                    self.server.jobs[run_id] = value
            try:
                perform_run(question, self.server.evidence, key, run_id,
                            self.server.out_dir, caller=self.server.caller, on_update=on_update)
            except Exception as exc:
                # Do not retry: record an unknown/partial failure for manual inspection.
                with self.server.job_lock:
                    snapshot = dict(self.server.jobs.get(run_id, {}))
                snapshot["status"] = "STOPPED_UNEXPECTED_ERROR_DO_NOT_RETRY"
                snapshot["error_type"] = type(exc).__name__
                snapshot["error_message"] = str(exc)[:180]
                save_trace(snapshot, self.server.out_dir)
                on_update(snapshot)
            finally:
                with self.server.job_lock:
                    self.server.running = False
        threading.Thread(target=worker, daemon=True).start()
        self.send_json(202, {"run_id": run_id, "status": "QUEUED", "max_calls": 4})

def main():
    p = argparse.ArgumentParser(description="TerraCouncil FAITH localhost interactive council")
    p.add_argument("--evidence", required=True, help="Local Boké screened evidence JSON")
    p.add_argument("--out-dir", default=str(Path.home() / "Documents" / "TerraCouncil-Hack008-Sessions"))
    p.add_argument("--port", type=int, default=8765)
    a = p.parse_args()
    if not 1024 <= a.port <= 65535:
        raise ValueError("Invalid local port")
    records = json.loads(Path(a.evidence).read_text(encoding="utf-8"))
    gate = make_plan("Question préparatoire de Boké", records)
    if not gate["gate"]["evidence"]:
        raise ValueError("No usable screened Boké FSDC evidence; cannot start interactive app")
    if not UI.exists():
        raise FileNotFoundError("Missing ui/hack008.html in the latest GitHub ZIP")
    app = App(a.port, records, Path(a.out_dir))
    print("TERRACOUNCIL LOCAL:", f"http://127.0.0.1:{a.port}")
    print("FSDC:", gate["status"], "records:", len(gate["gate"]["evidence"]))
    print("META KEY AVAILABLE:", bool(os.environ.get("MODEL_API_KEY")))
    print("PAGE LOAD CALLS: 0. RUN CALLS: MAX 4 PER EXPLICIT CONSENT.")
    print("SESSION RECORDS:", a.out_dir)
    try:
        app.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")

if __name__ == "__main__":
    main()
