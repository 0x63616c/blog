"""Writes assets/mesh-data.js and assets/chart-data.js from the real data files. Nothing here is typed in by hand."""
import json, base64, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f'{ROOT}/data/raw')

def b64(bs): return base64.b64encode(bytes(bs)).decode()

def mesh():
    cells = json.load(open(f'{ROOT}/data/cells.json'))
    quads = json.load(open(f'{ROOT}/data/quads.json'))
    pal = json.load(open(f'{ROOT}/data/palette.json'))['slots']
    vox = bytearray()
    for x, y, z, s in cells: vox += bytes([x + 64, y, z + 64, s])
    qb = bytearray()
    for ox, oy, oz, w, h, s, a, pos in quads:
        qb += bytes([ox + 64, oy, oz + 64, w, h, s, a | (pos << 2)])
    p = {s['index']: s['rgba'][:3] for s in pal}
    js = 'window.MESH=' + json.dumps({'vox': b64(vox), 'quads': b64(qb), 'pal': p, 'nvox': len(cells), 'nquads': len(quads)}, separators=(',', ':')) + ';\n'
    open(f'{ROOT}/assets/mesh-data.js', 'w').write(js)

def charts():
    B = json.load(open(f'{ROOT}/data/baseline-2026-10-26-d81e670.json'))['runs']
    import analyze as a
    scenes = [('autumn', 'Autumn Workshop', '27.9k voxels'), ('terrain1m', 'Terrain 1M', '1.04M voxels'),
              ('sponge1m', 'Sponge', '1.04M voxels'), ('terrain10m', 'Terrain 10M', '10M voxels')]
    out = {'scenes': [], 'abl': [], 'meta': 'baseline-2026-10-26-d81e670'}
    for key, name, vox in scenes:
        r5 = B[f'm5pro/{key}/same_fit']
        sc = {'key': key, 'name': name, 'vox': vox, 'tris': r5['triangles'], 'calls': r5['draw_calls'], 'runs': {}}
        for chip in ('m5pro', 'm2'):
            for cam, ph in (('fit', 'same_fit'), ('orbit', 'orbit_fit'), ('close', 'orbit_close')):
                r = B[f'{chip}/{key}/{ph}']
                sc['runs'][f'{chip}_{cam}'] = [r['wall_ms']['p50'], r['wall_ms']['p95'], r['gpu_total_ms_p50']]
        out['scenes'].append(sc)
    def g(f, ph):
        rs = [r for r in a.rows(f'{ROOT}/data/raw/{f}.jsonl') if r['phase'] == ph]
        return a.summ(rs, 'gpu_total_ms')['p50']
    for name, scene, phase in [('Autumn, fit', 'autumn', 'same_fit'), ('Autumn, close', 'autumn', 'orbit_close'),
                               ('Terrain 1M, fit', 'terrain1m', 'same_fit'), ('Terrain 1M, close', 'terrain1m', 'orbit_close')]:
        out['abl'].append({'name': name, 'base': g(f'{scene}_base', phase), 'ss1': g(f'{scene}_ss1', phase), 'noshadow': g(f'{scene}_noshadow', phase)})
    open(f'{ROOT}/assets/chart-data.js', 'w').write('window.CHART=' + json.dumps(out, separators=(',', ':')) + ';\n')
    return out

if __name__ == '__main__':
    mesh(); o = charts()
    print(json.dumps(o)[:1500])
