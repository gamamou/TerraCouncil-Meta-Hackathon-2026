"""TERRA-META-023 — Jury-ready local interface built on proven TERRA-META-020.
Reuse existing execution engine; no new scientific or billing logic.
"""
import argparse,html,json,webbrowser,threading
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
from tools import terra_meta_020_end_to_end as core

def esc(x):return html.escape(str(x if x is not None else ""))
def root_for(session):
    path=Path(session)
    return path.parent if path.name=="artifacts" else path
def audio_folders(root,language="fr"):
    if language=="en":return sorted(root.glob("audio_en_*"),reverse=True)
    return [root/"audio_generated",*sorted(root.glob("audio_retry_*"),reverse=True),
            *sorted(root.glob("audio_recovered_*"),reverse=True),
            *sorted(root.glob("audio_revised_*"),reverse=True)]
def audio_for_session(session,language="fr"):
    root=root_for(session)
    candidates=[x for x in audio_folders(root,language) if (x/"audio_manifest.json").exists()]
    verified=[]
    for folder in candidates:
        try:
            data=core.read_json(folder/"audio_manifest.json")
            if data.get("status")!="AUDIO_GENERATED_UNREVIEWED":continue
            tracks=data.get("audio_segments",[])
            if tracks and all((folder/t["file"]).is_file() for t in tracks):verified.append(folder)
        except (ValueError,KeyError,OSError):continue
    if verified:return max(verified,key=lambda p:p.stat().st_mtime)
    return None
def current_audio(language="fr"):
    if language=="en":return audio_for_session(core.STATE["session"],"en")
    folder=Path(core.STATE["audio"]) if core.STATE.get("audio") else audio_for_session(core.STATE["session"])
    return folder if folder and folder.exists() else None
def actions_html():
    f=Path(core.STATE["session"])/"03_investigation_plan.json"
    if not f.exists():return "<p>Plan d'investigation non disponible.</p>"
    d=core.read_json(f);tasks=d.get("tasks",[])
    rows="".join("<tr><td>"+esc(t.get("task_id"))+"</td><td>"+esc(t.get("action") or t.get("title") or t.get("description"))+
        "</td><td>"+esc(t.get("status"))+"</td></tr>" for t in tasks)
    return "<p class='muted'>Contrôles scientifiques préalables, non autorisés automatiquement. Les actions ci-dessous proviennent du moteur de vérification des sites miniers ; elles ne constituent pas un plan sectoriel spécifique à la question courante.</p><table><thead><tr><th>ID</th><th>Action</th><th>Statut</th></tr></thead><tbody>"+rows+"</tbody></table>"
def passport_html():
    f=Path(core.STATE["session"])/"04_passport_preview.json"
    if not f.exists():return "<p>Passport indisponible.</p>"
    d=core.read_json(f)
    audio=current_audio()
    link=root_for(core.STATE["session"])/"audio_passport_link.json"
    return ("<dl><dt>Session</dt><dd>"+esc(d.get("session_id"))+"</dd>"
        "<dt>Statut</dt><dd>"+esc(d.get("passport_status"))+"</dd>"
        "<dt>Maturité</dt><dd>"+esc(d.get("scientific_readiness"))+"</dd>"
        "<dt>Trace SHA-256</dt><dd><code>"+esc(d.get("trace_sha256"))+"</code></dd>"
        "<dt>Révision humaine</dt><dd>"+esc((d.get("human_review") or {}).get("status"))+"</dd>"
        "<dt>Audio</dt><dd>"+("Généré, non revu" if audio else "Non disponible")+"</dd></dl>"
        "<p><a href='/passport.pdf'>Télécharger le Passport PDF</a></p>")
