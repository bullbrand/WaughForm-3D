"""Turns Eagle part libraries (.lbr) into extra ready-made parts for WaughForm 3D's "Browse parts…".

It keeps the board-sized modules (controller boards, displays, sensors, relays, wireless modules…), not single
chips, and for each one takes the board outline (Eagle's Dimension layer, otherwise the drawn outline), the
mounting holes, the pins with their names (from the library's devices) and draws a picture of the board.
Writes desktop/eagle-parts.json in the same form as parts-library.json; the app lists both.

Usage:  python tools/eagle-to-parts.py <folder with .lbr files> [more folders...]
"""
import base64, glob, html, json, os, re, sys, xml.etree.ElementTree as ET
from datetime import date

OUT = os.path.join(os.path.dirname(__file__), '..', 'desktop', 'eagle-parts.json')
FRITZING = os.path.join(os.path.dirname(__file__), '..', 'desktop', 'parts-library.json')

# Who made each library and its licence, for the credit every part keeps (checked in the downloaded copies).
LIBS = [
    (r'sparkfun|lilypad', 'SparkFun Eagle Libraries', 'CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/)'),
    (r'^ai_', 'Ai EAGLE Libraries', 'Beerware licence'),
    (r'adafruit', 'Adafruit Eagle Library', 'licence not stated in the download: check before sharing'),
    (r'seeed|opl', 'Seeed Open Parts Library (OPL)', 'licence not stated in the download: check before sharing'),
]
# Which library wins when the same board is in several (the OPL comes in several near-identical versions).
PRIORITY = ['adafruit', 'sparkfun', 'ai_', 'seeed', 'opl']

# Single chips and other footprints that aren't modules.
CHIP = re.compile(r'^(?:(?:SO|SOIC|SSOP|TSSOP|MSOP|QFN|DFN|QFP|TQFP|LQFP|MQFP|BGA|DIL|DIP|PDIP|CDIP|SDIP|SOT|PLCC|LGA|WSON|VSON|SON|HVQFN|VQFN|UQFN|DPAK|D2PAK)[-_ ]?\d*\b|TO[-_ ]?\d)', re.I)
CHIP_DEVICE = re.compile(r'\b(PDIP|DIL\d|DIP IC SOCKET|TO[-_ ]?220|MOSFET|L78\d\d|7805)\b', re.I)

# The user's categories (from waughform_transmute.py), as kinds the parts browser already searches by.
KINDS = [  # first match wins, so the more particular kinds come first; words match whole words (or the start of one)
    ('Controller boards', ['arduino', 'raspberry', 'teensy', 'feather', 'trinket', 'esp32', 'esp8266', 'esp 01', 'esp 12', 'beaglebone', 'beagle bone', 'pro mini', 'pro micro', 'nano', 'shield', 'photon', 'thing', 'redboard', 'samd21', 'qduino', 'can485', 'micromod', 'mojo']),
    ('Switches and relays', ['switch', 'relay', 'solidstaterelay', 'pushbutton', 'tact', 'button', 'buttonpad', 'keyboard', 'cherry mx', 'momentary', 'thumbwheel', 'potentiometer', 'pot', 'encoder', 'joystick', 'keypad', 'slider', 'trackball']),
    ('Displays and LEDs', ['lcd', 'display', 'tft', 'oled', 'segment', 'bicol', 'matrix', 'ws2812', 'apa102', 'led', 'ili93', 'alphanumeric']),
    ('Sound', ['audio', 'sound', 'mic', 'microphone', 'electret', 'speaker', 'buzzer', 'piezo', 'mp3', 'xlr', 'midi', 'amp']),
    ('Sensors', ['sensor', 'bmp', 'bme', 'mics', 'adns', 'qre', 'tilt', 'ldr', 'pir', 'accel', 'gyro', 'imu', 'temp', 'temperature', 'humid', 'gas', 'ultrason', 'hall', 'lidar', 'thermocouple', 'conductivity', 'ms5803', 'isl29125', 'dht11', 'am2302']),
    ('Wireless and communication', ['antenna', 'xbee', 'sim800', 'sim900', 'wifi', 'rf', 'wireless', 'bluetooth', 'ble', 'gps', 'lora', 'nrf52832', 'rfm69', 'gsm', 'rj45', 'rj11', 'ethernet']),
    ('Power and batteries', ['power', 'battery', 'cr2032', 'cr1220', 'regulator', 'fuse', 'ldo', 'buck', 'boost', 'charger', 'lipo', 'atx24', 'urb']),
    ('Memory cards', ['microsd', 'sd card', 'sdcard']),
    ('Connectors', ['usb', 'jack', 'jst', 'molex', 'connector', 'conn', 'terminal', 'springterminal', 'latchterminal', 'header', 'fpc', 'idc', 'pogo', 'socket', 'db9', 'db15', 'din5', 'bnc', 'vernier', '1x03']),
]

