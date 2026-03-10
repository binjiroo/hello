import { uiNumber, uiText, uiSelect } from "../../../ui.js";
import { drawYagasuri } from "./yagusuri_generator.js";

export const manifest = {
  id: "trad.yagasuri",
  name: "矢絣 (Yagasuri)",
  version: "0.1.0",
  defaults: {
    cfg: {
      unit: {
        W: 120,
        H: 240,
        left: { width: 46, slantDy: 0 },
        right: { width: 46, slantDy: 0, mirrorSlant: true }, // mirrorSlant=true: mirror left slantDy
        shaft: { enabled: true, thickness: 28 },
        wave: {
          notchDepth: 10,
          notchSpan: 0,   // 0 = auto (H * 0.28)
          notchY1: 0,     // 0 = auto (H * 0.33)
          notchY2: 0,     // 0 = auto (H * 0.66)
          overlap: 0,
        },
      },
      layout: {
        gapX: 0,
        gapY: 0,
        offsetMode: "halfPitch",     // none | halfPitch
        flipEveryColumn: true,
        flipEveryRow: false,

        // Layout tweaks
        flipBase: false,       // base flip before row/column flips
        colYOffsetEven: 0,     // even column Y offset
        colYOffsetOdd: 0,      // odd column Y offset
        colPitchScaleEven: 1,  // even column pitchY scale
        colPitchScaleOdd: 1,   // odd column pitchY scale

        lockGap: 0,                  // 0=off, >0=スナッチE
        fillMode: "cover",           // cover | repeat
        repeat: { cols: 8, rows: 6 } // fillMode=repeat のとき利用
      },
        palette: {
        baseA: "",
        baseB: "",
        rule: "A=feather,B=shaft",
        leftColor: "",
        rightColor: "",
        shaftColor: "",

        // Alternate color mode
        // none   : use rule/baseA/baseB
        // row    : 行ごと (row%2)
        // checker: alternate by (row+col)%2
        alternateMode: "row", // "none" | "row" | "checker"
        altPhase: 0,              // 0 or 1: swap A/B

        // Default RowA/RowB colors
        rowA: { feather: "#6b4bbd", shaft: "#ffffff", stroke: "#ffffff" },
        rowB: { feather: "#ffffff", shaft: "#6b4bbd", stroke: "#6b4bbd" },
        },
        render: {
        strokeEnabled: true,
        strokeWidth: 1,
        },
      theme: {
        hueShift: 0,
        saturationScale: 1,
        brightnessScale: 1,
        contrast: 1,
      },
      render: {
        antialias: true,
        strokeEnabled: false,
        strokeColor: "#000000",
        strokeWidth: 1,
      }
    }
  },
};

