"""Read launcher activities, propose mapping repairs, and keep inventory local."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

def normalize(component):
    package,activity = component.removeprefix('ComponentInfo{').removesuffix('}').split('/',1)
    return package+'/'+(package+activity if activity.startswith('.') else activity)

def installed():
    output = subprocess.check_output(['adb','shell','cmd','package','query-activities','--brief',
        '-a','android.intent.action.MAIN','-c','android.intent.category.LAUNCHER'],text=True)
    return sorted({normalize(line.strip()) for line in output.splitlines()
                   if re.fullmatch(r'\s*[\w.]+/[\w.$]+\s*',line)})

def audit():
    current=installed()
    apps=json.loads((ROOT/'icons/apps.json').read_text())
    new={a['package']:'min_'+a['id'].replace('-','_') for a in apps}
    old={}
    by_package=defaultdict(Counter)
    for element in ET.parse(ROOT/'original/assets/appfilter.xml').getroot().iter('item'):
        raw=element.get('component','')
        if not raw.startswith('ComponentInfo{') or '/' not in raw:
            continue
        component=normalize(raw)
        drawable=element.get('drawable')
        if not (ROOT/'original/icons'/(drawable+'.png')).exists():
            continue
        old[component]=drawable
        by_package[component.split('/')[0]][drawable]+=1
    repairs=[]
    unresolved=[]
    for component in current:
        package=component.split('/')[0]
        if package in new:
            repairs.append(dict(component=component,drawable=new[package],source='device launcher query'))
        elif component not in old and package in by_package:
            candidates=by_package[package]
            if len(candidates)==1:
                repairs.append(dict(component=component,drawable=next(iter(candidates)),source='device launcher query; existing package mapping'))
            else:
                unresolved.append(dict(component=component,candidates=dict(candidates)))
        elif component not in old:
            unresolved.append(dict(component=component,candidates={}))
    local=ROOT/'.local'
    local.mkdir(exist_ok=True)
    (local/'mapping-audit.json').write_text(json.dumps(dict(installed=current,repairs=repairs,unresolved=unresolved),indent=2)+'\n')
    print(json.dumps(dict(installed_count=len(current),repairs=repairs,unresolved=unresolved),indent=2))

if __name__=='__main__':
    audit()
