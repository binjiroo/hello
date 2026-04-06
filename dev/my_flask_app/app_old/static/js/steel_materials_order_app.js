/*
====================================================================
  鋼材注文アプリ用 外部JavaScript（説明コメント付き）
  - 役割: 編集テーブルの管理、入力補助、印刷プレビュー（Paged.js）
  - 方針: 既存の挙動は変えず、可読性を高めるためのコメントだけを追加

  ▼セクション目次
    1) グローバル設定・定数
    2) 軽量ユーティリティ（副作用なし）
    3) データユーティリティ（steelData関連）
    4) 編集テーブル操作（行追加・再番号・集計など）
    5) 貼り付け解析（parse / count）
    6) UI結線/初期値設定（DOM依存）
    7) 印刷パイプライン（計測→算出→分割→プレビュー）
    8) フロー制御（freeze・プレビュー実行など）
    9) 初期化（DOMContentLoaded）

  ※注意:
    - コメントのみ追加・修正。ロジックは原則として変更していません。
    - addOrderRow() 内の appendChild は 2 回呼ばれる可能性がありますが、
      同一ノードを再度 appendChild すると移動になるだけで重複はしません。
      （挙動維持のためコードはそのままにし、コメントで意図を明記）
====================================================================
*/

// 1) グローバル設定・定数 ===============================
let currentRowNumber = 0;                                // 現在のデータ行数（再番号で更新）
const COL_IDX_ROW_NO      = 0;                           // 列インデックス: 行番号
const COL_IDX_STEEL_NAME  = 1;                           // 列インデックス: 鋼材名
const COL_IDX_DIMENSION   = 2;                           // 列インデックス: 寸法（長さなど）
const COL_IDX_QUANTITY    = 3;                           // 列インデックス: 本数
const COL_IDX_UNIT_WEIGHT = 4;                           // 列インデックス: 単位重量（長さ×単位重量換算後の1本重量）
const COL_IDX_TOTAL_WEIGHT = 5;                          // 列インデックス: 総重量

let running = false;                                     // 印刷プレビューの重複起動防止フラグ
let initialized = false;                                 // 初期20行生成などの二重実行防止

const LS_FIELDS = [                                      // localStorage 対象のフォーム項目
  'project_name','order_date','delivery_date',
  'chief_date','company_name','tel','fax','email'
];

// 表示中の編集テーブルにある数値 input を一括でフォーマット（カンマ付与等）
function formatAllVisibleNumbers(){
  const tbody = getEl('order_table_body_edit');
  qsa('tr', tbody).forEach(row=>{
    const dim = qs('input', row.cells[COL_IDX_DIMENSION]);
    const qty = qs('input', row.cells[COL_IDX_QUANTITY]);
    const uw  = qs('input', row.cells[COL_IDX_UNIT_WEIGHT]);
    const tw  = qs('input', row.cells[COL_IDX_TOTAL_WEIGHT]);
    if (dim) dim.value = formatNumber(toNumber(dim.value), decimalsOf(dim.value)); // 寸法: 元の小数桁を尊重
    if (qty) qty.value = formatNumber(toNumber(qty.value), 0);                     // 数量: 整数
    if (uw)  uw.value  = formatNumber(toNumber(uw.value), 2);                      // 単位重量: 小数2桁
    if (tw)  tw.value  = formatNumber(toNumber(tw.value), 2);                      // 総重量:   小数2桁
  });
}

// === Paged.js: 繰り返しヘッダー登録（最上部に置く） ===
// Paged.js のハンドラ登録が必要な場合のプレースホルダ。
// ここではロード順の安定化用。実際の登録処理が必要になれば doRegister 内に追記。
(function registerRepeatHeaders(){
  if (window.__RepeatHeadersRegistered) return;          // 二重登録防止

  function doRegister(){
    if (!window.Paged || !Paged.Handler) { setTimeout(doRegister, 30); return; }
    window.__RepeatHeadersRegistered = true;             // 登録完了フラグ
  }
  doRegister();
})();

// 2) 軽量ユーティリティ（副作用なし） ===================
function getEl(id) {                                     // id で単一要素取得（null 可）
  return document.getElementById(id);
}

function qs(selector, context = document) {              // querySelector の安全ラッパ
  if (!context || typeof context.querySelector !== 'function') {
    console.warn("⚠️ qs: 無効な context が指定されました", context);
    return null;
  }
  return context.querySelector(selector);
}

function qsa(selector, context = document) {             // querySelectorAll の安全ラッパ
  if (!context || typeof context.querySelectorAll !== 'function') {
    console.warn("⚠️ qsa: 無効な context です:", context);
    // 空の NodeList を返して後段処理を安全にスキップ
    return document.querySelectorAll(':scope __never__');
  }
  return context.querySelectorAll(selector);
}

function pxToMm(px){ return px * 25.4 / 96; }            // px→mm 変換（CSS の 1in=96px を使用）

function cssNum(name, fallback){                          // CSS 変数を数値として取得（小数可）
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const n = parseFloat(v);
  return Number.isFinite(n) ? n : fallback;
}

function cssInt(name, fallback){                           // CSS 変数を整数として取得
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const n = parseInt(v, 10);
  return Number.isFinite(n) ? n : fallback;
}

function snapMm(v, step){ return step>0 ? Math.round(v/step)*step : v; } // 任意刻みに丸め

// デバッグログ（初期データ埋め込みの確認）
console.log("✅ __STEEL_DATA__ present in HTML?", qs("#__STEEL_DATA__") !== null);
console.log("🔎 DOM state:", document.readyState);
console.log("🔎 script#__STEEL_DATA__:", getEl('__STEEL_DATA__'));
console.log(!!getEl('__STEEL_DATA__'))

// === 数値 ↔ 表示フォーマット（カンマ対応） ===
function unformatNumber(v){            // 表示用 → 計算用（"12,345.6" → "12345.6"）
  return String(v ?? '').replace(/[\,\s]/g,'');
}
function toNumber(v){                  // 計算用 number へ（失敗時は 0）
  const n = Number(unformatNumber(v));
  return Number.isFinite(n) ? n : 0;
}
function formatNumber(n, decimals=null){ // 計算用 → 表示用（桁区切り）
  if (!Number.isFinite(n)) return '';
  const opt = (decimals==null) ? {} : {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  };
  return n.toLocaleString('ja-JP', opt);
}
function decimalsOf(str){              // 元の文字列から小数桁を推測（最大6桁）
  const m = unformatNumber(str).match(/\.(\d+)/);
  return m ? Math.min(6, m[1].length) : 0;
}

// 3) データユーティリティ ================================
// --- SteelData（window.__STEEL_DATA__）を使った検索ヘルパ ---
let steelData = null;                  // { カテゴリ: { 鋼材名: 単位重量(kg/m) } | [候補配列] }

