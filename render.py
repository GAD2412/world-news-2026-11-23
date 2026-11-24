"""Draws entry.png: the world's news of Monday 23 November 2026 on one 1024x1024 front page.

Run: python3 render.py  (needs Pillow and the macOS system fonts Charter, Avenir Next Condensed, Helvetica Neue).
Every story and figure is listed with its sources in FACTS.md. Drawing is deterministic: same input, same bytes.
Layout: masthead, a UTC table, the day in numbers, a region bar, 3 drawn leads, 10 drawn cards, a numbered map,
one-line briefs and a date check that names the earlier events left out.
"""
from PIL import Image, ImageDraw, ImageFont

S = 2                      # draw at 2x, then downsample for clean edges
W = H = 1024
AVC = '/System/Library/Fonts/Avenir Next Condensed.ttc'
HN = '/System/Library/Fonts/HelveticaNeue.ttc'
CH = '/System/Library/Fonts/Supplemental/Charter.ttc'

PAPER = (248, 245, 238)
CARD = (255, 253, 248)
INK = (22, 24, 30)
GREY = (96, 100, 108)
RULE = (208, 202, 190)
NAVY = (20, 34, 60)
RED = (176, 32, 38)
GOLD = (240, 200, 100)

REGIONS = {
    'EUROPE': (36, 88, 168),
    'MIDDLE EAST': (184, 44, 40),
    'AFRICA': (204, 122, 18),
    'AMERICAS': (124, 46, 164),
    'SOUTH ASIA': (196, 64, 128),
    'ASIA-PACIFIC': (16, 136, 118),
    'GLOBAL': (70, 74, 84),
}
STATUS = {'CONFIRMED': (30, 120, 64), 'OFFICIAL': (40, 92, 170), 'REPORTED': (110, 114, 122), 'CLAIM': (214, 120, 20)}

_fonts = {}


def font(kind, size):
    key = (kind, size)
    if key not in _fonts:
        path, idx = {
            'black': (CH, 5), 'serif': (CH, 3), 'roman': (CH, 0),
            'heavy': (AVC, 8), 'bold': (AVC, 0), 'demi': (AVC, 2), 'med': (AVC, 5),
            'reg': (HN, 0), 'hbold': (HN, 1),
        }[kind]
        _fonts[key] = ImageFont.truetype(path, int(size * S), index=idx)
    return _fonts[key]


img = Image.new('RGB', (W * S, H * S), PAPER)
d = ImageDraw.Draw(img)


def P(*v):
    return [x * S for x in v]


def text(x, y, s, kind, size, fill=INK, anchor='la'):
    d.text((x * S, y * S), s, font=font(kind, size), fill=fill, anchor=anchor)


def tw(s, kind, size):
    return d.textlength(s, font=font(kind, size)) / S


def wrap(s, kind, size, width):
    lines, cur = [], ''
    for w in s.split():
        t = (cur + ' ' + w).strip()
        if tw(t, kind, size) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, kind, size, width, lead, fill=INK, max_lines=9):
    lines = wrap(s, kind, size, width)
    assert len(lines) <= max_lines, (s, len(lines))
    for i, ln in enumerate(lines):
        text(x, y + i * lead, ln, kind, size, fill)
    return y + len(lines) * lead


def rect(x0, y0, x1, y1, fill=None, outline=None, width=1, r=0):
    if r:
        d.rounded_rectangle(P(x0, y0, x1, y1), radius=r * S, fill=fill, outline=outline, width=int(width * S))
    else:
        d.rectangle(P(x0, y0, x1, y1), fill=fill, outline=outline, width=int(width * S))


def poly(pts, fill):
    d.polygon([v * S for p in pts for v in p], fill=fill)


def ell(cx, cy, rx, ry, fill=None, outline=None, width=1):
    d.ellipse(P(cx - rx, cy - ry, cx + rx, cy + ry), fill=fill, outline=outline, width=int(width * S))


def line(pts, fill, width=1):
    d.line([v * S for p in pts for v in p], fill=fill, width=int(width * S))


def badge(x, y, n, col):
    ell(x + 8, y + 8, 8, 8, fill=col, outline=(255, 255, 255), width=1.2)
    text(x + 8, y + 8.5, str(n), 'heavy', 10, (255, 255, 255), 'mm')


def chip(x, y, label, col, right=False):
    w = tw(label, 'heavy', 8.5) + 8
    if right:
        x -= w
    rect(x, y, x + w, y + 12, fill=col, r=2)
    text(x + 4, y + 1.5, label, 'heavy', 8.5, (255, 255, 255))
    return w


