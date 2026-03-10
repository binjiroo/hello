import { uiNumber, uiSelect } from "../../ui.js";

// モジュールの約束（インターフェイス）
export const manifest = {
  id: "geo.checker",
  name: "Checker（テスト用）",
  version: "0.1.0",
  defaults: {
    cell: 64,
    rotateDeg: 0,
    invert: false,
  },
};

export function createUI(root, state, api) {
  // root は右側の Pattern Controls 領域
  // state は「この柄専用 state」（メインが patterns[patternId] を渡す）
  // api は共通ヘルパ（render要求など）

  const d1 = uiNumber({
    root,
    label: "Cell Size",
    value: state.cell ?? manifest.defaults.cell,
    min: 4,
    max: 512,
    step: 1,
    onChange: (v) => {
      state.cell = v;
      api.requestRender();
    }
  });

  uiNumber({
    root,
    label: "Rotate (deg)",
    value: state.rotateDeg ?? 0,
    min: -45,
    max: 45,
    step: 1,
    onChange: (v) => {
      state.rotateDeg = v;
      api.requestRender();
    }
  });

  uiSelect({
    root,
    label: "Invert",
    value: String(state.invert ?? false),
    options: [
      { value: "false", label: "false" },
      { value: "true", label: "true" },
    ],
    onChange: (v) => {
      state.invert = (v === "true");
      api.requestRender();
    }
  });

  // 破棄が必要ならここで解除処理を返す
  return () => {
    // 今回は input event を個別に解除してない（DOM丸ごと消すので不要）
    void d1;
  };
}

export function render({ ctxMain, ctxTile, state, common }) {
  const bg = common.bg;
  const fg = common.fg;

  // タイル描画
  drawChecker(ctxTile, state, common, bg, fg);

  // メイン描画は「タイルを敷き詰め」して完成絵にする
  fillWithTile(ctxMain, ctxTile, bg);
}

function drawChecker(ctx, state, common, bg, fg) {
  const w = ctx.canvas.width;
  const h = ctx.canvas.height;
  ctx.save();
  ctx.setTransform(1,0,0,1,0,0);
  ctx.fillStyle = bg;
  ctx.fillRect(0,0,w,h);

  const cell = clampInt(state.cell ?? 64, 2, 2048);
  const rot = ((state.rotateDeg ?? 0) * Math.PI) / 180;
  const invert = !!state.invert;

  // 回転用：中心を原点に
  ctx.translate(w/2, h/2);
  ctx.rotate(rot);
  ctx.translate(-w/2, -h/2);

  for (let y = -cell; y < h + cell; y += cell) {
    for (let x = -cell; x < w + cell; x += cell) {
      const ix = Math.floor(x / cell);
      const iy = Math.floor(y / cell);
      const on = ((ix + iy) % 2 === 0);
      const useFg = invert ? !on : on;
      ctx.fillStyle = useFg ? fg : bg;
      ctx.fillRect(x, y, cell, cell);
    }
  }

  ctx.restore();
}

function fillWithTile(ctxMain, ctxTile, bg) {
  const mw = ctxMain.canvas.width;
  const mh = ctxMain.canvas.height;

  ctxMain.save();
  ctxMain.setTransform(1,0,0,1,0,0);
  ctxMain.fillStyle = bg;
  ctxMain.fillRect(0,0,mw,mh);

  const pattern = ctxMain.createPattern(ctxTile.canvas, "repeat");
  ctxMain.fillStyle = pattern;
  ctxMain.fillRect(0,0,mw,mh);
  ctxMain.restore();
}

function clampInt(v, min, max) {
  const n = Math.floor(Number(v));
  if (!Number.isFinite(n)) return min;
  return Math.max(min, Math.min(max, n));
}
