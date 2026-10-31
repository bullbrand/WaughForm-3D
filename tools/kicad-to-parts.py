"""Turns KiCad footprint libraries (.pretty folders of .kicad_mod files) into extra ready-made parts for
WaughForm 3D's "Browse parts…".

Like tools/eagle-to-parts.py, it keeps the board-sized footprints (controller boards, breakout boards,
sensors, displays…), not single-chip packages, and for each one takes the outline from the Edge.Cuts
layer, the mounting holes (unplated through-holes), the pads and draws a picture of the board. Writes
desktop/kicad-parts.json in the same form as parts-library.json and eagle-parts.json; the app lists all three.

IMPORTANT LIMITATION: unlike Eagle's .lbr files, a KiCad footprint file only knows pad NUMBERS (e.g. "1",
"14"), not signal NAMES (e.g. "VCC", "SCL") - that link lives in the schematic symbol and a project's
netlist, which aren't part of a plain footprint library. Where a library's own footprint already gives a
pad a descriptive name (common for breakout-board footprints, some SparkFun/Adafruit libraries do this),
that name is kept; otherwise the pad keeps its bare number as the pin name, and you'll need to work out
and rename the real pin roles yourself (same "check every pin" caution the app already gives for Eagle
and Fritzing imports).

Usage:  python tools/kicad-to-parts.py [--shareable] <folder with .pretty libraries or .kicad_mod files> [more folders...]
  --shareable  only libraries whose licence lets the converted parts be shared, so the file can go on
               GitHub and in the released app (edit LIBS below to mark the libraries you use)
"""
import base64, glob, json, os, re, sys, html
from datetime import date

OUT = os.path.join(os.path.dirname(__file__), '..', 'desktop', 'kicad-parts.json')
FRITZING = os.path.join(os.path.dirname(__file__), '..', 'desktop', 'parts-library.json')

# Who made each library, its licence (for the credit every part keeps) and whether that licence lets the
# converted parts be shared. Matched against the .pretty folder's (or file's) path; add your own libraries here.
LIBS = [
    (r'sparkfun', 'SparkFun KiCad Libraries', 'CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/)', True),
    (r'adafruit', 'Adafruit KiCad Libraries (github.com/adafruit/kicad-libraries)', 'CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/)', True),
    (r'kicad[-_]?footprints|official', 'KiCad official footprint libraries', 'CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/)', True),
]
PRIORITY = ['sparkfun', 'adafruit', 'kicad']

# Single-chip packages and generic connector/passive footprints that aren't modules.
CHIP = re.compile(r'^(?:SO|SOIC|SSOP|TSSOP|MSOP|QFN|DFN|QFP|TQFP|LQFP|MQFP|BGA|DIP|PDIP|CDIP|SDIP|SOT|SOD|PLCC|LGA|WSON|VSON|SON|HVQFN|VQFN|UQFN|DPAK|D2PAK|TO[-_]?\d|Crystal|Resistor|Capacitor|R_|C_|L_|D_|LED_|Diode)', re.I)
GENERIC = re.compile(r'^(PinHeader|PinSocket|Pin_Header|Pin_Socket|TestPoint|Fiducial|MountingHole|Jumper)', re.I)

