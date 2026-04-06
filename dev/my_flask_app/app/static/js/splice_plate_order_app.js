// splice_plate_order_app.js
// スプライスプレート製作指示書 用の基本JS

console.log("✅ splice_plate_order_app.js loaded");

// ============================================================
// Globals / Flags / Constants
// ============================================================

const SVG_NS = "http://www.w3.org/2000/svg";
const DRAW_STROKE_MM = 0.4;

// Draw root move state (viewBox mm)
let DRAW_ROOT = null;
const DRAW_ROOT_STATE = {
  offsetX: 0,
  offsetY: 0,
  viewW: 420,
  viewH: 210,
};

const DRAG_MODE = {
  OFF: "off",
  ALL: "all",
  SPLIT: "split",
  FLANGE: "flange",
  PLATES: "plates",
};

let dragMode = DRAG_MODE.ALL;
let activeDragTargetKey = "root";

const DRAG_GROUP_STATE = {
  h:      { offsetX: 0, offsetY: 0 },
  plates: { offsetX: 0, offsetY: 0 },
  flange: { offsetX: 0, offsetY: 0 },
  outer:  { offsetX: 0, offsetY: 0 },
  inner:  { offsetX: 0, offsetY: 0 },
  web:    { offsetX: 0, offsetY: 0 },
};

const DRAG_SESSION = {
  dragging: false,
  key: "root",
  startClientX: 0,
  startClientY: 0,
  startOffsetX: 0,
  startOffsetY: 0,
  lockAxis: null,
  moved: false,
};

const SNAP_CFG = {
  tol: 2,             // mm
  guideColor: "#0a84ff",
  guideWidth: 0.4,
  guideDash: "2 2",
};

let DRAG_GEOM = null;

