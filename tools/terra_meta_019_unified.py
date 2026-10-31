"""TERRA-META-019: local integrated hackathon console (standard library).
Uses existing FAITH pipeline. API charges require explicit confirmation in UI.
No transcript displayed. Works with replay session and linked AUDIO-003 assets.
"""
import argparse, html, json, os, subprocess, sys, threading, uuid, webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from tools.terra_meta_demo_015_brief import assemble
from tools.terra_meta_demo_013_integrated import write_bundle
from tools.terra_meta_demo_017_executive import render as render_brief
from terra_demo_001_faith_gateway import load

HOME=Path.home()/"Documents"/"TerraCouncil-Workspace"
PILOT=HOME/"Sessions-DEMO013"/"session_20261030_175652"
STATE={"busy":False,"message":"Prêt","session":str(PILOT),"audio":None}
LOCK=threading.Lock()
def page():
    s=STATE.copy();session=Path(s["session"])
    brief=session/"05_scientific_brief.json"
    audio_path=Path(s["audio"]) if s.get("audio") else None
    audio_ok=bool(audio_path and (audio_path/"audio_01.mp3").is_file())
    detail=""
    if brief.exists():
        b=json.loads(brief.read_text(encoding="utf-8-sig"))
        e=b.get("executive_brief",{})
        detail="<p><strong>Maturité :</strong> "+html.escape(str(e.get("scientific_readiness")))+"</p>"
        detail+="<p><strong>Investigations :</strong> "+str(len(b.get("follow_up",{}).get("proposed_investigations",[])))+"</p>"
    player='<audio controls preload="metadata" src="/audio"></audio>' if audio_ok else "<p>Aucun audio lié à cette session.</p>"
    buttons='<button type="submit">Lancer le Conseil (Meta payant)</button>' if not s["busy"] else "<button disabled>En cours…</button>"
    return """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>TerraCouncil · Hackathon</title>
<style>body{margin:0;background:#eef3f7;color:#173346;font:16px/1.6 system-ui}
main{max-width:970px;margin:30px auto;padding:0 16px}header{padding:32px;color:white;background:#15475b;border-radius:18px}
section{background:white;border:1px solid #d8e3e9;border-radius:14px;padding:24px;margin:18px 0}
textarea{width:100%;min-height:100px;box-sizing:border-box;padding:12px;font:inherit}
button{padding:12px 20px;background:#13637c;color:white;border:0;border-radius:8px;cursor:pointer}
button:disabled{opacity:.6}a{color:#08617c}audio{width:100%}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}
@media(max-width:650px){.grid{display:block}}.sub{opacity:.85}
</style></head><body><main><header><div>SUSTAINAFRICA · FAITH · TERRA COUNCIL</div>
<h1>Scientific Decision Intelligence</h1><p class="sub">Question → Conseil → Brief → Passport → Débat audio</p></header>
<section><h2>Votre question scientifique</h2>
<form action="/start" method="post" onsubmit="return confirm('Démarrer une nouvelle session Meta ? Des appels payants seront effectués.')">
<textarea name="question" required>Identifiez cinq sites miniers en Guinée prioritaires pour un programme pilote de réhabilitation. Recherchez les preuves FAITH disponibles, justifiez vos choix et proposez des interventions conditionnelles issues du catalogue.</textarea>
<p>""" +buttons+"""</p></form><p><strong>État :</strong> """+html.escape(s["message"])+"""</p></section>
<div class="grid"><section><h2>Executive Brief</h2>"""+detail+"""
<p><a href="/brief">Ouvrir le rapport</a></p></section>
<section><h2>Decision Passport</h2><p>Traçabilité et validation interne.</p>
<p><a href="/passport">Consulter le Passport</a></p></section></div>
<section><h2>Council Theater</h2><p>Spark · Wonder — conversation multivoix, sans transcription exposée.</p>
"""+player+"""</section>
<section><h2>Action &amp; Follow-up</h2><p>Investigations proposées, non autorisées automatiquement.</p>
<p><a href="/actions">Voir les actions</a></p></section>
<footer><small>FAITH : preuves disponibles et limites explicites. Audio de démonstration : validation scientifique post-hackathon requise.</small></footer>
</main></body></html>"""

