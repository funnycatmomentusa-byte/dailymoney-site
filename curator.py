import json, glob
from datetime import datetime
today = datetime.now()
for f in sorted(glob.glob('_articles/*.json')):
    with open(f) as j:
        data = json.load(j)
    try:
        d = datetime.strptime(data.get('date',''), '%d/%m/%Y')
        if (today - d).days > 3:
            data['_archived'] = True
        else:
            data.pop('_archived', None)
    except: pass
    with open(f, 'w') as j:
        json.dump(data, j, indent=2, ensure_ascii=False)
for f in sorted(glob.glob('_articles/en/*.json')):
    with open(f) as j:
        data = json.load(j)
    try:
        d = datetime.strptime(data.get('date',''), '%d/%m/%Y')
        if (today - d).days > 3:
            data['_archived'] = True
        else:
            data.pop('_archived', None)
    except: pass
    with open(f, 'w') as j:
        json.dump(data, j, indent=2, ensure_ascii=False)