if (window.__STEEL_DATA__) {
  steelData = window.__STEEL_DATA__;
  console.log("✅ steelData 読み込み成功:", steelData);
} else {
  console.error("❌ steelData が window に存在しません");
}

function getSteelList(category) {      // カテゴリから候補を配列で返す（オブジェクトならキー配列、配列ならそのまま）
  const items = steelData?.[category];
  if (Array.isArray(items)) {
    return items;
  } else if (items && typeof items === 'object') {
    return Object.keys(items);
  }
  return [];
}

function getUnitWeight(category, name) { // カテゴリと名称から単位重量を取得（なければ 0）
  const categoryData = steelData?.[category];
  if (!categoryData || typeof categoryData !== 'object') return 0;
  return categoryData[name] || 0;
}

function findUnitWeightByName(name) { // カテゴリ横断で名称一致の単位重量を取得（見つからなければ 0）
  for (const category in steelData) {
    const data = steelData[category];
    if (data && typeof data === 'object' && data[name] != null) {
      return data[name];
    }
  }
  return 0;
}

// 4) 編集テーブル操作 ====================================
// === 集計行ユーティリティ ==============================
function isSummaryRow(tr){ return tr?.classList?.contains('summary-row'); }

function getDataRows(tbody = getEl('order_table_body_edit')){ // サマリ行を除いた実データ行だけの配列
  return Array.from(tbody?.querySelectorAll('tr') || []).filter(tr => !isSummaryRow(tr));
}

function ensureSummaryRow(){           // 編集tbody末尾にサマリ行（合計）を必ず用意
  const tbody = getEl('order_table_body_edit');
  if (!tbody) return;

  let sumRow = tbody.querySelector('tr.summary-row');
  if (!sumRow){
    sumRow = document.createElement('tr');
    sumRow.className = 'summary-row';
    // 編集テーブルは 9 列（削除列含む）
    for(let i=0;i<9;i++) sumRow.appendChild(document.createElement('td'));
    tbody.appendChild(sumRow);
  }
  // ラベル初期化（重量総計は単位重量列に表示）
  sumRow.cells[COL_IDX_UNIT_WEIGHT].textContent  = '重量総計';
  sumRow.cells[COL_IDX_TOTAL_WEIGHT].textContent = '0';
  return sumRow;
}

function updateSummary(){               // 総重量を再集計→サマリ行に反映
  const tbody = getEl('order_table_body_edit');
  if (!tbody) return;

  const sumRow = ensureSummaryRow();
  const dataRows = getDataRows(tbody);

  let total = 0;
  for (const tr of dataRows){
    const totalInput = tr.cells[COL_IDX_TOTAL_WEIGHT]?.querySelector('input');
    if (totalInput) total += toNumber(totalInput.value);   // 値はカンマを外して数値化
  }
  sumRow.cells[COL_IDX_UNIT_WEIGHT].textContent  = '重量総計';
  sumRow.cells[COL_IDX_TOTAL_WEIGHT].textContent = formatNumber(total, 2); // 小数2桁で表示整形
}

// ✅ 行追加関数（どのtbodyに追加するか引数で指定）
function addOrderRow(template, targetTbody) {
  // --- 前提要素チェック ---
  if (!template) { console.error("❌ template#order-row-template が見つかりません"); return; }
  if (!targetTbody) { console.error("❌ tbodyが見つかりません"); return; }

  // <template> から 1 行分を複製
  const clone = template.content.cloneNode(true);
  const row = clone.querySelector("tr");
  if (!row) { console.error("❌ クローン内に<tr>が存在しません"); return; }

  // 行番号セル（.row-no）に連番を採番（後で updateRowNumbers でも再計算される）
  const rowNoCell = row.querySelector(".row-no");
  if (rowNoCell) { rowNoCell.textContent = ++currentRowNumber; }

  // 削除ボタン（編集用tbodyにだけ効く）。印刷用ではボタン自体を削除
  const deleteBtn = row.querySelector(".delete-row");
  if (deleteBtn && targetTbody.id === "order_table_body_edit") {
    deleteBtn.addEventListener("click", () => {
      row.remove();
      updateRowNumbers();
      updateSummary();
    });
  } else if (deleteBtn) {
    deleteBtn.remove();
  }

  // いったん末尾に追加 → 直後にサマリ行の直前へ移動（または末尾のまま）
  // ※ 同一ノードを再 appendChild しても重複にはならず「移動」になります。
  targetTbody.appendChild(row);

  const summary = targetTbody.querySelector('tr.summary-row');
  if (summary) {
    targetTbody.insertBefore(row, summary);  // サマリの直前に差し込む
  } else {
    targetTbody.appendChild(row);            // サマリ未作成時は末尾（実質的に位置は変わらない）
  }

  updateRowNumbers();
  updateSummary();                            // 追加のたびに合計を最新化
}

// ✅ 行番号再計算（サマリ行は除外）
function updateRowNumbers() {
  const rows = getDataRows(getEl('order_table_body_edit'));
  rows.forEach((row, index) => {
    const noCell = qs(".row-no", row);
    if (noCell) noCell.textContent = index + 1;
  });
  currentRowNumber = rows.length;
}

// 入力値の変更に応じて単位重量および総重量を自動更新する委譲リスナー
function setupAutoWeightListeners() {
  const tbodyEdit = getEl('order_table_body_edit');
  if (!tbodyEdit) return;

  tbodyEdit.addEventListener('input', (e) => {
    const target = e.target;
    // 対象の input 名のみ処理
    if (!target.matches('input[name="steel_name[]"], input[name="steel_size[]"], input[name="quantity[]"]')) return;

    const row = target.closest('tr');
    if (!row) return;

    // 鋼材名から単位重量(kg/m)を引く（カテゴリ横断検索）
    const steelInput = row.querySelector('input[name="steel_name[]"]');
    const quantityInput = row.querySelector('input[name="quantity[]"]');
    let unitWeight = 0;

    const steelName = steelInput.value.trim();
    for (const category in steelData) {
      const data = steelData[category];
      if (data && data[steelName] != null) { unitWeight = data[steelName]; break; }
    }

    updateWeightsForRow(row, unitWeight); // 長さ×(kg/m)×本数 → 総重量
    updateSummary();
  });
}

// 1 行分の重量計算と反映（表示は常にカンマ付きに統一）
function updateWeightsForRow(row, unitWeight) {
  const cells = row.getElementsByTagName('td');
  const lengthInput     = qs('input', cells[COL_IDX_DIMENSION]);
  const quantityInput   = qs('input', cells[COL_IDX_QUANTITY]);
  const unitWeightInput = qs('input', cells[COL_IDX_UNIT_WEIGHT]);
  const totalWeightInput= qs('input', cells[COL_IDX_TOTAL_WEIGHT]);

  const length   = toNumber(lengthInput?.value);          // mm or cm 相当の数値（単位は実装と運用で合わせる）
  const quantity = Math.trunc(toNumber(quantityInput?.value));

  // 単位重量(kg/m) → 1mm あたり(kg/mm) に換算
  const perMillimeterWeight = unitWeight / 1000;
  const singleWeight = length * perMillimeterWeight;      // 1本重量
  const totalWeight  = singleWeight * quantity;           // 総重量

  if (unitWeightInput)  unitWeightInput.value  = formatNumber(singleWeight, 2);
  if (totalWeightInput) totalWeightInput.value = formatNumber(totalWeight,  2);
}

