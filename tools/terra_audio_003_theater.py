"""AUDIO-003: private local Council Theater playback from an existing AUDIO-002 run.
No API calls, no oral transcript exposed, no alteration of source science.
"""
import argparse, hashlib, html, json, shutil
from pathlib import Path

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):h.update(block)
    return h.hexdigest()

def assemble(session,audio_run,out):
    session=Path(session);audio_run=Path(audio_run);out=Path(out)
    if out.exists():raise FileExistsError("New destination required")
    brief=json.loads((session/"05_scientific_brief.json").read_text(encoding="utf-8-sig"))
    original=json.loads((session/"04_passport_preview.json").read_text(encoding="utf-8-sig"))
    manifest=json.loads((audio_run/"audio_manifest.json").read_text(encoding="utf-8-sig"))
    if manifest.get("status")!="AUDIO_GENERATED_UNREVIEWED":raise ValueError("Audio run incomplete")
    segments=manifest.get("audio_segments",[])
    if not segments:raise ValueError("No audio segments")
    verified=[]
    for index,item in enumerate(segments,1):
        name=item.get("file","")
        if Path(name).name!=name or not name.endswith(".mp3"):raise ValueError("Invalid audio filename")
        src=audio_run/name
        if not src.is_file():raise FileNotFoundError(src)
        sha=digest(src)
        if sha!=item.get("sha256"):raise ValueError("Audio integrity mismatch "+name)
        verified.append((src,"audio_%02d.mp3"%index,sha))
    out.mkdir(parents=True)
    for src,name,_ in verified:shutil.copyfile(src,out/name)
    evidence={"schema_version":"TERRA-AUDIO-003","source_session":session.name,
        "session_id":original.get("session_id") or session.name,
        "passport_status":original.get("passport_status") or original.get("status") or "UNREVIEWED_INTERNAL",
        "question":brief.get("question"),"scientific_readiness":brief.get("executive_brief",{}).get("scientific_readiness"),
        "audio_status":"AUDIO_GENERATED_UNREVIEWED",
        "audio_policy":manifest.get("audio_policy"),
        "audio_model":manifest.get("model"),
        "audio_tracks":[{"file":name,"sha256":sha} for _,name,sha in verified],
        "scientific_conclusions_source":"05_scientific_brief.json",
        "review_required_post_hackathon":True,
        "automatic_approval":False}
    (out/"council_passport_audio.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out/"council_theater.html").write_text(render(evidence),encoding="utf-8")
    return evidence

def render(info):
    esc=lambda s:html.escape(str(s if s is not None else ""))
    audios="".join('<div class="track"><div class="caption">Séquence '+str(i)+'</div><audio controls preload="metadata" src="'+esc(track["file"])+'"></audio></div>'
        for i,track in enumerate(info["audio_tracks"],1))
    return """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>TerraCouncil · Council Theater</title>
<style>
*{box-sizing:border-box}body{background:#edf3f7;color:#19374b;font:16px/1.6 system-ui;margin:0}
main{max-width:850px;padding:24px;margin:auto}
header{background:linear-gradient(125deg,#123d52,#1e6574);color:white;border-radius:20px;padding:35px}
h1{font-size:31px;margin:7px 0 12px}.overline{letter-spacing:.12em;text-transform:uppercase;font-size:12px;opacity:.85}
section{background:white;border:1px solid #dae3ec;border-radius:16px;padding:26px;margin-top:18px}
.label,.caption{color:#687e8c;font-size:13px}.track{margin:20px 0}audio{width:100%;margin-top:7px}
.people{display:flex;gap:12px;flex-wrap:wrap}.person{border:1px solid #cddce4;border-radius:12px;padding:10px 16px}
a{color:#0a657a}footer{margin-top:22px;font-size:12px;color:#5d7383}
</style></head><body><main><header><div class="overline">SustainAfrica · FAITH · TerraCouncil</div>
<h1>Live Council Theater</h1><p>"""+esc(info["question"])+"""</p>
<div class="overline">Débat audio de votre session · Spark &amp; Wonder</div></header>
<section><h2>Écouter le Conseil</h2>
<div class="people"><div class="person">🎙️ Spark · Scientific Lead</div><div class="person">🎙️ Wonder · Scientific Critic</div></div>
"""+audios+"""
<p class="label">Audio créé à partir de la délibération de cette session. Réécoute locale sans appel API.</p></section>
<section><h2>Décision &amp; provenance</h2>
<p><strong>Maturité scientifique :</strong> """+esc(info["scientific_readiness"])+"""</p>
<p><strong>Passport :</strong> """+esc(info["passport_status"])+"""</p>
<p><strong>Statut audio :</strong> """+esc(info["audio_status"])+"""</p>
<p><strong>Session :</strong> """+esc(info["session_id"])+"""</p>
<p><a href="council_passport_audio.json">Consulter le manifeste de provenance</a></p></section>
<footer>Audio de démonstration non approuvé scientifiquement. Validation de l'adaptation orale prévue après le hackathon.</footer>
</main></body></html>"""

def main():
    p=argparse.ArgumentParser();p.add_argument("--session",required=True)
    p.add_argument("--audio-run",required=True);p.add_argument("--output-dir",required=True)
    a=p.parse_args();result=assemble(a.session,a.audio_run,a.output_dir)
    print(json.dumps({"status":"COUNCIL_THEATER_READY","audio_tracks":len(result["audio_tracks"]),
       "html":str(Path(a.output_dir)/"council_theater.html"),"api_calls":0},ensure_ascii=False))
if __name__=="__main__":main()
