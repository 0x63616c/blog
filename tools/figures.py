"""Builds every SVG on the blog from real data files in ../data.
Nothing here is typed in by hand except labels. Toy diagrams say they are toys."""
import json, math, collections, html
ROOT = __file__.rsplit('/tools/', 1)[0]
B = json.load(open(f'{ROOT}/data/baseline-2026-10-26-d81e670.json'))['runs']
Q = json.load(open(f'{ROOT}/data/quads.json'))
PAL = {s['index']: s['rgba'] for s in json.load(open(f'{ROOT}/data/palette.json'))['slots']}

INK, INK2, INK3 = '#F1ECE2', '#B9B3A6', '#9C968A'
ACC, AMBER, TEAL, RED, HAIR = '#F2A93B', '#7FB0BC', '#A3B06A', '#E0764C', 'rgba(241,236,226,0.22)'
FONT = "Epilogue, system-ui, sans-serif"
MONO = FONT

def esc(s): return html.escape(str(s))
def svg_open(w, h, title, desc):
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d" xmlns="http://www.w3.org/2000/svg" '
            f'font-family="{FONT}"><title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>')
def text(x, y, s, size=12, fill=INK2, anchor='start', mono=False, weight=400):
    fam = f' font-family="{MONO}"' if mono else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}"{fam}>{esc(s)}</text>'
def fmt(n):
    if n >= 100: return f'{n:,.0f}'
    if n >= 10: return f'{n:.1f}'
    return f'{n:.1f}'

# ---------- chart: triangles, naive vs drawn (baseline scenes, log axis) ----------
def tri_chart():
    scenes = [('autumn', 'Autumn cottage'), ('terrain1m', 'Terrain 1M'), ('sponge1m', 'Sponge 1M'), ('terrain10m', 'Terrain 10M')]
    vox = {'autumn': 27897, 'terrain1m': 1040000, 'sponge1m': 1040000, 'terrain10m': 10000000}
    W, H, L, R, T = 720, 330, 130, 130, 40
    lo, hi = 4.0, 8.1  # log10 axis
    def X(v): return L + (math.log10(v) - lo) / (hi - lo) * (W - L - R)
    s = [svg_open(W, H, 'Triangles: one cube per voxel versus what Quantum draws',
                  'Log-scale bars for four scenes. Cube per voxel is twelve triangles per voxel; the drawn count is from the baseline run.')]
    for e in range(5, 9):
        x = X(10 ** e)
        s.append(f'<line x1="{x}" x2="{x}" y1="{T-8}" y2="{H-30}" stroke="{HAIR}" stroke-width="1"/>')
        s.append(text(x, H - 12, f'{10**e:,}', 11, INK3, 'middle', True))
    y = T
    for key, name in scenes:
        naive = vox[key] * 12
        drawn = B[f'm5pro/{key}/same_fit']['triangles']
        s.append(text(L - 12, y + 18, name, 13, INK, 'end'))
        s.append(f'<rect x="{L}" y="{y}" width="{X(naive)-L}" height="16" fill="{INK3}"/>')
        s.append(text(X(naive) + 8, y + 12, f'{naive:,} cubes', 11, INK2, 'start', True))
        s.append(f'<rect x="{L}" y="{y+20}" width="{X(drawn)-L}" height="16" fill="{ACC}"/>')
        s.append(text(X(drawn) + 8, y + 32, f'{drawn:,} drawn  ({naive/drawn:.0f}x fewer)', 11, INK, 'start', True))
        y += 68
    s.append(text(L, 22, 'triangles per frame, log scale', 12, INK3))
    s.append('</svg>')
    return ''.join(s)