# Same categories as eagle-to-parts.py, for consistency with the parts browser's search-by-kind.
KINDS = [
    ('Controller boards', ['arduino', 'raspberry', 'teensy', 'feather', 'trinket', 'esp32', 'esp8266', 'esp 01', 'esp 12', 'beaglebone', 'beagle bone', 'pro mini', 'pro micro', 'nano', 'shield', 'photon', 'thing', 'redboard', 'samd21', 'qduino', 'can485', 'micromod', 'mojo', 'xiao', 'pico']),
    ('Switches and relays', ['switch', 'relay', 'solidstaterelay', 'pushbutton', 'tact', 'button', 'buttonpad', 'keyboard', 'cherry mx', 'momentary', 'thumbwheel', 'potentiometer', 'pot', 'encoder', 'joystick', 'keypad', 'slider', 'trackball']),
    ('Displays and LEDs', ['lcd', 'display', 'tft', 'oled', 'segment', 'bicol', 'matrix', 'ws2812', 'apa102', 'led', 'ili93', 'alphanumeric']),
    ('Sound', ['audio', 'sound', 'mic', 'microphone', 'electret', 'speaker', 'buzzer', 'piezo', 'mp3', 'xlr', 'midi', 'amp']),
    ('Sensors', ['sensor', 'bmp', 'bme', 'mics', 'adns', 'qre', 'tilt', 'ldr', 'pir', 'accel', 'gyro', 'imu', 'temp', 'temperature', 'humid', 'gas', 'ultrason', 'hall', 'lidar', 'thermocouple', 'conductivity', 'ms5803', 'isl29125', 'dht11', 'am2302']),
    ('Wireless and communication', ['antenna', 'xbee', 'sim800', 'sim900', 'wifi', 'rf', 'wireless', 'bluetooth', 'ble', 'gps', 'lora', 'nrf52832', 'rfm69', 'gsm', 'rj45', 'rj11', 'ethernet']),
    ('Power and batteries', ['power', 'battery', 'cr2032', 'cr1220', 'regulator', 'fuse', 'ldo', 'buck', 'boost', 'charger', 'lipo', 'atx24', 'urb']),
    ('Memory cards', ['microsd', 'sd card', 'sdcard']),
    ('Connectors', ['usb', 'jack', 'jst', 'molex', 'connector', 'conn', 'terminal', 'springterminal', 'latchterminal', 'header', 'fpc', 'idc', 'pogo', 'socket', 'db9', 'db15', 'din5', 'bnc', 'vernier']),
]

def lib_info(fn):
    for pat, who, lic, share in LIBS:
        if re.search(pat, fn, re.I):
            return who, lic, share
    return 'KiCad library', 'licence not stated in the download: check before sharing', False

def nice(name):
    return re.sub(r'\s+', ' ', re.sub(r'[_\-]+', ' ', name)).strip()

def kind(title):
    t = ' ' + re.sub(r'[^a-z0-9]+', ' ', title.lower()) + ' '
    for k, words in KINDS:
        if any(re.search(r'\b' + re.escape(wd) + (r'\b' if len(wd) <= 4 else ''), t) for wd in words):
            return k
    return 'Modules'

def norm(t):
    return re.sub(r'[^a-z0-9]', '', t.lower())

# ---------------------------------------------------------------- a small S-expression reader
def read_sexpr(text):
    """A .kicad_mod file's content as nested lists: (a b (c d)) -> ['a','b',['c','d']]. Strings keep quotes
    stripped; numbers stay as text (converted with float() where used)."""
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    pos = 0
    def parse():
        nonlocal pos
        assert toks[pos] == '('
        pos += 1
        node = []
        while toks[pos] != ')':
            if toks[pos] == '(':
                node.append(parse())
            else:
                t = toks[pos]
                node.append(t[1:-1].replace('\\"', '"') if t.startswith('"') else t)
                pos += 1
        pos += 1
        return node
    return parse()

def children(node, tag):
    return [c for c in node[1:] if isinstance(c, list) and c and c[0] == tag]

def child(node, tag):
    c = children(node, tag)
    return c[0] if c else None

def num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default

def at(node):
    """A (at x y [rot]) child's position, or (0, 0) if there isn't one."""
    a = child(node, 'at')
    return (num(a[1], 0), num(a[2], 0)) if a else (0.0, 0.0)