def generate(question,snapshot):
    with LOCK:STATE["busy"]=True;STATE["message"]="Conseil Meta en cours";STATE["audio"]=None
    try:
        if not Path(snapshot).is_file():raise FileNotFoundError("Snapshot FAITH introuvable")
        if not os.environ.get("MODEL_API_KEY"):raise RuntimeError("MODEL_API_KEY manquante")
        root=HOME/"Sessions-UNIFIED019"/("session_"+datetime.now().strftime("%Y%m%d_%H%M%S")+"_"+uuid.uuid4().hex[:6])
        root.mkdir(parents=True)
        cmd=[sys.executable,"-X","utf8",str(REPO/"tools"/"terra_meta_demo_010b_adaptive.py"),
            "--snapshot",snapshot,"--question",question,"--output",str(root/"trace_working.json"),"--execute"]
        env=os.environ.copy();env["PYTHONPATH"]=str(REPO)+os.pathsep+str(REPO/"src")
        result=subprocess.run(cmd,cwd=REPO,env=env,capture_output=True,text=True,timeout=900)
        if result.returncode:raise RuntimeError("Meta interrompu; trace conservée dans "+str(root))
        trace=json.loads((root/"trace_working.json").read_text(encoding="utf8"))
        target=root/"artifacts"
        write_bundle(load(snapshot),trace,target,root.name)
        d=json.loads((target/"02_scientific_dossier.json").read_text(encoding="utf8"))
        a=json.loads((target/"03_investigation_plan.json").read_text(encoding="utf8"))
        p=json.loads((target/"04_passport_preview.json").read_text(encoding="utf8"))
        brief=assemble(d,a,p)
        (target/"05_scientific_brief.json").write_text(json.dumps(brief,ensure_ascii=False,indent=2),encoding="utf8")
        with LOCK:STATE["session"]=str(target);STATE["message"]="Livrables créés. Audio à générer depuis AUDIO-002."
    except Exception as exc:
        with LOCK:STATE["message"]="Arrêt : "+str(exc)[:260]
    finally:
        with LOCK:STATE["busy"]=False

class Handler(BaseHTTPRequestHandler):
    def send(self,code,content,mime):
        self.send_response(code);self.send_header("Content-Type",mime)
        self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(content)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/":return self.send(200,page().encode("utf8"),"text/html; charset=utf-8")
        s=Path(STATE["session"])
        sources={"/brief":s/"05_scientific_brief.json",
                 "/passport":s/"04_passport_preview.json","/actions":s/"03_investigation_plan.json"}
        if path in sources:
            f=sources[path]
            if not f.is_file():return self.send(404,b"Not generated","text/plain")
            if path=="/brief":
                content=render_brief(json.loads(f.read_text(encoding="utf8"))).encode("utf8")
                return self.send(200,content,"text/html; charset=utf-8")
            return self.send(200,f.read_bytes(),"application/json; charset=utf-8")
        if path=="/audio" and STATE.get("audio"):
            f=Path(STATE["audio"])/"audio_01.mp3"
            if f.is_file():return self.send(200,f.read_bytes(),"audio/mpeg")
        return self.send(404,b"Not found","text/plain")
    def do_POST(self):
        if self.path!="/start":return self.send(404,b"Not found","text/plain")
        if STATE["busy"]:return self.send(409,b"Session busy","text/plain")
        size=int(self.headers.get("Content-Length","0"))
        if not 1<=size<=10000:return self.send(400,b"Invalid size","text/plain")
        from urllib.parse import parse_qs
        q=parse_qs(self.rfile.read(size).decode("utf8")).get("question",[""])[0].strip()
        if not 10<=len(q)<=4000:return self.send(400,b"Invalid question","text/plain")
        threading.Thread(target=generate,args=(q,ARGS.snapshot),daemon=True).start()
        self.send_response(303);self.send_header("Location","/");self.end_headers()
    def log_message(self,*args):pass

def main():
    global ARGS,REPO
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--session",default=str(PILOT))
    ap.add_argument("--audio-folder",help="AUDIO-003 output containing audio_01.mp3")
    ap.add_argument("--port",type=int,default=8765)
    ARGS=ap.parse_args();REPO=Path(__file__).resolve().parent.parent
    STATE["session"]=ARGS.session;STATE["audio"]=ARGS.audio_folder
    server=ThreadingHTTPServer(("127.0.0.1",ARGS.port),Handler)
    url="http://127.0.0.1:"+str(ARGS.port)
    print("TerraCouncil Unified 019: "+url,flush=True)
    webbrowser.open(url)
    server.serve_forever()
if __name__=="__main__":main()