function getDragSessionId() {
  try {
    let sid = sessionStorage.getItem("splice_drag_session_id");
    if (!sid) {
      sid = `sess_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
      sessionStorage.setItem("splice_drag_session_id", sid);
    }
    return sid;
  } catch (_) {
    return "sess_fallback";
  }
}

function getDragStoreKey() {
  const profileKey = document.body?.dataset?.profileKey || "";
  const sessionId = document.body?.dataset?.dragSessionId || getDragSessionId();
  return `splice_plate_drag_state::${location.pathname}::${profileKey}::${sessionId}`;
}

// プリセット自動適用ON/OFF（デフォルトON）
let autoPresetEnabled = true;

// 孔芯十字線ON/OFF（デフォルトOFF）
let holeCenterCrossEnabled = false;

// スプライスプレート長さ計算用の仮デフォルト（mm）
const DEFAULT_SP_END_PITCH_MM = 40; // 切端～最初孔芯の終端孔ピッチ
const DEFAULT_SP_CLEARANCE_MM = 10; // 柱ブラケットと大梁のクリアランス

// 寸法段組み（1段目=ピッチ、2段目=全長）
const DIM_ROW_GAP_MM = 10;                  // 1段目と2段目の段間
const DIM_OFFSET_PITCH_MM = 14;             // 部材からピッチ寸法線まで
const DIM_OFFSET_TOTAL_MM = DIM_OFFSET_PITCH_MM + DIM_ROW_GAP_MM; // 全長寸法線

// ============================================================
// Layout gap constants (viewBox mm)
// ============================================================

// Topline → gFlange（外プレート原点まで）のギャップ（※縮む）
const GAP_TOPLINE_TO_GFLANGE_DRAW = 2;

// gOuter ↔ gInner のギャップ（※縮む）
const GAP_GOUTER_GINNER_DRAW = 6;

// gFlange ↔ gWeb のギャップ（※縮む）
const GAP_GFLANGE_GWEB_DRAW = 6;

// gWeb → Bottomline のギャップ（※縮む）
const GAP_GWEB_TO_BOTTOMLINE_DRAW = 2;

// 余り高さを上下に等分配
const AUTO_CENTER_Y = true;

// ============================================================
// DOM Helpers / Read helpers
// ============================================================

function qs(sel, ctx = document) {
  return ctx.querySelector(sel);
}
function qsa(sel, ctx = document) {
  return ctx.querySelectorAll(sel);
}

function readNumberOrNaN(sel) {
  const el = qs(sel);
  if (!el) return NaN;
  const t = (el.value || "").trim();
  if (!t) return NaN;
  const v = Number(t);
  return Number.isFinite(v) ? v : NaN;
}

function firstFiniteNumber(...vals) {
  for (const v of vals) {
    const n = Number(v);
    if (Number.isFinite(n) && n > 0) return n;
  }
  return NaN;
}

// ============================================================
// Parse / Format helpers
// ============================================================

function parseDiaMmFromText(raw) {
  if (!raw) return NaN;
  const normalized = String(raw).trim().replace(/[０-９]/g, ch =>
    String.fromCharCode(ch.charCodeAt(0) - 0xFEE0)
  );
  const m = normalized.match(/([0-9]+(?:\.[0-9]+)?)/);
  if (!m) return NaN;
  const v = Number(m[1]);
  return (Number.isFinite(v) && v > 0) ? v : NaN;
}

function parsePlateSpec3(raw) {
  // "t×H×L" / "t x H x L" / "t*H*L" などから数値を最大3つ拾う
  if (!raw) return null;

  const normalized = String(raw)
    .replace(/[０-９]/g, ch => String.fromCharCode(ch.charCodeAt(0) - 0xFEE0))
    .replace(/×/g, "x")
    .replace(/X/g, "x");

  const nums = normalized.match(/[0-9]+(?:\.[0-9]+)?/g)?.map(Number) || [];
  if (nums.length < 2) return null;
  return { t: nums[0], h: nums[1], l: nums[2] ?? null };
}

function fmtMmInt(v) {
  if (!Number.isFinite(v)) return "";
  return String(Math.round(v));
}

// "12x410x200" / "12×410×200" などから板厚(t)だけ抜く
function getThicknessMmFromSpecText(specText) {
  if (!specText) return NaN;

  const normalized = String(specText)
    .trim()
    .replace(/[０-９]/g, ch => String.fromCharCode(ch.charCodeAt(0) - 0xFEE0));

  const m = normalized.match(/([0-9]+(?:\.[0-9]+)?)/);
  if (!m) return NaN;

  const t = Number(m[1]);
  return (Number.isFinite(t) && t > 0) ? t : NaN;
}

// t×a×b を作る（a,bはmm値）
function buildPlateSpec3(tMm, aMm, bMm) {
  if (!Number.isFinite(tMm) || tMm <= 0) return "";
  const a = fmtMmInt(aMm);
  const b = fmtMmInt(bMm);
  if (!a || !b) return "";
  // preset 表記が "x" なので合わせる
  return `${tMm}x${a}x${b}`;
}

// ============================================================
// Auto-set helpers（手入力尊重）
// ============================================================

// 自動生成の上書き（空欄 or 前回自動生成と同じ値なら更新）
function setAutoSpecValue(inputEl, newValue) {
  if (!inputEl) return;

  const next = String(newValue ?? "").trim();
  if (next === "") return;

  const cur = String(inputEl.value || "").trim();

  // 初回：サーバ初期値を autoSpec とみなして刻む（初期値でブロックされる問題対策）
  if (!inputEl.dataset.autoSpec && cur !== "") {
    inputEl.dataset.autoSpec = cur;
  }

  const last = String(inputEl.dataset.autoSpec || "").trim();

  // ユーザーが手入力で変えた場合は更新しない
  if (cur !== "" && cur !== last) return;

  inputEl.value = next;
  inputEl.dataset.autoSpec = next;
}

function setAutoValue(inputEl, newValue) {
  if (!inputEl) return;

  const nv = String(newValue ?? "").trim();
  if (nv === "") return;

  const cur = String(inputEl.value || "").trim();

  // autoVal に統一（後方互換で autoValue も読む）
  const last = String(inputEl.dataset.autoVal || inputEl.dataset.autoValue || "").trim();

  // 初回：サーバ初期値を autoVal とみなして刻む
  if (!inputEl.dataset.autoVal && cur !== "") {
    inputEl.dataset.autoVal = cur;
  }

  // 手入力尊重
  if (cur !== "" && cur !== last) return;

  inputEl.value = nv;

  // 両方に刻んで後方互換
  inputEl.dataset.autoVal = nv;
  inputEl.dataset.autoValue = nv;
}

// id指定版（共通欄など）
function setAutoValueById(id, newValue) {
  const el = document.getElementById(id);
  if (!el) {
    console.warn("[splice] setAutoValueById: element not found:", id);
    return;
  }

  const next = (newValue == null) ? "" : String(newValue).trim();
  if (next === "") return;

  const cur = String(el.value || "").trim();

  // 初回：サーバ初期値を autoVal とみなして刻む
  if (!el.dataset.autoVal && cur !== "") {
    el.dataset.autoVal = cur;
  }

  const last = String(el.dataset.autoVal || "").trim();

  // 手入力尊重
  if (cur !== "" && cur !== last) return;

  el.value = next;
  el.dataset.autoVal = next;
}

// 初期表示値を「自動値」として刻む（必要時に呼ぶ）
function markInitialAutoValById(id) {
  const el = document.getElementById(id);
  if (!el) return;

  const cur = String(el.value || "").trim();
  if (cur === "") return;

  if (!el.dataset.autoVal) {
    el.dataset.autoVal = cur;
  }
}

function markInitialAutoSpecByRow(tr) {
  [
    'input[name="flange_plate_outer[]"]',
    'input[name="flange_plate[]"]',           // 旧名互換
    'input[name="flange_plate_inner[]"]',
    'input[name="web_plate[]"]',
  ].forEach(sel => {
    const el = tr.querySelector(sel);
    if (!el) return;
    const cur = String(el.value || "").trim();
    if (cur === "") return;
    if (!el.dataset.autoSpec) el.dataset.autoSpec = cur;
  });
}

// ============================================================
// Preset access helper
// ============================================================

function getSplicePresets() {
  return (window.SPLICE_PRESETS || {});
}

// ============================================================
// Hole setting helpers
// ============================================================

function readWebHoleSettingsFallback(flangeSettings) {
  const webEndPitchMm     = readNumberOrNaN("#sp-common-web-end-pitch-mm");
  const webspXEndPitchMm  = readNumberOrNaN("#sp-common-websp-x-end-pitch-mm");
  const webspYEndPitchMm  = readNumberOrNaN("#sp-common-websp-y-end-pitch-mm");

  const webColPitchMm  = readNumberOrNaN("#sp-web-col-pitch-mm");
  const webHoleCountX  = readNumberOrNaN("#sp-web-hole-count-x");
  const webRowPitchMm  = readNumberOrNaN("#sp-web-row-pitch-mm");
  const webHoleCountY  = readNumberOrNaN("#sp-web-hole-count-y");
  const webDiaMmRaw    = parseDiaMmFromText(qs("#sp-web-hole-dia-mm")?.value);

  // ウェブ孔径：ウェブ欄が入っていればそれ、無ければ flangeSettings.holeDiaMm にフォールバック
  const holeDiaMm = Number.isFinite(webDiaMmRaw) ? webDiaMmRaw : flangeSettings.holeDiaMm;

  return {
    webEndPitchMm:    Number.isFinite(webEndPitchMm)    ? webEndPitchMm    : flangeSettings.endPitchMm,
    webspXEndPitchMm: Number.isFinite(webspXEndPitchMm) ? webspXEndPitchMm : flangeSettings.endPitchMm,
    webspYEndPitchMm: Number.isFinite(webspYEndPitchMm) ? webspYEndPitchMm : flangeSettings.endPitchMm,

    colPitchMm:  Number.isFinite(webColPitchMm) ? webColPitchMm : flangeSettings.colPitchMm,
    holeCountX:  Number.isFinite(webHoleCountX) ? webHoleCountX : flangeSettings.holeCountX,
    rowPitchMm:  Number.isFinite(webRowPitchMm) ? webRowPitchMm : flangeSettings.rowPitchMm,
    holeCountY:  Number.isFinite(webHoleCountY) ? webHoleCountY : flangeSettings.holeCountY,

    holeDiaMm,
  };
}

// ============================================================
// Hole grid text helpers (auto-fill per row)
// ============================================================

function formatHoleGridCount(v) {
  if (!Number.isFinite(v)) return "";
  return String(Math.round(v));
}

function buildHoleGridTotal(countX, countY) {
  if (!Number.isFinite(countX) || !Number.isFinite(countY)) return "";
  if (countX < 0 || countY < 0) return "";
  const total = countX * countY;
  return formatHoleGridCount(total);
}

function updateHoleGridInputs() {
  const tbody = getSpRowsTbody();
  if (!tbody) return;

  const flangeX = readNumberOrNaN("#sp-flange-hole-count-x");
  const flangeY = readNumberOrNaN("#sp-flange-hole-count-y");
  const webX    = readNumberOrNaN("#sp-web-hole-count-x");
  const webY    = readNumberOrNaN("#sp-web-hole-count-y");

  function doubleAndInt(text) {
    const v = Number(text);
    if (!Number.isFinite(v)) return "";
    return String(Math.round(v * 2));
  }

  const outerText = doubleAndInt(buildHoleGridTotal(flangeX, flangeY));
  const innerText = doubleAndInt(buildHoleGridTotal(flangeX, Number.isFinite(flangeY) ? flangeY / 2 : NaN));
  const webText   = doubleAndInt(buildHoleGridTotal(webX, webY));

  qsa("tr", tbody).forEach(tr => {
    setAutoValue(tr.querySelector('input[name="flange_holes_outer[]"]'), outerText);
    setAutoValue(tr.querySelector('input[name="flange_holes_inner[]"]'), innerText);
    setAutoValue(tr.querySelector('input[name="web_holes[]"]'), webText);
  });
}

// ============================================================
// Dimension config / helpers
// ============================================================

const DIM_CFG_DEFAULT = {
  enabled: true,
  scaleWithPlate: true, // true: plateScaleに合わせて寸法も縮む
  strictTier: true,     // true: 枠内優先のために段位置を動かさない

  gapFromObjMm: 5,      // 寸法補助線：プレート外形から離す距離
  extLineLenMm: 50,     // 寸法補助線の長さ（上/左方向）
  textGapMm: 2,         // 寸法線と文字（文字の下端）との離れ
  // 枠線から離す距離（draw mm）
  frameGapMm: 6,
  // ラベル見積りの追加余白（draw mm）
  labelSafePadMm: 3,

  endDotRadiusMm: 1.2,  // 寸法線端部の●

  strokeWidthMm: 0.4,
  fontSizeMm: 4,

  // 見えなくなるのを防ぐ下限
  minStroke: 0.4,
  minFontSize: 2.5
};

const DIM_Y_CFG = {
  enabled: true,
  scaleWithPlate: true,

  gapFromObjMm: 5,
  extLineLenMm: 50,
  textGapMm: 2,

  endDotRadiusMm: 1.2,
  strokeWidthMm: 0.4,
  fontSizeMm: 4,

  minStroke: 0.4,
  minFontSize: 2.5,
};

function getDimCfg() {
  // 将来：body.dataset から読むなどに置き換え可能
  const cfg = { ...DIM_CFG_DEFAULT };
  const fontMm = readNumberOrNaN("#sp-dim-font-mm");
  if (Number.isFinite(fontMm) && fontMm > 0) {
    cfg.fontSizeMm = fontMm;
  }
  return cfg;
}

function getDimYCfg() {
  const base = getDimCfg();
  return {
    ...DIM_Y_CFG,
    fontSizeMm: base.fontSizeMm,
    minFontSize: base.minFontSize,
  };
}

// ============================================================
// Dimension extents helper (scale/layout uses)
// ============================================================

// tier2（2段目）まで含めた「上/左にどれだけ必要か（mm）」の安全見積り
// ※ scaleWithPlate=true 前提。true なら plateScale 倍される
function estimateDimExtraMm(cfg, tier2Mm) {
  if (!cfg?.enabled) return 0;

  const gap    = Number(cfg.gapFromObjMm || 0);     // 補助線開始まで
  const tier2  = Number(tier2Mm || 0);             // tier2 距離
  const fs     = Number(cfg.fontSizeMm || 0);       // 文字サイズ
  const dotR   = Number(cfg.endDotRadiusMm || 0);
  const sw     = Number(cfg.strokeWidthMm || 0);
  const frameGap = Number(cfg.frameGapMm || 0);
  const labelPad = Number(cfg.labelSafePadMm || 0);
  const tGap   = Number(cfg.textGapMm || 0);        // 文字の離れ

  // 文字高さは安全側で 1.4em。ラベル余白と枠線離れも加味する
  const textUp = tGap + fs * 1.4 + labelPad;
  return gap + tier2 + textUp + frameGap + dotR + sw * 2;
}

// X寸法（上側）の「補助線開始Y（ローカル）」＝ yObjLocal - gap
function calcExtStartLocalY_ForDimX(yObjLocal, plateScale, cfg) {
  const s = cfg.scaleWithPlate ? (plateScale || 1) : 1;
  return yObjLocal - (cfg.gapFromObjMm || 0) * s;
}

// Y寸法（左側）の「補助線開始X（ローカル）」＝ xObjLocal - gap
function calcExtStartLocalX_ForDimY(xObjLocal, plateScale, cfg) {
  const s = cfg.scaleWithPlate ? (plateScale || 1) : 1;
  return xObjLocal - (cfg.gapFromObjMm || 0) * s;
}

// ============================================================
// Dimension tier offsets (UI-driven)
// ============================================================

const DIM_TIER1_CHOICES_MM = [25, 50, 75, 100];

function readDimTier1Mm() {
  const v = readNumberOrNaN("#sp-dim-tier1-mm");
  if (Number.isFinite(v) && DIM_TIER1_CHOICES_MM.includes(Math.round(v))) {
    return Math.round(v);
  }
  return 50; // デフォルト
}

function readDimTier2Denom() {
  const el = qs("#sp-dim-tier2-denom");
  const n = el ? parseInt(el.value, 10) : NaN;
  if (Number.isInteger(n) && n >= 1 && n <= 5) return n;
  return 1; // デフォルト 1/1
}

/**
 * 1段目：tier1Mm
 * 段間：tier1Mm / denom
 * 2段目の追加距離：tier1Mm + (tier1Mm/denom)
 */
function getDimTierOffsetsMm() {
  const tier1 = readDimTier1Mm();
  const denom = readDimTier2Denom();
  const gap   = tier1 / denom;
  const tier2 = tier1 + gap;
  return { tier1, tier2, gap, denom };
}

// ============================================================
// Dimension tier offsets (X/Y 共通化)
// ============================================================

// 2段まとめて clamp して、同じ delta を両段に足す（Y位置版）
function clampTwoTierLocalY(y1, y2, plateGlobalY, marginMm) {
  const minGlobal = plateGlobalY + Math.min(y1, y2);
  const delta = (Number.isFinite(marginMm) && minGlobal < marginMm) ? (marginMm - minGlobal) : 0;
  return { v1: y1 + delta, v2: y2 + delta, delta };
}

// 2段まとめて clamp（X位置版）
function clampTwoTierLocalX(x1, x2, plateGlobalX, marginMm) {
  const minGlobal = plateGlobalX + Math.min(x1, x2);
  const delta = (Number.isFinite(marginMm) && minGlobal < marginMm) ? (marginMm - minGlobal) : 0;
  return { v1: x1 + delta, v2: x2 + delta, delta };
}

// X方向寸法（上側）：2段のローカルYを作る
function getTwoTierYLocalForDimX(plateScale, cfg) {
  const off = getDimTierOffsetsMm();
  const y1 = calcDimLineYLocal_X(0, plateScale, cfg, off.tier1);
  const y2 = calcDimLineYLocal_X(0, plateScale, cfg, off.tier2);
  return { y1, y2 };
}

// Y方向寸法（左側）：2段のローカルXを作る
function getTwoTierXLocalForDimY(plateScale, cfg) {
  const off = getDimTierOffsetsMm();
  const x1 = calcDimLineXLocal_Y(0, plateScale, cfg, off.tier1);
  const x2 = calcDimLineXLocal_Y(0, plateScale, cfg, off.tier2);
  return { x1, x2 };
}

// X方向寸法線のY位置（ローカル座標）
// ★補助線開始位置から tierMm だけ離す（距離 = tierMm * plateScale）
function calcDimLineYLocal_X(yObjLocal, plateScale, cfg, tierMm = 0) {
  const s = cfg.scaleWithPlate ? (plateScale || 1) : 1;
  const gap = (cfg.gapFromObjMm || 0) * s;
  const off = (Number(tierMm) || 0) * s;

  const yExtStart = yObjLocal - gap;     // 補助線開始位置
  return yExtStart - off;                // ★ここが仕様（tierだけ）
}

// Y方向寸法線のX位置（ローカル座標）
// ★補助線開始位置から tierMm だけ離す（距離 = tierMm * plateScale）
function calcDimLineXLocal_Y(xObjLocal, plateScale, cfg, tierMm = 0) {
  const s = cfg.scaleWithPlate ? (plateScale || 1) : 1;
  const gap = (cfg.gapFromObjMm || 0) * s;
  const off = (Number(tierMm) || 0) * s;

  const xExtStart = xObjLocal - gap;     // 補助線開始位置
  return xExtStart - off;                // ★ここが仕様（tierだけ）
}

// 寸法文字が「寸法線よりどれだけ上に出るか」を見積もる（draw座標）
function getDimTextUpDraw(cfg, plateScale) {
  if (!cfg) return 0;
  const s = cfg.scaleWithPlate ? (plateScale || 1) : 1;

  const tGap = (cfg.textGapMm || 0) * s;

  const fs0 = (cfg.fontSizeMm || 0) * s;
  const fontSz = Math.max(cfg.minFontSize ?? 0, fs0);

  // 文字高さは安全側で 1.4em（少し大きめ）
  const textH = fontSz * 1.4;

  // ラベルが枠に近いと感じる場合の “追加余白”(draw mm)
  const extra = (cfg.labelSafePadMm ?? 2);  // ★ここを 3〜5 にするともっと離れる

  return tGap + textH + extra;
}

// X方向寸法（上側）2段のYを「文字上端が枠内」かつ「枠から一定距離」に入るようにクランプ
function clampTwoTierLocalY_ForDimX_Text(y1, y2, plateGlobalY, marginMm, plateScale, cfg) {
  if (cfg?.strictTier) {
    // 配置の「段位置」を動かさない（優先順位: 枠内 > 寸法位置 > スケール）
    return { v1: y1, v2: y2, delta: 0 };
  }

  const textUp = getDimTextUpDraw(cfg, plateScale);

  // ★枠線から必ず離したい距離（draw mm）
  const frameGap = (cfg?.frameGapMm ?? 3); // ★ここを 5〜8 にすると“はっきり”離れる

  // 文字上端（最も上に来る点）で判定
  const minTextGlobal = plateGlobalY + Math.min(y1, y2) - textUp;

  // ★判定ラインを margin ではなく margin + frameGap にする
  const targetTop = (Number.isFinite(marginMm) ? (marginMm + frameGap) : frameGap);

  const delta = (minTextGlobal < targetTop) ? (targetTop - minTextGlobal) : 0;

  return { v1: y1 + delta, v2: y2 + delta, delta };
}

// X方向のチェーン寸法（上側）
function drawDimChainX(
  g, yObjLocal, xMarksMm, labels,
  plateScale, plateOuterY, marginMm, cfg,
  extraOffsetMm = 0,
  yDimLocalOverride = null,

  // ★追加：補助線の開始/終点を上書き（ローカル座標）
  yExtStartLocalOverride = null,
  yExtEndLocalOverride   = null
) {
  if (!g || !cfg?.enabled) return;
  if (!Array.isArray(xMarksMm) || xMarksMm.length < 2) return;

  const s = cfg.scaleWithPlate ? (plateScale || 1) : 1;

  const gap   = (cfg.gapFromObjMm   || 0) * s;
  const extL  = (cfg.extLineLenMm   || 0) * s;
  const tGap  = (cfg.textGapMm      || 0) * s;

  const fs0   = (cfg.fontSizeMm     || 4)   * s;
  const strokeW = DRAW_STROKE_MM;
  const fontSz  = Math.max(cfg.minFontSize ?? 0, fs0);

  const dotR  = (cfg.endDotRadiusMm || 1.2) * s;

  // override があればそれを採用
  let yDimLocal = Number.isFinite(yDimLocalOverride)
    ? yDimLocalOverride
    : (yObjLocal - (gap + extL) - (Number(extraOffsetMm) || 0));

  if (!Number.isFinite(yDimLocalOverride)) {
    const yDimGlobal = plateOuterY + yDimLocal;
    if (Number.isFinite(marginMm) && yDimGlobal < marginMm) {
      yDimLocal += (marginMm - yDimGlobal);
    }
  }

  const xMarks = xMarksMm.map(x => x * plateScale);

  // ★補助線：開始/終点を上書きできるようにする
  const yExtStart = Number.isFinite(yExtStartLocalOverride)
    ? yExtStartLocalOverride
    : (yObjLocal - gap);

  const yExtEnd = Number.isFinite(yExtEndLocalOverride)
    ? yExtEndLocalOverride
    : yDimLocal;

  function addLine(x1, y1, x2, y2) {
    const ln = document.createElementNS(SVG_NS, "line");
    ln.setAttribute("x1", String(x1));
    ln.setAttribute("y1", String(y1));
    ln.setAttribute("x2", String(x2));
    ln.setAttribute("y2", String(y2));
    ln.setAttribute("stroke", "#000");
    ln.setAttribute("stroke-width", String(strokeW));
    g.appendChild(ln);
  }

  function addCircle(cx, cy, r) {
    const c = document.createElementNS(SVG_NS, "circle");
    c.setAttribute("cx", String(cx));
    c.setAttribute("cy", String(cy));
    c.setAttribute("r",  String(r));
    c.setAttribute("fill", "#000");
    c.setAttribute("stroke", "none");
    g.appendChild(c);
  }

  function addText(x, y, txt) {
    const t = document.createElementNS(SVG_NS, "text");
    t.setAttribute("x", String(x));
    t.setAttribute("y", String(y));
    t.setAttribute("text-anchor", "middle");
    t.setAttribute("dominant-baseline", "text-after-edge");
    t.setAttribute("font-size", String(fontSz));
    t.textContent = txt;
    g.appendChild(t);
  }

  const dotCache = new Set();
  function addDotOnce(x, y) {
    const key = `${x.toFixed(3)},${y.toFixed(3)}`;
    if (dotCache.has(key)) return;
    dotCache.add(key);
    addCircle(x, y, dotR);
  }

  // 1) ★補助線（ここが2段対応ポイント）
  xMarks.forEach(x => addLine(x, yExtStart, x, yExtEnd));

  // 2) 寸法線
  for (let i = 0; i < xMarks.length - 1; i++) {
    const xa = xMarks[i];
    const xb = xMarks[i + 1];
    addLine(xa, yDimLocal, xb, yDimLocal);
    addDotOnce(xa, yDimLocal);
    addDotOnce(xb, yDimLocal);
  }

  // 3) 寸法文字
  const segCount = xMarks.length - 1;
  const nLabel = Math.min(segCount, Array.isArray(labels) ? labels.length : 0);

  for (let i = 0; i < nLabel; i++) {
    const xa = xMarks[i];
    const xb = xMarks[i + 1];
    const xm = (xa + xb) / 2;
    addText(xm, yDimLocal - tGap, String(labels[i]));
  }
}

function drawDimChainY(
  g, xObjLocal, yMarksMm, labels,
  plateScale, plateOuterX, marginMm, cfg,
  extraOffsetMm = 0,
  xDimLocalOverride = null,

  // ★追加
  xExtStartLocalOverride = null,
  xExtEndLocalOverride   = null
) {
  if (!g || !cfg?.enabled) return;
  if (!Array.isArray(yMarksMm) || yMarksMm.length < 2) return;

  const s = cfg.scaleWithPlate ? (plateScale || 1) : 1;

  const gap   = (cfg.gapFromObjMm   || 0) * s;
  const extL  = (cfg.extLineLenMm   || 0) * s;
  const tGap  = (cfg.textGapMm      || 0) * s;

  const fs0   = (cfg.fontSizeMm     || 4)   * s;
  const strokeW = DRAW_STROKE_MM;
  const fontSz  = Math.max(cfg.minFontSize ?? 0, fs0);

  const dotR  = (cfg.endDotRadiusMm || 1.2) * s;

  let xDimLocal = Number.isFinite(xDimLocalOverride)
    ? xDimLocalOverride
    : (xObjLocal - (gap + extL) - (Number(extraOffsetMm) || 0));

  if (!Number.isFinite(xDimLocalOverride)) {
    const xDimGlobal = plateOuterX + xDimLocal;
    if (Number.isFinite(marginMm) && xDimGlobal < marginMm) {
      xDimLocal += (marginMm - xDimGlobal);
    }
  }

  const yMarks = yMarksMm.map(y => y * plateScale);

  const xExtStart = Number.isFinite(xExtStartLocalOverride)
    ? xExtStartLocalOverride
    : (xObjLocal - gap);

  const xExtEnd = Number.isFinite(xExtEndLocalOverride)
    ? xExtEndLocalOverride
    : xDimLocal;

  function addLine(x1, y1, x2, y2) {
    const ln = document.createElementNS(SVG_NS, "line");
    ln.setAttribute("x1", String(x1));
    ln.setAttribute("y1", String(y1));
    ln.setAttribute("x2", String(x2));
    ln.setAttribute("y2", String(y2));
    ln.setAttribute("stroke", "#000");
    ln.setAttribute("stroke-width", String(strokeW));
    g.appendChild(ln);
  }

  function addCircle(cx, cy, r) {
    const c = document.createElementNS(SVG_NS, "circle");
    c.setAttribute("cx", String(cx));
    c.setAttribute("cy", String(cy));
    c.setAttribute("r",  String(r));
    c.setAttribute("fill", "#000");
    c.setAttribute("stroke", "none");
    g.appendChild(c);
  }

  function addText(x, y, txt, rotateDeg = 0) {
    const t = document.createElementNS(SVG_NS, "text");
    t.setAttribute("x", String(x));
    t.setAttribute("y", String(y));
    t.setAttribute("text-anchor", "middle");

    if (rotateDeg === -90 || rotateDeg === 90) {
      t.setAttribute("dominant-baseline", "text-after-edge");
    } else {
      t.setAttribute("dominant-baseline", "central");
    }

    t.setAttribute("font-size", String(fontSz));

    if (rotateDeg) {
      t.setAttribute("transform", `rotate(${rotateDeg} ${x} ${y})`);
    }

    t.textContent = txt;
    g.appendChild(t);
  }

  const dotCache = new Set();
  function addDotOnce(x, y) {
    const key = `${x.toFixed(3)},${y.toFixed(3)}`;
    if (dotCache.has(key)) return;
    dotCache.add(key);
    addCircle(x, y, dotR);
  }

  // 1) ★補助線（2段対応）
  yMarks.forEach(y => addLine(xExtStart, y, xExtEnd, y));

  // 2) 寸法線
  for (let i = 0; i < yMarks.length - 1; i++) {
    const ya = yMarks[i];
    const yb = yMarks[i + 1];
    addLine(xDimLocal, ya, xDimLocal, yb);
    addDotOnce(xDimLocal, ya);
    addDotOnce(xDimLocal, yb);
  }

  // 3) 文字
  const segCount = yMarks.length - 1;
  const nLabel = Math.min(segCount, Array.isArray(labels) ? labels.length : 0);

  for (let i = 0; i < nLabel; i++) {
    const ya = yMarks[i];
    const yb = yMarks[i + 1];
    const ym = (ya + yb) / 2;
    addText(xDimLocal - tGap, ym, String(labels[i]), -90);
  }
}

// X方向の「1段目（終端+孔ピッチを1ピッチずつ）」チェーンを作る
function buildFlangeOuterXDimPitchMm(plEndPitchMm, colPitchMm, holeCountX, htEndPitchMm, clearanceMm) {
  const nX = Math.trunc(holeCountX);

  if (!(Number.isFinite(plEndPitchMm) && plEndPitchMm >= 0)) return null;
  if (!(Number.isFinite(htEndPitchMm) && htEndPitchMm >= 0)) return null;
  if (!(Number.isFinite(clearanceMm)  && clearanceMm  >= 0)) return null;
  if (!(Number.isFinite(nX) && nX >= 1)) return null;
  if (nX >= 2 && !(Number.isFinite(colPitchMm) && colPitchMm > 0)) return null;

  const marks = [];
  const labels = [];

  // 左PL切端 → 左最初孔
  marks.push(0);
  marks.push(plEndPitchMm);
  labels.push(Math.round(plEndPitchMm));

  // 左：孔間ピッチ（個別）
  if (nX >= 2) {
    for (let i = 1; i < nX; i++) {
      marks.push(plEndPitchMm + colPitchMm * i);
      labels.push(Math.round(colPitchMm));
    }
  }

  const lastLeftHole = plEndPitchMm + (nX > 1 ? colPitchMm * (nX - 1) : 0);

  // 中央：左最後孔 → 右最初孔（孔→孔）
  const holeToHoleMid = htEndPitchMm + clearanceMm + htEndPitchMm;

  const firstRightHole = lastLeftHole + holeToHoleMid;
  marks.push(firstRightHole);
  labels.push(Math.round(holeToHoleMid));

  // 右：孔間ピッチ（個別）
  if (nX >= 2) {
    for (let i = 1; i < nX; i++) {
      marks.push(firstRightHole + colPitchMm * i);
      labels.push(Math.round(colPitchMm));
    }
  }

  const lastRightHole = firstRightHole + (nX > 1 ? colPitchMm * (nX - 1) : 0);

  // 右最後孔 → 右PL切端
  const total = lastRightHole + plEndPitchMm;
  marks.push(total);
  labels.push(Math.round(plEndPitchMm));

  return { xMarksMm: marks, labels, totalMm: total };
}

// ============================================================
// Web plate size (mm) - compute ONCE and reuse for layout & draw
// ============================================================
function computeWebPlateSizeMm(webHole, webPlEndPitchMm, webHtEndPitchMm, webClearanceMm, fallbackLenMm, fallbackHeightMm) {
  // length
  let webPlateLengthMm = NaN;
  if (Number.isFinite(webHole?.colPitchMm) && webHole.colPitchMm > 0 &&
      Number.isFinite(webHole?.holeCountX) && webHole.holeCountX >= 1) {
    const nX = Math.trunc(webHole.holeCountX);
    const midSpanX = (nX > 1) ? webHole.colPitchMm * (nX - 1) : 0;
    const a = webPlEndPitchMm + midSpanX + webHtEndPitchMm;
    const b = webHtEndPitchMm + midSpanX + webPlEndPitchMm;
    webPlateLengthMm = a + webClearanceMm + b;
  } else {
    webPlateLengthMm = fallbackLenMm;
  }

  // height
  let webPlateHeightMm = NaN;
  if (Number.isFinite(webHole?.rowPitchMm) && webHole.rowPitchMm > 0 &&
      Number.isFinite(webHole?.holeCountY) && webHole.holeCountY >= 1) {
    const nY = Math.trunc(webHole.holeCountY);
    const spanY = (nY > 1) ? webHole.rowPitchMm * (nY - 1) : 0;
    webPlateHeightMm = webPlEndPitchMm + spanY + webPlEndPitchMm;
  } else {
    webPlateHeightMm = fallbackHeightMm;
  }

  return { webPlateLengthMm, webPlateHeightMm };
}

// Y方向の「1段目（終端+孔ピッチを1ピッチずつ）」チェーンを作る
function buildFlangeYDimPitchChainMm(plateWidthMm, rowPitchMm, holeCountY, edgePitchMm = null) {
  const B = Number(plateWidthMm);
  const nY = Math.trunc(holeCountY);

  if (!(Number.isFinite(B) && B > 0)) return null;
  if (!(Number.isFinite(nY) && nY >= 1)) return null;

  const edgeExplicit = Number(edgePitchMm);

  function labelOrBlank(v) {
    const n = Math.round(v);
    return n === 0 ? "" : String(n);
  }

  // nY=1：中央1列 → 終端ピッチがB/2を左右に表示
  if (nY === 1) {
    const e = (Number.isFinite(edgeExplicit) && edgeExplicit >= 0) ? edgeExplicit : (B / 2);
    return {
      yMarksMm: [0, e, B],
      labels: [labelOrBlank(e), labelOrBlank(B - e)],
    };
  }

  // nY>=2：終端 + ピッチ(個別) + 終端
  if (!(Number.isFinite(rowPitchMm) && rowPitchMm > 0)) return null;

  const spanY = rowPitchMm * (nY - 1);
  const edge = (Number.isFinite(edgeExplicit) && edgeExplicit >= 0)
    ? edgeExplicit
    : (B - spanY) / 2;

  if (!(Number.isFinite(edge) && edge >= 0)) return null;

  const yMarksMm = [0, edge];
  for (let j = 1; j < nY; j++) {
    yMarksMm.push(edge + rowPitchMm * j);
  }
  yMarksMm.push(B);

  // ラベル：まとめず “1ピッチずつ”
  const labels = [];
  labels.push(labelOrBlank(edge));
  for (let j = 0; j < nY - 1; j++) labels.push(labelOrBlank(rowPitchMm));
  labels.push(labelOrBlank(B - (edge + spanY)));

  return { yMarksMm, labels };
}

// 内フランジ（現状：中央1列孔前提）のY寸法チェーン（a/2, a/2）
function buildInnerPlateYDimPitchChainMm(innerPlateWidthMm) {
  const a = Number(innerPlateWidthMm);
  if (!(Number.isFinite(a) && a > 0)) return null;

  const e = a / 2;
  return {
    yMarksMm: [0, e, a],
    labels: [Math.round(e), Math.round(e)],
  };
}

// ============================================================
// SVG creation / init helpers
// ============================================================

function getSpRowsTbody() {
  return (
    document.querySelector("#sp-plate-rows") || // 旧
    document.querySelector("#sp-type-rows")     // 現在
  );
}

function createGroup(svg, id, x, y) {
  const g = document.createElementNS(SVG_NS, "g");
  if (id) g.setAttribute("id", id);
  g.setAttribute("transform", `translate(${x} ${y})`);
  svg.appendChild(g);
  return g;
}

function ensureDragGroup(parent, id, key) {
  let g = parent.querySelector(`#${id}`);
  if (!g) {
    g = createGroup(parent, id, 0, 0);
  }
  if (key) applyDragTransformForKey(key);
  return g;
}

function getDrawRoot(svg) {
  if (DRAW_ROOT && DRAW_ROOT.isConnected) return DRAW_ROOT;
  const found = svg.querySelector("#sp-draw-root");
  if (found) {
    DRAW_ROOT = found;
    return found;
  }
  const g = document.createElementNS(SVG_NS, "g");
  g.setAttribute("id", "sp-draw-root");
  g.setAttribute("transform", `translate(${DRAW_ROOT_STATE.offsetX} ${DRAW_ROOT_STATE.offsetY})`);
  svg.appendChild(g);
  DRAW_ROOT = g;
  return g;
}

function updateDrawRootTransform() {
  if (!DRAW_ROOT) return;
  DRAW_ROOT.setAttribute(
    "transform",
    `translate(${DRAW_ROOT_STATE.offsetX} ${DRAW_ROOT_STATE.offsetY})`
  );
}

function isDragEnabled() {
  return dragMode !== DRAG_MODE.OFF;
}

function isKeyAllowedForMode(key) {
  if (dragMode === DRAG_MODE.ALL) return key === "root";
  if (dragMode === DRAG_MODE.SPLIT) return key === "h" || key === "plates";
  if (dragMode === DRAG_MODE.FLANGE) return key === "h" || key === "flange" || key === "web";
  if (dragMode === DRAG_MODE.PLATES) {
    return key === "h" || key === "outer" || key === "inner" || key === "web";
  }
  return false;
}

function getDefaultKeyForMode() {
  if (dragMode === DRAG_MODE.ALL) return "root";
  if (dragMode === DRAG_MODE.SPLIT) return "plates";
  if (dragMode === DRAG_MODE.FLANGE) return "flange";
  if (dragMode === DRAG_MODE.PLATES) return "outer";
  return null;
}

function getDragStateForKey(key) {
  if (key === "root") return DRAW_ROOT_STATE;
  return DRAG_GROUP_STATE[key] || null;
}

function getDragGroupNode(key) {
  const svg = qs("#sp-drawing-svg");
  if (!svg) return null;
  switch (key) {
    case "root":   return svg.querySelector("#sp-draw-root");
    case "h":      return svg.querySelector("#sp-draw-h");
    case "plates": return svg.querySelector("#sp-draw-plates");
    case "flange": return svg.querySelector("#sp-drag-flange");
    case "outer":  return svg.querySelector("#sp-drag-outer");
    case "inner":  return svg.querySelector("#sp-drag-inner");
    case "web":    return svg.querySelector("#sp-drag-web");
    default: return null;
  }
}

function applyDragTransformForKey(key) {
  if (key === "root") {
    updateDrawRootTransform();
    return;
  }
  const node = getDragGroupNode(key);
  const st = getDragStateForKey(key);
  if (!node || !st) return;
  node.setAttribute("transform", `translate(${st.offsetX} ${st.offsetY})`);
}

function applyAllDragTransforms() {
  ["root", "h", "plates", "flange", "outer", "inner", "web"].forEach((key) => {
    applyDragTransformForKey(key);
  });
}

function resetDragOffsetsToDefault() {
  DRAW_ROOT_STATE.offsetX = 0;
  DRAW_ROOT_STATE.offsetY = 0;
  DRAG_GROUP_STATE.h.offsetX = 0;
  DRAG_GROUP_STATE.h.offsetY = 0;
  DRAG_GROUP_STATE.plates.offsetX = 0;
  DRAG_GROUP_STATE.plates.offsetY = 0;
  DRAG_GROUP_STATE.flange.offsetX = 0;
  DRAG_GROUP_STATE.flange.offsetY = 0;
  DRAG_GROUP_STATE.outer.offsetX = 0;
  DRAG_GROUP_STATE.outer.offsetY = 0;
  DRAG_GROUP_STATE.inner.offsetX = 0;
  DRAG_GROUP_STATE.inner.offsetY = 0;
  DRAG_GROUP_STATE.web.offsetX = 0;
  DRAG_GROUP_STATE.web.offsetY = 0;
}

function saveDragStateToStorage() {
  try {
    const payload = {
      root: { ...DRAW_ROOT_STATE },
      groups: {
        h: { ...DRAG_GROUP_STATE.h },
        plates: { ...DRAG_GROUP_STATE.plates },
        flange: { ...DRAG_GROUP_STATE.flange },
        outer: { ...DRAG_GROUP_STATE.outer },
        inner: { ...DRAG_GROUP_STATE.inner },
        web: { ...DRAG_GROUP_STATE.web },
      },
      ts: Date.now(),
    };
    localStorage.setItem(getDragStoreKey(), JSON.stringify(payload));
  } catch (err) {
    console.warn("[splice] saveDragStateToStorage failed:", err);
  }
}

function loadDragStateFromStorage(opts = {}) {
  try {
    const key = getDragStoreKey();
    let raw = localStorage.getItem(key);

    if (!raw && opts.allowFallback) {
      // 旧キー（クエリ込み）
      const legacyExact = `splice_plate_drag_state::${location.pathname}${location.search}`;
      raw = localStorage.getItem(legacyExact);
    }

    if (!raw && opts.allowFallback) {
      // 旧キー互換: pathname だけ一致するものを拾う（同一セッション内の移行用）
      const path = location.pathname || "";
      const pathNoSlash = path.endsWith("/") ? path.slice(0, -1) : path;
      const prefixes = [
        `splice_plate_drag_state::${path}`,
        `splice_plate_drag_state::${pathNoSlash}`,
      ];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (!k) continue;
        if (!prefixes.some(p => k.startsWith(p))) continue;
        try {
          const v = JSON.parse(localStorage.getItem(k));
          if (!v || !Number.isFinite(v.ts)) continue;
          raw = JSON.stringify(v);
          break;
        } catch (_) {
          // ignore
        }
      }
    }

    if (!raw) return false;
    const data = JSON.parse(raw);
    if (!data || !data.root || !data.groups) return false;

    function assignState(dst, src) {
      if (!dst || !src) return;
      if (Number.isFinite(src.offsetX)) dst.offsetX = src.offsetX;
      if (Number.isFinite(src.offsetY)) dst.offsetY = src.offsetY;
      if (Number.isFinite(src.viewW)) dst.viewW = src.viewW;
      if (Number.isFinite(src.viewH)) dst.viewH = src.viewH;
    }

    assignState(DRAW_ROOT_STATE, data.root);
    assignState(DRAG_GROUP_STATE.h, data.groups.h);
    assignState(DRAG_GROUP_STATE.plates, data.groups.plates);
    assignState(DRAG_GROUP_STATE.flange, data.groups.flange);
    assignState(DRAG_GROUP_STATE.outer, data.groups.outer);
    assignState(DRAG_GROUP_STATE.inner, data.groups.inner);
    assignState(DRAG_GROUP_STATE.web, data.groups.web);

    return true;
  } catch (err) {
    console.warn("[splice] loadDragStateFromStorage failed:", err);
    return false;
  }
}

function clearSnapGuides() {
  const root = qs("#sp-draw-root");
  if (!root) return;
  const g = root.querySelector("#sp-snap-guides");
  if (g) g.remove();
}

function showVerticalGuide(x, top, bottom) {
  const root = qs("#sp-draw-root");
  if (!root) return;
  let g = root.querySelector("#sp-snap-guides");
  if (!g) {
    g = document.createElementNS(SVG_NS, "g");
    g.setAttribute("id", "sp-snap-guides");
    root.appendChild(g);
  } else {
    while (g.firstChild) g.removeChild(g.firstChild);
  }

  const ln = document.createElementNS(SVG_NS, "line");
  ln.setAttribute("x1", String(x));
  ln.setAttribute("y1", String(top));
  ln.setAttribute("x2", String(x));
  ln.setAttribute("y2", String(bottom));
  ln.setAttribute("stroke", SNAP_CFG.guideColor);
  ln.setAttribute("stroke-width", String(SNAP_CFG.guideWidth));
  ln.setAttribute("stroke-dasharray", SNAP_CFG.guideDash);
  g.appendChild(ln);
}

function computeSnapXForKey(key) {
  if (!DRAG_GEOM) return null;

  const basePlatesX = DRAG_GROUP_STATE.plates.offsetX;
  const flangeBaseX = basePlatesX + DRAG_GROUP_STATE.flange.offsetX;

  const outerLeft = DRAG_GEOM.plateX + flangeBaseX + DRAG_GROUP_STATE.outer.offsetX;
  const outerCenter = outerLeft + DRAG_GEOM.plateDrawLength / 2;
  const outerRight = outerLeft + DRAG_GEOM.plateDrawLength;

  const innerLeft = DRAG_GEOM.plateX + flangeBaseX + DRAG_GROUP_STATE.inner.offsetX;
  const innerCenter = innerLeft + DRAG_GEOM.plateDrawLength / 2;
  const innerRight = innerLeft + DRAG_GEOM.plateDrawLength;

  const webLeft = DRAG_GEOM.webPlateX + basePlatesX + DRAG_GROUP_STATE.web.offsetX;
  const webCenter = webLeft + DRAG_GEOM.webPlateDrawLength / 2;
  const webRight = webLeft + DRAG_GEOM.webPlateDrawLength;

  const targetLines = [];
  const anchors = [];

  if (key === "web") {
    // Web snaps to outer+inner flange lines
    targetLines.push(outerLeft, outerCenter, outerRight, innerLeft, innerCenter, innerRight);
    anchors.push(
      { name: "left", value: webLeft },
      { name: "center", value: webCenter },
      { name: "right", value: webRight }
    );
  } else if (key === "outer") {
    // Outer snaps to inner + web lines
    targetLines.push(innerLeft, innerCenter, innerRight, webLeft, webCenter, webRight);
    anchors.push(
      { name: "left", value: outerLeft },
      { name: "center", value: outerCenter },
      { name: "right", value: outerRight }
    );
  } else if (key === "inner") {
    // Inner snaps to outer + web lines
    targetLines.push(outerLeft, outerCenter, outerRight, webLeft, webCenter, webRight);
    anchors.push(
      { name: "left", value: innerLeft },
      { name: "center", value: innerCenter },
      { name: "right", value: innerRight }
    );
  } else {
    return null;
  }

  let best = null;
  for (const anchor of anchors) {
    for (const line of targetLines) {
      const delta = line - anchor.value;
      const dist = Math.abs(delta);
      if (dist <= SNAP_CFG.tol && (!best || dist < best.dist)) {
        best = { delta, dist, line };
      }
    }
  }

  if (!best) return null;

  const guideTop = DRAG_GEOM.margin;
  const guideBottom = DRAG_GEOM.drawingHeightMm - DRAG_GEOM.margin;
  return { delta: best.delta, guideX: best.line, top: guideTop, bottom: guideBottom };
}

function resolveDragTargetKey(target) {
  if (!target) return null;
  if (dragMode === DRAG_MODE.ALL) return "root";
  if (dragMode === DRAG_MODE.SPLIT) {
    if (target.closest("#sp-draw-h")) return "h";
    if (target.closest("#sp-draw-plates")) return "plates";
    return null;
  }
  if (dragMode === DRAG_MODE.FLANGE) {
    if (target.closest("#sp-draw-h")) return "h";
    if (target.closest("#sp-drag-web")) return "web";
    if (target.closest("#sp-drag-flange")) return "flange";
    return null;
  }
  if (dragMode === DRAG_MODE.PLATES) {
    if (target.closest("#sp-draw-h")) return "h";
    if (target.closest("#sp-drag-outer")) return "outer";
    if (target.closest("#sp-drag-inner")) return "inner";
    if (target.closest("#sp-drag-web")) return "web";
    return null;
  }
  return null;
}

function bindCanvasDrag(svg) {
  if (!svg || svg.dataset.drawRootBind === "1") return;
  svg.dataset.drawRootBind = "1";

  function clientToView(dx, dy) {
    const rect = svg.getBoundingClientRect();
    const scaleX = DRAW_ROOT_STATE.viewW / rect.width;
    const scaleY = DRAW_ROOT_STATE.viewH / rect.height;
    return { vx: dx * scaleX, vy: dy * scaleY };
  }

  svg.addEventListener("mousedown", (ev) => {
    if (!isDragEnabled()) return;
    const key = resolveDragTargetKey(ev.target);
    if (!key) return;
    const st = getDragStateForKey(key);
    if (!st) return;

    activeDragTargetKey = key;
    DRAG_SESSION.dragging = true;
    DRAG_SESSION.key = key;
    DRAG_SESSION.startClientX = ev.clientX;
    DRAG_SESSION.startClientY = ev.clientY;
    DRAG_SESSION.startOffsetX = st.offsetX;
    DRAG_SESSION.startOffsetY = st.offsetY;
    DRAG_SESSION.lockAxis = null;
    DRAG_SESSION.moved = false;
    ev.preventDefault();
  });

  window.addEventListener("mousemove", (ev) => {
    if (!DRAG_SESSION.dragging) return;
    if (!isDragEnabled()) {
      DRAG_SESSION.dragging = false;
      return;
    }
    const key = DRAG_SESSION.key;
    const st = getDragStateForKey(key);
    if (!st) return;
    const dx = ev.clientX - DRAG_SESSION.startClientX;
    const dy = ev.clientY - DRAG_SESSION.startClientY;
    const { vx, vy } = clientToView(dx, dy);
    let adjVx = vx;
    let adjVy = vy;

    if (ev.shiftKey) {
      if (!DRAG_SESSION.lockAxis) {
        DRAG_SESSION.lockAxis = Math.abs(vx) >= Math.abs(vy) ? "x" : "y";
      }
      if (DRAG_SESSION.lockAxis === "x") adjVy = 0;
      if (DRAG_SESSION.lockAxis === "y") adjVx = 0;
    } else {
      DRAG_SESSION.lockAxis = null;
    }

    const nextX = DRAG_SESSION.startOffsetX + adjVx;
    const nextY = DRAG_SESSION.startOffsetY + adjVy;
    if (Math.abs(nextX - st.offsetX) > 0.01 || Math.abs(nextY - st.offsetY) > 0.01) {
      DRAG_SESSION.moved = true;
    }
    st.offsetX = nextX;
    st.offsetY = nextY;

    const canSnap =
      (dragMode === DRAG_MODE.FLANGE && key === "web") ||
      (dragMode === DRAG_MODE.PLATES && (key === "web" || key === "outer" || key === "inner"));

    if (canSnap) {
      const snap = computeSnapXForKey(key);
      if (snap) {
        st.offsetX += snap.delta;
        showVerticalGuide(snap.guideX, snap.top, snap.bottom);
      } else {
        clearSnapGuides();
      }
    } else {
      clearSnapGuides();
    }
    applyDragTransformForKey(key);
  });

  window.addEventListener("mouseup", () => {
    DRAG_SESSION.dragging = false;
    DRAG_SESSION.lockAxis = null;
    clearSnapGuides();
    if (DRAG_SESSION.moved) saveDragStateToStorage();
  });

  svg.addEventListener("mouseleave", () => {
    DRAG_SESSION.dragging = false;
    DRAG_SESSION.lockAxis = null;
    clearSnapGuides();
    if (DRAG_SESSION.moved) saveDragStateToStorage();
  });
}

function bindDragKeys() {
  if (document.body.dataset.drawRootKeys === "1") return;
  document.body.dataset.drawRootKeys = "1";

  document.addEventListener("keydown", (ev) => {
    if (!isDragEnabled()) return;
    const tag = (ev.target && ev.target.tagName) ? ev.target.tagName.toLowerCase() : "";
    if (tag === "input" || tag === "textarea" || tag === "select") return;

    let key = activeDragTargetKey;
    if (!isKeyAllowedForMode(key)) {
      key = getDefaultKeyForMode();
    }
    if (!key) return;

    const st = getDragStateForKey(key);
    if (!st) return;

    let step = 1;
    if (ev.shiftKey) step = 5;
    if (ev.altKey) step = 0.5;

    let moved = false;
    if (ev.key === "ArrowUp") {
      st.offsetY -= step;
      moved = true;
    } else if (ev.key === "ArrowDown") {
      st.offsetY += step;
      moved = true;
    } else if (ev.key === "ArrowLeft") {
      st.offsetX -= step;
      moved = true;
    } else if (ev.key === "ArrowRight") {
      st.offsetX += step;
      moved = true;
    }

    if (moved) {
      ev.preventDefault();
      applyDragTransformForKey(key);
      saveDragStateToStorage();
    }
  });
}

function initSpliceDrawingCanvas() {
  const body = document.body;
  const drawingArea = qs("#sp-drawing-area");
  if (!drawingArea || !body) return;

  // プレースホルダ文字を消す
  const placeholder = qs(".sp-drawing-placeholder", drawingArea);
  if (placeholder) placeholder.style.display = "none";

  // body の data-* から mm 単位の情報を取得
  const pageWidthMm  = parseFloat(body.dataset.pageWidth  || "420");
  const pageHeightMm = parseFloat(body.dataset.pageHeight || "297");
  const drawingRatio = parseFloat(body.dataset.drawingRatio || "0.7");

  // 図面エリアの高さ（mm）
  const drawingHeightMm = pageHeightMm * drawingRatio;
  const drawingWidthMm  = pageWidthMm;

  let svg = qs("#sp-drawing-svg", drawingArea);
  if (!svg) {
    svg = document.createElementNS(SVG_NS, "svg");
    svg.id = "sp-drawing-svg";
    svg.setAttribute("xmlns", SVG_NS);
    drawingArea.appendChild(svg);
  }

  // viewBox / サイズを常に最新に
  svg.setAttribute("viewBox", `0 0 ${pageWidthMm} ${drawingHeightMm}`);
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  svg.style.width = "100%";
  svg.style.height = "100%";
  svg.setAttribute("tabindex", "0");

  // 中身をクリア
  while (svg.firstChild) svg.removeChild(svg.firstChild);

  const margin = 10; // mm

  // 外枠（図面内の内枠）は不要のため描画しない

  // 中心線（縦・横）は印刷プレビューでは非表示
  if (!body.classList.contains("sp-print-mode")) {
    const cx = drawingWidthMm  / 2;
    const cy = drawingHeightMm / 2;

    const vLine = document.createElementNS(SVG_NS, "line");
    vLine.setAttribute("x1", String(cx));
    vLine.setAttribute("y1", String(margin));
    vLine.setAttribute("x2", String(cx));
    vLine.setAttribute("y2", String(drawingHeightMm - margin));
    vLine.setAttribute("stroke", "#888");
    vLine.setAttribute("stroke-width", String(DRAW_STROKE_MM));
    vLine.setAttribute("stroke-dasharray", "2 2");
    svg.appendChild(vLine);

    const hLine = document.createElementNS(SVG_NS, "line");
    hLine.setAttribute("x1", String(margin));
    hLine.setAttribute("y1", String(cy));
    hLine.setAttribute("x2", String(drawingWidthMm - margin));
    hLine.setAttribute("y2", String(cy));
    hLine.setAttribute("stroke", "#888");
    hLine.setAttribute("stroke-width", String(DRAW_STROKE_MM));
    hLine.setAttribute("stroke-dasharray", "2 2");
    svg.appendChild(hLine);
  }

  DRAW_ROOT_STATE.viewW = pageWidthMm;
  DRAW_ROOT_STATE.viewH = drawingHeightMm;
  DRAW_ROOT_STATE.offsetX = 0;
  DRAW_ROOT_STATE.offsetY = 0;
  DRAG_GROUP_STATE.h.offsetX = 0;
  DRAG_GROUP_STATE.h.offsetY = 0;
  DRAG_GROUP_STATE.plates.offsetX = 0;
  DRAG_GROUP_STATE.plates.offsetY = 0;
  DRAG_GROUP_STATE.flange.offsetX = 0;
  DRAG_GROUP_STATE.flange.offsetY = 0;
  DRAG_GROUP_STATE.outer.offsetX = 0;
  DRAG_GROUP_STATE.outer.offsetY = 0;
  DRAG_GROUP_STATE.inner.offsetX = 0;
  DRAG_GROUP_STATE.inner.offsetY = 0;
  DRAG_GROUP_STATE.web.offsetX = 0;
  DRAG_GROUP_STATE.web.offsetY = 0;
  DRAW_ROOT = null;
  getDrawRoot(svg);
  bindCanvasDrag(svg);
  bindDragKeys();

  console.log("🖊 initSpliceDrawingCanvas:", {
    pageWidthMm,
    pageHeightMm,
    drawingRatio,
    drawingWidthMm,
    drawingHeightMm
  });
}

// ============================================================
// Drawing helpers (web/flange/hole)
// ============================================================

// ウェブの4隅に「入隅R（ウェブの外側へふくらむR）」だけを描く
function drawWebWithInnerFillet(svg, webX, webY, webWidth, webHeight, r) {
  const webL = webX;
  const webR = webX + webWidth;
  const yTop = webY;
  const yBot = webY + webHeight;

  // R がほぼ無い場合は普通の矩形ウェブ
  if (!r || r < 0.1) {
    const rect = document.createElementNS(SVG_NS, "rect");
    rect.setAttribute("x", String(webX));
    rect.setAttribute("y", String(webY));
    rect.setAttribute("width",  String(webWidth));
    rect.setAttribute("height", String(webHeight));
    rect.setAttribute("fill", "#ffffff");
    rect.setAttribute("stroke", "#000");
    rect.setAttribute("stroke-width", String(DRAW_STROKE_MM));
    svg.appendChild(rect);
    return;
  }

  // R の上限クリップ
  const maxR = Math.min(webWidth, webHeight) / 2;
  const rr = Math.min(r, maxR);

  // ウェブの中身だけ白で塗る（線なし）
  const fillRect = document.createElementNS(SVG_NS, "rect");
  fillRect.setAttribute("x", String(webL));
  fillRect.setAttribute("y", String(yTop));
  fillRect.setAttribute("width",  String(webWidth));
  fillRect.setAttribute("height", String(webHeight));
  fillRect.setAttribute("fill", "#ffffff");
  fillRect.setAttribute("stroke", "none");
  svg.appendChild(fillRect);

  const strokeW = DRAW_STROKE_MM;

  function addPath(d) {
    const p = document.createElementNS(SVG_NS, "path");
    p.setAttribute("d", d);
    p.setAttribute("fill", "none");
    p.setAttribute("stroke", "#000");
    p.setAttribute("stroke-width", String(strokeW));
    svg.appendChild(p);
  }

  // 左右の縦線（R の間だけ）
  addPath(`M ${webL} ${yTop + rr} L ${webL} ${yBot - rr}`);
  addPath(`M ${webR} ${yTop + rr} L ${webR} ${yBot - rr}`);

  // 上側の入隅R
  addPath(`M ${webL - rr} ${yTop} Q ${webL} ${yTop} ${webL} ${yTop + rr}`);
  addPath(`M ${webR + rr} ${yTop} Q ${webR} ${yTop} ${webR} ${yTop + rr}`);

  // 下側の入隅R
  addPath(`M ${webR} ${yBot - rr} Q ${webR} ${yBot} ${webR + rr} ${yBot}`);
  addPath(`M ${webL} ${yBot - rr} Q ${webL} ${yBot} ${webL - rr} ${yBot}`);
}

// 角丸R用の1/4円弧をポリラインで追加（現状未使用だが保持）
function addQuarterFillet(points, corner, P, r, segments = 8) {
  const Px = P.x;
  const Py = P.y;

  let Cx, Cy;
  let start, end;

  if (corner === "TL") {
    Cx = Px - r; Cy = Py + r;
    start = { x: Px,     y: Py + r };
    end   = { x: Px - r, y: Py     };
  } else if (corner === "TR") {
    Cx = Px + r; Cy = Py + r;
    start = { x: Px + r, y: Py     };
    end   = { x: Px,     y: Py + r };
  } else if (corner === "BR") {
    Cx = Px + r; Cy = Py - r;
    start = { x: Px,     y: Py - r };
    end   = { x: Px + r, y: Py     };
  } else if (corner === "BL") {
    Cx = Px - r; Cy = Py - r;
    start = { x: Px - r, y: Py     };
    end   = { x: Px,     y: Py - r };
  } else {
    return;
  }

  const angleStart = Math.atan2(start.y - Cy, start.x - Cx);
  const angleEnd   = Math.atan2(end.y   - Cy, end.x   - Cx);

  let delta = angleEnd - angleStart;
  if (delta > Math.PI)  delta -= 2 * Math.PI;
  if (delta < -Math.PI) delta += 2 * Math.PI;

  if (Math.abs(delta) < 1e-6) {
    points.push(end);
    return;
  }

  const steps = Math.max(3, segments);
  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    const a = angleStart + delta * t;
    const x = Cx + r * Math.cos(a);
    const y = Cy + r * Math.sin(a);
    points.push({ x, y });
  }
}