// すべての行を走査して重量を再計算（復元直後や一括貼付け後に使用）
function recalculateAllWeights() {
  const tbodyEdit = getEl('order_table_body_edit');
  const rows = qsa('tr', tbodyEdit);

  rows.forEach(row => {
    const inputs = qsa('input', row);
    if (inputs.length < 3) return; // 空行などはスキップ

    const steelInput = inputs[0];
    const lengthInput = inputs[1];
    const quantityInput = inputs[2];

    const steelName = steelInput.value.trim();
    const unitWeight = findUnitWeightByName(steelName);

    updateWeightsForRow(row, unitWeight);
  });
}

// 編集テーブルの内容を印刷テーブルへコピー（input → textContent）
function syncToPrintTable() {
  const tbodyEdit  = document.getElementById('order_table_body_edit');
  const tbodyPrint = document.getElementById('order_table_body_print');
  if (!tbodyEdit || !tbodyPrint) {
    console.error('syncToPrintTable: tbody が見つかりません', { tbodyEdit, tbodyPrint });
    return;
  }
  tbodyPrint.innerHTML = '';

  tbodyEdit.querySelectorAll('tr').forEach(tr => {
    const trPrint = document.createElement('tr');
    // 印刷用は先頭8列のみ処理（削除ボタン=no-print列は含めない）
    for (let i = 0; i < 8; i++) {
      const tdEdit = tr.children[i];
      if (!tdEdit) continue;
      const tdPrint = document.createElement('td');
      const input = tdEdit.querySelector('input');
      tdPrint.textContent = input ? input.value : tdEdit.textContent.trim();
      trPrint.appendChild(tdPrint);
    }
    tbodyPrint.appendChild(trPrint);
  });
}

// 5) 貼り付け解析 ========================================
// クリップ/テキストから抽出した配列でテーブルを埋める（足りなければ行を追加）
function fillRowsByParsedData({ steels = [], dimensions = [], quantities = [] }) {
  const tbodyEdit = getEl('order_table_body_edit');
  const template  = getEl('order-row-template');
  if (!tbodyEdit) return;

  const rowCount = Math.max(steels.length, dimensions.length, quantities.length);

  // ★サマリを除いたデータ行数で比較し、必要なら行を追加
  while (getDataRows(tbodyEdit).length < rowCount) {
    addOrderRow(template, tbodyEdit);
  }

  const rows = getDataRows(tbodyEdit);
  for (let i = 0; i < rowCount; i++) {
    const inputs = qsa('input', rows[i]);
    if (steels[i])     inputs[0].value = steels[i];
    if (dimensions[i]) inputs[1].value = dimensions[i];
    if (quantities[i]) inputs[2].value = quantities[i];
  }

  setupAutoWeightListeners();  // 念のためリスナーを確実に張る
  recalculateAllWeights();     // 数値算出
  formatAllVisibleNumbers();   // 表示整形
  updateRowNumbers();          // 行番号振り直し
  updateSummary();             // 最後に合計更新
}

// 「H-400x200x8x13  6000  4本」などを行に割り当てる（順不同で出現しても拾う）
function handleParseFill() {
  const text = getEl("auto_fill_textarea").value;
  const lines = text.split(/\r?\n/).map(line => line.trim()).filter(line => line !== "");

  const steels = [];
  const dimensions = [];
  const quantities = [];

  // パターン: 鋼材名 / 寸法(3〜4桁, カンマ区切可) / 本数（末尾に「本」可）
  const steelPattern = /^H-\d+x\d+(?:x\d+(?:\.\d+)?){0,3}$/i;
  const dimensionPattern = /^\d{3,4}(?:,\d{3})*$/;
  const quantityPattern = /^\d{1,2}\s*本?$/;

  for (const line of lines) {
    const tokens = line.split(/\s+/);
    for (const token of tokens) {
      const clean = token.replace(/,/g, '');

      if (steelPattern.test(token)) {
        steels.push(token);
      } else if (dimensionPattern.test(clean)) {
        dimensions.push(clean);
      } else if (quantityPattern.test(token)) {
        const num = token.replace(/\D/g, '');
        quantities.push(parseInt(num));
      }
    }
  }

  fillRowsByParsedData({ steels, dimensions, quantities });
  console.log("✅ handleParseFill 完了:", { steels, dimensions, quantities });
}

// 複数行から「各値の出現回数」を数えて転記（例: 同じ H-400… が 3 回 → 数量 3）
function handleCountFill() {
  const text = getEl("count_and_fill_textarea").value;
  const lines = text.split(/\r?\n/);

  const materialCount = {};
  const dimensionCount = {};

  const steelPattern = /^H-\d+x\d+(?:x\d+(?:\.\d+)?){0,3}$/i;
  const numberPattern = /^(?:\d{1,3}(?:,\d{3})*|\d{2,6})(?:\.\d)?$/;

  for (let line of lines) {
    if (!line.trim()) continue;
    line = line.replace(/\u3000/g, ' ');                 // 全角スペース対策
    const tokens = line.trim().split(/\s+/);

    for (const token of tokens) {
      if (steelPattern.test(token)) {
        materialCount[token] = (materialCount[token] || 0) + 1;
      } else if (numberPattern.test(token)) {
        const clean = token.replace(/,/g, '');
        dimensionCount[clean] = (dimensionCount[clean] || 0) + 1;
      }
    }
  }

  const steels     = Object.keys(materialCount);
  const quantities = Object.values(materialCount);
  const dimensions = Object.keys(dimensionCount);
  const dimCounts  = Object.values(dimensionCount);

  // 寸法の出現回数も数量として後ろに連結（用途次第で別カラムにしたい場合は要拡張）
  fillRowsByParsedData({
    steels,
    dimensions,
    quantities: [...quantities, ...dimCounts],
  });

  console.log("✅ handleCountFill 完了:", { materialCount, dimensionCount });
}

// 入力値をクリアする汎用関数（行単位）
function clearRowInputs(row) {
  qsa("input", row).forEach(input => input.value = "");
}

