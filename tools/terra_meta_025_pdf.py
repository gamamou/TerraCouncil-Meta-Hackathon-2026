"""PDF deliverables from existing audited session artifacts; no model calls."""
import io,re,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,KeepTogether,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4

def _clean(line):
    line=re.sub(r"\*\*(.*?)\*\*",r"\1",line)
    line=re.sub(r"\x60([^\x60]*)\x60",r"\1",line)
    return html.escape(line).replace("&amp;","&amp;")

def generate(kind,data,language='fr',detailed=False):
    if language not in ('fr','en'):raise ValueError('Unsupported language')
    en=language=='en'
    if kind not in ("brief","passport"):raise ValueError("Invalid PDF kind")
    buf=io.BytesIO()
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SA_Title",parent=styles["Title"],fontSize=19,leading=24,
        textColor=HexColor("#12394c"),spaceAfter=16,alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="SA_Heading",parent=styles["Heading2"],fontSize=12,leading=16,
        textColor=HexColor("#146074"),spaceBefore=14,spaceAfter=6))
    styles.add(ParagraphStyle(name="SA_Text",parent=styles["BodyText"],fontSize=9.3,leading=14,spaceAfter=7))
    styles.add(ParagraphStyle(name="SA_Meta",parent=styles["BodyText"],fontSize=8.6,leading=13,
        textColor=HexColor("#4e6473"),spaceAfter=7))
    story=[Paragraph("SUSTAINAFRICA  /  FAITH  /  TERRACOUNCIL",styles["SA_Meta"]),
           Paragraph("Executive Decision Brief" if kind=="brief" else "Decision Passport",styles["SA_Title"])]
    def line(value,sty="SA_Text"):
        s=_clean(str(value or "")).strip()
        if s:story.append(Paragraph(s,styles[sty]))
    if kind=="brief" and not detailed:
        from reportlab.platypus import HRFlowable
        b=data.get("executive_brief") or {}
        conclusion=str(b.get("council_recommendations_verbatim") or "")
        critique=str(b.get("critic_assessment_verbatim") or "")
        question=str(data.get("question") or "")
        line("Strategic decision note" if en else "Note de décision stratégique","SA_Heading")
        line(("Decision issue: " if en else "Objet de la décision : ")+question[:500]+("…" if len(question)>500 else ""))
        line("Decision readiness" if en else "Maturité scientifique","SA_Heading")
        level=str(b.get("scientific_readiness") or "UNKNOWN")
        labels={"EVIDENCE_NOT_READY_FOR_SITE_PRESCRIPTIONS":
           ("Insufficient evidence for site-specific decisions" if en else "Preuves insuffisantes pour prescrire des interventions sur site")}
        line(labels.get(level,level))
        line("Unreviewed scientific draft — not an approved decision." if en else "Projet scientifique non revu — ne constitue pas une décision approuvée.","SA_Meta")
        def section(text,headers):
            lines=text.splitlines()
            for h in headers:
                for i,x in enumerate(lines):
                    if h.casefold() in x.casefold():
                        remainder=[y.strip() for y in lines[i+1:] if y.strip() and not y.lstrip().startswith("#")]
                        if remainder:return remainder[:4]
            return []
        lines=section(conclusion,["Conclusion provisoire","Conclusion","Synthèse","Synthesis","Recommendation"])
        if not lines:
            lines=[x.strip() for x in conclusion.splitlines() if len(x.strip())>60 and not x.strip().startswith(("#","|"))][-2:]
        line("Council recommendation" if en else "Orientation proposée par le Conseil","SA_Heading")
        for item in lines[:3]:line(item[:1250])
        line("Critical reservations" if en else "Réserves et objections","SA_Heading")
        objections=section(critique,["Conclusion","Synthèse","Synthesis","Limites scientifiques","Scientific limitations"])
        if not objections:
            objections=[x.strip() for x in critique.splitlines() if len(x.strip())>55 and not x.strip().startswith(("#","|"))][:2]
        for item in objections[:3]:line(item[:1000])
        line("Scientific limitations" if en else "Limites scientifiques","SA_Heading")
        for item in (b.get("evidence_limitations") or [])[:5]:line("• "+str(item))
        line("Required follow-up" if en else "Suite à donner","SA_Heading")
        tasks=(data.get("follow_up") or {}).get("proposed_investigations") or []
        for item in tasks[:4]:
            line("• "+str(item.get("action") or item.get("description") or item.get("task_id") or ""))
        line("Full scientific report available separately. Original council text and source trace preserved." if en else "Rapport scientifique détaillé disponible séparément. Délibération originale et traces conservées.","SA_Meta")
    elif kind=="brief":
        line("Scientific question" if en else "Question scientifique", "SA_Heading");line(data.get("question"))
        b=data.get("executive_brief") or {}
        line("Evidence status" if en else "Etat des preuves","SA_Heading")
        line(("Readiness: " if en else "Maturite : ")+str(b.get("scientific_readiness","Non disponible")))
        line("Working document. Human review required." if en else "Document de travail. Validation humaine requise.","SA_Meta")
        line("Council conclusions" if en else "Conclusions du Conseil", "SA_Heading")
        for raw in str(b.get("council_recommendations_verbatim") or "").splitlines():
            raw=raw.strip()
            if raw.startswith("#"):line(raw.lstrip("# ").strip(),"SA_Heading")
            elif raw.startswith(("- ","* ")):line("• "+raw[2:])
            else:line(raw)
        line("Critical assessment" if en else "Evaluation critique", "SA_Heading")
        for raw in str(b.get("critic_assessment_verbatim") or "").splitlines():
            raw=raw.strip()
            if raw.startswith("#"):line(raw.lstrip("# ").strip(),"SA_Heading")
            elif raw.startswith(("- ","* ")):line("• "+raw[2:])
            else:line(raw)
        line("Scientific limitations" if en else "Limites scientifiques", "SA_Heading")
        for item in b.get("evidence_limitations") or []:line("• "+str(item))
    else:
        line("Provenance and decision status" if en else "Provenance et statut de la decision", "SA_Heading")
        for k in ("session_id","passport_status","scientific_readiness","snapshot_id","trace_sha256"):
            if k in data:line(k.replace("_"," ").capitalize()+" : "+str(data[k]))
        human=data.get("human_review") or {}
        line("Human review" if en else "Revue humaine","SA_Heading")
        line(("Status: " if en else "Statut : ")+str(human.get("status","Non disponible")))
        line("Complete provenance metadata is retained in the source JSON." if en else "Les donnees de provenance detaillees figurent dans le JSON de reference.","SA_Meta")
        line("Passport details" if en else "Details du Passport","SA_Heading")
        for key,val in data.items():
            if key in ("session_id","passport_status","scientific_readiness","snapshot_id","trace_sha256","human_review"):continue
            line(key.replace("_"," ").capitalize(),"SA_Heading")
            if isinstance(val,dict):
                for k,v in val.items():line(str(k)+": "+str(v)[:1300])
            elif isinstance(val,list):
                for v in val[:45]:line("• "+str(v)[:1300])
            else:line(str(val))
    def footer(c,doc):
        c.setFont("Helvetica",8);c.setFillColor(HexColor("#657888"))
        c.drawString(42,30,"TerraCouncil | Draft - human review required" if en else "TerraCouncil | Document provisoire - revision humaine requise")
        c.drawRightString(550,30,str(doc.page))
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=43,leftMargin=43,
                          topMargin=44,bottomMargin=46,title="TerraCouncil "+kind)
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return buf.getvalue()