// フランジを「内側Rの端」で左右2本に分割して描画
function drawFlangeWithCutout(
  svg,
  x0,
  y0,
  width,
  flangeThk,
  webX,
  webW,
  r,
  innerAtBottom = true
) {
  const hasR = r && r > 0;

  const yTop    = y0;
  const yBottom = y0 + flangeThk;
  const yInner  = innerAtBottom ? yBottom : yTop;
  const yOuter  = innerAtBottom ? yTop    : yBottom;

  // フランジ全体を塗りつぶし（枠線なし）
  const fillRect = document.createElementNS(SVG_NS, "rect");
  fillRect.setAttribute("x", String(x0));
  fillRect.setAttribute("y", String(y0));
  fillRect.setAttribute("width",  String(width));
  fillRect.setAttribute("height", String(flangeThk));
  fillRect.setAttribute("fill", "#ffffff");
  fillRect.setAttribute("stroke", "none");
  svg.appendChild(fillRect);

  const strokeW = DRAW_STROKE_MM;

  function drawLine(x1, y1, x2, y2) {
    const ln = document.createElementNS(SVG_NS, "line");
    ln.setAttribute("x1", String(x1));
    ln.setAttribute("y1", String(y1));
    ln.setAttribute("x2", String(x2));
    ln.setAttribute("y2", String(y2));
    ln.setAttribute("stroke", "#000");
    ln.setAttribute("stroke-width", String(strokeW));
    svg.appendChild(ln);
  }

  // 左右の外周縦線
  drawLine(x0,         yTop, x0,         yBottom);
  drawLine(x0 + width, yTop, x0 + width, yBottom);

  // 外側の水平線
  drawLine(x0, yOuter, x0 + width, yOuter);

  // 内側の水平線
  if (!hasR) {
    drawLine(x0, yInner, x0 + width, yInner);
  } else {
    const webL = webX;
    const webR = webX + webW;

    const leftEnd    = webL - r; // 左Rのフランジ側端
    const rightStart = webR + r; // 右Rのフランジ側端

    if (leftEnd > x0) {
      drawLine(x0, yInner, leftEnd, yInner);
    }
    if (x0 + width > rightStart) {
      drawLine(rightStart, yInner, x0 + width, yInner);
    }
  }
}