# ------------------------------------------------------------------ stories
LEADS = [
    dict(n=1, region='AMERICAS', field='TECH', place='SANTA CLARA, US', when='MON', status='CONFIRMED',
         art='nvidia', ll=(-122.0, 37.4),
         head='Nvidia brings back Jensen Huang as CEO',
         dek='The board reinstates him with immediate effect, little more than a week after he quit over affairs, '
             'one of them with an alleged Chinese spy.',
         src='Al Jazeera · Guardian · CBS'),
    dict(n=2, region='EUROPE', field='WAR', place='KYIV · BENGHAZI', when='MON MORNING', status='OFFICIAL',
         art='ship', ll=(30.5, 50.4),
         head='Ukraine says it sank Russian warship off Libya',
         dek='Zelenskyy hails an "exemplary operation"; the SBU says seven sea drones from a mothership hit the '
             'Merkury and a cargo ship. Moscow warns of a "dangerous trend".',
         src='Al Jazeera · Guardian'),
    dict(n=3, region='MIDDLE EAST', field='RIGHTS', place='TEHRAN, IRAN', when='MON', status='CONFIRMED',
         art='singer', ll=(51.4, 35.7),
         head='Iran flogs singer who sang without hijab',
         dek='Parastoo Ahmadi and four of her team are flogged for "offending public decency" and banned '
             'from travel and artistic work for two years.',
         src='Al Jazeera · Guardian · BBC'),
]
CARDS = [
    dict(n=4, region='ASIA-PACIFIC', field='JUSTICE', place='DUSHANBE', when='MON', status='CONFIRMED',
         art='icc', ll=(68.8, 38.6), label='ICC EXIT',
         head='Tajikistan moves to quit the ICC',
         dek='Fourth country to start leaving since a US push in July.',
         src='Al Jazeera · Reuters'),
    dict(n=5, region='EUROPE', field='SECURITY', place='MOSCOW · TALLINN', when='MON', status='OFFICIAL',
         art='border', ll=(24.7, 59.4), label='WARNING',
         head='Russia warns Estonia of "open war"',
         dek='Foreign ministry accuses Tallinn of "hostile actions".',
         src='Russian MFA via Al Jazeera'),
    dict(n=6, region='EUROPE', field='LABOUR', place='BRUSSELS', when='06-20 UTC', status='OFFICIAL',
         art='plane', ll=(4.5, 50.9), label='STRIKE',
         head='Strike grounds Belgian flights',
         dek='Brussels Airport cancels all flights in a national strike.',
         src='Brussels Airport via Al Jazeera'),
    dict(n=7, region='ASIA-PACIFIC', field='MARKETS', place='SEOUL', when='CLOSE 06:30 UTC', status='REPORTED',
         art='chart', ll=(127.0, 37.5), label='KOSPI',
         head='AI fears knock Seoul stocks',
         dek='Kospi falls as much as 5.8%, closes down 3.3%; Samsung -3.1%.',
         src='Al Jazeera'),
    dict(n=8, region='SOUTH ASIA', field='DIPLOMACY', place='NEW DELHI', when='MON', status='OFFICIAL',
         art='money', ll=(77.2, 28.6), label='AID',
         head='India pledges $1.62bn to Nepal',
         dek='Flood-recovery package as PM Balendra Shah meets Modi.',
         src='Al Jazeera'),
    dict(n=9, region='AMERICAS', field='CONFLICT', place='CÚCUTA, COLOMBIA', when='MON', status='CONFIRMED',
         art='drone', ll=(-72.5, 7.9), label='DRONE ATTACK',
         head='Drone hits Colombian police base',
         dek='Three civilians hurt, an infant among them; 60 homes damaged.',
         src='Al Jazeera · Colombia Reports'),
    dict(n=10, region='AMERICAS', field='SANCTIONS', place='WASHINGTON', when='MON', status='OFFICIAL',
         art='sanctions', ll=(-77.0, 38.9), label='TREASURY',
         head='US widens sanctions on Iran',
         dek='Over two dozen entities in "shadow banking" networks targeted.',
         src='US Treasury via Al Jazeera'),
    dict(n=11, region='MIDDLE EAST', field='ENVIRONMENT', place='GAZA', when='MON', status='CONFIRMED',
         art='toxic', ll=(34.4, 31.4), label='OXFAM REPORT',
         head='Gaza left a "toxic wasteland"',
         dek='Pollution found in 99% of the strip; water and soil poisoned.',
         src='Al Jazeera · Guardian'),
    dict(n=12, region='ASIA-PACIFIC', field='CRICKET', place='WELLINGTON', when='MON (NZT)', status='REPORTED',
         art='cricket', ll=(174.8, -41.3), label='DRAWN',
         head='New Zealand hold out to draw Test',
         dek='They bat 120 overs to 239-5 to deny India victory.',
         src='Al Jazeera'),
    dict(n=13, region='EUROPE', field='ENERGY', place='AMSTERDAM (TTF)', when='MON', status='REPORTED',
         art='gas', ll=(4.9, 52.4), label='GAS PRICE',
         head='Cold-snap fears lift European gas',
         dek='Benchmark up as much as 8.6% to €96.08, closes +4%.',
         src='Guardian'),
]
BRIEFS = [  # region, place, text, outlet, status, field
    ('MIDDLE EAST', 'Yemen', 'air raid kills at least 8 in Houthi-held Hodeidah', 'Al Jazeera', 'REPORTED', 'WAR'),
    ('MIDDLE EAST', 'Gaza', 'Israeli strikes kill 3, among them an UNRWA worker', 'UNRWA', 'OFFICIAL', 'WAR'),
    ('MIDDLE EAST', 'Istanbul', 'police hunt a lioness seen in a northern suburb', 'Al Jazeera', 'REPORTED', 'WILDLIFE'),
    ('MIDDLE EAST', 'Iraq', 'Turkey says PKK has left 14 more bases', 'AFP', 'CLAIM', 'SECURITY'),
    ('EUROPE', 'Schools', 'hundreds in Germany, Denmark get bomb threats', 'Reuters · AJ', 'CONFIRMED', 'SECURITY'),
    ('EUROPE', 'Brussels', 'EU proposes Russia sanctions incl. a sports ban', 'Al Jazeera', 'OFFICIAL', 'SANCTIONS'),
    ('EUROPE', 'Denmark', 'top court backs "ghetto law" evictions', 'Al Jazeera', 'REPORTED', 'JUSTICE'),
    ('EUROPE', 'Russia', 'leaked data: 1,000+ military suicides in war', 'Guardian', 'REPORTED', 'WAR'),
    ('EUROPE', 'Berlin', 'weighs reports Russia may put nukes in space', 'Guardian', 'REPORTED', 'SPACE'),
    ('AMERICAS', 'SpaceX', 'Virginia and Oregon sue over Grok sexual images', 'Al Jazeera', 'OFFICIAL', 'TECH'),
    ('AMERICAS', 'Iowa', 'Trump delays an ammunition-plant detonation', 'Al Jazeera', 'REPORTED', 'POLITICS'),
    ('AMERICAS', 'Quebec', 'court says legislators must swear oath to King', 'AFP', 'REPORTED', 'JUSTICE'),
    ('SOUTH ASIA', 'Bangladesh', 'garment workers reject employers\' pay offer', 'Al Jazeera', 'REPORTED', 'LABOUR'),
    ('SOUTH ASIA', 'Pakistan', 'truck crash kills 7 in Punjab', 'Xinhua', 'REPORTED', 'ACCIDENTS'),
    ('ASIA-PACIFIC', 'Canberra', 'Chalmers: unemployment to top 5%', 'Guardian', 'OFFICIAL', 'ECONOMY'),
    ('ASIA-PACIFIC', 'Sydney', '"pervert glasses" is Macquarie word of the year', 'Guardian', 'REPORTED', 'CULTURE'),
    ('ASIA-PACIFIC', 'Tokyo', 'calls grow for education minister Seki to quit', 'Xinhua', 'REPORTED', 'POLITICS'),
    ('AFRICA', 'Nigeria', 'Tinubu seeks to decriminalise attempted suicide', 'allAfrica', 'REPORTED', 'HEALTH'),
    ('AFRICA', 'Kenya-DRC', 'move to restore diplomatic ties', 'allAfrica', 'REPORTED', 'DIPLOMACY'),
]
STORIES = len(LEADS) + len(CARDS) + len(BRIEFS)
assert STORIES == 32, STORIES
counts = {r: 0 for r in REGIONS}
for s in LEADS + CARDS:
    counts[s['region']] += 1
