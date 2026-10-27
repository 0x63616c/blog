import re, html, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import figures as F
ROOT = F.ROOT

def hl(code):
    e = html.escape(code)
    e = re.sub(r'(//[^\n]*)', r'<span class="c">\1</span>', e)
    e = re.sub(r'\b(let|fn|for|in|if|else|while|continue|return|var|const|true|false)\b(?![^<]*</span>)', r'<span class="k">\1</span>', e)
    return e
def code(src, cap=None):
    c = f'<span class="cap">{html.escape(cap)}</span>' if cap else ''
    return f'<pre>{c}<code>{hl(src.strip(chr(10)))}</code></pre>'
def fig(inner, cap=None):
    c = f'<figcaption>{cap}</figcaption>' if cap else ''
    return f'<figure><div class="tile">{inner}</div>{c}</figure>'
def img(src, alt, cap):
    return f'<figure><div class="tile"><img src="{src}" alt="{html.escape(alt)}" loading="lazy"></div><figcaption>{cap}</figcaption></figure>'

HEAD = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#000000">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:type" content="article">
<link rel="stylesheet" href="{base}assets/style.css">
</head><body>
<header class="site"><div class="wrap"><a class="brand" href="{base}">blog <span>/ calum</span></a><nav><a href="{base}">posts</a></nav></div></header>
<main><div class="wrap">
'''
FOOT = '''</div></main>
<footer class="site"><div class="wrap">Plain HTML, black theme borrowed from the rest of my sites. No tracking, no cookies.</div></footer>
</body></html>
'''

greedy_svg, g_units, g_quads = F.greedy_diagram()
trace_svg, t_naive, t_fast = F.trace_diagram()
abl_svg, A = F.ablation_chart()

post = HEAD.format(title='How Voxelite draws a cottage without drawing 333,804 triangles',
                   desc='Culling, greedy meshing, chunks, exact voxel shadows and a bench that keeps me honest, with the real numbers from my renderer.',
                   base='../../')
post += '''<article>
<h1>How Voxelite draws a cottage without drawing 333,804 triangles</h1>
<div class="meta">Oct 26, 2026 &middot; renderer notes</div>
<p class="lede">Voxelite is the voxel editor I'm building. The name might change, it has already been three different things this month. The part I keep poking at is the renderer, because an editor with a stuttering viewport is just a sad spreadsheet.</p>
<p>My test scene is a small autumn cottage with a tree, a fence and a chimney I'm unreasonably proud of. The example file in the repo has 27,817 voxels.</p>
''' + img('../../img/wide_full.png', 'Isometric render of a voxel cottage with an orange autumn tree',
          'A render from the CPU rasteriser in the repo, because the box I wrote this on has no GPU. It is slow but deterministic, which matters at the end. The real viewport is wgpu on Metal.') + '''
<p>This is not a tutorial. There are plenty of those and they hold your hand better than I do. It's the handful of things that moved the needle, in the order I hit them, with real numbers where I have them and a plain note where I don't.</p>

<h2>The version everyone writes first</h2>
<p>One cube per voxel. Eight corners, twelve triangles, done.</p>
''' + code('''
for voxel in scene.voxels() {
    // 12 triangles, whether or not anyone can see them
    push_cube(&mut mesh, voxel.pos, voxel.color);
}''', 'not from the repo, this is the one everyone writes on day one') + '''
<p>For the cottage that's 27,817 &times; 12 = 333,804 triangles, most of them inside walls or under grass. A modern GPU would probably shrug at that and I never timed it, so I won't pretend I did. The trouble is the other scenes I test with. A million voxels is 12.5 million triangles. Ten million voxels is 120 million triangles of dirt, and I'd like to still see 120 frames a second.</p>

