import json,re
import os; ROOT=os.path.dirname(os.path.abspath(__file__))
fr=json.load(open(os.path.join(ROOT,'frags.json')))
PIN='\U000F3BA7'  # CB15271 私用字（原書品首符號）
MK=re.compile(r'^([○〇△▲]|'+PIN+')')
def clean(n):
    lab=n['label']; mark=None
    m=MK.match(lab)
    if m: mark={'○':'○','〇':'○','△':'△','▲':'▲',PIN:'品首'}[m.group(1)]; lab=lab[1:]
    stub=False
    if lab.endswith('○') and not n['children'] and n['note'] is None:
        stub=True; lab=lab[:-1]
    n['label']=lab.replace(PIN,'')
    n['mark']=mark; n['stub']=stub
    for c in n['children']: clean(c)
for f in fr: clean(f)
# 依文件順序收集 stub（含位置序號），片段依序匹配最早的同名未匹配 stub
order=[]
def collect(n,fi):
    if n['stub']: order.append((fi,n))
    for c in n['children']: collect(c,fi)
roots=[]; unmatched_frag=[]; used=set()
for fi,f in enumerate(fr): collect(f,fi)
for fi,f in enumerate(fr):
    if f['mark'] in ('○','△','▲'):
        cand=[s for (sfi,s) in order if sfi<fi and id(s) not in used and s['label']==f['label']]
        if cand:
            s=cand[0]; used.add(id(s))
            s['children']=f['children']; s['note']=f['note']; s['count']=f['count']; s['cue']=f['cue']
            s['expanded_from']=f['id']; s['expand_mark']=f['mark']
            continue
        unmatched_frag.append(f)
    roots.append(f)
unused=[s for (_,s) in order if id(s) not in used]
print('縫合成功',len(used),'未匹配片段',len(unmatched_frag),'未展開stub',len(unused),'剩餘頂層',len(roots))
for f in unmatched_frag: print('  片段:',f['juan'],f['label'])
for s in unused: print('  stub:',s['juan'],s['id'],s['label'])
json.dump({'roots':roots},open(os.path.join(ROOT,'stitched.json'),'w'),ensure_ascii=False)