for b in BRIEFS:
    counts[b[0]] += 1
SPORTS = {'CRICKET'}
FIELDS = {('SPORT' if f in SPORTS else 'WAR' if f in ('CONFLICT', 'WAR') else f)
          for f in [s['field'] for s in LEADS + CARDS] + [b[5] for b in BRIEFS]}
NFIELDS = len(FIELDS)
NREG = sum(1 for r in counts if counts[r] and r != 'GLOBAL')
print('fields', NFIELDS, sorted(FIELDS), 'regions', NREG)

# ------------------------------------------------------------------ top rail and masthead
rect(0, 0, W, 18, fill=NAVY)
text(14, 3.5, 'THE WORLD IN ONE DAY  ·  FINAL EDITION: OUTCOMES, NOT PREVIEWS', 'heavy', 10.5, GOLD)
text(W - 14, 3.5, '%d STORIES · %d REGIONS · %d FIELDS · EVERY ONE DATED MONDAY 23 NOVEMBER 2026'
     % (STORIES, NREG, NFIELDS), 'heavy', 10.5, (255, 255, 255), 'ra')
MAST = 'Monday 23 November 2026'
assert tw(MAST, 'black', 62) < 990
text(W / 2, 19, MAST, 'black', 62, NAVY, 'ma')
mast_bottom = d.textbbox((W / 2 * S, 19 * S), MAST, font=font('black', 62), anchor='ma')[3] / S
assert mast_bottom + 1 + 17 < 113, mast_bottom
text(W / 2, mast_bottom + 1, 'Nvidia brings back Huang  ·  Ukraine claims Libya sinking  ·  Iran flogs a singer  ·  '
     'Russia warns Estonia', 'serif', 14.5, RED, 'ma')
d.line(P(14, 113, W - 14, 113), fill=INK, width=2 * S)


def row_label(y, h, lines):
    rect(14, y, 92, y + h, fill=RED)
    for j, ln in enumerate(lines):
        text(53, y + h / 2 - 6 * len(lines) + 1 + 12 * j, ln, 'heavy', 10.5, (255, 255, 255), 'ma')


UTC = [('~05:30', 'NZ draw Test v India'), ('06:00', 'Brussels flights halted'), ('06:30', 'Kospi shuts -3.3%'),
       ('~07:30', 'Kyiv claims Libya strike'), ('~14:00', 'Nvidia reinstates Huang'), ('~19:00', 'Moscow warns Tallinn'),
       ('~21:00', 'US sanctions on Iran')]