def lib_info(fn):
    name = os.path.basename(fn)
    for pat, who, lic in LIBS:
        if re.search(pat, name, re.I) or re.search(pat, fn, re.I):
            return who, lic
    return 'Eagle library', 'licence not stated in the download: check before sharing'

def text(el):
    """Plain words from an Eagle description (often a small web page)."""
    if el is None or not (el.text or '').strip():
        return ''
    t = html.unescape(re.sub(r'<[^>]+>', ' ', html.unescape(el.text)))
    return re.sub(r'\s+', ' ', t).strip()

def nice(name):
    return re.sub(r'\s+', ' ', name.replace('_', ' ').replace('-', ' ')).strip()

def pin_names(root):
    """For each package: its pads' pin names, and the device's name and description (first device that uses it)."""
    out = {}
    for ds in root.iter('deviceset'):
        gates = {g.get('name'): g.get('symbol') for g in ds.iter('gate')}
        for dev in ds.iter('device'):
            pkg = dev.get('package')
            if not pkg or pkg in out:
                continue
            pads = {}
            for c in dev.iter('connect'):
                pin = (c.get('pin') or '').split('@')[0]
                for pad in (c.get('pad') or '').split():
                    pads[pad] = pin
            out[pkg] = {'pads': pads, 'device': ds.get('name') or '', 'desc': text(ds.find('description'))}
    return out

def board(pkg):
    """Outline (mm), pads and holes of one package, or None if it isn't a module."""
    def pts(layers):
        p = []
        for w in pkg.findall('wire'):
            if w.get('layer') in layers:
                p += [(float(w.get('x1')), float(w.get('y1'))), (float(w.get('x2')), float(w.get('y2')))]
        for r in pkg.findall('rectangle'):
            if r.get('layer') in layers:
                p += [(float(r.get('x1')), float(r.get('y1'))), (float(r.get('x2')), float(r.get('y2')))]
        for c in pkg.findall('circle'):
            if c.get('layer') in layers:
                x, y, rad = float(c.get('x')), float(c.get('y')), float(c.get('radius'))
                p += [(x - rad, y - rad), (x + rad, y + rad)]
        return p
    pads = [(p.get('name') or '', float(p.get('x')), float(p.get('y')), float(p.get('drill') or 0), float(p.get('diameter') or 0)) for p in pkg.findall('pad')]
    holes = [(float(h.get('x')), float(h.get('y')), float(h.get('drill') or 3)) for h in pkg.findall('hole')]
    if len(pads) < 3:
        return None
    outline = pts({'20'}) or pts({'51'}) or pts({'21'})
    if not outline:
        return None
    # pads count with their copper ring plus a little board around it, so edge pins don't sit on the edge
    rad = lambda drill, dia: (dia or max(1.6, drill * 1.6)) / 2 + 0.5
    xs = [p[0] for p in outline] + [x + s * rad(dr, di) for _, x, y, dr, di in pads for s in (-1, 1)] + [h[0] + s * (h[2] / 2 + 1) for h in holes for s in (-1, 1)]
    ys = [p[1] for p in outline] + [y + s * rad(dr, di) for _, x, y, dr, di in pads for s in (-1, 1)] + [h[1] + s * (h[2] / 2 + 1) for h in holes for s in (-1, 1)]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, d = x1 - x0, y1 - y0
    if min(w, d) < 10 or max(w, d) < 15 or w * d < 200:
        return None
    return {'x0': x0, 'y1': y1, 'w': w, 'd': d, 'pads': pads, 'holes': holes,
            'outline': [(w_.get('x1'), w_.get('y1'), w_.get('x2'), w_.get('y2')) for w_ in pkg.findall('wire') if w_.get('layer') in ('20', '51', '21')]}