// 6) UI結線/初期値設定（DOM依存） =========================
// 単純な <input list=...> + datalist に「入力履歴」を乗せる補助
function setupAutoComplete(fieldId, listId, storageKey, maxItems = 20) {
  // --- 引数バリデーション ---
  if (fieldId == null || listId == null) { console.error("setupAutoComplete: fieldId/listId が null または undefined です。"); return false; }
  if (typeof fieldId !== "string" || typeof listId !== "string") { console.error("setupAutoComplete: fieldId/listId は文字列である必要があります。"); return false; }
  if (fieldId.trim() === "" || listId.trim() === "") { console.error("setupAutoComplete: fieldId/listId が空文字です。"); return false; }

  // --- DOM 取得 ---
  const input = document.getElementById(fieldId);
  const datalist = document.getElementById(listId);

  // --- 要素存在チェック ---
  if (!input)    { console.error(`setupAutoComplete: id="${fieldId}" の要素が見つかりません。`); return false; }
  if (!datalist) { console.error(`setupAutoComplete: id="${listId}" の要素が見つかりません。`); return false; }

  // --- 要素型チェック ---
  if (!(input instanceof HTMLInputElement))      { console.error(`setupAutoComplete: id="${fieldId}" は <input> 要素ではありません。`); return false; }
  if (!(datalist instanceof HTMLDataListElement)) { console.error(`setupAutoComplete: id="${listId}" は <datalist> 要素ではありません。`); return false; }

  // input の list 属性を保証
  if (input.getAttribute("list") !== listId) { input.setAttribute("list", listId); }

  // --- 候補の更新 ---
  function updateDatalist() {
    let values = [];
    try {
      values = JSON.parse(localStorage.getItem(storageKey) || "[]");
      if (!Array.isArray(values)) values = [];
    } catch { values = []; }

    datalist.innerHTML = "";
    values.forEach((val) => {
      const opt = document.createElement("option");
      opt.value = String(val);
      datalist.appendChild(opt);
    });
  }

  // --- 履歴保存＋候補更新 ---
  function addToStorageAndUpdate() {
    let values;
    try {
      values = JSON.parse(localStorage.getItem(storageKey) || "[]");
      if (!Array.isArray(values)) values = [];
    } catch { values = []; }

    const v = input.value.trim();
    if (v && !values.includes(v)) {
      values.unshift(v);
      if (values.length > maxItems) values = values.slice(0, maxItems);
      try { localStorage.setItem(storageKey, JSON.stringify(values)); }
      catch (e) { console.warn("localStorage への保存に失敗:", e); }
      updateDatalist();
    }
  }

  // --- イベント設定 & 初期反映 ---
  input.addEventListener("change", addToStorageAndUpdate); // 決定時に履歴へ
  input.addEventListener("input",  updateDatalist);        // 入力中も候補を反映
  updateDatalist();

  return true;
}

// 日付の自動初期化（発注日=今日 / 納期=明日）
function initDefaultDates() {
  const orderDateInput    = getEl('order_date');
  const deliveryDateInput = getEl('delivery_date');

  const today = new Date();
  const tomorrow = new Date(); tomorrow.setDate(today.getDate() + 1);

  const fmt = (d) => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;

  if (orderDateInput && !orderDateInput.value)          orderDateInput.value    = fmt(today);
  if (deliveryDateInput && !deliveryDateInput.value)    deliveryDateInput.value = fmt(tomorrow);
}

// フォーム内容を localStorage へ保存（submit 時）
function saveFormToLocalStorage(){
  LS_FIELDS.forEach(id => {
    const el = getEl(id);
    if (el) localStorage.setItem(el.name || id, el.value);
  });
}

// localStorage からフォームに復元（init 時）
function restoreFormFromLocalStorage() {
  LS_FIELDS.forEach(id => {
    const el = getEl(id);
    if (!el) return;
    const v = localStorage.getItem(el.name || id);
    if (v !== null) el.value = v;
  });
}

// ================== init（フル移植版） ==================
// 画面ロード完了時に 1 度だけ呼ばれる初期化ルーチン
function init() {
  // ネストした <template> 対策（もし <template> の中に誤って置かれていたら body 直下へ退避）
  extractOrderRowTemplateToBody();

  const template  = getEl('order-row-template');
  const tbodyEdit = getEl('order_table_body_edit');

  // 初期20行（未初期化の場合のみ）+ サマリ行の確保
  if (template && tbodyEdit && !initialized) {
    initializeApp(template, tbodyEdit);
    ensureSummaryRow();
    updateSummary();
  }

  // 入力→重量計算の委譲をセット
  setupAutoWeightListeners();

  // 日付の初期値 & 保存内容の復元
  initDefaultDates();
  restoreFormFromLocalStorage();

  // 復元後の値に基づいて重量再計算→表示整形→合計
  recalculateAllWeights?.();
  formatAllVisibleNumbers?.();
  updateSummary();                 // ← init 末尾で最終更新

  // UI はここで 1 回だけ結線
  wireFormUI();

  console.log("✅ init() done");
}