# ---------------------------------------------------------------- one footprint -> board data
def board(fp):
    """Outline (mm, KiCad y-down), pads and holes of one footprint, or None if it isn't a module.
    Prefers the Edge.Cuts layer (the real board edge); many hand-made module footprints draw their
    outline on F.Fab instead (no Edge.Cuts at all, left for whoever uses the part to draw their own
    board), so that's used as a fallback."""
    by_layer = {}
    def add(layer, pts):
        by_layer.setdefault(layer, []).extend(pts)
    for ln in children(fp, 'fp_line'):
        la = child(ln, 'layer')
        if la:
            s, e = child(ln, 'start'), child(ln, 'end')
            add(la[1], [(num(s[1]), num(s[2])), (num(e[1]), num(e[2]))])
    for rc in children(fp, 'fp_rect'):
        la = child(rc, 'layer')
        if la:
            s, e = child(rc, 'start'), child(rc, 'end')
            add(la[1], [(num(s[1]), num(s[2])), (num(e[1]), num(e[2]))])
    for cc in children(fp, 'fp_circle'):
        la = child(cc, 'layer')
        if la:
            c, e = child(cc, 'center'), child(cc, 'end')
            cx, cy = num(c[1]), num(c[2])
            r = ((num(e[1]) - cx) ** 2 + (num(e[2]) - cy) ** 2) ** 0.5
            add(la[1], [(cx - r, cy - r), (cx + r, cy + r)])
    for pg in children(fp, 'fp_poly'):
        la = child(pg, 'layer')
        if la:
            pts = child(pg, 'pts')
            if pts:
                add(la[1], [(num(xy[1]), num(xy[2])) for xy in children(pts, 'xy')])
    edges = by_layer.get('Edge.Cuts') or by_layer.get('F.Fab') or []
    pads, holes = [], []
    for p in children(fp, 'pad'):
        pnum, ptype = (p[1] if len(p) > 1 else ''), (p[2] if len(p) > 2 else '')
        x, y = at(p)
        drill = child(p, 'drill')
        dia = num(drill[1], 0) if drill and len(drill) > 1 and drill[1] not in ('oval',) else (num(drill[2], 0) if drill and len(drill) > 2 else 0)
        if ptype == 'np_thru_hole' or (not pnum.strip() and dia >= 1.5):
            holes.append({'x': x, 'y': y, 'dia': dia or 3})
        elif ptype in ('thru_hole', 'smd', 'connect'):
            pads.append({'name': pnum or 'PIN', 'x': x, 'y': y})
    if len(pads) < 3 or not edges:
        return None
    xs = [p[0] for p in edges] + [p['x'] for p in pads] + [h['x'] for h in holes]
    ys = [p[1] for p in edges] + [p['y'] for p in pads] + [h['y'] for h in holes]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, d = x1 - x0, y1 - y0
    if min(w, d) < 10 or max(w, d) < 15 or w * d < 200:
        return None
    return {'x0': x0, 'y0': y0, 'w': w, 'd': d, 'pads': pads, 'holes': holes, 'edges': edges}

def picture(b, pins, holes, title):
    """A drawn top view at 10 px per mm: board, outline, mounting holes and pin numbers/names."""
    W, D, x0, y0 = b['w'], b['d'], b['x0'], b['y0']
    X = lambda x: (x - x0) * 10
    Y = lambda y: (y - y0) * 10
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*10:.0f}" height="{D*10:.0f}" viewBox="0 0 {W*10:.1f} {D*10:.1f}">',
         f'<rect width="{W*10:.1f}" height="{D*10:.1f}" rx="8" fill="#2d4a6b"/>']
    e = b['edges']
    for i in range(0, len(e) - 1, 2):
        s.append(f'<line x1="{X(e[i][0]):.1f}" y1="{Y(e[i][1]):.1f}" x2="{X(e[i+1][0]):.1f}" y2="{Y(e[i+1][1]):.1f}" stroke="#e8e8e8" stroke-width="2" opacity=".5"/>')
    s.append(f'<text x="{W*5:.1f}" y="{D*5:.1f}" font-family="Arial" font-size="{max(12, min(28, W*0.6)):.0f}" fill="#fff" opacity=".8" text-anchor="middle" dominant-baseline="middle">{html.escape(title[:40])}</text>')
    for h in holes:
        s.append(f'<circle cx="{h["x"]*10:.1f}" cy="{h["y"]*10:.1f}" r="{h["dia"]*5:.1f}" fill="#fff" stroke="#c9a227" stroke-width="3"/>')
    fs = 9 if len(pins) > 30 else 11
    for p in pins:
        s.append(f'<circle cx="{p["x"]*10:.1f}" cy="{p["y"]*10:.1f}" r="7" fill="#d4af37" stroke="#7a6010" stroke-width="1.5"/>')
        s.append(f'<text x="{p["x"]*10:.1f}" y="{p["y"]*10-10:.1f}" font-family="Arial" font-size="{fs}" fill="#fff" text-anchor="middle">{html.escape(p["name"][:8])}</text>')
    s.append('</svg>')
    return 'data:image/svg+xml;base64,' + base64.b64encode(''.join(s).encode()).decode()

