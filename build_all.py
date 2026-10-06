import json,re,difflib,glob
import os; ROOT=os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(ROOT,'build.py')).read().split('def parse')[0])   # CBid, ORD
exec('def strip_no0'+open(os.path.join(ROOT,'build.py')).read().split('def strip_no')[1].split('def align')[0])
CN='零一二三四五六七八九十'
JUAN={i:1 for i in range(1,8)}
NUMV={c:i for i,c in enumerate('零一二三四五六七八九十')}
def nv(no):
    if no in NUMV: return NUMV[no]
    if no and all(c in NUMV for c in no) and no.count('十')==1:
        a,b=no.split('十')
        return (NUMV[a] if a else 1)*10+(NUMV[b] if b else 0)
    return 999
def strip_no(c,no):
    c1=strip_no0(c,no)
    if c1!=c:
        c2=strip_no0(c1,'初')
        return c1 if c2==c1 else c1
    return c
def labeq(p,c,no='',count=None):
    cands={c,strip_no(c,no),strip_no0(strip_no0(c,no),'初')}
    if count and 0<count<=10: cands|={x+CN[count] for x in list(cands)}
    return p in cands
nodes={}; roots=[]; diffs=[]
def cb_match(pn,cands):
    best=(0,None)
    for c in cands:
        if labeq(pn['label'],c['label'],pn.get('no',''),c.get('count')): return c
        r=difflib.SequenceMatcher(None,pn['label'],strip_no(c['label'],pn.get('no',''))).ratio()
        if r>best[0]: best=(r,c)
    return best[1] if best[0]>=0.5 else None
def note_diff(pn,d):
    if not d: return
    pn['cbeta']=d; parts=[]
    if 'label' in d: parts.append(f"科名作「{d['label']}」")
    if 'cue' in d: parts.append(f"起止作〔{d['cue']}〕" if d['cue'] else '無起止語')
    if 'children_n' in d: parts.append(f"子科 {d['children_n']} 個")
    if 'unmatched' in d: parts.append('無對應科')
    pn['remark']='CBETA '+'；'.join(parts)
    diffs.append((pn['pdf_page'],pn.get('no'),pn['label'],d))
def align(pn,cn):
    if pn.get('_force'): cn=CBid[pn.pop('_force')]
    if cn is None: note_diff(pn,{'unmatched':True}); return
    pn['cbeta_id']=cn['id']; d={}
    if not labeq(pn['label'],cn['label'],pn.get('no',''),cn.get('count')): d['label']=cn['label']
    if (pn.get('cue') or pn.get('jing'))!=cn.get('cue') and not (pn.get('jing') and not pn.get('cue') and cn.get('cue') is None): d['cue']=cn.get('cue')
    pk=pn.get('children',[]); ck=cn.get('children',[])
    if not pn.get('continued') and len(ck)!=len(pk): d['children_n']=len(ck)
    note_diff(pn,d)
    if not pk: return
    if len(ck)==len(pk) and not pn.get('continued'):
        for a,b in zip(pk,ck): align(a,b)
    else:
        rest=list(ck)
        for a in pk:
            m=cb_match(a,rest)
            if m: rest.remove(m)
            align(a,m)
page_default=[0]
def resolve(u):
    cur=None
    for seg in u[5:].split('/'):
        cand=[v for v in nodes.values() if v['label']==seg] if cur is None else [v for v in cur.get('children',[]) if v['label']==seg]
        assert cand,('找不到路徑段',seg,u)
        cur=cand[0]
    return cur
