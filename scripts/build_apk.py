"""Build Min Extended using Android SDK tools; no Gradle or network dependencies.

Run scripts/bootstrap_android.py once, or provide ANDROID_SDK_ROOT with platform
36 and build-tools 36.0.0. Java 17+ is required. Signing material stays in .local.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PACKAGE='io.github.clementou.miniconpack'

def resources(stage):
    drawable=stage/'res/drawable-nodpi'
    drawable.mkdir(parents=True)
    assets=stage/'assets'; assets.mkdir()
    xml=stage/'res/xml'; xml.mkdir()
    for source in sorted((ROOT/'original/icons').glob('*.png')):
        shutil.copyfile(source,drawable/source.name)
    # Calendar days and fallback masks were density-qualified in the old APK.
    with zipfile.ZipFile(ROOT/'original/Min-4.0.6.1.apk') as apk:
        support=stage/'res/drawable-xxhdpi'; support.mkdir()
        for name in apk.namelist():
            if re.fullmatch(r'res/drawable-xxhdpi-v4/(ic_calendar_\d+|iconback|iconmask|iconupon)\.png',name):
                (support/Path(name).name).write_bytes(apk.read(name))
    names={p.stem for p in (stage/'res').glob('*/*.png')}
    apps=json.loads((ROOT/'icons/apps.json').read_text())
    replacements={a['package']:'min_'+a['id'].replace('-','_') for a in apps}
    catalog=[]
    for app in apps:
        name=replacements[app['package']]
        shutil.copyfile(ROOT/'icons/png'/(app['id']+'.png'),drawable/(name+'.png'))
        names.add(name); catalog.append((name,app['name']))
    # Native pack glyph, deliberately distinct from an app icon.
    vector=stage/'res/drawable'; vector.mkdir()
    (vector/'min_pack.xml').write_text('''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="48dp" android:height="48dp" android:viewportWidth="48" android:viewportHeight="48"><path android:fillColor="#282B30" android:pathData="M0,0h48v48h-48z"/><path android:fillColor="#FFFFFF" android:pathData="M10,34V14h6l8,12 8,-12h6v20h-6V24l-8,11 -8,-11v10z"/></vector>''')
    original=ET.parse(ROOT/'original/assets/appfilter.xml').getroot()
    merged=ET.Element('resources')
    mappings={}; dropped=[]
    for item in original:
        if item.tag=='item':
            component=item.get('component','')
            target=item.get('drawable','')
            if target not in names:
                dropped.append(dict(component=component,drawable=target)); continue
            if component.startswith('ComponentInfo{'):
                parts=component[14:-1].split('/',1)
                if len(parts)==2:
                    package,activity=parts
                    if activity.startswith('.'): activity=package+activity
                    component='ComponentInfo{'+package+'/'+activity+'}'
                    target=replacements.get(package,target)
            mappings[component]=target
        elif item.tag=='calendar':
            if all(item.get('prefix','')+str(day) in names for day in range(1,32)):
                merged.append(item)
        elif item.tag in {'iconback','iconmask','iconupon'}:
            kept={k:v for k,v in item.attrib.items() if v in names}
            if kept: ET.SubElement(merged,item.tag,kept)
        elif item.tag=='scale':
            merged.append(item)
    fixes=json.loads((ROOT/'android/mappings.json').read_text())
    for fix in fixes:
        assert fix['drawable'] in names, fix
        mappings['ComponentInfo{'+fix['component']+'}']=fix['drawable']
    for component,target in sorted(mappings.items()):
        ET.SubElement(merged,'item',component=component,drawable=target)
    ET.indent(merged)
    data=ET.tostring(merged,encoding='utf-8',xml_declaration=True)
    (assets/'appfilter.xml').write_bytes(data); (xml/'appfilter.xml').write_bytes(data)
    picker=ET.Element('resources'); ET.SubElement(picker,'version').text='1'
    ET.SubElement(picker,'category',title='New additions')
    for name,label in catalog: ET.SubElement(picker,'item',drawable=name)
    ET.SubElement(picker,'category',title='Original Min')
    listed=set()
    for item in ET.parse(ROOT/'original/assets/drawable.xml').getroot().iter('item'):
        name=item.get('drawable')
        if name in names and name not in listed:
            ET.SubElement(picker,'item',drawable=name)
            listed.add(name); catalog.append((name,name.replace('_',' ')))
    ET.indent(picker)
    data=ET.tostring(picker,encoding='utf-8',xml_declaration=True)
    (assets/'drawable.xml').write_bytes(data); (xml/'drawable.xml').write_bytes(data)
    (assets/'catalog.tsv').write_text(''.join(name+'\t'+label+'\n' for name,label in catalog))
    # Legacy calendars and fallback shapes are support assets, not picker entries.
    assert len({x[0] for x in catalog})==len(catalog)
    assert all(target in names for target in mappings.values())
    assert set(replacements.values()) <= set(mappings.values())
    report=dict(package=PACKAGE,target_sdk=36,min_sdk=26,drawables=len(names),
                picker_icons=len(catalog),mappings=len(mappings),reviewed_updates=len(fixes),
                removed_broken_legacy_references=dropped)
    return report

def build():
    sdk=Path(os.environ.get('ANDROID_SDK_ROOT',ROOT/'.local/sdk'))
    tools=sdk/'build-tools/36.0.0'
    if not tools.exists(): tools=sdk/'build-tools/android-16'
    platform=sdk/'platforms/android-36/android.jar'
    if not tools.exists() or not platform.exists():
        raise SystemExit('Run python3 scripts/bootstrap_android.py or set ANDROID_SDK_ROOT.')
    java=Path(os.environ.get('JAVA_HOME','/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home'))
    env=os.environ.copy()
    if java.exists(): env['JAVA_HOME']=str(java); env['PATH']=str(java/'bin')+os.pathsep+env['PATH']
    def run(*args):
        subprocess.run([str(a) for a in args],check=True,env=env)
    build_dir=ROOT/'.build'; build_dir.mkdir(exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='apk-',dir=build_dir))
    report=resources(stage)
    compiled=stage/'resources.zip'; linked=stage/'linked.apk'
    run(tools/'aapt2','compile','--dir',stage/'res','-o',compiled)
    run(tools/'aapt2','link','-o',linked,'-I',platform,'--manifest',ROOT/'android/AndroidManifest.xml',
        '-A',stage/'assets',compiled)
    classes=stage/'classes'; classes.mkdir()
    run('javac','--release','8','-classpath',platform,'-d',classes,ROOT/'android/MainActivity.java')
    dex=stage/'dex'; dex.mkdir()
    run(tools/'d8','--lib',platform,'--min-api','26','--output',dex,*sorted(classes.rglob('*.class')))
    with zipfile.ZipFile(linked,'a',zipfile.ZIP_DEFLATED) as apk:
        apk.write(dex/'classes.dex','classes.dex')
    aligned=stage/'aligned.apk'
    run(tools/'zipalign','-f','-p','4',linked,aligned)
    signing=ROOT/'.local/signing'; signing.mkdir(parents=True,exist_ok=True)
    key=signing/'min-release.jks'; password=signing/'password.txt'
    if not key.exists():
        if not password.exists():
            password.write_text(secrets.token_urlsafe(32)+'\n'); password.chmod(0o600)
        run('keytool','-genkeypair','-keystore',key,'-storetype','JKS','-alias','min',
            '-storepass:file',password,'-keypass:file',password,'-keyalg','RSA','-keysize','3072',
            '-sigalg','SHA256withRSA','-validity','10000','-dname','CN=Min Extended')
        key.chmod(0o600)
    dist=ROOT/'dist'; dist.mkdir(exist_ok=True)
    out=dist/'min-extended-1.0.0.apk'
    # apksigner reads a password file sequentially, so one file cannot serve both prompts.
    env['MIN_KEYSTORE_PASSWORD']=password.read_text().strip()
    run(tools/'apksigner','sign','--ks',key,'--ks-key-alias','min','--ks-pass','env:MIN_KEYSTORE_PASSWORD',
        '--key-pass','env:MIN_KEYSTORE_PASSWORD','--out',out,aligned)
    run(tools/'apksigner','verify','--verbose',out)
    run(tools/'zipalign','-c','-p','4',out)
    report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest()
    (dist/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    shutil.copyfile(stage/'assets/appfilter.xml',dist/'appfilter.xml')
    (dist/(out.name+'.sha256')).write_text(report['sha256']+'  '+out.name+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='removed_broken_legacy_references'},indent=2))
    print('APK: '+str(out))

if __name__=='__main__': build()