<h2>Don't draw faces nobody can see</h2>
<p>Put two cubes next to each other and the faces that touch are inside solid matter. Nobody will ever look at them. In a 3&times;3&times;3 block that's 162 faces, and only the 54 on the outside can ever show up on screen.</p>
''' + fig(F.cull_diagram(), 'Red edges touch another voxel, blue edges touch air. A 2D cross section keeps the picture readable.') + '''
<p>The check is one hash lookup per face. If there's a voxel on the other side, skip it.</p>
''' + code('''
let Some(&slot) = cells.get(&p) else { continue };
let mut neighbor = p;
neighbor[axis] += if positive { 1 } else { -1 };
if cells.contains_key(&neighbor) {
    continue; // solid on the other side, nobody will ever see this face
}''', 'crates/voxelite-render/src/chunk_mesh.rs, trimmed') + '''
<p>On the cottage that takes 333,804 triangles down to 42,564, which is 21,282 exposed faces. About 87 percent of the model was never going to be seen.</p>

<h2>Then merge what's left</h2>
<p>Look at a flat stretch of grass. Hundreds of identical little squares, all facing up, all the same colour. Greedy meshing walks each layer, finds a square, grows it as far right as it can, then as far down as it can, and emits one big rectangle instead.</p>
''' + fig(greedy_svg, f'The top faces of the ground layer of the cottage, straight out of the real mesher. {g_units} unit faces on the left, {g_quads} rectangles on the right.') + '''
<p>There's one catch. I bake ambient occlusion into the vertices, so two neighbouring faces with the same colour but different corner darkness can't share a quad or the shading smears across it. The merge only happens when all four corners agree.</p>
''' + code('''
let flat = face.ao.iter().all(|a| *a == face.ao[0]);
let mut w = 1;
let mut h = 1;
if flat {
    while x + w < 16 && mask[y * 16 + x + w] == face { w += 1; }
    while y + h < 16 && (0..w).all(|dx| mask[(y + h) * 16 + x + dx] == face) { h += 1; }
}''', 'same file, the grow step') + '''
''' + fig(F.ladder_chart(), 'Triangles for the cottage after each step. The first three rows are the plain CPU mesher run on the example file. The last row is the mesher the GPU actually uses, from the baseline run.') + '''
<p>So the GPU mesher is a worse greedy mesher than the plain one, on purpose. 17,201 quads (34,402 triangles) against 9,817 quads (19,634 triangles). I'm paying quads for nicer shading. One more oddity: the scene in my baseline run has 27,897 voxels and the file in the repo has 27,817. I don't know where 80 voxels went, I'm choosing to blame the fence.</p>

<h2>Chunks, so an edit is cheap</h2>
<p>The mesh isn't one giant blob. It's cut into 16&times;16&times;16 chunks, each with its own buffer and its own draw call (the cottage is 30 draw calls). Move the camera and nothing gets rebuilt. Change one voxel and only the chunk it lives in gets remeshed.</p>
<p>Almost only. Culling and AO both look at neighbours, so an edit near a chunk border changes the faces on the other side too. I reach two cells in every direction and rebuild whatever chunks that touches.</p>
''' + code('''
// Cull and AO dependencies extend two cells across chunk borders,
// including diagonals. Interior edits only invalidate one chunk.
let lo = p.map(|v| (v - 2).div_euclid(16));
let hi = p.map(|v| (v + 2).div_euclid(16));
for z in lo[2]..=hi[2] {
    for y in lo[1]..=hi[1] {
        for x in lo[0]..=hi[0] { dirty.insert([x, y, z]); }
    }
}''', 'same file, sync_validated') + fig(F.chunk_diagram(), 'Toy 2D version. The real one is 3D, so a corner edit can dirty eight chunks.') + '''
<p>Here's what that buys on the M5 Pro. A one-voxel edit on the 10 million voxel terrain shows up in 26.8 ms. Changing a palette colour takes 3,116 ms, because colours are baked into the vertices and a palette change remeshes everything. Yes, that's a bit embarrassing, and it's on the list (palette index in the vertex plus a palette buffer in the shader, so a recolour is a buffer write).</p>
''' + fig(F.edit_chart(), 'Baseline run, M5 Pro, median of 20 frames. Render side only.') + '''
<div class="note"><p>These numbers start when the renderer gets the edit. The document engine is separate and sits on top. A one-voxel edit costs about 2 ms of engine time on the cottage, 83 ms at 1M voxels and 0.84 s at 10M. So at 10M the renderer is the smaller problem, which is a funny thing to learn after doing the renderer work.</p></div>
<p>All three tricks together, against the cube-per-voxel triangle count for each baseline scene:</p>
''' + fig(F.tri_chart(), 'The cube-per-voxel count is voxels &times; 12, nothing measured. The drawn count is from the baseline run at the fit camera.') + '''