# ---------- chart: the ladder on the cottage (culling, greedy) ----------
def ladder_chart():
    rows = [('cube per voxel', 333804, INK3), ('internal faces culled', 42564, AMBER),
            ('greedy merged (CPU mesher)', 19634, TEAL), ('what the GPU path draws', 34402, ACC)]
    W, H, L, R, T = 720, 230, 210, 110, 16
    mx = 333804
    s = [svg_open(W, H, 'Triangles for the cottage after each trick',
                  'Bars: 333,804 triangles as cubes, 42,564 after culling hidden faces, 19,634 after greedy merging, 34,402 drawn by the GPU path.')]
    y = T
    for name, v, col in rows:
        w = (W - L - R) * v / mx
        s.append(text(L - 12, y + 17, name, 13, INK, 'end'))
        s.append(f'<rect x="{L}" y="{y}" width="{max(w,2)}" height="24" fill="{col}"/>')
        s.append(text(L + max(w, 2) + 8, y + 17, f'{v:,}', 12, INK, 'start', True))
        y += 40
    s.append(text(L, H - 12, 'bars are linear. GPU row is a different mesher, see the text', 11, INK3))
    s.append('</svg>')
    return ''.join(s)

# ---------- diagram: culling on a 3x3 block (2D cross-section toy) ----------
def cull_diagram():
    W, H, c = 720, 230, 52
    s = [svg_open(W, H, 'Hidden faces on a block of voxels',
                  'A three by three cross section. Left shows every face of every cube. Right keeps only the faces on the outside.')]
    def block(ox, oy, outer_only):
        out = []
        for i in range(3):
            for j in range(3):
                x, y = ox + i * c, oy + j * c
                out.append(f'<rect x="{x}" y="{y}" width="{c}" height="{c}" fill="#000" stroke="rgba(241,236,226,0.22)" />')
        for i in range(4):  # vertical lines
            for j in range(3):
                inner = 0 < i < 3
                if outer_only and inner: continue
                col = RED if inner else ACC
                out.append(f'<line x1="{ox+i*c}" x2="{ox+i*c}" y1="{oy+j*c+3}" y2="{oy+(j+1)*c-3}" stroke="{col}" stroke-width="3" stroke-linecap="round"/>')
        for j in range(4):
            for i in range(3):
                inner = 0 < j < 3
                if outer_only and inner: continue
                col = RED if inner else ACC
                out.append(f'<line x1="{ox+i*c+3}" x2="{ox+(i+1)*c-3}" y1="{oy+j*c}" y2="{oy+j*c}" stroke="{col}" stroke-width="3" stroke-linecap="round"/>')
        return ''.join(out)
    s.append(block(70, 36, False)); s.append(block(430, 36, True))
    s.append(text(70 + 1.5 * c, 218, 'every face of every cube', 12, INK2, 'middle'))
    s.append(text(430 + 1.5 * c, 218, 'only faces that touch air', 12, INK2, 'middle'))
    s.append(text(70 + 1.5 * c, 22, '36 edges in 2D', 12, INK3, 'middle', True))
    s.append(text(430 + 1.5 * c, 22, '12 edges in 2D', 12, INK3, 'middle', True))
    s.append(text(360, 120, '→', 28, INK3, 'middle'))
    s.append('</svg>')
    return ''.join(s)

