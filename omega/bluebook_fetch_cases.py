import json,subprocess,time,re,os,sys,random
ids=[l.strip() for l in open("ids.txt") if l.strip()]
random.seed(int(sys.argv[2]) if len(sys.argv)>2 else 7)
N=int(sys.argv[1])
# stratify by leading year in the identifier
def yr(i):
    m=re.match(r'(\d{4})-',i)
    return int(m.group(1)) if m else 0
by={}
for i in ids: by.setdefault(yr(i),[]).append(i)
pick=[]
years=sorted(k for k in by if 1947<=k<=1969)
per=max(1,N//max(1,len(years)))
for y in years:
    random.shuffle(by[y]); pick += by[y][:per]
random.shuffle(pick); pick=pick[:N]
os.makedirs("txt",exist_ok=True)
got=0
for k,ident in enumerate(pick):
    fn=f"txt/{ident}.txt"
    if os.path.exists(fn): got+=1; continue
    u=f"https://archive.org/cors/{ident}/{ident}_djvu.txt"
    r=subprocess.run(["curl","-sS","--max-time","45","-o",fn,"-w","%{http_code} %{size_download}",u],
                     capture_output=True,text=True)
    p=r.stdout.strip().split()
    if p and p[0]=="200" and int(p[1])>200: got+=1
    else:
        try: os.remove(fn)
        except Exception: pass
    if (k+1)%50==0: print(f"  {k+1}/{len(pick)} ok={got}",flush=True)
    time.sleep(0.25)
print(f"FETCHED ok={got} of {len(pick)} attempted")
