// yagusuri_generator.js
// Draw yagasuri pattern on canvas using unit/layout/palette/theme/render

export function drawYagasuri(ctx, cfg, canvasW, canvasH, common) {
  const unit = cfg?.unit ?? {};
  const layout = cfg?.layout ?? {};
  const palette = cfg?.palette ?? {};
  const theme = cfg?.theme ?? {};
  const render = cfg?.render ?? {};

  // Render setup
  ctx.save();
  ctx.setTransform(1,0,0,1,0,0);
  ctx.imageSmoothingEnabled = !!render.antialias;

  // Background
  const bg = (common?.bg ?? "#0b0d12");
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, canvasW, canvasH);

  // Normalize unit
  const nu = normalizeUnit(unit);

  // pitch
  const gapX = num(layout.gapX, 0);
  const gapY = num(layout.gapY, 0);
  const overlap = clamp(num(nu.wave.overlap, 0), 0, nu.H * 0.49);

  const pitchX = nu.W + gapX;
  const pitchY = nu.H + gapY - overlap;
  const colYOffsetEven = num(layout.colYOffsetEven, 0);
  const colYOffsetOdd = num(layout.colYOffsetOdd, 0);
  const colPitchScaleEven = clamp(num(layout.colPitchScaleEven, 1), 0.1, 10);
  const colPitchScaleOdd = clamp(num(layout.colPitchScaleOdd, 1), 0.1, 10);
  const pitchYMin = pitchY * Math.min(colPitchScaleEven, colPitchScaleOdd);

  // Alternate color mode (row)
  const useAlt = (palette.alternateMode === "row");

  // Precompute polygons (local coords)
  const leftPts  = buildLeftFeatherPolygon(nu);
  const rightPts = buildRightFeatherPolygon(nu, leftPts);
  const shaftPts = buildShaftPolygon(nu);

  // count (repeat/cover)
  const fillMode = (layout.fillMode ?? "cover");
  let cols, rows;

  if (fillMode === "repeat" && layout?.repeat?.cols && layout?.repeat?.rows) {
    cols = Math.max(1, Math.floor(layout.repeat.cols));
    rows = Math.max(1, Math.floor(layout.repeat.rows));
  } else {
    cols = Math.ceil(canvasW / pitchX) + 2;
    rows = Math.ceil(canvasH / pitchYMin) + 2;
  }

  const lockGap = clamp(num(layout.lockGap, 0), 0, 256);
  const halfPitch = (layout.offsetMode === "halfPitch");
  const flipEveryColumn = !!layout.flipEveryColumn;
  const flipEveryRow = !!layout.flipEveryRow;

  // Start offset so edges cover the canvas
  // (ok to start off-screen)
  const startX = -pitchX;
  const startY = -pitchY;

  for (let col = 0; col < cols; col++) {
    const baseX = startX + col * pitchX;

    for (let row = 0; row < rows; row++) {

      // Alternate scheme by row when useAlt=true
      // RowA/RowB colors
      const scheme =
        useAlt
          ? ((row % 2 === 1) ? (palette.rowA ?? null) : (palette.rowB ?? null))
          : null;

      const colors =
        scheme
          ? resolveSchemeColors(scheme, theme, common) // { left,right,shaft,stroke }
          : resolvePartColors(nu, palette, theme, common); // 従来互換 { left,right,shaft,stroke? }

      const isOddCol = (col % 2 === 1);
      const rawScale = isOddCol ? colPitchScaleOdd : colPitchScaleEven;
      const pitchScale = Math.min(rawScale, 1);
      const extraOffset = rawScale > 1 ? (rawScale - 1) * pitchY : 0;
      const pitchYCol = pitchY * pitchScale;

      let x = baseX;
      let y = startY + row * pitchYCol + extraOffset;

      // halfPitch
      if (halfPitch && isOddCol) y += (rawScale > 1 ? pitchY / 2 : pitchYCol / 2);

      // per-column Y offset
      y += isOddCol ? colYOffsetOdd : colYOffsetEven;

      // lockGap snap
      if (lockGap > 0) {
        x = snap(x, lockGap);
        y = snap(y, lockGap);
      }

        // Flip handling (base + row/column)
        const baseFlip = !!layout.flipBase;
        const flipY =
        baseFlip ^
        ((flipEveryColumn && (col % 2 === 1)) ^
        (flipEveryRow && (row % 2 === 1)));

      // Draw a single unit
      ctx.save();
      ctx.translate(x, y);

      if (flipY) {
        // Flip vertically: (x,y) -> (x, H-y)
        ctx.translate(0, nu.H);
        ctx.scale(1, -1);
      }

      // Draw polygons (with optional stroke)
      drawPolygon(ctx, leftPts,  colors.left,  render, colors.stroke);
      drawPolygon(ctx, rightPts, colors.right, render, colors.stroke);
      if (nu.shaft.enabled) drawPolygon(ctx, shaftPts, colors.shaft, render, colors.stroke);

      ctx.restore();
    }
  }

  ctx.restore();
}