# ---------- diagram: greedy slice, from the real quads of the cottage ----------
def greedy_diagram():
    # top-facing quads (axis 1, positive) in slice y=8 (the ground layer); horizontal = z (u), vertical = x (v)
    sl = [q for q in Q if q[6] == 1 and q[7] == 1 and q[1] == 8]
    units = {}
    for x, y, z, w, h, slot, axis, pos in sl:
        for du in range(w):
            for dv in range(h):
                units[(z + du, x + dv)] = slot
    z0 = min(k[0] for k in units); z1 = max(k[0] for k in units) + 1
    x0 = min(k[1] for k in units); x1 = max(k[1] for k in units) + 1
    nz, nx = z1 - z0, x1 - x0
    cs = 4.2
    gap = 50
    W = 720
    ox1 = (W - 2 * nz * cs - gap) / 2; ox2 = ox1 + nz * cs + gap; oy = 36
    H = int(nx * cs + 76)
    nu, nq = len(units), len(sl)
    s = [svg_open(W, H, 'Greedy merging on a real layer of the cottage',
                  f'Top faces of the ground layer of the cottage, {nu} unit faces on the left, {nq} merged rectangles on the right.')]
    def col(slot):
        r, g, b, _ = PAL.get(slot, (128, 128, 128, 255)); return f'rgb({r},{g},{b})'
    for (z, x), slot in units.items():
        s.append(f'<rect x="{ox1+(z-z0)*cs:.1f}" y="{oy+(x-x0)*cs:.1f}" width="{cs}" height="{cs}" fill="{col(slot)}" stroke="rgba(0,0,0,.5)" stroke-width=".5"/>')
    for x, y, z, w, h, slot, axis, pos in sl:
        s.append(f'<rect x="{ox2+(z-z0)*cs:.1f}" y="{oy+(x-x0)*cs:.1f}" width="{w*cs:.1f}" height="{h*cs:.1f}" fill="{col(slot)}" stroke="#000" stroke-width=".8"/>')
    s.append(text(ox1, 22, f'{nu:,} unit faces', 12, INK2, 'start', True))
    s.append(text(ox2, 22, f'{nq:,} quads', 12, INK, 'start', True))
    s.append(text(ox1, H - 14, 'real top faces of the ground layer in the example file, colours from its palette', 11, INK3))
    s.append('</svg>')
    return ''.join(s), nu, nq

