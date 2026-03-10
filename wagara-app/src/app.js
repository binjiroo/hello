import { PATTERN_REGISTRY } from "./modules/registry.js";
import { createInitialState, clone, History } from "./state.js";
import { showToast, setCanvasSize, clearCanvas } from "./ui.js";

const $ = (sel) => document.querySelector(sel);

const STORAGE_LAST = "wagara:lastState";
const STORAGE_PRESETS = "wagara:presets";

const canvasMain = $("#canvasMain");
const canvasTile = $("#canvasTile");
const ctxMain = canvasMain.getContext("2d");
const ctxTile = canvasTile.getContext("2d");

const patternListEl = $("#patternList");
const controlsRoot = $("#controlsRoot");

const lblCurrentPattern = $("#lblCurrentPattern");
const lblMainInfo = $("#lblMainInfo");
const lblTileInfo = $("#lblTileInfo");

const inpSeed = $("#inpSeed");
const inpBg = $("#inpBg");
const inpFg = $("#inpFg");

const selPreset = $("#selPreset");
const inpPresetName = $("#inpPresetName");
const btnPresetSave = $("#btnPresetSave");
const btnPresetLoad = $("#btnPresetLoad");
const btnPresetDelete = $("#btnPresetDelete");

const selCanvasSize = $("#selCanvasSize");
const selPatternTile = $("#selPatternTile");

const btnNew = $("#btnNew");
const btnOpen = $("#btnOpen");
const btnSave = $("#btnSave");
const btnExportPng = $("#btnExportPng");
const btnUndo = $("#btnUndo");
const btnRedo = $("#btnRedo");
const btnRandomize = $("#btnRandomize");
const fileOpenInput = $("#fileOpenInput");

let state = createInitialState();
const history = new History(60);

let currentModule = null;
let currentModuleDisposeUI = null;

let renderQueued = false;
let saveTimer = null;

let presets = [];

function loadLastState() {
  try {
    const raw = localStorage.getItem(STORAGE_LAST);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || !parsed.app || !parsed.common || !parsed.patterns) return null;
    return parsed;
  } catch {
    return null;
  }
}

function saveLastState(stateToSave) {
  try {
    localStorage.setItem(STORAGE_LAST, JSON.stringify(stateToSave));
  } catch {}
}

function scheduleSave() {
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    saveTimer = null;
    saveLastState(state);
  }, 250);
}