// === UI結線を1か所に集約（多重バインド防止） ===
let __wired = false;
function wireFormUI(){
  if (__wired) return;  // 二重結線防止
  __wired = true;

  // --- カテゴリ選択 → 鋼材リスト更新 ---
  const steelCategorySelect = getEl('steel_category');
  const steelItemSelect     = getEl('steel_item');
  if (steelCategorySelect && steelItemSelect) {
    steelCategorySelect.addEventListener('change', function () {
      const list = getSteelList(this.value);
      steelItemSelect.innerHTML = '<option value="">選択してください</option>';
      list.forEach(name => {
        const opt = document.createElement('option');
        opt.value = name; opt.textContent = name;
        steelItemSelect.appendChild(opt);
      });
    });
  }

  // --- 鋼材追加ボタン: 選択された鋼材を最初の空行 or 新規行にセット ---
  const addSteelButton = getEl('add_steel_button');
  if (addSteelButton) {
    addSteelButton.addEventListener('click', () => {
      const template  = getEl('order-row-template');
      const tbodyEdit = getEl('order_table_body_edit');
      const selectedCategory = steelCategorySelect?.value;
      const selectedItem     = steelItemSelect?.value;

      if (!selectedCategory || !selectedItem) {
        alert('鋼材カテゴリと鋼材を選択してください');
        return;
      }

      const unitWeight = getUnitWeight(selectedCategory, selectedItem);

      const rows = tbodyEdit.getElementsByTagName('tr');
      let targetRow = null;
      for (let i = 0; i < rows.length; i++) {
        const steelInput = rows[i].getElementsByTagName('td')[COL_IDX_STEEL_NAME]?.querySelector('input');
        if (steelInput && steelInput.value.trim() === '') { // 空いている行を優先
          steelInput.value = selectedItem;
          targetRow = rows[i];
          break;
        }
      }
      if (!targetRow) {                                     // 空行がなければ新規行
        addOrderRow(template, tbodyEdit);
        targetRow = tbodyEdit.lastElementChild;
        const steelInput = targetRow.getElementsByTagName('td')[COL_IDX_STEEL_NAME]?.querySelector('input');
        if (steelInput) steelInput.value = selectedItem;
      }

      // 寸法・数量の変更で重量が即時更新されるよう結線
      const lengthInput   = targetRow.getElementsByTagName('td')[COL_IDX_DIMENSION]?.querySelector('input');
      const quantityInput = targetRow.getElementsByTagName('td')[COL_IDX_QUANTITY]?.querySelector('input');
      lengthInput  && lengthInput.addEventListener('input',  () => updateWeightsForRow(targetRow, unitWeight));
      quantityInput&& quantityInput.addEventListener('input', () => updateWeightsForRow(targetRow, unitWeight));
      updateWeightsForRow(targetRow, unitWeight);
    });
  }

  // --- 寸法スライダー: ラベルは常にカンマ付きで表示 ---
  const dimensionSlider = getEl('dimension_slider');
  const dimensionValue  = getEl('dimension_value');
  const dimensionStep   = getEl('dimension_step');
  const addDimBtn       = getEl('add_dimension_button');

  if (dimensionSlider && dimensionValue) {
    dimensionValue.textContent =
      formatNumber(toNumber(dimensionSlider.value), decimalsOf(dimensionSlider.value));
    dimensionSlider.addEventListener('input', () => {
      dimensionValue.textContent =
        formatNumber(toNumber(dimensionSlider.value), decimalsOf(dimensionSlider.value));
    });
  }
  if (dimensionSlider && dimensionStep) {
    dimensionStep.addEventListener('change', () => { dimensionSlider.step = dimensionStep.value; });
  }

  if (addDimBtn) {
    addDimBtn.addEventListener('click', () => {
      const template  = getEl('order-row-template');
      const tbodyEdit = getEl('order_table_body_edit');

      const raw = dimensionSlider.value;                         // 例: "1234.5"
      const val = formatNumber(toNumber(raw), decimalsOf(raw));  // カンマ付き

      const rows = tbodyEdit.getElementsByTagName('tr');

      for (let i = 0; i < rows.length; i++) {
        const sizeInput = qs('td:nth-child(3) input', rows[i]);
        if (sizeInput && sizeInput.value.trim() === '') {
          sizeInput.value = val;
          // 既存の鋼材名があればその単位重量で更新（空なら 0）
          const steelName = qs('td:nth-child(2) input', rows[i])?.value?.trim();
          const unitW = steelName ? findUnitWeightByName(steelName) : 0;
          updateWeightsForRow(rows[i], unitW);
          if (typeof updateSummary === 'function') updateSummary?.();
          return;
        }
      }

      // 空行が無ければ追加してから値を入れる
      addOrderRow(template, tbodyEdit);
      const lastRow  = tbodyEdit.lastElementChild;
      const sizeInput = qs('td:nth-child(3) input', lastRow);
      if (sizeInput) sizeInput.value = val;

      const steelName = qs('td:nth-child(2) input', lastRow)?.value?.trim();
      const unitW = steelName ? findUnitWeightByName(steelName) : 0;
      updateWeightsForRow(lastRow, unitW);
      if (typeof updateSummary === 'function') updateSummary?.();
    });
  }

  // --- 数量スライダー ---
  const quantitySlider = getEl('quantity_slider');
  const quantityValue  = getEl('quantity_value');
  const quantityStep   = getEl('quantity_step');
  const addQtyBtn      = getEl('add_quantity_button');

  if (quantitySlider && quantityValue) {
    quantityValue.textContent = formatNumber(toNumber(quantitySlider.value), 0);
    quantitySlider.addEventListener('input', () => {
      quantityValue.textContent = formatNumber(toNumber(quantitySlider.value), 0);
    });
  }
  if (quantitySlider && quantityStep) {
    quantityStep.addEventListener('change', () => { quantitySlider.step = quantityStep.value; });
  }

  if (addQtyBtn) {
    addQtyBtn.addEventListener('click', () => {
      const template  = getEl('order-row-template');
      const tbodyEdit = getEl('order_table_body_edit');

      const raw = quantitySlider.value;                 // 例: "12"
      const val = formatNumber(toNumber(raw), 0);       // 整数・カンマ付

      const rows = tbodyEdit.getElementsByTagName('tr');

      for (let i = 0; i < rows.length; i++) {
        const qtyInput = qs('td:nth-child(4) input', rows[i]);
        if (qtyInput && qtyInput.value.trim() === '') {
          qtyInput.value = val;
          const steelName = qs('td:nth-child(2) input', rows[i])?.value?.trim();
          const unitW = steelName ? findUnitWeightByName(steelName) : 0;
          updateWeightsForRow(rows[i], unitW);
          if (typeof updateSummary === 'function') updateSummary?.();
          return;
        }
      }

      addOrderRow(template, tbodyEdit);
      const lastRow  = tbodyEdit.lastElementChild;
      const qtyInput = qs('td:nth-child(4) input', lastRow);
      if (qtyInput) qtyInput.value = val;

      const steelName = qs('td:nth-child(2) input', lastRow)?.value?.trim();
      const unitW = steelName ? findUnitWeightByName(steelName) : 0;
      updateWeightsForRow(lastRow, unitW);
      if (typeof updateSummary === 'function') updateSummary?.();
    });
  }

  // --- 貼り付けボタン（parse/count） ---
  const parseFillButton = getEl("parse-fill-button");
  if (parseFillButton) { parseFillButton.addEventListener("click", handleParseFill); }

  const countFillButton = getEl("count-fill-button");
  if (countFillButton) { countFillButton.addEventListener("click", handleCountFill); }

  // --- オートコンプリート（履歴） ---
  setupAutoComplete('project_name', 'project_name_list', 'history_project_name');
  setupAutoComplete('chief_date',   'chief_date_list',   'history_chief_date');
  setupAutoComplete('company_name', 'company_name_list', 'history_company_name');
  setupAutoComplete('tel',          'tel_list',          'history_tel');
  setupAutoComplete('fax',          'fax_list',          'history_fax');
  setupAutoComplete('email',        'email_list',        'history_email');

  // --- フォーム保存/復元 ---
  const form = document.querySelector("form");
  if (form) { form.addEventListener("submit", saveFormToLocalStorage); }

  // --- 印刷プレビュー ---
  const previewBtn = getEl('print-preview-btn');
  if (previewBtn) previewBtn.addEventListener('click', runPreview);

  // 編集テーブルの数値入力を「表示はカンマ・計算は素」に統一
  const tbodyEdit = getEl('order_table_body_edit');
  if (tbodyEdit && !tbodyEdit.__commaWired){
    // フォーカス時: 生値（カンマ無し）にして編集しやすく
    tbodyEdit.addEventListener('focusin', (e)=>{
      const t = e.target;
      if (!(t instanceof HTMLInputElement)) return;
      if (!/^(steel_size\[\]|quantity\[\]|unit_weight\[\]|total_weight\[\])$/.test(t.name)) return;
      t.value = unformatNumber(t.value);
    });

    // フォーカスアウト時: 表示はカンマ付きに整形
    tbodyEdit.addEventListener('focusout', (e)=>{
      const t = e.target;
      if (!(t instanceof HTMLInputElement)) return;
      if (!/^(steel_size\[\]|quantity\[\]|unit_weight\[\]|total_weight\[\])$/.test(t.name)) return;
      const n = toNumber(t.value);
      const decimals =
        (t.name === 'unit_weight[]' || t.name === 'total_weight[]') ? 2 :
        (t.name === 'steel_size[]' ? decimalsOf(t.value) : 0); // 寸法は元の小数桁を維持
      t.value = formatNumber(n, decimals);
    });

    tbodyEdit.__commaWired = true; // 二重バインド防止フラグ
  }
}

