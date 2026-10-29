"""Conservative French number and identifier pronunciation, no scientific paraphrase.

Only small integers and unambiguous decimal tokens are expanded. Date-like,
measurement-code and underscore identifiers stay review-required. Does not
remove text or change source trace.
"""
import re

UNITS=("zéro","un","deux","trois","quatre","cinq","six","sept","huit","neuf",
       "dix","onze","douze","treize","quatorze","quinze","seize",
       "dix-sept","dix-huit","dix-neuf")
TENS={20:"vingt",30:"trente",40:"quarante",50:"cinquante",60:"soixante"}
NUM=re.compile(r"(?<![\w])\d+(?:[.,]\d+)?(?![\w])")
IDENTIFIER=re.compile(r"\b[\w]+_[\w]+(?:_[\w]+)*\b")

def integer_words(n):
    if not 0<=n<=9999:
        raise ValueError("Numeric value outside conservative speech range")
    if n<20:return UNITS[n]
    if n<70:
        ten=(n//10)*10
        return TENS[ten]+(" et un" if n%10==1 else "-"+UNITS[n%10] if n%10 else "")
    if n<80:
        return "soixante"+(" et onze" if n==71 else "-"+integer_words(n-60))
    if n<100:
        return "quatre-vingts" if n==80 else "quatre-vingt-"+integer_words(n-80)
    if n<1000:
        q,r=divmod(n,100)
        prefix="cent" if q==1 else UNITS[q]+" cent"+("s" if r==0 else "")
        return prefix+(" "+integer_words(r) if r else "")
    q,r=divmod(n,1000)
    prefix="mille" if q==1 else integer_words(q)+" mille"
    return prefix+(" "+integer_words(r) if r else "")

def expand_unambiguous_numbers(text):
    if IDENTIFIER.search(text):
        raise ValueError("Technical identifier requires contextual speech rendering")
    # Slashed dates/codes or digit ranges require contextual handling.
    if re.search(r"\d\s*[/−–-]\s*\d",text):
        raise ValueError("Numeric dates, ranges or ratios require contextual interpretation")
    def repl(m):
        raw=m.group()
        if raw.count(".")+raw.count(",")>1:raise ValueError("Ambiguous numeric grouping")
        if "." in raw or "," in raw:
            a,b=re.split(r"[.,]",raw)
            if not a or not b or len(b)>2:
                raise ValueError("Decimal precision requires contextual review")
            if len(a)>1 and a[0]=="0":raise ValueError("Leading zeros require review")
            return integer_words(int(a))+" virgule "+" ".join(UNITS[int(ch)] for ch in b)
        if len(raw)>1 and raw[0]=="0":raise ValueError("Leading zeros require review")
        return integer_words(int(raw))
    return NUM.sub(repl,text)
