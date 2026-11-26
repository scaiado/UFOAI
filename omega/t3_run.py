import json,os,re,sys,math,collections
import numpy as np
sys.path.insert(0,'/home/user/UFOAI/omega')
import phase6
RNG=np.random.default_rng(31337)
labs={}
for fn in ('t3_labels.json','t3_labels_v2.json'):
    if os.path.exists(fn):
        for r in json.load(open(fn)):
            labs.setdefault(r['id'],r)   # first file wins (larger recall set)
have={x[:-4] for x in os.listdir('txt') if x.endswith('.txt')}
rows=[]
for i,r in labs.items():
    if i not in have: continue
    s=open(f'txt/{i}.txt',encoding='utf-8',errors='replace').read()
    hits=[]
    for k,rx in phase6.KRX.items():
        m=rx.search(s)
        if m: hits.append((m.start(),k))
    if len(hits)<2: continue
    hits.sort()
    rows.append(dict(id=i,year=r['year'],lab=('UNID' if r['eval']=='unidentified' else 'RES'),
                     ev=r['eval'],kin=[k for _,k in hits],n=len(s)))
c=collections.Counter(r['lab'] for r in rows)
print(f'T3 dataset: {len(rows)} cases  {dict(c)}')
yu=collections.Counter(r['year'] for r in rows if r['lab']=='UNID')
yr=collections.Counter(r['year'] for r in rows if r['lab']=='RES')
yrs=[y for y in sorted(yu) if yu[y]>=2 and yr.get(y,0)>=2]
print(f'years with >=2 in both arms: {len(yrs)} -> {yrs}')
sel=[r for r in rows if r['year'] in yrs]
cu=[r for r in sel if r['lab']=='UNID']; cr=[r for r in sel if r['lab']=='RES']
print(f'year-matched subset: UNID={len(cu)} RES={len(cr)}')
def ce(sq):
    bi=collections.Counter(); pre=collections.Counter()
    for q in sq:
        for a,b in zip(q,q[1:]): bi[(a,b)]+=1; pre[a]+=1
    N=sum(bi.values())
    if N==0: return float('nan')
    return -sum((v/N)*math.log2(v/pre[a]) for (a,b),v in bi.items())
def gain(sq,nperm=600):
    if len(sq)<15: return None
    H=ce(sq)
    nl=np.array([ce([list(RNG.permutation(q)) for q in sq]) for _ in range(nperm)])
    return H, float(nl.mean()), float(nl.std(ddof=1)), float((1+int((nl<=H).sum()))/(nperm+1))
print()
print('=== T3  kinematic sequence structure, UNIDENTIFIED vs RESOLVED ===')
for nm,g in (('UNIDENTIFIED',cu),('RESOLVED',cr)):
    r=gain([x['kin'] for x in g])
    if not r: print(f'  {nm:<14} n={len(g):<5} too few'); continue
    H,mu,sd,p=r
    print(f'  {nm:<14} n={len(g):<5} H={H:.4f}  shuffled_null={mu:.4f}+/-{sd:.4f}  '
          f'gain={mu-H:+.4f}  p={p:.4f}')
# size-matched comparison
if len(cu)>=15 and len(cr)>=len(cu):
    gu=gain([x['kin'] for x in cu])
    sub=[]
    for _ in range(120):
        pick=RNG.choice(len(cr),size=len(cu),replace=False)
        r=gain([cr[i]['kin'] for i in pick],nperm=150)
        if r: sub.append(r[1]-r[0])
    sub=np.array(sub)
    print(f'\n  size-matched RESOLVED gain (n={len(cu)}): {sub.mean():+.4f} +/- {sub.std(ddof=1):.4f}')
    print(f'  UNIDENTIFIED gain: {gu[1]-gu[0]:+.4f}')
    pr=(1+int((sub>=(gu[1]-gu[0])).sum()))/(len(sub)+1)
    print(f'  one-sided p (UNID gain >= matched RES gain): {pr:.4f}')
    # POWER: what gain difference would be detectable at this n?
    print(f'\n  POWER: sd of the size-matched resolved gain is {sub.std(ddof=1):.4f} bits.')
    print(f'  Minimum detectable difference at alpha=0.05, 80% power ~ 2.5 sd = '
          f'{2.5*sub.std(ddof=1):.4f} bits.')
    print(f'  Phase 6 measured the MID-vs-nonMID difference at 0.112 bits.')
print()
print('=== T3d  descriptors appearing ONLY in one arm ===')
du=collections.Counter(k for x in cu for k in x['kin'])
dr=collections.Counter(k for x in cr for k in x['kin'])
print("  %-12s%8s%8s%8s" % ('descriptor','UNID%','RES%','ratio'))
for k in sorted(set(du)|set(dr)):
    a=du[k]/max(1,len(cu)); b=dr[k]/max(1,len(cr))
    rt = (a/b) if b else float('inf')
    print('  %-12s%6.1f%%%6.1f%%%8.2f' % (k, a*100, b*100, rt))
only_u=[k for k in du if not dr.get(k)]
only_r=[k for k in dr if not du.get(k)]
print(f'  descriptors only in UNID: {only_u}')
print(f'  descriptors only in RES : {only_r}')
