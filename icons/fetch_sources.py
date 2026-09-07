# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow==12.3.0", "requests==2.34.2"]
# ///
"""Download publisher-provided Play Store artwork and record its provenance."""
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
import json
import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / 'sources'
SOURCES.mkdir(exist_ok=True)

class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta':
            self.meta[attrs.get('property', '')] = attrs.get('content', '')

def fetch(app):
    try:
        url = 'https://play.google.com/store/apps/details?id=' + app['package'] + '&hl=en_US&gl=US'
        target = SOURCES / (app['id'] + '.png')
        record = SOURCES / (app['id'] + '.json')
        if target.exists() and record.exists():
            return json.loads(record.read_text())
        response = requests.get(url, timeout=40)
        response.raise_for_status()
        parser = MetaParser()
        parser.feed(response.text)
        image_url = parser.meta['og:image']
        response = requests.get(image_url, timeout=40)
        response.raise_for_status()
        target.write_bytes(response.content)
        with Image.open(target) as im:
            im.convert('RGBA').save(target)
        result = dict(app, listing=url, title=parser.meta.get('og:title'), image_url=image_url)
        record.write_text(json.dumps(result, indent=2) + '\n')
        print(app['id'] + ': ' + result['title'], flush=True)
        return result
    except Exception as error:
        print(app['id'] + ': ERROR ' + str(error), flush=True)
        return dict(app, error=str(error))

if __name__ == '__main__':
    apps = json.loads((ROOT / 'apps.json').read_text())
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(fetch, apps))
    (SOURCES / 'manifest.json').write_text(json.dumps(results, indent=2) + '\n')
    sheet = Image.new('RGB', (1200, 1200), '#e5e7eb')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 15)
    for i, app in enumerate(apps):
        x, y = (i % 6)*200, (i // 6)*200
        path = SOURCES / (app['id'] + '.png')
        if path.exists():
            im = Image.open(path).convert('RGBA')
            im.thumbnail((140, 140))
            sheet.paste(im, (x+30, y+12), im)
        draw.text((x+8, y+163), app['id'], fill='#111827', font=font)
    sheet.save(SOURCES / 'contact-sheet.jpg')
