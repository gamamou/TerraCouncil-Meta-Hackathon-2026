"""012J: generate an offline, single-page human editorial review studio.
Original FSDC artifacts never modified. No API requests.
"""
import argparse,hashlib,html,json
from pathlib import Path
def sha(s):return hashlib.sha256(s.encode("utf-8")).hexdigest()
def build(src,voice):
 if src.get("schema")!="TERRA_META_012E_VOICE_REVIEW_V1" or len(src.get("turns",[]))!=19:raise ValueError("012E review needed")
 if voice.get("schema")!="TERRA_META_012H_CONFIRMED_ROLE_VOICES":raise ValueError("Confirmed voices needed")
 rows=[]
 for t in src["turns"]:
  if sha(t["original_text"])!=t["original_sha256"]:raise ValueError("Original text corrupted")
  r=voice["roles"][t["role"]]
  rows.append({"turn":t["turn"],"role":t["role"],"speaker":r["name"],"voice_id":r["voice_id"],
   "original_text":t["original_text"],"original_sha256":t["original_sha256"],
   "alerts":t["unresolved_alerts"]})
 data=json.dumps(rows,ensure_ascii=False).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
 page=r'''<!doctype html><html lang="fr"><meta charset="UTF-8"><title>TerraCouncil · Revue 012J</title>
 <style>body{font:16px Segoe UI,Arial;background:#0c1726;color:#e9f3f9;margin:0}header{position:sticky;top:0;background:#14263b;padding:18px 28px;z-index:2;border-bottom:1px solid #36576d}main{max-width:1100px;margin:auto;padding:20px}article{background:#16293e;border:1px solid #345169;border-radius:13px;padding:22px;margin:18px 0}h1{margin:0}h2{margin:3px 0 13px}textarea{width:100%;min-height:210px;background:#0c1929;color:#fff;border:1px solid #52718b;border-radius:7px;padding:14px;font:15px/1.6 Segoe UI;box-sizing:border-box}button{background:#5ed5c0;color:#10283a;border:0;border-radius:7px;padding:12px 18px;font-weight:bold;cursor:pointer}label{display:block;margin:11px 0}details{margin:10px 0}.alert{color:#ffc78e}.muted{color:#b5c5d7}.row{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap}.note{background:#243e56;border-left:3px solid #ffc78e;padding:12px;margin:16px 0}pre{white-space:pre-wrap}small{color:#b5c5d7}</style>
 <header><div class="row"><div><h1>TerraCouncil · Atelier de revue 012J</h1><small>19 interventions · textes originaux intacts · aucune transmission à ElevenLabs</small></div><button id="save">Exporter les corrections et validations</button></div><p id="count">0 intervention approuvée</p></header>
 <main><div class="note">Chaque texte doit être relu et approuvé explicitement. Les cinq tours avec alertes exigent une correction des problèmes signalés, ou une justification documentée. Une approbation éditoriale ne constitue PAS une validation scientifique du terrain, ni une autorisation de facturation ou d'envoi à ElevenLabs. Le fichier exporté reste local.</div><div id="cards"></div></main>
 <script>const rows=__DATA__;const cards=document.getElementById('cards');
 const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
 rows.forEach(r=>{const a=document.createElement('article');a.dataset.turn=r.turn;const flag=r.alerts.length;
 a.innerHTML='<div class="row"><h2>T'+String(r.turn).padStart(2,'0')+' · '+esc(r.role)+' · '+esc(r.speaker)+'</h2><b class="'+(flag?'alert':'muted')+'">'+(flag?'ALERTES À RÉSOUDRE':'RELECTURE REQUISE')+'</b></div>'+
 '<details><summary>Consulter le texte original (lecture seule)</summary><pre>'+esc(r.original_text)+'</pre></details>'+
 (flag?'<details open><summary>Alertes scientifiques ('+flag+')</summary><pre>'+esc(JSON.stringify(r.alerts,null,2))+'</pre></details>':'')+
 '<label>Version orale corrigée proposée</label><textarea class="edit"></textarea>'+
 '<label>Note de revue et justification des modifications'+(flag?' (obligatoire)':'')+'</label><textarea class="noteedit" style="min-height:80px"></textarea>'+
 '<label><input type="checkbox" class="approve"> J’ai relu l’intégralité et approuve cette version orale sur le plan éditorial (sans valider les faits scientifiques)</label>';
 cards.append(a);a.querySelector('.edit').value=r.original_text;
 });
 function update(){const n=[...cards.querySelectorAll('.approve')].filter(x=>x.checked).length;document.getElementById('count').textContent=n+'/19 relectures approuvées — '+(19-n)+' en attente';}
 cards.addEventListener('change',update);update();
 document.getElementById('save').addEventListener('click',()=>{
 const turns=rows.map((r,i)=>{const a=cards.children[i],text=a.querySelector('.edit').value.trim(),note=a.querySelector('.noteedit').value.trim(),approved=a.querySelector('.approve').checked;
 const eligible=approved&&text.length>0&&(!r.alerts.length||(note.length>=20 && text!==r.original_text));
 return {turn:r.turn,role:r.role,voice_id:r.voice_id,original_sha256:r.original_sha256,proposed_text:text,review_note:note,editorial_checked:approved,editorial_review_complete:eligible,unresolved_source_alert_count:r.alerts.length};
 });
 const obj={schema:'TERRA_META_012J_EDITORIAL_EXPORT_V1',status:'LOCAL_HUMAN_EDITORIAL_REVIEW_ONLY',human_scientific_validation:false,tts_authorized:false,voice_provider_calls:0,turns};
 const blob=new Blob([JSON.stringify(obj,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download='Boke-012J-Editorial-Review.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),2000);
 alert('Fichier exporté. Tours éditorialement complets : '+turns.filter(x=>x.editorial_review_complete).length+'/19. AUCUN appel ElevenLabs.');
 });</script></html>''';
 return page.replace("__DATA__",data)
def main():
 a=argparse.ArgumentParser();a.add_argument("--review",required=True);a.add_argument("--voices",required=True);a.add_argument("--output",required=True);v=a.parse_args()
 path=Path(v.output)
 if path.exists():raise SystemExit("Refusing existing output")
 page=build(json.loads(Path(v.review).read_text(encoding="utf-8-sig")),json.loads(Path(v.voices).read_text(encoding="utf-8-sig")))
 with path.open("x",encoding="utf-8") as f:f.write(page)
 print("REVIEW_STUDIO_READY",path,"19 turns; 5 flagged; 0 TTS calls")
if __name__=="__main__":main()
