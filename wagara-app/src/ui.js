export function showToast(msg, ms = 1800) {
  const el = document.getElementById("toast");
  if (!el) return;
  el.textContent = msg;
  el.style.display = "block";
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => {
    el.style.display = "none";
  }, ms);
}

// 簡易コントロール生成（モジュールから使う）
export function uiNumber({ root, label, value, min, max, step = 1, onChange }) {
  const row = document.createElement("div");
  row.className = "ctrlRow";

  const lab = document.createElement("label");
  lab.textContent = label;

  const inp = document.createElement("input");
  inp.type = "number";
  inp.value = String(value ?? 0);
  if (min != null) inp.min = String(min);
  if (max != null) inp.max = String(max);
  inp.step = String(step);

  inp.addEventListener("input", () => {
    const v = Number(inp.value);
    onChange(Number.isFinite(v) ? v : value);
  });

  row.appendChild(lab);
  row.appendChild(inp);
  root.appendChild(row);

  return { row, inp };
}

export function uiText({ root, label, value, placeholder = "", onChange }) {
  const row = document.createElement("div");
  row.className = "ctrlRow";

  const lab = document.createElement("label");
  lab.textContent = label;

  const inp = document.createElement("input");
  inp.type = "text";
  inp.value = String(value ?? "");
  inp.placeholder = placeholder;

  inp.addEventListener("input", () => onChange(inp.value));

  row.appendChild(lab);
  row.appendChild(inp);
  root.appendChild(row);

  return { row, inp };
}

export function uiSelect({ root, label, value, options, onChange }) {
  const row = document.createElement("div");
  row.className = "ctrlRow";

  const lab = document.createElement("label");
  lab.textContent = label;

  const sel = document.createElement("select");
  for (const opt of options) {
    const o = document.createElement("option");
    o.value = String(opt.value);
    o.textContent = opt.label;
    if (String(opt.value) === String(value)) o.selected = true;
    sel.appendChild(o);
  }
  sel.addEventListener("change", () => onChange(sel.value));

  row.appendChild(lab);
  row.appendChild(sel);
  root.appendChild(row);

  return { row, sel };
}

// 2D Canvas ヘルパ
export function setCanvasSize(canvas, size) {
  canvas.width = size;
  canvas.height = size;
}

export function clearCanvas(ctx, color = "#000000") {
  const { canvas } = ctx;
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = color;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.restore();
}