// 孔描画
function isHoleCrossEnabled() {
  const cb = qs("#sp-hole-cross-toggle");
  if (cb) return cb.checked;
  const hidden = qs("#sp-hole-cross-print");
  if (hidden) {
    const v = String(hidden.value || "").trim().toLowerCase();
    if (v === "1" || v === "true" || v === "on" || v === "yes") return true;
    if (v === "0" || v === "false" || v === "off" || v === "no") return false;
  }
  return holeCenterCrossEnabled;
}

function drawSpliceHole(svg, cx, cy, radius) {
  const c = document.createElementNS(SVG_NS, "circle");
  c.setAttribute("cx", String(cx));
  c.setAttribute("cy", String(cy));
  c.setAttribute("r",  String(radius));
  c.setAttribute("fill", "#ffffff");
  c.setAttribute("stroke", "#000");
  c.setAttribute("stroke-width", String(DRAW_STROKE_MM));
  svg.appendChild(c);

  if (isHoleCrossEnabled() && radius > 0) {
    const strokeW = DRAW_STROKE_MM;

    const hLine = document.createElementNS(SVG_NS, "line");
    hLine.setAttribute("x1", String(cx - radius));
    hLine.setAttribute("y1", String(cy));
    hLine.setAttribute("x2", String(cx + radius));
    hLine.setAttribute("y2", String(cy));
    hLine.setAttribute("stroke", "#000");
    hLine.setAttribute("stroke-width", String(strokeW));
    hLine.setAttribute("vector-effect", "non-scaling-stroke");
    svg.appendChild(hLine);

    const vLine = document.createElementNS(SVG_NS, "line");
    vLine.setAttribute("x1", String(cx));
    vLine.setAttribute("y1", String(cy - radius));
    vLine.setAttribute("x2", String(cx));
    vLine.setAttribute("y2", String(cy + radius));
    vLine.setAttribute("stroke", "#000");
    vLine.setAttribute("stroke-width", String(strokeW));
    vLine.setAttribute("vector-effect", "non-scaling-stroke");
    svg.appendChild(vLine);
  }
}

// ============================================================
// H断面 拡大インジケータ（Zoom/Drag）
// ============================================================

const H_ZOOM_STATE = {
  geom: null,     // hGeom: {hWidthMm, hHeightMm, ...}
  hText: "",      // 表示用の "H-400x200x8x13" など
  zoom: 1.5,      // 1.0 = フィット
  offsetX: 0,
  offsetY: 0,
};

/**
 * H 型鋼サイズ → 角丸 R(mm)
 * config.py の H_STEEL_MASTER の r を写したもの
 */
const H_STEEL_R_MAP = {
  "100x50x5x7":    8,
  "125x60x6x7":    8,
  "150x75x5x7":    8,
  "175x90x5x8":    8,
  "200x100x5.5x8": 8,
  "248x124x5x8":   8,
  "250x125x6x9":   8,
  "298x149x5.5x8": 13,
  "300x150x6.5x9": 13,
  "346x174x6x9":   13,
  "350x175x7x11":  13,
  "396x199x7x11":  13,
  "400x200x8x13":  13,
  "446x199x8x12":  13,
  "450x200x9x14":  13,
  "496x199x9x14":  13,
  "500x200x10x16": 13,
  "100x100x6x8":    8,
  "150x150x7x10":   8,
  "175x175x7.5x11": 13,
  "200x200x8x12":   13,
  "250x250x9x14":   13,
  "300x300x10x15":  13,
  "400x400x13x21":  22,
};

function bindHZoomDrag(svg, viewSize) {
  let dragging = false;
  let startClientX = 0;
  let startClientY = 0;
  let startOffsetX = 0;
  let startOffsetY = 0;

  function clientToView(dx, dy) {
    const rect = svg.getBoundingClientRect();
    const scaleX = viewSize / rect.width;
    const scaleY = viewSize / rect.height;
    return { vx: dx * scaleX, vy: dy * scaleY };
  }

  svg.addEventListener("mousedown", (ev) => {
    if (!isDragEnabled()) return;
    ev.preventDefault();
    dragging = true;
    startClientX = ev.clientX;
    startClientY = ev.clientY;
    startOffsetX = H_ZOOM_STATE.offsetX;
    startOffsetY = H_ZOOM_STATE.offsetY;
  });

  window.addEventListener("mousemove", (ev) => {
    if (!dragging) return;

    const dx = ev.clientX - startClientX;
    const dy = ev.clientY - startClientY;

    const { vx, vy } = clientToView(dx, dy);

    H_ZOOM_STATE.offsetX = startOffsetX + vx;
    H_ZOOM_STATE.offsetY = startOffsetY + vy;

    renderHSectionZoomIndicator();
  });

  window.addEventListener("mouseup", () => {
    dragging = false;
  });

  svg.addEventListener("mouseleave", () => {
    dragging = false;
  });
}

function initSpliceZoomCanvas() {
  const zoomArea = qs("#sp-h-zoom-indicator");
  if (!zoomArea) return null;

  let svg = qs("#sp-h-zoom-svg", zoomArea);
  if (!svg) {
    svg = document.createElementNS(SVG_NS, "svg");
    svg.id = "sp-h-zoom-svg";
    svg.setAttribute("xmlns", SVG_NS);
    zoomArea.appendChild(svg);
  }

  const viewSize = 100;
  svg.setAttribute("viewBox", `0 0 ${viewSize} ${viewSize}`);
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  svg.style.width  = "200px";
  svg.style.height = "200px";

  while (svg.firstChild) svg.removeChild(svg.firstChild);

  // ドラッグ用イベント（1回だけバインド）
  if (svg.dataset.dragBound !== "1") {
    bindHZoomDrag(svg, viewSize);
    svg.dataset.dragBound = "1";
  }

  return svg;
}

function renderHSectionZoomIndicator() {
  const svg = initSpliceZoomCanvas();
  const state = H_ZOOM_STATE;

  if (!svg || !state.geom) return;

  const { geom, hText, zoom, offsetX, offsetY } = state;

  const {
    hWidthMm,
    hHeightMm,
    flangeThkMm,
    webWidthMm,
    webHeightMm,
    rMm
  } = geom;

  const viewSize = 100;
  const margin   = 8;

  const availWidth  = viewSize - margin * 2;
  const availHeight = viewSize - margin * 2;

  const baseScale = Math.min(
    availWidth  / hWidthMm,
    availHeight / hHeightMm
  ) || 1;

  const s = baseScale * zoom;

  const width  = hWidthMm  * s;
  const height = hHeightMm * s;

  const flangeThk = flangeThkMm * s;
  const webW      = webWidthMm  * s;
  const webH      = webHeightMm * s;
  const r         = (rMm || 0) * s;

  console.log("[splice] zoom fillet radius", {
    hSize: geom.sizeKey,
    rMm,
    baseScale,
    zoom,
    usedScale: s,
    rPx: r,
    webW,
    webH,
  });

  // 中心（オフセット込み）
  const cx = viewSize / 2 + offsetX;
  const cy = viewSize / 2 + offsetY;

  // 左上
  const x0 = cx - width  / 2;
  const y0 = cy - height / 2;

  // ウェブ位置
  const webX = x0 + (width - webW) / 2;
  const webY = y0 + flangeThk;

  const hasR = r && r >= 0.05;

  // ウェブ（背面）
  if (!hasR) {
    const webRect = document.createElementNS(SVG_NS, "rect");
    webRect.setAttribute("x", String(webX));
    webRect.setAttribute("y", String(webY));
    webRect.setAttribute("width",  String(webW));
    webRect.setAttribute("height", String(webH));
    webRect.setAttribute("fill", "#ffffff");
    webRect.setAttribute("stroke", "#000");
    webRect.setAttribute("stroke-width", String(DRAW_STROKE_MM));
    svg.appendChild(webRect);
  } else {
    drawWebWithInnerFillet(svg, webX, webY, webW, webH, r);
  }

  // フランジ（手前）
  drawFlangeWithCutout(svg, x0, y0, width, flangeThk, webX, webW, r, true);
  drawFlangeWithCutout(
    svg,
    x0,
    y0 + height - flangeThk,
    width,
    flangeThk,
    webX,
    webW,
    r,
    false
  );

  // 中央線（任意）
  const midLine = document.createElementNS(SVG_NS, "line");
  midLine.setAttribute("x1", String(viewSize / 2));
  midLine.setAttribute("y1", String(0));
  midLine.setAttribute("x2", String(viewSize / 2));
  midLine.setAttribute("y2", String(viewSize));
  midLine.setAttribute("stroke", "#ccc");
  midLine.setAttribute("stroke-width", String(DRAW_STROKE_MM));
  midLine.setAttribute("stroke-dasharray", "1 2");
  svg.appendChild(midLine);

  // ラベル
  if (hText) {
    const label = document.createElementNS(SVG_NS, "text");
    label.setAttribute("x", String(viewSize / 2));
    label.setAttribute("y", String(viewSize - 2));
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("font-size", "6");
    label.textContent = hText;
    svg.appendChild(label);
  }

  console.log("[splice] zoom indicator render:", {
    zoom,
    offsetX,
    offsetY,
    baseScale,
    usedScale: s,
  });
}

function drawHSectionZoomIndicator(hGeom, hText) {
  if (!hGeom) {
    H_ZOOM_STATE.geom    = null;
    H_ZOOM_STATE.hText   = "";
    H_ZOOM_STATE.offsetX = 0;
    H_ZOOM_STATE.offsetY = 0;
    renderHSectionZoomIndicator();
    return;
  }

  H_ZOOM_STATE.geom    = hGeom;
  H_ZOOM_STATE.hText   = hText || "";
  H_ZOOM_STATE.offsetX = 0; // Hサイズが変わったら位置リセット
  H_ZOOM_STATE.offsetY = 0;

  renderHSectionZoomIndicator();
}

// ============================================================
// Hサイズ → プリセットキー正規化 / Preset lookup / Parse
// ============================================================
function normalizeHSizeKey(raw) {
  return (raw || "")
    .trim()
    .replace(/[ 　\t]+/g, "")
    .replace(/×/g, "x")
    .replace(/X/g, "x");
}

function findPresetByHText(hText) {
  const presets = getSplicePresets();
  const hSize = normalizeHSizeKey(hText);
  if (!hSize) return null;

  const key1 = hSize;
  const key2 = hSize.replace(/^H-?/i, "H");
  const key3 = hSize.replace(/^H-?/i, "");

  return presets[key1] || presets[key2] || presets[key3] || null;
}