def topic_label(question):
    q=(question or "").lower()
    categories=[
        ("Énergie",("énergie","energie","électricité","electricite","solaire")),
        ("Climat",("climat","résilience","resilience")),
        ("Mines",("mine","minier","bauxite")),
        ("Agriculture",("agriculture","agricole")),
        ("Eau",("eau","hydrologique","bassin versant")),
        ("Biodiversité",("biodiversité","biodiversite","écologique"))]
    found=[label for label,terms in categories if any(w in q for w in terms)]
    return " · ".join(found[:3]) if found else "Conseil scientifique"

def session_question(folder):
    f=folder.parent/"question.json"
    if f.exists():
        try:return core.read_json(f).get("question","")
        except (ValueError,OSError):pass
    f=folder/"05_scientific_brief.json"
    if f.exists():
        try:return core.read_json(f).get("question","")
        except (ValueError,OSError):pass
    return ""

def frontpage(language="fr"):
    state=core.STATE.copy()
    root=Path(state["session"])
    brief=root/"05_scientific_brief.json"
    question=""
    level="Non disponible";investigations="—"
    if brief.is_file():
        b=core.read_json(brief);question=b.get("question") or ""
        level=(b.get("executive_brief") or {}).get("scientific_readiness","—")
        investigations=str(len((b.get("follow_up") or {}).get("proposed_investigations",[])))
    audio=current_audio(language)
    tracks=[]
    if audio:
        try:tracks=core.read_json(audio/"audio_manifest.json").get("audio_segments",[])
        except (ValueError,OSError):pass
    english_audio=current_audio("en")
    players="".join("<div class='player'><strong>Segment "+str(i+1)+" / "+str(len(tracks))+"</strong> · "+esc(audio.name if audio else "")+" · "+esc(t.get("file"))+"<audio controls preload='metadata' src='/audio?lang="+language+"&i="+str(i)+"'></audio></div>"
          for i,t in enumerate(tracks))
    if not players:
        players="<p class='muted'>"+("English audio is not generated for this session." if language=="en" else "Aucun audio disponible pour cette session.")+"</p>"
        if language=="en" and not state["busy"]:
            players+="<form method='post' action='/generate-english-audio'><p>Paid AI generation / Génération avec frais API.</p><button type='submit'>Generate English debate</button></form>"
    else:
        players="<p class='muted'>"+("Scientific debate in English" if language=="en" else "Délibération en français")+" · "+esc(topic_label(question))+"</p>"+players
    if audio:
        source=root_for(state["session"])/"oral"/"internal_oral_script.json"
        newer=sorted(root_for(state["session"]).glob("oral_revised_*/internal_oral_script.json"),reverse=True)
        if audio.name.startswith(("audio_recovered_","audio_revised_")) and newer:source=newer[0]
        try:
            from tools.terra_audio_002_live import parse_dialogue
            turns=parse_dialogue(core.read_json(source)["raw_meta_output"])
            speakers=sorted(set(t["speaker"] for t in turns))
            players="<p><strong>Voix du dialogue :</strong> "+esc(", ".join(speakers))+" · "+str(len(turns))+" interventions</p>"+players
            if len(speakers)<2:players="<p role='alert'><strong>Attention :</strong> audio à voix unique. Ce résultat ne constitue pas un débat multivoix validé.</p>"+players
        except (OSError,ValueError,KeyError,TypeError):pass
    oral=root_for(state["session"])/"oral"/"internal_oral_script.json"
    revised=list(root_for(state["session"]).glob("oral_revised_*/internal_oral_script.json"))
    retry=bool(oral.is_file() or revised)
    # Do not automatically rerun Meta if only revised script is present.
    if language=="fr" and not audio and retry and not state["busy"]:
        players+="<form method='post' action='/resume-audio' onsubmit=\"return confirm('Reprendre ElevenLabs uniquement ? Cet appel est payant.')\"><button>Reprendre la génération audio</button></form>"
    items=core.sessions(core.ARGS.storage)
    history="".join("<li><a href='/select?session="+esc(x.parent.name)+"'>"+esc(topic_label(session_question(x)))+"</a> · "+esc(x.parent.name)+"</li>" for x in items)
    busy=bool(state["busy"])
    stage=state.get("phase","READY")
    progress={"READY":0,"FAITH_COUNCIL":20,"DOCUMENTS":60,"DOCUMENTS_READY":100,
              "META_ORAL":73,"ELEVENLABS":86,"COMPLETE":100,"AUDIO_FAILED":100}.get(stage,0)
    return """<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>TerraCouncil · Decision Intelligence</title>
<style>
:root{font:15px/1.55 system-ui,Segoe UI,sans-serif;color:#163348;background:#eef4f7}*{box-sizing:border-box}body{margin:0}
main{max-width:1120px;margin:auto;padding:26px 18px}header{padding:30px;border-radius:20px;background:linear-gradient(115deg,#0f394f,#16616d);color:white}
header h1{font-size:34px;margin:8px 0}.eyebrow{font-size:12px;letter-spacing:.15em;opacity:.8}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.panel{border:1px solid #d5e3ec;background:white;border-radius:16px;padding:23px;margin-top:18px}
h2{margin:0 0 12px;font-size:21px}h3{margin:0;font-size:17px}.muted{color:#617a88}
textarea{width:100%;min-height:120px;border-radius:10px;padding:12px;font:inherit;border:1px solid #b6cad6}
button{background:#12647d;color:white;border:0;border-radius:10px;padding:11px 17px;cursor:pointer;margin-top:10px}
button:disabled{opacity:.55}a{color:#09647a}audio{width:100%}.player{margin:14px 0}
.stat{font-size:21px;font-weight:750;overflow-wrap:anywhere}dt{font-weight:700;margin-top:12px}dd{margin:3px 0;overflow-wrap:anywhere}
table{border-collapse:collapse;width:100%}td,th{padding:9px;border-bottom:1px solid #d9e4eb;text-align:left}
#status{padding:13px;border-radius:10px;background:#edf4f7;border-left:4px solid #12647d}#status[aria-busy=true]{background:#fff5d9;border-left-color:#c8871e}.player strong{display:inline-block;margin-bottom:8px}nav{display:flex;gap:16px;flex-wrap:wrap;margin-top:14px}
nav a{color:white}li{padding:3px}small{color:#617a88}
@media(max-width:750px){.grid{display:block}header h1{font-size:28px}}@media print{form,nav,audio{display:none}}
</style></head><body><main><header><div class="eyebrow">SUSTAINAFRICA · FAITH · TERRACOUNCIL</div>
<h1>Scientific Decision Intelligence</h1><p>De la question aux preuves, aux recommandations et au débat oral.</p>
<p style="text-align:right"><label for="ui-language">Langue / Language :</label> <select id="ui-language" aria-label="Interface language"><option value="fr">Français</option><option value="en">English</option></select></p>
<nav><a href="#question">Nouvelle question</a><a href="#deliverables">Livrables</a><a href="#audio">Council Theater</a>
<a href="#passport">Passport</a><a href="#actions">Suivi</a></nav></header>
<section class="panel" id="question"><h2>Question scientifique</h2>
<form action="/start" method="post" onsubmit="return confirm('Démarrer une nouvelle délibération Meta ? Les appels API peuvent être facturés.')">
<textarea name="question" required placeholder="Saisissez une nouvelle question scientifique…"></textarea>
<label><input type="checkbox" name="audio" value="yes" checked> Générer également le débat oral</label>
<p><button """+("disabled" if busy else "")+""">Lancer le Conseil</button></p></form>
<div class="panel" style="padding:14px;margin:12px 0 0"><strong>Question sélectionnée</strong><p>"""+esc(question or "Aucune question traitée")+"""</p></div>
<div id="status" role="status" aria-live="polite" aria-busy='"""+("true" if busy else "false")+"""'><strong>Étape :</strong> """+esc(state["phase"])+""" · """+esc(state["message"])+"""</div><progress id="progress" value='"""+str(progress)+"""' max="100" style="width:100%;margin-top:9px"></progress><p class="muted">Progression indicative par étape (et non durée restante).</p></section>
<section class="panel" id="deliverables"><h2>Livrables de la session</h2><p>Choisissez la langue du PDF. La traduction anglaise du Brief nécessite un appel Meta lors du premier export.</p><p><a href="/brief.pdf?lang=fr">Executive Brief · Français</a> &nbsp; <a href="/passport.pdf?lang=fr">Decision Passport · Français</a></p><p><a href="/brief.pdf?lang=en" onclick="return confirm('La première traduction peut consommer des crédits Meta. Continuer ?')">Executive Brief · English</a> &nbsp; <a href="/passport.pdf?lang=en">Decision Passport · English</a></p><small><a href="/passport.json">Passport JSON original</a></small></section>
<section class="panel" id="audio"><h2>Council Theater</h2>"""+players+"""</section>
<section class="panel" id="actions"><h2>Actions & suivi</h2>"""+actions_html()+"""</section>
<section class="panel"><h2>Historique des sessions</h2><ul>"""+history+"""</ul></section>
<p><small>Les résultats conservent leurs réserves scientifiques. Toute validation humaine est enregistrée séparément.</small></p>
</main><script>
const previous="""+json.dumps({"phase":state["phase"],"busy":busy},ensure_ascii=False)+""";
async function poll(){try{
 const r=await fetch('/status');const s=await r.json();
 const box=document.getElementById('status');
 box.setAttribute('aria-busy',String(s.busy));
 const stages={READY:0,FAITH_COUNCIL:20,DOCUMENTS:60,DOCUMENTS_READY:100,META_ORAL:73,ELEVENLABS:86,COMPLETE:100,AUDIO_FAILED:100};
 document.getElementById('progress').value=stages[s.phase] ?? 0;
 box.textContent=(s.busy?'⏳ Traitement en cours — ':'Étape : ')+s.phase+' · '+s.message;
 if(!s.busy && s.phase!==previous.phase && s.phase!=='READY' && s.phase!=='REPLAY'){location.reload();}
}catch(e){}}
setInterval(poll,3000);
const dictionary={
'Question scientifique':'Scientific question',
'Nouvelle question':'New question',
'Livrables':'Deliverables',
'Livrables de la session':'Session deliverables',
'Council Theater':'Council Theater',
'Suivi':'Action tracking',
'Actions & suivi':'Actions and tracking',
'Historique des sessions':'Session history',
'Question sélectionnée':'Selected question',
'Lancer le Conseil':'Start Council',
'Générer également le débat oral':'Generate spoken debate',
'Français':'French','Rapports PDF et documents de traçabilité.':'PDF reports and traceability documents.',
'Progression indicative par étape (et non durée restante).':'Stage-based indicative progress, not remaining time.',
'De la question aux preuves, aux recommandations et au débat oral.':'From questions and evidence to recommendations and spoken debate.'
};
function setLanguage(lang){
 document.documentElement.lang=lang;
 document.getElementById('ui-language').value=lang;
 document.querySelector('textarea[name=question]').placeholder=lang==='en'?'Enter your scientific question…':'Saisissez une nouvelle question scientifique…';
 document.querySelectorAll('h2,nav a,button,label,strong,p,small').forEach(el=>{
  if(el.children.length)return;
  if(!el.dataset.fr)el.dataset.fr=el.textContent.trim();
  const key=el.dataset.fr;
  el.textContent=lang==='en'?(dictionary[key]||key):key;
 });
 history.replaceState({},'',location.pathname+'?lang='+lang+location.hash);
}
const lang=new URLSearchParams(location.search).get('lang')==='en'?'en':'fr';
setLanguage(lang);
document.getElementById('ui-language').addEventListener('change',e=>{location.href='/?lang='+e.target.value+location.hash;});
</script></body></html>"""

