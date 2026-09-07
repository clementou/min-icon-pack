# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["pillow==12.3.0", "vtracer==0.6.15", "cairosvg==2.9.0"]
# ///
"""Trace publisher artwork, style editable vectors, and render Min-size PNGs.

Run with uv run icons/build.py (uv selects Python 3.12 automatically).
Source-specific masks are intentional: automatic background removal alone loses
internal logo detail. No generative images are used by this build.
"""
from pathlib import Path
from html import escape
import io
import json
import shutil
import xml.etree.ElementTree as ET
import zipfile
import cairosvg
import vtracer
from PIL import Image, ImageDraw, ImageFont, ImageChops

ROOT = Path(__file__).resolve().parent
APPS = json.loads((ROOT / 'apps.json').read_text())
for folder in ['svg', 'png', 'traces', 'masks']:
    (ROOT / folder).mkdir(exist_ok=True)

WHITE_ON_COLOR = {'chipotle', 'fidelity', 'grubhub', 'sutter-health', 'oura',
                  'pagerduty', 'parkmobile', 'roborock', 'schwab', 'tesla',
                  'wealthfront', 'zoom', 'united-airlines'}
DARK_ON_LIGHT = {'chatgpt', 'beli', 'cbp-mpc', 'okta-verify', 'uber-eats'}
WIDTHS = {'stanford-health':84, 'chipotle':78, 'microsoft-authenticator':80,
          'dunkin':88, 'renpho-health':90, 'beli':84, 'uber-eats':80,
          'zoom':86, 'cbp-mpc':86, 'google-fi':78, 'mini-metro':80}

def make_mask(app, image, layer='main'):
    key = app['id']
    mask = Image.new('L', image.size)
    pixels = []
    for y in range(image.height):
        for x in range(image.width):
            r,g,b,a = image.getpixel((x,y))
            high, low = max(r,g,b), min(r,g,b)
            if layer == 'person':
                keep = b > 160 and g > 145 and r < 110
            elif layer == 'safety-blue':
                keep = b > r*1.3 and high-low > 65
            elif key in WHITE_ON_COLOR:
                keep = low > 180 and high-low < 65
            elif key in DARK_ON_LIGHT:
                keep = high < 155 if key in {'chatgpt','uber-eats'} else low < 110 and high < 210
            elif key == 'tiktok':
                keep = low > 190  # white core; omit the cyan/red offset duplicates
            elif key == 'stanford-health':
                keep = r > 90 and r > g*1.5 and r > b*1.15
            else:
                keep = high-low > 65 and low < 180
            if key in {'beli','chatgpt'} and (x<55 or x>457 or y<55 or y>457):
                keep = False  # baked-in black corner pixels in this publisher image
            if key == 'sutter-health' and x < 180 and y > 410:
                keep = False  # omit the tiny trademark notice
            if key == 'dunkin' and x > 475:
                keep = False  # omit tiny registration symbol
            pixels.append(255 if keep and a > 128 else 0)
    mask.putdata(pixels)
    return mask

def trace(key, mask):
    path = ROOT / 'masks' / (key + '.png')
    ImageChops.invert(mask).convert('RGB').save(path)
    out = ROOT / 'traces' / (key + '.svg')
    vtracer.convert_image_to_svg_py(str(path), str(out), colormode='binary',
        mode='spline', filter_speckle=8, corner_threshold=70,
        length_threshold=3.5, splice_threshold=45, path_precision=3)
    svg = ET.parse(out).getroot()
    paths = []
    for element in svg:
        if element.tag.endswith('path'):
            element.attrib.pop('fill', None)
            paths.append(ET.tostring(element, encoding='unicode'))
    return ''.join(paths)

def style_svg(app, paths, bounds, overlay=''):
    x0,y0,x1,y1 = bounds
    width,height = x1-x0,y1-y0
    size = WIDTHS.get(app['id'],80)
    scale = size/max(width,height)
    tx,ty = 96-(x0+x1)*scale/2,95-(y0+y1)*scale/2
    edge = {'united-airlines':0.7,'stanford-health':0.7,'chipotle':1.0,'tiktok':0.6}.get(app['id'],1.7)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192">