function parseHSize(raw) {
  const key = normalizeHSizeKey(raw);
  if (!key) return null;

  const withoutPrefix = key.replace(/^H-?/i, "");
  const parts = withoutPrefix.split("x");

  if (parts.length < 2) {
    console.warn("[splice] parseHSize: 期待する形式ではありません:", raw);
    return null;
  }

  const nums = parts.map(p => parseFloat(p));
  if (nums.some(n => !Number.isFinite(n))) {
    console.warn("[splice] parseHSize: 数値に変換できません:", raw);
    return null;
  }

  const [depth, flangeWidth, webThk, flangeThk] = nums;

  const radius = H_STEEL_R_MAP[withoutPrefix];

  const result = {
    raw,
    key,
    sizeKey: withoutPrefix,
    depth,
    flangeWidth,
    webThk,
    flangeThk,
    radius: radius ?? null,
  };

  console.log("[splice] parseHSize:", raw, "=>", result);
  return result;
}

// ============================================================
// Main drawing (form -> preview)
// ============================================================
function drawSplicePreviewFromForm(preferredRow = null) {
  const body = document.body;

  // 編集画面でのみ動かす（印刷プレビューでは静的枠だけ）
  if (!body || (!body.classList.contains("sp-edit-mode") && !body.classList.contains("sp-print-mode"))) return;

  const svg = qs("#sp-drawing-svg");
  if (!svg) return;

  // 静的枠＋中心線を一度描き直して、前回描画をリセット
  initSpliceDrawingCanvas();

  const isPrintMode = document.body?.classList.contains("sp-print-mode");
  let hasStoredDrag = false;
  if (isPrintMode) {
    // 印刷プレビュー時のみドラッグ位置を反映（同一セッションの保存のみ）
    hasStoredDrag = loadDragStateFromStorage({ allowFallback: false });
  } else {
    // 作図時（編集）は常に初期位置へ戻す
    resetDragOffsetsToDefault();
  }

  const root = getDrawRoot(svg);
  const gH = ensureDragGroup(root, "sp-draw-h", "h");
  const gPlates = ensureDragGroup(root, "sp-draw-plates", "plates");

  // 1) 対象行の選定（preferredRow → 最初の入力行）
  const tbody = getSpRowsTbody();
  if (!tbody) return;

  const trs = qsa("tr", tbody);

  let targetRow = preferredRow;
  if (!targetRow) {
    for (const tr of trs) {
      const hInput      = tr.querySelector('input[name="h_size[]"]');
      const flangeOuter = tr.querySelector('input[name="flange_plate_outer[]"]');
      const flangeInner = tr.querySelector('input[name="flange_plate_inner[]"]');
      const webInput    = tr.querySelector('input[name="web_plate[]"]');

      const hasAny = [hInput, flangeOuter, flangeInner, webInput].some(inp => {
        return inp && inp.value && inp.value.trim() !== "";
      });

      if (hasAny) {
        targetRow = tr;
        break;
      }
    }
  }

  if (!targetRow) {
    console.log("[splice] drawSplicePreviewFromForm: 入力行なし");
    return;
  }

  // 2) 行入力の取得（nameフォールバック含む）
  const hInput = targetRow.querySelector('input[name="h_size[]"]');

  const flangeOuter =
    targetRow.querySelector('input[name="flange_plate_outer[]"]') ||
    targetRow.querySelector('input[name="flange_plate[]"]');

  const flangeInner =
    targetRow.querySelector('input[name="flange_plate_inner[]"]');

  const webInput = targetRow.querySelector('input[name="web_plate[]"]');

  const colPitchInp = targetRow.querySelector('input[name="col_pitch[]"]');
  const rowPitchInp = targetRow.querySelector('input[name="row_pitch[]"]');
  const holeDiaInp  = targetRow.querySelector('input[name="hole_dia[]"]');

  const holeCntXInp =
    targetRow.querySelector('input[name="hole_count_x[]"]') ||
    targetRow.querySelector('input[name="hole_count[]"]');

  const holeCntYInp =
    targetRow.querySelector('input[name="hole_count_y[]"]');

  const hText = hInput ? hInput.value.trim() : "";

  // 3) 行入力の数値化（NaN 許容）
  const colPitchMmRaw = colPitchInp && colPitchInp.value.trim() !== ""
    ? parseFloat(colPitchInp.value)
    : NaN;

  const rowPitchMmRaw = rowPitchInp && rowPitchInp.value.trim() !== ""
    ? parseFloat(rowPitchInp.value)
    : NaN;

  let holeCountXRaw = holeCntXInp && holeCntXInp.value.trim() !== ""
    ? parseInt(holeCntXInp.value, 10)
    : NaN;

  let holeCountYRaw = holeCntYInp && holeCntYInp.value.trim() !== ""
    ? parseInt(holeCntYInp.value, 10)
    : NaN;

  // ★孔径は共通ヘルパへ統一（重複ロジック削除）
  const holeDiaMmRow = parseDiaMmFromText(holeDiaInp?.value);

  console.log("[splice] holeDia parse:", {
    raw: holeDiaInp ? holeDiaInp.value : null,
    holeDiaMmRow,
  });

  // 4) 図面エリアのサイズ（mm）
  const pageWidthMm     = parseFloat(body.dataset.pageWidth  || "420");
  const pageHeightMm    = parseFloat(body.dataset.pageHeight || "297");
  const drawingRatio    = parseFloat(body.dataset.drawingRatio || "0.7");
  const drawingWidthMm  = pageWidthMm;
  const drawingHeightMm = pageHeightMm * drawingRatio;
  const margin          = 10;

  const innerWidth  = drawingWidthMm  - margin * 2;
  const innerHeight = drawingHeightMm - margin * 2;

  // ★追加：H断面が実際に占有した “下端(描画座標mm)” を保持（プレート領域決定に使う）
  let hUsedBottomDraw = margin;   // 初期値（Hが無い時は上端付近）
  const H_USED_PAD_DRAW = 6;      // Hの下に少し余白（mm）

  // 5) H型鋼断面の描画（上段）
  const hDims = hText ? parseHSize(hText) : null;

  let hWidthMm  = null;
  let hHeightMm = null;
  let flangeThkMm = null;
  let webThkMm    = null;
  let hScale = null;

  if (hDims) {
    const hZoneHeight  = innerHeight * 0.3;
    const hAvailWidth  = innerWidth  * 0.6;
    const hAvailHeight = hZoneHeight * 0.8;

    hScale = Math.min(
      hAvailWidth  / hDims.flangeWidth,
      hAvailHeight / hDims.depth
    );

    hWidthMm  = hDims.flangeWidth * hScale;
    hHeightMm = hDims.depth       * hScale;

    // ★H断面の「実寸ベース」移動量（mm）
    const H_SHIFT_X_REAL_MM = 50;  // 右へ（実寸）
    const H_SHIFT_Y_REAL_MM = 50;  // 下へ（実寸）

    // ★描画座標(mm)へ変換（hScale を掛ける）
    const hShiftX = H_SHIFT_X_REAL_MM * hScale;
    const hShiftY = H_SHIFT_Y_REAL_MM * hScale;

    // 左寄せ基準
    const hLeftPad = margin + 4;
    let hX = hLeftPad + hShiftX;

    // Yは上段中央基準
    let hY = margin + (hZoneHeight - hHeightMm) / 2 + hShiftY;

    // ---- 右/下のはみ出しを「上段ゾーン」ではなく「作図エリア全体」で抑える（重要）----
    const maxHX = drawingWidthMm  - margin - hWidthMm;
    const maxHY = drawingHeightMm - margin - hHeightMm;

    if (Number.isFinite(maxHX)) hX = Math.min(hX, maxHX);
    if (Number.isFinite(maxHY)) hY = Math.min(hY, maxHY);

    hX = Math.max(margin, hX);
    hY = Math.max(margin, hY);

    // ★追加：H断面の実下端を記録（プレート領域の開始位置に使う）
    hUsedBottomDraw = Math.max(hUsedBottomDraw, hY + hHeightMm + H_USED_PAD_DRAW);

    flangeThkMm = Math.max(hDims.flangeThk * hScale, 0.7);
    webThkMm    = Math.max(hDims.webThk    * hScale, 0.7);

    const webWidthMm  = webThkMm;
    const webX        = hX + (hWidthMm - webWidthMm) / 2;
    const webY        = hY + flangeThkMm;
    const webHeightMm = hHeightMm - flangeThkMm * 2;

    const radiusConfig = hDims.radius || 0;
    const baseRadiusMm = radiusConfig * hScale;

    const maxRByWeb    = Math.max(webWidthMm  / 2 - 0.2, 0);
    const maxRByHeight = Math.max(webHeightMm / 2 - 0.2, 0);

    let rMm = Math.min(baseRadiusMm, maxRByWeb, maxRByHeight);
    if (!Number.isFinite(rMm) || rMm < 0) rMm = 0;

    console.log("[splice] main H fillet radius", {
      rawRadiusMm: radiusConfig,
      scale: hScale,
      rMm,
      webWidthMm,
      webHeightMm,
      hSize: hDims.sizeKey,
    });

    const hGeom = {
      hWidthMm,
      hHeightMm,
      flangeThkMm,
      webWidthMm,
      webHeightMm,
      rMm,

      // 実寸(mm)
      sizeKey:        hDims.sizeKey,
      depthMm:        hDims.depth,
      flangeWidthMm:  hDims.flangeWidth,
      webThkMmRaw:    hDims.webThk,
      flangeThkMmRaw: hDims.flangeThk,
      scale:          hScale,
    };

    const hasR = rMm && rMm >= 0.2;

    // ウェブ（背面）
    if (!hasR) {
      const webRect = document.createElementNS(SVG_NS, "rect");
      webRect.setAttribute("x", String(webX));
      webRect.setAttribute("y", String(webY));
      webRect.setAttribute("width",  String(webWidthMm));
      webRect.setAttribute("height", String(webHeightMm));
      webRect.setAttribute("fill", "#ffffff");
      webRect.setAttribute("stroke", "#000");
      webRect.setAttribute("stroke-width", String(DRAW_STROKE_MM));
      gH.appendChild(webRect);
    } else {
      drawWebWithInnerFillet(gH, webX, webY, webWidthMm, webHeightMm, rMm);
    }

    // フランジ（手前）
    drawFlangeWithCutout(gH, hX, hY, hWidthMm, flangeThkMm, webX, webWidthMm, rMm, true);
    drawFlangeWithCutout(
      gH,
      hX,
      hY + hHeightMm - flangeThkMm,
      hWidthMm,
      flangeThkMm,
      webX,
      webWidthMm,
      rMm,
      false
    );

    // Drag hit for H section area
    const prevHitH = gH.querySelector("#sp-drag-hit-h");
    if (prevHitH) prevHitH.remove();
    const hitH = document.createElementNS(SVG_NS, "rect");
    hitH.setAttribute("id", "sp-drag-hit-h");
    hitH.setAttribute("x", String(hX));
    hitH.setAttribute("y", String(hY));
    hitH.setAttribute("width", String(hWidthMm));
    hitH.setAttribute("height", String(hHeightMm));
    hitH.setAttribute("fill", "transparent");
    hitH.setAttribute("pointer-events", "all");
    gH.appendChild(hitH);

    // 右下インジケータ
    drawHSectionZoomIndicator(hGeom, hText);

    console.log("[splice] drawSplicePreviewFromForm: H断面描画", {
      hDims,
      hScale,
      hWidthMm,
      hHeightMm,
    });
  }

  // 6) 最終採用値（Xは行→共通 / Yは新仕様により共通優先）====
  // 行の値
  const colPitchRow = colPitchMmRaw;
  const rowPitchRow = rowPitchMmRaw;
  const cntXRow     = holeCountXRaw;
  const cntYRow     = holeCountYRaw;
  const diaRow      = holeDiaMmRow;

  // 共通フォーム
  const colPitchCommon = readNumberOrNaN("#sp-flange-col-pitch-mm");
  const rowPitchCommon = readNumberOrNaN("#sp-flange-row-pitch-mm");
  const cntXCommon     = readNumberOrNaN("#sp-flange-hole-count-x");
  const cntYCommon     = readNumberOrNaN("#sp-flange-hole-count-y");
  const diaCommon      = parseDiaMmFromText(qs("#sp-flange-hole-dia-mm")?.value);

  // ★X方向：行優先 → 共通フォールバック
  const colPitchMm  = Number.isFinite(colPitchRow) ? colPitchRow : colPitchCommon;
  const holeCountX  = Number.isFinite(cntXRow)     ? cntXRow     : cntXCommon;

  // ★Y方向：新仕様＝共通フォーム優先（行入力は参考値）
  const rowPitchMm  = Number.isFinite(rowPitchCommon) ? rowPitchCommon : rowPitchRow;
  const holeCountY  = Number.isFinite(cntYCommon)     ? cntYCommon     : cntYRow;

  // 孔径：行優先 → 共通
  const holeDiaMmFinal = Number.isFinite(diaRow) ? diaRow : diaCommon;

  // 7) スプライスプレート外形寸法（外フランジ：設計値）
  let plateLengthMm = NaN;
  let plateWidthMm  = NaN;

  // 共通設定（fg/fgsp/clearance）※ readNumberOrNaN に統一
  const fgEndPitchMm   = readNumberOrNaN("#sp-common-flange-end-pitch-mm");     // fg終端（H切端側）
  const fgspEndPitchMm = readNumberOrNaN("#sp-common-flangesp-end-pitch-mm");   // fgsp終端（プレート端側）
  const clearanceMm    = readNumberOrNaN("#sp-common-clearance-mm");

  // フォールバック（空ならデフォルト）
  const fgEnd   = Number.isFinite(fgEndPitchMm)   ? fgEndPitchMm   : DEFAULT_SP_END_PITCH_MM;
  const fgspEnd = Number.isFinite(fgspEndPitchMm) ? fgspEndPitchMm : DEFAULT_SP_END_PITCH_MM;
  const clr     = Number.isFinite(clearanceMm)    ? clearanceMm    : DEFAULT_SP_CLEARANCE_MM;

  // フランジ孔設定（X）
  const colCount   = holeCountX;

  const flangeXOk =
    Number.isFinite(colPitchMm) && colPitchMm > 0 &&
    Number.isFinite(colCount)   && colCount   >= 1;

  if (flangeXOk) {
    const nX = Math.trunc(colCount);
    const spanX = (nX > 1) ? colPitchMm * (nX - 1) : 0;

    // ★新仕様：L = fgsp + spanX + fg + clr + fg + spanX + fgsp
    plateLengthMm = fgspEnd + spanX + fgEnd + clr + fgEnd + spanX + fgspEnd;
  }

  // ★外フランジ幅W（実寸mm）
  if (hDims && Number.isFinite(hDims.flangeWidth)) {
    plateWidthMm = hDims.flangeWidth;
  }

  console.log("[splice] flange plate size(new spec)", {
    fgEnd, fgspEnd, clr,
    colPitchMm, colCount,
    plateLengthMm, plateWidthMm
  });

// ------------------------------------------------------------
// 9) Y方向の孔配置（外フランジ）※layoutより前に確定させる
// ------------------------------------------------------------
let spanYmm = NaN;
let yCentersMm = [];
let nY = 0;
let edgeMarginMm = NaN;
let flangeRowEdgeMm = NaN;

// ★Y方向は「フランジ孔設定（共通フォーム）」を正とする（新仕様）
// 端距離（行端距離）は明示値を優先。無ければ fgsp をフォールバック。
const flangeRowPitchMm = readNumberOrNaN("#sp-flange-row-pitch-mm");
const flangeRowCount   = readNumberOrNaN("#sp-flange-hole-count-y");
const flangeRowEdgeRaw = readNumberOrNaN("#sp-flange-row-edge-mm");

const flangeYPitchOk = Number.isFinite(flangeRowPitchMm) && flangeRowPitchMm > 0;
const flangeYCountOk = Number.isFinite(flangeRowCount)   && flangeRowCount   >= 1;

if (Number.isFinite(plateWidthMm) && flangeYPitchOk && flangeYCountOk) {
  const n = Math.trunc(flangeRowCount);

  spanYmm = (n > 1) ? flangeRowPitchMm * (n - 1) : 0;
  const fallbackEdge = fgspEnd;
  flangeRowEdgeMm = Number.isFinite(flangeRowEdgeRaw) ? flangeRowEdgeRaw : fallbackEdge;
  edgeMarginMm = flangeRowEdgeMm;

  yCentersMm = [];
  nY = n;

  const startYmm = flangeRowEdgeMm;
  for (let j = 0; j < nY; j++) {
    yCentersMm.push(startYmm + flangeRowPitchMm * j);
  }

  if (Number.isFinite(flangeRowEdgeMm) && Number.isFinite(spanYmm)) {
    const tail = plateWidthMm - (flangeRowEdgeMm + spanYmm);
    if (tail < -0.01) {
      console.warn("[splice] flange row edge/pitch exceed plate width", {
        plateWidthMm,
        flangeRowEdgeMm,
        spanYmm,
        tail,
      });
    }
  }
} else {
  const centerYmm = Number.isFinite(plateWidthMm) ? plateWidthMm / 2 : 0;
  yCentersMm = [centerYmm];
  nY = 1;
  spanYmm = NaN;
  edgeMarginMm = NaN;
}

// ★ layout 用：内フランジの実寸高さ a = B - spanY（無ければB）
const innerPlateHeightMmForLayout =
  (Number.isFinite(plateWidthMm) && Number.isFinite(spanYmm) && spanYmm >= 0)
    ? Math.max(plateWidthMm - spanYmm, 0)
    : plateWidthMm;

// ------------------------------------------------------------
// ★ web plate の実寸(mm)をここで「確定」する（layoutも描画も同じ値を使う）
// ------------------------------------------------------------
const flangeSettingsForWeb = {
  endPitchMm: fgEnd,
  clearanceMm: clr,
  colPitchMm: colPitchMm,
  holeCountX: holeCountX,
  rowPitchMm: flangeRowPitchMm,
  holeCountY: flangeRowCount,
  holeDiaMm: holeDiaMmFinal,
};
 
const webHole = readWebHoleSettingsFallback(flangeSettingsForWeb);
 
const webSpXEndPitchMm = Number.isFinite(webHole.webspXEndPitchMm)
  ? webHole.webspXEndPitchMm
  : fgspEnd;
 
const webHEndPitchMm = Number.isFinite(webHole.webEndPitchMm)
  ? webHole.webEndPitchMm
  : fgEnd;
 
const webPlEndPitchMm = webSpXEndPitchMm;
const webHtEndPitchMm = webHEndPitchMm;
const webClearanceMm  = clr;
 
// ★ここで webPlateLengthMm / webPlateHeightMm を1回だけ確定
const webSize = computeWebPlateSizeMm(
  webHole,
  webPlEndPitchMm,
  webHtEndPitchMm,
  webClearanceMm,
  plateLengthMm,                          // フォールバック長さ
  (hDims?.depth ?? plateWidthMm) * 0.6     // フォールバック高さ
);
let webPlateLengthMm = webSize.webPlateLengthMm;
let webPlateHeightMm = webSize.webPlateHeightMm;

const WEB_LABEL_FONT_DRAW  = 4;   // あなたの LABEL_FONT と合わせる（今 4）
const WEB_LABEL_LINES      = 1;
const WEB_LABEL_PAD_DRAW   = 2;   // hanging + 余白
const FIX_BOTTOM_LABEL_DRAW =
  WEB_LABEL_FONT_DRAW * 1.2 * WEB_LABEL_LINES + WEB_LABEL_PAD_DRAW;

// 固定合計（縮まない）
const LABEL_LINE_HEIGHT_DRAW = WEB_LABEL_FONT_DRAW * 1.2;
const LABEL_BLOCK_DRAW = LABEL_LINE_HEIGHT_DRAW + WEB_LABEL_PAD_DRAW;
const LABEL_SAFE_GAP_DRAW = 2;
const LABEL_TO_DIM_GAP_DRAW = 2;

// Pre-calc label gaps using computed specs (before auto inputs)
const layoutPreset = findPresetByHText(hText);
const layoutFtMm = firstFiniteNumber(
  layoutPreset?.flange_thk_mm,
  layoutPreset?.flange_plate_thk_mm,
  layoutPreset?.flange_thk,
  layoutPreset?.flange_plate_thk,
  getThicknessMmFromSpecText(flangeOuter?.value),
  getThicknessMmFromSpecText(flangeInner?.value),
  hDims?.flangeThk
);

const layoutWtMm = firstFiniteNumber(
  layoutPreset?.web_thk_mm,
  layoutPreset?.web_plate_thk_mm,
  layoutPreset?.web_thk,
  layoutPreset?.web_plate_thk,
  getThicknessMmFromSpecText(webInput?.value),
  hDims?.webThk
);

const layoutOuterSpec = buildPlateSpec3(layoutFtMm, plateLengthMm, plateWidthMm);
const layoutInnerSpec = (Number.isFinite(innerPlateHeightMmForLayout) && innerPlateHeightMmForLayout > 0)
  ? buildPlateSpec3(layoutFtMm, plateLengthMm, innerPlateHeightMmForLayout)
  : "";
const layoutWebSpec = buildPlateSpec3(layoutWtMm, webPlateLengthMm, webPlateHeightMm);

const outerSpecForLayout = (flangeOuter && flangeOuter.value && flangeOuter.value.trim())
  ? flangeOuter.value.trim()
  : layoutOuterSpec;
const innerSpecForLayout = (flangeInner && flangeInner.value && flangeInner.value.trim())
  ? flangeInner.value.trim()
  : layoutInnerSpec;

const needOuterLabelGapDraw = outerSpecForLayout ? (LABEL_BLOCK_DRAW + LABEL_SAFE_GAP_DRAW) : 0;
const needInnerLabelGapDraw = innerSpecForLayout ? (LABEL_BLOCK_DRAW + LABEL_SAFE_GAP_DRAW) : 0;

// ============================================================
// ★ Y方向ギャップ設定（viewBox mm：固定）
// ============================================================
let plateScale = 1;

let plateDrawLength = 0;
let plateDrawHeight = 0;

let webPlateDrawLength = 0;
let webPlateDrawHeight = 0;

let plateX = 0;
let webPlateX = 0;

let plateOuterY = 0;
let plateInnerY = 0;
let webPlateY   = 0;

// ============================================================
// ★B案：文字は固定、形状とギャップは scale
//    → 固定で縮まない領域を innerHeight から先に引いて scaleY を決める
// ============================================================

  const dimCfgX = getDimCfg();
  const dimCfgY = getDimYCfg();

// 寸法の段（tier2まで使う想定）
const offTier = getDimTierOffsetsMm();
const tier2Mm = offTier.tier2;

// （ここは“実寸mm”として扱い、後で *plateScale する：＝縮む側）
const dimTopExtraMm  = estimateDimExtraMm(dimCfgX, tier2Mm);
const dimLeftExtraMm = estimateDimExtraMm(dimCfgY, tier2Mm);

// ---------- 固定（縮まない）予算：textが占有する分 ----------
// 外フランジ上面の「寸法ラベルが枠上に当たらない」ための固定余白（draw座標mm）
const TOP_TEXT_FONT_DRAW   = 4;   // 寸法文字が 4mm 想定なら 4
const TOP_TEXT_LINES       = 2;   // 2段ラベル想定
const TOP_TEXT_PAD_DRAW    = 2;   // 安全マージン
const FIX_TOP_LABEL_DRAW   = TOP_TEXT_FONT_DRAW * 1.2 * TOP_TEXT_LINES + TOP_TEXT_PAD_DRAW;

// ウェブ下面の「Web: ... ラベル」の固定余白（draw座標mm）
const fixedTextBudgetDraw =
  FIX_TOP_LABEL_DRAW + FIX_BOTTOM_LABEL_DRAW;

// ---------- 縮む（scale適用）領域の“実寸mm” ----------
// ここには「プレート高さ」「寸法線の逃げ（dimTopExtraMm）」「ギャップ（GAP_*）」を入れる
const outerH_mm = plateWidthMm;
const innerH_mm = innerPlateHeightMmForLayout;
const webH_mm   = webPlateHeightMm;     // ← layout用のweb高さ（※あなたのコードの変数に合わせる）

const maxLen_mm = Math.max(plateLengthMm, webPlateLengthMm);

// 幅側（左寸法逃げは縮む側として扱う）
const needWidthMmPerScale = (
  maxLen_mm + 2 * dimLeftExtraMm
);

// 高さ側（ギャップも縮む：＝mmで足して後で *plateScale）
const needHeightMmPerScale = (
  // Topline→gFlange
  GAP_TOPLINE_TO_GFLANGE_DRAW
  // 外フランジ：上面寸法線ゾーン
  + dimTopExtraMm
  // 外プレート
  + outerH_mm
  // 外↔内
  + GAP_GOUTER_GINNER_DRAW
  // 内プレート
  + innerH_mm
  // フランジ↔ウェブ
  + GAP_GFLANGE_GWEB_DRAW
  // ウェブ：上面寸法線ゾーン
  + dimTopExtraMm
  // ウェブプレート
  + webH_mm
  // gWeb→Bottomline
  + GAP_GWEB_TO_BOTTOMLINE_DRAW
);
// 使える高さ（固定文字ぶんを先に引く）
const baseAvailYForScaledDraw = innerHeight - fixedTextBudgetDraw;

const scaleX = (needWidthMmPerScale > 0)
  ? (innerWidth / needWidthMmPerScale)
  : 1;

const baseScaleY = (needHeightMmPerScale > 0 && baseAvailYForScaledDraw > 0)
  ? (baseAvailYForScaledDraw / needHeightMmPerScale)
  : -1;

plateScale = Math.min(scaleX, baseScaleY, 1);

let extraFixedGapDraw =
  Math.max(0, needOuterLabelGapDraw - GAP_GOUTER_GINNER_DRAW * plateScale) +
  Math.max(0, (needInnerLabelGapDraw - dimTopExtraMm * plateScale) - GAP_GFLANGE_GWEB_DRAW * plateScale);

let availYForScaledDraw = innerHeight - fixedTextBudgetDraw - extraFixedGapDraw;

let scaleY = (needHeightMmPerScale > 0 && availYForScaledDraw > 0)
  ? (availYForScaledDraw / needHeightMmPerScale)
  : -1;

plateScale = Math.min(scaleX, scaleY, 1);

const extraFixedGapDraw2 =
  Math.max(0, needOuterLabelGapDraw - GAP_GOUTER_GINNER_DRAW * plateScale) +
  Math.max(0, (needInnerLabelGapDraw - dimTopExtraMm * plateScale) - GAP_GFLANGE_GWEB_DRAW * plateScale);

if (extraFixedGapDraw2 > extraFixedGapDraw + 0.01) {
  extraFixedGapDraw = extraFixedGapDraw2;
  availYForScaledDraw = innerHeight - fixedTextBudgetDraw - extraFixedGapDraw;
  scaleY = (needHeightMmPerScale > 0 && availYForScaledDraw > 0)
    ? (availYForScaledDraw / needHeightMmPerScale)
    : -1;
  plateScale = Math.min(scaleX, scaleY, 1);
}

if (scaleY <= 0) {
  console.warn("[layout] scaleY <= 0 (insufficient height)", {
    innerHeight,
    fixedTextBudgetDraw,
    extraFixedGapDraw,
    availYForScaledDraw,
    needHeightMmPerScale,
  });
}


// --- draw寸法（縮む側） ---
plateDrawLength = plateLengthMm * plateScale;
plateDrawHeight = outerH_mm * plateScale;

const innerPlateDrawHeight_layout = innerH_mm * plateScale;

webPlateDrawLength = webPlateLengthMm * plateScale;
webPlateDrawHeight = webH_mm * plateScale;

// ============================================================
// ★互換ギャップ（draw単位）
//   既存コードが flangeGapDraw / webGapDraw を参照しているため
// ============================================================
const flangeGapDrawBase = GAP_GOUTER_GINNER_DRAW * plateScale;
const webGapDrawBase    = GAP_GFLANGE_GWEB_DRAW  * plateScale;

const dimTopExtraDraw  = dimTopExtraMm  * plateScale;
const dimLeftExtraDraw = dimLeftExtraMm * plateScale;

const needInnerToWebGapDraw = Math.max(0, needInnerLabelGapDraw + LABEL_TO_DIM_GAP_DRAW);

const gapOuterInnerDraw = Math.max(flangeGapDrawBase, needOuterLabelGapDraw);
const gapFlangeWebDraw = Math.max(webGapDrawBase, needInnerToWebGapDraw);

// compat
const flangeGapDraw = gapOuterInnerDraw;
const webGapDraw    = gapFlangeWebDraw;

// デバッグ（予算確認）
console.log("[layout] check(B-plan)", {
  innerHeight,
  fixedTextBudgetDraw,
  availYForScaledDraw,
  needHeightMmPerScale,
  extraFixedGapDraw,
  plateScale,
  scaledNeedDraw: needHeightMmPerScale * plateScale,
});

console.log("[layout] debug needHeight", {
  needHeightMmPerScale,
  dimTopExtraMm,
  outerH_mm,
  innerH_mm,
  webH_mm,
  GAP_TOPLINE_TO_GFLANGE_DRAW,
  GAP_GOUTER_GINNER_DRAW,
  GAP_GFLANGE_GWEB_DRAW,
  GAP_GWEB_TO_BOTTOMLINE_DRAW,
});

// ============================================================
// 位置決定（B案）
//   - 固定文字（上ラベル・下ラベル）は “固定で確保”
//   - ギャップ・プレート・寸法線ゾーンは “scaleで縮む”
// ============================================================

// X：センタリング + 左寸法確保
plateX = (drawingWidthMm - plateDrawLength) / 2;
plateX = Math.max(margin + dimLeftExtraDraw, plateX);
if (plateX + plateDrawLength > drawingWidthMm - margin) {
  plateX = Math.max(margin + dimLeftExtraDraw, drawingWidthMm - margin - plateDrawLength);
}

webPlateX = (drawingWidthMm - webPlateDrawLength) / 2;
webPlateX = Math.max(margin + dimLeftExtraDraw, webPlateX);
if (webPlateX + webPlateDrawLength > drawingWidthMm - margin) {
  webPlateX = Math.max(margin + dimLeftExtraDraw, drawingWidthMm - margin - webPlateDrawLength);
}

// 総高さ（draw）
const scaledBlockDraw =
  needHeightMmPerScale * plateScale;

const blockHeightDraw =
  fixedTextBudgetDraw + extraFixedGapDraw + scaledBlockDraw;

const freeY = Math.max(0, innerHeight - blockHeightDraw);
const autoPadTopRaw = (AUTO_CENTER_Y ? freeY / 2 : 0);
const autoPadTop = Math.max(0, autoPadTopRaw);

 // ??Y?Topline???
 let y = margin + autoPadTop;

// ????????????????????? margin ????
const bottomLimit = margin + innerHeight;
if (y + blockHeightDraw > bottomLimit) {
  y = Math.max(margin, bottomLimit - blockHeightDraw);
}

// ============================================================
// ★Gapを「一度だけ」計算して、以降は必ずこの変数を使う
//   - *_draw : viewBox(mm)上の描画距離
//   - 「縮むギャップ」= 元(mm) × plateScale
//   - 「縮まない領域」= FIX_* をそのまま加算
// ============================================================
const gapTopToFlangeDraw   = GAP_TOPLINE_TO_GFLANGE_DRAW   * plateScale; // ②
const gapWebToBottomDraw   = GAP_GWEB_TO_BOTTOMLINE_DRAW   * plateScale; // ⑧

 // ① 上固定ラベル領域（縮まない）
 y += FIX_TOP_LABEL_DRAW;

 // ② Topline→gFlange（縮む）
 y += gapTopToFlangeDraw;

 // ③ 外フランジ：上面寸法線ゾーン（縮む）
 y += dimTopExtraDraw;
 plateOuterY = y;

 // 外プレート
 y += plateDrawHeight;

 // ④ 外↔内（縮む）
 y += gapOuterInnerDraw;
 plateInnerY = y;

 // 内プレート
 y += innerPlateDrawHeight_layout;

 // ⑤ フランジ↔ウェブ（縮む）
 y += gapFlangeWebDraw;

 // ⑥ ウェブ：上面寸法線ゾーン（縮む）
 y += dimTopExtraDraw;
 webPlateY = y;

 // ウェブ
 y += webPlateDrawHeight;

 // ⑦ 下固定ラベル領域（縮まない）
 y += FIX_BOTTOM_LABEL_DRAW;

 // ⑧ gWeb→Bottomline（縮む）
 y += gapWebToBottomDraw;


// 最終チェック
if (y > bottomLimit + 0.01) {
  const overflow = y - bottomLimit;
  const maxShiftUp = Math.max(0, plateOuterY - margin);
  const shiftUp = Math.min(overflow, maxShiftUp);
  if (shiftUp > 0) {
    plateOuterY -= shiftUp;
    plateInnerY -= shiftUp;
    webPlateY   -= shiftUp;
    y -= shiftUp;
  }
}
if (y > bottomLimit + 0.01) {
  console.warn("[layout] overflow even after scale (B-plan)", {
    y, bottomLimit,
    plateScale,
    fixedTextBudgetDraw,
    scaledBlockDraw,
    freeY,
  });
}

  DRAG_GEOM = {
    drawingWidthMm,
    drawingHeightMm,
    margin,
    plateX,
    plateDrawLength,
    plateDrawHeight,
    plateOuterY,
    plateInnerY,
    innerPlateDrawHeight: innerPlateDrawHeight_layout,
    webPlateX,
    webPlateDrawLength,
    webPlateDrawHeight,
    webPlateY,
  };

  // Drag hit for plates area (avoid H section zone)
  const prevHitPlates = gPlates.querySelector("#sp-drag-hit-plates");
  if (prevHitPlates) prevHitPlates.remove();
  const platesHitTop = Math.max(
    margin,
    hUsedBottomDraw,
    plateOuterY - dimTopExtraDraw
  );
  const platesHitBottom = Math.min(
    drawingHeightMm - margin,
    webPlateY + webPlateDrawHeight + FIX_BOTTOM_LABEL_DRAW + gapWebToBottomDraw
  );
  const platesHitH = Math.max(0, platesHitBottom - platesHitTop);
  if (platesHitH > 0) {
    const hitP = document.createElementNS(SVG_NS, "rect");
    hitP.setAttribute("id", "sp-drag-hit-plates");
    hitP.setAttribute("x", String(margin));
    hitP.setAttribute("y", String(platesHitTop));
    hitP.setAttribute("width", String(drawingWidthMm - margin * 2));
    hitP.setAttribute("height", String(platesHitH));
    hitP.setAttribute("fill", "transparent");
    hitP.setAttribute("pointer-events", "all");
    gPlates.appendChild(hitP);
  }

  // 10) X方向の孔配置チェック用フラグ 
  const xPitchOk = Number.isFinite(colPitchMm) && colPitchMm > 0;
  const xCountOk = Number.isFinite(holeCountX) && holeCountX >= 1;
  const diaOk    = Number.isFinite(holeDiaMmFinal) && holeDiaMmFinal > 0;

  // ★ フランジ系をまとめて移動する親グループ
  const gFlange = createGroup(gPlates, "sp-g-flange", plateX, plateOuterY);

  const gFlangeWrap = ensureDragGroup(gPlates, "sp-drag-flange", "flange");
  gFlangeWrap.appendChild(gFlange);


  // ★ 外フランジ（外プレート）グループ：外プレート左上を (0,0) にする
  const gOuterWrap = ensureDragGroup(gFlange, "sp-drag-outer", "outer");
  const gOuter = createGroup(gOuterWrap, "sp-g-outer", 0, 0);

  // 外フランジ枠（←これは必要）
  const plateRect = document.createElementNS(SVG_NS, "rect");
  plateRect.setAttribute("x", "0");
  plateRect.setAttribute("y", "0");
  plateRect.setAttribute("width",  String(plateDrawLength));
  plateRect.setAttribute("height", String(plateDrawHeight));
  plateRect.setAttribute("fill", "transparent");
  plateRect.setAttribute("stroke", "#000");
  plateRect.setAttribute("stroke-width", String(DRAW_STROKE_MM));
  plateRect.setAttribute("pointer-events", "all");
  gOuter.appendChild(plateRect);

  let gInner = null; // 内フランジ用

  // 12) 外/内フランジ 左側Y寸法（2段）
  const dimYCfg = getDimYCfg();

  const yPitchDataOuter = buildFlangeYDimPitchChainMm(
    plateWidthMm,
    flangeRowPitchMm,
    nY,
    flangeRowEdgeMm
  );

  // 2段の理論位置
  const { x1, x2 } = getTwoTierXLocalForDimY(plateScale, dimYCfg);
  const cl = clampTwoTierLocalX(x1, x2, plateX, margin);
  const x1c = cl.v1;
  const x2c = cl.v2;


  if (yPitchDataOuter) {
    // 1段目：ピッチ鎖
    drawDimChainY(
      gOuter, 0,
      yPitchDataOuter.yMarksMm,
      yPitchDataOuter.labels,
      plateScale, plateX, margin, dimYCfg,
      0,
      x1c
    );

    // 2段目：全長
    drawDimChainY(
      gOuter, 0,
      [0, plateWidthMm],
      [Math.round(plateWidthMm)],
      plateScale, plateX, margin, dimYCfg,
      0,
      x2c
    );
  } else {
    // フォールバック：全長のみ
    drawDimChainY(
      gOuter, 0,
      [0, plateWidthMm],
      [Math.round(plateWidthMm)],
      plateScale, plateX, margin, dimYCfg,
      0,
      x1c
    );
  }

  // 13) 内フランジプレート（7-0）外形描画 
  let innerPlateWidthMm = null;
  let yInnerTopMm = null;

  if (
    Number.isFinite(plateWidthMm) &&
    Number.isFinite(spanYmm) &&
    spanYmm >= 0
  ) {
    // a = B - spanY
    const aInnerWidthMm = plateWidthMm - spanYmm;

    if (aInnerWidthMm > 0) {
      innerPlateWidthMm = aInnerWidthMm;

      const centerYmm = plateWidthMm / 2;
      yInnerTopMm = centerYmm - innerPlateWidthMm / 2;

      const innerPlateDrawHeight = innerPlateWidthMm * plateScale;

      // 内フランジグループ（外の下に配置）
      const gInnerWrap = ensureDragGroup(gFlange, "sp-drag-inner", "inner");
      gInner = createGroup(gInnerWrap, "sp-g-inner", 0, plateDrawHeight + flangeGapDraw);

      const innerRect = document.createElementNS(SVG_NS, "rect");
      innerRect.setAttribute("x", "0");
      innerRect.setAttribute("y", "0");
      innerRect.setAttribute("width",  String(plateDrawLength));
      innerRect.setAttribute("height", String(innerPlateDrawHeight));
      innerRect.setAttribute("fill", "transparent");
      innerRect.setAttribute("stroke", "#000");
      innerRect.setAttribute("stroke-width", String(DRAW_STROKE_MM));
      innerRect.setAttribute("pointer-events", "all");
      gInner.appendChild(innerRect);

      // 内フランジY寸法（2段）を外/ウェブと同じ方式に統一
      if (gInner && Number.isFinite(innerPlateWidthMm) && innerPlateWidthMm > 0) {
        const yPitchDataInner = buildInnerPlateYDimPitchChainMm(innerPlateWidthMm);

        const { x1, x2 } = getTwoTierXLocalForDimY(plateScale, dimYCfg);
        const cl = clampTwoTierLocalX(x1, x2, plateX, margin);
        const x1c = cl.v1;
        const x2c = cl.v2;

        if (yPitchDataInner) {
          // 1段目：ピッチ
          drawDimChainY(
            gInner, 0,
            yPitchDataInner.yMarksMm,
            yPitchDataInner.labels,
            plateScale, plateX, margin, dimYCfg,
            0,
            x1c
          );

          // 2段目：全長
          drawDimChainY(
            gInner, 0,
            [0, innerPlateWidthMm],
            [Math.round(innerPlateWidthMm)],
            plateScale, plateX, margin, dimYCfg,
            0,
            x2c
          );
        } else {
          drawDimChainY(
            gInner, 0,
            [0, innerPlateWidthMm],
            [Math.round(innerPlateWidthMm)],
            plateScale, plateX, margin, dimYCfg,
            0,
            x1c
          );
        }
      }

      console.log("[splice] inner flange plate (separated)", {
        plateWidthMm,
        rowPitchMm,
        holeCountY,
        spanYmm,
        aInnerWidthMm,
        innerPlateWidthMm,
        yInnerTopMm,
        centerYmm,
      });
    } else {
      console.warn("[splice] inner flange plate skipped (a <= 0)", {
        plateWidthMm,
        rowPitchMm,
        holeCountY,
        spanYmm,
        aInnerWidthMm,
      });
    }
  }

  // 14) 外/内フランジ孔（7-1） + 外フランジX寸法（2段）
  const plendPitchMm = fgspEnd; // プレート端側
  const htendPitchMm = fgEnd;   // H切端側

  if (xPitchOk && xCountOk && diaOk) {
    const nX = holeCountX;

    const sides = {
      bracket: { nearEndPitch: plendPitchMm, farEndPitch: htendPitchMm },
      pbeam:   { nearEndPitch: htendPitchMm, farEndPitch: plendPitchMm },
    };

    const midSpanMm = (nX > 1) ? colPitchMm * (nX - 1) : 0;

    const bracketSideLenMm =
      sides.bracket.nearEndPitch + midSpanMm + sides.bracket.farEndPitch;

    const pbeamSideLenMm =
      sides.pbeam.nearEndPitch + midSpanMm + sides.pbeam.farEndPitch;

    const xCentersMm = [];

    // 左側（柱側）
    for (let i = 0; i < nX; i++) {
      xCentersMm.push(sides.bracket.nearEndPitch + colPitchMm * i);
    }

    // 右側（梁側）
    const rightOffsetMm = bracketSideLenMm + clr;
    for (let i = 0; i < nX; i++) {
      xCentersMm.push(rightOffsetMm + sides.pbeam.nearEndPitch + colPitchMm * i);
    }

    const holeRadius = (holeDiaMmFinal / 2) * plateScale;

    xCentersMm.forEach((xMm) => {
      const cxLocal = xMm * plateScale;

      // 外フランジ（外プレート）
      yCentersMm.forEach((yMm) => {
        const cyOuterLocal = yMm * plateScale;
        drawSpliceHole(gOuter, cxLocal, cyOuterLocal, holeRadius);
      });

      // 内フランジ（内プレート）※現状は中央1列
      if (gInner && Number.isFinite(innerPlateWidthMm) && innerPlateWidthMm > 0) {
        const yLocalCenterMm = innerPlateWidthMm / 2;
        const cyInnerLocal   = yLocalCenterMm * plateScale;
        drawSpliceHole(gInner, cxLocal, cyInnerLocal, holeRadius);
      }
    });

    // 外フランジ：上側X寸法（2段）
    const dimCfg = getDimCfg();


    const dimPitchX = buildFlangeOuterXDimPitchMm(
      plendPitchMm, // fgsp
      colPitchMm,   // Px
      nX,           // 孔数X
      htendPitchMm, // fg
      clr           // クリアランス
    );

    if (dimPitchX) {
    const off = getDimTierOffsetsMm();
    const y1 = calcDimLineYLocal_X(0, plateScale, dimCfg, off.tier1);
    const y2 = calcDimLineYLocal_X(0, plateScale, dimCfg, off.tier2);

      const clY = clampTwoTierLocalY_ForDimX_Text(y1, y2, plateOuterY, margin, plateScale, dimCfg);
      const y1c = clY.v1;
      const y2c = clY.v2;

      // 1段目：ピッチ
      drawDimChainX(
        gOuter, 0,
        dimPitchX.xMarksMm, dimPitchX.labels,
        plateScale, plateOuterY, margin, dimCfg,
        0,
        y1c
      );

      // 2段目：全長
      drawDimChainX(
        gOuter, 0,
        [0, dimPitchX.totalMm], [Math.round(dimPitchX.totalMm)],
        plateScale, plateOuterY, margin, dimCfg,
        0,
        y2c
      );
    }

    console.log("[splice] draw holes (outer & inner)", {
      nX,
      nY,
      colPitchMm,
      rowPitchMm,
      htendPitchMm,
      plendPitchMm,
      clearanceMm,
      midSpanMm,
      sides,
      bracketSideLenMm,
      pbeamSideLenMm,
      holeDiaMmFinal,
      plateWidthMm,
      plateLengthMm,
      xCentersMm,
      yCentersMm,
      plateScale,
      innerPlateWidthMm,
      yInnerTopMm,
    });
  }

  // 15) ウェブプレート（7-2）外形・孔・寸法 
  // ※ここでは「確定済みの webHole / webPlEndPitchMm / webHtEndPitchMm / webClearanceMm /
  //            webPlateLengthMm / webPlateHeightMm」を使って描画するだけ

  const webColPitchOk = Number.isFinite(webHole.colPitchMm) && webHole.colPitchMm > 0;
  const webCountXOk   = Number.isFinite(webHole.holeCountX) && webHole.holeCountX >= 1;
  const webRowPitchOk = Number.isFinite(webHole.rowPitchMm) && webHole.rowPitchMm > 0;
  const webCountYOk   = Number.isFinite(webHole.holeCountY) && webHole.holeCountY >= 1;
  const webDiaOk      = Number.isFinite(webHole.holeDiaMm) && webHole.holeDiaMm > 0;
  const webRowEdgeMm = Number.isFinite(webHole.webspYEndPitchMm)
    ? webHole.webspYEndPitchMm
    : webPlEndPitchMm;

  webPlateDrawLength = webPlateLengthMm * plateScale;
  webPlateDrawHeight = webPlateHeightMm * plateScale;

  let gWeb = null;
  let webHoleCountYActual = null;
  if (Number.isFinite(webPlateDrawLength) && Number.isFinite(webPlateDrawHeight)) {
    const gWebWrap = ensureDragGroup(gPlates, "sp-drag-web", "web");
    gWeb = createGroup(gWebWrap, "sp-g-web", webPlateX, webPlateY);

    const webPlateRect = document.createElementNS(SVG_NS, "rect");
    webPlateRect.setAttribute("x", "0");
    webPlateRect.setAttribute("y", "0");
    webPlateRect.setAttribute("width",  String(webPlateDrawLength));
    webPlateRect.setAttribute("height", String(webPlateDrawHeight));
    webPlateRect.setAttribute("fill", "transparent");
    webPlateRect.setAttribute("stroke", "#000");
    webPlateRect.setAttribute("stroke-width", String(DRAW_STROKE_MM));
    webPlateRect.setAttribute("pointer-events", "all");
    gWeb.appendChild(webPlateRect);
  }

  // ウェブ孔（中心合わせ）
  if (gWeb && webColPitchOk && webCountXOk && webDiaOk) {
    const nX = Math.trunc(webHole.holeCountX);
    const colP = webHole.colPitchMm;

    const midSpanX = (nX > 1) ? colP * (nX - 1) : 0;
    const a = webPlEndPitchMm + midSpanX + webHtEndPitchMm;

    const xCentersMm = [];

    for (let i = 0; i < nX; i++) {
      xCentersMm.push(webPlEndPitchMm + colP * i);
    }

    const rightOffsetMm = a + webClearanceMm;
    for (let i = 0; i < nX; i++) {
      xCentersMm.push(rightOffsetMm + webHtEndPitchMm + colP * i);
    }

    let yCentersWebMm = [];
    if (webRowPitchOk && webCountYOk) {
      const nY = Math.trunc(webHole.holeCountY);
      const rowP = webHole.rowPitchMm;
      const spanY = (nY > 1) ? rowP * (nY - 1) : 0;
      const startY = Number.isFinite(webRowEdgeMm) ? webRowEdgeMm : (webPlateHeightMm - spanY) / 2;
      for (let j = 0; j < nY; j++) {
        yCentersWebMm.push(startY + rowP * j);
      }
    } else {
      yCentersWebMm = [webPlateHeightMm / 2];
    }
    webHoleCountYActual = yCentersWebMm.length;

    const holeRadius = (webHole.holeDiaMm / 2) * plateScale;

    xCentersMm.forEach((xMm) => {
      const cxLocal = xMm * plateScale;
      yCentersWebMm.forEach((yMm) => {
        const cyLocal = yMm * plateScale;
        drawSpliceHole(gWeb, cxLocal, cyLocal, holeRadius);
      });
    });

    console.log("[splice] draw web holes(centered)", {
      webPlateLengthMm,
      webPlateHeightMm,
      xCentersMm,
      yCentersWebMm,
    });
  }

  // ウェブ：上側X寸法（2段）
  if (gWeb && webColPitchOk && webCountXOk) {
    const dimCfg = getDimCfg();
    const nX = Math.trunc(webHole.holeCountX);

    const dimPitchXWeb = buildFlangeOuterXDimPitchMm(
      webPlEndPitchMm,
      webHole.colPitchMm,
      nX,
      webHtEndPitchMm,
      webClearanceMm
    );

    if (dimPitchXWeb) {
    const off = getDimTierOffsetsMm();
    const y1 = calcDimLineYLocal_X(0, plateScale, dimCfg, off.tier1);
    const y2 = calcDimLineYLocal_X(0, plateScale, dimCfg, off.tier2);

      const clY = clampTwoTierLocalY_ForDimX_Text(y1, y2, webPlateY, margin, plateScale, dimCfg);
      const y1c = clY.v1;
      const y2c = clY.v2;

      drawDimChainX(
        gWeb, 0,
        dimPitchXWeb.xMarksMm, dimPitchXWeb.labels,
        plateScale, webPlateY, margin, dimCfg,
        0,
        y1c
      );

      drawDimChainX(
        gWeb, 0,
        [0, dimPitchXWeb.totalMm], [Math.round(dimPitchXWeb.totalMm)],
        plateScale, webPlateY, margin, dimCfg,
        0,
        y2c
      );
    }
  }

  // ウェブ：左側Y寸法（2段）
  if (gWeb && webRowPitchOk && webCountYOk) {
    const dimYCfg = getDimYCfg();
    const nY = Number.isFinite(webHoleCountYActual)
      ? Math.trunc(webHoleCountYActual)
      : Math.trunc(webHole.holeCountY);

    const yPitchDataWeb = buildFlangeYDimPitchChainMm(
      webPlateHeightMm,
      webHole.rowPitchMm,
      nY,
      webRowEdgeMm
    );

  const { x1, x2 } = getTwoTierXLocalForDimY(plateScale, dimYCfg);
  const cl = clampTwoTierLocalX(x1, x2, webPlateX, margin);
  const x1c = cl.v1;
  const x2c = cl.v2;

    if (yPitchDataWeb) {
      drawDimChainY(
        gWeb, 0,
        yPitchDataWeb.yMarksMm,
        yPitchDataWeb.labels,
        plateScale, webPlateX, margin, dimYCfg,
        0,
        x1c
      );

      if (Number.isFinite(webHoleCountYActual) && webHoleCountYActual !== Math.trunc(webHole.holeCountY)) {
        console.warn("[splice] web Y dim count mismatch; using actual hole count", {
          holeCountY: webHole.holeCountY,
          actual: webHoleCountYActual
        });
      }

      drawDimChainY(
        gWeb, 0,
        [0, webPlateHeightMm],
        [Math.round(webPlateHeightMm)],
        plateScale, webPlateX, margin, dimYCfg,
        0,
        x2c
      );
    } else {
      drawDimChainY(
        gWeb, 0,
        [0, webPlateHeightMm],
        [Math.round(webPlateHeightMm)],
        plateScale, webPlateX, margin, dimYCfg,
        0,
        x1c
      );
    }
  }

  // 16) 7-3 仕様入力へ反映（外/内フランジ・ウェブ） + ラベル
  const preset = findPresetByHText(hText);

  const ftMm = firstFiniteNumber(
    preset?.flange_thk_mm,
    preset?.flange_plate_thk_mm,
    preset?.flange_thk,
    preset?.flange_plate_thk,
    getThicknessMmFromSpecText(flangeOuter?.value),
    getThicknessMmFromSpecText(flangeInner?.value),
    hDims?.flangeThk
  );

  const wtMm = firstFiniteNumber(
    preset?.web_thk_mm,
    preset?.web_plate_thk_mm,
    preset?.web_thk,
    preset?.web_plate_thk,
    getThicknessMmFromSpecText(webInput?.value),
    hDims?.webThk
  );

  console.log("[splice] 7-3 spec inputs", {
    hText,
    preset,
    ftMm,
    wtMm,
    plateLengthMm,
    plateWidthMm,
    innerPlateWidthMm,
    webPlateLengthMm,
    webPlateHeightMm,
  });

  const outerSpec = buildPlateSpec3(ftMm, plateLengthMm, plateWidthMm);

  const innerSpec = (Number.isFinite(innerPlateWidthMm) && innerPlateWidthMm > 0)
    ? buildPlateSpec3(ftMm, plateLengthMm, innerPlateWidthMm)
    : "";

  const webSpec = buildPlateSpec3(wtMm, webPlateLengthMm, webPlateHeightMm);

  console.log("[splice] 7-3 built specs", { outerSpec, innerSpec, webSpec });

  setAutoSpecValue(flangeOuter, outerSpec);
  setAutoSpecValue(flangeInner, innerSpec);
  setAutoSpecValue(webInput, webSpec);

  const flangeOuterText = flangeOuter ? flangeOuter.value.trim() : "";
  const flangeInnerText = flangeInner ? flangeInner.value.trim() : "";
  const webText         = webInput     ? webInput.value.trim()     : "";

  // Hサイズラベル（図面内の左下へ配置）
  if (hText) {
    const label = document.createElementNS(SVG_NS, "text");
    const padX = 6;
    const padY = 4;
    label.setAttribute("x", String(margin + padX));
    label.setAttribute("y", String(drawingHeightMm - margin - padY));
    label.setAttribute("text-anchor", "start");
    label.setAttribute("dominant-baseline", "alphabetic");
    label.setAttribute("font-size", "6");
    label.textContent = `${hText}用スプライスプレート`;
    root.appendChild(label);
  }

  // -----------------------------
  // ★プレート個別ラベル（左下・左上基準で配置）
  // -----------------------------
  const LABEL_PAD_X = 2;   // 左端から少し右へ (mm, ローカル)
  const LABEL_PAD_Y = 1;   // 下端から少し下へ (mm, ローカル)
  const LABEL_FONT  = 4;

  function addPlateLabel(g, x, y, text) {
    if (!g || !text) return;
    const t = document.createElementNS(SVG_NS, "text");
    t.setAttribute("x", String(x));
    t.setAttribute("y", String(y));
    t.setAttribute("text-anchor", "start");            // 左上基準（X）
    t.setAttribute("dominant-baseline", "hanging");    // 左上基準（Y）
    t.setAttribute("font-size", String(LABEL_FONT));
    t.textContent = text;
    g.appendChild(t);
  }

  // 外フランジ（外プレート）左下ラベル
  if (flangeOuterText) {
    addPlateLabel(
      gOuter,
      LABEL_PAD_X,
      plateDrawHeight + LABEL_PAD_Y,
      `OuterFlange: ${flangeOuterText}`
    );
  }

  // 内フランジ（内プレート）左下ラベル
  const innerDrawH = (Number.isFinite(innerPlateWidthMm) && innerPlateWidthMm > 0)
    ? innerPlateWidthMm * plateScale
    : NaN;

  if (gInner && Number.isFinite(innerDrawH) && flangeInnerText) {
    addPlateLabel(
      gInner,
      LABEL_PAD_X,
      innerDrawH + LABEL_PAD_Y,
      `InnerFlange: ${flangeInnerText}`
    );
  }

  // ウェブプレート左下ラベル
  if (gWeb && webText) {
    addPlateLabel(
      gWeb,
      LABEL_PAD_X,
      webPlateDrawHeight + LABEL_PAD_Y,
      `Web: ${webText}`
    );
  }

  console.log("[splice] drawSplicePreviewFromForm: 使用行の内容", {
    hText,
    flangeOuterText,
    flangeInnerText,
    webText,
    hDims,
  });

  // 自動上下センタリング（保存済みドラッグが無い場合のみ）
  applyAllDragTransforms();
  if (!hasStoredDrag) {
    autoCenterDrawRootY(svg, margin, drawingHeightMm);
  }
}