<h2>Shadows that are actually right</h2>
<p>Most real-time shadows use a shadow map: render the scene from the sun, then compare depths. It's fast and it's fuzzy, with bias to tune, resolution to tune, and the occasional floating-object look. I wanted voxel shadows to be exactly the voxel shape, so every pixel shoots a ray at the sun through the grid and asks whether it hits a voxel on the way out.</p>
<figure><div class="tile"><div class="pair">
<div><img src="../../img/close_ao.png" alt="Close up of the cottage roof with ambient occlusion and no shadows" loading="lazy"><div class="lab">AO, no shadows</div></div>
<div><img src="../../img/close_full.png" alt="Close up of the cottage roof with ambient occlusion and shadows" loading="lazy"><div class="lab">AO + traced shadows</div></div>
</div></div><figcaption>The CPU renderer again. The GPU does the same thing in the fragment shader.</figcaption></figure>
<p>That's a per-pixel loop, so it had better be smart about empty space. The occupancy grid is stored as 8&times;8&times;8 bricks: 512 bits is 16 words per brick, plus one more bitmask with a single bit per brick that says whether it has anything in it at all. An empty brick gets crossed in one jump.</p>
''' + code('''
let brick = b.x + occupancy.bricks.x * (b.y + occupancy.bricks.y * b.z);
let mask  = occupancy.bricks.w + brick / 32u;
if (occupancy.words[mask] & (1u << (brick % 32u))) == 0u {
    // empty brick: jump straight to where the ray leaves it
} else {
    if (occupancy.words[word] & (1u << (bit % 32u))) != 0u { return true; }
    // inside a busy brick: walk one cell along the closest axis
}''', 'gpu/viewport.wgsl, trace_shadow, trimmed (the full loop runs up to 768 times)') + '''
''' + fig(trace_svg, f'A toy ray on a toy grid. Stepping cell by cell takes {t_naive} steps and skipping empty bricks takes {t_fast}, and both land on the same red cell. The step counts are computed from this toy, not from the renderer.') + '''
<p>That works, and it's still the most expensive thing in the frame by a distance. I turned it off to see how much, one change at a time on the real shader, 60 frames per phase.</p>
''' + fig(abl_svg, 'Baseline run on the Mac mini M2. GPU time from timestamp queries, median of 60 frames.') + f'''
<div class="note"><p>Read this chart carefully, because it isn't a before and after. It's what shadows cost, which is the ceiling on what any shadow speed-up could ever win. At the fit camera on Autumn that's {A[('Autumn, fit','base')]:.1f} ms down to {A[('Autumn, fit','noshadow')]:.1f}. Zoomed in on the 1M terrain it's {A[('Terrain 1M, close','base')]:.1f} ms down to {A[('Terrain 1M, close','noshadow')]:.1f}. I haven't sped the trace up yet, so there is no real after number to show you.</p></div>
<p>The other ablations were more interesting than I expected. Removing the extra geometry attachment write changed nothing measurable (18.5 ms against 18.6 on Autumn at the fit camera). The sponge scene has 912,356 triangles and the terrain has 149,192, and the sponge renders three times faster close up. Triangle count isn't the problem. Pixels times ray length is. Rendering at 1x instead of 2x supersample also helps a lot (18.6 ms down to 8.2 on Autumn) but I'm not going to take it, because the whole rule here is that the picture doesn't get worse. It's a measurement, not a plan.</p>
''' + fig(F.frame_chart(), 'Baseline run, M5 Pro. The M5 Pro GPU timestamp came back zero, so these are wall times per frame, which equals GPU wait because the pipeline is GPU-bound.') + '''
<p>So on the M5 Pro the cottage holds 120 Hz at the fit camera (7.8 ms against an 8.3 budget) and doesn't once you zoom in. Ten million voxels doesn't hold it anywhere.</p>
<p>The plan for the trace is a second occupancy level, one bit per 32-cell super-brick, so rays cross big empty areas in a few steps. Plus clipping each ray to the occupied bounds and to the highest occupied cell along the sun direction. The image should come out identical. There's one trap: the loop stops at 768 steps, and a ray that used to run out of steps and give up (no shadow) could now finish its walk and find something. A few pixels could change. I want that to show up in a diff, not slip through.</p>
<div class="note"><p>That change hasn't landed. When it does, the numbers get added here with a proper after chart. If the result is boring I'll say so.</p></div>

