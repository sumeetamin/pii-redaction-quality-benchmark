"""Regex PII redaction baseline and exact-span benchmark for labeled text."""
import argparse,json,re
from pathlib import Path
import pandas as pd
PATTERNS={"email":re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),"ssn":re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),"phone":re.compile(r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]?\d{3}[ .-]?\d{4}(?!\d)")}
def detect(text):
 return sorted([(m.start(),m.end(),kind) for kind,pat in PATTERNS.items() for m in pat.finditer(str(text))])
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",required=True);p.add_argument("--text",default="text");p.add_argument("--gold-spans",default="gold_spans_json",help="JSON list of {start,end,type} spans");p.add_argument("--out",default="outputs");a=p.parse_args()
 d=pd.read_csv(a.input);pred=[detect(x) for x in d[a.text]];tp=fp=fn=0
 for raw,got in zip(d.get(a.gold_spans,pd.Series(["[]"]*len(d))),pred):
  goldraw=json.loads(raw) if isinstance(raw,str) else (raw if isinstance(raw,list) else [])
  gold={(int(s["start"]),int(s["end"]),str(s["type"]).lower()) for s in goldraw};guess=set(got);tp+=len(gold&guess);fp+=len(guess-gold);fn+=len(gold-guess)
 def redact(s,spans):
  text=str(s)
  for start,end,kind in sorted(spans,reverse=True):text=text[:start]+f"[REDACTED:{kind}]"+text[end:]
  return text
 output=pd.DataFrame({"redacted_text":[redact(x,spans) for x,spans in zip(d[a.text],pred)],"detected_spans":[json.dumps(s) for s in pred]})
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True);output.to_csv(out/"redacted.csv",index=False)
 report={"rows":len(d),"true_positive_spans":tp,"false_positive_spans":fp,"false_negative_spans":fn,"precision":tp/max(1,tp+fp),"recall":tp/max(1,tp+fn),"f1":2*tp/max(1,2*tp+fp+fn),"note":"Regex baseline; validate on representative text, locales, and adversarial formatting."}
 (out/"metrics.json").write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=="__main__":main()