// ============================================================
// Hサイズ入力リスナー / プリセット適用
// ============================================================

function setupHSizeListeners() {
  const inputs = qsa('input[name="h_size[]"]');
  inputs.forEach(input => {
    if (input.dataset.bound === "1") return;
    input.dataset.bound = "1";
    input.addEventListener("change", onHSizeChange);
  });
}

function onHSizeChange(e) {
  const input = e.target;
  const rawHSize = input.value;
  const hSize = normalizeHSizeKey(rawHSize);
  const tr = input.closest("tr");

  console.log("[splice] Hサイズ変更: raw=", rawHSize, " -> normalized=", hSize);

  if (!tr || !hSize) return;

  if (!autoPresetEnabled) {
    console.log("[splice] 自動プリセットOFFのため適用スキップ");
    return;
  }

  const presets = getSplicePresets();

  const key1 = hSize;
  const key2 = hSize.replace(/^H-?/i, "H");
  const key3 = hSize.replace(/^H-?/i, "");

  const preset =
    presets[key1] ||
    presets[key2] ||
    presets[key3];

  console.log("[splice] preset lookup:", {
    hSize,
    key1,
    key2,
    key3,
    found: !!preset
  });

  if (!preset) {
    console.log("[splice] プリセット無し（この H サイズには自動設定しない）");
    return;
  }

  // 共通preset
  setAutoValueById("sp-common-flange-end-pitch-mm",     preset.common_flange_end_pitch);
  setAutoValueById("sp-common-flangesp-end-pitch-mm",  preset.common_flangesp_end_pitch);
  setAutoValueById("sp-common-web-end-pitch-mm",       preset.common_web_end_pitch);
  setAutoValueById("sp-common-websp-x-end-pitch-mm",   preset.common_websp_x_end_pitch);
  setAutoValueById("sp-common-websp-y-end-pitch-mm",   preset.common_websp_y_end_pitch);
  setAutoValueById("sp-common-clearance-mm",           preset.common_clearance);

  // flange用preset（共通フォーム）
  setAutoValueById("sp-flange-col-pitch-mm",     preset.flange_col_pitch);
  setAutoValueById("sp-flange-row-pitch-mm",     preset.flange_row_pitch);
  setAutoValueById("sp-flange-hole-count-x",     preset.flange_hole_count_x);
  setAutoValueById("sp-flange-hole-count-y",     preset.flange_hole_count_y);
  setAutoValueById("sp-flange-hole-dia-mm",      preset.flange_hole_dia);
  setAutoValueById(
    "sp-flange-row-edge-mm",
    preset.flange_row_edge_pitch ??
    preset.flange_row_edge_mm ??
    preset.common_flangesp_end_pitch ??
    preset.common_flange_end_pitch
  );

  // web用preset（共通フォーム）
  setAutoValueById("sp-web-col-pitch-mm",        preset.web_col_pitch);
  setAutoValueById("sp-web-row-pitch-mm",        preset.web_row_pitch);
  setAutoValueById("sp-web-hole-count-x",        preset.web_hole_count_x);
  setAutoValueById("sp-web-hole-count-y",        preset.web_hole_count_y);
  setAutoValueById("sp-web-hole-dia-mm",         preset.web_hole_dia);

  // 行入力（旧互換あり）
  const holeDiaInp  = qs('input[name="hole_dia[]"]', tr);

  const holeCntXInp =
    qs('input[name="hole_count_x[]"]', tr) ||
    qs('input[name="hole_count[]"]', tr);

  const holeCntYInp =
    qs('input[name="hole_count_y[]"]', tr);

  const colPitchInp = qs('input[name="col_pitch[]"]', tr);
  const rowPitchInp = qs('input[name="row_pitch[]"]', tr);

  const presetHoleCountX =
    (preset.hole_count_x != null)
      ? preset.hole_count_x
      : preset.hole_count;

  setAutoValue(holeCntXInp, presetHoleCountX);

  if (holeCntYInp && !holeCntYInp.value && preset.hole_count_y != null) {
    holeCntYInp.value = String(preset.hole_count_y);
  }

  const pCol = preset.flange_col_pitch ?? preset.col_pitch;
  const pRow = preset.flange_row_pitch ?? preset.row_pitch;
  const pDia = preset.flange_hole_dia ?? preset.hole_dia;

  setAutoValue(colPitchInp, pCol);
  setAutoValue(rowPitchInp, pRow);
  setAutoValue(holeDiaInp, pDia);

  // Hサイズ変更に合わせて簡易プレビュー更新
  updateHoleGridInputs();
  drawSplicePreviewFromForm(tr);
}