row_label(117, 34, ['THE DAY', 'IN UTC'])
cw = (W - 14 - 96) / len(UTC)
for i, (t, lab) in enumerate(UTC):
    x = 96 + i * cw
    if i:
        d.line(P(x, 119, x, 149), fill=RULE, width=S)
    text(x + cw / 2, 117, t, 'black', 14, INK, 'ma')
    assert tw(lab, 'med', 10) < cw - 4, lab
    text(x + cw / 2, 137, lab, 'med', 10, GREY, 'ma')
d.line(P(14, 154, W - 14, 154), fill=RULE, width=S)

NUMS = [('-3.3%', 'Kospi close, Seoul'), ('7', 'sea drones, SBU says'), ('$1.62bn', "India's package to Nepal"),
        ('4th', 'country leaving the ICC'), ('239-5', 'NZ bat out a draw'), ('+8.6%', 'EU gas at its peak')]
row_label(158, 34, ['THE DAY IN', 'NUMBERS'])
cw = (W - 14 - 96) / len(NUMS)
for i, (big, small) in enumerate(NUMS):
    x = 96 + i * cw
    if i:
        d.line(P(x, 160, x, 190), fill=RULE, width=S)
    text(x + cw / 2, 156, big, 'black', 18, RED, 'ma')
    assert tw(small, 'med', 10) < cw - 4, small
    text(x + cw / 2, 179, small, 'med', 10, GREY, 'ma')

x = 14
for reg, c in REGIONS.items():
    if not counts[reg]:
        continue
    w = (W - 28) * counts[reg] / STORIES
    rect(x, 196, x + w, 210, fill=c)
    lab = '%s %d' % (reg, counts[reg])
    if tw(lab, 'heavy', 9.5) > w - 6:
        lab = '%s %d' % ({'SOUTH ASIA': 'S. ASIA', 'ASIA-PACIFIC': 'ASIA-PAC', 'MIDDLE EAST': 'MID-EAST'}.get(reg, reg[:4]),
                         counts[reg])
    assert tw(lab, 'heavy', 9.5) <= w - 4, lab
    text(x + w / 2, 197, lab, 'heavy', 9.5, (255, 255, 255), 'ma')
    x += w


# ------------------------------------------------------------------ drawings
def sky(x, y, w, h, top, bottom):
    for i in range(int(h)):
        t = i / max(1, h - 1)
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        d.line(P(x, y + i, x + w, y + i), fill=c, width=S + 1)


def art_nvidia(x, y, w, h):
    sky(x, y, w, h, (18, 24, 30), (40, 52, 46))
    cx, cy = x + 80, y + h / 2 + 4
    rect(cx - 38, cy - 38, cx + 38, cy + 38, fill=(60, 66, 72), outline=(118, 185, 0), width=2, r=4)
    rect(cx - 24, cy - 24, cx + 24, cy + 24, fill=(30, 34, 38), outline=(118, 185, 0), width=1.5)
    for k in range(6):
        o = -30 + k * 12
        line([(cx + o, cy - 38), (cx + o, cy - 46)], (190, 196, 200), 2)
        line([(cx + o, cy + 38), (cx + o, cy + 46)], (190, 196, 200), 2)
        line([(cx - 38, cy + o), (cx - 46, cy + o)], (190, 196, 200), 2)
        line([(cx + 38, cy + o), (cx + 46, cy + o)], (190, 196, 200), 2)
    text(cx, cy + 1, 'GPU', 'heavy', 15, (118, 185, 0), 'mm')
    # the chair: resigned on 12 Nov, back on 23 Nov
    bx = x + 160
    rect(bx, y + 10, bx + 140, y + h - 22, fill=(250, 250, 246), r=4)
    text(bx + 10, y + 15, 'CEO, NVIDIA', 'heavy', 12, (30, 34, 38))
    text(bx + 10, y + 32, '12 Nov: resigns', 'demi', 12, GREY)
    line([(bx + 10, y + 39), (bx + 92, y + 39)], RED, 1.5)
    text(bx + 10, y + 50, '23 Nov: back', 'heavy', 16, (60, 120, 0))
    text(bx + 10, y + 68, 'with immediate effect', 'demi', 10, GREY)


