import json,re,sys,difflib
cb=json.load(open('/mnt/user-data/outputs/huayan_kewen_X0231.json'))
CBid={}
def idx(n,p):
    CBid[n['id']]=n; n['_p']=p
    for c in n.get('children',[]): idx(c,n)
for r in cb['roots']: idx(r,None)
ORD=re.compile(r'^(初|次|後|[一二三四五六七八九十]+)')
def parse(path,page,juan):
    roots=[];stack=[];title=None;seq=0
    for ln in open(path,encoding='utf8'):
        if not ln.strip() or ln.startswith('#'): continue
        if ln.startswith('@title'): title=ln.split(None,1)[1].strip(); continue
        dep=len(ln)-len(ln.lstrip(' ')); s=ln.strip()
        unc=s.endswith('?'); s=s.rstrip('?')
        no,rest=s.split(' ',1)
        m=re.match(r'^(.*?)(?:\((.*)\))?$',rest); lab,cue=m.group(1),m.group(2)
        seq+=1
        n={'id':f'p{page:03d}-{seq}','no':no,'label':lab}
        if cue: n['cue']=cue
        n['juan']=juan; n['pdf_page']=page
        if unc: n['uncertain']=True
        while stack and stack[-1][0]>=dep: stack.pop()
        (stack[-1][1].setdefault('children',[]) if stack else roots).append(n)
        stack.append((dep,n))
    return title,roots
CN='零一二三四五六七八九十'
def strip_no(c,no):
    for pre in ([no] if no else [])+(['初','次','後'] if no in ('一','二','三','') else []):
        if pre and c.startswith(pre): return c[len(pre):]
    return c
def labeq(p,c,no='',count=None):
    s=strip_no(c,no)
    cands={c,s}
    if count and 0<count<=10: cands|={c+CN[count],s+CN[count]}
    return p in cands
def align(pn,cn,diffs):
    pn['cbeta_id']=cn['id']
    d={}
    if not labeq(pn['label'],cn['label'],pn.get('no',''),cn.get('count')): d['label']=cn['label']
    if pn.get('cue')!=cn.get('cue'): d['cue']=cn.get('cue')
    pk=pn.get('children',[]); ck=cn.get('children',[])
    if cn.get('count') is not None and cn['count']!=len(pk): d['count']=cn['count']
    if len(ck)!=len(pk): d['children_n']=len(ck)
    if d:
        pn['cbeta']=d
        parts=[]
        if 'label' in d: parts.append(f"科名作「{d['label']}」")
        if 'cue' in d: parts.append(f"起止作〔{d['cue']}〕" if d['cue'] else '無起止語')
        if 'children_n' in d: parts.append(f"子科 {d['children_n']} 個")
        pn['remark']='CBETA '+('；'.join(parts))
        diffs.append((pn['pdf_page'],pn['no'],pn['label'],d))
    if len(ck)==len(pk):
        for a,b in zip(pk,ck): align(a,b,diffs)
    else:  # 依標題相似度配對
        used=set()
        for a in pk:
            best=max(((difflib.SequenceMatcher(None,a['label'],ORD.sub('',b['label'],1)).ratio(),i) for i,b in enumerate(ck) if i not in used),default=(0,None))
            if best[0]>=0.5: used.add(best[1]); align(a,ck[best[1]],diffs)
            else: a['cbeta']={'unmatched':True}; a['remark']='CBETA 無對應'; diffs.append((a['pdf_page'],a['no'],a['label'],{'unmatched':True}))
