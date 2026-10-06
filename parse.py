import re, json
from lxml import etree
T='{http://www.tei-c.org/ns/1.0}'; CB='{http://www.cbeta.org/ns/1.0}'
t=etree.parse('/tmp/x0231.xml'); body=t.find('.//'+T+'body')
NUM=re.compile(r'^[一二三四五六七八九十百]+$')
MARK=re.compile(r'[○〇△▲]')
def text_of(el):
    """item 自身文字（不含子 list、行內 note、校勘 rdg）"""
    out=[]
    def walk(e):
        tag=e.tag
        if tag in (T+'list',T+'note',T+'rdg'): 
            if e.tail: out.append(e.tail); 
            return
        if tag not in (T+'item',): 
            if e.text: out.append(e.text)
        for c in e: walk(c)
        if e is not el and e.tail: out.append(e.tail)
    if el.text: out.append(el.text)
    for c in el: walk(c)
    return re.sub(r'\s+','',''.join(out))
juan=[0]
def build(item):
    note=None
    for n in item.findall(T+'note'):
        if n.get('place')=='inline': note=re.sub(r'\s+','',''.join(n.itertext())); break
    label=text_of(item)
    node={'id':item.get('{http://www.w3.org/XML/1998/namespace}id','').replace('item',''),
          'juan':juan[0],'label':label,'note':note,
          'count':None,'cue':None,'children':[]}
    if note is not None:
        if NUM.match(note): node['count']=note
        else: node['cue']=note
    for l in item.findall(T+'list'):
        for it in l.findall(T+'item'): node['children'].append(build(it))
    return node
# 依文件順序走訪 body，記錄卷次與頂層 list
frags=[]
def scan(e):
    for c in e:
        if c.tag==CB+'juan' and c.get('fun')=='open': juan[0]=int(c.get('n'))
        if c.tag==T+'list':
            for it in c.findall(T+'item'): frags.append(build(it))
        elif c.tag!=T+'item': scan(c)
scan(body)
json.dump(frags,open('frags.json','w'),ensure_ascii=False)
print('頂層片段',len(frags))
