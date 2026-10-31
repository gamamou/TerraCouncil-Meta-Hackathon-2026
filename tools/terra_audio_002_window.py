"""TerraCouncil AUDIO-002 Windows configuration window. Python stdlib only.
Keys kept in memory only. Launches existing live audio module as subprocess.
"""
import json, os, subprocess, sys, threading, tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT=Path(__file__).resolve().parent.parent
DEFAULT_SESSION=Path.home()/"Documents/TerraCouncil-Workspace/Sessions-DEMO013/session_20261030_175652"
OUTPUT_ROOT=Path.home()/"Documents/TerraCouncil-Workspace/Sessions-AUDIO002"

class Window:
    def __init__(self,master):
        self.root=master;master.title("TerraCouncil — Audio Configuration")
        master.geometry("740x550");master.minsize(640,470)
        self.key=tk.StringVar(value=os.environ.get("ELEVENLABS_API_KEY",""))
        self.meta=tk.StringVar(value=os.environ.get("MODEL_API_KEY",""))
        self.spark=tk.StringVar();self.wonder=tk.StringVar()
        self.session=tk.StringVar(value=str(DEFAULT_SESSION))
        self.status=tk.StringVar(value="Configurez les clés puis cliquez sur Tester la connexion.")
        self.voices={}
        frame=ttk.Frame(master,padding=18);frame.pack(fill="both",expand=True)
        ttk.Label(frame,text="TerraCouncil · Audio Configuration",font=("Segoe UI",17,"bold")).pack(anchor="w",pady=(0,15))
        for label,var in (("Meta MODEL_API_KEY",self.meta),("ElevenLabs API Key",self.key)):
            ttk.Label(frame,text=label).pack(anchor="w")
            entry=ttk.Entry(frame,textvariable=var,show="*",width=85);entry.pack(fill="x",pady=(2,10))
        buttons=ttk.Frame(frame);buttons.pack(fill="x",pady=(0,12))
        self.connect=ttk.Button(buttons,text="Tester connexion / Charger les voix",command=self.load);self.connect.pack(side="left")
        ttk.Label(frame,text="Voix de Spark").pack(anchor="w")
        self.spark_box=ttk.Combobox(frame,textvariable=self.spark,state="readonly")
        self.spark_box.pack(fill="x",pady=(2,10))
        ttk.Label(frame,text="Voix de Wonder").pack(anchor="w")
        self.wonder_box=ttk.Combobox(frame,textvariable=self.wonder,state="readonly")
        self.wonder_box.pack(fill="x",pady=(2,10))
        ttk.Label(frame,text="Session TerraCouncil").pack(anchor="w")
        ttk.Entry(frame,textvariable=self.session).pack(fill="x",pady=(2,12))
        ttk.Label(frame,textvariable=self.status,wraplength=660).pack(anchor="w",pady=8)
        self.generate=ttk.Button(frame,text="Générer le débat audio de cette session",command=self.launch)
        self.generate.pack(fill="x",pady=10)
        ttk.Label(frame,text="Clés gardées en mémoire uniquement. Les appels Meta et ElevenLabs peuvent être facturés.",wraplength=660).pack(anchor="w")
    def notify(self,msg,error=False):
        self.status.set(msg)
        if error:messagebox.showerror("TerraCouncil AUDIO-002",msg)
    def load(self):
        key=self.key.get().strip()
        if not key:self.notify("Saisissez la clé API ElevenLabs.",True);return
        self.connect.config(state="disabled");self.status.set("Connexion à ElevenLabs...")
        def worker():
            try:
                req=Request("https://api.elevenlabs.io/v2/voices?page_size=100",headers={"xi-api-key":key})
                with urlopen(req,timeout=20) as resp:data=json.load(resp)
                voices={v["name"]+"  ["+v["voice_id"]+"]":v["voice_id"] for v in data.get("voices",[])}
                if not voices:raise ValueError("Aucune voix disponible.")
                def done():
                    self.voices=voices
                    values=list(voices)
                    self.spark_box["values"]=values;self.wonder_box["values"]=values
                    self.spark.set(values[0]);self.wonder.set(values[min(1,len(values)-1)])
                    self.connect.config(state="normal")
                    self.notify(str(len(values))+" voix disponibles. Choisissez Spark et Wonder.")
                self.root.after(0,done)
            except (HTTPError,URLError,ValueError,KeyError) as exc:
                def failed():
                    self.connect.config(state="normal")
                    self.notify("Connexion échouée : "+type(exc).__name__+" (vérifiez la clé et les permissions).",True)
                self.root.after(0,failed)
        threading.Thread(target=worker,daemon=True).start()
    def launch(self):
        if not self.meta.get().strip() or not self.key.get().strip():
            self.notify("Les clés Meta et ElevenLabs sont nécessaires.",True);return
        if self.spark.get() not in self.voices or self.wonder.get() not in self.voices:
            self.notify("Chargez et sélectionnez les deux voix.",True);return
        session=Path(self.session.get()).expanduser()
        if not (session/"01_trace.json").is_file():
            self.notify("Le dossier ne contient pas 01_trace.json.",True);return
        if not messagebox.askyesno("Confirmer les appels API","Générer un nouvel audio pour cette session ? Des crédits Meta et ElevenLabs peuvent être consommés."):return
        from datetime import datetime
        OUTPUT_ROOT.mkdir(parents=True,exist_ok=True)
        out=OUTPUT_ROOT/("audio_"+datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
        env=os.environ.copy()
        env.update({"MODEL_API_KEY":self.meta.get().strip(),"ELEVENLABS_API_KEY":self.key.get().strip(),
          "ELEVENLABS_SPARK_VOICE_ID":self.voices[self.spark.get()],
          "ELEVENLABS_WONDER_VOICE_ID":self.voices[self.wonder.get()],
          "PYTHONPATH":str(ROOT)+os.pathsep+str(ROOT/"src")})
        cmd=[sys.executable,"-X","utf8",str(ROOT/"tools/terra_audio_002_live.py"),
          "--session",str(session),"--output-dir",str(out),"--execute"]
        self.generate.config(state="disabled");self.status.set("Génération en cours...")
        def worker():
            try:
                p=subprocess.run(cmd,cwd=str(ROOT),env=env,capture_output=True,text=True,timeout=480)
                def done():
                    self.generate.config(state="normal")
                    self.notify(("Audio terminé : "+str(out)) if p.returncode==0 else
                        ("Échec de génération. Consultez audio_manifest.json dans "+str(out)),p.returncode!=0)
                    if p.returncode==0 and sys.platform=="win32":os.startfile(out)
                self.root.after(0,done)
            except Exception as exc:
                def failed():
                    self.generate.config(state="normal");self.notify("Génération interrompue : "+type(exc).__name__,True)
                self.root.after(0,failed)
        threading.Thread(target=worker,daemon=True).start()

if __name__=="__main__":
    app=tk.Tk();Window(app);app.mainloop()
