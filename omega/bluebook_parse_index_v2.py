import re,os,json,collections,statistics
EVAL={'balloon':r'^ballo+ns?$|^balloon','aircraft':r'^aircraft|^a/c$|^airplane',
      'astro':r'^astro','satellite':r'^satell','insufficient':r'^insu[fv]+icien',
      'unidentified':r'^unidenti','hoax':r'^hoax','other':r'^other','radar':r'^radar'}
ERX={k:re.compile(v,re.I) for k,v in EVAL.items()}
MON={'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,
     'oct':10,'nov':11,'dec':12}
MONRX=re.compile(r'\b(january|february|march|april|may|june|july|august|september|'
                 r'october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\b',re.I)
rows=[]
for fn in sorted(os.listdir("idx")):
    y=int(fn[:4]); var=fn[5:-4]
    s=open(f"idx/{fn}",encoding='utf-8',errors='replace').read()
    pages=re.split(r'<OBJECT\b',s)[1:]
    for pi,pg in enumerate(pages):
        W=[(int(m[0]),int(m[1]),m[4]) for m in
           re.findall(r'<WORD coords="(\d+),(\d+),(\d+),(\d+)"[^>]*>([^<]*)</WORD>',pg)]
        if not W: continue
        # month from the page header region (small y)
        hdr=" ".join(t for x,yy,t in W if yy<460)
        mh=[MON[m.group(1).lower()[:3]] for m in MONRX.finditer(hdr)]
        month=collections.Counter(mh).most_common(1)[0][0] if mh else None
        ev=[]
        for x,yy,t in W:
            tt=re.sub(r'[^A-Za-z/]','',t)
            for k,rx in ERX.items():
                if rx.match(tt): ev.append((x,yy,k)); break
        if len(ev)<3: continue
        xs=[e[0] for e in ev]; gate=statistics.median(xs)-250
        seen=set()
        for x,yy,k in ev:
            if x<gate: continue
            key=round(yy/20)
            if key in seen: continue
            seen.add(key)
            loc=[t for xx,y2,t in W if abs(y2-yy)<22 and 440<xx<x-100]
            day=[t for xx,y2,t in W if abs(y2-yy)<22 and xx<440 and re.fullmatch(r'\d{1,2}',t.strip())]
            rows.append(dict(year=y,month=month,
                             day=int(day[0]) if day else None,
                             variant=var,page=pi,y=yy,eval=k,
                             row=re.sub(r'\s+',' '," ".join(loc))[:100]))
print(f"rows: {len(rows)}")
print(f"with month: {sum(1 for r in rows if r['month'])} ({sum(1 for r in rows if r['month'])*100//len(rows)}%)")
print(f"with day:   {sum(1 for r in rows if r['day'])} ({sum(1 for r in rows if r['day'])*100//len(rows)}%)")
def norm(t): return re.sub(r'[^a-z]','',t.lower())
best={}
for r in rows:
    k=(r['year'],r['month'],r['eval'],norm(r['row'])[:22])
    if k not in best or len(r['row'])>len(best[k]['row']): best[k]=r
ded=list(best.values())
print(f"after dedupe (now including month in the key): {len(ded)}")
c=collections.Counter(r['eval'] for r in ded); tot=sum(c.values())
for k,v in c.most_common(): print(f"  {k:<14}{v:>6} ({v*100/tot:.1f}%)")
print(f"  UNIDENTIFIED={c['unidentified']}")
mm=collections.Counter(r['month'] for r in ded)
print(f"month distribution: {dict(sorted((k,v) for k,v in mm.items() if k))}")
json.dump(ded,open("bluebook_evaluations_v2.json","w"),indent=0)
print("wrote bluebook_evaluations_v2.json")
