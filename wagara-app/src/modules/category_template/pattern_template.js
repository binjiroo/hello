import { uiNumber, uiText, uiSelect } from "../../ui.js";

export const manifest = {
  id: "template.pattern",
  name: "Pattern Template",
  version: "0.1.0",
  defaults: {
    paramA: 10,
    paramB: "hello",
    mode: "A",
  },
};

export function createUI(root, state, api) {
  uiNumber({
    root,
    label: "Param A",
    value: state.paramA ?? manifest.defaults.paramA,
    min: 0, max: 999, step: 1,
    onChange: (v) => { state.paramA = v; api.requestRender(); }
  });

  uiText({
    root,
    label: "Param B",
    value: state.paramB ?? manifest.defaults.paramB,
    placeholder: "text",
    onChange: (v) => { state.paramB = v; api.requestRender(); }
  });

  uiSelect({
    root,
    label: "Mode",
    value: state.mode ?? manifest.defaults.mode,
    options: [
      { value: "A", label: "A" },
      { value: "B", label: "B" },
    ],
    onChange: (v) => { state.mode = v; api.requestRender(); }
  });

  return () => {};
}

export function render({ ctxMain, ctxTile, state, common }) {
  // ここで ctxTile に「タイル」描画
  // ctxMain には「タイル敷き詰め or 完成画」描画
  ctxTile.save();
  ctxTile.setTransform(1,0,0,1,0,0);
  ctxTile.fillStyle = common.bg;
  ctxTile.fillRect(0,0,ctxTile.canvas.width,ctxTile.canvas.height);
  ctxTile.restore();

  ctxMain.save();
  ctxMain.setTransform(1,0,0,1,0,0);
  ctxMain.fillStyle = common.bg;
  ctxMain.fillRect(0,0,ctxMain.canvas.width,ctxMain.canvas.height);
  ctxMain.restore();
}