# ---------- diagram: chunk dirtying (toy) ----------
def chunk_diagram():
    cols, rows, cs = 8, 4, 70
    W, H = 720, rows * cs + 80
    ox, oy = 80, 36
    s = [svg_open(W, H, 'An edit only rebuilds nearby chunks',
                  'A grid of chunks in 2D. A voxel edit in the middle of a chunk dirties one chunk. An edit near a corner dirties four.')]
    def edit_dirty(px, py):
        lo = ((px - 2) // 16, (py - 2) // 16); hi = ((px + 2) // 16, (py + 2) // 16)
        return {(i, j) for i in range(lo[0], hi[0] + 1) for j in range(lo[1], hi[1] + 1)}
    edits = [(40, 40), (79, 31)]  # voxel coords in 16-cell chunks; second is near a chunk corner
    edits = [(40, 40), (79, 47)]
    dirty = set()
    for e in edits: dirty |= edit_dirty(*e)
    for i in range(cols):
        for j in range(rows):
            d = (i, j) in dirty
            s.append(f'<rect x="{ox+i*cs}" y="{oy+j*cs}" width="{cs}" height="{cs}" fill="{"rgba(242,169,59,.28)" if d else "#000"}" stroke="{ACC if d else HAIR}" stroke-width="1"/>')
    for (px, py) in edits:
        x = ox + px / 16 * cs; y = oy + py / 16 * cs
        s.append(f'<rect x="{x-14*cs/16*0.0-(2*cs/16)}" y="{y-(2*cs/16)}" width="{4*cs/16}" height="{4*cs/16}" fill="none" stroke="{AMBER}" stroke-dasharray="3 2"/>')
        s.append(f'<circle cx="{x}" cy="{y}" r="3.5" fill="{AMBER}"/>')
    s.append(text(ox, 22, '16-cell chunks, toy 2D version', 12, INK3))
    s.append(text(ox, H - 14, f'{len(edit_dirty(*edits[0]))} chunk and {len(edit_dirty(*edits[1]))} chunks rebuilt for two one-voxel edits. Dashed box is the 2-cell halo.', 11, INK3))
    s.append('</svg>')
    return ''.join(s)

# ---------- diagram: shadow ray with brick skipping (toy 2D, counts are computed) ----------
def trace_diagram():
    G, BR, cs = (32, 12), 4, 20  # cells, brick size (8 in the real thing; 4 to fit a page)
    occ = set()
    for x in range(9, 14):
        for y in range(4, 8): occ.add((x, y))
    for x in range(20, 24):
        for y in range(0, 3): occ.add((x, y))
    occ.add((26, 9))
    bricks = {(x // BR, y // BR) for x, y in occ}
    origin = (3.5, 1.5)  # start in the cell, in cell units
    d = (1.0, 0.42)
    def cross(o, dr, cell):
        if dr == 0: return 1e30
        b = cell + (1 if dr > 0 else 0)
        return (b - o) / dr
    def walk(skip):
        cell = [int(origin[0]), int(origin[1])]; steps = []; hit = None
        for _ in range(768):
            if not (0 <= cell[0] < G[0] and 0 <= cell[1] < G[1]): break
            br = (cell[0] // BR, cell[1] // BR)
            steps.append(tuple(cell))
            if skip and br not in bricks:
                lo = (br[0] * BR, br[1] * BR); hi = (lo[0] + BR - 1, lo[1] + BR - 1)
                ex = cross(origin[0], d[0], hi[0]); ey = cross(origin[1], d[1], hi[1])
                t = min(ex, ey) + 1e-9
                nx = origin[0] + d[0] * t; ny = origin[1] + d[1] * t
                cell = [int(math.floor(nx)), int(math.floor(ny))]
                continue
            if tuple(cell) in occ: hit = tuple(cell); break
            tx = cross(origin[0], d[0], cell[0]); ty = cross(origin[1], d[1], cell[1])
            if tx <= ty: cell[0] += 1
            else: cell[1] += 1
        return steps, hit
    naive, hit1 = walk(False)
    fast, hit2 = walk(True)
    assert hit1 == hit2, (hit1, hit2)
    W, H = 720, G[1] * cs + 90
    ox, oy = 40, 40
    s = [svg_open(W, H, 'A shadow ray with and without brick skipping',
                  f'Toy 2D grid. The same ray hits the same cell. Walking cell by cell takes {len(naive)} steps, skipping empty bricks takes {len(fast)}.')]
    # y up: flip
    def P(x, y): return ox + x * cs, oy + (G[1] - 1 - y) * cs
    for bx in range(G[0] // BR):
        for by in range(G[1] // BR):
            x, y = P(bx * BR, by * BR + BR - 1)
            full = (bx, by) in bricks
            s.append(f'<rect x="{x}" y="{y}" width="{BR*cs}" height="{BR*cs}" fill="{"rgba(241,236,226,.08)" if full else "none"}" stroke="{HAIR}" stroke-width="1"/>')
    for (x, y) in occ:
        px, py = P(x, y)
        s.append(f'<rect x="{px+1}" y="{py+1}" width="{cs-2}" height="{cs-2}" fill="{INK3}"/>')
    for (x, y) in naive:
        px, py = P(x, y)
        s.append(f'<circle cx="{px+cs/2}" cy="{py+cs/2}" r="2.2" fill="{AMBER}" opacity=".8"/>')
    pts = [P(x, y) for x, y in fast]
    s.append(f'<polyline points="{" ".join(f"{a+cs/2:.0f},{b+cs/2:.0f}" for a,b in pts)}" fill="none" stroke="{ACC}" stroke-width="2"/>')
    for a, b in pts:
        s.append(f'<circle cx="{a+cs/2}" cy="{b+cs/2}" r="3.6" fill="{ACC}"/>')
    hx, hy = P(*hit1)
    s.append(f'<rect x="{hx+1}" y="{hy+1}" width="{cs-2}" height="{cs-2}" fill="{RED}"/>')
    ox0, oy0 = P(int(origin[0]), int(origin[1]))
    s.append(text(ox, 22, 'toy 2D grid, bricks 4x4 (the real ones are 8x8x8)', 12, INK3))
    s.append(text(ox, H - 38, f'slate dots: step cell by cell, {len(naive)} steps', 12, AMBER, 'start', True))
    s.append(text(ox, H - 18, f'amber dots: jump over empty bricks, {len(fast)} steps. Same hit.', 12, ACC, 'start', True))
    s.append('</svg>')
    return ''.join(s), len(naive), len(fast)

# ---------- chart: ablation, M2 GPU ms (from raw jsonl) ----------
def ablation_chart():
    import sys; sys.path.insert(0, f'{ROOT}/data/raw')
    import analyze as a
    def g(f, ph):
        rs = [r for r in a.rows(f'{ROOT}/data/raw/{f}.jsonl') if r['phase'] == ph]
        return a.summ(rs, 'gpu_total_ms')['p50']
    groups = [('Autumn, fit', 'autumn', 'same_fit'), ('Autumn, close', 'autumn', 'orbit_close'),
              ('Terrain 1M, fit', 'terrain1m', 'same_fit'), ('Terrain 1M, close', 'terrain1m', 'orbit_close')]
    series = [('base', 'everything on', INK3), ('ss1', '1x supersample', AMBER), ('noshadow', 'shadows off', ACC)]
    W, H, L, R, T, Bt = 720, 340, 56, 20, 40, 60
    mx = 80
    s = [svg_open(W, H, 'Where the GPU time goes on the M2',
                  'Grouped bars of GPU milliseconds per frame for four scene and camera combinations, with everything on, one-times supersample, and shadows off.')]
    ph = H - Bt - T
    for v in (0, 20, 40, 60, 80):
        y = T + ph - v / mx * ph
        s.append(f'<line x1="{L}" x2="{W-R}" y1="{y}" y2="{y}" stroke="{HAIR}"/>')
        s.append(text(L - 8, y + 4, v, 11, INK3, 'end', True))
    gw = (W - L - R) / len(groups)
    out = {}
    for gi, (name, scene, phase) in enumerate(groups):
        for si, (k, label, col) in enumerate(series):
            v = g(f'{scene}_{k}', phase); out[(name, k)] = v
            bw = 30; x = L + gi * gw + (gw - 3 * bw - 8) / 2 + si * (bw + 4)
            h = v / mx * ph
            s.append(f'<rect x="{x}" y="{T+ph-h}" width="{bw}" height="{h}" fill="{col}"/>')
            s.append(text(x + bw / 2, T + ph - h - 6, f'{v:.1f}', 11, INK, 'middle', True))
        s.append(text(L + gi * gw + gw / 2, H - Bt + 22, name, 12, INK2, 'middle'))
    lx = L
    for k, label, col in series:
        s.append(f'<rect x="{lx}" y="{H-18}" width="10" height="10" fill="{col}"/>')
        s.append(text(lx + 16, H - 9, label, 11, INK2)); lx += 150
    s.append(text(L, 22, 'GPU ms per frame, Mac mini M2, lower is better', 12, INK3))
    s.append('</svg>')
    return ''.join(s), out

# ---------- chart: M5 Pro frame times vs 120 Hz ----------
def frame_chart():
    groups = [('Autumn', 'autumn'), ('Terrain 1M', 'terrain1m'), ('Terrain 10M', 'terrain10m')]
    W, H, L, R, T, Bt = 720, 320, 56, 84, 40, 50
    mx = 40
    s = [svg_open(W, H, 'Frame time on the M5 Pro',
                  'Bars of wall milliseconds per frame at fit and close camera for three scenes with a line at 8.3 milliseconds for 120 hertz.')]
    ph = H - Bt - T
    for v in (0, 10, 20, 30, 40):
        y = T + ph - v / mx * ph
        s.append(f'<line x1="{L}" x2="{W-R}" y1="{y}" y2="{y}" stroke="{HAIR}"/>')
        s.append(text(L - 8, y + 4, v, 11, INK3, 'end', True))
    gw = (W - L - R) / len(groups)
    for gi, (name, key) in enumerate(groups):
        for si, (phase, col, lab) in enumerate([('same_fit', ACC, 'fit'), ('orbit_close', AMBER, 'close')]):
            v = B[f'm5pro/{key}/{phase}']['wall_ms']['p50']
            bw = 44; x = L + gi * gw + (gw - 2 * bw - 6) / 2 + si * (bw + 6)
            h = v / mx * ph
            s.append(f'<rect x="{x}" y="{T+ph-h}" width="{bw}" height="{h}" fill="{col}"/>')
            s.append(text(x + bw / 2, T + ph - h - 6, f'{v:.1f}', 11, INK, 'middle', True))
        s.append(text(L + gi * gw + gw / 2, H - Bt + 22, name, 12, INK2, 'middle'))
    y = T + ph - 8.33 / mx * ph
    s.append(f'<line x1="{L}" x2="{W-R}" y1="{y}" y2="{y}" stroke="{RED}" stroke-dasharray="5 4"/>')
    s.append(text(W - R + 8, y - 2, '120 Hz', 11, RED, 'start', True)); s.append(text(W - R + 8, y + 12, '8.3 ms', 11, RED, 'start', True))
    s.append(f'<rect x="{L}" y="{H-18}" width="10" height="10" fill="{ACC}"/>' + text(L + 16, H - 9, 'fit camera', 11, INK2))
    s.append(f'<rect x="{L+110}" y="{H-18}" width="10" height="10" fill="{AMBER}"/>' + text(L + 126, H - 9, 'close camera', 11, INK2))
    s.append(text(L, 22, 'wall ms per frame, M5 Pro, one run, median', 12, INK3))
    s.append('</svg>')
    return ''.join(s)

# ---------- chart: edits (log axis, M5 Pro) ----------
def edit_chart():
    rows = [('Autumn', 'autumn', 27897), ('Terrain 1M', 'terrain1m', 1040000), ('Terrain 10M', 'terrain10m', 10000000)]
    W, H, L, R, T = 720, 330, 130, 90, 40
    lo, hi = 0.0, 4.0
    def X(v): return L + (math.log10(v) - lo) / (hi - lo) * (W - L - R)
    s = [svg_open(W, H, 'Cost of a one-voxel edit versus a palette change',
                  'Log-scale bars, milliseconds from edit to next presented frame, render side only, on the M5 Pro.')]
    for e in range(0, 5):
        x = X(10 ** e)
        s.append(f'<line x1="{x}" x2="{x}" y1="{T-8}" y2="{H-34}" stroke="{HAIR}"/>')
        s.append(text(x, H - 16, f'{10**e:,} ms', 11, INK3, 'middle', True))
    y = T
    for name, key, _ in rows:
        one = B[f'm5pro/{key}/edit_1voxel']['wall_ms']['p50']
        rec = B[f'm5pro/{key}/edit_recolor']['wall_ms']['p50']
        s.append(text(L - 12, y + 18, name, 13, INK, 'end'))
        s.append(f'<rect x="{L}" y="{y}" width="{X(one)-L}" height="16" fill="{ACC}"/>')
        s.append(text(X(one) + 8, y + 12, f'{fmt(one)} ms, one voxel', 11, INK, 'start', True))
        s.append(f'<rect x="{L}" y="{y+20}" width="{X(rec)-L}" height="16" fill="{AMBER}"/>')
        s.append(text(X(rec) + 8, y + 32, f'{fmt(rec)} ms, recolour', 11, INK, 'start', True))
        y += 78
    s.append(text(L, 22, 'edit to next presented frame, render side only, log scale', 12, INK3))
    s.append('</svg>')
    return ''.join(s)

if __name__ == '__main__':
    g, nu, nq = greedy_diagram(); print('greedy window', nu, nq)
    t, n1, n2 = trace_diagram(); print('trace steps', n1, n2)
    a, out = ablation_chart(); print(out)
