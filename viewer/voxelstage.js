/*
 * VoxelStage — visor three.js (r149, build clásico) para los modelos de cubos
 * exportados por blender/build.py (exports/*.json).
 *
 * Incluye: instancing por material, animación muestreada desde Blender,
 * bloom HDR propio (sin addons), entorno PMREM para el oro, partículas,
 * haz de luz, brillo de suelo y una animación de "romper" para los huevos.
 *
 *   const stage = VoxelStage.create(canvas, data, options);
 *   stage.setPlaying(bool); stage.setSpin(bool); stage.setView('front'|'side'|'tq');
 *   stage.burst(); stage.dispose();
 */
(function () {
  'use strict';
  var T = window.THREE;

  // ------------------------------------------------------------------ utilidades
  function lerp(a, b, t) { return a + (b - a) * t; }
  function clamp01(x) { return Math.max(0, Math.min(1, x)); }
  function easeOut(t) { return 1 - Math.pow(1 - t, 3); }
  function easeInOut(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function rand(seed) { var x = Math.sin(seed * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }

  function canvasTexture(size, draw) {
    var c = document.createElement('canvas');
    c.width = c.height = size;
    draw(c.getContext('2d'), size);
    var t = new T.CanvasTexture(c);
    t.encoding = T.sRGBEncoding;
    return t;
  }

  function softDot() {
    return canvasTexture(64, function (g, s) {
      var r = g.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
      r.addColorStop(0, 'rgba(255,255,255,1)');
      r.addColorStop(0.25, 'rgba(255,255,255,0.8)');
      r.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = r;
      g.fillRect(0, 0, s, s);
    });
  }

  function sparkle() {
    return canvasTexture(64, function (g, s) {
      var c = s / 2;
      var r = g.createRadialGradient(c, c, 0, c, c, c * 0.5);
      r.addColorStop(0, 'rgba(255,255,255,1)');
      r.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = r;
      g.fillRect(0, 0, s, s);
      g.fillStyle = 'rgba(255,255,255,0.95)';
      g.beginPath();
      g.moveTo(c, 0); g.lineTo(c + 3, c - 3); g.lineTo(s, c); g.lineTo(c + 3, c + 3);
      g.lineTo(c, s); g.lineTo(c - 3, c + 3); g.lineTo(0, c); g.lineTo(c - 3, c - 3);
      g.closePath();
      g.fill();
    });
  }

  function studBump() {
    // relieve de un "stud" (botón tipo LEGO) para el bumpMap; se repite por cara según el tamaño de la pieza
    var t = canvasTexture(128, function (g, s) {
      g.fillStyle = 'rgb(118,118,118)';
      g.fillRect(0, 0, s, s);
      g.fillStyle = 'rgb(96,96,96)';
      g.fillRect(0, 0, s, 3); g.fillRect(0, 0, 3, s);
      var c = s / 2, r = s * 0.3;
      g.beginPath(); g.arc(c + 3, c + 4, r + 3, 0, Math.PI * 2); g.fillStyle = 'rgb(70,70,70)'; g.fill();
      var gr = g.createRadialGradient(c - r * 0.3, c - r * 0.3, r * 0.1, c, c, r);
      gr.addColorStop(0, 'rgb(250,250,250)'); gr.addColorStop(0.75, 'rgb(215,215,215)'); gr.addColorStop(1, 'rgb(180,180,180)');
      g.beginPath(); g.arc(c, c, r, 0, Math.PI * 2); g.fillStyle = gr; g.fill();
    });
    t.encoding = T.LinearEncoding;
    t.wrapS = t.wrapT = T.RepeatWrapping;
    t.anisotropy = 4;
    return t;
  }

  function addStuds(mat, tex, size, bump) {
    mat.bumpMap = tex;
    mat.bumpScale = bump;
    mat.onBeforeCompile = function (sh) {
      sh.uniforms.studSize = { value: size };
      sh.vertexShader = 'uniform float studSize;\n' + sh.vertexShader.replace('#include <uv_vertex>', [
        '#ifdef USE_UV',
        '  vec3 sc = vec3(length(instanceMatrix[0].xyz), length(instanceMatrix[1].xyz), length(instanceMatrix[2].xyz));',
        '  vec2 rep = abs(normal.x) > 0.5 ? sc.zy : (abs(normal.y) > 0.5 ? sc.xz : sc.xy);',
        '  rep = max(vec2(1.0), floor(rep / studSize + 0.5));',
        '  vUv = uv * rep;',
        '#endif',
      ].join('\n'));
    };
    mat.customProgramCacheKey = function () { return 'studs' + size; };
  }

  function squareDot() {
    return canvasTexture(32, function (g, s) {
      g.fillStyle = 'rgba(255,255,255,1)';
      g.fillRect(s * 0.2, s * 0.2, s * 0.6, s * 0.6);
    });
  }

  function gradientTexture(top, bottom) {
    return canvasTexture(256, function (g, s) {
      var r = g.createLinearGradient(0, 0, 0, s);
      r.addColorStop(0, top);
      r.addColorStop(1, bottom);
      g.fillStyle = r;
      g.fillRect(0, 0, s, s);
    });
  }

  function radialTexture(color) {
    return canvasTexture(256, function (g, s) {
      var r = g.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
      r.addColorStop(0, color);
      r.addColorStop(0.35, color.replace(/[\d.]+\)$/, '0.35)'));
      r.addColorStop(1, color.replace(/[\d.]+\)$/, '0)'));
      g.fillStyle = r;
      g.fillRect(0, 0, s, s);
    });
  }

  // ------------------------------------------------------------------ bloom HDR
  var VERT = 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }';

  function Bloom(renderer, opts) {
    this.renderer = renderer;
    this.opts = opts;
    var rt = { type: T.HalfFloatType, minFilter: T.LinearFilter, magFilter: T.LinearFilter, depthBuffer: false };
    this.sceneRT = new T.WebGLRenderTarget(4, 4, { type: T.HalfFloatType, minFilter: T.LinearFilter, magFilter: T.LinearFilter, samples: 4 });
    this.levels = [];
    for (var i = 0; i < 5; i++) this.levels.push([new T.WebGLRenderTarget(4, 4, rt), new T.WebGLRenderTarget(4, 4, rt)]);
    this.quadScene = new T.Scene();
    this.quadCam = new T.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    this.quad = new T.Mesh(new T.PlaneGeometry(2, 2));
    this.quad.frustumCulled = false;
    this.quadScene.add(this.quad);
    this.bright = new T.ShaderMaterial({
      uniforms: { tDiffuse: { value: null }, threshold: { value: opts.threshold } },
      vertexShader: VERT,
      fragmentShader: 'uniform sampler2D tDiffuse; uniform float threshold; varying vec2 vUv;' +
        'void main(){ vec3 c = texture2D(tDiffuse, vUv).rgb; float l = max(c.r, max(c.g, c.b));' +
        ' float k = smoothstep(threshold, threshold + 0.8, l); gl_FragColor = vec4(min(c * k, vec3(40.0)), 1.0); }',
      depthTest: false, depthWrite: false,
    });
    this.blur = new T.ShaderMaterial({
      uniforms: { tDiffuse: { value: null }, dir: { value: new T.Vector2() } },
      vertexShader: VERT,
      fragmentShader: 'uniform sampler2D tDiffuse; uniform vec2 dir; varying vec2 vUv;' +
        'void main(){ vec3 s = texture2D(tDiffuse, vUv).rgb * 0.227027;' +
        ' s += texture2D(tDiffuse, vUv + dir * 1.3846153846).rgb * 0.3162162162;' +
        ' s += texture2D(tDiffuse, vUv - dir * 1.3846153846).rgb * 0.3162162162;' +
        ' s += texture2D(tDiffuse, vUv + dir * 3.2307692308).rgb * 0.0702702703;' +
        ' s += texture2D(tDiffuse, vUv - dir * 3.2307692308).rgb * 0.0702702703;' +
        ' gl_FragColor = vec4(s, 1.0); }',
      depthTest: false, depthWrite: false,
    });
    this.composite = new T.ShaderMaterial({
      uniforms: {
        tScene: { value: null }, b0: { value: null }, b1: { value: null }, b2: { value: null }, b3: { value: null }, b4: { value: null },
        strength: { value: opts.strength }, exposure: { value: opts.exposure || 1.0 }, flash: { value: 0 },
        flashColor: { value: new T.Color(1, 1, 1) }, vignette: { value: opts.vignette == null ? 0.35 : opts.vignette },
      },
      vertexShader: VERT,
      fragmentShader: [
        'uniform sampler2D tScene, b0, b1, b2, b3, b4; uniform float strength, exposure, flash, vignette; uniform vec3 flashColor; varying vec2 vUv;',
        'vec3 aces(vec3 x){ return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0); }',
        'vec3 toSRGB(vec3 c){ return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(0.0031308, c)); }',
        'void main(){',
        ' vec3 c = texture2D(tScene, vUv).rgb;',
        ' vec3 b = texture2D(b0, vUv).rgb * 1.0 + texture2D(b1, vUv).rgb * 0.9 + texture2D(b2, vUv).rgb * 0.75 + texture2D(b3, vUv).rgb * 0.6 + texture2D(b4, vUv).rgb * 0.5;',
        ' c += b * strength + flashColor * flash;',
        ' c = aces(c * exposure);',
        ' float d = distance(vUv, vec2(0.5));',
        ' c *= 1.0 - vignette * smoothstep(0.35, 0.85, d);',
        ' gl_FragColor = vec4(toSRGB(c), 1.0);',
        '}',
      ].join('\n'),
      depthTest: false, depthWrite: false,
    });
  }
  Bloom.prototype.setSize = function (w, h) {
    this.sceneRT.setSize(w, h);
    for (var i = 0; i < this.levels.length; i++) {
      var lw = Math.max(1, w >> (i + 1)), lh = Math.max(1, h >> (i + 1));
      this.levels[i][0].setSize(lw, lh);
      this.levels[i][1].setSize(lw, lh);
    }
  };
  Bloom.prototype.pass = function (mat, target) {
    this.quad.material = mat;
    this.renderer.setRenderTarget(target);
    this.renderer.render(this.quadScene, this.quadCam);
  };
  Bloom.prototype.render = function (scene, camera) {
    var r = this.renderer;
    r.setRenderTarget(this.sceneRT);
    r.render(scene, camera);
    this.bright.uniforms.tDiffuse.value = this.sceneRT.texture;
    this.pass(this.bright, this.levels[0][0]);
    for (var i = 0; i < this.levels.length; i++) {
      var a = this.levels[i][0], b = this.levels[i][1];
      if (i > 0) {
        this.blur.uniforms.tDiffuse.value = this.levels[i - 1][0].texture;
        this.blur.uniforms.dir.value.set(0, 0);
        this.pass(this.blur, a);
      }
      var spread = this.opts.radius || 1;
      this.blur.uniforms.tDiffuse.value = a.texture;
      this.blur.uniforms.dir.value.set(spread / a.width, 0);
      this.pass(this.blur, b);
      this.blur.uniforms.tDiffuse.value = b.texture;
      this.blur.uniforms.dir.value.set(0, spread / a.height);
      this.pass(this.blur, a);
    }
    var u = this.composite.uniforms;
    u.tScene.value = this.sceneRT.texture;
    u.b0.value = this.levels[0][0].texture;
    u.b1.value = this.levels[1][0].texture;
    u.b2.value = this.levels[2][0].texture;
    u.b3.value = this.levels[3][0].texture;
    u.b4.value = this.levels[4][0].texture;
    this.pass(this.composite, null);
  };
  Bloom.prototype.dispose = function () {
    this.sceneRT.dispose();
    this.levels.forEach(function (l) { l[0].dispose(); l[1].dispose(); });
  };

  // ------------------------------------------------------------------ partículas
  // kind: 'rise' (suben y se desvanecen), 'orbit' (giran alrededor), 'snow' (caen), 'float' (flotan quietas)
  function Particles(cfg, textures) {
    this.cfg = cfg;
    var n = cfg.count;
    this.n = n;
    this.pos = new Float32Array(n * 3);
    this.seed = new Float32Array(n * 4);
    for (var i = 0; i < n; i++) {
      this.seed[i * 4] = Math.random();
      this.seed[i * 4 + 1] = Math.random();
      this.seed[i * 4 + 2] = Math.random();
      this.seed[i * 4 + 3] = Math.random();
    }
    var g = new T.BufferGeometry();
    g.setAttribute('position', new T.BufferAttribute(this.pos, 3));
    var m = new T.PointsMaterial({
      color: new T.Color(cfg.color).multiplyScalar(cfg.intensity || 3),
      size: cfg.size || 0.25,
      map: textures[cfg.sprite || 'dot'],
      transparent: true,
      depthWrite: false,
      blending: T.AdditiveBlending,
      sizeAttenuation: true,
    });
    this.points = new T.Points(g, m);
    this.points.frustumCulled = false;
  }
  Particles.prototype.update = function (t, center) {
    var c = this.cfg, p = this.pos, s = this.seed;
    var rIn = c.radius || [1, 4], h = c.height || [0, 8];
    for (var i = 0; i < this.n; i++) {
      var a = s[i * 4] * Math.PI * 2, r = lerp(rIn[0], rIn[1], s[i * 4 + 1]);
      var sp = (c.speed || 0.3) * (0.6 + s[i * 4 + 2] * 0.8);
      var x, y, z;
      if (c.kind === 'rise') {
        var life = (t * sp * 0.25 + s[i * 4 + 3]) % 1;
        var aa = a + t * 0.2;
        x = Math.cos(aa) * r * (1 - life * 0.3); z = Math.sin(aa) * r * (1 - life * 0.3);
        y = lerp(h[0], h[1], life);
      } else if (c.kind === 'snow') {
        var lf = (s[i * 4 + 3] - t * sp * 0.08) % 1;
        if (lf < 0) lf += 1;
        x = Math.cos(a) * r + Math.sin(t * 0.7 + i) * 0.3; z = Math.sin(a) * r + Math.cos(t * 0.6 + i) * 0.3;
        y = lerp(h[0], h[1], lf);
      } else if (c.kind === 'orbit') {
        var ao = a + t * sp;
        x = Math.cos(ao) * r; z = Math.sin(ao) * r;
        y = lerp(h[0], h[1], s[i * 4 + 3]) + Math.sin(t * 1.5 + i) * 0.3;
      } else {
        x = Math.cos(a) * r; z = Math.sin(a) * r;
        y = lerp(h[0], h[1], s[i * 4 + 3]) + Math.sin(t * sp + i) * 0.25;
      }
      p[i * 3] = center.x + x; p[i * 3 + 1] = y; p[i * 3 + 2] = center.z + z;
    }
    this.points.geometry.attributes.position.needsUpdate = true;
    if (c.twinkle) this.points.material.opacity = 0.7 + 0.3 * Math.sin(t * 5);
  };

  // estallido (partículas que salen disparadas una vez)
  function Burst(color, count, textures) {
    this.n = count;
    this.pos = new Float32Array(count * 3);
    this.vel = new Float32Array(count * 3);
    var g = new T.BufferGeometry();
    g.setAttribute('position', new T.BufferAttribute(this.pos, 3));
    this.mat = new T.PointsMaterial({
      color: new T.Color(color).multiplyScalar(6), size: 0.35, map: textures.sparkle, transparent: true,
      depthWrite: false, blending: T.AdditiveBlending, opacity: 0,
    });
    this.points = new T.Points(g, this.mat);
    this.points.frustumCulled = false;
    this.t = -1;
  }
  Burst.prototype.fire = function (center) {
    for (var i = 0; i < this.n; i++) {
      var u = Math.random() * 2 - 1, th = Math.random() * Math.PI * 2, k = Math.sqrt(1 - u * u);
      var sp = 4 + Math.random() * 9;
      this.vel[i * 3] = k * Math.cos(th) * sp;
      this.vel[i * 3 + 1] = u * sp * 0.8 + 3;
      this.vel[i * 3 + 2] = k * Math.sin(th) * sp;
      this.pos[i * 3] = center.x; this.pos[i * 3 + 1] = center.y; this.pos[i * 3 + 2] = center.z;
    }
    this.t = 0;
  };
  Burst.prototype.update = function (dt) {
    if (this.t < 0) return;
    this.t += dt;
    var drag = Math.exp(-dt * 1.6);
    for (var i = 0; i < this.n; i++) {
      this.vel[i * 3] *= drag; this.vel[i * 3 + 1] = this.vel[i * 3 + 1] * drag - 4 * dt; this.vel[i * 3 + 2] *= drag;
      this.pos[i * 3] += this.vel[i * 3] * dt; this.pos[i * 3 + 1] += this.vel[i * 3 + 1] * dt; this.pos[i * 3 + 2] += this.vel[i * 3 + 2] * dt;
    }
    this.points.geometry.attributes.position.needsUpdate = true;
    this.mat.opacity = Math.max(0, 1 - this.t / 2.2);
    if (this.t > 2.2) this.t = -1;
  };

  // ------------------------------------------------------------------ entorno para metales
  function makeEnvironment(renderer, tint) {
    var env = new T.Scene();
    var sky = new T.Mesh(new T.SphereGeometry(50, 32, 16), new T.MeshBasicMaterial({
      side: T.BackSide, map: gradientTexture(tint[0], tint[1]),
    }));
    env.add(sky);
    var panel = new T.MeshBasicMaterial({ color: new T.Color(1, 1, 1).multiplyScalar(6) });
    [[0, 30, 0, 30, 1, 30], [35, 10, 10, 1, 14, 24], [-35, 12, -6, 1, 10, 18], [0, 8, 38, 20, 8, 1]].forEach(function (b) {
      var m = new T.Mesh(new T.BoxGeometry(b[3], b[4], b[5]), panel);
      m.position.set(b[0], b[1], b[2]);
      env.add(m);
    });
    var pm = new T.PMREMGenerator(renderer);
    var rt = pm.fromScene(env, 0.03);
    pm.dispose();
    return rt;
  }

  // ------------------------------------------------------------------ piezas suaves
  var _sph = null;
  function primGeo(r, stud) {
    var parts = [];
    var sph = function (c, rad, q) {
      var gg = (_sph || (_sph = new T.SphereGeometry(1, 24, 16))).clone();
      var m4 = new T.Matrix4().compose(new T.Vector3().fromArray(c), q || new T.Quaternion(), new T.Vector3().fromArray(rad));
      gg.applyMatrix4(m4);
      var ru = Math.max(1, Math.round(Math.PI * (rad[0] + rad[2]) / stud)), rv = Math.max(1, Math.round(Math.PI * rad[1] / stud));
      var uv = gg.attributes.uv;
      for (var i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * ru, uv.getY(i) * rv);
      parts.push(gg);
    };
    if (r[0] === 0) {
      sph([r[1], r[2], r[3]], [r[4], r[5], r[6]], new T.Quaternion(r[7], r[8], r[9], r[10]));
    } else {
      var a = new T.Vector3(r[1], r[2], r[3]), b = new T.Vector3(r[4], r[5], r[6]), ra = r[7], rb = r[8];
      var d = new T.Vector3().subVectors(b, a), len = d.length();
      if (len > 1e-4) {
        var cyl = new T.CylinderGeometry(rb, ra, len, 20, 1, true);
        var q = new T.Quaternion().setFromUnitVectors(new T.Vector3(0, 1, 0), d.clone().normalize());
        cyl.applyMatrix4(new T.Matrix4().compose(a.clone().add(b).multiplyScalar(0.5), q, new T.Vector3(1, 1, 1)));
        var ru = Math.max(1, Math.round(Math.PI * (ra + rb) / stud)), rv = Math.max(1, Math.round(len / stud));
        var uv = cyl.attributes.uv;
        for (var i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * ru, uv.getY(i) * rv);
        parts.push(cyl);
      }
      sph([a.x, a.y, a.z], [ra, ra, ra]);
      sph([b.x, b.y, b.z], [rb, rb, rb]);
    }
    return parts;
  }

  function mergeGeos(lists) {
    var geos = [].concat.apply([], lists).map(function (g) { return g.index ? g.toNonIndexed() : g; });
    var n = 0;
    geos.forEach(function (g) { n += g.attributes.position.count; });
    var pos = new Float32Array(n * 3), nor = new Float32Array(n * 3), uv = new Float32Array(n * 2), o3 = 0, o2 = 0;
    geos.forEach(function (g) {
      pos.set(g.attributes.position.array, o3);
      nor.set(g.attributes.normal.array, o3);
      uv.set(g.attributes.uv.array, o2);
      o3 += g.attributes.position.array.length;
      o2 += g.attributes.uv.array.length;
      g.dispose();
    });
    var out = new T.BufferGeometry();
    out.setAttribute('position', new T.BufferAttribute(pos, 3));
    out.setAttribute('normal', new T.BufferAttribute(nor, 3));
    out.setAttribute('uv', new T.BufferAttribute(uv, 2));
    return out;
  }

  // ------------------------------------------------------------------ escena principal
  function create(canvas, data, o) {
    T.ColorManagement.legacyMode = false;
    // un renderer por canvas: cambiar de modelo reutiliza el mismo contexto WebGL
    var renderer = canvas.__voxelRenderer || new T.WebGLRenderer({ canvas: canvas, antialias: false, powerPreference: 'high-performance' });
    canvas.__voxelRenderer = renderer;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = T.PCFSoftShadowMap;
    renderer.outputEncoding = T.LinearEncoding;
    renderer.toneMapping = T.NoToneMapping;

    var bloom = new Bloom(renderer, o.bloom || { strength: 0.6, threshold: 1.0, radius: 1.0 });
    var scene = new T.Scene();
    scene.background = gradientTexture(o.bgTop, o.bgBottom);
    if (o.fog) scene.fog = new T.Fog(new T.Color(o.fog[2] || o.bgBottom), o.fog[0], o.fog[1]);
    var envRT = makeEnvironment(renderer, o.envTint || [o.bgTop, o.bgBottom]);
    scene.environment = envRT.texture;

    var camera = new T.PerspectiveCamera(o.fov || 35, 1, 0.1, 400);
    var textures = { dot: softDot(), sparkle: sparkle(), square: squareDot() };

    // luces
    var L = o.lights || {};
    var LS = 1 / Math.PI; // r149 multiplica por π las luces en modo no físico
    scene.add(new T.HemisphereLight(new T.Color(L.sky || '#bcd4ff'), new T.Color(L.groundCol || '#1a1428'), (L.hemi == null ? 0.6 : L.hemi) * LS));
    var key = new T.DirectionalLight(new T.Color(L.keyColor || '#ffffff'), (L.key == null ? 2.2 : L.key) * LS);
    key.position.set(8, 16, 11);
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    key.shadow.bias = -0.0004;
    key.shadow.normalBias = 0.02;
    Object.assign(key.shadow.camera, { left: -12, right: 12, top: 16, bottom: -6, near: 1, far: 60 });
    scene.add(key);
    (L.points || []).forEach(function (p) {
      var pl = new T.PointLight(new T.Color(p.color), p.intensity * LS, p.distance || 30, 2);
      pl.position.fromArray(p.pos);
      scene.add(pl);
    });

    // suelo
    if (o.ground) {
      var ground = new T.Mesh(new T.CircleGeometry(120, 64), new T.MeshStandardMaterial({ color: new T.Color(o.ground), roughness: 0.92, metalness: 0 }));
      ground.rotation.x = -Math.PI / 2;
      ground.receiveShadow = true;
      scene.add(ground);
    }
    if (o.groundGlow) {
      var gg = new T.Mesh(new T.PlaneGeometry(1, 1), new T.MeshBasicMaterial({
        map: radialTexture(o.groundGlow), transparent: true, depthWrite: false, blending: T.AdditiveBlending,
      }));
      gg.rotation.x = -Math.PI / 2;
      gg.position.y = 0.03;
      gg.scale.setScalar(o.groundGlowSize || 12);
      scene.add(gg);
    }

    // ------------------------------------------------ modelo (instancing por parte y material)
    var root = new T.Group();
    scene.add(root);
    var unit = new T.BoxGeometry(1, 1, 1);
    var mats = {}, glow = {}, nodes = {}, cubes = 0, burstSets = [], studTex = null;
    var dummy = new T.Object3D();
    data.parts.forEach(function (p) {
      var g = new T.Group();
      g.position.fromArray(p.p);
      g.quaternion.fromArray(p.q);
      (p.parent ? nodes[p.parent] : root).add(g);
      nodes[p.name] = g;
      var groups = {};
      var boxes = p.boxes || (p.bx || []).map(function (r) {
        // formato compacto: [x,y,z, sx,sy,sz, color, emit, tag, metal, qx,qy,qz,qw]
        return { c: [r[0], r[1], r[2]], s: [r[3], r[4], r[5]], col: data.pal[r[6]], emit: r[7] || 0,
                 tag: r[8] ? data.tags[r[8] - 1] : null, metal: r[9] || 0, q: r.length > 10 ? [r[10], r[11], r[12], r[13]] : [0, 0, 0, 1] };
      });
      boxes.forEach(function (b) {
        var k = b.col + '|' + (b.emit || 0) + '|' + (b.tag || '') + '|' + (b.metal || 0);
        (groups[k] = groups[k] || []).push(b);
      });
      Object.keys(groups).forEach(function (k) {
        var list = groups[k], b0 = list[0];
        var m = mats[k];
        if (!m) {
          var col = new T.Color(b0.col);
          m = new T.MeshStandardMaterial({
            color: col,
            roughness: b0.metal ? 0.22 : (o.roughness || 0.55),
            metalness: b0.metal ? 1.0 : 0.0,
            envMapIntensity: b0.metal ? 1.2 : (o.envIntensity || 0.25),
          });
          if (b0.emit) {
            m.emissive = col.clone();
            m.userData.base = b0.emit * (o.emitScale || 0.5);
            m.emissiveIntensity = m.userData.base;
            m.toneMapped = false;
          }
          if (b0.tag) (glow[b0.tag] = glow[b0.tag] || []).push(m);
          if (o.studs && !b0.emit) addStuds(m, studTex || (studTex = studBump()), o.studSize || 0.3, -(o.studBump || 0.9));
          mats[k] = m;
        }
        var im = new T.InstancedMesh(unit, m, list.length);
        im.castShadow = !b0.emit;
        im.receiveShadow = true;
        var base = [];
        list.forEach(function (b, i) {
          dummy.position.fromArray(b.c);
          dummy.quaternion.fromArray(b.q);
          dummy.scale.fromArray(b.s);
          dummy.updateMatrix();
          im.setMatrixAt(i, dummy.matrix);
          base.push({ c: new T.Vector3().fromArray(b.c), q: new T.Quaternion().fromArray(b.q), s: new T.Vector3().fromArray(b.s), r: rand(cubes + i) });
        });
        im.instanceMatrix.needsUpdate = true;
        g.add(im);
        cubes += list.length;
        if (o.burstPart && p.name === o.burstPart) burstSets.push({ im: im, base: base });
      });
      // piezas suaves (elipsoides y cápsulas) fusionadas por material
      if (p.pr && p.pr.length) {
        var pg = {};
        p.pr.forEach(function (r) { var ci = r[0] === 0 ? 11 : 9; (pg[r.slice(ci).join('|')] = pg[r.slice(ci).join('|')] || []).push(r); });
        Object.keys(pg).forEach(function (k) {
          var list = pg[k], r0 = list[0], ci = r0[0] === 0 ? 11 : 9;
          var col = new T.Color(data.pal[r0[ci]]), emit = r0[ci + 1] || 0, tag = r0[ci + 2] ? data.tags[r0[ci + 2] - 1] : null, metal = r0[ci + 3] || 0;
          var m = new T.MeshStandardMaterial({ color: col, roughness: metal ? 0.25 : 0.6, metalness: metal ? 1 : 0, envMapIntensity: metal ? 1.2 : (o.envIntensity || 0.25) });
          if (emit) { m.emissive = col.clone(); m.userData.base = emit * (o.emitScale || 0.5); m.emissiveIntensity = m.userData.base; }
          if (tag) (glow[tag] = glow[tag] || []).push(m);
          if (o.studs && !emit) { m.bumpMap = studTex || (studTex = studBump()); m.bumpScale = -(o.studBump || 0.9); }
          var geo = mergeGeos(list.map(function (r) { return primGeo(r, o.studSize || 0.3); }));
          var mesh = new T.Mesh(geo, m);
          mesh.castShadow = !emit;
          mesh.receiveShadow = true;
          g.add(mesh);
          cubes += list.length;
        });
      }
    });

    var fb = o.focus || data.bounds;
    var lo = fb[0], hi = fb[1];
    var size = Math.max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]);
    var target = new T.Vector3((lo[0] + hi[0]) / 2, o.targetY != null ? o.targetY : (hi[1] - lo[1]) * 0.48, (lo[2] + hi[2]) / 2);
    var views = o.views || { front: [0, 0.18], side: [Math.PI / 2, 0.15], tq: [0.7, 0.3] };
    var orbit = { theta: views.tq[0], phi: views.tq[1], r: size * (o.dist || 1.6), goal: null };

    // ------------------------------------------------ VFX extra
    var center = new T.Vector3(target.x, 0, target.z);
    var systems = (o.particles || []).map(function (cfg) {
      var ps = new Particles(cfg, textures);
      scene.add(ps.points);
      return ps;
    });
    var beam = null;
    if (o.beam) {
      var bt = canvasTexture(64, function (g, s) {
        var r = g.createLinearGradient(0, 0, 0, s);
        r.addColorStop(0, 'rgba(255,255,255,0)');
        r.addColorStop(0.7, 'rgba(255,255,255,0.5)');
        r.addColorStop(1, 'rgba(255,255,255,1)');
        g.fillStyle = r;
        g.fillRect(0, 0, s, s);
      });
      beam = new T.Mesh(new T.CylinderGeometry(o.beam.top, o.beam.bottom, o.beam.height, 32, 1, true), new T.MeshBasicMaterial({
        map: bt, color: new T.Color(o.beam.color).multiplyScalar(o.beam.intensity || 1.2), transparent: true,
        depthWrite: false, blending: T.AdditiveBlending, side: T.DoubleSide,
      }));
      beam.position.set(target.x, o.beam.y + o.beam.height / 2, target.z);
      scene.add(beam);
    }
    if (o.burstPart && !nodes[o.burstPart]) o.burstPart = null;
    var canBurst = !!(o.burstPart || o.special); // huevo: romper · animal: habilidad especial
    var burstFx = canBurst ? new Burst(o.burstColor || '#ffffff', 260, textures) : null;
    var burst2 = canBurst ? new Burst(o.burstColor2 || o.burstColor || '#ffffff', 160, textures) : null;
    if (burstFx) { scene.add(burstFx.points); scene.add(burst2.points); }
    var shock = null;
    if (canBurst) {
      shock = new T.Mesh(new T.RingGeometry(0.85, 1, 64), new T.MeshBasicMaterial({
        color: new T.Color(o.burstColor || '#ffffff').multiplyScalar(5), transparent: true, opacity: 0,
        depthWrite: false, blending: T.AdditiveBlending, side: T.DoubleSide,
      }));
      shock.rotation.x = -Math.PI / 2;
      scene.add(shock);
    }

    // ------------------------------------------------ estado
    var st = { playing: true, spin: true, t: 0, last: performance.now(), burstT: -1, dead: false };

    function resize() {
      var w = canvas.clientWidth, h = canvas.clientHeight;
      if (!w || !h) return;
      renderer.setSize(w, h, false);
      var pr = renderer.getPixelRatio();
      bloom.setSize(Math.floor(w * pr), Math.floor(h * pr));
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    var ro = new ResizeObserver(resize);
    ro.observe(canvas);
    resize();

    // control de órbita
    var drag = null;
    function down(e) { drag = { x: e.clientX, y: e.clientY }; orbit.goal = null; canvas.setPointerCapture(e.pointerId); canvas.style.cursor = 'grabbing'; }
    function move(e) {
      if (!drag) return;
      orbit.theta -= (e.clientX - drag.x) * 0.008;
      orbit.phi = Math.min(1.25, Math.max(-0.05, orbit.phi + (e.clientY - drag.y) * 0.006));
      drag = { x: e.clientX, y: e.clientY };
    }
    function up() { drag = null; canvas.style.cursor = 'grab'; }
    function wheel(e) {
      e.preventDefault();
      orbit.r = Math.min(size * 3.5, Math.max(size * 0.55, orbit.r * (1 + e.deltaY * 0.001)));
    }
    canvas.addEventListener('pointerdown', down);
    canvas.addEventListener('pointermove', move);
    canvas.addEventListener('pointerup', up);
    canvas.addEventListener('pointercancel', up);
    canvas.addEventListener('wheel', wheel, { passive: false });

    var tracks = Object.keys(data.tracks).map(function (n) { return [nodes[n], data.tracks[n]]; });
    var glowTracks = Object.keys(data.glow).map(function (tag) { return [glow[tag] || [], data.glow[tag]]; });
    var qa = new T.Quaternion(), qb = new T.Quaternion(), tmpQ = new T.Quaternion(), axis = new T.Vector3(), dir = new T.Vector3();
    var shakeNode = canBurst ? (nodes[o.shakePart || 'egg'] || null) : null;

    function applyBurst(bt, dt) {
      // 0-1.1 temblor creciente · 1.1 estallido · 1.1-2.0 vuelan · 2.0-3.0 vuelven
      var shakeAmt = bt < 1.1 ? easeInOut(bt / 1.1) : (bt < 1.3 ? 1 - (bt - 1.1) / 0.2 : 0);
      if (shakeNode) {
        shakeNode.rotation.z += Math.sin(bt * 60) * 0.06 * shakeAmt;
        shakeNode.rotation.x += Math.cos(bt * 47) * 0.04 * shakeAmt;
        shakeNode.position.x += Math.sin(bt * 71) * 0.08 * shakeAmt;
      }
      var out = 0;
      if (bt >= 1.1 && bt < 2.0) out = easeOut((bt - 1.1) / 0.9);
      else if (bt >= 2.0 && bt < 3.0) out = 1 - easeInOut((bt - 2.0) / 1.0);
      burstSets.forEach(function (set) {
        set.base.forEach(function (b, i) {
          dir.copy(b.c);
          if (dir.lengthSq() < 1e-6) dir.set(0, 1, 0);
          dir.normalize();
          var dist = out * (2.5 + b.r * 5);
          dummy.position.copy(b.c).addScaledVector(dir, dist);
          dummy.position.y += out * (b.r - 0.3) * 2;
          axis.set(b.r - 0.5, 0.5, 0.5 - b.r).normalize();
          tmpQ.setFromAxisAngle(axis, out * (3 + b.r * 6));
          dummy.quaternion.copy(b.q).premultiply(tmpQ);
          dummy.scale.copy(b.s).multiplyScalar(1 - out * 0.25);
          dummy.updateMatrix();
          set.im.setMatrixAt(i, dummy.matrix);
        });
        set.im.instanceMatrix.needsUpdate = true;
      });
      // destello y onda
      var fl = bt >= 1.1 ? Math.max(0, 1 - (bt - 1.1) / 0.45) : 0;
      bloom.composite.uniforms.flash.value = fl * fl * 1.6;
      if (shock) {
        var sp = bt >= 1.1 ? (bt - 1.1) / 1.2 : -1;
        shock.material.opacity = sp >= 0 && sp < 1 ? (1 - sp) : 0;
        shock.scale.setScalar(0.5 + Math.max(sp, 0) * 14);
        shock.position.set(target.x, 0.1, target.z);
      }
      var boost = bt < 1.1 ? 1 + 2.5 * shakeAmt : (bt < 2.2 ? 3.5 - (bt - 1.1) * 2 : 1);
      return Math.max(1, boost);
    }

    function frame(now) {
      if (st.dead) return;
      var dt = Math.max(0, Math.min(0.05, (now - st.last) / 1000));
      st.last = now;
      if (st.playing) st.t += dt;
      if (st.spin && !drag && !orbit.goal) orbit.theta += dt * 0.22;
      if (orbit.goal) {
        var dTh = orbit.goal[0] - orbit.theta;
        dTh = Math.atan2(Math.sin(dTh), Math.cos(dTh));
        orbit.theta += dTh * Math.min(1, dt * 5);
        orbit.phi += (orbit.goal[1] - orbit.phi) * Math.min(1, dt * 5);
        if (Math.abs(dTh) < 0.002 && Math.abs(orbit.goal[1] - orbit.phi) < 0.002) orbit.goal = null;
      }

      var f = (st.t * data.fps) % data.frames;
      var i0 = Math.floor(f), i1 = (i0 + 1) % data.frames, u = f - i0;
      for (var k = 0; k < tracks.length; k++) {
        var node = tracks[k][0], rows = tracks[k][1], a = rows[i0], b = rows[i1];
        if (!a || !b || !node) { if (!st.warned) { st.warned = true; console.warn('track', k, i0, rows && rows.length, !!node); } continue; }
        node.position.set(lerp(a[0], b[0], u), lerp(a[1], b[1], u), lerp(a[2], b[2], u));
        qa.set(a[3], a[4], a[5], a[6]);
        qb.set(b[3], b[4], b[5], b[6]);
        node.quaternion.slerpQuaternions(qa, qb, u);
        node.scale.set(lerp(a[7], b[7], u), lerp(a[8], b[8], u), lerp(a[9], b[9], u));
      }

      var boost = 1;
      if (st.burstT >= 0) {
        st.burstT += dt;
        boost = applyBurst(st.burstT, dt);
        if (st.burstT > 3.05) { st.burstT = -1; applyBurst(3.05, 0); bloom.composite.uniforms.flash.value = 0; }
      }
      for (var g2 = 0; g2 < glowTracks.length; g2++) {
        var list = glowTracks[g2][0], vals = glowTracks[g2][1];
        var gv = lerp(vals[i0], vals[i1], u) * boost;
        for (var j = 0; j < list.length; j++) list[j].emissiveIntensity = list[j].userData.base * gv;
      }
      var pt = st.t;
      systems.forEach(function (s) { s.update(pt, center); });
      if (beam) beam.material.opacity = 0.55 + 0.25 * Math.sin(pt * 3) + (boost - 1) * 0.3;
      if (burstFx) { burstFx.update(dt); burst2.update(dt); }

      camera.position.set(
        target.x + orbit.r * Math.cos(orbit.phi) * Math.sin(orbit.theta),
        target.y + orbit.r * Math.sin(orbit.phi),
        target.z + orbit.r * Math.cos(orbit.phi) * Math.cos(orbit.theta)
      );
      camera.lookAt(target);
      bloom.render(scene, camera);
      st.raf = requestAnimationFrame(frame);
    }
    st.raf = requestAnimationFrame(frame);

    return {
      cubes: cubes,
      parts: data.parts.length,
      seconds: data.frames / data.fps,
      setPlaying: function (v) { st.playing = v; },
      setSpin: function (v) { st.spin = v; if (v) orbit.goal = null; },
      setView: function (id) { st.spin = false; orbit.goal = views[id]; },
      burst: function () {
        if (!canBurst || st.burstT >= 0) return;
        st.burstT = 0;
        var c = new T.Vector3();
        (shakeNode || root).getWorldPosition(c);
        setTimeout(function () { if (!st.dead) { burstFx.fire(c); burst2.fire(c); } }, 1100);
      },
      dispose: function () {
        st.dead = true;
        cancelAnimationFrame(st.raf);
        ro.disconnect();
        canvas.removeEventListener('pointerdown', down);
        canvas.removeEventListener('pointermove', move);
        canvas.removeEventListener('pointerup', up);
        canvas.removeEventListener('pointercancel', up);
        canvas.removeEventListener('wheel', wheel);
        bloom.dispose();
        envRT.dispose();
        scene.traverse(function (obj) {
          if (obj.geometry) obj.geometry.dispose();
          if (obj.material) {
            [].concat(obj.material).forEach(function (mt) { if (mt.map) mt.map.dispose(); mt.dispose(); });
          }
        });
        if (scene.background && scene.background.dispose) scene.background.dispose();
        renderer.renderLists.dispose();
      },
    };
  }

  // ------------------------------------------------------------------ presets por modelo
  var PRESETS = {
    egg_celestial: {
      bgTop: '#0b1233', bgBottom: '#03050f', fog: [30, 80, '#050816'], ground: '#070b1c', fov: 34, dist: 1.9, targetY: 4.6,
      envTint: ['#9fc3ff', '#1a1f40'],
      lights: { sky: '#a9c6ff', groundCol: '#140f2a', hemi: 0.9, key: 2.6, points: [
        { color: '#33ffd0', intensity: 3, pos: [0, 2.5, 4], distance: 12 },
        { color: '#ff7ce0', intensity: 1.8, pos: [-5, 7, -3], distance: 16 },
        { color: '#8fb8ff', intensity: 2, pos: [5, 9, 4], distance: 18 },
      ] },
      bloom: { strength: 0.38, threshold: 1.35, radius: 1.0, exposure: 0.85 }, emitScale: 0.36,
      groundGlow: 'rgba(80,255,215,0.3)', groundGlowSize: 10,
      beam: { color: '#9dfbe6', top: 1.3, bottom: 0.7, height: 3.0, y: 0.9, intensity: 0.45 },
      particles: [
        { kind: 'rise', count: 140, color: '#7dfff0', size: 0.22, radius: [0.4, 3.2], height: [0.8, 11], speed: 0.6, intensity: 3 },
        { kind: 'orbit', count: 90, color: '#ffe58a', size: 0.32, radius: [3.6, 6], height: [1.5, 10], speed: 0.25, sprite: 'sparkle', intensity: 4 },
        { kind: 'float', count: 120, color: '#c6d8ff', size: 0.16, radius: [7, 22], height: [0.5, 18], speed: 0.8, sprite: 'square', intensity: 2 },
      ],
      burstPart: 'shell', shakePart: 'egg', burstColor: '#9dfbe6', burstColor2: '#ffe58a',
      views: { front: [0, 0.12], side: [Math.PI / 2, 0.12], tq: [0.55, 0.22] },
    },
    egg_ice: {
      bgTop: '#071a3a', bgBottom: '#020611', fog: [30, 80, '#03091a'], ground: '#05101f', fov: 34, dist: 1.9, targetY: 4.4,
      envTint: ['#bff3ff', '#0d2440'],
      lights: { sky: '#b5ecff', groundCol: '#0a1a2a', hemi: 0.9, key: 2.4, points: [
        { color: '#5ff4ff', intensity: 3, pos: [0, 1.5, 3], distance: 12 },
        { color: '#c8a8ff', intensity: 1.6, pos: [-5, 8, 3], distance: 16 },
        { color: '#9fe8ff', intensity: 2, pos: [5, 6, 5], distance: 18 },
      ] },
      bloom: { strength: 0.6, threshold: 1.25, radius: 1.0, exposure: 0.9 },
      groundGlow: 'rgba(95,244,255,0.3)', groundGlowSize: 12,
      particles: [
        { kind: 'snow', count: 260, color: '#e6fbff', size: 0.14, radius: [0.5, 12], height: [0, 16], speed: 0.8, sprite: 'square', intensity: 2.2 },
        { kind: 'rise', count: 120, color: '#5ff4ff', size: 0.22, radius: [0.5, 3.4], height: [0.3, 10], speed: 0.5, intensity: 3 },
        { kind: 'orbit', count: 70, color: '#c8a8ff', size: 0.3, radius: [3.4, 5.5], height: [1, 9], speed: -0.3, sprite: 'sparkle', intensity: 3.5 },
      ],
      emitScale: 0.28, burstPart: 'shell', shakePart: 'egg', burstColor: '#5ff4ff', burstColor2: '#c8a8ff',
      views: { front: [0, 0.12], side: [Math.PI / 2, 0.12], tq: [0.5, 0.22] },
    },
    shark_dino: {
      bgTop: '#111a2c', bgBottom: '#05070c', fog: [30, 75, '#070a12'], ground: '#0b1018', fov: 35, dist: 1.5,
      envTint: ['#8aa0c0', '#140c10'],
      lights: { sky: '#9fb4d8', groundCol: '#1a0f12', hemi: 0.6, key: 2.6, points: [
        { color: '#ff3020', intensity: 4, pos: [-7, 6, -7], distance: 22 },
        { color: '#ff2a22', intensity: 1.4, pos: [0, 0.8, 3], distance: 10 },
      ] },
      bloom: { strength: 0.5, threshold: 1.1, radius: 1.0, exposure: 1.0 },
      groundGlow: 'rgba(255,60,40,0.35)', groundGlowSize: 10,
      particles: [
        { kind: 'float', count: 80, color: '#ff6a5f', size: 0.12, radius: [6, 20], height: [0.3, 12], speed: 0.6, sprite: 'square', intensity: 2 },
      ],
      views: { front: [0, 0.18], side: [Math.PI / 2, 0.12], tq: [0.75, 0.25] },
    },
    mailbox: {
      bgTop: '#7cc4ff', bgBottom: '#d7efff', fog: [45, 120, '#cfeaff'], ground: '#5fb548', fov: 35, dist: 2.0,
      envTint: ['#cfe8ff', '#6aa35a'],
      lights: { sky: '#e1f2ff', groundCol: '#4e8a3a', hemi: 0.9, key: 2.6, keyColor: '#fff1dc', points: [] },
      bloom: { strength: 0.25, threshold: 1.4, radius: 1.0, exposure: 1.0 }, roughness: 0.65,
      particles: [
        { kind: 'float', count: 40, color: '#ffffff', size: 0.12, radius: [3, 10], height: [1, 9], speed: 0.6, sprite: 'square', intensity: 1.2 },
      ],
      vignette: 0.15,
      views: { front: [0, 0.12], side: [Math.PI / 2, 0.12], tq: [0.6, 0.22] },
    },
  };
  PRESETS.mailbox.bloom.vignette = 0.15;

  window.VoxelStage = {
    create: function (canvas, data, options) {
      var preset = Object.assign({}, PRESETS[data.name] || {}, data.stage || {});
      var o = Object.assign({}, preset, options || {});
      o.bloom = Object.assign({ strength: 0.6, threshold: 1.0, radius: 1.0 }, o.bloom);
      if (o.vignette != null) o.bloom.vignette = o.vignette;
      // Brillo contenido: poco resplandor y emisión suave (glow = 1 para el brillo original)
      var g = o.glow == null ? 0.45 : o.glow;
      o.emitScale = (o.emitScale || 0.5) * g;
      o.bloom.strength *= g * 0.8;
      o.bloom.threshold += (1 - g) * 0.6;
      o.particles = (o.particles || []).map(function (p) { return Object.assign({}, p, { intensity: (p.intensity || 3) * (0.35 + 0.65 * g) }); });
      if (o.beam) o.beam = Object.assign({}, o.beam, { intensity: (o.beam.intensity || 1) * g });
      if (o.groundGlow) o.groundGlow = o.groundGlow.replace(/[\d.]+\)$/, function (a) { return (parseFloat(a) * g).toFixed(2) + ')'; });
      return create(canvas, data, o);
    },
    presets: PRESETS,
  };
})();