<title>{escape(app['name'])} — Min adaptation</title>
<desc>Traced from publisher Play Store artwork. White face, pale gray lower edge, transparent canvas.</desc>
<defs><linearGradient id="face" x1="0" y1="0" x2="0" y2="1" gradientUnits="objectBoundingBox"><stop stop-color="#fff"/><stop offset="1" stop-color="#f6f6f6"/></linearGradient>
<g id="mark" transform="translate({tx:.5f} {ty:.5f}) scale({scale:.7f})">{paths}</g></defs>
<use href="#mark" xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#mark" transform="translate(0 {edge})" fill="#dcdcdc"/>
<use href="#mark" xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#mark" fill="url(#face)"/>
<g fill="#dfdfdf" transform="translate({tx:.5f} {ty:.5f}) scale({scale:.7f})">{overlay}</g>
</svg>'''

def mini_metro():
    # A miniature playable map: hollow circle, square and triangle stations.
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192">
<title>Mini Metro — Min adaptation</title>
<defs><g id="map" fill="none" stroke-linecap="round" stroke-linejoin="round">
<path d="M75 116H83L105 94H113V78" stroke-width="5"/>
<circle cx="65" cy="116" r="9" stroke-width="5"/>
<rect x="105" y="62" width="16" height="16" rx="1" stroke-width="5"/>
<path d="M113 94H130V108" stroke-width="5"/>
<path d="M130 108L141 127H119Z" stroke-width="5"/>
</g></defs>
<use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#map" stroke="#ddd" transform="translate(-3 1.2)"/>
<use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#map" stroke="#fbfbfb" transform="translate(-3 0)"/>
</svg>'''

def uber_eats():
    mask=Image.new('L',(512,512))
    draw=ImageDraw.Draw(mask)
    font=ImageFont.truetype(str(ROOT/'sources/Inter.ttf'),145)
    font.set_variation_by_axes([24,600])
    for text,y in [('Uber',95),('Eats',265)]:
        box=draw.textbbox((0,0),text,font=font)
        draw.text(((512-(box[2]-box[0]))/2-box[0],y-box[1]),text,font=font,fill=255)
    app=next(a for a in APPS if a['id']=='uber-eats')
    return style_svg(app,trace('uber-eats',mask),mask.getbbox())