def kind(title):
    t = ' ' + re.sub(r'[^a-z0-9]+', ' ', title.lower()) + ' '
    for k, words in KINDS:
        # short words must be whole words ("mic" is not "micro", "pot" is not "potting"); longer ones may start a word
        if any(re.search(r'\b' + re.escape(wd) + (r'\b' if len(wd) <= 4 else ''), t) for wd in words):
            return k
    return 'Modules'

def picture(b, pins, holes, title):
    """A drawn top view at 10 px per mm: board, outline, mounting holes and pins with their names."""
    W, D, x0, y1 = b['w'], b['d'], b['x0'], b['y1']
    X = lambda x: (float(x) - x0) * 10
    Y = lambda y: (y1 - float(y)) * 10
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*10:.0f}" height="{D*10:.0f}" viewBox="0 0 {W*10:.1f} {D*10:.1f}">',
         f'<rect width="{W*10:.1f}" height="{D*10:.1f}" rx="8" fill="#1f5c3d"/>']
    for a, b_, c, d in b['outline']:
        s.append(f'<line x1="{X(a):.1f}" y1="{Y(b_):.1f}" x2="{X(c):.1f}" y2="{Y(d):.1f}" stroke="#e8e8e8" stroke-width="2" opacity=".55"/>')
    s.append(f'<text x="{W*5:.1f}" y="{D*5:.1f}" font-family="Arial" font-size="{max(12, min(28, W*0.6)):.0f}" fill="#fff" opacity=".8" text-anchor="middle" dominant-baseline="middle">{html.escape(title[:40])}</text>')
    for h in holes:
        s.append(f'<circle cx="{h["x"]*10:.1f}" cy="{h["y"]*10:.1f}" r="{h["dia"]*5:.1f}" fill="#fff" stroke="#c9a227" stroke-width="3"/>')
    fs = 9 if len(pins) > 30 else 11
    for p in pins:
        s.append(f'<circle cx="{p["x"]*10:.1f}" cy="{p["y"]*10:.1f}" r="7" fill="#d4af37" stroke="#7a6010" stroke-width="1.5"/>')
        s.append(f'<text x="{p["x"]*10:.1f}" y="{p["y"]*10-10:.1f}" font-family="Arial" font-size="{fs}" fill="#fff" text-anchor="middle">{html.escape(p["name"][:8])}</text>')
    s.append('</svg>')
    return 'data:image/svg+xml;base64,' + base64.b64encode(''.join(s).encode()).decode()

def norm(t):
    return re.sub(r'[^a-z0-9]', '', t.lower())