class Handler(core.Handler):
    def do_POST(self):
        if self.path!="/generate-english-audio":return super().do_POST()
        with core.LOCK:
            if core.STATE["busy"]:return self.send(409,b"Already running","text/plain")
            core.STATE["busy"]=True
        threading.Thread(target=generate_english_background,daemon=True).start()
        self.send_response(303)
        self.send_header("Location","/?lang=en#audio")
        self.end_headers()
    def do_GET(self):
        route=urlparse(self.path)
        if route.path=="/":
            language=parse_qs(route.query).get("lang",["fr"])[0]
            if language not in ("fr","en"):language="fr"
            return self.send(200,frontpage(language).encode("utf8"),"text/html; charset=utf-8")
        if route.path in ("/brief.pdf","/passport.pdf"):
            from tools.terra_meta_025_pdf import generate
            filename="05_scientific_brief.json" if route.path=="/brief.pdf" else "04_passport_preview.json"
            f=Path(core.STATE["session"])/filename
            if f.is_file():
                try:
                    kind="brief" if route.path=="/brief.pdf" else "passport"
                    language=parse_qs(route.query).get("lang",["fr"])[0]
                    if language not in ("fr","en"):return self.send(400,b"Unsupported language","text/plain")
                    data=core.read_json(f)
                    if language=="en" and kind=="brief":
                        import os
                        from tools.terra_meta_026_translation import get_english
                        data=get_english(kind,data,root_for(core.STATE["session"]),os.getenv("MODEL_API_KEY"))
                    body=generate(kind,data,language=language)
                    return self.send(200,body,"application/pdf")
                except Exception as exc:
                    return self.send(500,("Erreur PDF : "+str(exc)).encode("utf8"),"text/plain; charset=utf-8")
        if route.path=="/status":
            s={k:core.STATE.get(k) for k in ("phase","message","busy")}
            return self.send(200,json.dumps(s,ensure_ascii=False).encode("utf8"),"application/json")
        if route.path=="/passport.json":
            f=Path(core.STATE["session"])/"04_passport_preview.json"
            if f.is_file():return self.send(200,f.read_bytes(),"application/json")
        if route.path=="/audio":
            language=parse_qs(route.query).get("lang",["fr"])[0]
            folder=current_audio(language)
            if folder:
                try:
                    tracks=core.read_json(folder/"audio_manifest.json")["audio_segments"]
                    index=int(parse_qs(route.query).get("i",["0"])[0])
                    if 0<=index<len(tracks):
                        f=folder/tracks[index]["file"]
                        if f.is_file():return self.send(200,f.read_bytes(),"audio/mpeg")
                except (ValueError,KeyError,IndexError,OSError):pass
            return self.send(404,b"Audio unavailable","text/plain")
        return super().do_GET()