// ------------------------------------------------------------
// Geometry
// ------------------------------------------------------------

function normalizeUnit(unit) {
  const W = clamp(num(unit.W, 120), 4, 4000);
  const H = clamp(num(unit.H, 240), 4, 8000);

  const shaftEnabled = (unit?.shaft?.enabled !== false);
  const S = clamp(num(unit?.shaft?.thickness, 28), 1, W - 2);

  let Lw = clamp(num(unit?.left?.width, (W - S) / 2), 1, W - 2);
  let Rw = clamp(num(unit?.right?.width, (W - S) / 2), 1, W - 2);

  // Adjust widths so L + S + R == W
  const sum = Lw + S + Rw;
  if (Math.abs(sum - W) > 1e-6) {
    const delta = W - sum;
    Lw += delta / 2;
    Rw += delta / 2;

    // clampしながら再調整
    Lw = clamp(Lw, 1, W - S - 1);
    Rw = clamp(Rw, 1, W - S - 1);

    const sum2 = Lw + S + Rw;
    if (Math.abs(sum2 - W) > 1e-6) {
      // Final fallback for width consistency
      Rw = clamp(W - S - Lw, 1, W - S - 1);
    }
  }

  const x0 = 0;
  const x1 = Lw;
  const x2 = Lw + S;
  const x3 = W;

  const slantLeft = clamp(num(unit?.left?.slantDy, 0), -H, H);
  const mirrorSlant = (unit?.right?.mirrorSlant !== false);
  const slantRight = mirrorSlant ? -slantLeft : slantLeft;

  // wave
  const notchDepth = clamp(num(unit?.wave?.notchDepth, 10), 0, Lw * 0.98);

  const notchSpanRaw = num(unit?.wave?.notchSpan, 0);
  const notchSpan = (notchSpanRaw > 0) ? clamp(notchSpanRaw, 2, H) : (H * 0.28);

  const nY1Raw = num(unit?.wave?.notchY1, 0);
  const nY2Raw = num(unit?.wave?.notchY2, 0);
  const notchY1 = (nY1Raw > 0) ? clamp(nY1Raw, 0, H) : (H * 0.33);
  const notchY2 = (nY2Raw > 0) ? clamp(nY2Raw, 0, H) : (H * 0.66);

  const overlap = clamp(num(unit?.wave?.overlap, 0), 0, H * 0.49);

  return {
    W, H,
    x0, x1, x2, x3,
    left: { width: Lw, slantDy: slantLeft },
    right: { width: Rw, slantDy: slantRight },
    shaft: { enabled: shaftEnabled, thickness: S },
    wave: { notchDepth, notchSpan, notchY1, notchY2, overlap },
  };
}

