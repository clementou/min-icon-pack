"""Verify that APK resource compilation preserved the checked-in artwork."""
import io
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def pixels(data):
    with Image.open(io.BytesIO(data)) as image:
        return image.size, image.convert('RGBA').tobytes()

def verify(path):
    with zipfile.ZipFile(path) as apk, zipfile.ZipFile(ROOT/'original/Min-4.0.6.1.apk') as original:
        launchers = [p for p in original.namelist() if p.startswith('res/mipmap-') and p.endswith('/ic_launcher.png')]
        assert len(launchers) == 5
        for source in launchers:
            target = source.replace('ic_launcher.png', 'min_pack.png')
            assert pixels(original.read(source)) == pixels(apk.read(target)), target
        apps = json.loads((ROOT/'icons/apps.json').read_text())
        for app in apps:
            name = 'min_'+app['id'].replace('-', '_')+'.png'
            matches = [p for p in apk.namelist() if p.startswith('res/drawable-nodpi') and p.endswith('/'+name)]
            assert len(matches) == 1, name
            assert pixels(apk.read(matches[0])) == pixels((ROOT/'icons/png'/(app['id']+'.png')).read_bytes()), name
        mappings = {i.get('component'): i.get('drawable') for i in ET.fromstring(apk.read('assets/appfilter.xml')).iter('item')}
        for mapping in json.loads((ROOT/'android/mappings.json').read_text()):
            assert mappings['ComponentInfo{'+mapping['component']+'}'] == mapping['drawable'], mapping
    print(f'Verified {len(apps)} bundled icons, all reviewed mappings, and original launcher artwork at five densities.')

if __name__ == '__main__':
    verify(sys.argv[1])