def run(path,page):
    page_default[0]=page
    under=None; cbparent=None; stack=[]; seq=0; top=[]
    for ln in open(path,encoding='utf8'):
        if not ln.strip() or ln.startswith('#'): continue
        if ln.startswith('@title'):
            t=ln.split(None,1)[1].strip(); n={'id':'title-'+t,'label':t,'kind':'圖題','pdf_page':page,'juan':JUAN.get(page,1)}
            roots.append(n); nodes[n['id']]=n; under=n['id']; continue
        if ln.startswith('@under'):
            flush(under,cbparent,top); top=[]
            u=ln.split()[1]
            if u.startswith('path:'):
                segs=u[5:].split('/')
                cur=[v for v in nodes.values() if v['label']==segs[0]]
                for sg in segs[1:]:
                    cur=[c for v in cur for c in v.get('children',[]) if c['label']==sg]
                assert len(cur)==1, (u,len(cur))
                u=cur[0]['id']; cbparent=cur[0].get('cbeta_id')
            elif u.startswith('cb:'):
                u=next(k for k,v in nodes.items() if v.get('cbeta_id')==u[3:])
            under=u; continue
        if ln.startswith('@page'): page_default[0]=int(ln.split()[1]); continue
        if ln.startswith('@set'):
            _,p,kv=ln.split(None,2); k,v=kv.strip().split('=',1)
            tgt=resolve(p); tgt[k]=v; continue
        if ln.startswith('@cbparent'): cbparent=ln.split()[1]; continue
        dep=len(ln)-len(ln.lstrip(' ')); s=ln.strip()
        force=None
        mf=re.search(r' #cb=(\S+)',s)
        if mf: force=mf.group(1); s=(s[:mf.start()]+s[mf.end():]).rstrip()
        pg=page_default[0]
        mm=re.search(r'\s@(\d+)$',s)
        if mm: pg=int(mm.group(1)); s=s[:mm.start()].rstrip()
        note=None; ptitle=None
        if ' !' in s: s,note=s.split(' !',1)
        if ' %' in s: s,ptitle=s.split(' %',1)
        pin=None
        if ' &' in s: s,pin=s.split(' &',1)
        cont=s.endswith('…'); s=s.rstrip('…')
        unc=s.endswith('?'); s=s.rstrip('?')
        jing=None
        mj=re.search(r'【(.*?)】',s)
        if mj: jing=mj.group(1); s=s[:mj.start()]+s[mj.end():]
        no,rest=s.split(' ',1)
        m=re.match(r'^(.*?)(?:\((.*)\))?$',rest); lab,cue=m.group(1),m.group(2)
        seq+=1
        n={'id':f'p{page:03d}-{seq}','no':no,'label':lab}
        if cue: n['cue']=cue
        n['juan']=JUAN.get(pg,1); n['pdf_page']=pg
        if unc: n['uncertain']=True
        if force: n['_force']=force
        if jing: n['jing']=jing
        if pin: n['pin']=pin
        if cont: n['continued']=True
        if note: n['pdf_note']=note
        if ptitle: n['pdf_title']=ptitle
        while stack and stack[-1][0]>=dep: stack.pop()
        if stack: stack[-1][1].setdefault('children',[]).append(n)
        else: nodes[under].setdefault('children',[]).append(n); top.append(n)
        stack.append((dep,n)); nodes[n['id']]=n
    flush(under,cbparent,top)
def flush(under,cbparent,top):
    if not top: return
    if under and nodes[under].get('children'):
        ch=nodes[under]['children']
        if all('no' in x for x in ch): ch.sort(key=lambda x:nv(x['no']))
    cands=list(CBid[cbparent].get('children',[])) if cbparent else []
    if under and nodes[under].get('children'):
        taken={x.get('cbeta_id') for x in nodes[under]['children'] if x not in top}
        cands=[c for c in cands if c['id'] not in taken]
    for n in top:
        m=cb_match(n,cands)
        if m: cands.remove(m)
        align(n,m)
import os
PAGES=sorted(int(f[-7:-4]) for f in glob.glob(os.path.join(ROOT,'pdf_p*.txt')))
for page in PAGES:
    run(os.path.join(ROOT,f'pdf_p{page:03d}.txt'),page)
def settle(n):
    if n.get('continued') and n.get('cbeta_id') and n.get('children') and len(n.get('children',[]))==len(CBid[n['cbeta_id']].get('children',[])):
        del n['continued']
    for k in n.get('children',[]): settle(k)
for r in roots: settle(r)
cnt=[0]; pages_seen=set()
def c(n): cnt[0]+=1; pages_seen.add(n.get('pdf_page')); [c(k) for k in n.get('children',[])]
[c(r) for r in roots]
out={'meta':{'來源':'《大方廣佛華嚴經疏科文表解》PDF 為主，對照 CBETA X05n0231','已轉頁':sorted({x for x in pages_seen}),'節點總數':cnt[0],
  '欄位':{'no':'表解上的序號','label':'表解科名（不含序號）','cue':'表解括號內的起止語','pdf_page':'PDF 頁次（第1頁＝書頁11）',
   'pdf_title':'表解另起圖表時的圖題','pdf_note':'表解上的案語','continued':'此科的子科在後續頁面才出現（尚未轉錄完）',
   'cbeta_id':'對應的 CBETA 行號','cbeta':'CBETA 與表解不同之處（只列有差異的欄位）','uncertain':'掃描字跡不清，待人工確認',
   'remark':'差異摘要','kind':'圖題等非科判節點'}},'roots':roots}
json.dump(out,open(os.path.join(ROOT,'huayan_kewen_pdf.json'),'w'),ensure_ascii=False,indent=1)
print('nodes',cnt[0],'diffs',len(diffs))
for d in diffs:
    if d[0]==PAGES[-1]: print(d)