def main(folders):
    files = sorted({f for d in folders for f in glob.glob(os.path.join(d, '**', '*.lbr'), recursive=True) if '__MACOSX' not in f},
                   key=lambda f: next((i for i, k in enumerate(PRIORITY) if k in os.path.basename(f).lower()), 99))
    known = set()
    try:
        known = {norm(p['title']) for p in json.load(open(FRITZING, encoding='utf-8'))['parts']}
    except Exception:
        pass
    parts, seen, skipped = [], {}, {'chip': 0, 'small': 0, 'duplicate': 0, 'in Fritzing library': 0}
    for fn in files:
        try:
            root = ET.parse(fn).getroot()
        except ET.ParseError:
            print('  can\'t read', fn)
            continue
        lib = os.path.splitext(os.path.basename(fn))[0]
        who, lic = lib_info(fn)
        names = pin_names(root)
        for pkg in root.iter('package'):
            pname = pkg.get('name') or ''
            if CHIP.match(pname):
                skipped['chip'] += 1
                continue
            b = board(pkg)
            if not b:
                skipped['small'] += 1
                continue
            dev = names.get(pname, {'pads': {}, 'device': '', 'desc': ''})
            if CHIP_DEVICE.search(nice(dev['device'] + ' ' + pname)):
                skipped['chip'] += 1
                continue
            title = nice(dev['device'] or pname)
            if dev['device'] and norm(dev['device']) != norm(pname):
                title += ' (' + nice(pname) + ')'
            # pins: named pads; big unconnected plain pads are mounting holes
            pins, holes = [], []
            for name, x, y, drill, dia in b['pads']:
                pin = dev['pads'].get(name)
                if not pin and drill >= 2.5:
                    holes.append({'x': round(x - b['x0'], 2), 'y': round(b['y1'] - y, 2), 'dia': round(drill, 2)})
                    continue
                pins.append({'name': pin or name or 'PIN', 'x': round(x - b['x0'], 2), 'y': round(b['y1'] - y, 2)})
            holes += [{'x': round(x - b['x0'], 2), 'y': round(b['y1'] - y, 2), 'dia': round(dr, 2)} for x, y, dr in b['holes']]
            if len(pins) < 3:
                skipped['small'] += 1
                continue
            if norm(dev['device'] or pname) in known:
                skipped['in Fritzing library'] += 1
                continue
            # the same board again (other library versions, or variants like _NOHOLE): keep the first, or the one with holes
            key = (round(b['w']), round(b['d']), tuple(sorted(p['name'] for p in pins)))
            if key in seen:
                old = parts[seen[key]]
                if holes and not old['features']:
                    old['features'] = [{'t': 'hole', **h} for h in holes]
                skipped['duplicate'] += 1
                continue
            k = kind(title)
            desc = (dev['desc'] or '').strip()
            credit = f'From {lib}.lbr ({who}), {lic}.'
            seen[key] = len(parts)
            parts.append({
                'title': title, 'folder': 'eagle', 'file': f'{lib}.lbr / {pname}',
                'info': {'title': title, 'description': ((desc + ' ') if desc else '') + f'Board {b["w"]:.1f} x {b["d"]:.1f} mm, {len(pins)} pins. ' + credit,
                         'family': k, 'props': {'family': k, 'library': lib, 'package': pname}, 'label': '', 'file': f'{lib}.lbr',
                         'tags': [lib, 'Eagle', k], 'credit': credit},
                'conns': [{'name': p['name'], 'desc': p['name'], 'svgId': f'p{i}'} for i, p in enumerate(pins)],
                'features': [{'t': 'hole', **h} for h in holes],
                'g': {'w': round(b['w'], 2), 'h': round(b['d'], 2), 'pos': {f'p{i}': [p['x'], p['y']] for i, p in enumerate(pins)},
                      'photo': picture(b, pins, holes, title)},
            })
    json.dump({'name': 'WaughForm 3D Eagle parts', 'made': date.today().isoformat(),
               'source': 'Eagle libraries: ' + ', '.join(sorted({lib_info(f)[0] for f in files})),
               'credit': 'Each part keeps the credit and licence of the Eagle library it came from (see its description).',
               'parts': parts}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'{len(parts)} parts written to {os.path.normpath(OUT)}')
    print('skipped:', ', '.join(f'{v} {k}' for k, v in skipped.items()))
    counts = {}
    for p in parts:
        counts[p['info']['family']] = counts.get(p['info']['family'], 0) + 1
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f'  {v:4} {k}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