def main(folders, shareable=False):
    files = sorted({f for d in folders for f in glob.glob(os.path.join(d, '**', '*.kicad_mod'), recursive=True) if '__MACOSX' not in f},
                   key=lambda f: next((i for i, k in enumerate(PRIORITY) if k in f.lower()), 99))
    if shareable:
        files = [f for f in files if lib_info(f)[2]]
    known = set()
    try:
        known = {norm(p['title']) for p in json.load(open(FRITZING, encoding='utf-8'))['parts']}
    except Exception:
        pass
    parts, seen, skipped = [], {}, {'chip or generic': 0, 'small or no outline': 0, 'duplicate': 0, 'in Fritzing library': 0, 'unreadable': 0}
    for fn in files:
        try:
            text = open(fn, encoding='utf-8').read()
            root = read_sexpr(text)
        except Exception:
            skipped['unreadable'] += 1
            continue
        if root[0] not in ('footprint', 'module'):
            continue
        fname = root[1] if len(root) > 1 and isinstance(root[1], str) else os.path.splitext(os.path.basename(fn))[0]
        base = os.path.basename(fname)
        if CHIP.match(base) or GENERIC.match(base):
            skipped['chip or generic'] += 1
            continue
        b = board(root)
        if not b:
            skipped['small or no outline'] += 1
            continue
        title = nice(base)
        lib = os.path.basename(os.path.dirname(fn)).replace('.pretty', '') or os.path.splitext(os.path.basename(fn))[0]
        who, lic, _ = lib_info(fn)
        pins = [{'name': p['name'], 'x': round(p['x'] - b['x0'], 2), 'y': round(p['y'] - b['y0'], 2)} for p in b['pads']]
        holes = [{'x': round(h['x'] - b['x0'], 2), 'y': round(h['y'] - b['y0'], 2), 'dia': round(h['dia'], 2)} for h in b['holes']]
        if norm(title) in known:
            skipped['in Fritzing library'] += 1
            continue
        key = (round(b['w']), round(b['d']), len(pins))
        if key in seen:
            old = parts[seen[key]]
            if holes and not old['features']:
                old['features'] = [{'t': 'hole', **h} for h in holes]
            skipped['duplicate'] += 1
            continue
        k = kind(title)
        credit = f'From {lib} ({who}), {lic}.'
        note = (' Pin numbers are from the footprint only (KiCad keeps signal names in the schematic symbol, '
                'not the footprint), so check and rename each pin\'s role before wiring.')
        seen[key] = len(parts)
        parts.append({
            'title': title, 'folder': 'kicad', 'file': f'{lib}/{base}.kicad_mod',
            'info': {'title': title, 'description': f'Board {b["w"]:.1f} x {b["d"]:.1f} mm, {len(pins)} pins. ' + credit + note,
                      'family': k, 'props': {'family': k, 'library': lib}, 'label': '', 'file': f'{lib}.pretty',
                      'tags': [lib, 'KiCad', k], 'credit': credit},
            'conns': [{'name': p['name'], 'desc': p['name'], 'svgId': f'p{i}'} for i, p in enumerate(pins)],
            'features': [{'t': 'hole', **h} for h in holes],
            'g': {'w': round(b['w'], 2), 'h': round(b['d'], 2), 'pos': {f'p{i}': [p['x'], p['y']] for i, p in enumerate(pins)},
                  'photo': picture(b, pins, holes, title)},
        })
    json.dump({'name': 'WaughForm 3D KiCad parts', 'made': date.today().isoformat(),
               'source': 'KiCad footprint libraries: ' + ', '.join(sorted({lib_info(f)[0] for f in files})) if files else 'KiCad footprint libraries',
               'credit': 'Each part keeps the credit and licence of the KiCad library it came from (see its description). Pin numbers are from the footprint only: check and rename pin roles before wiring.',
               'parts': parts}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'{len(parts)} parts written to {os.path.normpath(OUT)}')
    print('skipped:', ', '.join(f'{v} {k}' for k, v in skipped.items()))
    counts = {}
    for p in parts:
        counts[p['info']['family']] = counts.get(p['info']['family'], 0) + 1
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f'  {v:4} {k}')

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--shareable']
    if not args:
        sys.exit(__doc__)
    main(args, shareable='--shareable' in sys.argv)
