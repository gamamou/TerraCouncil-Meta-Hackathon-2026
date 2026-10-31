"""TERRA-META-020 — unified council / audio orchestration, local-only service.
Runs science once; checkpoints. Meta oral adaptation and ElevenLabs are explicit opt-in.
No scientific approval; no transcript exposed in HTML.
"""
import argparse,html,json,os,threading,uuid,webbrowser
from datetime import datetime
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import parse_qs,urlparse
from tools.terra_meta_demo_010b_adaptive import run as council_run
from tools.terra_meta_demo_013_integrated import write_bundle
from tools.terra_meta_demo_015_brief import assemble
from tools.terra_meta_demo_017_executive import render as render_brief
from tools.terra_audio_002_live import adapt,parse_dialogue,POLICY
from tools.terra_audio_002_resume import resume
from terra_demo_001_faith_gateway import load

HOME=Path.home()/"Documents"/"TerraCouncil-Workspace"
PILOT=HOME/"Sessions-DEMO013"/"session_20261030_175652"
STATE={"busy":False,"phase":"READY","message":"Prêt","session":str(PILOT),"audio":None}
LOCK=threading.Lock()
def update(**kw):
    with LOCK:STATE.update(kw)
def read_json(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sessions(root):
    if not root.exists():return []
    return sorted([x/"artifacts" for x in root.glob("session_*") if (x/"artifacts"/"05_scientific_brief.json").is_file()],
        key=lambda x:x.parent.name,reverse=True)
def make_session(question,snapshot,session_dir,meta_key,eleven_key=None,voices=None,do_audio=False,
                 council=council_run,adapt_model=adapt,audio_resume=resume):
    target=Path(session_dir)
    if target.exists():raise FileExistsError("Session directory already exists")
    data=load(snapshot)
    target.mkdir(parents=True)
    (target/"question.json").write_text(json.dumps({"question":question},ensure_ascii=False),encoding="utf8")
    tracefile=target/"trace_working.json"
    update(phase="FAITH_COUNCIL",message="Recherche FAITH et délibération Spark–Wonder")
    trace=council(data,question,meta_key,tracefile,max_lookups=5)
    if trace.get("status")!="GENERATED_NEEDS_SCIENTIFIC_REVIEW":
        raise RuntimeError("Conseil interrompu; checkpoint conservé : "+str(tracefile))
    update(phase="DOCUMENTS",message="Création Brief, Passport et investigations")
    artifacts=target/"artifacts"
    write_bundle(data,trace,artifacts,target.name)
    dossier=read_json(artifacts/"02_scientific_dossier.json")
    actions=read_json(artifacts/"03_investigation_plan.json")
    passport=read_json(artifacts/"04_passport_preview.json")
    brief=assemble(dossier,actions,passport)
    (artifacts/"05_scientific_brief.json").write_text(json.dumps(brief,ensure_ascii=False,indent=2),encoding="utf8")
    update(session=str(artifacts),audio=None,message="Brief, Passport et actions disponibles")
    if not do_audio:return {"status":"DOCUMENTS_READY_AUDIO_NOT_REQUESTED","session":str(artifacts)}
    update(phase="META_ORAL",message="Adaptation orale Meta")
    oral=target/"oral"
    oral.mkdir()
    raw=adapt_model(trace,meta_key)
    (oral/"internal_oral_script.json").write_text(json.dumps({"raw_meta_output":raw},ensure_ascii=False,indent=2),encoding="utf8")
    parse_dialogue(raw)
    update(phase="ELEVENLABS",message="Génération voix Spark–Wonder avec ElevenLabs v4")
    output=target/"audio_generated"
    result=audio_resume(oral,output,eleven_key,voices,model="eleven_v4",execute=True)
    if result["status"]!="AUDIO_GENERATED_UNREVIEWED":
        update(phase="AUDIO_FAILED",message="Documents préservés. Audio non produit ; consulter audio_manifest.json")
        return {"status":"DOCUMENTS_READY_AUDIO_FAILED","session":str(artifacts),"audio_manifest":str(output/"audio_manifest.json")}
    update(audio=str(output),phase="COMPLETE",message="Tous les livrables sont disponibles")
    passport_link={"audio_status":"AUDIO_GENERATED_UNREVIEWED","manifest":str(output/"audio_manifest.json"),
                   "session":target.name,"policy":POLICY}
    (target/"audio_passport_link.json").write_text(json.dumps(passport_link,ensure_ascii=False,indent=2),encoding="utf8")
    return {"status":"COMPLETE","session":str(artifacts),"audio":str(output)}

def webpage():
    s=STATE.copy();root=Path(s["session"]);brief=root/"05_scientific_brief.json"
    detail=""
    if brief.exists():
        b=read_json(brief);e=b.get("executive_brief",{})
        detail="<p>Maturité : <strong>"+html.escape(str(e.get("scientific_readiness")))+"</strong></p>"
        detail+="<p>Investigations : "+str(len(b.get("follow_up",{}).get("proposed_investigations",[])))+"</p>"
    audio=Path(s["audio"]) if s.get("audio") else None
    player='<audio controls preload="metadata" src="/audio"></audio>' if audio and (audio/"council_audio_01.mp3").exists() else "<p>Audio non associé à cette session.</p>"
    history="".join('<li><a href="/select?session='+x.parent.name+'">'+html.escape(x.parent.name)+'</a></li>' for x in sessions(ARGS.storage))
    refresh='<script>setTimeout(()=>location.reload(),12000)</script>' if s["busy"] else ""
    return """<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TerraCouncil — Hackathon</title><style>
body{font:16px/1.6 system-ui;background:#edf3f7;color:#16364a;margin:0}main{max-width:980px;margin:26px auto;padding:15px}
header{background:#13485b;color:white;padding:30px;border-radius:18px}section{background:white;border:1px solid #d7e3ed;border-radius:14px;padding:22px;margin-top:17px}
textarea{width:100%;box-sizing:border-box;min-height:100px;font:inherit;padding:12px}
button{padding:12px 20px;background:#12617a;border:0;color:white;border-radius:9px;cursor:pointer}audio{width:100%}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}@media(max-width:700px){.grid{display:block}}
a{color:#08617b}</style><main><header><div>SUSTAINAFRICA · FAITH · TERRACOUNCIL</div><h1>Scientific Decision Intelligence</h1>
<p>Question → Conseil → Brief → Passport → Council Theater</p></header>
<section><h2>Question scientifique</h2><form action="/start" method="post" onsubmit="return confirm('Lancer les appels Meta, et éventuellement ElevenLabs ? Ces appels peuvent être facturés.')">
<textarea name="question" required>Identifiez cinq sites miniers en Guinée prioritaires pour un programme pilote de réhabilitation. Recherchez les preuves FAITH disponibles et proposez des interventions conditionnelles issues du catalogue.</textarea>
<p><label><input type="checkbox" name="audio" value="yes"> Générer également le débat audio ElevenLabs v4 (coût API)</label></p>
<button """+("disabled" if s["busy"] else "")+""">Lancer une nouvelle session</button></form>
<p><strong>Étape : </strong>"""+html.escape(s["phase"])+""" · """+html.escape(s["message"])+"""</p></section>
<div class="grid"><section><h2>Executive Brief</h2>"""+detail+"""<p><a href="/brief">Ouvrir le rapport</a></p></section>
<section><h2>Decision Passport</h2><p>Provenance et revue humaine.</p><p><a href="/passport">Consulter</a></p></section></div>
<section><h2>Council Theater</h2><p>Spark et Wonder · Audio sans transcription publique.</p>"""+player+"""</section>
<section><h2>Actions & suivi</h2><a href="/actions">Investigations proposées</a></section>
<section><h2>Sessions précédentes</h2><ul>"""+history+"""</ul></section>
<small>Les preuves non validées ne sont jamais présentées comme des décisions approuvées.</small></main>"""+refresh

def background(question,do_audio):
    try:
        key=os.getenv("MODEL_API_KEY")
        if not key:raise RuntimeError("MODEL_API_KEY manquante")
        voices={"spark":os.getenv("ELEVENLABS_SPARK_VOICE_ID"),"wonder":os.getenv("ELEVENLABS_WONDER_VOICE_ID")}
        eleven=os.getenv("ELEVENLABS_API_KEY")
        if do_audio and (not eleven or not all(voices.values())):raise RuntimeError("Paramètres ElevenLabs manquants")
        target=ARGS.storage/("session_"+datetime.now().strftime("%Y%m%d_%H%M%S")+"_"+uuid.uuid4().hex[:6])
        make_session(question,ARGS.snapshot,target,key,eleven,voices,do_audio)
    except Exception as exc:update(phase="STOPPED_NO_AUTO_RETRY",message=str(exc)[:320])
    finally:update(busy=False)

class Handler(BaseHTTPRequestHandler):
    def send(self,status,body,mime):
        self.send_response(status);self.send_header("Content-Type",mime);self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(body)
    def do_GET(self):
        route=urlparse(self.path)
        if route.path=="/":return self.send(200,webpage().encode("utf8"),"text/html; charset=utf-8")
        if route.path=="/select" and not STATE["busy"]:
            candidate=parse_qs(route.query).get("session",[""])[0]
            valid={x.parent.name:x for x in sessions(ARGS.storage)}
            if candidate in valid:
                session=valid[candidate];audio=session.parent/"audio_generated"
                update(session=str(session),audio=str(audio) if (audio/"council_audio_01.mp3").exists() else None,
                    phase="REPLAY",message="Session retrouvée sans appels API")
            self.send_response(303);self.send_header("Location","/");self.end_headers();return
        path=Path(STATE["session"])
        files={"/passport":path/"04_passport_preview.json","/actions":path/"03_investigation_plan.json"}
        if route.path=="/brief":
            f=path/"05_scientific_brief.json"
            if f.exists():return self.send(200,render_brief(read_json(f)).encode("utf8"),"text/html; charset=utf-8")
        if route.path in files and files[route.path].exists():
            return self.send(200,files[route.path].read_bytes(),"application/json; charset=utf-8")
        if route.path=="/audio" and STATE.get("audio"):
            audio=Path(STATE["audio"])/"council_audio_01.mp3"
            if audio.exists():return self.send(200,audio.read_bytes(),"audio/mpeg")
        return self.send(404,b"Not found","text/plain")
    def do_POST(self):
        if self.path!="/start":return self.send(404,b"Not found","text/plain")
        with LOCK:
            if STATE["busy"]:return self.send(409,b"Already running","text/plain")
            STATE["busy"]=True
        try:
            size=int(self.headers.get("Content-Length","0"))
            if size<1 or size>10000:raise ValueError("Request size invalid")
            fields=parse_qs(self.rfile.read(size).decode("utf8"))
            question=fields.get("question",[""])[0].strip()
            if not 10<=len(question)<=4000:raise ValueError("Invalid question")
            threading.Thread(target=background,args=(question,fields.get("audio")==["yes"]),daemon=True).start()
        except Exception as exc:
            update(busy=False);return self.send(400,str(exc).encode(),"text/plain")
        self.send_response(303);self.send_header("Location","/");self.end_headers()
    def log_message(self,*args):pass

def main():
    global ARGS
    p=argparse.ArgumentParser();p.add_argument("--snapshot",required=True)
    p.add_argument("--session",default=str(PILOT));p.add_argument("--audio-folder")
    p.add_argument("--storage",type=Path,default=HOME/"Sessions-UNIFIED020");p.add_argument("--port",type=int,default=8766)
    ARGS=p.parse_args()
    STATE["session"]=ARGS.session;STATE["audio"]=ARGS.audio_folder
    server=ThreadingHTTPServer(("127.0.0.1",ARGS.port),Handler)
    url="http://127.0.0.1:"+str(ARGS.port)
    print("TerraCouncil 020: "+url,flush=True);webbrowser.open(url);server.serve_forever()
if __name__=="__main__":main()