function autoCenterDrawRootY(svg, marginMm, drawingHeightMm) {
  if (!AUTO_CENTER_Y) return;
  if (!svg) return;
  const root = getDrawRoot(svg);
  if (!root) return;

  let bbox;
  try {
    bbox = root.getBBox();
  } catch (err) {
    return;
  }
  if (!bbox || !Number.isFinite(bbox.height) || bbox.height <= 0) return;

  const targetTop = Number.isFinite(marginMm) ? marginMm : 0;
  const targetBottom = Number.isFinite(drawingHeightMm) ? (drawingHeightMm - marginMm) : null;
  if (!Number.isFinite(targetBottom) || targetBottom <= targetTop) return;

  const targetCenter = (targetTop + targetBottom) / 2;
  const bboxCenter = bbox.y + bbox.height / 2;
  const delta = targetCenter - bboxCenter;

  if (Math.abs(delta) < 0.01) return;

  DRAW_ROOT_STATE.offsetY += delta;
  updateDrawRootTransform();
}

// ============================================================
// テーブル行関連
// ============================================================

function renumberSpRows() {
  const tbody = getSpRowsTbody();
  if (!tbody) return;

  const trs = qsa("tr", tbody);
  trs.forEach((tr, idx) => {
    const noCell = tr.querySelector("td:first-child");
    if (noCell) noCell.textContent = String(idx + 1);
  });
}

