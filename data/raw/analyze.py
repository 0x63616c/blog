import json,glob,statistics as st,sys,collections,os
def pct(v,p):
    v=sorted(v); 
    if not v: return float('nan')
    k=(len(v)-1)*p/100; f=int(k); c=min(f+1,len(v)-1); return v[f]+(v[c]-v[f])*(k-f)
def rows(f):
    out=[]
    for l in open(f):
        try: out.append(json.loads(l))
        except: pass
    return out
def summ(rs,key='wall_ms'):
    v=[r[key] for r in rs]
    return dict(n=len(v),p50=pct(v,50),p95=pct(v,95),p99=pct(v,99),mean=sum(v)/len(v))
if __name__=='__main__':
    for f in sorted(glob.glob(sys.argv[1])):
        rs=rows(f); ph=collections.defaultdict(list)
        for r in rs: ph[r['phase']].append(r)
        print(f)
        for p,v in ph.items():
            s=summ(v); g=summ(v,'gpu_total_ms') if 'gpu_total_ms' in v[0] else None
            print(f"  {p:12s} n={s['n']:3d} wall p50={s['p50']:.1f} p95={s['p95']:.1f} fps50={1000/s['p50']:.0f} gpu p50={g['p50']:.1f} mesh_sync p50={pct([r.get('mesh_sync_ms',0) for r in v],50):.2f} enc={pct([r.get('encode_ms',0) for r in v],50):.2f} draws={v[0].get('draws')} tris={v[0].get('triangles')} up={pct([r.get('upload_bytes',0) for r in v],50):.0f}")
