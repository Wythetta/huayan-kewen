import json,re,difflib
exec(open('stitch3.py').read().split("json.dump(roots")[0].replace("print(","(lambda *a,**k:None)("))
CN={c:i+1 for i,c in enumerate('一二三四五六七八九十')}
def num(s):
    if not re.fullmatch(r'[一二三四五六七八九十]+',s or ''): return None
    if s=='十': return 10
    if s[0]=='十' and len(s)==2: return 10+CN[s[1]]
    if len(s)==2 and s[1]=='十': return CN[s[0]]*10
    if len(s)==3 and s[1]=='十': return CN[s[0]]*10+CN[s[2]]
    if len(s)==1: return CN[s]
    return None
mism=[]
def fin(x,path):
    ch=x['children']; note=x['note']
    x['count']=None; x['cue']=None
    if note is not None:
        if ch and num(note) is not None: x['count']=num(note)
        else: x['cue']=note          # 葉節點上的數字字樣視為起止語
    if x['count'] is not None and x['count']!=len(ch):
        mism.append({'id':x['id'],'juan':x['juan'],'label':x['label'],'標示子科數':x['count'],'實際子節點數':len(ch)})
    out={'id':x['id'],'juan':x['juan'],'label':x['label']}
    if x['count'] is not None: out['count']=x['count']
    if x['cue'] is not None: out['cue']=x['cue']
    if x.get('mark'): out['mark']=x['mark']
    if x.get('stub'):
        out['stub']=True
        if x.get('expanded_from'): out['expanded_from']=x['expanded_from']; out['match']=x['match']
    if ch: out['children']=[fin(c,path) for c in ch]
    return out
final_roots=[fin(r,[]) for r in roots]
# 審核清單
fuzzy=[{'match':h,'juan':j,'stub標題':a,'展開處標題':b} for h,j,a,b in log]
orph=[r for r in roots[2:] if r['mark']!='品首']
sugg=[]
for f in orph:
    cands=sorted(((difflib.SequenceMatcher(None,norm(s['label']),norm(f['label'])).ratio(),s) for s in unused),key=lambda t:-t[0])
    sc,s=cands[0] if cands else (0,None)
    sugg.append({'片段id':f['id'],'juan':f['juan'],'片段標題':f['label'],
                 '建議stub':(s['label'] if s and sc>=0.5 else None),'建議stub_id':(s['id'] if s and sc>=0.5 else None),'相似度':round(sc,2)})
cnt=[0]
def c(n): cnt[0]+=1; [c(k) for k in n.get('children',[])]
[c(r) for r in final_roots]
data={'meta':{
  '來源':'CBETA X05n0231《華嚴經疏科文》XML（cbeta-org/xml-p5）',
  '定位':'參考底稿，與《大方廣佛華嚴經疏科文表解》PDF 有出入之處以 PDF 為準',
  '節點總數':cnt[0],
  'roots說明':'roots[0]=疏鈔序科文；roots[1]=正文總科；其餘為尚未掛回主樹的品首段落或斷點片段（依原文順序）',
  '欄位':{'id':'CBETA 行號（X05p頁碼欄行）','juan':'卷次','label':'科名（含序號字）','count':'原文標示的子科數（有子節點者）',
          'cue':'起止語（疏文起首二字）','mark':'原文段首符號 ○/△/▲/品首','stub':'原文在此處以○略記、後文另行展開',
          'expanded_from':'展開段落所在行號','match':'縫合方式 exact/fuzzy 相似度'}},
 'roots':final_roots,
 'review':{'近似縫合_請核對':fuzzy,'子科數不符':mism,
   '未展開的stub':[{'id':s['id'],'juan':s['juan'],'label':s['label']} for s in unused],
   '未掛接的片段':sugg}}
json.dump(data,open('/mnt/user-data/outputs/huayan_kewen_X0231.json','w'),ensure_ascii=False,indent=1)
print('節點',cnt[0],'頂層',len(final_roots),'近似',len(fuzzy),'不符',len(mism),'未展開',len(unused),'孤立片段',len(sugg))
for m in mism[:25]: print(' ',m['juan'],m['label'],m['標示子科數'],m['實際子節點數'])
for s in sugg: print(' ',s)