// 行番号の見た目だけを更新（必要な場面用）
function updateRowDisplayNumbers() {
  const rows = qsa('#order_table_body_edit > tr');
  rows.forEach((row, idx) => {
    const noCell = row.cells[COL_IDX_ROW_NO];
    if (noCell) { noCell.textContent = idx + 1; }
  });
}

// 現在のデータ行数を反映（サマリ行を含めない用途では getDataRows を使う）
function updateRowCount() {
  currentRowNumber = qsa('#order_table_body_edit > tr').length;
}

// ✅ 開始ログ（読み込み確認）
console.log("✅ steel-materials-order-app.js loaded");

// <template> が別の <template> の内側に入っている誤配置を救出
function extractOrderRowTemplateToBody() {
  const template = document.getElementById("order-row-template");
  if (template && template.parentElement.tagName === "TEMPLATE") {
    console.warn("⚠️ order-row-template が別の <template> 内にあります。body に移動します。");
    document.body.appendChild(template);
  }
}

// 0.5mm刻み丸め用の定数・関数（行高の微調整向け）
const ROUND_TO = 0.5;
const roundTo = (v, step=ROUND_TO) => Math.round(v/step)*step;
// function roundTo(x, step = 0.5) { return Math.round(x / step) * step; }

// ==== 固定ギャップ（用紙端との見た目の余白）====
const HEADER_TOP_GAP_MM    = 15;   // 上端→ヘッダー枠 見かけの余白
const SAFE_BODY_GAP_MM     = 0.2;  // 本文との安全距離（にじみ防止）※必要なら使用
const SAFE_BODY_GAP_BOTTOM_MM = 0.2;  // フッター側
const FOOTER_BOTTOM_GAP_MM = 10;    // フッター枠→下端 見かけの余白

// 既存の定数名互換（他所から参照される可能性を考慮）
const HEADER_GAP_MM = (typeof HEADER_TOP_GAP_MM !== 'undefined') ? HEADER_TOP_GAP_MM : 10;
const FOOTER_GAP_MM = (typeof FOOTER_BOTTOM_GAP_MM !== 'undefined') ? FOOTER_BOTTOM_GAP_MM : 5;

// 微調整量（mm）と最低値（mm）
const MARGIN_EXTRA = { header: 0, footer: 0 }; // 必要に応じて ±0.5mm ずつ調整
const MARGIN_MIN   = { header: 0,  footer: 0   }; // 下限

// 用紙高さ（A4 横: 210mm）
const A4H_MM = 210;

// 7) 印刷パイプライン（計測→算出→分割） ==================
// 計算結果の CSS 変数を :root に書き出す（行高・ヘッダー/フッター高）
function writeComputedVars({headerMm, footerMm, rowMm}){
  const css =
    `:root{
      --header-h: ${headerMm.toFixed(3)}mm;
      --footer-h: ${footerMm.toFixed(3)}mm;
      --row-h-mm: ${rowMm.toFixed(3)}mm;
    }`;
  let s = document.getElementById('print-vars-override');
  if(!s){ s = document.createElement('style'); s.id = 'print-vars-override'; document.head.appendChild(s); }
  s.textContent = css;
}

// 余白を mm 単位で @page に上書き（ヘッダー/フッターの実寸に追従）
function applyPageMargins(headerMm, footerMm, {left=8, right=8} = {}){
  const TOP    = +(headerMm + HEADER_GAP_MM).toFixed(3);
  const BOTTOM = +(footerMm + FOOTER_GAP_MM).toFixed(3);
  const css = `@page{
    /* A4 横向き（数値指定で強制）*/
    size: 297mm 210mm;
    margin: ${TOP}mm ${right}mm ${BOTTOM}mm ${left}mm;
    @top-center    { content: element(header); }
    @bottom-center { content: element(footer); }
  }`;
  let s = document.getElementById('page-margins-override');
  if (!s) { s = document.createElement('style'); s.id = 'page-margins-override'; document.head.appendChild(s); }
  s.textContent = css;
  console.log('[applyPageMargins] wrote:', css);
}

// thead + 本文(行数指定) が“ピッタリ”収まる行高を算出して CSS 変数へ反映
function computeAndSetRowHeight({headerPx, footerPx, theadPx}, rowsPerPage){
  // ▼ CSS 変数（つまみ）を取得
  const rows   = rowsPerPage ?? cssInt('--rows-per-page', 20);
  const scale  = cssNum('--row-auto-scale', 1);
  const bias   = cssNum('--row-auto-bias-mm', 0);
  const snap   = cssNum('--row-snap-mm', 0);
  const minMm  = cssNum('--row-min-mm', 4.5);

  const headerMm = pxToMm(headerPx);
  const footerMm = pxToMm(footerPx);
  const theadMm  = pxToMm(theadPx);

  // 罫線厚みの見積り（thead/tbody の下線幅を代表値として使用）
  const basePrint = document.querySelector('.order-table-print');
  let borderPx = 1;
  const probe = basePrint?.querySelector('thead th, thead td, tbody td');
  if (probe) borderPx = parseFloat(getComputedStyle(probe).borderBottomWidth || '1') || 1;
  const borderMm  = pxToMm(borderPx);
  const bordersMm = (rows + 3) * borderMm; // 既存ロジック踏襲（ヘッダー/フッター分を含めた見積り）

  // 本文に割り当て可能な高さ（上下の見かけ余白を差し引き）
  const bodyAvailMm = A4H_MM - (headerMm + HEADER_GAP_MM) - (footerMm + FOOTER_GAP_MM);

  // ★ベース行高の自動計算
  let rowMm = (bodyAvailMm - theadMm - bordersMm) / rows;

  // ★“つまみ”で調整
  rowMm = rowMm * scale + bias;    // 拡大/縮小 + mm オフセット
  rowMm = snapMm(rowMm, snap);     // 任意刻みにスナップ
  rowMm = Math.max(minMm, rowMm);  // 下限

  // ★安全上限（わずかに余白を残す）
  const maxRowMm = (bodyAvailMm - theadMm - bordersMm - 0.1) / rows; // 0.1mm マージン
  rowMm = Math.min(rowMm, maxRowMm);

  // 反映
  writeComputedVars({headerMm, footerMm, rowMm});
  applyPageMargins(headerMm, footerMm);

  console.log('[row-calc+knob]', 'rows=', rows, 'scale=', scale, 'bias=', bias, 'snap=', snap, 'min=', minMm, '=> row=', rowMm.toFixed(3), 'mm');
}