function clearErrorHighlights() {
  qsa(".sp-error-cell").forEach(td => td.classList.remove("sp-error-cell"));
}

function validateSpliceForm() {
  const tbody = getSpRowsTbody();
  if (!tbody) return { ok: true, messages: [] };

  clearErrorHighlights();

  const trs = qsa("tr", tbody);
  const errors = [];

  trs.forEach((tr, idx) => {
    const rowNo = idx + 1;

    const hInput        = tr.querySelector('input[name="h_size[]"]');
    const setInput      = tr.querySelector('input[name="set_count[]"]');
    const flangeOuterInput =
      tr.querySelector('input[name="flange_plate_outer[]"]') ||
      tr.querySelector('input[name="flange_plate[]"]');

    const flangeInnerInput =
      tr.querySelector('input[name="flange_plate_inner[]"]');

    const webInput         = tr.querySelector('input[name="web_plate[]"]');
    const holeDiaInput     = tr.querySelector('input[name="hole_dia[]"]');
    const holeCountXInput =
      tr.querySelector('input[name="hole_count_x[]"]') ||
      tr.querySelector('input[name="hole_count[]"]');

    const holeCountYInput =
      tr.querySelector('input[name="hole_count_y[]"]');

    const colPitchInput    = tr.querySelector('input[name="col_pitch[]"]');
    const rowPitchInput    = tr.querySelector('input[name="row_pitch[]"]');
    const remarksInput     = tr.querySelector('input[name="remarks[]"]');

    const vals = [
      hInput, setInput,
      flangeOuterInput, flangeInnerInput, webInput,
      holeDiaInput, holeCountXInput, holeCountYInput,
      colPitchInput, rowPitchInput, remarksInput
    ].map(inp => (inp && inp.value) ? inp.value.trim() : "");

    const isBlank = vals.every(v => v === "");
    if (isBlank) return;

    if (hInput && !hInput.value.trim()) {
      const td = hInput.closest("td");
      if (td) td.classList.add("sp-error-cell");
      errors.push(`行${rowNo}: H型鋼サイズを入力してください。`);
    }

    if (setInput && setInput.value.trim() !== "") {
      const n = Number(setInput.value);
      if (!Number.isInteger(n) || n <= 0) {
        const td = setInput.closest("td");
        if (td) td.classList.add("sp-error-cell");
        errors.push(`行${rowNo}: セット数は1以上の整数で入力してください。`);
      }
    }

    if (holeCountXInput && holeCountXInput.value.trim() !== "") {
      const n = Number(holeCountXInput.value);
      if (!Number.isInteger(n) || n < 0) {
        const td = holeCountXInput.closest("td");
        if (td) td.classList.add("sp-error-cell");
        errors.push(`行${rowNo}: 孔数(X)は0以上の整数で入力してください。`);
      }
    }

    if (holeCountYInput && holeCountYInput.value.trim() !== "") {
      const n = Number(holeCountYInput.value);
      if (!Number.isInteger(n) || n < 0) {
        const td = holeCountYInput.closest("td");
        if (td) td.classList.add("sp-error-cell");
        errors.push(`行${rowNo}: 孔数(Y)は0以上の整数で入力してください。`);
      }
    }
  });

  return {
    ok: errors.length === 0,
    messages: errors
  };
}

function setupRowActionHandlers() {
  const tbody = getSpRowsTbody();
  if (!tbody) return;

  tbody.addEventListener("click", (e) => {
    const copyBtn = e.target.closest(".sp-row-copy, .sp-type-row-copy");
    const delBtn  = e.target.closest(".sp-row-delete, .sp-type-row-delete");

    if (copyBtn) {
      const tr = copyBtn.closest("tr");
      if (!tr) return;

      const newTr = tr.cloneNode(true);

      const hInputs = newTr.querySelectorAll('input[name="h_size[]"]');
      hInputs.forEach(inp => { inp.dataset.bound = ""; });

      newTr.querySelectorAll(".sp-error-cell").forEach(td => {
        td.classList.remove("sp-error-cell");
      });

      tr.after(newTr);

      setupHSizeListeners();
      renumberSpRows();

      updateHoleGridInputs();
      drawSplicePreviewFromForm();
      return;
    }

    if (delBtn) {
      const tr = delBtn.closest("tr");
      if (!tr) return;

      tr.remove();
      renumberSpRows();

      drawSplicePreviewFromForm();
      return;
    }
  });
}

function setupHZoomControls() {
  const plusBtn   = qs("#sp-h-zoom-plus");
  const minusBtn  = qs("#sp-h-zoom-minus");
  const slider    = qs("#sp-h-zoom-slider");

  if (!plusBtn || !minusBtn || !slider) return;

  function sliderValueToZoom() {
    const v = Number(slider.value) || 100;
    return Math.min(3.0, Math.max(0.5, v / 100));
  }

  function applyZoomFromSlider() {
    H_ZOOM_STATE.zoom = sliderValueToZoom();
    renderHSectionZoomIndicator();
  }

  slider.addEventListener("input", applyZoomFromSlider);

  plusBtn.addEventListener("click", () => {
    const current = H_ZOOM_STATE.zoom || 1.0;
    let next = current + 0.25;
    if (next > 3.0) next = 3.0;
    H_ZOOM_STATE.zoom = next;
    slider.value = String(Math.round(next * 100));
    renderHSectionZoomIndicator();
  });

  minusBtn.addEventListener("click", () => {
    const current = H_ZOOM_STATE.zoom || 1.0;
    let next = current - 0.25;
    if (next < 0.5) next = 0.5;
    H_ZOOM_STATE.zoom = next;
    slider.value = String(Math.round(next * 100));
    renderHSectionZoomIndicator();
  });

  H_ZOOM_STATE.zoom = sliderValueToZoom();
}

// ============================================================
// DOMContentLoaded
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;

  initSpliceDrawingCanvas();

  const dragModeSelect = qs("#sp-drag-mode");
  if (dragModeSelect) {
    dragMode = dragModeSelect.value || DRAG_MODE.ALL;
    dragModeSelect.addEventListener("change", () => {
      dragMode = dragModeSelect.value || DRAG_MODE.ALL;
      if (dragMode === DRAG_MODE.OFF) {
        DRAG_SESSION.dragging = false;
      }
      const nextKey = getDefaultKeyForMode();
      if (nextKey) activeDragTargetKey = nextKey;
    });
  }

  // 孔芯十字線トグル
  const holeCrossToggle = qs("#sp-hole-cross-toggle");
  const holeCrossHidden = qs("#sp-hole-cross-print");
  if (holeCrossToggle) {
    // hidden の値があればそれを優先（印刷プレビュー用）
    if (holeCrossHidden && String(holeCrossHidden.value || "").trim() !== "") {
      const v = String(holeCrossHidden.value || "").trim().toLowerCase();
      holeCrossToggle.checked = (v === "1" || v === "true" || v === "on" || v === "yes");
    }
    holeCenterCrossEnabled = holeCrossToggle.checked;

    holeCrossToggle.addEventListener("change", () => {
      holeCenterCrossEnabled = holeCrossToggle.checked;
      if (holeCrossHidden) {
        holeCrossHidden.value = holeCenterCrossEnabled ? "1" : "0";
      }
      console.log("[splice] holeCenterCrossEnabled =", holeCenterCrossEnabled);
      drawSplicePreviewFromForm();
    });

    if (holeCrossHidden && String(holeCrossHidden.value || "").trim() === "") {
      holeCrossHidden.value = holeCrossToggle.checked ? "1" : "0";
    }
  }

  // 初回プレビュー
  drawSplicePreviewFromForm();
  updateHoleGridInputs();

  // ドラッグ保存用セッションIDをフォームに設定
  const existingSessionId = body?.dataset?.dragSessionId;
  const dragSessionId = existingSessionId || getDragSessionId();
  if (!existingSessionId) {
    document.body.dataset.dragSessionId = dragSessionId;
  }
  const dragSessionInput = qs("#sp-drag-session-id");
  if (dragSessionInput) {
    dragSessionInput.value = dragSessionId;
  }
  // 編集画面ではセッション内の保存キーを初期化（未ドラッグ時の印刷がずれないように）
  if (body && body.classList.contains("sp-edit-mode")) {
    try {
      localStorage.removeItem(getDragStoreKey());
    } catch (_) {
      // ignore
    }
  }

  // 初期表示値を autoVal として刻む（初回プリセット適用の前）
  [
    "sp-common-flange-end-pitch-mm",
    "sp-common-flangesp-end-pitch-mm",
    "sp-common-clearance-mm",
  ].forEach(markInitialAutoValById);

  const layoutMain  = qs("#sp-layout-main");
  const drawingArea = qs("#sp-drawing-area");
  const dataArea    = qs("#sp-data-area");

  if (layoutMain && drawingArea && dataArea && body && body.classList.contains("sp-edit-mode")) {
    const drawingRatio = parseFloat(body.dataset.drawingRatio || "0.7");
    const dataRatio    = parseFloat(body.dataset.dataRatio || "0.3");

    layoutMain.style.display = "flex";
    layoutMain.style.flexDirection = "column";

    drawingArea.style.flex = drawingRatio.toString();
    dataArea.style.flex    = dataRatio.toString();

    console.log("🧮 layout ratios:", { drawingRatio, dataRatio });
  }

  // プロファイル切り替え
  const profileSelect = qs("#sp-profile-select");
  if (profileSelect) {
    profileSelect.addEventListener("change", () => {
      const key = profileSelect.value;
      const url = new URL(window.location.href);
      url.searchParams.set("profile", key);
      window.location.href = url.toString();
    });
  }

  // 自動プリセットON/OFF
  const autoPresetToggle = qs("#sp-auto-preset-toggle");
  if (autoPresetToggle) {
    autoPresetEnabled = autoPresetToggle.checked;

    autoPresetToggle.addEventListener("change", () => {
      autoPresetEnabled = autoPresetToggle.checked;
      console.log("[splice] autoPresetEnabled =", autoPresetEnabled);
    });
  }

  // 行追加
  const addRowBtn = qs("#sp-add-row-btn");
  const tbody     = getSpRowsTbody();

  // 既存行の plate欄の初期値を autoSpec として刻む
  if (tbody) qsa("tr", tbody).forEach(markInitialAutoSpecByRow);

  if (addRowBtn && tbody) {
    addRowBtn.addEventListener("click", () => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td></td>
        <td><input type="text" name="h_size[]" list="h_size_list" style="width: 90%;"></td>
        <td><input type="number" name="set_count[]" min="1" style="width: 60px;"></td>
        <td><input type="text" name="flange_plate_outer[]" placeholder="t×B×L" style="width: 95%;"></td>
        <td><input type="text" name="flange_plate_inner[]" placeholder="t×B×L" style="width: 95%;"></td>
        <td><input type="text" name="web_plate[]" placeholder="t×B×L" style="width: 95%;"></td>
        <td><input type="text" name="hole_dia[]" style="width: 60px;"></td>
        <td><input type="text" name="flange_holes_outer[]" style="width: 90%;"></td>
        <td><input type="text" name="flange_holes_inner[]" style="width: 90%;"></td>
        <td><input type="text" name="web_holes[]" style="width: 90%;"></td>
        <td>
          <input type="text" name="remarks[]" style="width: 95%;">
          <input type="hidden" name="hole_count_x[]" value="">
          <input type="hidden" name="hole_count_y[]" value="">
          <input type="hidden" name="col_pitch[]" value="">
          <input type="hidden" name="row_pitch[]" value="">
        </td>
        <td>
          <button type="button" class="sp-type-row-copy">複製</button>
          <button type="button" class="sp-type-row-delete">削除</button>
        </td>
      `;
      tbody.appendChild(tr);

      renumberSpRows();
      updateHoleGridInputs();
      drawSplicePreviewFromForm(tr);
    });
  }

  // 既存行への「初回プリセット適用」
  if (tbody && autoPresetEnabled) {
    qsa("tr", tbody).forEach(tr => {
      const hInput = qs('input[name="h_size[]"]', tr);
      if (!hInput) return;
      if (!hInput.value) return;
      onHSizeChange({ target: hInput });
    });
  }

  setupHSizeListeners();
  setupRowActionHandlers();
  setupHZoomControls();
  renumberSpRows();

  // Enter によるフォーム送信を抑止（入力消失対策）
  const formEl = document.querySelector("form");
  if (formEl && body && body.classList.contains("sp-edit-mode")) {
    formEl.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && e.target && e.target.matches("input, select")) {
        e.preventDefault();
        e.target.blur();
      }
    });
  }

  // 共通フォーム変更でプレビュー更新
  [
    "#sp-common-flange-end-pitch-mm",
    "#sp-common-flangesp-end-pitch-mm",
    "#sp-common-clearance-mm",
    "#sp-flange-col-pitch-mm",
    "#sp-flange-row-pitch-mm",
    "#sp-flange-hole-count-x",
    "#sp-flange-hole-count-y",
    "#sp-flange-hole-dia-mm",
    "#sp-flange-row-edge-mm",
    "#sp-web-hole-count-x",
    "#sp-web-hole-count-y",
    "#sp-dim-font-mm",
    "#sp-dim-tier1-mm",
    "#sp-dim-tier2-denom",
  ].forEach((sel) => {
    const el = qs(sel);
    if (!el) return;
    el.addEventListener("input", () => {
      updateHoleGridInputs();
      drawSplicePreviewFromForm();
    });
  });

  console.log("SPLICE_PRESETS[H-400x200x8x13] =", window.SPLICE_PRESETS?.["H-400x200x8x13"]);
});
