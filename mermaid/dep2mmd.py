import json, sys
try:
    data=json.load(open('mermaid/dep.json'))
except:
    sys.exit(0)
with open('mermaid/deps.mmd','w',encoding='utf-8') as f:
    f.write('graph TD;\n')
    def walk(d,parent='root'):
        for k,v in d.get('dependencies',{}).items():
            f.write(f'  {parent}-->{k};\n'); walk(v,k)
    walk(data)