def art_ship(x, y, w, h):
    sky(x, y, w, h, (26, 34, 64), (88, 70, 96))
    for sx, sy in [(30, 14), (90, 24), (160, 10), (250, 20), (300, 12)]:
        ell(x + sx, y + sy, 1.2, 1.2, fill=(255, 255, 230))
    wy = y + h - 40
    rect(x, wy + 6, x + 88, wy + 20, fill=(120, 116, 108))
    rect(x, wy + 20, x + w, y + h, fill=(30, 60, 110))
    rect(x + 88, wy, x + w, wy + 20, fill=(30, 60, 110))
    hull = Image.new('RGBA', (190 * S, 64 * S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hull)
    hd.polygon([(0, 18 * S), (160 * S, 18 * S), (188 * S, 4 * S), (176 * S, 42 * S), (12 * S, 42 * S)],
               fill=(110, 116, 124, 255))
    hd.rectangle((46 * S, 2 * S, 104 * S, 18 * S), fill=(140, 146, 154, 255))
    hull = hull.rotate(-22, resample=Image.BICUBIC, expand=True)
    img.paste(hull, (int((x + 92) * S), int((wy - 52) * S)), hull)
    rect(x + 88, wy + 14, x + w, y + h, fill=(30, 60, 110))
    for i in range(5):
        yy = wy + 20 + (i % 2) * 7
        d.arc(P(x + 100 + i * 34, yy, x + 136 + i * 34, yy + 8), 200, 340, fill=(150, 180, 220), width=2 * S)
    # mothership and seven drones
    rect(x + 14, y + h - 16, x + 60, y + h - 8, fill=(70, 74, 82))
    for k in range(7):
        dx, dy = x + 70 + k * 13, y + h - 11 + (k % 2) * 3
        poly([(dx, dy), (dx + 10, dy - 2), (dx + 10, dy + 2)], (235, 235, 235))
    text(x + 8, y + 6, 'MERKURY, BENGHAZI', 'heavy', 10, (255, 255, 255))
    text(x + w - 8, y + 4, '7 drones', 'black', 16, (255, 220, 120), 'ra')


def art_singer(x, y, w, h):
    sky(x, y, w, h, (30, 22, 40), (70, 40, 60))
    poly([(x + 60, y), (x + 120, y), (x + 150, y + h), (x + 30, y + h)], (90, 70, 96))
    rect(x, y + h - 14, x + w, y + h, fill=(50, 34, 44))
    mx = x + 90
    line([(mx, y + h - 14), (mx, y + 40)], (200, 200, 210), 2.5)
    rect(mx - 7, y + 24, mx + 7, y + 44, fill=(60, 60, 66), r=6)
    for k in range(4):
        line([(mx - 6, y + 28 + k * 4), (mx + 6, y + 28 + k * 4)], (120, 120, 128), 1)
    bx = x + 170
    rect(bx, y + 20, bx + 140, y + h - 18, fill=(250, 248, 242), r=4)
    text(bx + 10, y + 27, 'VERDICT', 'heavy', 12, RED)
    text(bx + 10, y + 45, 'flogged · 5 people', 'demi', 12, INK)
    text(bx + 10, y + 61, '2-year bans on travel', 'demi', 11, GREY)
    text(bx + 10, y + 74, 'and artistic work', 'demi', 11, GREY)


def art_icc(x, y, w, h):
    sky(x, y, w, h, (226, 232, 242), (244, 246, 250))
    cx = x + 52
    line([(cx, y + 10), (cx, y + h - 6)], (90, 96, 110), 2.5)
    line([(cx - 26, y + 16), (cx + 26, y + 16)], (90, 96, 110), 2.5)
    for sx in (cx - 26, cx + 26):
        d.pieslice(P(sx - 11, y + 22, sx + 11, y + 40), 0, 180, fill=(200, 170, 90))
    rect(cx - 14, y + h - 8, cx + 14, y + h - 4, fill=(90, 96, 110))
    text(x + w - 8, y + 8, '4th exit', 'black', 17, (16, 136, 118), 'ra')


def art_border(x, y, w, h):
    sky(x, y, w, h, (220, 228, 236), (238, 242, 246))
    rect(x + w / 2 - 2, y, x + w / 2 + 2, y + h, fill=(150, 40, 40))
    for k in range(4):
        rect(x + w / 2 - 14, y + 8 + k * 12, x + w / 2 + 14, y + 12 + k * 12, fill=(200, 60, 50))
    text(x + w / 2 - 20, y + 22, 'RUSSIA', 'heavy', 11, INK, 'ra')
    text(x + w / 2 + 20, y + 22, 'ESTONIA', 'heavy', 11, INK)


def art_plane(x, y, w, h):
    sky(x, y, w, h, (200, 214, 230), (232, 238, 246))
    rect(x, y + h - 10, x + w, y + h, fill=(130, 130, 136))
    px, py = x + 70, y + h - 22
    poly([(px - 34, py + 4), (px + 30, py - 2), (px + 36, py + 2), (px - 30, py + 8)], (90, 100, 120))
    poly([(px - 6, py + 2), (px + 6, py - 14), (px + 12, py - 14), (px + 6, py + 4)], (90, 100, 120))
    line([(x + 120, y + 10), (x + 150, y + 40)], RED, 4)
    line([(x + 150, y + 10), (x + 120, y + 40)], RED, 4)


def art_chart(x, y, w, h):
    rect(x, y, x + w, y + h, fill=(20, 26, 36))
    pts = [(x + 10, y + 16), (x + 30, y + 12), (x + 50, y + 20), (x + 70, y + 18), (x + 90, y + 34),
           (x + 110, y + 44), (x + 125, y + 38)]
    line(pts, (230, 60, 50), 2.5)
    text(x + w - 8, y + 8, '-3.3%', 'black', 18, (240, 90, 80), 'ra')


def art_money(x, y, w, h):
    sky(x, y, w, h, (236, 228, 210), (246, 240, 228))
    ell(x + 40, y + h / 2 + 4, 18, 18, fill=(200, 150, 50))
    text(x + 40, y + h / 2 + 4, '$', 'black', 18, (255, 250, 230), 'mm')
    text(x + w - 8, y + 10, '$1.62bn', 'black', 18, (196, 64, 128), 'ra')


def art_drone(x, y, w, h):
    sky(x, y, w, h, (214, 224, 236), (236, 240, 246))
    for k, (bw, bh) in enumerate([(26, 18), (30, 24), (22, 16), (28, 20)]):
        bx = x + 6 + k * 30
        rect(bx, y + h - bh, bx + bw, y + h, fill=(176, 150, 120) if k != 1 else (130, 100, 80))
    dx, dy = x + 70, y + 14
    rect(dx - 8, dy - 3, dx + 8, dy + 3, fill=(50, 50, 56))
    for ox in (-14, 14):
        line([(dx, dy), (dx + ox, dy - 4)], (50, 50, 56), 1.5)
        ell(dx + ox, dy - 5, 5, 1.5, fill=(80, 80, 86))
    text(x + w - 8, y + 8, '60 homes', 'black', 15, (124, 46, 164), 'ra')


def art_sanctions(x, y, w, h):
    sky(x, y, w, h, (226, 232, 242), (244, 246, 250))
    rect(x + 16, y + 6, x + 62, y + h - 4, fill=(255, 255, 255), outline=GREY, width=0.8)
    for k in range(4):
        line([(x + 22, y + 14 + k * 7), (x + 56, y + 14 + k * 7)], RULE, 1.5)
    text(x + w - 8, y + 8, '24+ targets', 'black', 15, (40, 92, 170), 'ra')


def art_toxic(x, y, w, h):
    sky(x, y, w, h, (214, 206, 180), (230, 222, 200))
    poly([(x + 40, y + 8), (x + 54, y + 30), (x + 40, y + 44), (x + 26, y + 30)], (90, 120, 60))
    ell(x + 40, y + 32, 14, 12, fill=(90, 120, 60))
    text(x + w - 8, y + 8, '99%', 'black', 20, (184, 44, 40), 'ra')


def art_cricket(x, y, w, h):
    rect(x, y, x + w, y + h, fill=(92, 160, 80))
    rect(x + 30, y + 8, x + 60, y + h, fill=(214, 196, 150))
    for k in range(3):
        rect(x + 40 + k * 4, y + 12, x + 41.5 + k * 4, y + 28, fill=(250, 250, 250))
    rect(x + w - 70, y + 8, x + w - 6, y + 32, fill=(20, 30, 20), r=3)
    text(x + w - 38, y + 9, '239-5', 'heavy', 16, (250, 210, 90), 'ma')


def art_gas(x, y, w, h):
    sky(x, y, w, h, (24, 30, 56), (50, 60, 96))
    poly([(x + 40, y + 8), (x + 54, y + 30), (x + 48, y + h - 6), (x + 32, y + h - 6), (x + 26, y + 30)], (70, 140, 240))
    poly([(x + 40, y + 22), (x + 47, y + 34), (x + 44, y + h - 8), (x + 36, y + h - 8), (x + 33, y + 34)], (170, 210, 255))
    text(x + w - 8, y + 8, '+8.6%', 'black', 18, (255, 200, 90), 'ra')


ART_FNS = {k[4:]: v for k, v in globals().items() if k.startswith('art_')}


def draw_art(key, x, y, w, h):
    """Draw one picture and keep only what falls inside its box (rotated pastes may spill)."""
    before = img.copy()
    ART_FNS[key](x, y, w, h)
    box = (int(x * S), int(y * S), int((x + w) * S), int((y + h) * S))
    inside = img.crop(box)
    img.paste(before)
    img.paste(inside, box[:2])


# ------------------------------------------------------------------ leads
LY = 216
LW = (W - 28 - 24) / 3
for i, L in enumerate(LEADS):
    x = 14 + i * (LW + 12)
    c = REGIONS[L['region']]
    rect(x, LY, x + LW, 446, fill=CARD, outline=RULE, width=1)
    draw_art(L['art'], x, LY, LW, 104)
    rect(x, LY, x + LW, LY + 3, fill=c)
    badge(x + 6, LY + 82, L['n'], c)
    chip(x + LW - 6, LY + 88, L['status'], STATUS[L['status']], right=True)
    tag = '%s · %s' % (L['place'], L['field'])
    text(x + 8, LY + 108, tag, 'heavy', 10.5, c)
    text(x + LW - 8, LY + 108.5, L['when'], 'demi', 10, GREY, 'ra')
    assert tw(tag, 'heavy', 10.5) + tw(L['when'], 'demi', 10) + 10 < LW - 16, tag
    yy = para(x + 8, LY + 121, L['head'], 'serif', 21, LW - 16, 23, INK, 2)
    yy = para(x + 8, yy + 2, L['dek'], 'reg', 11.5, LW - 16, 13.8, (44, 46, 52), 3)
    assert yy <= 432, (L['head'], yy)
    text(x + 8, 432, L['src'], 'med', 9.5, GREY)

# ------------------------------------------------------------------ cards
CY = 452
CWD = (W - 28 - 4 * 7) / 5
for k, C in enumerate(CARDS):
    col, row = k % 5, k // 5
    x = 14 + col * (CWD + 7)
    y = CY + row * 154
    c = REGIONS[C['region']]
    rect(x, y, x + CWD, y + 148, fill=CARD, outline=RULE, width=1)
    draw_art(C['art'], x, y, CWD, 54)
    rect(x, y, x + CWD, y + 3, fill=c)
    badge(x + 5, y + 34, C['n'], c)
    chip(x + CWD - 5, y + 38, C['status'], STATUS[C['status']], right=True)
    lw = tw(C['label'], 'heavy', 9) + 10
    rect(x + 5, y + 6, x + 5 + lw, y + 20, fill=(20, 24, 34), r=2)
    text(x + 10, y + 7.5, C['label'], 'heavy', 9, (255, 255, 255))
    tag = '%s · %s' % (C['place'], C['field'])
    text(x + 7, y + 58, tag, 'heavy', 10, c)
    text(x + CWD - 7, y + 58.5, C['when'], 'demi', 9.5, GREY, 'ra')
    assert tw(tag, 'heavy', 10) + tw(C['when'], 'demi', 9.5) + 8 < CWD - 14, tag
    yy = para(x + 7, y + 71, C['head'], 'serif', 14.5, CWD - 14, 16.5, INK, 2)
    yy = para(x + 7, yy + 2, C['dek'], 'reg', 10.5, CWD - 14, 12.5, (44, 46, 52), 3)
    assert yy <= y + 134, (C['head'], yy - y)
    text(x + 7, y + 134, C['src'], 'med', 9, GREY)

# ------------------------------------------------------------------ map with numbered pins
MX0, MY0, MW, MH = 14, 778, 300, 156
text(MX0, 762, 'WHERE IT HAPPENED', 'heavy', 11.5, NAVY)
text(MX0 + 116, 763.5, 'pins = story numbers 1-13', 'med', 9.5, GREY)
rect(MX0, MY0, MX0 + MW, MY0 + MH, fill=(226, 234, 242))
LON0, LON1, LAT0, LAT1 = -170, 180, -50, 78


def mp(lon, lat):
    return (MX0 + (lon - LON0) / (LON1 - LON0) * MW, MY0 + (LAT1 - lat) / (LAT1 - LAT0) * MH)


LAND = [  # rough coastlines (lon, lat), enough for a dotted locator map
    [(-168, 66), (-156, 71), (-125, 70), (-95, 72), (-80, 73), (-62, 66), (-55, 52), (-66, 45), (-75, 35), (-81, 25),
     (-90, 29), (-97, 26), (-97, 20), (-87, 21), (-83, 10), (-78, 8), (-86, 13), (-95, 16), (-105, 20), (-112, 30),
     (-117, 33), (-124, 40), (-125, 49), (-135, 58), (-150, 60), (-165, 60)],
    [(-55, 60), (-45, 60), (-20, 70), (-20, 80), (-60, 82), (-70, 77)],
    [(-80, 9), (-72, 12), (-60, 10), (-50, 0), (-35, -5), (-38, -13), (-48, -26), (-58, -35), (-65, -42), (-68, -55),
     (-75, -50), (-73, -35), (-71, -18), (-81, -5)],
    [(-10, 36), (-9, 44), (-2, 44), (-5, 48), (2, 51), (8, 54), (10, 58), (5, 62), (15, 69), (28, 71), (40, 67),
     (60, 70), (80, 73), (105, 78), (140, 72), (170, 68), (180, 65), (160, 58), (142, 52), (135, 43), (128, 35),
     (122, 30), (120, 22), (108, 20), (108, 10), (103, 1), (98, 8), (98, 16), (92, 22), (88, 22), (80, 15), (77, 8),
     (72, 20), (66, 25), (57, 25), (60, 22), (52, 16), (44, 12), (38, 20), (35, 30), (32, 31), (26, 40), (23, 36),
     (15, 38), (12, 44), (5, 43), (0, 39)],
    [(-17, 21), (-10, 35), (10, 37), (32, 31), (34, 28), (43, 12), (51, 12), (40, -3), (40, -15), (35, -25),
     (20, -35), (15, -28), (12, -15), (13, -5), (9, 4), (-8, 4), (-15, 10)],
    [(114, -22), (123, -17), (131, -12), (142, -11), (146, -19), (153, -27), (150, -37), (140, -38), (132, -32), (115, -35)],
    [(130, 31), (135, 34), (140, 36), (142, 40), (141, 45), (139, 38), (132, 34)],
    [(-6, 50), (1, 51), (-2, 56), (-5, 58), (-6, 55)],
    [(95, 5), (106, -6), (115, -8), (120, -9), (118, -3), (110, -2), (104, 2)],
    [(109, 1), (117, 7), (119, 1), (116, -4), (110, -3)],
    [(172, -34), (178, -38), (174, -41), (167, -46), (170, -44)],
    [(44, -25), (47, -25), (50, -15), (49, -12)],
]
mask = Image.new('L', (MW, MH), 0)
md = ImageDraw.Draw(mask)
for shape in LAND:
    md.polygon([(p[0] - MX0, p[1] - MY0) for p in (mp(*q) for q in shape)], fill=255)
for gy in range(2, MH, 5):
    for gx in range(2, MW, 5):
        if mask.getpixel((gx, gy)):
            ell(MX0 + gx, MY0 + gy, 1.5, 1.5, fill=(150, 160, 175))
pins = [[*mp(*s['ll']), *mp(*s['ll']), s] for s in LEADS + CARDS]
for _ in range(120):
    for a in pins:
        for b in pins:
            if a is b:
                continue
            dx, dy = a[0] - b[0], a[1] - b[1]
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < 13.5:
                if dist < 1e-6:
                    dx, dy, dist = (1.0, 0.3, 1.0) if a[4]['n'] > b[4]['n'] else (-1.0, -0.3, 1.0)
                push = (13.5 - dist) / 2
                a[0] += dx / dist * push
                a[1] += dy / dist * push
        a[0] = min(max(a[0], MX0 + 7), MX0 + MW - 7)
        a[1] = min(max(a[1], MY0 + 7), MY0 + MH - 7)
for px, py, ox, oy, s in pins:
    ell(ox, oy, 1.8, 1.8, fill=INK)
    line([(ox, oy), (px, py)], INK, 0.8)
for px, py, ox, oy, s in pins:
    ell(px, py, 6.5, 6.5, fill=REGIONS[s['region']], outline=(255, 255, 255), width=1)
    text(px, py + 0.5, str(s['n']), 'heavy', 8, (255, 255, 255), 'mm')

# ------------------------------------------------------------------ briefs
BX = 330
text(BX, 762, 'ALSO ON MONDAY 23 NOVEMBER — %d MORE STORIES' % len(BRIEFS), 'heavy', 11.5, NAVY)
BCW = (W - 14 - BX - 12) / 2
for k, (reg, place, body, outlet, status, _field) in enumerate(BRIEFS):
    col, row = k // 10, k % 10
    x = BX + col * (BCW + 12)
    y = 779 + row * 15.6
    c = REGIONS[reg]
    n = 14 + k
    text(x, y, str(n), 'heavy', 11.5, c)
    xx = x + 17
    text(xx, y, place + ':', 'bold', 11.5, c)
    xx += tw(place + ': ', 'bold', 11.5)
    text(xx, y, body, 'med', 11.5, INK)
    xx += tw(body + ' ', 'med', 11.5)
    tag = outlet + ('' if status in ('CONFIRMED', 'OFFICIAL') else ' · ' + status)
    text(xx, y + 1, tag, 'med', 9, STATUS['CLAIM'] if status == 'CLAIM' else GREY)
    xx += tw(tag, 'med', 9)
    assert xx <= x + BCW + 1, (body, xx - x - BCW)

# ------------------------------------------------------------------ date check and footer
rect(14, 940, W - 14, 994, fill=(253, 240, 238), outline=RED, width=1.5)
text(22, 944.5, 'DATE CHECK', 'heavy', 12, RED)
text(100, 945.5, 'Every story happened, or was first reported, on Monday 23 Nov 2026 (UTC or local time). Final edition: '
     'results read to the end of the day, so outcomes are shown, not previews.', 'med', 10.5, INK)
text(22, 959, 'LEFT OUT AS EARLIER NEWS:', 'heavy', 10, RED)
para(150, 959.5, "The Merkury sinking itself (Sun 22; only Ukraine's Monday claim is shown) · COP31 collapse (Sun 22) · "
     "Alcaraz and Márquez titles (Sun 22) · Russian strikes on Kyiv region (Sun 22) · Amtrak derailment, Louisiana "
     "(Sun 22) · California concert shooting (Sat 21) · Indonesia candy-factory fire (Sat 21) · Estonia border "
     "closure announced (Fri 20)", 'med', 10, W - 14 - 156, 12, INK, 2)
x = 14
y = 998
for reg, c in REGIONS.items():
    if not counts[reg]:
        continue
    ell(x + 4, y + 5, 4, 4, fill=c)
    lab = '%s %d' % (reg, counts[reg])
    text(x + 11, y, lab, 'bold', 9.5, INK)
    x += 11 + tw(lab, 'bold', 9.5) + 7
x += 3
for lab, desc in [('CONFIRMED', '2+ outlets'), ('OFFICIAL', 'on record'), ('REPORTED', 'one outlet'),
                  ('CLAIM', 'one side')]:
    x += chip(x, y - 1, lab, STATUS[lab]) + 3
    text(x, y, desc, 'reg', 9, INK)
    x += tw(desc, 'reg', 9) + 7
assert x < W - 10, x
text(14, 1011, 'Sources: Al Jazeera, The Guardian, Reuters, AFP, BBC, CBS, Colombia Reports, Xinhua, allAfrica and others named '
     'on each story (full list in FACTS.md). Pictures and map: original, drawn in code.', 'reg', 8.5, GREY)

out = img.resize((W, H), Image.LANCZOS)
out = out.quantize(colors=240, method=Image.MEDIANCUT, dither=Image.NONE)
out.save('entry.png', optimize=True)
print('wrote entry.png', STORIES, 'stories', counts)