def generate_english_background():
    try:
        from tools.terra_audio_027_english import run
        root=root_for(core.STATE["session"])
        core.update(phase="META_ORAL",message="Preparing English scientific dialogue")
        outcome=run(root,execute=True)
        if outcome["status"]!="AUDIO_GENERATED_UNREVIEWED":
            raise RuntimeError(str(outcome.get("error") or outcome["status"]))
        core.update(phase="COMPLETE",message="English debate available")
    except Exception as exc:
        core.update(phase="AUDIO_FAILED",message="English audio: "+str(exc)[:250])
    finally:
        core.update(busy=False)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--snapshot",required=True)
    parser.add_argument("--session",default=str(core.PILOT))
    parser.add_argument("--storage",type=Path,default=core.HOME/"Sessions-UNIFIED020")
    parser.add_argument("--port",type=int,default=8767)
    args=parser.parse_args()
    core.ARGS=args
    core.STATE.update(session=args.session,audio=str(audio_for_session(args.session)) if audio_for_session(args.session) else None)
    server=ThreadingHTTPServer(("127.0.0.1",args.port),Handler)
    url="http://127.0.0.1:"+str(args.port)
    print("TerraCouncil 023: "+url,flush=True)
    webbrowser.open(url);server.serve_forever()
if __name__=="__main__":main()