// Build left feather polygon (P0..P7 + slanted edge)
export function buildLeftFeatherPolygon(u) {
  const { x1, H } = u;
  const Lw = u.left.width;
  const slantDy = u.left.slantDy;

  const notchDepth = u.wave.notchDepth;
  const notchSpan  = u.wave.notchSpan;
  const notchY1    = u.wave.notchY1;
  const notchY2    = u.wave.notchY2;

  const yA = clamp(notchY1 - notchSpan / 2, 0, H);
  const yB = clamp(notchY1 + notchSpan / 2, 0, H);
  const yC = clamp(notchY2 - notchSpan / 2, 0, H);
  const yD = clamp(notchY2 + notchSpan / 2, 0, H);

  // Notches along the inner edge at x1
  const P0 = pt(x1, 0);
  const P1 = pt(x1, yA);
  const P2 = pt(x1 - notchDepth, notchY1);
  const P3 = pt(x1, yB);
  const P4 = pt(x1, yC);
  const P5 = pt(x1 - notchDepth, notchY2);
  const P6 = pt(x1, yD);
  const P7 = pt(x1, H);

  // Slanted outer edge using slantDy
  // a=(x1,H), b=(x1,0)
  const c = pt(x1 - Lw, H + slantDy);
  const d = pt(x1 - Lw, 0 + slantDy);

  // Order points for a clean polygon
  return [d, c, P7, P6, P5, P4, P3, P2, P1, P0];
}

export function buildRightFeatherPolygon(u, leftPts) {
  // 左羽根の全頂点めE(W-x, y) で反転
  const W = u.W;
  return leftPts.map(p => pt(W - p.x, p.y));
}

export function buildShaftPolygon(u) {
  const { x1, x2, H } = u;
  return [pt(x1, 0), pt(x2, 0), pt(x2, H), pt(x1, H)];
}

// ------------------------------------------------------------
// Color / Theme
// ------------------------------------------------------------

function resolvePartColors(u, palette, theme, common) {
  // baseA/baseB fall back to common fg/bg
  const baseA = (palette.baseA && palette.baseA.trim()) ? palette.baseA.trim() : (common?.fg ?? "#e7e7ea");
  const baseB = (palette.baseB && palette.baseB.trim()) ? palette.baseB.trim() : (common?.bg ?? "#0b0d12");

  let featherHex = baseA;
  let shaftHex = baseB;

  const rule = String(palette.rule ?? "A=feather,B=shaft").toLowerCase();
  // Swap A/B if rule says so
  // 侁E "a=shaft,b=feather" なら反転
  const aIsShaft = rule.includes("a=shaft");
  const bIsFeather = rule.includes("b=feather");
  if (aIsShaft || bIsFeather) {
    featherHex = baseB;
    shaftHex = baseA;
  }

  // Left/Right/Shaft override if provided
  const left = (palette.leftColor && palette.leftColor.trim()) ? palette.leftColor.trim() : featherHex;
  const right = (palette.rightColor && palette.rightColor.trim()) ? palette.rightColor.trim() : featherHex;
  const shaft = (palette.shaftColor && palette.shaftColor.trim()) ? palette.shaftColor.trim() : shaftHex;

  return {
    left: applyThemeToColor(left, theme),
    right: applyThemeToColor(right, theme),
    shaft: applyThemeToColor(shaft, theme),
  };
}

function applyThemeToColor(hex, theme) {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex; // invalid hex

  const hueShift = num(theme.hueShift, 0);
  const satScale = num(theme.saturationScale, 1);
  const briScale = num(theme.brightnessScale, 1);
  const contrast = num(theme.contrast, 1);

  let { h, s, l } = rgbToHsl(rgb.r, rgb.g, rgb.b);

  h = (h + hueShift) % 360; if (h < 0) h += 360;
  s = clamp(s * satScale, 0, 1);
  l = clamp(l * briScale, 0, 1);

  let out = hslToRgb(h, s, l);

  // contrast around 0.5
  out.r = clamp01((out.r - 0.5) * contrast + 0.5);
  out.g = clamp01((out.g - 0.5) * contrast + 0.5);
  out.b = clamp01((out.b - 0.5) * contrast + 0.5);

  return `rgb(${Math.round(out.r * 255)},${Math.round(out.g * 255)},${Math.round(out.b * 255)})`;
}