function loadPresets() {
  try {
    const raw = localStorage.getItem(STORAGE_PRESETS);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function savePresets() {
  try {
    localStorage.setItem(STORAGE_PRESETS, JSON.stringify(presets));
  } catch {}
}

function refreshPresetSelect() {
  if (!selPreset) return;
  selPreset.innerHTML = "";
  if (presets.length === 0) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "(no presets)";
    selPreset.appendChild(opt);
    return;
  }
  for (const p of presets) {
    const opt = document.createElement("option");
    opt.value = p.name;
    opt.textContent = p.name;
    selPreset.appendChild(opt);
  }
}

function syncCommonUI() {
  inpSeed.value = String(state.common.seed);
  inpBg.value = state.common.bg;
  inpFg.value = state.common.fg;
}

function bindPresetUI() {
  if (!selPreset || !inpPresetName || !btnPresetSave || !btnPresetLoad || !btnPresetDelete) return;
  presets = loadPresets();
  refreshPresetSelect();

  btnPresetSave.addEventListener("click", () => {
    const name = (inpPresetName.value || "").trim() ||
      `Preset ${new Date().toISOString().slice(0, 19).replace("T", " ")}`;
    const existing = presets.findIndex(p => p.name === name);
    const snap = clone(state);
    if (existing >= 0) {
      presets[existing] = { name, state: snap };
    } else {
      presets.push({ name, state: snap });
    }
    savePresets();
    refreshPresetSelect();
    selPreset.value = name;
    showToast("Preset saved");
  });

  btnPresetLoad.addEventListener("click", () => {
    const name = selPreset.value;
    const preset = presets.find(p => p.name === name);
    if (!preset) return;
    state = clone(preset.state);
    applyCanvasSizes();
    rebuildRightPanelForCurrentPattern(true);
    syncCommonUI();
    requestRender();
    showToast("Preset loaded");
  });

  btnPresetDelete.addEventListener("click", () => {
    const name = selPreset.value;
    const idx = presets.findIndex(p => p.name === name);
    if (idx < 0) return;
    presets.splice(idx, 1);
    savePresets();
    refreshPresetSelect();
    showToast("Preset deleted");
  });
}

// 起勁E
init();

function init() {
  const stored = loadLastState();
  if (stored) state = stored;

  // 初期サイズ
  applyCanvasSizes();

  // パターンリストを構篁E
  buildPatternList();

  // 共送EUI バインチE
  bindCommonUI();
  bindPresetUI();

  // �O���Ԃ̃p�^�[��UI�𕜌�
  if (state.app.currentPatternId) {
    rebuildRightPanelForCurrentPattern(true);
  }

  // 履歴初期匁E
  pushHistory("init");

  // 初期レンダ
  requestRender();
}

function buildPatternList() {
  patternListEl.innerHTML = "";

  // category ごとに並べたい場合�EここでソーチEグループ化しても良ぁE
  for (const item of PATTERN_REGISTRY) {
    const card = document.createElement("div");
    card.className = "patternCard";

    const h3 = document.createElement("h3");
    h3.textContent = item.name;

    const btn = document.createElement("button");
    btn.textContent = "Load";
    btn.className = "btnAccent";
    btn.addEventListener("click", async () => {
      await loadPattern(item.id);
    });

    // タイトル行にボタンを置くため、h3 の中身を絁E�E
    h3.textContent = "";
    const titleSpan = document.createElement("span");
    titleSpan.textContent = item.name;
    titleSpan.style.whiteSpace = "nowrap";
    titleSpan.style.overflow = "hidden";
    titleSpan.style.textOverflow = "ellipsis";

    const rightSpan = document.createElement("span");
    rightSpan.style.display = "flex";
    rightSpan.style.gap = "6px";
    rightSpan.style.alignItems = "center";
    const cat = document.createElement("span");
    cat.textContent = item.category;
    cat.style.color = "var(--muted)";
    cat.style.fontSize = "12px";
    rightSpan.appendChild(cat);
    rightSpan.appendChild(btn);

    h3.appendChild(titleSpan);
    h3.appendChild(rightSpan);

    const p = document.createElement("p");
    p.textContent = item.description ?? "";

    card.appendChild(h3);
    card.appendChild(p);

    patternListEl.appendChild(card);
  }
}

function bindCommonUI() {
  // 共通パラメータ
  syncCommonUI();

  inpSeed.addEventListener("input", () => {
    const v = Number(inpSeed.value);
    if (!Number.isFinite(v)) return;
    mutate(() => { state.common.seed = Math.floor(v); }, "seed");
  });

  inpBg.addEventListener("input", () => {
    mutate(() => { state.common.bg = inpBg.value.trim() || "#0b0d12"; }, "bg");
  });

  inpFg.addEventListener("input", () => {
    mutate(() => { state.common.fg = inpFg.value.trim() || "#e7e7ea"; }, "fg");
  });

  // View
  selCanvasSize.value = String(state.app.canvasSize);
  selCanvasSize.addEventListener("change", () => {
    mutate(() => {
      state.app.canvasSize = Number(selCanvasSize.value);
    }, "canvasSize");
    applyCanvasSizes();
    requestRender();
  });

  selPatternTile.value = String(state.app.tileSize);
  selPatternTile.addEventListener("change", () => {
    mutate(() => {
      state.app.tileSize = Number(selPatternTile.value);
    }, "tileSize");
    applyCanvasSizes();
    requestRender();
  });

  // File/Edit menu
  btnNew.addEventListener("click", () => {
    state = createInitialState();
    applyCanvasSizes();
    rebuildRightPanelForCurrentPattern(); // 何も選択されてなぁE��態に戻ぁE
    pushHistory("new");
    requestRender();
    showToast("New project");
  });

  btnOpen.addEventListener("click", () => {
    fileOpenInput.value = "";
    fileOpenInput.click();
  });

  fileOpenInput.addEventListener("change", async () => {
    const file = fileOpenInput.files?.[0];
    if (!file) return;
    const text = await file.text();
    try {
      const loaded = JSON.parse(text);
      // 最低限の形だけ確認（厳寁E��リチE�Eションは段階的に�E�E
      if (!loaded || !loaded.app || !loaded.common) throw new Error("invalid state");
      state = loaded;
      applyCanvasSizes();
      rebuildRightPanelForCurrentPattern(true);
      pushHistory("open");
      requestRender();
      showToast("Opened JSON");
    } catch (e) {
      console.error(e);
      showToast("Open failed (invalid JSON)", 2200);
    }
  });

  btnSave.addEventListener("click", () => {
    downloadJson(state, "wagara_state.json");
    showToast("Saved JSON");
  });

  btnExportPng.addEventListener("click", () => {
    exportCanvasPng(canvasMain, "wagara.png");
    showToast("Exported PNG");
  });

  btnUndo.addEventListener("click", () => {
    const snap = history.undo();
    if (!snap) return;
    state = clone(snap);
    applyCanvasSizes();
    rebuildRightPanelForCurrentPattern(true);
    requestRender();
    showToast("Undo");
  });

  btnRedo.addEventListener("click", () => {
    const snap = history.redo();
    if (!snap) return;
    state = clone(snap);
    applyCanvasSizes();
    rebuildRightPanelForCurrentPattern(true);
    requestRender();
    showToast("Redo");
  });

  btnRandomize.addEventListener("click", () => {
    mutate(() => {
      state.common.seed = (Math.floor(Math.random() * 1_000_000) + 1);
      inpSeed.value = String(state.common.seed);
    }, "randomize");
  });
}

function applyCanvasSizes() {
  const mainSize = Number(state.app.canvasSize) || 1536;
  const tileSize = Number(state.app.tileSize) || 512;

  setCanvasSize(canvasMain, mainSize);
  setCanvasSize(canvasTile, tileSize);

  lblMainInfo.textContent = `${mainSize} x ${mainSize}`;
  lblTileInfo.textContent = `${tileSize} x ${tileSize}`;
}

async function loadPattern(patternId) {
  const item = PATTERN_REGISTRY.find(x => x.id === patternId);
  if (!item) {
    showToast("Pattern not found", 2200);
    return;
  }

  // すでに同じなら何もしなぁE
  if (state.app.currentPatternId === patternId && currentModule) {
    showToast("Already loaded");
    return;
  }

  // 旧UI破棁E
  disposeCurrentPatternUI();

  // モジュールローチE
  try {
    const mod = await item.loader();
    currentModule = mod;

    // state の pattern 領域を用愁E
    if (!state.patterns[patternId]) state.patterns[patternId] = {};

    // defaults を適用�E�未定義のみ�E�E
    const defaults = (mod.manifest && mod.manifest.defaults) ? mod.manifest.defaults : {};
    for (const [k, v] of Object.entries(defaults)) {
      if (state.patterns[patternId][k] === undefined) state.patterns[patternId][k] = v;
    }

    // current pattern 更新
    mutate(() => { state.app.currentPatternId = patternId; }, "loadPattern");

    lblCurrentPattern.textContent = item.name;

    // 動的 UI 生�E
    buildPatternControlsUI();

    requestRender();
    showToast(`Loaded: ${item.name}`);
  } catch (e) {
    console.error(e);
    showToast("Load failed", 2200);
  }
}

function rebuildRightPanelForCurrentPattern(keepModuleIfPossible = false) {
  // Open/Undo/Redo/New などで state が差し替わった時に、E
  // 右パネル�E�Eattern Controls�E�を再構築する、E
  const pid = state.app.currentPatternId;

  disposeCurrentPatternUI();
  controlsRoot.innerHTML = "";

  if (!pid) {
    lblCurrentPattern.textContent = "(none)";
    currentModule = null;
    return;
  }

  const item = PATTERN_REGISTRY.find(x => x.id === pid);
  lblCurrentPattern.textContent = item ? item.name : pid;

  // keepModuleIfPossible ぁEtrue の場合でも、実際は module が忁E��なのでロードすめE
  // �E�すでに currentModule が同じなら使ぁE��す！E
  if (keepModuleIfPossible && currentModule?.manifest?.id === pid) {
    buildPatternControlsUI();
    return;
  }

  // 非同期ロードして UI 作り直ぁE
  if (item) {
    item.loader()
      .then((mod) => {
        currentModule = mod;
        // defaults�E�未定義のみ�E�E
        const defaults = (mod.manifest && mod.manifest.defaults) ? mod.manifest.defaults : {};
        if (!state.patterns[pid]) state.patterns[pid] = {};
        for (const [k, v] of Object.entries(defaults)) {
          if (state.patterns[pid][k] === undefined) state.patterns[pid][k] = v;
        }
        buildPatternControlsUI();
        requestRender();
      })
      .catch((e) => {
        console.error(e);
        showToast("Reload failed", 2200);
      });
  }
}

function buildPatternControlsUI() {
  controlsRoot.innerHTML = "";

  const pid = state.app.currentPatternId;
  if (!pid || !currentModule) return;

  const patternState = state.patterns[pid] || (state.patterns[pid] = {});

  const api = {
    requestRender,
    mutate: (fn, reason = "pattern") => mutate(fn, reason),
    getCommon: () => state.common,
  };

  if (typeof currentModule.createUI === "function") {
    currentModuleDisposeUI = currentModule.createUI(controlsRoot, patternState, api);
  }
}

function disposeCurrentPatternUI() {
  if (typeof currentModuleDisposeUI === "function") {
    try { currentModuleDisposeUI(); } catch {}
  }
  currentModuleDisposeUI = null;
}

function requestRender() {
  if (renderQueued) return;
  renderQueued = true;
  queueMicrotask(() => {
    renderQueued = false;
    render();
  });
  scheduleSave();
}

function render() {
  // 未選択なら背景だぁE
  if (!state.app.currentPatternId || !currentModule?.render) {
    clearCanvas(ctxTile, state.common.bg);
    clearCanvas(ctxMain, state.common.bg);
    return;
  }

  const pid = state.app.currentPatternId;
  const patternState = state.patterns[pid] || {};

  try {
    currentModule.render({
      ctxMain,
      ctxTile,
      state: patternState,
      common: state.common,
      app: state.app,
    });
  } catch (e) {
    console.error(e);
    // 例外で真っ黒になる�Eを避け、最低限の塗りつぶぁE
    clearCanvas(ctxTile, "#220b0b");
    clearCanvas(ctxMain, "#220b0b");
    showToast("Render error (see console)", 2400);
  }
}

// 状態変更をまとめて扱ぁE��Endo/Redoのため�E�E
function mutate(fn, reason = "change") {
  fn();
  // 右の共通�E力�E同期�E�忁E��最低限�E�E
  syncCommonUI();

  pushHistory(reason);
  requestRender();
}

function pushHistory(reason) {
  // 連打時に履歴が増えすぎる�Eが気になるなめEdebounce する
  history.push(clone(state));
  void reason;
}

function downloadJson(obj, filename) {
  const blob = new Blob([JSON.stringify(obj, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function exportCanvasPng(canvas, filename) {
  canvas.toBlob((blob) => {
    if (!blob) return;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }, "image/png");
}