def build():
    report = []
    for app in APPS:
        key = app['id']
        original = app.get('original')
        if original:
            path = ROOT.parent / 'original/icons' / (original+'.png')
            shutil.copyfile(path, ROOT / 'png' / (key+'.png'))
            # Keep the exact original PNG as final; a traced vector is provided for edits.
            image = Image.open(path).convert('RGBA')
            mask = image.getchannel('A').point(lambda a: 255 if a>128 else 0)
            svg = style_svg(app, trace(key,mask), mask.getbbox())
            method = 'Original Min PNG; traced silhouette SVG supplied separately'
        elif key == 'mini-metro':
            svg = mini_metro()
            method = 'Original vector design inspired by Mini Metro station shapes'
        elif key == 'uber-eats':
            svg = uber_eats()
            method = 'Two lines typeset at equal Inter SemiBold weight; outlined as SVG'
        elif key == 'tiktok':
            source=ET.parse(ROOT/'sources/tiktok-vector.svg').getroot()
            paths=''.join(ET.tostring(p,encoding='unicode') for p in source if p.tag.endswith('path'))
            svg=style_svg(app,paths,(1.57,0,22.43,24))
            method='Clean TikTok vector from Simple Icons; reduced gray edge'
        else:
            image = Image.open(ROOT/'sources'/(key+'.png')).convert('RGBA')
            mask = make_mask(app,image)
            bounds = mask.getbbox()
            if not bounds:
                raise ValueError('Empty mask: '+key)
            overlay = trace(key+'-person',make_mask(app,image,'person')) if key=='microsoft-authenticator' else ''
            if key=='safety':
                overlay=trace(key+'-blue',make_mask(app,image,'safety-blue'))
            svg = style_svg(app,trace(key,mask),bounds,overlay)
            method = 'Traced publisher Play Store artwork'
        (ROOT/'svg'/(key+'.svg')).write_text(svg)
        if not original:
            rendered = cairosvg.svg2png(bytestring=svg.encode(), output_width=768,output_height=768)
            image = Image.open(io.BytesIO(rendered)).convert('RGBA')
            image.resize((192,192),Image.Resampling.LANCZOS).save(ROOT/'png'/(key+'.png'))
        result = Image.open(ROOT/'png'/(key+'.png')).convert('RGBA')
        alpha = result.getchannel('A')
        bounds = alpha.point(lambda a: 255 if a>16 else 0).getbbox()
        assert result.size==(192,192) and alpha.getextrema()==(0,255), key
        assert bounds and all(v>=40 for v in bounds[:2]) and all(v<=152 for v in bounds[2:]),(key,bounds)
        report.append(dict(id=key,method=method,visible_bounds=bounds))
    (ROOT/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    gallery(report)
    with zipfile.ZipFile(ROOT/'min-additions.zip','w',zipfile.ZIP_DEFLATED) as archive:
        archive.write(ROOT/'README.md','min-additions/README.md')
        for app in APPS:
            archive.write(ROOT/'png'/(app['id']+'.png'),'min-additions/'+app['id']+'.png')
    print(f'Built {len(report)} PNGs and SVGs; gallery.html; min-additions.zip')

def gallery(report):
    font = ImageFont.truetype(str(ROOT/'sources/Inter.ttf'),14)
    sheet = Image.new('RGB',(1200,1200),'#282b30')
    draw = ImageDraw.Draw(sheet)
    cards = []
    for i,(app,item) in enumerate(zip(APPS,report)):
        key,name = app['id'],app['name']
        im = Image.open(ROOT/'png'/(key+'.png')).convert('RGBA')
        x,y=(i%6)*200,(i//6)*200
        sheet.paste(im,(x+4,y-12),im)
        draw.text((x+8,y+165),key,fill='#ddd',font=font)
        listing='https://play.google.com/store/apps/details?id='+app['package']
        cards.append(f'''<article data-search="{escape(name.lower())}"><h2>{escape(name)}</h2><div class="pair"><figure><img class="source" src="sources/{key}.png" alt="Official {escape(name)} icon"><figcaption>Play Store</figcaption></figure><figure><a href="png/{key}.png" download><img class="min" src="png/{key}.png" alt="Min-style {escape(name)} icon"></a><figcaption>Min adaptation</figcaption></figure></div><footer><a href="png/{key}.png" download>PNG</a><a href="svg/{key}.svg" download>SVG</a><a href="{listing}">Source</a></footer></article>''')
    sheet.save(ROOT/'preview.jpg',quality=95)
    refs=''.join(f'<figure><img class="min" src="../original/icons/{n}.png" alt="Original Min {n}"><figcaption>{n}</figcaption></figure>' for n in ['spotify','twitter','telegram','instagram','googlephotos','onepassword'])
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Min additions — 32 apps</title>
<style>:root{font-family:system-ui;color:#eee;background:#191b20;color-scheme:dark;--tile:#292d33;--size:144px}body{margin:28px auto;padding:0 22px;max-width:1300px}h1{font-size:28px;margin-bottom:8px}p{color:#b8bec8;line-height:1.5}a{color:#abcaff}header{margin-bottom:24px}.controls{display:flex;gap:20px;flex-wrap:wrap;align-items:center}input[type=search]{padding:10px;background:#2c3037;border:1px solid #68707e;border-radius:6px;color:white;font:inherit}#grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}article{background:var(--tile);border-radius:12px;padding:16px}h2{font-size:15px;margin:0 0 12px}figure{margin:0;display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:0}figcaption{font-size:11px;color:#b8bec8;margin:6px 0}.pair{display:grid;grid-template-columns:1fr 1fr;align-items:center;min-height:150px}.source{width:76px;height:76px;border-radius:12px}.min{width:var(--size);height:var(--size);object-fit:contain}footer{display:flex;gap:20px;margin-top:12px;font-size:12px}#refs{display:flex;flex-wrap:wrap;background:var(--tile);border-radius:12px;margin:16px 0 28px;padding:8px}#refs figure{flex:1}#refs .min{max-width:100%}[hidden]{display:none!important}</style>
<header><h1>Min / additions</h1><p>32 apps. Publisher artwork → editable SVG → transparent 192 × 192 PNG. The 1Password PNG is the unchanged Min original. Mini Metro’s routes are shortened to fit. Click PNG to save an icon.</p><p><a href="min-additions.zip" download>Download all 32 PNGs</a> · <a href="README.md">Nova instructions</a></p><div class="controls"><input id="search" type="search" placeholder="Find an app…" aria-label="Find an app"><label>Preview background <input id="background" type="color" value="#292d33"></label><label>Preview size <input id="size" type="range" min="64" max="192" value="144"></label></div></header><p>Original Min icons, shown at the same canvas size:</p><section id="refs">REFS</section><main id="grid">CARDS</main>
<script>document.querySelector('#search').oninput=e=>{for(const card of document.querySelectorAll('article'))card.hidden=!card.dataset.search.includes(e.target.value.toLowerCase())};document.querySelector('#background').oninput=e=>document.documentElement.style.setProperty('--tile',e.target.value);document.querySelector('#size').oninput=e=>document.documentElement.style.setProperty('--size',e.target.value+'px');</script></html>'''.replace('REFS',refs).replace('CARDS','\n'.join(cards))
    page=page.replace('32 apps',str(len(APPS))+' apps').replace('all 32 PNGs','all '+str(len(APPS))+' PNGs')
    (ROOT/'gallery.html').write_text(page)

if __name__=='__main__':
    build()
