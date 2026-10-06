import json,sys
import os; ROOT=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(os.path.join(ROOT,'huayan_kewen_X0231.json')))
key=sys.argv[1]; mx=int(sys.argv[2]) if len(sys.argv)>2 else 4
def pr(n,dep):
    print('  '*dep+n['label']+'  '+n['id']+('  ['+str(n.get('count'))+']' if n.get('count') else ''))
    if dep<mx:
        for c in n.get('children',[]): pr(c,dep+1)
def walk(n):
    if key in n['label']: pr(n,0); print('----')
    for c in n.get('children',[]): walk(c)
for r in d['roots']: walk(r)