<h2>The part that keeps me from lying</h2>
<p>I don't trust myself to eyeball a shadow change. So the plan is two small tools that share the same scenes and camera paths. One measures speed, the other measures whether the picture moved.</p>
<table>
<tr><th></th><th>bench</th><th>visual</th></tr>
<tr><td>What it does</td><td>Drives the real Metal renderer headless along scripted camera and edit paths at the baseline size</td><td>Same scenes and paths at a small size, compared against golden PNGs</td></tr>
<tr><td>Fails when</td><td>Median of 3 runs is worse than the baseline by more than 5 percent and more than 0.3 ms</td><td>Any pixel differs (exact mode, used for every optimisation)</td></tr>
<tr><td>Leaves behind</td><td>JSON per run and a before and after table</td><td>Actual, golden, a log-scaled diff heatmap and a side by side</td></tr>
</table>
<p>There's a looser tolerance mode for changes I actually want, like tweaking the look: at most 0.05 percent of pixels off by more than 6/255, and no blob of failing pixels bigger than 32 px. Goldens are pinned to one chip, the Mac mini, because shadow and AO output can differ in the last bits between GPUs, and every other machine gets a polite skip rather than a failure. Before goldens are trusted, every frame is rendered twice and has to match itself. Changing a golden on purpose takes a command that wants a reason and writes it to a changelog.</p>
<p>Here is roughly what the diff output looks like. This one is the cottage with shadows on against shadows off, from the CPU renderer. It isn't a regression, I just needed a real pair of images that differ.</p>
''' + img('../../img/diff_heatmap.png', 'Log-scaled difference heatmap, black where the images match', 'Black means identical. 25,140 of 655,360 pixels differ (3.84 percent), 22,382 of them by more than 6/255, biggest channel difference 55. The tolerance mode would reject this and exact mode would reject it harder, which is the point.') + '''
<div class="note"><p>Status: the bench and the visual tool are being written as I type this and aren't merged yet. Nothing is gated by them today, and the speed numbers above come from a one-off instrumented run, not from the finished tool.</p></div>
<p>That's where it is. The second brick level is next.</p>

<h2>Where the numbers come from</h2>
<p>All speed numbers come from a baseline run of the production Metal worker driven headless: 4128&times;3232 pixel target, 4x MSAA, 2x supersample, exact voxel shadows, commit d81e670, on 2026-10-26. The M2 mini was busy running CI during the runs (load average 11 to 66), so treat those timings as rough. The M5 Pro was in normal use and its numbers are from a single run. The raw per-frame data for the ablation and the triangle counts is in <code>data/</code> in this site's repo, along with the script that draws every chart on this page.</p>
</article>
''' + FOOT

os.makedirs(f'{ROOT}/posts/voxelite-renderer', exist_ok=True)
open(f'{ROOT}/posts/voxelite-renderer/index.html', 'w').write(post)

index = HEAD.format(title='Calum\'s blog', desc='Notes on things I build.', base='') + '''
<h1>Notes on things I build</h1>
<p class="lede">Mostly Voxelite for now, a voxel editor with a renderer I fuss over too much.</p>
<ul class="posts">
<li><a href="posts/voxelite-renderer/"><div class="tile">
<div class="t">How Voxelite draws a cottage without drawing 333,804 triangles</div>
<div class="d">Culling, greedy meshing, chunks, exact voxel shadows, and the bench that stops me lying to myself.</div>
<div class="m">Oct 26, 2026</div></div></a></li>
</ul>
''' + FOOT
open(f'{ROOT}/index.html', 'w').write(index)
print('built', len(post))
