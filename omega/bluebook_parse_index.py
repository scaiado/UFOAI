import re,os,json,collections,statistics
EVAL={'balloon':r'^ballo+ns?$|^balloon','aircraft':r'^aircraft|^a/c$|^airplane',
      'astro':r'^astro','satellite':r'^satell','insufficient':r'^insu[fv]+icien',
      'unidentified':r'^unidenti','hoax':r'^hoax','other':r'^other','radar':r'^radar'}
ERX={k:re.compile(v,re.I) for k,v in EVAL.items()}
rows=[]
perfile={}
for fn in sorted(os.listdir("idx")):
    y=int(fn[:4]); var=fn[5:-4]
    s=open(f"idx/{fn}",encoding='utf-8',errors='replace').read()
    pages=re.split(r'<OBJECT\b',s)[1:]
    got=0
    for pi,pg in enumerate(pages):
        words=re.findall(r'<WORD coords="(\d+),(\d+),(\d+),(\d+)"[^>]*>([^<]*)</WORD>',pg)
        if not words: continue
        W=[(int(a),int(b),int(c),int(d),e) for a,b,c,d,e in words]
        ev=[]
        for x0,y0,x1,y1,t in W:
            tt=re.sub(r'[^A-Za-z/]','',t)
            for k,rx in ERX.items():
                if rx.match(tt): ev.append((x0,y0,k,t)); break
        if len(ev)<3: continue
        xs=[e[0] for e in ev]; gate=statistics.median(xs)-250
        seen=set()
        for x0,y0,k,t in ev:
            if x0<gate: continue
            key=(pi,round(y0/20))
            if key in seen: continue
            seen.add(key)
            loc=[w for w in W if abs(w[1]-y0)<22 and w[0]<x0-120]
            loc.sort(key=lambda w:w[0])
            txt=" ".join(w[4] for w in loc)
            rows.append(dict(year=y,variant=var,page=pi,y=y0,eval=k,
                             row=re.sub(r'\s+',' ',txt)[:100]))
            got+=1
    perfile[fn]=got
print(f"total evaluation rows across 46 files: {len(rows)}")
# dedupe across the two scan variants, per year, by (eval, normalised location text)
def norm(t):
    return re.sub(r'[^a-z]','',t.lower())[:22]
best={}
for r in rows:
    k=(r['year'],r['eval'],norm(r['row']))
    if k not in best or len(r['row'])>len(best[k]['row']): best[k]=r
ded=list(best.values())
print(f"after cross-variant dedupe: {len(ded)}")
c=collections.Counter(r['eval'] for r in ded)
tot=sum(c.values())
print("\nFULL BLUE BOOK EVALUATION DISTRIBUTION (recovered)")
for k,v in c.most_common(): print(f"  {k:<14}{v:>6} ({v*100/tot:.1f}%)")
unid=c['unidentified']
print(f"\n  RESOLVED={tot-unid}  UNIDENTIFIED={unid}  ({unid*100/tot:.1f}%)")
print("\nPER-YEAR RECOVERY")
py=collections.Counter(r['year'] for r in ded)
pu=collections.Counter(r['year'] for r in ded if r['eval']=='unidentified')
print(f"  {'year':>5}{'rows':>7}{'unid':>7}{'unid%':>8}")
for y in sorted(py): print(f"  {y:>5}{py[y]:>7}{pu[y]:>7}{pu[y]*100/py[y]:>7.1f}%")
json.dump(ded,open("bluebook_evaluations.json","w"),indent=0)
print(f"\nwrote bluebook_evaluations.json ({len(ded)} labelled rows)")
print("\nVALIDATION: Project Blue Book's own final accounting is 12,618 total")
print("sightings. Recovered row count above is the comparison figure.")