export function createUI(root, state, api) {
  // state is patterns[patternId]
  if (!state.cfg) state.cfg = structuredClone(manifest.defaults.cfg);

  const cfg = state.cfg;
  const u = cfg.unit;
  const lay = cfg.layout;
  const pal = cfg.palette;
  const th = cfg.theme;
  const rr = cfg.render;
  const targetInputs = {};

  // --- Unit ---
  uiNumber({
    root, label: "Unit W",
    value: u.W, min: 10, max: 800, step: 1,
    onChange: (v) => { u.W = v; api.requestRender(); }
  });
  uiNumber({
    root, label: "Unit H",
    value: u.H, min: 10, max: 1200, step: 1,
    onChange: (v) => { u.H = v; api.requestRender(); }
  });

  uiNumber({
    root, label: "Left width",
    value: u.left.width, min: 1, max: 600, step: 1,
    onChange: (v) => { u.left.width = v; api.requestRender(); }
  });
  uiNumber({
    root, label: "Right width",
    value: u.right.width, min: 1, max: 600, step: 1,
    onChange: (v) => { u.right.width = v; api.requestRender(); }
  });

  uiNumber({
    root, label: "Shaft thickness",
    value: u.shaft.thickness, min: 1, max: 600, step: 1,
    onChange: (v) => { u.shaft.thickness = v; api.requestRender(); }
  });

  uiSelect({
    root, label: "Shaft enabled",
    value: String(u.shaft.enabled ?? true),
    options: [{ value: "true", label: "true" }, { value: "false", label: "false" }],
    onChange: (v) => { u.shaft.enabled = (v === "true"); api.requestRender(); }
  });

  uiNumber({
    root, label: "Slant dy (left)",
    value: u.left.slantDy ?? 0, min: -300, max: 300, step: 1,
    onChange: (v) => { u.left.slantDy = v; api.requestRender(); }
  });

  uiSelect({
    root, label: "Right slant mirror",
    value: String(u.right.mirrorSlant ?? true),
    options: [{ value: "true", label: "true" }, { value: "false", label: "false" }],
    onChange: (v) => { u.right.mirrorSlant = (v === "true"); api.requestRender(); }
  });

  uiNumber({
    root, label: "Notch depth",
    value: u.wave.notchDepth ?? 10, min: 0, max: 300, step: 1,
    onChange: (v) => { u.wave.notchDepth = v; api.requestRender(); }
  });
  uiNumber({
    root, label: "Notch span (0=auto)",
    value: u.wave.notchSpan ?? 0, min: 0, max: 800, step: 1,
    onChange: (v) => { u.wave.notchSpan = v; api.requestRender(); }
  });
  uiNumber({
    root, label: "Notch Y1 (0=auto)",
    value: u.wave.notchY1 ?? 0, min: 0, max: 2000, step: 1,
    onChange: (v) => { u.wave.notchY1 = v; api.requestRender(); }
  });
  uiNumber({
    root, label: "Notch Y2 (0=auto)",
    value: u.wave.notchY2 ?? 0, min: 0, max: 2000, step: 1,
    onChange: (v) => { u.wave.notchY2 = v; api.requestRender(); }
  });

  uiNumber({
    root, label: "Overlap",
    value: u.wave.overlap ?? 0, min: 0, max: 600, step: 1,
    onChange: (v) => { u.wave.overlap = v; api.requestRender(); }
  });

  // --- Layout ---
  uiNumber({
    root, label: "Gap X",
    value: lay.gapX ?? 0, min: -300, max: 300, step: 1,
    onChange: (v) => { lay.gapX = v; api.requestRender(); }
  });
  uiNumber({
    root, label: "Gap Y",
    value: lay.gapY ?? 0, min: -300, max: 300, step: 1,
    onChange: (v) => { lay.gapY = v; api.requestRender(); }
  });

  uiSelect({
    root, label: "Offset mode",
    value: lay.offsetMode ?? "halfPitch",
    options: [
      { value: "none", label: "none" },
      { value: "halfPitch", label: "halfPitch" },
    ],
    onChange: (v) => { lay.offsetMode = v; api.requestRender(); }
  });

  uiSelect({
    root, label: "flipEveryColumn",
    value: String(lay.flipEveryColumn ?? true),
    options: [{ value: "true", label: "true" }, { value: "false", label: "false" }],
    onChange: (v) => { lay.flipEveryColumn = (v === "true"); api.requestRender(); }
  });

  uiSelect({
    root, label: "flipEveryRow",
    value: String(lay.flipEveryRow ?? false),
    options: [{ value: "true", label: "true" }, { value: "false", label: "false" }],
    onChange: (v) => { lay.flipEveryRow = (v === "true"); api.requestRender(); }
  });
  uiNumber({
    root, label: "Col pitch scale (even)",
    value: lay.colPitchScaleEven ?? 1, min: 0.2, max: 3, step: 0.05,
    onChange: (v) => { lay.colPitchScaleEven = v; api.requestRender(); }
  });
  uiNumber({
    root, label: "Col pitch scale (odd)",
    value: lay.colPitchScaleOdd ?? 1, min: 0.2, max: 3, step: 0.05,
    onChange: (v) => { lay.colPitchScaleOdd = v; api.requestRender(); }
  });

  uiNumber({
    root, label: "lockGap (0=off)",
    value: lay.lockGap ?? 0, min: 0, max: 64, step: 1,
    onChange: (v) => { lay.lockGap = v; api.requestRender(); }
  });

  uiSelect({
    root, label: "Fill mode",
    value: lay.fillMode ?? "cover",
    options: [{ value: "cover", label: "cover" }, { value: "repeat", label: "repeat" }],
    onChange: (v) => { lay.fillMode = v; api.requestRender(); }
  });

  uiNumber({
    root, label: "Repeat cols",
    value: lay.repeat?.cols ?? 8, min: 1, max: 200, step: 1,
    onChange: (v) => { if (!lay.repeat) lay.repeat = { cols: 8, rows: 6 }; lay.repeat.cols = v; api.requestRender(); }
  });
  uiNumber({
    root, label: "Repeat rows",
    value: lay.repeat?.rows ?? 6, min: 1, max: 200, step: 1,
    onChange: (v) => { if (!lay.repeat) lay.repeat = { cols: 8, rows: 6 }; lay.repeat.rows = v; api.requestRender(); }
  });

  // --- Palette / Theme ---
  const baseAInput = uiText({
    root, label: "Base A (empty=common.fg)",
    value: pal.baseA ?? "",
    placeholder: "#e7e7ea",
    onChange: (v) => { pal.baseA = v.trim(); api.requestRender(); }
  });
  const baseBInput = uiText({
    root, label: "Base B (empty=common.bg)",
    value: pal.baseB ?? "",
    placeholder: "#0b0d12",
    onChange: (v) => { pal.baseB = v.trim(); api.requestRender(); }
  });
  uiText({
    root, label: "Rule",
    value: pal.rule ?? "A=feather,B=shaft",
    placeholder: "A=feather,B=shaft",
    onChange: (v) => { pal.rule = v; api.requestRender(); }
  });
  uiSelect({
    root, label: "Alt mode",
    value: String((pal.alternateMode ?? "none")),
    options: [
      { value: "none", label: "none" },
      { value: "row", label: "row" },
      { value: "checker", label: "checker" },
    ],
    onChange: (v) => { pal.alternateMode = v; api.requestRender(); }
  });

  uiNumber({
    root, label: "Alt phase (0/1)",
    value: pal.altPhase ?? 0,
    min: 0, max: 1, step: 1,
    onChange: (v) => { pal.altPhase = (v|0)&1; api.requestRender(); }
  });

  // RowA / RowB
  if (!pal.rowA) pal.rowA = { feather: "#6b4bbd", shaft: "#ffffff", stroke: "#ffffff" };
  if (!pal.rowB) pal.rowB = { feather: "#ffffff", shaft: "#6b4bbd", stroke: "#6b4bbd" };

  const rowAFeatherInput = uiText({
    root, label: "RowA feather", value: pal.rowA.feather ?? "",
    placeholder: "#6b4bbd",
    onChange: (v) => { pal.rowA.feather = v.trim(); api.requestRender(); }
  });
  const rowAShaftInput = uiText({
    root, label: "RowA shaft", value: pal.rowA.shaft ?? "",
    placeholder: "#ffffff",
    onChange: (v) => { pal.rowA.shaft = v.trim(); api.requestRender(); }
  });
  const rowAStrokeInput = uiText({
    root, label: "RowA stroke", value: pal.rowA.stroke ?? "",
    placeholder: "#ffffff",
    onChange: (v) => { pal.rowA.stroke = v.trim(); api.requestRender(); }
  });

  const rowBFeatherInput = uiText({
    root, label: "RowB feather", value: pal.rowB.feather ?? "",
    placeholder: "#ffffff",
    onChange: (v) => { pal.rowB.feather = v.trim(); api.requestRender(); }
  });
  const rowBShaftInput = uiText({
    root, label: "RowB shaft", value: pal.rowB.shaft ?? "",
    placeholder: "#6b4bbd",
    onChange: (v) => { pal.rowB.shaft = v.trim(); api.requestRender(); }
  });
  const rowBStrokeInput = uiText({
    root, label: "RowB stroke", value: pal.rowB.stroke ?? "",
    placeholder: "#6b4bbd",
    onChange: (v) => { pal.rowB.stroke = v.trim(); api.requestRender(); }
  });

  targetInputs.baseA = baseAInput.inp;
  targetInputs.baseB = baseBInput.inp;
  targetInputs.rowA_feather = rowAFeatherInput.inp;
  targetInputs.rowA_shaft = rowAShaftInput.inp;
  targetInputs.rowA_stroke = rowAStrokeInput.inp;
  targetInputs.rowB_feather = rowBFeatherInput.inp;
  targetInputs.rowB_shaft = rowBShaftInput.inp;
  targetInputs.rowB_stroke = rowBStrokeInput.inp;

  // --- Color Tools ---
  const colorTitle = document.createElement("div");
  colorTitle.className = "panelTitle";
  colorTitle.textContent = "Color Tools";
  root.appendChild(colorTitle);

  const colorTools = document.createElement("div");
  colorTools.className = "colorTools";
  root.appendChild(colorTools);

  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  const hexToRgb = (hex) => {
    const s = String(hex || "").trim();
    const m = s.match(/^#?([0-9a-f]{6}|[0-9a-f]{3})$/i);
    if (!m) return null;
    let h = m[1];
    if (h.length === 3) h = h.split("").map(ch => ch + ch).join("");
    const n = parseInt(h, 16);
    return { r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255 };
  };
  const rgbToHex = (r, g, b) =>
    "#" + [r, g, b].map(v => clamp(Math.round(v), 0, 255).toString(16).padStart(2, "0")).join("");
  const rgbToHsl = (r, g, b) => {
    r /= 255; g /= 255; b /= 255;
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
    return { h, s: s * 100, l: l * 100 };
  };
  const hslToRgb = (h, s, l) => {
    s /= 100; l /= 100;
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
    return { r: (rp + m) * 255, g: (gp + m) * 255, b: (bp + m) * 255 };
  };

  const ensureRows = () => {
    if (!pal.rowA) pal.rowA = { feather: "#6b4bbd", shaft: "#ffffff", stroke: "#ffffff" };
    if (!pal.rowB) pal.rowB = { feather: "#ffffff", shaft: "#6b4bbd", stroke: "#6b4bbd" };
  };
  ensureRows();

  const targets = [
    { id: "baseA", label: "Base A", get: () => pal.baseA || "#e7e7ea", set: (v) => { pal.baseA = v; } },
    { id: "baseB", label: "Base B", get: () => pal.baseB || "#0b0d12", set: (v) => { pal.baseB = v; } },
    { id: "left", label: "Left", get: () => pal.leftColor || pal.baseA || "#e7e7ea", set: (v) => { pal.leftColor = v; } },
    { id: "right", label: "Right", get: () => pal.rightColor || pal.baseA || "#e7e7ea", set: (v) => { pal.rightColor = v; } },
    { id: "shaft", label: "Shaft", get: () => pal.shaftColor || pal.baseB || "#0b0d12", set: (v) => { pal.shaftColor = v; } },
    { id: "rowA_feather", label: "RowA feather", get: () => pal.rowA.feather, set: (v) => { pal.rowA.feather = v; } },
    { id: "rowA_shaft", label: "RowA shaft", get: () => pal.rowA.shaft, set: (v) => { pal.rowA.shaft = v; } },
    { id: "rowA_stroke", label: "RowA stroke", get: () => pal.rowA.stroke, set: (v) => { pal.rowA.stroke = v; } },
    { id: "rowB_feather", label: "RowB feather", get: () => pal.rowB.feather, set: (v) => { pal.rowB.feather = v; } },
    { id: "rowB_shaft", label: "RowB shaft", get: () => pal.rowB.shaft, set: (v) => { pal.rowB.shaft = v; } },
    { id: "rowB_stroke", label: "RowB stroke", get: () => pal.rowB.stroke, set: (v) => { pal.rowB.stroke = v; } },
  ];

  const row1 = document.createElement("div");
  row1.className = "colorRow";
  const targetLabel = document.createElement("label");
  targetLabel.textContent = "Target";
  const targetSelect = document.createElement("select");
  for (const t of targets) {
    const opt = document.createElement("option");
    opt.value = t.id;
    opt.textContent = t.label;
    targetSelect.appendChild(opt);
  }
  row1.appendChild(targetLabel);
  row1.appendChild(targetSelect);
  colorTools.appendChild(row1);

  const row2 = document.createElement("div");
  row2.className = "colorRow";
  const pickLabel = document.createElement("label");
  pickLabel.textContent = "Picker";
  const colorPicker = document.createElement("input");
  colorPicker.type = "color";
  row2.appendChild(pickLabel);
  row2.appendChild(colorPicker);
  colorTools.appendChild(row2);

  const hexRow = document.createElement("div");
  hexRow.className = "colorRow";
  const hexLabel = document.createElement("label");
  hexLabel.textContent = "HEX";
  const hexInput = document.createElement("input");
  hexInput.type = "text";
  hexInput.placeholder = "#112233";
  hexRow.appendChild(hexLabel);
  hexRow.appendChild(hexInput);
  colorTools.appendChild(hexRow);

  const rgbRow = document.createElement("div");
  rgbRow.className = "colorRow";
  const rgbLabel = document.createElement("label");
  rgbLabel.textContent = "RGB";
  const rgbWrap = document.createElement("div");
  rgbWrap.className = "colorInputs";
  const rgbR = document.createElement("input");
  const rgbG = document.createElement("input");
  const rgbB = document.createElement("input");
  [rgbR, rgbG, rgbB].forEach((el) => { el.type = "number"; el.min = "0"; el.max = "255"; el.step = "1"; });
  rgbWrap.appendChild(rgbR); rgbWrap.appendChild(rgbG); rgbWrap.appendChild(rgbB);
  rgbRow.appendChild(rgbLabel);
  rgbRow.appendChild(rgbWrap);
  colorTools.appendChild(rgbRow);

  const hslRow = document.createElement("div");
  hslRow.className = "colorRow";
  const hslLabel = document.createElement("label");
  hslLabel.textContent = "HSL";
  const hslWrap = document.createElement("div");
  hslWrap.className = "colorInputs";
  const hslH = document.createElement("input");
  const hslS = document.createElement("input");
  const hslL = document.createElement("input");
  hslH.type = "number"; hslH.min = "0"; hslH.max = "360"; hslH.step = "1";
  hslS.type = "number"; hslS.min = "0"; hslS.max = "100"; hslS.step = "1";
  hslL.type = "number"; hslL.min = "0"; hslL.max = "100"; hslL.step = "1";
  hslWrap.appendChild(hslH); hslWrap.appendChild(hslS); hslWrap.appendChild(hslL);
  hslRow.appendChild(hslLabel);
  hslRow.appendChild(hslWrap);
  colorTools.appendChild(hslRow);

  const swatchLabel = document.createElement("div");
  swatchLabel.className = "swatchLabel";
  swatchLabel.textContent = "Traditional Swatches";
  colorTools.appendChild(swatchLabel);
  const swatchGrid = document.createElement("div");
  swatchGrid.className = "swatchGrid";
  colorTools.appendChild(swatchGrid);

  const recentLabel = document.createElement("div");
  recentLabel.className = "swatchLabel";
  recentLabel.textContent = "Recent";
  colorTools.appendChild(recentLabel);
  const recentGrid = document.createElement("div");
  recentGrid.className = "swatchGrid";
  colorTools.appendChild(recentGrid);

  const swatches = [
    { name: "Shironeri", hex: "#f2e9e4" }, { name: "Kinari", hex: "#f1e0c5" },
    { name: "Kohaku", hex: "#f6c0a8" }, { name: "Sakura", hex: "#f4a7b9" },
    { name: "Nadeshiko", hex: "#d05a6e" }, { name: "Kurenai", hex: "#8f1d21" },
    { name: "Aka", hex: "#b31b1b" }, { name: "Kihada", hex: "#f1c40f" },
    { name: "Yamabuki", hex: "#e9c46a" }, { name: "Susu", hex: "#a78b71" },
    { name: "Kogecha", hex: "#6e4b3a" }, { name: "Kurocha", hex: "#3d2b1f" },
    { name: "Sumi", hex: "#1c1c1c" }, { name: "Nibi", hex: "#4a4e69" },
    { name: "Kuro", hex: "#22223b" }, { name: "Ususumi", hex: "#9a8c98" },
    { name: "Kachi", hex: "#0f4c5c" }, { name: "Kon", hex: "#1b4965" },
    { name: "Nando", hex: "#3d5a80" }, { name: "Asagi", hex: "#98c1d9" },
    { name: "Mizu", hex: "#e0fbfc" }, { name: "Seiji", hex: "#5f8575" },
    { name: "Urahayanagi", hex: "#b7c9b2" }, { name: "Moegi", hex: "#4f6d2f" },
    { name: "Wakaba", hex: "#7b9e2f" }, { name: "Kimidori", hex: "#b5bd00" },
    { name: "Aoni", hex: "#264653" }, { name: "Rokushou", hex: "#3f4c3b" },
    { name: "Murasaki", hex: "#5e548e" }, { name: "Fuji", hex: "#9f86c0" },
    { name: "Usumurasaki", hex: "#be95c4" }, { name: "Kikyo", hex: "#8d6b94" },
    { name: "Tsuchiiro", hex: "#d4a373" }, { name: "Mame", hex: "#8d6a9f" },
    { name: "SakuraNezu", hex: "#c9ada7" }, { name: "Shiro", hex: "#f7f0e6" },
  ];

  const setTargetColor = (hex, pushRecent = true) => {
    const rgb = hexToRgb(hex);
    if (!rgb) return;
    const fixed = rgbToHex(rgb.r, rgb.g, rgb.b);
    const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b);
    colorPicker.value = fixed;
    hexInput.value = fixed;
    rgbR.value = String(Math.round(rgb.r));
    rgbG.value = String(Math.round(rgb.g));
    rgbB.value = String(Math.round(rgb.b));
    hslH.value = String(Math.round(hsl.h));
    hslS.value = String(Math.round(hsl.s));
    hslL.value = String(Math.round(hsl.l));

    const targetId = targetSelect.value;
    const target = targets.find(t => t.id === targetId);
    if (target) target.set(fixed);
    if (targetInputs[targetId]) targetInputs[targetId].value = fixed;
    if (pushRecent) addRecent(fixed);
    api.requestRender();
  };

  const addRecent = (hex) => {
    pal._recentColors = Array.isArray(pal._recentColors) ? pal._recentColors : [];
    const list = pal._recentColors.filter(c => c.toLowerCase() !== hex.toLowerCase());
    list.unshift(hex);
    pal._recentColors = list.slice(0, 12);
    renderRecent();
  };

  const renderRecent = () => {
    recentGrid.innerHTML = "";
    const list = Array.isArray(pal._recentColors) ? pal._recentColors : [];
    list.forEach((hex) => {
      const s = document.createElement("div");
      s.className = "swatch";
      s.style.background = hex;
      s.title = hex;
      s.addEventListener("click", () => setTargetColor(hex, false));
      recentGrid.appendChild(s);
    });
  };

  swatches.forEach((sw) => {
    const s = document.createElement("div");
    s.className = "swatch";
    s.style.background = sw.hex;
    s.title = `${sw.name} ${sw.hex}`;
    s.addEventListener("click", () => setTargetColor(sw.hex));
    swatchGrid.appendChild(s);
  });

  const syncTargetFromSelect = () => {
    const target = targets.find(t => t.id === targetSelect.value);
    if (!target) return;
    setTargetColor(target.get(), false);
  };
  targetSelect.addEventListener("change", syncTargetFromSelect);

  Object.entries(targetInputs).forEach(([id, inp]) => {
    if (!inp) return;
    const activate = () => {
      targetSelect.value = id;
      syncTargetFromSelect();
    };
    inp.addEventListener("focus", activate);
    inp.addEventListener("click", activate);
  });

  colorPicker.addEventListener("input", () => setTargetColor(colorPicker.value));
  hexInput.addEventListener("input", () => {
    const rgb = hexToRgb(hexInput.value);
    if (rgb) setTargetColor(hexInput.value);
  });
  const applyRgb = () => {
    const r = clamp(Number(rgbR.value), 0, 255);
    const g = clamp(Number(rgbG.value), 0, 255);
    const b = clamp(Number(rgbB.value), 0, 255);
    setTargetColor(rgbToHex(r, g, b));
  };
  [rgbR, rgbG, rgbB].forEach((el) => el.addEventListener("input", applyRgb));
  const applyHsl = () => {
    const h = clamp(Number(hslH.value), 0, 360);
    const s = clamp(Number(hslS.value), 0, 100);
    const l = clamp(Number(hslL.value), 0, 100);
    const rgb = hslToRgb(h, s, l);
    setTargetColor(rgbToHex(rgb.r, rgb.g, rgb.b));
  };
  [hslH, hslS, hslL].forEach((el) => el.addEventListener("input", applyHsl));

  // init
  setTargetColor(targets[0].get(), false);
  renderRecent();

  uiNumber({
    root, label: "Hue shift (deg)",
    value: th.hueShift ?? 0, min: -180, max: 180, step: 1,
    onChange: (v) => { th.hueShift = v; api.requestRender(); }
  });
  uiNumber({
    root, label: "Saturation scale",
    value: th.saturationScale ?? 1, min: 0, max: 3, step: 0.05,
    onChange: (v) => { th.saturationScale = v; api.requestRender(); }
  });
  uiNumber({
    root, label: "Brightness scale",
    value: th.brightnessScale ?? 1, min: 0, max: 3, step: 0.05,
    onChange: (v) => { th.brightnessScale = v; api.requestRender(); }
  });
  uiNumber({
    root, label: "Contrast",
    value: th.contrast ?? 1, min: 0, max: 3, step: 0.05,
    onChange: (v) => { th.contrast = v; api.requestRender(); }
  });

  // --- Render ---
  uiSelect({
    root, label: "Antialias",
    value: String(rr.antialias ?? true),
    options: [{ value: "true", label: "true" }, { value: "false", label: "false" }],
    onChange: (v) => { rr.antialias = (v === "true"); api.requestRender(); }
  });
  uiSelect({
    root, label: "Stroke",
    value: String(rr.strokeEnabled ?? false),
    options: [{ value: "false", label: "false" }, { value: "true", label: "true" }],
    onChange: (v) => { rr.strokeEnabled = (v === "true"); api.requestRender(); }
  });
  uiText({
    root, label: "Stroke color",
    value: rr.strokeColor ?? "#000000",
    placeholder: "#000000",
    onChange: (v) => { rr.strokeColor = v.trim() || "#000000"; api.requestRender(); }
  });
  uiNumber({
    root, label: "Stroke width",
    value: rr.strokeWidth ?? 1, min: 0, max: 20, step: 1,
    onChange: (v) => { rr.strokeWidth = v; api.requestRender(); }
  });

  return () => {};
}

export function render({ ctxMain, ctxTile, state, common }) {
  const cfg = state.cfg ?? manifest.defaults.cfg;

  // Draw tile (pattern preview)
  drawYagasuri(ctxTile, cfg, ctxTile.canvas.width, ctxTile.canvas.height, common);

  // Draw main (cover)
  drawYagasuri(ctxMain, cfg, ctxMain.canvas.width, ctxMain.canvas.height, common);
}
