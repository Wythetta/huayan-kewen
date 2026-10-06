import json,re,difflib
import os; ROOT=os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(ROOT,'stitch.py')).read().split('# 依文件順序')[0])   # 重用 clean()
order=[]
def collect(n,fi):
    if n['stub']: order.append((fi,n))
    for c in n['children']: collect(c,fi)
for fi,f in enumerate(fr): collect(f,fi)
def norm(s): return re.sub(r'[第分〔〕]|大文','',s)
used={}; log=[]
def attach(s,f,how):
    used[id(s)]=f['id']
    s['children']=f['children']; s['note']=f['note']; s['count']=f['count']; s['cue']=f['cue']
    s['expanded_from']=f['id']; s['expand_mark']=f['mark']; s['match']=how
    if how!='exact': log.append((how,f['juan'],s['label'],f['label']))
merged=set()
# 第一輪：完全同名（含品首）
for fi,f in enumerate(fr):
    if f['mark'] is None: continue
    c=[s for sfi,s in order if sfi<fi and id(s) not in used and s['label']==f['label']]
    if c: attach(c[-1],f,'exact'); merged.add(fi)
# 第二輪：近似同名，只在同卷或前一卷內找
for fi,f in enumerate(fr):
    if fi in merged or f['mark'] is None: continue
    best=None
    for sfi,s in order:
        if sfi>=fi or id(s) in used: continue
        if fr[sfi]['juan'] < f['juan']-1: continue
        a,b=norm(s['label']),norm(f['label'])
        if f['mark']=='品首':
            sc=1.0 if (a in b and len(a)>=3) else 0
        else:
            if a[:1]!=b[:1]: continue
            sc=difflib.SequenceMatcher(None,a,b).ratio()
        if best is None or sc>=best[0]: best=(sc,s)
    if best and best[0]>=0.6:
        attach(best[1],f,'fuzzy %.2f'%best[0]); merged.add(fi)
roots=[f for fi,f in enumerate(fr) if fi not in merged]
unused=[s for _,s in order if id(s) not in used]
print('縫合',len(used),'| 剩餘頂層',len(roots),'| 未展開stub',len(unused))
for l in log: print('  ',l)
print('--- 未展開 stub'); [print('  ',s['juan'],s['label']) for s in unused]
print('--- 頂層'); [print('  ',f['juan'],f['mark'],f['label']) for f in roots if f['mark']!='品首']
json.dump(roots,open(os.path.join(ROOT,'stitched.json'),'w'),ensure_ascii=False)
