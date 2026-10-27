/* Interactive bits for the Quantum post. Every number comes from window.MESH and window.CHART,
   which tools/export_data.py writes from the real data files. Nothing is typed in here. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var fmt = function (n) { return Math.round(n).toLocaleString('en-US'); };
  var f1 = function (n) { return n.toFixed(1); };
  var NS = 'http://www.w3.org/2000/svg';
  var INK = '#F1ECE2', INK2 = '#B9B3A6', INK3 = '#9C968A', HAIR = 'rgba(241,236,226,0.22)';
  var ACC = '#F2A93B', AMBER = '#7FB0BC', TEAL = '#A3B06A', RED = '#E0764C';

  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
  function txt(x, y, s, o) {
    o = o || {};
    return '<text x="' + x + '" y="' + y + '" font-size="' + (o.size || 11) + '" fill="' + (o.fill || INK2) +
      '" text-anchor="' + (o.anchor || 'start') + '" font-family="Epilogue, system-ui, sans-serif"' +
      (o.w ? ' font-weight="' + o.w + '"' : '') + '>' + esc(s) + '</text>';
  }
  function seg(root, sel, cb) {
    var btns = $$(sel, root);
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        btns.forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
        cb(b.dataset.v);
      });
    });
  }
  function onResize(el, fn) {
    var w = 0;
    function go() { var nw = el.clientWidth; if (nw && nw !== w) { w = nw; fn(nw); } }
    if (window.ResizeObserver) new ResizeObserver(go).observe(el); else window.addEventListener('resize', go);
    go();
  }

  /* ---------------------------------------------------------------- meshing modes */
  function initMesh(root) {
    var M = window.MESH; if (!M) return;
    function b64(s) { var b = atob(s), u = new Uint8Array(b.length); for (var i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return u; }
    var V = b64(M.vox), Qd = b64(M.quads), n = V.length / 4, nq = Qd.length / 7;
    var gi = function (x, y, z) { return (x << 14) | (y << 7) | z; };
    var G = new Uint8Array(1 << 21), i;
    for (i = 0; i < n; i++) G[gi(V[4 * i], V[4 * i + 1], V[4 * i + 2])] = 1;
    // exposure bits: 1 +x, 2 +y, 4 +z, 8 -x, 16 -y, 32 -z. Same test the mesher uses: a face is kept if the neighbour is empty.
    var E = new Uint8Array(n), exposed = 0;
    for (i = 0; i < n; i++) {
      var x = V[4 * i], y = V[4 * i + 1], z = V[4 * i + 2], m = 0;
      if (!G[gi(x + 1, y, z)]) m |= 1; if (!G[gi(x, y + 1, z)]) m |= 2; if (!G[gi(x, y, z + 1)]) m |= 4;
      if (!G[gi(x - 1, y, z)]) m |= 8; if (!G[gi(x, y - 1, z)]) m |= 16; if (!G[gi(x, y, z - 1)]) m |= 32;
      E[i] = m; for (var b = 0; b < 6; b++) if (m & (1 << b)) exposed++;
    }
    // painter's order, far to near, for a camera sitting at +x +y +z
    var keys = new Int32Array(n), ord = [];
    for (i = 0; i < n; i++) { keys[i] = V[4 * i] + V[4 * i + 1] + V[4 * i + 2]; ord.push(i); }
    ord.sort(function (a, b) { return keys[a] - keys[b]; });
    var counts = [
      { name: 'Cube per voxel', faces: n * 6 },
      { name: 'Hidden faces culled', faces: exposed },
      { name: 'Greedy meshed', faces: nq }
    ];
    counts[0].tris = counts[0].faces * 2; counts[1].tris = counts[1].faces * 2; counts[2].tris = nq * 2;

    var cv = $('canvas', root), ctx = cv.getContext('2d');
    var S = { mode: 2, wire: false, view: 'whole' };
    var K = 0.8660254;
    // bounds of everything in projected space, for the fit
    var minx = 1e9, maxx = -1e9, miny = 1e9, maxy = -1e9;
    for (i = 0; i < n; i++) {
      var X = V[4 * i], Y = V[4 * i + 1], Z = V[4 * i + 2];
      var l = (X - Z - 1) * K, r = (X - Z + 1) * K, t = (X + Z) * 0.5 - Y - 1, bt = (X + Z + 2) * 0.5 - Y;
      if (l < minx) minx = l; if (r > maxx) maxx = r; if (t < miny) miny = t; if (bt > maxy) maxy = bt;
    }
    var VIEWS = {
      whole: { c: [(minx + maxx) / 2, (miny + maxy) / 2], z: 1 },
      house: { c: [-1, 42], z: 1.9 },
      roof: { c: [4, 37], z: 5 }
    };
    var pal = {}; Object.keys(M.pal).forEach(function (k) { pal[k] = M.pal[k]; });
    var SH = [0.8, 1, 0.62]; // +x, +y (top), +z

    function draw() {
      var W = cv.clientWidth, H = cv.clientHeight, dpr = window.devicePixelRatio || 1;
      if (!W) return;
      cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
      var bw = (maxx - minx) * 1.04, bh = (maxy - miny) * 1.04;
      var base = Math.min(W / bw, H / bh), vw = VIEWS[S.view], k = base * vw.z;
      var tx = W / 2 - vw.c[0] * k, ty = H / 2 - vw.c[1] * k;
      var dim = S.wire ? 0.42 : 1;
      var mode = S.mode;
      ctx.lineJoin = 'round'; ctx.lineWidth = Math.max(0.5, Math.min(1, k * 0.12));
      // face corner helper: axis a, origin, extents w,h along (a+1)%3 and (a+2)%3
      function face(a, o0, o1, o2, w, h) {
        var o = [o0, o1, o2], u = (a + 1) % 3, v = (a + 2) % 3, c = [0, 0, 0, 0];
        var P = [o.slice(), o.slice(), o.slice(), o.slice()];
        P[1][u] += w; P[2][u] += w; P[2][v] += h; P[3][v] += h;
        ctx.moveTo(tx + (P[0][0] - P[0][2]) * K * k, ty + ((P[0][0] + P[0][2]) * 0.5 - P[0][1]) * k);
        for (var q = 1; q < 4; q++) ctx.lineTo(tx + (P[q][0] - P[q][2]) * K * k, ty + ((P[q][0] + P[q][2]) * 0.5 - P[q][1]) * k);
        ctx.closePath();
      }
      var cache = {};
      function col(slot, a) {
        var key = slot * 3 + a;
        if (!cache[key]) { var c = pal[slot] || [200, 200, 200], s = SH[a] * dim; cache[key] = 'rgb(' + Math.round(c[0] * s) + ',' + Math.round(c[1] * s) + ',' + Math.round(c[2] * s) + ')'; }
        return cache[key];
      }
      var pad = 3 * k, j, x, y, z, sx, sy, mask, a;
      // fill. Same picture in every mode: draw the front faces back to front.
      for (j = 0; j < n; j++) {
        i = ord[j]; x = V[4 * i]; y = V[4 * i + 1]; z = V[4 * i + 2];
        sx = tx + (x - z) * K * k; sy = ty + ((x + z) * 0.5 - y) * k;
        if (sx < -pad || sx > W + pad || sy < -pad || sy > H + pad) continue;
        mask = mode === 0 ? 7 : E[i] & 7;
        for (a = 0; a < 3; a++) {
          if (!(mask & (1 << a))) continue;
          ctx.beginPath(); face(a, x + (a === 0 ? 1 : 0), y + (a === 1 ? 1 : 0), z + (a === 2 ? 1 : 0), 1, 1);
          ctx.fillStyle = ctx.strokeStyle = col(V[4 * i + 3], a); ctx.fill(); ctx.stroke();
        }
      }
      if (S.wire) {
        ctx.beginPath();
        if (mode === 2) {
          for (j = 0; j < nq; j++) {
            var q = j * 7, fl = Qd[q + 6];
            if (!(fl & 4)) continue;
            face(fl & 3, Qd[q], Qd[q + 1], Qd[q + 2], Qd[q + 3], Qd[q + 4]);
          }
        } else {
          for (j = 0; j < n; j++) {
            i = ord[j]; x = V[4 * i]; y = V[4 * i + 1]; z = V[4 * i + 2];
            sx = tx + (x - z) * K * k; sy = ty + ((x + z) * 0.5 - y) * k;
            if (sx < -pad || sx > W + pad || sy < -pad || sy > H + pad) continue;
            mask = mode === 0 ? 7 : E[i] & 7;
            for (a = 0; a < 3; a++) if (mask & (1 << a)) face(a, x + (a === 0 ? 1 : 0), y + (a === 1 ? 1 : 0), z + (a === 2 ? 1 : 0), 1, 1);
          }
        }
        ctx.strokeStyle = 'rgba(255,255,255,0.85)'; ctx.lineWidth = Math.max(0.5, Math.min(1.2, k * 0.14)); ctx.stroke();
      }
    }
    function stats() {
      $$('.card', root).forEach(function (el, idx) {
        $('.f', el).textContent = fmt(counts[idx].faces);
        $('.t', el).textContent = fmt(counts[idx].tris) + ' triangles';
        $('.x', el).textContent = idx === 0 ? 'baseline' : (counts[0].tris / counts[idx].tris).toFixed(1) + 'x fewer';
        el.setAttribute('aria-pressed', idx === S.mode ? 'true' : 'false');
        el.onclick = function () { S.mode = idx; stats(); draw(); };
      });
    }
    seg(root, '.v-btn', function (v) { S.view = v; draw(); });
    var wb = $('.wire', root);
    wb.addEventListener('click', function () { S.wire = !S.wire; wb.setAttribute('aria-pressed', S.wire ? 'true' : 'false'); draw(); });
    stats(); onResize(cv, draw);
    root.classList.add('ready');
  }

  /* ---------------------------------------------------------------- frame time explorer */
  function initFrames(root) {
    var C = window.CHART; if (!C) return;
    var sc = C.scenes;
    var SER = [
      { id: 'm5pro_fit', label: 'M5 Pro, fit', col: ACC, dash: '', on: true },
      { id: 'm5pro_orbit', label: 'M5 Pro, orbit', col: TEAL, dash: '', on: false },
      { id: 'm5pro_close', label: 'M5 Pro, close', col: AMBER, dash: '', on: true },
      { id: 'm2_fit', label: 'M2 mini, fit', col: ACC, dash: '5 4', on: true },
      { id: 'm2_orbit', label: 'M2 mini, orbit', col: TEAL, dash: '5 4', on: false },
      { id: 'm2_close', label: 'M2 mini, close', col: AMBER, dash: '5 4', on: true }
    ];
    var S = { sel: 0, log: false, p95: false };
    var chips = $('.chips', root), svgHost = $('.chart', root), rd = $('.readout', root), rng = $('input[type=range]', root);
    rng.max = sc.length - 1;
    SER.forEach(function (s) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'chip'; b.setAttribute('aria-pressed', s.on ? 'true' : 'false');
      b.innerHTML = '<svg width="26" height="10" viewBox="0 0 26 10" aria-hidden="true"><line x1="1" x2="25" y1="5" y2="5" stroke="' + s.col + '" stroke-width="2.5"' + (s.dash ? ' stroke-dasharray="5 4"' : '') + '/></svg>' + esc(s.label);
      b.addEventListener('click', function () { s.on = !s.on; b.setAttribute('aria-pressed', s.on ? 'true' : 'false'); draw(); });
      chips.appendChild(b);
    });
    var logb = $('.log', root), p95b = $('.p95', root);
    logb.addEventListener('click', function () { S.log = !S.log; logb.setAttribute('aria-pressed', S.log); draw(); });
    p95b.addEventListener('click', function () { S.p95 = !S.p95; p95b.setAttribute('aria-pressed', S.p95); draw(); });
    rng.addEventListener('input', function () { S.sel = +rng.value; draw(); });

    function draw() {
      var W = Math.max(svgHost.clientWidth, 280), H = W < 480 ? 300 : 340;
      var L = 40, R = 12, T = 14, B = 46, pw = W - L - R, ph = H - T - B;
      var act = SER.filter(function (s) { return s.on; });
      var mx = 0; act.forEach(function (s) { sc.forEach(function (c) { var v = c.runs[s.id][S.p95 ? 1 : 0]; if (v > mx) mx = v; }); });
      var ticks, ymin, ymax;
      if (S.log) { ymin = 4; ymax = 200; ticks = [5, 10, 20, 50, 100, 200]; }
      else { ymin = 0; ymax = Math.max(20, Math.ceil(mx / 20) * 20); ticks = []; for (var t = 0; t <= ymax; t += ymax > 100 ? 40 : 20) ticks.push(t); }
      var Y = function (v) {
        if (S.log) return T + ph - (Math.log(v) - Math.log(ymin)) / (Math.log(ymax) - Math.log(ymin)) * ph;
        return T + ph - (v - ymin) / (ymax - ymin) * ph;
      };
      var X = function (i) { return L + (i + 0.5) * pw / sc.length; };
      var s = ['<svg viewBox="0 0 ' + W + ' ' + H + '" width="' + W + '" height="' + H + '" role="img" aria-label="Frame time per scene, one line per chip and camera. Use the slider and chips below to explore.">'];
      ticks.forEach(function (v) { s.push('<line x1="' + L + '" x2="' + (W - R) + '" y1="' + Y(v) + '" y2="' + Y(v) + '" stroke="' + HAIR + '"/>' + txt(L - 6, Y(v) + 4, v, { anchor: 'end', fill: INK3, size: 10 })); });
      // selected scene band
      s.push('<rect x="' + (L + S.sel * pw / sc.length) + '" y="' + T + '" width="' + (pw / sc.length) + '" height="' + ph + '" fill="rgba(241,236,226,0.09)"/>');
      [[8.33, '120 Hz', RED], [16.67, '60 Hz', INK3]].forEach(function (r) {
        if (r[0] < ymin || r[0] > ymax) return;
        s.push('<line x1="' + L + '" x2="' + (W - R) + '" y1="' + Y(r[0]) + '" y2="' + Y(r[0]) + '" stroke="' + r[2] + '" stroke-dasharray="2 4"/>' + txt(W - R - 2, Y(r[0]) - 4, r[1], { anchor: 'end', fill: r[2], size: 10 }));
      });
      sc.forEach(function (c, i) {
        s.push(txt(X(i), H - 24, c.name.length > 11 && W < 480 ? c.name.replace('Autumn Workshop', 'Autumn') : c.name, { anchor: 'middle', fill: i === S.sel ? INK : INK2, size: 11 }));
        s.push(txt(X(i), H - 9, c.vox.replace(' voxels', ''), { anchor: 'middle', fill: INK3, size: 10 }));
      });
      act.forEach(function (ser) {
        var d = '';
        sc.forEach(function (c, i) { d += (i ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(c.runs[ser.id][0]).toFixed(1); });
        s.push('<path d="' + d + '" fill="none" stroke="' + ser.col + '" stroke-width="2" stroke-linejoin="round"' + (ser.dash ? ' stroke-dasharray="' + ser.dash + '"' : '') + '/>');
        sc.forEach(function (c, i) {
          var p50 = c.runs[ser.id][0], p95 = c.runs[ser.id][1], r = i === S.sel ? 5 : 3.2;
          if (S.p95) s.push('<line x1="' + X(i) + '" x2="' + X(i) + '" y1="' + Y(p50) + '" y2="' + Y(p95) + '" stroke="' + ser.col + '" stroke-opacity="0.7" stroke-width="1.5"/><line x1="' + (X(i) - 4) + '" x2="' + (X(i) + 4) + '" y1="' + Y(p95) + '" y2="' + Y(p95) + '" stroke="' + ser.col + '" stroke-opacity="0.7" stroke-width="1.5"/>');
          s.push(ser.dash ? '<rect x="' + (X(i) - r) + '" y="' + (Y(p50) - r) + '" width="' + 2 * r + '" height="' + 2 * r + '" fill="#000" stroke="' + ser.col + '" stroke-width="2"/>'
            : '<circle cx="' + X(i) + '" cy="' + Y(p50) + '" r="' + r + '" fill="' + ser.col + '"/>');
        });
      });
      s.push('<rect class="hit" x="' + L + '" y="0" width="' + pw + '" height="' + H + '" fill="transparent"/></svg>');
      svgHost.innerHTML = s.join('');
      var hit = $('.hit', svgHost);
      function pick(e) { var r = svgHost.getBoundingClientRect(), x = e.clientX - r.left - L, i = Math.max(0, Math.min(sc.length - 1, Math.floor(x / (pw / sc.length)))); if (i !== S.sel) { S.sel = i; rng.value = i; draw(); } }
      hit.addEventListener('pointerdown', pick);
      readout(act);
    }
    function readout(act) {
      var c = sc[S.sel], cube = c.vox.indexOf('k') > 0 ? parseFloat(c.vox) * 1e3 : parseFloat(c.vox) * 1e6;
      var h = '<div class="facts"><b>' + esc(c.name) + '</b> <span>' + esc(c.vox) + ', ' + fmt(c.tris) + ' triangles drawn, ' + fmt(c.calls) + ' draw calls. A cube per voxel would be about ' +
        (cube * 12 >= 1e6 ? (cube * 12 / 1e6).toFixed(1) + 'M' : (cube * 12 / 1e3).toFixed(0) + 'k') + ' triangles (voxels x 12, not measured).</span></div>';
      h += '<table><thead><tr><th>Run</th><th>median</th><th>p95</th><th>vs 120 Hz (8.3 ms)</th></tr></thead><tbody>';
      if (!act.length) h += '<tr><td colspan="4">Switch a line on.</td></tr>';
      act.forEach(function (s) {
        var r = c.runs[s.id], ok = r[0] <= 8.34;
        h += '<tr><td><i style="background:' + s.col + '"></i>' + esc(s.label) + '</td><td>' + f1(r[0]) + ' ms</td><td>' + f1(r[1]) + ' ms</td><td class="' + (ok ? 'ok' : 'no') + '">' + (ok ? 'holds it' : 'misses') + '</td></tr>';
      });
      rd.innerHTML = h + '</tbody></table>';
    }
    onResize(svgHost, draw);
    root.classList.add('ready');
  }

  /* ---------------------------------------------------------------- shadow cost, ablation chart */
  function initAblation(root) {
    var C = window.CHART; if (!C) return;
    var G = C.abl;
    var SER = [
      { k: 'base', label: 'Everything on', col: INK3, on: true },
      { k: 'ss1', label: '1x supersample', col: AMBER, on: true },
      { k: 'noshadow', label: 'Shadows off', col: ACC, on: true }
    ];
    var S = { sel: G.length - 1 };
    var chips = $('.chips', root), host = $('.chart', root), rd = $('.readout', root);
    SER.forEach(function (s) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'chip'; b.setAttribute('aria-pressed', 'true');
      b.innerHTML = '<i style="background:' + s.col + '"></i>' + esc(s.label);
      b.addEventListener('click', function () { s.on = !s.on; b.setAttribute('aria-pressed', s.on ? 'true' : 'false'); draw(); });
      chips.appendChild(b);
    });
    function draw() {
      var W = Math.max(host.clientWidth, 280), H = 300, L = 36, R = 8, T = 14, B = 48, pw = W - L - R, ph = H - T - B, mx = 80;
      var act = SER.filter(function (s) { return s.on; }), gw = pw / G.length;
      var s = ['<svg viewBox="0 0 ' + W + ' ' + H + '" width="' + W + '" height="' + H + '" role="img" aria-label="GPU milliseconds per frame on the M2 mini for four scene and camera combinations, with series you can switch on and off.">'];
      [0, 20, 40, 60, 80].forEach(function (v) { var y = T + ph - v / mx * ph; s.push('<line x1="' + L + '" x2="' + (W - R) + '" y1="' + y + '" y2="' + y + '" stroke="' + HAIR + '"/>' + txt(L - 6, y + 4, v, { anchor: 'end', fill: INK3, size: 10 })); });
      G.forEach(function (g, gi) {
        var gx = L + gi * gw;
        if (gi === S.sel) s.push('<rect x="' + gx + '" y="' + T + '" width="' + gw + '" height="' + ph + '" fill="rgba(241,236,226,0.09)"/>');
        var bw = Math.min(34, (gw - 10) / Math.max(act.length, 1) - 3), tot = act.length * (bw + 3) - 3;
        act.forEach(function (ser, si) {
          var v = g[ser.k], h = v / mx * ph, x = gx + (gw - tot) / 2 + si * (bw + 3);
          s.push('<rect x="' + x + '" y="' + (T + ph - h) + '" width="' + bw + '" height="' + h + '" rx="3" fill="' + ser.col + '"/>' + txt(x + bw / 2, T + ph - h - 5, f1(v), { anchor: 'middle', fill: INK, size: bw < 22 ? 9 : 10 }));
        });
        var parts = g.name.split(', ');
        s.push(txt(gx + gw / 2, H - 26, parts[0], { anchor: 'middle', fill: gi === S.sel ? INK : INK2, size: 11 }) + txt(gx + gw / 2, H - 12, parts[1], { anchor: 'middle', fill: INK3, size: 10 }));
        s.push('<rect class="hit" data-i="' + gi + '" x="' + gx + '" y="0" width="' + gw + '" height="' + H + '" fill="transparent"/>');
      });
      s.push('</svg>');
      host.innerHTML = s.join('');
      $$('.hit', host).forEach(function (el) { el.addEventListener('pointerdown', function () { S.sel = +el.dataset.i; draw(); }); });
      var g = G[S.sel], cost = g.base - g.noshadow;
      rd.innerHTML = '<b>' + esc(g.name) + ':</b> <span>everything on ' + f1(g.base) + ' ms, shadows off ' + f1(g.noshadow) + ' ms. Shadows cost ' + f1(cost) + ' ms of the frame, ' + Math.round(cost / g.base * 100) + '%. With 1x supersample instead: ' + f1(g.ss1) + ' ms.</span>';
    }
    onResize(host, draw);
    root.classList.add('ready');
  }

  /* ---------------------------------------------------------------- shadows on/off: slider and pixel diff */
  function initShadows(root) {
    var C = window.CHART;
    var SETS = {
      wide: { off: '../../img/wide_ao.png', on: '../../img/wide_full.png', alt: 'wide shot of the cottage', abl: 0 },
      close: { off: '../../img/close_ao.png', on: '../../img/close_full.png', alt: 'close up of the cottage roof', abl: 1 }
    };
    var S = { set: 'wide', view: 'slider', thr: 0 }, imgs = {}, diffs = {};
    var stage = $('.stage', root), top = $('.top', stage), bot = $('.bot', stage), cv = $('canvas', stage), rng = $('.pos', root),
      thr = $('.thr', root), thrWrap = $('.thr-wrap', root), rd = $('.readout', root), sliderWrap = $('.pos-wrap', root), bar = $('.bar', stage);
    function load(name) {
      if (imgs[name]) return imgs[name];
      var p = SETS[name];
      imgs[name] = Promise.all([p.off, p.on].map(function (u) { return new Promise(function (res, rej) { var im = new Image(); im.onload = function () { res(im); }; im.onerror = rej; im.src = u; }); }));
      return imgs[name];
    }
    function diffFor(name, pair) {
      if (diffs[name]) return diffs[name];
      var w = pair[0].naturalWidth, h = pair[0].naturalHeight, c = document.createElement('canvas'); c.width = w; c.height = h;
      var x = c.getContext('2d', { willReadFrequently: true }), a, b;
      x.drawImage(pair[0], 0, 0); a = x.getImageData(0, 0, w, h).data;
      x.drawImage(pair[1], 0, 0); b = x.getImageData(0, 0, w, h).data;
      var d = new Uint8Array(w * h), mx = 0;
      for (var i = 0, p = 0; p < d.length; p++, i += 4) {
        var m = Math.max(Math.abs(a[i] - b[i]), Math.abs(a[i + 1] - b[i + 1]), Math.abs(a[i + 2] - b[i + 2]));
        d[p] = m; if (m > mx) mx = m;
      }
      diffs[name] = { w: w, h: h, d: d, max: mx };
      return diffs[name];
    }
    function setPos() { var p = +rng.value; top.style.clipPath = 'inset(0 0 0 ' + p + '%)'; bar.style.left = p + '%'; }
    function render() {
      var name = S.set, p = SETS[name];
      load(name).then(function (pair) {
        top.src = p.on; bot.src = p.off; top.alt = 'Same ' + p.alt + ' with traced shadows'; bot.alt = 'Same ' + p.alt + ' with no shadows';
        var df = diffFor(name, pair);
        thr.max = df.max; if (+thr.value > df.max) thr.value = df.max; S.thr = +thr.value;
        var isDiff = S.view === 'diff';
        stage.classList.toggle('isdiff', isDiff); sliderWrap.hidden = isDiff; thrWrap.hidden = !isDiff;
        if (isDiff) {
          cv.width = df.w; cv.height = df.h;
          var x = cv.getContext('2d'), im = x.createImageData(df.w, df.h), cnt = 0, o = im.data;
          for (var i = 0; i < df.d.length; i++) {
            var v = df.d[i], q = i * 4;
            if (v > S.thr) {
              cnt++; var t = v / df.max, a = t < 0.5 ? t * 2 : (t - 0.5) * 2; // dark amber to amber to bone
              if (t < 0.5) { o[q] = 90 + 152 * a; o[q + 1] = 52 + 117 * a; o[q + 2] = 8 + 51 * a; }
              else { o[q] = 242 - 1 * a; o[q + 1] = 169 + 67 * a; o[q + 2] = 59 + 167 * a; }
              o[q + 3] = 255;
            } else { o[q] = 0; o[q + 1] = 0; o[q + 2] = 0; o[q + 3] = 255; }
          }
          x.putImageData(im, 0, 0);
          rd.innerHTML = '<b>' + fmt(cnt) + '</b> of ' + fmt(df.d.length) + ' pixels differ by more than ' + S.thr + '/255 (' + (cnt / df.d.length * 100).toFixed(2) + '%). Biggest single channel change: ' + df.max + '/255. Everything else is bit for bit the same.';
        } else rd.innerHTML = abl();
        setPos();
      });
    }
    function abl() {
      var g = C && C.abl[SETS[S.set].abl]; if (!g) return '';
      return 'What shadows cost on the GPU (M2 mini, Autumn scene, ' + esc(g.name.split(', ')[1]) + ' camera): <b>' + f1(g.base) + ' ms</b> with, <b>' + f1(g.noshadow) + ' ms</b> without. The pictures are CPU renders of the example file and the timings are from the GPU baseline, so they are neighbours and not the same experiment.';
    }
    seg(root, '.s-btn', function (v) { S.set = v; render(); });
    seg(root, '.m-btn', function (v) { S.view = v; render(); });
    rng.addEventListener('input', setPos);
    thr.addEventListener('input', function () { S.thr = +thr.value; render(); });
    function drag(e) { var r = stage.getBoundingClientRect(), p = Math.max(0, Math.min(100, (e.clientX - r.left) / r.width * 100)); rng.value = p; setPos(); }
    stage.addEventListener('pointerdown', function (e) { if (S.view !== 'slider') return; stage.setPointerCapture(e.pointerId); drag(e); stage.onpointermove = drag; });
    stage.addEventListener('pointerup', function () { stage.onpointermove = null; });
    render();
    root.classList.add('ready');
  }

  function boot() {
    var r;
    if ((r = $('#w-mesh'))) initMesh(r);
    if ((r = $('#w-frames'))) initFrames(r);
    if ((r = $('#w-abl'))) initAblation(r);
    if ((r = $('#w-shadow'))) initShadows(r);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
