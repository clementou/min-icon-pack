"""Promote reviewed mapping fixes, without publishing a device inventory."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
audit=json.loads((ROOT/'.local/mapping-audit.json').read_text())
repairs=audit['repairs']
existing={r['component'] for r in repairs}
# Reviewed package migrations and renamed products retaining their Min artwork.
reviewed={
 'com.google.android.apps.walletnfcrel':'googlewallet',
 'com.google.android.videos':'playmovies',
 'com.sonos.acr2':'sonos',
 'com.blizzard.messenger':'battlenet',
 'app.revanced.android.youtube':'youtube',
 'app.revanced.android.apps.youtube.music':'youtubemusic',
}
for component in audit['installed']:
    package=component.split('/')[0]
    if package in reviewed and component not in existing:
        repairs.append(dict(component=component,drawable=reviewed[package],source='device launcher query; reviewed product migration'))
# The three requested apps absent from the device: corroborated public mappings.
public={'com.okta.android.auth':'min_okta_verify','com.pagerduty.android':'min_pagerduty','us.zoom.videomeetings':'min_zoom'}
source='https://github.com/Delta-Icons/android/blob/master/app/src/main/assets/appfilter.xml'
for item in ET.parse(ROOT/'.local/downloads/delta-appfilter.xml').getroot().iter('item'):
    component=item.get('component','').removeprefix('ComponentInfo{').removesuffix('}')
    package=component.split('/')[0]
    if package in public:
        repairs.append(dict(component=component,drawable=public[package],source=source))
repairs=sorted({r['component']:r for r in repairs}.values(),key=lambda r:r['component'])
(ROOT/'android/mappings.json').write_text(json.dumps(repairs,indent=2)+'\n')
print(f'Wrote {len(repairs)} reviewed mappings; full inventory remains local.')
