# 產生 待查清單_自動.md：字跡不清(?)、CBETA 無對應、子科數不同、表解共用子科等
import json,glob,re
import os; ROOT=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(os.path.join(ROOT,'huayan_kewen_pdf.json')))
rows={'unc':[],'unm':[],'cnt':[],'shared':[],'cont':[]}
def w(n,path):
    p=path+[n['label']]; loc=f"p{n.get('pdf_page','?'):>3}｜{'／'.join(p[-4:])}"
    if n.get('uncertain'): rows['unc'].append(f"- {loc}　{n.get('pdf_note','')}")
    r=n.get('remark','')
    if '無對應科' in r and n.get('pdf_page',0)>0 and not n.get('pin') and n.get('no'): rows['unm'].append(f"- {loc}")
    if '子科' in r: rows['cnt'].append(f"- {loc}　{r}")
    if '共用' in n.get('pdf_note',''): rows['shared'].append(f"- {loc}　{n['pdf_note']}")
    if n.get('continued'): rows['cont'].append(f"- {loc}")
    for k in n.get('children',[]): w(k,p)
for r in d['roots']: w(r,[])
T={'unc':'字跡不清（標 ?）','unm':'CBETA 無對應科','cnt':'子科數與 CBETA 不同','shared':'表解共用子科（JSON 已分別展開）','cont':'尚未續完（標 …）'}
out=['# 待查清單（自動產生，check_list.py）\n']
for k,t in T.items():
    out.append(f"## {t}（{len(rows[k])}）\n"+('\n'.join(rows[k]) or '（無）')+'\n')
open(os.path.join(ROOT,'待查清單_自動.md'),'w').write('\n'.join(out))
print({k:len(v) for k,v in rows.items()})