// ------------------------------------------------------------
// Draw helpers
// ------------------------------------------------------------

function drawPolygon(ctx, pts, fill, render, strokeColorOverride = null) {
  if (!pts || pts.length < 3) return;

  ctx.beginPath();
  ctx.moveTo(pts[0].x, pts[0].y);
  for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i].x, pts[i].y);
  ctx.closePath();

  ctx.fillStyle = fill;
  ctx.fill();

  if (render?.strokeEnabled) {
    ctx.strokeStyle = strokeColorOverride ?? (render.strokeColor ?? "#000");
    ctx.lineWidth = clamp(num(render.strokeWidth, 1), 0, 100);
    ctx.stroke();
  }
}

function resolveSchemeColors(scheme, theme, common) {
  // scheme: { feather, shaft, stroke } を想宁E
  const feather = scheme.feather ?? (common?.fg ?? "#e7e7ea");
  const shaft   = scheme.shaft   ?? (common?.bg ?? "#0b0d12");
  const stroke  = scheme.stroke  ?? shaft;

  const f = applyThemeToColor(feather, theme);
  const s = applyThemeToColor(shaft, theme);
  const k = applyThemeToColor(stroke, theme);

  // left/right use feather color by default
  return { left: f, right: f, shaft: s, stroke: k };
}

// ------------------------------------------------------------
// Utils
// ------------------------------------------------------------

function pt(x, y) { return { x, y }; }
function num(v, dflt) { const n = Number(v); return Number.isFinite(n) ? n : dflt; }
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
function snap(v, step) { return Math.round(v / step) * step; }
function clamp01(v) { return clamp(v, 0, 1); }

// hex -> rgb(0..1)
function hexToRgb(hex) {
  if (!hex) return null;
  const s = String(hex).trim();
  const m = s.match(/^#?([0-9a-f]{6}|[0-9a-f]{3})$/i);
  if (!m) return null;
  let h = m[1];
  if (h.length === 3) h = h.split("").map(ch => ch + ch).join("");
  const n = parseInt(h, 16);
  const r = ((n >> 16) & 255) / 255;
  const g = ((n >> 8) & 255) / 255;
  const b = (n & 255) / 255;
  return { r, g, b };
}

// rgb(0..1) -> hsl
function rgbToHsl(r, g, b) {
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  let h = 0, s = 0;
  const l = (max + min) / 2;
  const d = max - min;
  if (d !== 0) {
    s = d / (1 - Math.abs(2 * l - 1));
    switch (max) {
      case r: h = 60 * (((g - b) / d) % 6); break;
      case g: h = 60 * (((b - r) / d) + 2); break;
      default: h = 60 * (((r - g) / d) + 4); break;
    }
  }
  if (h < 0) h += 360;
  return { h, s, l };
}

// hsl -> rgb(0..1)
function hslToRgb(h, s, l) {
  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = l - c / 2;

  let rp = 0, gp = 0, bp = 0;
  if (0 <= h && h < 60) { rp = c; gp = x; bp = 0; }
  else if (60 <= h && h < 120) { rp = x; gp = c; bp = 0; }
  else if (120 <= h && h < 180) { rp = 0; gp = c; bp = x; }
  else if (180 <= h && h < 240) { rp = 0; gp = x; bp = c; }
  else if (240 <= h && h < 300) { rp = x; gp = 0; bp = c; }
  else { rp = c; gp = 0; bp = x; }

  return { r: rp + m, g: gp + m, b: bp + m };
}
