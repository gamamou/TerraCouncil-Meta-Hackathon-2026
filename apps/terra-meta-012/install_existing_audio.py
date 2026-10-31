"""012D: locate pre-existing TerraCouncil MP3; publish ONE unambiguous archival demo.
Never generate TTS, overwrite source, or relabel legacy recording as 19-turn final.
"""
import argparse,json,re,shutil,hashlib
from pathlib import Path
def discover(root):
 matches=[]
 for base in [root/"Sessions-HACK016",root/"Application"/"TerraCouncil-Meta-Hackathon"]:
  if not base.exists():continue
  for p in base.rglob("*.mp3"):
   if any(x in p.parts for x in (".git","node_modules",".venv")):continue
   if p.is_file() and p.stat().st_size>10000:
    matches.append(p)
 return sorted(set(matches),key=lambda p:str(p).lower())
def main():
 p=argparse.ArgumentParser();p.add_argument("--workspace",required=True);p.add_argument("--app",required=True)
 a=p.parse_args();root=Path(a.workspace);dest=Path(a.app)/"data"
 matches=discover(root)
 print("AUDIO_ARCHIVES_FOUND",len(matches))
 for n,path in enumerate(matches,1):print(n, str(path), "bytes",path.stat().st_size)
 candidates=[x for x in matches if re.search(r"boke|council|debate|dialogue",x.name,re.I)]
 if len(candidates)!=1:
  print("NO_AUTO_PUBLISH: expected exactly one distinguishable council audio archive.")
  return
 original=candidates[0];dest.mkdir(parents=True,exist_ok=True)
 target=dest/"audio/archive-boke-legacy.mp3"
 target.parent.mkdir(parents=True,exist_ok=True)
 manifest=dest/"audio-archive.json"
 if target.exists() or manifest.exists():
  print("EXISTING_ARCHIVE: no overwrite. Check",str(target))
  return
 shutil.copyfile(original,target)
 raw=target.read_bytes()
 m={"status":"LEGACY_DEMO_NOT_FINAL","file":"audio/archive-boke-legacy.mp3","sha256":hashlib.sha256(raw).hexdigest(),
 "source_path":str(original),"scientific_approval":False,"nineteen_turn_audio":False}
 with manifest.open("x",encoding="utf8") as f:json.dump(m,f,ensure_ascii=False,indent=2)
 print("LEGACY_AUDIO_READY",target,"bytes",len(raw))
if __name__=="__main__":main()