// 空行を 1 行作る（印刷の 20 行埋めに使用）
function makeBlankRow(){
  const tr = document.createElement('tr');
  tr.dataset.blank = '1';
  for (let i=0; i<8; i++){
    const td = document.createElement('td');
    td.innerHTML = '&nbsp;';
    tr.appendChild(td);
  }
  return tr;
}

// 印刷用テーブルをページ単位に分割して .print-area に並べる
function buildPagedPrintTables(rowsPerPage){
  rowsPerPage = rowsPerPage ?? cssInt('--rows-per-page', 20);

  console.log('[buildPagedPrintTables] start:', rowsPerPage);
  const area  = document.querySelector('.print-area');
  const base  = area?.querySelector('table.order-table-print');
  if (!area || !base) return;

  // 既存の分割結果を掃除
  area.querySelectorAll('table.page-table').forEach(t => t.remove());

  const thead   = base.querySelector('thead')?.cloneNode(true);
  const srcBody = base.querySelector('tbody');
  if (!thead || !srcBody) return;

  // 元データ行は「読むだけ」。ここでは base/srcBody を破壊しない
  const dataRows = Array.from(srcBody.querySelectorAll('tr'));

  const pageCount = Math.max(1, Math.ceil(dataRows.length / rowsPerPage));

  const made = [];
  for (let p = 0; p < pageCount; p++){
    // 元テーブルの属性（class等）は維持しつつ、.page-table を付与
    const t = base.cloneNode(false);
    t.classList.add('page-table');

    const h = thead.cloneNode(true);
    const b = document.createElement('tbody');

    // 各ページの tbody は「常に20行」：不足分は空行で埋める
    for (let j = 0; j < rowsPerPage; j++){
      const idx = p * rowsPerPage + j;
      const src = dataRows[idx];
      b.appendChild(src ? src.cloneNode(true) : makeBlankRow());
    }

    t.appendChild(h);
    t.appendChild(b);
    area.appendChild(t);
    made.push(t);
  }

  // 最後の 1 枚だけ改ページしない（余計な空白ページを避ける）
  made.forEach((tbl, i) => {
    const isLast = i === made.length - 1;
    tbl.style.setProperty('break-after',      isLast ? 'auto'   : 'page',   'important');
    tbl.style.setProperty('page-break-after', isLast ? 'auto'   : 'always', 'important');
  });

  // 元の巨大テーブルは非表示（破壊しない）
  base.style.display = 'none';
  console.log('[buildPagedPrintTables] done. pages=', pageCount);
}

// Paged.js が作った複製DOMから「空ページ」を除去
function pruneEmptyPages(){
  const root = getPagesRoot();
  if (!root) return;
  const pages = [...root.querySelectorAll('.pagedjs_page')];
  let removed = 0;
  pages.forEach(p => {
    // 本体テーブル（table.page-table）が1つも無いページを削除
    if (!p.querySelector('table.page-table')) { p.remove(); removed++; }
  });
  if (removed) console.warn(`[pruneEmptyPages] removed ${removed} empty page(s)`);
}

// 複数の .pagedjs_pages が残ってしまった場合に古い方をクリア
function clearOldPages() {
  document.querySelectorAll('.pagedjs_pages').forEach((n,i) => {
    if (i !== 0) n.remove(); // 最新だけ残す。全削除したい場合は if を外す
  });
}

// 下部の余白を平均化しつつ行高を微増させて「隙間」を詰める微調整
async function tightenBottomGap(rowsPerPage = 20, maxIters = 2){
  for (let iter = 0; iter < maxIters; iter++){
    // 最新のページ群のみ対象
    const pagesRoot = [...document.querySelectorAll('.pagedjs_pages')].pop();
    if (!pagesRoot) break;
    const pages = [...pagesRoot.querySelectorAll('.pagedjs_page')];

    const gapsPx = [];
    for (const p of pages){
      const footBox = p.querySelector('.pagedjs_margin-bottom-center');
      const lastRow = p.querySelector('.page-table tbody tr:last-child');
      if (!footBox || !lastRow) continue;
      const gapPx = footBox.getBoundingClientRect().top - lastRow.getBoundingClientRect().bottom;
      if (gapPx > 0 && gapPx < 200) gapsPx.push(gapPx); // 異常値は除外
    }
    const avgPx = gapsPx.length ? gapsPx.reduce((a,b)=>a+b,0) / gapsPx.length : 0;

    // 0.5px 未満なら誤差として終了
    if (avgPx < 0.5) break;

    // 平均隙間を 20 行に等配して行高を増やす
    const deltaMm = pxToMm(avgPx) / rowsPerPage;

    // 現在の行高を取得して上書き（style 変数に直接）
    const curr = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--row-h-mm')) || 8;
    document.documentElement.style.setProperty('--row-h-mm', (curr + deltaMm).toFixed(3) + 'mm');

    // 再分割→再プレビュー
    buildPagedPrintTables(rowsPerPage);
    clearOldPages();
    await PagedPolyfill.preview();
  }
}

// ページごとの上部/下部の隙間（px）をログ出力するデバッグ用
function logGaps(){
  document.querySelectorAll('.pagedjs_page').forEach((page, i)=>{
    const topBox   = page.querySelector('.pagedjs_margin-top-center');
    const footBox  = page.querySelector('.pagedjs_margin-bottom-center');
    const firstTbl = page.querySelector('.page-table');
    const lastRow  = page.querySelector('.page-table tbody tr:last-child');
    if (!topBox || !footBox || !firstTbl || !lastRow) return;

    const gapTopPx = firstTbl.getBoundingClientRect().top - topBox.getBoundingClientRect().bottom;
    const gapBotPx = footBox.getBoundingClientRect().top - lastRow.getBoundingClientRect().bottom;
    console.log(`page ${i+1}: gapTop=${gapTopPx.toFixed(2)}px, gapBottom=${gapBotPx.toFixed(2)}px`);
  });
}

// 8) フロー制御 ==========================================
// input/select/textarea の現在値を HTML 属性へ反映して「静的化」
// （Paged.js が複製DOMを生成する前に呼ぶことで、値の取りこぼしを防止）
function freezeFormValues(root=document) {
  root.querySelectorAll('input, textarea, select').forEach(el => {
    if (el.tagName === 'SELECT') {
      [...el.options].forEach(o => o.removeAttribute('selected'));
      const sel = el.options[el.selectedIndex];
      if (sel) sel.setAttribute('selected', 'selected');
    } else if (el.tagName === 'TEXTAREA') {
      el.textContent = el.value ?? '';
    } else {
      el.setAttribute('value', el.value ?? '');
    }
  });
}

