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

def generate(kind,data):
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
    if kind=="brief":
        line("Question scientifique", "SA_Heading");line(data.get("question"))
        b=data.get("executive_brief") or {}
        line("Etat des preuves","SA_Heading")
        line("Maturite : "+str(b.get("scientific_readiness","Non disponible")))
        line("Document de travail. Validation humaine requise.","SA_Meta")
        line("Conclusions du Conseil", "SA_Heading")
        for raw in str(b.get("council_recommendations_verbatim") or "").splitlines():
            raw=raw.strip()
            if raw.startswith("#"):line(raw.lstrip("# ").strip(),"SA_Heading")
            elif raw.startswith(("- ","* ")):line("• "+raw[2:])
            else:line(raw)
        line("Evaluation critique", "SA_Heading")
        for raw in str(b.get("critic_assessment_verbatim") or "").splitlines():
            raw=raw.strip()
            if raw.startswith("#"):line(raw.lstrip("# ").strip(),"SA_Heading")
            elif raw.startswith(("- ","* ")):line("• "+raw[2:])
            else:line(raw)
        line("Limites scientifiques", "SA_Heading")
        for item in b.get("evidence_limitations") or []:line("• "+str(item))
    else:
        line("Provenance et statut de la decision", "SA_Heading")
        for k in ("session_id","passport_status","scientific_readiness","snapshot_id","trace_sha256"):
            if k in data:line(k.replace("_"," ").capitalize()+" : "+str(data[k]))
        human=data.get("human_review") or {}
        line("Revue humaine","SA_Heading")
        line("Statut : "+str(human.get("status","Non disponible")))
        line("Les donnees de provenance detaillees figurent dans le JSON de reference.","SA_Meta")
        line("Details du Passport","SA_Heading")
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
        c.drawString(42,30,"TerraCouncil  |  Document provisoire - revision humaine requise")
        c.drawRightString(550,30,str(doc.page))
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=43,leftMargin=43,
                          topMargin=44,bottomMargin=46,title="TerraCouncil "+kind)
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return buf.getvalue()