// PagedPolyfill.preview() 実行 → 直後に空ページの刈り取り
async function previewAndPrune(){
  await PagedPolyfill.preview();
  pruneEmptyPages();
}

// 入力チェック & エラーハイライト 数値/範囲検証 セル単位の強調
function validateRow(row){
  const errs=[];
  const len = toNumber(qs('td:nth-child(3) input', row)?.value);
  const qty = toNumber(qs('td:nth-child(4) input', row)?.value);
  if (len <= 0) errs.push(['寸法', 3]);
  if (!Number.isInteger(qty) || qty<=0) errs.push(['本数', 4]);
  errs.forEach(([label, col])=>{
    const td = row.cells[col-1]; td.classList.add('is-error');
    td.title = `${label}の値を見直してください`;
  });
  return errs.length === 0;
}
function validateAll(){
  qsa('#order_table_body_edit tr').forEach(tr=>{
    tr.querySelectorAll('.is-error').forEach(td=>{ td.classList.remove('is-error'); td.removeAttribute('title'); });
    validateRow(tr);
  });
}

// 印刷プレビューのメインフロー
// 1) 古い複製DOMをクリーン → 2) 編集→印刷同期 → 3) 値の静的化
// 4) 物理寸法計測 → 5) 行高算出 → 6) 分割生成 → 7) プレビュー → 8) 必要なら詰め調整
async function runPreview(){
  if (running) return; running = true;                   // 多重実行防止
  try{
    clearOldPages();
    syncToPrintTable();
    formatAllVisibleNumbers();
    freezeFormValues();

    const basePrint = document.querySelector('.order-table-print');
    if (basePrint) basePrint.style.display = 'table';

    // 物理寸法の計測（printing クラス付与でスタイル確定 → 次フレームで測る）
    document.body.classList.add('printing');
    await new Promise(r => requestAnimationFrame(r));

    const headerPx = document.querySelector('.running-header .print-header-wrapper')?.getBoundingClientRect().height || 0;
    const footerPx = document.querySelector('.running-footer .print-footer')?.getBoundingClientRect().height || 0;
    let theadPx    = basePrint?.querySelector('thead')?.getBoundingClientRect().height || 0;
    if (!theadPx) {
      // thead が非表示のケースに備えて、既定の行高から見積もるフォールバック
      const mm = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--row-h-mm')) || 7.5;
      theadPx = mm * 96 / 25.4;
    }

    const rows = cssInt('--rows-per-page', 20);
    computeAndSetRowHeight({headerPx, footerPx, theadPx}, rows);

    document.querySelector('.print-area')?.classList.add('is-printing');

    buildPagedPrintTables(rows);
    await previewAndPrune(); // ★ 空ページの自動削除

    const tightenIters = cssInt('--row-tighten-iters', 0);
    if (tightenIters > 0) {
      await tightenBottomGap(rows, tightenIters);
      pruneEmptyPages(); // ★ つめ直後に念のためもう一度
    }

    logGaps && logGaps();
  } catch(e){
    console.error('Paged preview failed:', e);
  } finally {
    running = false;
  }
}

// 9) 初期化 ==============================================
// 起動直後の 1 回だけ呼ぶ初期化（20 行生成など）。
function initializeApp(template, tbodyEdit) {
  console.log("📦 initializeApp 実行開始");

  // 初期 20 行生成（編集用 tbody のみ）
  if (template && tbodyEdit) {
    for (let i = 0; i < 20; i++) {
      addOrderRow(template, tbodyEdit);
    }
  }

  // 行追加ボタン（編集用だけ）
  const addRowButton = document.getElementById('add_row_button');
  if (addRowButton) {
    addRowButton.addEventListener("click", () => { addOrderRow(template, tbodyEdit); });
  } else {
    console.warn("⚠️ #add_row_button が見つかりません");
  }
  initialized = true;
}

// DOM 準備待ちのリトライ（テンプレート/ tbody が遅延して挿入されるケース向け）
function waitForTemplateAndTbody(retry = 0) {
  if (initialized) return; // 二重実行防止
  const template = document.getElementById('order-row-template');
  const tbodyEdit = document.getElementById('order_table_body_edit');
  if (template && tbodyEdit) {
    initializeApp(template, tbodyEdit);
    ensureSummaryRow();
    updateSummary();
    return;
  }
  if (retry < 5) {
    setTimeout(() => waitForTemplateAndTbody(retry + 1), 300);
  } else {
    console.error('❌ テンプレートまたは tbodyEdit が見つかりません（最大リトライ回数到達）');
  }
}

// 実 DOM のヘッダー/フッター高さを px で測って CSS 変数に反映（必要なら使用）
function calibratePageMarginsFromHeaderFooter() {
  const headerBox = document.querySelector('.running-header .print-header-wrapper');
  const footerBox = document.querySelector('.running-footer .print-footer');
  if (!headerBox || !footerBox) return;

  const headerPx = headerBox.getBoundingClientRect().height;
  const footerPx = footerBox.getBoundingClientRect().height;

  // mm に変換（小数1桁で丸めると安定）
  const headerMm = Math.round(pxToMm(headerPx) * 10) / 10;
  const footerMm = Math.round(pxToMm(footerPx) * 10) / 10;

  // CSS 変数に反映 → @page margin が更新される
  const root = document.documentElement.style;
  root.setProperty('--header-h', `${headerMm}mm`);
  root.setProperty('--footer-h', `${footerMm}mm`);

  console.log('[calibrate] header:', headerPx, 'px ->', headerMm, 'mm', '/ footer:', footerPx, 'px ->', footerMm, 'mm');
}

// Paged.js が生成した最後の複製DOM（最新）を取る
function getPagesRoot(){
  return [...document.querySelectorAll('.pagedjs_pages')].pop() || null;
}

// 生成済みページから thead/ヘッダー/フッターの実寸を再計測（デバッグ用）
function measureFromRealPage(){
  const pagesRoot = [...document.querySelectorAll('.pagedjs_pages')].pop();
  const firstPage = pagesRoot?.querySelector('.pagedjs_page');
  const theadPx = firstPage?.querySelector('.page-table thead')?.getBoundingClientRect().height || 0;
  const headPx  = firstPage?.querySelector('.pagedjs_margin-top-center .pagedjs_margin-content')?.getBoundingClientRect().height || 0;
  const footPx  = firstPage?.querySelector('.pagedjs_margin-bottom-center .pagedjs_margin-content')?.getBoundingClientRect().height || 0;
  return {theadPx, headPx, footPx};
}

// DOM 準備完了で初期化を 1 回だけ実行
// （既に HTML 側で defer/async の制御がされていても安全に動く）
document.addEventListener('DOMContentLoaded', init, { once: true });