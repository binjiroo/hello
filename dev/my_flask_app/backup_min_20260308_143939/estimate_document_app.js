(function () {
  "use strict";

  function toNum(v) {
    if (v == null) return 0;
    var s = String(v).replace(/,/g, "").trim();
    if (!s) return 0;
    var n = Number(s);
    return Number.isFinite(n) ? n : 0;
  }

  function yenRound(v) {
    return Math.round(v);
  }

  function calcRow(row) {
    var qty = toNum(row.querySelector('input[name="quantity[]"]')?.value);
    var unitPrice = toNum(row.querySelector('input[name="unit_price[]"]')?.value);
    var discount = toNum(row.querySelector('input[name="discount[]"]')?.value);
    var lineTotal = Math.max(0, yenRound(qty * unitPrice - discount));
    var lineTotalInput = row.querySelector('input[name="line_total[]"]');
    if (lineTotalInput) lineTotalInput.value = String(lineTotal);
    return lineTotal;
  }

  function calcAll() {
    var body = document.getElementById("ed-lines-body");
    if (!body) return;

    var rows = Array.from(body.querySelectorAll("tr"));
    var taxable10 = 0;
    var taxable8 = 0;
    var taxable0 = 0;

    rows.forEach(function (row) {
      var total = calcRow(row);
      var taxRate = row.querySelector('select[name="tax_rate[]"]')?.value || "10";
      if (taxRate === "8") taxable8 += total;
      else if (taxRate === "0") taxable0 += total;
      else taxable10 += total;
    });

    var consumptionTax = yenRound(taxable10 * 0.1) + yenRound(taxable8 * 0.08);
    var subtotal = taxable10 + taxable8 + taxable0;
    var total = subtotal + consumptionTax;

    var set = function (id, value) {
      var el = document.getElementById(id);
      if (el) el.value = String(value);
    };

    set("ed-taxable-10", taxable10);
    set("ed-taxable-8", taxable8);
    set("ed-taxable-0", taxable0);
    set("ed-tax-excluded", subtotal);
    set("ed-tax", consumptionTax);
    set("ed-subtotal", subtotal);
    set("ed-tax-again", consumptionTax);
    set("ed-total", total);
  }

  function buildRow() {
    var tr = document.createElement("tr");
    tr.innerHTML = [
      "<td></td>",
      '<td><input type="text" name="description[]" list="ed-description-options" value=""></td>',
      '<td><input type="number" step="0.001" min="0" name="quantity[]" value=""></td>',
      '<td><input type="text" name="unit[]" list="ed-unit-options" value=""></td>',
      '<td><input type="number" step="1" min="0" name="unit_price[]" value=""></td>',
      '<td><input type="number" step="1" min="0" name="discount[]" value=""></td>',
      '<td><select name="tax_rate[]"><option value="10" selected>10%</option><option value="8">8%</option><option value="0">0%</option></select></td>',
      '<td><input type="number" step="1" min="0" name="line_total[]" value="0" readonly></td>',
      '<td><button type="button" class="ed-delete-row">削除</button></td>'
    ].join("");
    return tr;
  }

  function renumberEstimateRows(body) {
    if (!body) return;
    var rows = Array.from(body.querySelectorAll("tr"));
    rows.forEach(function (row, idx) {
      var noCell = row.querySelector("td");
      if (noCell) noCell.textContent = String(idx + 1);
    });
  }

  function applyCheckedAddonsToRows() {
    var body = document.getElementById("ed-lines-body");
    if (!body) return;
    var addDesc = document.getElementById("ed-check-add-description");
    var addUnit = document.getElementById("ed-check-add-unit");
    var rows = Array.from(body.querySelectorAll("tr"));

    rows.forEach(function (row) {
      var descInput = row.querySelector('input[name="description[]"]');
      var unitInput = row.querySelector('input[name="unit[]"]');

      if (addDesc && addDesc.checked && descInput) {
        var token = "見積合計額(税抜)";
        var current = (descInput.value || "").trim();
        if (!current) {
          descInput.value = token;
        } else if (!current.includes(token)) {
          descInput.value = current + " " + token;
        }
      }

      if (addUnit && addUnit.checked && unitInput) {
        unitInput.value = "式";
      }
    });
  }

  function renumberDetailRows(body) {
    var rows = Array.from(body.querySelectorAll("tr"));
    rows.forEach(function (row, idx) {
      var noCell = row.querySelector("td");
      if (noCell) noCell.textContent = String(idx + 1);
    });
  }

  function calcDetailRow(row) {
    var qty = toNum(row.querySelector('input[name="detail_quantity[]"]')?.value);
    var unitPrice = toNum(row.querySelector('input[name="detail_unit_price[]"]')?.value);
    var amount = yenRound(qty * unitPrice);
    var amountInput = row.querySelector('input[name="detail_amount[]"]');
    if (amountInput) amountInput.value = String(amount);
    return amount;
  }

  function calcDetailAll() {
    var body = document.getElementById("dd-lines-body");
    if (!body) return;
    var subtotal = 0;
    Array.from(body.querySelectorAll("tr")).forEach(function (row) {
      subtotal += calcDetailRow(row);
    });
    var adjustment = toNum(document.getElementById("dd-adjustment")?.value);
    var total = subtotal + adjustment;
    var subtotalEl = document.getElementById("dd-subtotal");
    var totalEl = document.getElementById("dd-total");
    if (subtotalEl) subtotalEl.value = String(subtotal);
    if (totalEl) totalEl.value = String(total);
  }

  function buildDetailRow(description, unit) {
    var tr = document.createElement("tr");
    tr.innerHTML = [
      "<td></td>",
      '<td><input type="text" name="detail_description[]" list="dd-description-options" value=""></td>',
      '<td><input type="number" step="0.001" min="0" name="detail_quantity[]" value=""></td>',
      '<td><input type="text" name="detail_unit[]" list="dd-unit-options" value=""></td>',
      '<td><input type="number" step="0.001" min="0" name="detail_weight_kg[]" value=""></td>',
      '<td><input type="number" step="1" min="0" name="detail_unit_price[]" value=""></td>',
      '<td><input type="number" step="1" min="0" name="detail_amount[]" value="0" readonly></td>',
      '<td><button type="button" class="dd-delete-row">削除</button></td>'
    ].join("");
    if (description) {
      var d = tr.querySelector('input[name="detail_description[]"]');
      if (d) d.value = description;
    }
    if (unit) {
      var u = tr.querySelector('input[name="detail_unit[]"]');
      if (u) u.value = unit;
    }
    return tr;
  }

  function getPrintablePageSizePx() {
    var orientationEl = document.getElementById("ed-paper-orientation");
    var orientation = orientationEl ? orientationEl.value : "portrait";
    var mmToPx = 96 / 25.4;
    var contentWidthMm = orientation === "landscape" ? 287 : 200;
    var contentHeightMm = orientation === "landscape" ? 200 : 287;
    return {
      width: Math.floor(contentWidthMm * mmToPx),
      height: Math.floor(contentHeightMm * mmToPx)
    };
  }

  function estimatePrintPageCount() {
    var form = document.getElementById("ed-form");
    if (!form) return 1;

    var size = getPrintablePageSizePx();
    if (!size.width || !size.height) return 1;

    var sandbox = document.createElement("div");
    sandbox.style.position = "fixed";
    sandbox.style.left = "-20000px";
    sandbox.style.top = "0";
    sandbox.style.visibility = "hidden";
    sandbox.style.pointerEvents = "none";
    sandbox.style.width = size.width + "px";

    var wrap = document.createElement("div");
    wrap.className = "ed-wrap ed-print-mode";
    wrap.style.maxWidth = "none";
    wrap.style.padding = "0";
    wrap.style.width = size.width + "px";

    var clone = form.cloneNode(true);
    Array.from(clone.querySelectorAll(".no-print")).forEach(function (el) {
      el.remove();
    });

    wrap.appendChild(clone);
    sandbox.appendChild(wrap);
    document.body.appendChild(sandbox);

    var contentHeight = wrap.scrollHeight || wrap.getBoundingClientRect().height || 0;
    sandbox.remove();
    if (contentHeight <= 0) return 1;
    return Math.max(1, Math.ceil(contentHeight / size.height));
  }

  var isRestoringState = false;

  function tryAddWithoutPageIncrease(addFn) {
    if (typeof addFn !== "function") return null;
    if (isRestoringState) return addFn();
    var beforePages = estimatePrintPageCount();
    var added = addFn();
    if (!added) return null;
    var afterPages = estimatePrintPageCount();
    if (afterPages > beforePages) {
      if (added.parentNode) added.parentNode.removeChild(added);
      window.alert("これ以上行を追加すると印刷時にページ数が増えるため、追加を中止しました。");
      return null;
    }
    return added;
  }

  function addDetailRow(body, description, unit, forceAdd) {
    var added = null;
    var addFn = function () {
      var row = buildDetailRow(description, unit);
      body.appendChild(row);
      return row;
    };
    if (forceAdd) {
      added = addFn();
    } else {
      added = tryAddWithoutPageIncrease(addFn);
      if (!added) return null;
    }
    renumberDetailRows(body);
    calcDetailAll();
    return added;
  }

  function fillDetailFieldFromTopOrAppend(body, fieldName, value) {
    if (!value) return;
    var rows = Array.from(body.querySelectorAll("tr"));
    for (var i = 0; i < rows.length; i += 1) {
      var input = rows[i].querySelector('input[name="' + fieldName + '"]');
      if (input && !(input.value || "").trim()) {
        input.value = value;
        calcDetailAll();
        return;
      }
    }
    if (fieldName === "detail_description[]") {
      addDetailRow(body, value, "");
    } else if (fieldName === "detail_unit[]") {
      addDetailRow(body, "", value);
    }
  }

  function renumberRowsByBody(body) {
    var rows = Array.from(body.querySelectorAll("tr"));
    rows.forEach(function (row, idx) {
      var noCell = row.querySelector("td");
      if (noCell) noCell.textContent = String(idx + 1);
    });
  }

  function fillFieldFromTopOrAppend(body, fieldName, value, appendCallback) {
    if (!value) return;
    var rows = Array.from(body.querySelectorAll("tr"));
    for (var i = 0; i < rows.length; i += 1) {
      var input = rows[i].querySelector('input[name="' + fieldName + '"]');
      if (input && !(input.value || "").trim()) {
        input.value = value;
        return;
      }
    }
    appendCallback(value);
  }

  var STORAGE_KEY = "estimate_document_state_v1";

  function getStoredState() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return {};
      var parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== "object") return {};

      // Normalize legacy snapshots: never persist/restore selector state.
      Object.keys(parsed).forEach(function (docKey) {
        var doc = parsed[docKey];
        if (!doc || typeof doc !== "object") return;
        if (Object.prototype.hasOwnProperty.call(doc, "doc_type")) {
          delete doc.doc_type;
        }
      });
      return parsed;
    } catch (_) {
      return {};
    }
  }

  function setStoredState(state) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state || {}));
    } catch (_) {}
  }

  function collectFormState(form) {
    var result = {};
    Array.from(form.elements).forEach(function (el) {
      if (!el || !el.name || el.disabled) return;
      if (el.name === "doc_type") return;
      var type = (el.type || "").toLowerCase();
      if (type === "button" || type === "submit" || type === "reset" || type === "file") return;
      if (!result[el.name]) result[el.name] = [];
      if (type === "checkbox" || type === "radio") {
        result[el.name].push({ type: type, checked: !!el.checked, value: el.value });
      } else {
        result[el.name].push({ type: type || "text", value: el.value });
      }
    });
    return result;
  }

  function createNoteRow(prefix, index, value) {
    var row = document.createElement("div");
    row.className = "ed-row ed-note-row";
    row.innerHTML =
      '<label>備考</label>' +
      '<input type="text" name="' +
      prefix +
      "_note_" +
      index +
      '" value="" style="min-width:70%;">' +
      '<button type="button" class="ed-note-delete-row">削除</button>';
    var input = row.querySelector("input");
    if (input && value != null) input.value = String(value);
    return row;
  }

  function renumberNoteRows(card) {
    var prefix = card ? card.getAttribute("data-note-prefix") : "";
    if (!prefix) return;
    var rows = Array.from(card.querySelectorAll(".ed-note-row"));
    if (rows.length === 0) {
      var addWrap = card.querySelector(".ed-right");
      var first = createNoteRow(prefix, 1, "");
      if (addWrap && addWrap.parentNode) addWrap.parentNode.insertBefore(first, addWrap);
      rows = [first];
    }
    rows.forEach(function (row, idx) {
      var input = row.querySelector('input[name*="_note_"]');
      if (input) input.name = prefix + "_note_" + String(idx + 1);
    });
  }

  function ensureNoteRowsByPrefix(prefix, needed) {
    if (!prefix || needed <= 0) return;
    var card = document.querySelector('.ed-note-card[data-note-prefix="' + prefix + '"]');
    if (!card) return;
    var rows = Array.from(card.querySelectorAll(".ed-note-row"));
    var addWrap = card.querySelector(".ed-right");
    while (rows.length < needed) {
      var row = createNoteRow(prefix, rows.length + 1, "");
      if (addWrap && addWrap.parentNode) addWrap.parentNode.insertBefore(row, addWrap);
      else card.appendChild(row);
      rows.push(row);
    }
    renumberNoteRows(card);
  }

  function initNoteCards(form) {
    var cards = Array.from(form.querySelectorAll(".ed-note-card"));
    cards.forEach(function (card) {
      if (card.dataset.noteReady === "1") return;
      card.dataset.noteReady = "1";
      renumberNoteRows(card);
      var addBtn = card.querySelector(".ed-note-add-row");
      if (addBtn) {
        addBtn.addEventListener("click", function () {
          var prefix = card.getAttribute("data-note-prefix");
          if (!prefix) return;
          var addWrap = card.querySelector(".ed-right");
          var rows = Array.from(card.querySelectorAll(".ed-note-row"));
          var row = tryAddWithoutPageIncrease(function () {
            var created = createNoteRow(prefix, rows.length + 1, "");
            if (addWrap && addWrap.parentNode) addWrap.parentNode.insertBefore(created, addWrap);
            else card.appendChild(created);
            return created;
          });
          if (!row) return;
          renumberNoteRows(card);
          var input = row.querySelector('input[name*="_note_"]');
          if (input) input.focus();
        });
      }
      card.addEventListener("click", function (e) {
        var target = e.target;
        if (!(target instanceof HTMLElement)) return;
        if (!target.classList.contains("ed-note-delete-row")) return;
        var row = target.closest(".ed-note-row");
        if (!row) return;
        row.remove();
        renumberNoteRows(card);
      });
    });
  }

  function ensureRowCountByName(form, name, needed) {
    if (needed <= 0) return;
    var buttonMap = {
      "description[]": "ed-add-row-btn",
      "detail_description[]": "dd-add-row-btn",
      "material_description[]": "md-add-row-btn",
      "outsource_description[]": "os-add-row-btn",
      "factory_description[]": "fl-add-row-btn",
      "site_description[]": "sl-add-row-btn",
      "zinc_description[]": "zn-add-row-btn"
    };
    var addBtnId = buttonMap[name];
    if (!addBtnId) return;
    var addBtn = document.getElementById(addBtnId);
    if (!addBtn) return;
    var current = Array.from(form.elements).filter(function (el) {
      return el && el.name === name;
    }).length;
    var guard = 0;
    while (current < needed && guard < 200) {
      addBtn.click();
      current += 1;
      guard += 1;
    }
  }

  function restoreFormState(form, docType) {
    if (!docType) return;
    var all = getStoredState();
    var docState = all[docType];
    if (!docState || typeof docState !== "object") return;

    isRestoringState = true;
    try {
      Object.keys(docState).forEach(function (name) {
        if (name === "doc_type") return;
        var entries = docState[name];
        if (!Array.isArray(entries)) return;
        if (name.endsWith("[]")) {
          ensureRowCountByName(form, name, entries.length);
        } else {
          var noteMatch = name.match(/^([a-z]+)_note_(\d+)$/);
          if (noteMatch) {
            ensureNoteRowsByPrefix(noteMatch[1], Number(noteMatch[2]));
          }
        }
      });

      Object.keys(docState).forEach(function (name) {
        if (name === "doc_type") return;
        var entries = docState[name];
        if (!Array.isArray(entries)) return;
        var els = Array.from(form.elements).filter(function (el) {
          return el && el.name === name;
        });
        var max = Math.min(entries.length, els.length);
        for (var i = 0; i < max; i += 1) {
          var el = els[i];
          var entry = entries[i] || {};
          var type = (el.type || "").toLowerCase();
          if (type === "checkbox" || type === "radio") {
            el.checked = !!entry.checked;
          } else if (entry.value != null) {
            el.value = String(entry.value);
          }
        }
      });
    } finally {
      isRestoringState = false;
    }
  }

  function saveCurrentDocState(form, docType) {
    if (!docType) return;
    var all = getStoredState();
    all[docType] = collectFormState(form);
    setStoredState(all);
  }

  function clearCurrentDocInputs(form, docType) {
    Array.from(form.elements).forEach(function (el) {
      if (!el || !el.name || el.disabled) return;
      if (el.name === "doc_type") return;
      var type = (el.type || "").toLowerCase();
      if (type === "button" || type === "submit" || type === "reset" || type === "hidden") return;
      if (type === "checkbox" || type === "radio") {
        el.checked = false;
      } else if (el.tagName === "SELECT") {
        el.selectedIndex = 0;
      } else {
        el.value = "";
      }
    });
    if (docType) {
      var all = getStoredState();
      delete all[docType];
      setStoredState(all);
    }
    form.dispatchEvent(new Event("input", { bubbles: true }));
    form.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function clearAllDocStatesAndCurrent(form, docType) {
    setStoredState({});
    clearCurrentDocInputs(form, "");
    if (docType) {
      saveCurrentDocState(form, docType);
    }
  }

  function getDocFieldValues(docKey, fieldName) {
    var all = getStoredState();
    var doc = all[docKey];
    if (!doc || !Array.isArray(doc[fieldName])) return [];
    return doc[fieldName].map(function (entry) {
      if (!entry) return "";
      if (entry.type === "checkbox" || entry.type === "radio") {
        return entry.checked ? (entry.value || "") : "";
      }
      return entry.value == null ? "" : String(entry.value);
    });
  }

  function formatMaybeInt(num) {
    if (!Number.isFinite(num)) return "";
    if (Math.abs(num - Math.round(num)) < 1e-9) return String(Math.round(num));
    return String(Math.round(num * 1000) / 1000);
  }

  function firstStoredScalar(docKey, fieldName) {
    var values = getDocFieldValues(docKey, fieldName);
    if (!values || values.length === 0) return "";
    return values[0] == null ? "" : String(values[0]);
  }

  function escapeHtml(raw) {
    return String(raw || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function csvCell(raw) {
    var s = String(raw == null ? "" : raw);
    if (s.indexOf('"') !== -1) s = s.replace(/"/g, '""');
    if (/[",\n\r]/.test(s)) return '"' + s + '"';
    return s;
  }

  function normalizeNumericText(raw) {
    return String(raw == null ? "" : raw)
      .replace(/,/g, "")
      .replace(/，/g, "")
      .trim();
  }

  function formatNumericTextWithComma(raw) {
    var s = normalizeNumericText(raw);
    if (!s) return "";
    var sign = "";
    if (s[0] === "-") {
      sign = "-";
      s = s.slice(1);
    }
    var parts = s.split(".");
    var intPart = (parts[0] || "").replace(/^0+(?=\d)/, "");
    if (!intPart) intPart = "0";
    var fracPart = parts.length > 1 ? parts.slice(1).join("").replace(/[^\d]/g, "") : "";
    intPart = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return sign + intPart + (fracPart ? "." + fracPart : "");
  }

  function attachCommaInputBehavior(input) {
    if (!input || input.dataset.commaNumberReady === "1") return;
    input.dataset.commaNumberReady = "1";
    input.dataset.commaNumber = "1";
    input.type = "text";
    if (!input.inputMode) input.inputMode = "decimal";

    input.addEventListener("focus", function () {
      if (input.readOnly) return;
      input.value = normalizeNumericText(input.value);
    });
    input.addEventListener("blur", function () {
      if (!String(input.value || "").trim()) return;
      input.value = formatNumericTextWithComma(input.value);
    });

    if (String(input.value || "").trim()) {
      input.value = formatNumericTextWithComma(input.value);
    }
  }

  function applyCommaInputBehavior(root) {
    if (!root || !root.querySelectorAll) return;
    root.querySelectorAll('input[type="number"], input[data-comma-number="1"]').forEach(function (input) {
      attachCommaInputBehavior(input);
    });
  }

  function parseCsvLine(line) {
    var out = [];
    var cur = "";
    var inQuote = false;
    for (var i = 0; i < line.length; i += 1) {
      var ch = line[i];
      if (inQuote) {
        if (ch === '"') {
          if (i + 1 < line.length && line[i + 1] === '"') {
            cur += '"';
            i += 1;
          } else {
            inQuote = false;
          }
        } else {
          cur += ch;
        }
      } else if (ch === ",") {
        out.push(cur);
        cur = "";
      } else if (ch === '"') {
        inQuote = true;
      } else {
        cur += ch;
      }
    }
    out.push(cur);
    return out;
  }

  function parseCsvState(text) {
    var lines = String(text || "")
      .split(/\r?\n/)
      .filter(function (line) {
        return line.trim() !== "";
      });
    if (lines.length <= 1) return {};
    var state = {};
    for (var i = 1; i < lines.length; i += 1) {
      var cols = parseCsvLine(lines[i]);
      if (cols.length < 2) continue;
      var docType = cols[0] || "";
      var field = cols[1] || "";
      if (!docType || !field) continue;
      var idx = Number(cols[2] || "0");
      if (!Number.isFinite(idx) || idx < 0) idx = 0;
      var type = cols[3] || "text";
      var value = cols[4] == null ? "" : String(cols[4]);
      var checkedRaw = (cols[5] || "").toLowerCase();
      var checked = checkedRaw === "1" || checkedRaw === "true";
      if (!state[docType]) state[docType] = {};
      if (!Array.isArray(state[docType][field])) state[docType][field] = [];
      var entry = { type: type, value: value };
      if (type === "checkbox" || type === "radio") {
        entry.checked = checked;
      }
      state[docType][field][idx] = entry;
    }
    return state;
  }

  function parseHtmlState(text) {
    var parser = new DOMParser();
    var doc = parser.parseFromString(String(text || ""), "text/html");
    var pre = doc.querySelector("pre");
    if (!pre) throw new Error("html_no_pre");
    var jsonText = (pre.textContent || "").trim();
    if (!jsonText) throw new Error("html_no_json");
    return JSON.parse(jsonText);
  }

  function normalizeLoadedState(raw) {
    var source = raw;
    if (raw && typeof raw === "object" && raw.state && typeof raw.state === "object") {
      source = raw.state;
    }
    if (!source || typeof source !== "object") return {};
    var normalized = {};
    Object.keys(source).forEach(function (docKey) {
      var doc = source[docKey];
      if (!doc || typeof doc !== "object") return;
      var outDoc = {};
      Object.keys(doc).forEach(function (field) {
        if (field === "doc_type") return;
        var entries = doc[field];
        if (!Array.isArray(entries)) return;
        outDoc[field] = entries.map(function (entry) {
          if (entry && typeof entry === "object" && !Array.isArray(entry)) {
            var type = entry.type ? String(entry.type) : "text";
            var out = { type: type };
            if (type === "checkbox" || type === "radio") {
              out.checked = !!entry.checked;
              out.value = entry.value == null ? "" : String(entry.value);
            } else {
              out.value = entry.value == null ? "" : String(entry.value);
            }
            return out;
          }
          return { type: "text", value: entry == null ? "" : String(entry) };
        });
      });
      normalized[docKey] = outDoc;
    });
    return normalized;
  }

  function readFileAsText(file) {
    return new Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onload = function () {
        resolve(reader.result == null ? "" : String(reader.result));
      };
      reader.onerror = function () {
        reject(new Error("read_failed"));
      };
      reader.readAsText(file, "UTF-8");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("ed-form");
    if (!form) return;
    initNoteCards(form);
    applyCommaInputBehavior(form);
    var observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (m) {
        m.addedNodes.forEach(function (n) {
          if (!(n instanceof HTMLElement)) return;
          if (n.matches && (n.matches('input[type="number"]') || n.matches('input[data-comma-number="1"]'))) {
            attachCommaInputBehavior(n);
          }
          applyCommaInputBehavior(n);
        });
      });
    });
    observer.observe(form, { childList: true, subtree: true });

    var docType = document.getElementById("ed-doc-type");
    var pageDocType = docType ? docType.value : "";
    if (docType) {
      docType.addEventListener("change", function () {
        saveCurrentDocState(form, pageDocType);
        form.submit();
      });
    }

    var addBtn = document.getElementById("ed-add-row-btn");
    var body = document.getElementById("ed-lines-body");
    function applyDetailSubmitLinkToEstimateRows() {
      var link = document.getElementById("ed-link-detail-submit");
      if (!link || !link.checked || !body) return;
      var detailTotalRaw = firstStoredScalar("detail_submit", "detail_total");
      var detailTotal = toNum(detailTotalRaw);
      if (!detailTotal) return;

      var rows = Array.from(body.querySelectorAll("tr"));
      if (rows.length === 0) {
        body.appendChild(buildRow());
        rows = Array.from(body.querySelectorAll("tr"));
      }

      var target = null;
      for (var i = 0; i < rows.length; i += 1) {
        var descInput = rows[i].querySelector('input[name="description[]"]');
        var desc = (descInput && descInput.value ? String(descInput.value) : "").trim();
        if (desc.indexOf("見積合計額(税抜)") !== -1) {
          target = rows[i];
          break;
        }
      }
      if (!target) target = rows[0];

      var desc = target.querySelector('input[name="description[]"]');
      var qty = target.querySelector('input[name="quantity[]"]');
      var unit = target.querySelector('input[name="unit[]"]');
      var unitPrice = target.querySelector('input[name="unit_price[]"]');
      var discount = target.querySelector('input[name="discount[]"]');
      var lineTotal = target.querySelector('input[name="line_total[]"]');
      if (desc) desc.value = "見積合計額(税抜)";
      if (qty) qty.value = "1";
      if (unit) unit.value = "式";
      if (unitPrice) unitPrice.value = String(Math.round(detailTotal));
      if (discount && !(discount.value || "").trim()) discount.value = "0";
      if (lineTotal) lineTotal.value = String(Math.round(detailTotal));
      calcAll();
    }
    if (addBtn && body) {
      addBtn.addEventListener("click", function () {
        var row = tryAddWithoutPageIncrease(function () {
          var created = buildRow();
          body.appendChild(created);
          return created;
        });
        if (!row) return;
        renumberEstimateRows(body);
        applyCheckedAddonsToRows();
        applyDetailSubmitLinkToEstimateRows();
        calcAll();
      });

      body.addEventListener("click", function (e) {
        var target = e.target;
        if (!(target instanceof HTMLElement)) return;
        if (!target.classList.contains("ed-delete-row")) return;
        var row = target.closest("tr");
        if (!row) return;
        row.remove();
        if (!body.querySelector("tr")) {
          body.appendChild(buildRow());
        }
        renumberEstimateRows(body);
        applyCheckedAddonsToRows();
        applyDetailSubmitLinkToEstimateRows();
        calcAll();
      });
    }

    var addDesc = document.getElementById("ed-check-add-description");
    var addUnit = document.getElementById("ed-check-add-unit");
    if (addDesc) {
      addDesc.addEventListener("change", function () {
        applyCheckedAddonsToRows();
        var link = document.getElementById("ed-link-detail-submit");
        if (link && link.checked) {
          var evt = new Event("change", { bubbles: true });
          link.dispatchEvent(evt);
        }
      });
    }
    if (addUnit) {
      addUnit.addEventListener("change", function () {
        applyCheckedAddonsToRows();
        var link = document.getElementById("ed-link-detail-submit");
        if (link && link.checked) {
          var evt = new Event("change", { bubbles: true });
          link.dispatchEvent(evt);
        }
      });
    }

    var linkDetailSubmit = document.getElementById("ed-link-detail-submit");
    if (linkDetailSubmit) {
      linkDetailSubmit.addEventListener("change", function () {
        applyDetailSubmitLinkToEstimateRows();
      });
    }

    form.addEventListener("input", function () {
      calcAll();
      if (linkDetailSubmit && linkDetailSubmit.checked) {
        applyDetailSubmitLinkToEstimateRows();
      }
    });
    form.addEventListener("change", function () {
      calcAll();
      if (linkDetailSubmit && linkDetailSubmit.checked) {
        applyDetailSubmitLinkToEstimateRows();
      }
    });
    applyCheckedAddonsToRows();
    if (linkDetailSubmit && linkDetailSubmit.checked) {
      applyDetailSubmitLinkToEstimateRows();
    }
    renumberEstimateRows(body);
    calcAll();

    var ddBody = document.getElementById("dd-lines-body");
    var ddAddBtn = document.getElementById("dd-add-row-btn");
    if (ddBody) {
      function calcLinkedSummary(docKey, prefix) {
        var quantities = getDocFieldValues(docKey, prefix + "_quantity[]");
        var units = getDocFieldValues(docKey, prefix + "_unit[]");
        var weights = getDocFieldValues(docKey, prefix + "_weight_kg[]");
        var unitPrices = getDocFieldValues(docKey, prefix + "_unit_price[]");
        var amounts = getDocFieldValues(docKey, prefix + "_amount[]");

        var maxLen = Math.max(quantities.length, units.length, weights.length, unitPrices.length, amounts.length, 0);
        var qtySum = 0;
        var weightSum = 0;
        var amountSum = 0;
        var unitSet = {};

        for (var i = 0; i < maxLen; i += 1) {
          var q = toNum(quantities[i] || "");
          var w = toNum(weights[i] || "");
          var p = toNum(unitPrices[i] || "");
          var aRaw = toNum(amounts[i] || "");
          var a = aRaw || yenRound(q * p);
          var u = (units[i] || "").trim();
          qtySum += q;
          weightSum += w;
          amountSum += a;
          if (u) unitSet[u] = true;
        }

        var uniqueUnits = Object.keys(unitSet);
        var unit = uniqueUnits.length === 1 ? uniqueUnits[0] : "";
        var unitPrice = qtySum > 0 ? amountSum / qtySum : 0;
        return {
          quantity: formatMaybeInt(qtySum),
          unit: unit,
          weight: formatMaybeInt(weightSum),
          unitPrice: qtySum > 0 ? String(Math.round(unitPrice * 100) / 100) : "",
          amount: formatMaybeInt(amountSum)
        };
      }

      function applyMaterialLinkToDetailRows() {
        var link = document.getElementById("dd-link-material");
        if (!link || !link.checked) return;
        var summary = calcLinkedSummary("material_internal", "material");
        var rows = Array.from(ddBody.querySelectorAll("tr"));
        rows.forEach(function (row) {
          var descInput = row.querySelector('input[name="detail_description[]"]');
          if (!descInput) return;
          var desc = (descInput.value || "").trim();
          if (desc.indexOf("材料費") === -1 && desc.indexOf("材料費詳細") === -1) return;
          var q = row.querySelector('input[name="detail_quantity[]"]');
          var u = row.querySelector('input[name="detail_unit[]"]');
          var w = row.querySelector('input[name="detail_weight_kg[]"]');
          var p = row.querySelector('input[name="detail_unit_price[]"]');
          var a = row.querySelector('input[name="detail_amount[]"]');
          if (q) q.value = summary.quantity;
          if (u) u.value = summary.unit; // 混在時は未入力
          if (w) w.value = summary.weight;
          if (p) p.value = summary.unitPrice;
          if (a) a.value = summary.amount;
        });
        calcDetailAll();
      }

      function applyOutsourceLinkToDetailRows() {
        var link = document.getElementById("dd-link-outsource");
        if (!link || !link.checked) return;
        var summary = calcLinkedSummary("outsource_internal", "outsource");
        var rows = Array.from(ddBody.querySelectorAll("tr"));
        rows.forEach(function (row) {
          var descInput = row.querySelector('input[name="detail_description[]"]');
          if (!descInput) return;
          var desc = (descInput.value || "").trim();
          if (desc.indexOf("1次加工費") === -1) return;
          var q = row.querySelector('input[name="detail_quantity[]"]');
          var u = row.querySelector('input[name="detail_unit[]"]');
          var w = row.querySelector('input[name="detail_weight_kg[]"]');
          var p = row.querySelector('input[name="detail_unit_price[]"]');
          var a = row.querySelector('input[name="detail_amount[]"]');
          if (q) q.value = summary.quantity;
          if (u) u.value = summary.unit; // 混在時は未入力
          if (w) w.value = summary.weight;
          if (p) p.value = summary.unitPrice;
          if (a) a.value = summary.amount;
        });
        calcDetailAll();
      }

      function calcFactoryLinkedManDays() {
        var totalMins = getDocFieldValues("factory_labor_internal", "factory_time_total_min[]");
        var qtys = getDocFieldValues("factory_labor_internal", "factory_quantity[]");
        var perMins = getDocFieldValues("factory_labor_internal", "factory_time_per_min[]");
        var maxLen = Math.max(totalMins.length, qtys.length, perMins.length, 0);
        var minutesSum = 0;
        for (var i = 0; i < maxLen; i += 1) {
          var m = toNum(totalMins[i] || "");
          if (!m) {
            m = toNum(qtys[i] || "") * toNum(perMins[i] || "");
          }
          minutesSum += m;
        }
        return (minutesSum / 60) / 8;
      }

      function applyFactoryLinkToDetailRows() {
        var link = document.getElementById("dd-link-factory");
        if (!link || !link.checked) return;
        var manDays = calcFactoryLinkedManDays();
        var quantity = Math.round(manDays * 100) / 100;
        var unitPrice = 30000;
        var amount = Math.round(quantity * unitPrice);
        var rows = Array.from(ddBody.querySelectorAll("tr"));
        rows.forEach(function (row) {
          var descInput = row.querySelector('input[name="detail_description[]"]');
          if (!descInput) return;
          var desc = (descInput.value || "").trim();
          if (desc.indexOf("2次加工費") === -1) return;
          var q = row.querySelector('input[name="detail_quantity[]"]');
          var u = row.querySelector('input[name="detail_unit[]"]');
          var p = row.querySelector('input[name="detail_unit_price[]"]');
          var a = row.querySelector('input[name="detail_amount[]"]');
          if (q) q.value = quantity ? String(quantity) : "";
          if (u) u.value = quantity ? "人工" : "";
          if (p) p.value = quantity ? String(unitPrice) : "";
          if (a) a.value = quantity ? String(amount) : "";
        });
        calcDetailAll();
      }

      function calcSiteLinkedManDays() {
        var totalMins = getDocFieldValues("site_labor_internal", "site_time_total_min[]");
        var qtys = getDocFieldValues("site_labor_internal", "site_quantity[]");
        var perMins = getDocFieldValues("site_labor_internal", "site_time_per_min[]");
        var maxLen = Math.max(totalMins.length, qtys.length, perMins.length, 0);
        var minutesSum = 0;
        for (var i = 0; i < maxLen; i += 1) {
          var m = toNum(totalMins[i] || "");
          if (!m) {
            m = toNum(qtys[i] || "") * toNum(perMins[i] || "");
          }
          minutesSum += m;
        }
        return (minutesSum / 60) / 8;
      }

      function applySiteLinkToDetailRows() {
        var link = document.getElementById("dd-link-site");
        if (!link || !link.checked) return;
        var manDays = calcSiteLinkedManDays();
        var quantity = Math.round(manDays * 100) / 100;
        var unitPrice = 30000;
        var amount = Math.round(quantity * unitPrice);
        var rows = Array.from(ddBody.querySelectorAll("tr"));
        rows.forEach(function (row) {
          var descInput = row.querySelector('input[name="detail_description[]"]');
          if (!descInput) return;
          var desc = (descInput.value || "").trim();
          if (desc.indexOf("現場作業費") === -1) return;
          var q = row.querySelector('input[name="detail_quantity[]"]');
          var u = row.querySelector('input[name="detail_unit[]"]');
          var p = row.querySelector('input[name="detail_unit_price[]"]');
          var a = row.querySelector('input[name="detail_amount[]"]');
          if (q) q.value = quantity ? String(quantity) : "";
          if (u) u.value = quantity ? "人工" : "";
          if (p) p.value = quantity ? String(unitPrice) : "";
          if (a) a.value = quantity ? String(amount) : "";
        });
        calcDetailAll();
      }

      function calcZincLinkedSummary() {
        var quantities = getDocFieldValues("zinc_internal", "zinc_quantity[]");
        var amounts = getDocFieldValues("zinc_internal", "zinc_amount[]");
        var weights = getDocFieldValues("zinc_internal", "zinc_weight_kg[]");
        var unitPrices = getDocFieldValues("zinc_internal", "zinc_unit_price[]");

        var maxLen = Math.max(quantities.length, amounts.length, weights.length, unitPrices.length, 0);
        var qtySum = 0;
        var amountSum = 0;
        for (var i = 0; i < maxLen; i += 1) {
          var q = toNum(quantities[i] || "");
          var a = toNum(amounts[i] || "");
          if (!a) {
            a = yenRound(toNum(weights[i] || "") * toNum(unitPrices[i] || ""));
          }
          qtySum += q;
          amountSum += a;
        }
        var avgUnitPrice = qtySum > 0 ? amountSum / qtySum : 0;
        return {
          quantity: formatMaybeInt(qtySum),
          unitPrice: qtySum > 0 ? String(Math.round(avgUnitPrice * 100) / 100) : "",
          amount: formatMaybeInt(amountSum)
        };
      }

      function applyZincLinkToDetailRows() {
        var link = document.getElementById("dd-link-zinc");
        if (!link || !link.checked) return;
        var summary = calcZincLinkedSummary();
        var rows = Array.from(ddBody.querySelectorAll("tr"));
        rows.forEach(function (row) {
          var descInput = row.querySelector('input[name="detail_description[]"]');
          if (!descInput) return;
          var desc = (descInput.value || "").trim();
          if (desc.indexOf("亜鉛メッキ代") === -1) return;
          var q = row.querySelector('input[name="detail_quantity[]"]');
          var p = row.querySelector('input[name="detail_unit_price[]"]');
          var a = row.querySelector('input[name="detail_amount[]"]');
          if (q) q.value = summary.quantity;
          if (p) p.value = summary.unitPrice;
          if (a) a.value = summary.amount;
        });
        calcDetailAll();
      }

      function applyAllDetailLinks() {
        applyMaterialLinkToDetailRows();
        applyOutsourceLinkToDetailRows();
        applyFactoryLinkToDetailRows();
        applySiteLinkToDetailRows();
        applyZincLinkToDetailRows();
      }

      renumberDetailRows(ddBody);
      calcDetailAll();

      if (ddAddBtn) {
        ddAddBtn.addEventListener("click", function () {
          addDetailRow(ddBody, "", "");
        });
      }

      ddBody.addEventListener("click", function (e) {
        var target = e.target;
        if (!(target instanceof HTMLElement)) return;
        if (!target.classList.contains("dd-delete-row")) return;
        var row = target.closest("tr");
        if (!row) return;
        row.remove();
        if (!ddBody.querySelector("tr")) {
          ddBody.appendChild(buildDetailRow("", ""));
        }
        renumberDetailRows(ddBody);
        calcDetailAll();
      });

      var ddDescSelect = document.getElementById("dd-add-description-select");
      if (ddDescSelect) {
        ddDescSelect.addEventListener("change", function () {
          var value = ddDescSelect.value;
          if (!value) return;
          addDetailRow(ddBody, value, "");
          applyAllDetailLinks();
          ddDescSelect.value = "";
        });
      }

      var ddUnitSelect = document.getElementById("dd-add-unit-select");
      if (ddUnitSelect) {
        ddUnitSelect.addEventListener("change", function () {
          var value = ddUnitSelect.value;
          if (!value) return;
          addDetailRow(ddBody, "", value);
          applyAllDetailLinks();
          ddUnitSelect.value = "";
        });
      }

      document.querySelectorAll(".dd-content-check").forEach(function (cb) {
        cb.addEventListener("change", function () {
          if (!cb.checked) return;
          fillDetailFieldFromTopOrAppend(ddBody, "detail_description[]", cb.value);
          applyAllDetailLinks();
          cb.checked = false;
        });
      });

      document.querySelectorAll(".dd-unit-check").forEach(function (cb) {
        cb.addEventListener("change", function () {
          if (!cb.checked) return;
          fillDetailFieldFromTopOrAppend(ddBody, "detail_unit[]", cb.value);
          applyAllDetailLinks();
          cb.checked = false;
        });
      });

      var ddLinkMaterial = document.getElementById("dd-link-material");
      if (ddLinkMaterial) {
        ddLinkMaterial.addEventListener("change", function () {
          applyAllDetailLinks();
        });
      }
      var ddLinkOutsource = document.getElementById("dd-link-outsource");
      if (ddLinkOutsource) {
        ddLinkOutsource.addEventListener("change", function () {
          applyAllDetailLinks();
        });
      }
      var ddLinkFactory = document.getElementById("dd-link-factory");
      if (ddLinkFactory) {
        ddLinkFactory.addEventListener("change", function () {
          applyAllDetailLinks();
        });
      }
      var ddLinkSite = document.getElementById("dd-link-site");
      if (ddLinkSite) {
        ddLinkSite.addEventListener("change", function () {
          applyAllDetailLinks();
        });
      }
      var ddLinkZinc = document.getElementById("dd-link-zinc");
      if (ddLinkZinc) {
        ddLinkZinc.addEventListener("change", function () {
          applyAllDetailLinks();
        });
      }

      form.addEventListener("input", function () {
        calcDetailAll();
        applyAllDetailLinks();
      });
      form.addEventListener("change", function () {
        calcDetailAll();
        applyAllDetailLinks();
      });
      applyAllDetailLinks();
    }

    var mdBody = document.getElementById("md-lines-body");
    var mdAddBtn = document.getElementById("md-add-row-btn");
    if (mdBody) {
      function calcMaterialRow(row) {
        var weight = toNum(row.querySelector('input[name="material_weight_kg[]"]')?.value);
        var unitPrice = toNum(row.querySelector('input[name="material_unit_price[]"]')?.value);
        var amount = yenRound(weight * unitPrice);
        var amountInput = row.querySelector('input[name="material_amount[]"]');
        if (amountInput) amountInput.value = String(amount);
        return amount;
      }

      function calcMaterialAll() {
        var subtotal = 0;
        Array.from(mdBody.querySelectorAll("tr")).forEach(function (row) {
          subtotal += calcMaterialRow(row);
        });
        var adjustment = toNum(document.getElementById("md-adjustment")?.value);
        var total = subtotal + adjustment;
        var subtotalEl = document.getElementById("md-subtotal");
        var totalEl = document.getElementById("md-total");
        if (subtotalEl) subtotalEl.value = String(subtotal);
        if (totalEl) totalEl.value = String(total);
      }

      function buildMaterialRow(description, unit) {
        var tr = document.createElement("tr");
        tr.innerHTML = [
          "<td></td>",
          '<td><input type="text" name="material_description[]" list="md-description-options" value=""></td>',
          '<td><input type="number" step="0.001" min="0" name="material_quantity[]" value=""></td>',
          '<td><input type="text" name="material_unit[]" list="md-unit-options" value=""></td>',
          '<td><input type="number" step="0.001" min="0" name="material_weight_kg[]" value=""></td>',
          '<td><input type="number" step="1" min="0" name="material_unit_price[]" value=""></td>',
          '<td><input type="number" step="1" min="0" name="material_amount[]" value="0" readonly></td>',
          '<td><button type="button" class="md-delete-row">削除</button></td>'
        ].join("");
        if (description) {
          var d = tr.querySelector('input[name="material_description[]"]');
          if (d) d.value = description;
        }
        if (unit) {
          var u = tr.querySelector('input[name="material_unit[]"]');
          if (u) u.value = unit;
        }
        return tr;
      }

      function appendMaterialRow(description, unit, forceAdd) {
        var added = null;
        var addFn = function () {
          var row = buildMaterialRow(description || "", unit || "");
          mdBody.appendChild(row);
          return row;
        };
        if (forceAdd) {
          added = addFn();
        } else {
          added = tryAddWithoutPageIncrease(addFn);
          if (!added) return null;
        }
        renumberRowsByBody(mdBody);
        calcMaterialAll();
        return added;
      }

      function rebuildMaterialContentOptions() {
        var presets = window.MATERIAL_CONTENT_PRESETS || {};
        var sourceSelect = document.getElementById("md-content-source-select");
        var addSelect = document.getElementById("md-add-description-select");
        var checkboxWrap = document.getElementById("md-content-checkboxes");
        var datalist = document.getElementById("md-description-options");
        if (!sourceSelect || !addSelect || !checkboxWrap || !datalist) return;

        var key = sourceSelect.value;
        var options = presets[key] || [];

        addSelect.innerHTML = '<option value="">選択してください</option>';
        options.forEach(function (opt) {
          var o = document.createElement("option");
          o.value = opt;
          o.textContent = opt;
          addSelect.appendChild(o);
        });

        datalist.innerHTML = "";
        options.forEach(function (opt) {
          var o = document.createElement("option");
          o.value = opt;
          datalist.appendChild(o);
        });

        checkboxWrap.innerHTML = "";
        options.forEach(function (opt) {
          var label = document.createElement("label");
          var input = document.createElement("input");
          input.type = "checkbox";
          input.className = "md-content-check";
          input.value = opt;
          input.addEventListener("change", function () {
            if (!input.checked) return;
            fillFieldFromTopOrAppend(mdBody, "material_description[]", input.value, function (val) {
              appendMaterialRow(val, "");
            });
            renumberRowsByBody(mdBody);
            calcMaterialAll();
            input.checked = false;
          });
          label.appendChild(input);
          label.appendChild(document.createTextNode(opt));
          checkboxWrap.appendChild(label);
        });
      }

      if (mdAddBtn) {
        mdAddBtn.addEventListener("click", function () {
          appendMaterialRow("", "");
        });
      }

      mdBody.addEventListener("click", function (e) {
        var target = e.target;
        if (!(target instanceof HTMLElement)) return;
        if (!target.classList.contains("md-delete-row")) return;
        var row = target.closest("tr");
        if (!row) return;
        row.remove();
        if (!mdBody.querySelector("tr")) {
          mdBody.appendChild(buildMaterialRow("", ""));
        }
        renumberRowsByBody(mdBody);
        calcMaterialAll();
      });

      var mdDescSelect = document.getElementById("md-add-description-select");
      if (mdDescSelect) {
        mdDescSelect.addEventListener("change", function () {
          var value = mdDescSelect.value;
          if (!value) return;
          fillFieldFromTopOrAppend(mdBody, "material_description[]", value, function (val) {
            appendMaterialRow(val, "");
          });
          renumberRowsByBody(mdBody);
          calcMaterialAll();
          mdDescSelect.value = "";
        });
      }

      var mdUnitSelect = document.getElementById("md-add-unit-select");
      if (mdUnitSelect) {
        mdUnitSelect.addEventListener("change", function () {
          var value = mdUnitSelect.value;
          if (!value) return;
          fillFieldFromTopOrAppend(mdBody, "material_unit[]", value, function (val) {
            appendMaterialRow("", val);
          });
          renumberRowsByBody(mdBody);
          calcMaterialAll();
          mdUnitSelect.value = "";
        });
      }

      document.querySelectorAll(".md-unit-check").forEach(function (cb) {
        cb.addEventListener("change", function () {
          if (!cb.checked) return;
          fillFieldFromTopOrAppend(mdBody, "material_unit[]", cb.value, function (val) {
            appendMaterialRow("", val);
          });
          renumberRowsByBody(mdBody);
          calcMaterialAll();
          cb.checked = false;
        });
      });

      var mdSourceSelect = document.getElementById("md-content-source-select");
      if (mdSourceSelect) {
        mdSourceSelect.addEventListener("change", rebuildMaterialContentOptions);
        rebuildMaterialContentOptions();
      }

      renumberRowsByBody(mdBody);
      calcMaterialAll();
      form.addEventListener("input", calcMaterialAll);
      form.addEventListener("change", calcMaterialAll);
    }

    var osBody = document.getElementById("os-lines-body");
    var osAddBtn = document.getElementById("os-add-row-btn");
    if (osBody) {
      function calcOutsourceRow(row) {
        var weight = toNum(row.querySelector('input[name="outsource_weight_kg[]"]')?.value);
        var unitPrice = toNum(row.querySelector('input[name="outsource_unit_price[]"]')?.value);
        var amount = yenRound(weight * unitPrice);
        var amountInput = row.querySelector('input[name="outsource_amount[]"]');
        if (amountInput) amountInput.value = String(amount);
        return amount;
      }

      function calcOutsourceAll() {
        var subtotal = 0;
        Array.from(osBody.querySelectorAll("tr")).forEach(function (row) {
          subtotal += calcOutsourceRow(row);
        });
        var adjustment = toNum(document.getElementById("os-adjustment")?.value);
        var total = subtotal + adjustment;
        var subtotalEl = document.getElementById("os-subtotal");
        var totalEl = document.getElementById("os-total");
        if (subtotalEl) subtotalEl.value = String(subtotal);
        if (totalEl) totalEl.value = String(total);
      }

      function buildOutsourceRow(description, unit) {
        var tr = document.createElement("tr");
        tr.innerHTML = [
          "<td></td>",
          '<td><input type="text" name="outsource_description[]" list="os-description-options" value=""></td>',
          '<td><input type="number" step="0.001" min="0" name="outsource_quantity[]" value=""></td>',
          '<td><input type="text" name="outsource_unit[]" list="os-unit-options" value=""></td>',
          '<td><input type="number" step="0.001" min="0" name="outsource_weight_kg[]" value=""></td>',
          '<td><input type="number" step="1" min="0" name="outsource_unit_price[]" value=""></td>',
          '<td><input type="number" step="1" min="0" name="outsource_amount[]" value="0" readonly></td>',
          '<td><button type="button" class="os-delete-row">削除</button></td>'
        ].join("");
        if (description) {
          var d = tr.querySelector('input[name="outsource_description[]"]');
          if (d) d.value = description;
        }
        if (unit) {
          var u = tr.querySelector('input[name="outsource_unit[]"]');
          if (u) u.value = unit;
        }
        return tr;
      }

      function appendOutsourceRow(description, unit, forceAdd) {
        var added = null;
        var addFn = function () {
          var row = buildOutsourceRow(description || "", unit || "");
          osBody.appendChild(row);
          return row;
        };
        if (forceAdd) {
          added = addFn();
        } else {
          added = tryAddWithoutPageIncrease(addFn);
          if (!added) return null;
        }
        renumberRowsByBody(osBody);
        calcOutsourceAll();
        return added;
      }

      if (osAddBtn) {
        osAddBtn.addEventListener("click", function () {
          appendOutsourceRow("", "");
        });
      }

      osBody.addEventListener("click", function (e) {
        var target = e.target;
        if (!(target instanceof HTMLElement)) return;
        if (!target.classList.contains("os-delete-row")) return;
        var row = target.closest("tr");
        if (!row) return;
        row.remove();
        if (!osBody.querySelector("tr")) {
          osBody.appendChild(buildOutsourceRow("", ""));
        }
        renumberRowsByBody(osBody);
        calcOutsourceAll();
      });

      var osDescSelect = document.getElementById("os-add-description-select");
      if (osDescSelect) {
        osDescSelect.addEventListener("change", function () {
          var value = osDescSelect.value;
          if (!value) return;
          fillFieldFromTopOrAppend(osBody, "outsource_description[]", value, function (val) {
            appendOutsourceRow(val, "");
          });
          renumberRowsByBody(osBody);
          calcOutsourceAll();
          osDescSelect.value = "";
        });
      }

      document.querySelectorAll(".os-content-check").forEach(function (cb) {
        cb.addEventListener("change", function () {
          if (!cb.checked) return;
          fillFieldFromTopOrAppend(osBody, "outsource_description[]", cb.value, function (val) {
            appendOutsourceRow(val, "");
          });
          renumberRowsByBody(osBody);
          calcOutsourceAll();
          cb.checked = false;
        });
      });

      var osUnitSelect = document.getElementById("os-add-unit-select");
      if (osUnitSelect) {
        osUnitSelect.addEventListener("change", function () {
          var value = osUnitSelect.value;
          if (!value) return;
          fillFieldFromTopOrAppend(osBody, "outsource_unit[]", value, function (val) {
            appendOutsourceRow("", val);
          });
          renumberRowsByBody(osBody);
          calcOutsourceAll();
          osUnitSelect.value = "";
        });
      }

      document.querySelectorAll(".os-unit-check").forEach(function (cb) {
        cb.addEventListener("change", function () {
          if (!cb.checked) return;
          fillFieldFromTopOrAppend(osBody, "outsource_unit[]", cb.value, function (val) {
            appendOutsourceRow("", val);
          });
          renumberRowsByBody(osBody);
          calcOutsourceAll();
          cb.checked = false;
        });
      });

      renumberRowsByBody(osBody);
      calcOutsourceAll();
      form.addEventListener("input", calcOutsourceAll);
      form.addEventListener("change", calcOutsourceAll);
    }

    var flBody = document.getElementById("fl-lines-body");
    var flAddBtn = document.getElementById("fl-add-row-btn");
    if (flBody) {
      function calcFactoryRow(row) {
        var qty = toNum(row.querySelector('input[name="factory_quantity[]"]')?.value);
        var timePer = toNum(row.querySelector('input[name="factory_time_per_min[]"]')?.value);
        var totalMin = yenRound(qty * timePer);
        var manDays = Math.round((totalMin / 480) * 100) / 100;
        var totalMinInput = row.querySelector('input[name="factory_time_total_min[]"]');
        var amountInput = row.querySelector('input[name="factory_man_days[]"]');
        if (totalMinInput) totalMinInput.value = String(totalMin);
        if (amountInput) amountInput.value = String(manDays);
        return totalMin;
      }

      function calcFactoryAll() {
        var totalMinutes = 0;
        Array.from(flBody.querySelectorAll("tr")).forEach(function (row) {
          totalMinutes += calcFactoryRow(row);
        });
        var totalHours = totalMinutes / 60;
        var totalManDays = totalHours / 8;
        var m = document.getElementById("fl-total-minutes");
        var h = document.getElementById("fl-total-hours");
        var d = document.getElementById("fl-total-man-days");
        if (m) m.value = String(totalMinutes);
        if (h) h.value = String(Math.round(totalHours * 100) / 100);
        if (d) d.value = String(Math.round(totalManDays * 100) / 100);
      }

      function buildFactoryRow(description, unit) {
        var tr = document.createElement("tr");
        tr.innerHTML = [
          "<td></td>",
          '<td><input type="text" name="factory_description[]" list="fl-description-options" value=""></td>',
          '<td><input type="number" step="0.001" min="0" name="factory_quantity[]" value=""></td>',
          '<td><input type="text" name="factory_unit[]" list="fl-unit-options" value=""></td>',
          '<td><input type="number" step="0.1" min="0" name="factory_time_per_min[]" value=""></td>',
          '<td><input type="number" step="1" min="0" name="factory_time_total_min[]" value="0" readonly></td>',
          '<td><input type="number" step="0.01" min="0" name="factory_man_days[]" value="0" readonly></td>',
          '<td><button type="button" class="fl-delete-row">削除</button></td>'
        ].join("");
        if (description) {
          var d = tr.querySelector('input[name="factory_description[]"]');
          if (d) d.value = description;
        }
        if (unit) {
          var u = tr.querySelector('input[name="factory_unit[]"]');
          if (u) u.value = unit;
        }
        return tr;
      }

      function appendFactoryRow(description, unit, forceAdd) {
        var added = null;
        var addFn = function () {
          var row = buildFactoryRow(description || "", unit || "");
          flBody.appendChild(row);
          return row;
        };
        if (forceAdd) {
          added = addFn();
        } else {
          added = tryAddWithoutPageIncrease(addFn);
          if (!added) return null;
        }
        renumberRowsByBody(flBody);
        calcFactoryAll();
        return added;
      }

      if (flAddBtn) {
        flAddBtn.addEventListener("click", function () {
          appendFactoryRow("", "");
        });
      }

      flBody.addEventListener("click", function (e) {
        var target = e.target;
        if (!(target instanceof HTMLElement)) return;
        if (!target.classList.contains("fl-delete-row")) return;
        var row = target.closest("tr");
        if (!row) return;
        row.remove();
        if (!flBody.querySelector("tr")) {
          flBody.appendChild(buildFactoryRow("", ""));
        }
        renumberRowsByBody(flBody);
        calcFactoryAll();
      });

      var flDescSelect = document.getElementById("fl-add-description-select");
      if (flDescSelect) {
        flDescSelect.addEventListener("change", function () {
          var value = flDescSelect.value;
          if (!value) return;
          fillFieldFromTopOrAppend(flBody, "factory_description[]", value, function (val) {
            appendFactoryRow(val, "");
          });
          renumberRowsByBody(flBody);
          calcFactoryAll();
          flDescSelect.value = "";
        });
      }

      var flUnitSelect = document.getElementById("fl-add-unit-select");
      if (flUnitSelect) {
        flUnitSelect.addEventListener("change", function () {
          var value = flUnitSelect.value;
          if (!value) return;
          fillFieldFromTopOrAppend(flBody, "factory_unit[]", value, function (val) {
            appendFactoryRow("", val);
          });
          renumberRowsByBody(flBody);
          calcFactoryAll();
          flUnitSelect.value = "";
        });
      }

      document.querySelectorAll(".fl-content-check").forEach(function (cb) {
        cb.addEventListener("change", function () {
          if (!cb.checked) return;
          fillFieldFromTopOrAppend(flBody, "factory_description[]", cb.value, function (val) {
            appendFactoryRow(val, "");
          });
          renumberRowsByBody(flBody);
          calcFactoryAll();
          cb.checked = false;
        });
      });

      document.querySelectorAll(".fl-unit-check").forEach(function (cb) {
        cb.addEventListener("change", function () {
          if (!cb.checked) return;
          fillFieldFromTopOrAppend(flBody, "factory_unit[]", cb.value, function (val) {
            appendFactoryRow("", val);
          });
          renumberRowsByBody(flBody);
          calcFactoryAll();
          cb.checked = false;
        });
      });

      renumberRowsByBody(flBody);
      calcFactoryAll();
      form.addEventListener("input", calcFactoryAll);
      form.addEventListener("change", calcFactoryAll);
    }

    var slBody = document.getElementById("sl-lines-body");
    var slAddBtn = document.getElementById("sl-add-row-btn");
    if (slBody) {
      function calcSiteRow(row) {
        var qty = toNum(row.querySelector('input[name="site_quantity[]"]')?.value);
        var timePer = toNum(row.querySelector('input[name="site_time_per_min[]"]')?.value);
        var totalMin = yenRound(qty * timePer);
        var manDays = Math.round((totalMin / 480) * 100) / 100;
        var totalMinInput = row.querySelector('input[name="site_time_total_min[]"]');
        var amountInput = row.querySelector('input[name="site_man_days[]"]');
        if (totalMinInput) totalMinInput.value = String(totalMin);
        if (amountInput) amountInput.value = String(manDays);
        return totalMin;
      }

      function calcSiteAll() {
        var totalMinutes = 0;
        Array.from(slBody.querySelectorAll("tr")).forEach(function (row) {
          totalMinutes += calcSiteRow(row);
        });
        var totalHours = totalMinutes / 60;
        var totalManDays = totalHours / 8;
        var m = document.getElementById("sl-total-minutes");
        var h = document.getElementById("sl-total-hours");
        var d = document.getElementById("sl-total-man-days");
        if (m) m.value = String(totalMinutes);
        if (h) h.value = String(Math.round(totalHours * 100) / 100);
        if (d) d.value = String(Math.round(totalManDays * 100) / 100);
      }

      function buildSiteRow(description, unit) {
        var tr = document.createElement("tr");
        tr.innerHTML = [
          "<td></td>",
          '<td><input type="text" name="site_description[]" list="sl-description-options" value=""></td>',
          '<td><input type="number" step="0.001" min="0" name="site_quantity[]" value=""></td>',
          '<td><input type="text" name="site_unit[]" list="sl-unit-options" value=""></td>',
          '<td><input type="number" step="0.1" min="0" name="site_time_per_min[]" value=""></td>',
          '<td><input type="number" step="1" min="0" name="site_time_total_min[]" value="0" readonly></td>',
          '<td><input type="number" step="0.01" min="0" name="site_man_days[]" value="0" readonly></td>',
          '<td><button type="button" class="sl-delete-row">削除</button></td>'
        ].join("");
        if (description) {
          var d = tr.querySelector('input[name="site_description[]"]');
          if (d) d.value = description;
        }
        if (unit) {
          var u = tr.querySelector('input[name="site_unit[]"]');
          if (u) u.value = unit;
        }
        return tr;
      }

      function appendSiteRow(description, unit, forceAdd) {
        var added = null;
        var addFn = function () {
          var row = buildSiteRow(description || "", unit || "");
          slBody.appendChild(row);
          return row;
        };
        if (forceAdd) {
          added = addFn();
        } else {
          added = tryAddWithoutPageIncrease(addFn);
          if (!added) return null;
        }
        renumberRowsByBody(slBody);
        calcSiteAll();
        return added;
      }

      if (slAddBtn) {
        slAddBtn.addEventListener("click", function () {
          appendSiteRow("", "");
        });
      }

      slBody.addEventListener("click", function (e) {
        var target = e.target;
        if (!(target instanceof HTMLElement)) return;
        if (!target.classList.contains("sl-delete-row")) return;
        var row = target.closest("tr");
        if (!row) return;
        row.remove();
        if (!slBody.querySelector("tr")) {
          slBody.appendChild(buildSiteRow("", ""));
        }
        renumberRowsByBody(slBody);
        calcSiteAll();
      });

      var slDescSelect = document.getElementById("sl-add-description-select");
      if (slDescSelect) {
        slDescSelect.addEventListener("change", function () {
          var value = slDescSelect.value;
          if (!value) return;
          fillFieldFromTopOrAppend(slBody, "site_description[]", value, function (val) {
            appendSiteRow(val, "");
          });
          renumberRowsByBody(slBody);
          calcSiteAll();
          slDescSelect.value = "";
        });
      }

      var slUnitSelect = document.getElementById("sl-add-unit-select");
      if (slUnitSelect) {
        slUnitSelect.addEventListener("change", function () {
          var value = slUnitSelect.value;
          if (!value) return;
          fillFieldFromTopOrAppend(slBody, "site_unit[]", value, function (val) {
            appendSiteRow("", val);
          });
          renumberRowsByBody(slBody);
          calcSiteAll();
          slUnitSelect.value = "";
        });
      }

      document.querySelectorAll(".sl-content-check").forEach(function (cb) {
        cb.addEventListener("change", function () {
          if (!cb.checked) return;
          fillFieldFromTopOrAppend(slBody, "site_description[]", cb.value, function (val) {
            appendSiteRow(val, "");
          });
          renumberRowsByBody(slBody);
          calcSiteAll();
          cb.checked = false;
        });
      });

      document.querySelectorAll(".sl-unit-check").forEach(function (cb) {
        cb.addEventListener("change", function () {
          if (!cb.checked) return;
          fillFieldFromTopOrAppend(slBody, "site_unit[]", cb.value, function (val) {
            appendSiteRow("", val);
          });
          renumberRowsByBody(slBody);
          calcSiteAll();
          cb.checked = false;
        });
      });

      renumberRowsByBody(slBody);
      calcSiteAll();
      form.addEventListener("input", calcSiteAll);
      form.addEventListener("change", calcSiteAll);
    }

    var znBody = document.getElementById("zn-lines-body");
    var znAddBtn = document.getElementById("zn-add-row-btn");
    if (znBody) {
      function calcZincRow(row) {
        var weight = toNum(row.querySelector('input[name="zinc_weight_kg[]"]')?.value);
        var unitPrice = toNum(row.querySelector('input[name="zinc_unit_price[]"]')?.value);
        var amount = yenRound(weight * unitPrice);
        var amountInput = row.querySelector('input[name="zinc_amount[]"]');
        if (amountInput) amountInput.value = String(amount);
        return amount;
      }

      function calcZincAll() {
        var total = 0;
        Array.from(znBody.querySelectorAll("tr")).forEach(function (row) {
          total += calcZincRow(row);
        });
        var t = document.getElementById("zn-total");
        if (t) t.value = String(total);
      }

      function buildZincRow(description, unit) {
        var tr = document.createElement("tr");
        tr.innerHTML = [
          "<td></td>",
          '<td><input type="text" name="zinc_description[]" list="zn-description-options" value=""></td>',
          '<td><input type="number" step="0.001" min="0" name="zinc_quantity[]" value=""></td>',
          '<td><input type="text" name="zinc_unit[]" list="zn-unit-options" value=""></td>',
          '<td><input type="number" step="0.001" min="0" name="zinc_weight_kg[]" value=""></td>',
          '<td><input type="number" step="1" min="0" name="zinc_unit_price[]" value=""></td>',
          '<td><input type="number" step="1" min="0" name="zinc_amount[]" value="0" readonly></td>',
          '<td><button type="button" class="zn-delete-row">削除</button></td>'
        ].join("");
        if (description) {
          var d = tr.querySelector('input[name="zinc_description[]"]');
          if (d) d.value = description;
        }
        if (unit) {
          var u = tr.querySelector('input[name="zinc_unit[]"]');
          if (u) u.value = unit;
        }
        return tr;
      }

      function appendZincRow(description, unit, forceAdd) {
        var added = null;
        var addFn = function () {
          var row = buildZincRow(description || "", unit || "");
          znBody.appendChild(row);
          return row;
        };
        if (forceAdd) {
          added = addFn();
        } else {
          added = tryAddWithoutPageIncrease(addFn);
          if (!added) return null;
        }
        renumberRowsByBody(znBody);
        calcZincAll();
        return added;
      }

      function rebuildZincContentOptions() {
        var presets = window.ZINC_CONTENT_PRESETS || {};
        var sourceSelect = document.getElementById("zn-content-source-select");
        var addSelect = document.getElementById("zn-add-description-select");
        var checkboxWrap = document.getElementById("zn-content-checkboxes");
        var datalist = document.getElementById("zn-description-options");
        if (!sourceSelect || !addSelect || !checkboxWrap || !datalist) return;

        var key = sourceSelect.value;
        var options = presets[key] || [];

        addSelect.innerHTML = '<option value="">選択してください</option>';
        options.forEach(function (opt) {
          var o = document.createElement("option");
          o.value = opt;
          o.textContent = opt;
          addSelect.appendChild(o);
        });

        datalist.innerHTML = "";
        options.forEach(function (opt) {
          var o = document.createElement("option");
          o.value = opt;
          datalist.appendChild(o);
        });

        checkboxWrap.innerHTML = "";
        options.forEach(function (opt) {
          var label = document.createElement("label");
          var input = document.createElement("input");
          input.type = "checkbox";
          input.className = "zn-content-check";
          input.value = opt;
          input.addEventListener("change", function () {
            if (!input.checked) return;
            fillFieldFromTopOrAppend(znBody, "zinc_description[]", input.value, function (val) {
              appendZincRow(val, "");
            });
            renumberRowsByBody(znBody);
            calcZincAll();
            input.checked = false;
          });
          label.appendChild(input);
          label.appendChild(document.createTextNode(opt));
          checkboxWrap.appendChild(label);
        });
      }

      if (znAddBtn) {
        znAddBtn.addEventListener("click", function () {
          appendZincRow("", "");
        });
      }

      znBody.addEventListener("click", function (e) {
        var target = e.target;
        if (!(target instanceof HTMLElement)) return;
        if (!target.classList.contains("zn-delete-row")) return;
        var row = target.closest("tr");
        if (!row) return;
        row.remove();
        if (!znBody.querySelector("tr")) {
          znBody.appendChild(buildZincRow("", ""));
        }
        renumberRowsByBody(znBody);
        calcZincAll();
      });

      var znDescSelect = document.getElementById("zn-add-description-select");
      if (znDescSelect) {
        znDescSelect.addEventListener("change", function () {
          var value = znDescSelect.value;
          if (!value) return;
          fillFieldFromTopOrAppend(znBody, "zinc_description[]", value, function (val) {
            appendZincRow(val, "");
          });
          renumberRowsByBody(znBody);
          calcZincAll();
          znDescSelect.value = "";
        });
      }

      var znUnitSelect = document.getElementById("zn-add-unit-select");
      if (znUnitSelect) {
        znUnitSelect.addEventListener("change", function () {
          var value = znUnitSelect.value;
          if (!value) return;
          fillFieldFromTopOrAppend(znBody, "zinc_unit[]", value, function (val) {
            appendZincRow("", val);
          });
          renumberRowsByBody(znBody);
          calcZincAll();
          znUnitSelect.value = "";
        });
      }

      document.querySelectorAll(".zn-unit-check").forEach(function (cb) {
        cb.addEventListener("change", function () {
          if (!cb.checked) return;
          fillFieldFromTopOrAppend(znBody, "zinc_unit[]", cb.value, function (val) {
            appendZincRow("", val);
          });
          renumberRowsByBody(znBody);
          calcZincAll();
          cb.checked = false;
        });
      });

      var znSourceSelect = document.getElementById("zn-content-source-select");
      if (znSourceSelect) {
        znSourceSelect.addEventListener("change", rebuildZincContentOptions);
        rebuildZincContentOptions();
      }

      renumberRowsByBody(znBody);
      calcZincAll();
      form.addEventListener("input", calcZincAll);
      form.addEventListener("change", calcZincAll);
    }

    if (docType) {
      restoreFormState(form, docType.value);
      form.dispatchEvent(new Event("input", { bubbles: true }));
      form.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function isLinkedMetaDoc(docKey) {
      return docKey === "detail_submit" || docKey === "detail_internal" || docKey === "material_internal" || docKey === "outsource_internal" || docKey === "factory_labor_internal" || docKey === "site_labor_internal" || docKey === "zinc_internal";
    }

    function linkedMetaFieldIds(docKey) {
      if (docKey === "detail_submit" || docKey === "detail_internal") {
        return {
          subject: "dd-subject",
          estimateNo: "dd-estimate-no",
          estimateDate: "dd-estimate-date"
        };
      }
      if (docKey === "material_internal") {
        return {
          subject: "md-subject",
          estimateNo: "md-estimate-no",
          estimateDate: "md-estimate-date"
        };
      }
      if (docKey === "outsource_internal") {
        return {
          subject: "os-subject",
          estimateNo: "os-estimate-no",
          estimateDate: "os-estimate-date"
        };
      }
      if (docKey === "factory_labor_internal") {
        return {
          subject: "fl-subject",
          estimateNo: "fl-estimate-no",
          estimateDate: "fl-estimate-date"
        };
      }
      if (docKey === "site_labor_internal") {
        return {
          subject: "sl-subject",
          estimateNo: "sl-estimate-no",
          estimateDate: "sl-estimate-date"
        };
      }
      if (docKey === "zinc_internal") {
        return {
          subject: "zn-subject",
          estimateNo: "zn-estimate-no",
          estimateDate: "zn-estimate-date"
        };
      }
      return null;
    }

    function syncDetailSubjectFallback() {
      if (!isLinkedMetaDoc(pageDocType)) return;
      var fieldIds = linkedMetaFieldIds(pageDocType);
      if (!fieldIds) return;
      var fallbackInput = document.getElementById("ed-detail-subject-fallback");
      if (!fallbackInput) return;
      var detailSubjectInput = document.getElementById(fieldIds.subject);
      var current = detailSubjectInput ? String(detailSubjectInput.value || "").trim() : "";
      if (current) {
        fallbackInput.value = current;
        return;
      }
      fallbackInput.value = firstStoredScalar("quotation_submit", "subject");
    }

    function syncDetailEstimateNoFallback() {
      if (!isLinkedMetaDoc(pageDocType)) return;
      var fieldIds = linkedMetaFieldIds(pageDocType);
      if (!fieldIds) return;
      var fallbackInput = document.getElementById("ed-detail-estimate-no-fallback");
      if (!fallbackInput) return;
      var detailInput = document.getElementById(fieldIds.estimateNo);
      var current = detailInput ? String(detailInput.value || "").trim() : "";
      if (current) {
        fallbackInput.value = current;
        return;
      }
      fallbackInput.value = firstStoredScalar("quotation_submit", "estimate_no");
    }

    function syncDetailEstimateDateFallback() {
      if (!isLinkedMetaDoc(pageDocType)) return;
      var fieldIds = linkedMetaFieldIds(pageDocType);
      if (!fieldIds) return;
      var fallbackInput = document.getElementById("ed-detail-estimate-date-fallback");
      if (!fallbackInput) return;
      var detailInput = document.getElementById(fieldIds.estimateDate);
      var current = detailInput ? String(detailInput.value || "").trim() : "";
      if (current) {
        fallbackInput.value = current;
        return;
      }
      fallbackInput.value = firstStoredScalar("quotation_submit", "estimate_date");
    }

    if (isLinkedMetaDoc(pageDocType)) {
      var fieldIds = linkedMetaFieldIds(pageDocType);
      if (!fieldIds) return;
      var detailSubjectInput = document.getElementById(fieldIds.subject);
      if (detailSubjectInput && !String(detailSubjectInput.value || "").trim()) {
        detailSubjectInput.value = firstStoredScalar("quotation_submit", "subject");
      }
      var detailEstimateNoInput = document.getElementById(fieldIds.estimateNo);
      if (detailEstimateNoInput && !String(detailEstimateNoInput.value || "").trim()) {
        detailEstimateNoInput.value = firstStoredScalar("quotation_submit", "estimate_no");
      }
      var detailEstimateDateInput = document.getElementById(fieldIds.estimateDate);
      if (detailEstimateDateInput && !String(detailEstimateDateInput.value || "").trim()) {
        detailEstimateDateInput.value = firstStoredScalar("quotation_submit", "estimate_date");
      }
      syncDetailSubjectFallback();
      syncDetailEstimateNoFallback();
      syncDetailEstimateDateFallback();
    }

    var saveTimer = null;
    var scheduleSave = function () {
      if (!pageDocType) return;
      if (saveTimer) clearTimeout(saveTimer);
      saveTimer = setTimeout(function () {
        saveCurrentDocState(form, pageDocType);
      }, 250);
    };
    form.addEventListener("input", scheduleSave);
    form.addEventListener("change", scheduleSave);
    form.addEventListener("submit", function () {
      syncDetailSubjectFallback();
      syncDetailEstimateNoFallback();
      syncDetailEstimateDateFallback();
      if (pageDocType) saveCurrentDocState(form, pageDocType);
    });
    window.addEventListener("beforeunload", function () {
      if (pageDocType) saveCurrentDocState(form, pageDocType);
    });

    var lastNamedSaveHandle = null;
    var lastNamedSaveFormat = "";
    var saveFormatSelect = document.getElementById("ed-save-format");
    var useSubjectFileName = document.getElementById("ed-use-subject-filename");

    function submitSaveAction() {
      var submitter = document.createElement("button");
      submitter.type = "submit";
      submitter.name = "action";
      submitter.value = "save";
      submitter.style.display = "none";
      form.appendChild(submitter);
      submitter.click();
      submitter.remove();
    }

    function submitPrintActionForPdf() {
      var submitter = document.createElement("button");
      submitter.type = "submit";
      submitter.name = "action";
      submitter.value = "print";
      submitter.formTarget = "_blank";
      submitter.style.display = "none";
      form.appendChild(submitter);
      submitter.click();
      submitter.remove();
    }

    function buildSnapshotPayload() {
      if (pageDocType) saveCurrentDocState(form, pageDocType);
      var now = new Date();
      var orientation = document.getElementById("ed-paper-orientation");
      return {
        app: "estimate_document",
        saved_at: now.toISOString(),
        current_doc_type: pageDocType || "",
        paper_orientation: orientation ? orientation.value : "",
        state: getStoredState()
      };
    }

    function buildContentForFormat(format, payload) {
      if (format === "json") {
        return JSON.stringify(payload, null, 2);
      }
      if (format === "txt") {
        return [
          "Estimate Document App - Saved Data",
          "saved_at: " + payload.saved_at,
          "current_doc_type: " + payload.current_doc_type,
          "paper_orientation: " + payload.paper_orientation,
          "",
          JSON.stringify(payload.state, null, 2)
        ].join("\n");
      }
      if (format === "html") {
        return [
          "<!doctype html>",
          '<html lang="ja"><head><meta charset="UTF-8"><title>estimate_document backup</title></head><body>',
          "<h1>Estimate Document App - Saved Data</h1>",
          "<p>saved_at: " + escapeHtml(payload.saved_at) + "</p>",
          "<p>current_doc_type: " + escapeHtml(payload.current_doc_type) + "</p>",
          "<p>paper_orientation: " + escapeHtml(payload.paper_orientation) + "</p>",
          "<pre>" + escapeHtml(JSON.stringify(payload.state, null, 2)) + "</pre>",
          "</body></html>"
        ].join("");
      }
      if (format === "csv") {
        var lines = ["doc_type,field,index,type,value,checked"];
        var state = payload.state || {};
        Object.keys(state).forEach(function (docKey) {
          var doc = state[docKey] || {};
          Object.keys(doc).forEach(function (fieldName) {
            var entries = doc[fieldName];
            if (!Array.isArray(entries)) return;
            entries.forEach(function (entry, idx) {
              lines.push(
                [
                  csvCell(docKey),
                  csvCell(fieldName),
                  csvCell(String(idx)),
                  csvCell(entry && entry.type ? entry.type : ""),
                  csvCell(entry && entry.value != null ? String(entry.value) : ""),
                  csvCell(entry && entry.checked ? "1" : "0")
                ].join(",")
              );
            });
          });
        });
        return lines.join("\n");
      }
      return JSON.stringify(payload, null, 2);
    }

    function fileExtensionByFormat(format) {
      if (format === "pdf") return ".pdf";
      if (format === "csv") return ".csv";
      if (format === "txt") return ".txt";
      if (format === "html") return ".html";
      return ".json";
    }

    function mimeByFormat(format) {
      if (format === "csv") return "text/csv;charset=utf-8";
      if (format === "txt") return "text/plain;charset=utf-8";
      if (format === "html") return "text/html;charset=utf-8";
      return "application/json;charset=utf-8";
    }

    function defaultFileName(format) {
      var now = new Date();
      var pad = function (n) {
        return String(n).padStart(2, "0");
      };
      var ts =
        now.getFullYear() +
        pad(now.getMonth() + 1) +
        pad(now.getDate()) +
        "_" +
        pad(now.getHours()) +
        pad(now.getMinutes()) +
        pad(now.getSeconds());
      return "estimate_document_" + ts + fileExtensionByFormat(format);
    }

    function sanitizeFileBaseName(raw) {
      var s = String(raw || "").trim();
      s = s.replace(/[\\/:*?"<>|]/g, "");
      s = s.replace(/\s+/g, " ");
      s = s.replace(/[. ]+$/g, "");
      return s;
    }

    function buildSuggestedFileName(format) {
      if (useSubjectFileName && useSubjectFileName.checked && pageDocType === "quotation_submit") {
        var subjectInput = document.getElementById("ed-subject");
        var subject = subjectInput ? subjectInput.value : "";
        var base = sanitizeFileBaseName((subject || "") + "見積書");
        if (base) return base + fileExtensionByFormat(format);
      }
      return defaultFileName(format);
    }

    function pickerTypeForFormat(format) {
      if (format === "csv") {
        return { description: "CSV", accept: { "text/csv": [".csv"] } };
      }
      if (format === "txt") {
        return { description: "Text", accept: { "text/plain": [".txt"] } };
      }
      if (format === "html") {
        return { description: "HTML", accept: { "text/html": [".html"] } };
      }
      return { description: "JSON", accept: { "application/json": [".json"] } };
    }

    function downloadFallback(fileName, content, mimeType) {
      var blob = new Blob([content], { type: mimeType });
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(function () {
        URL.revokeObjectURL(url);
      }, 1000);
    }

    async function writeToHandle(handle, content) {
      var writable = await handle.createWritable();
      await writable.write(content);
      await writable.close();
    }

    async function saveAs(format) {
      if (format === "json_pdf") {
        var jsonSaved = await saveAs("json");
        if (!jsonSaved) return false;
        submitPrintActionForPdf();
        lastNamedSaveFormat = "json_pdf";
        return true;
      }

      if (format === "pdf") {
        lastNamedSaveHandle = null;
        lastNamedSaveFormat = "pdf";
        submitPrintActionForPdf();
        return true;
      }

      var payload = buildSnapshotPayload();
      var content = buildContentForFormat(format, payload);
      var mime = mimeByFormat(format);
      var suggestedName = buildSuggestedFileName(format);

      try {
        if (window.showSaveFilePicker) {
          var handle = await window.showSaveFilePicker({
            suggestedName: suggestedName,
            types: [pickerTypeForFormat(format)],
            excludeAcceptAllOption: false
          });
          await writeToHandle(handle, content);
          lastNamedSaveHandle = handle;
          lastNamedSaveFormat = format;
          return true;
        }
      } catch (err) {
        if (err && err.name === "AbortError") return false;
      }

      downloadFallback(suggestedName, content, mime);
      lastNamedSaveHandle = null;
      lastNamedSaveFormat = format;
      return true;
    }

    async function overwriteLastNamedSave() {
      if (!lastNamedSaveFormat) return false;
      if (lastNamedSaveFormat === "json_pdf") {
        if (!lastNamedSaveHandle) return false;
        var payloadJsonPdf = buildSnapshotPayload();
        var contentJsonPdf = buildContentForFormat("json", payloadJsonPdf);
        try {
          await writeToHandle(lastNamedSaveHandle, contentJsonPdf);
          submitPrintActionForPdf();
          return true;
        } catch (_) {
          return false;
        }
      }
      if (lastNamedSaveFormat === "pdf") {
        submitPrintActionForPdf();
        return true;
      }
      if (!lastNamedSaveHandle) return false;
      var payload = buildSnapshotPayload();
      var content = buildContentForFormat(lastNamedSaveFormat, payload);
      try {
        await writeToHandle(lastNamedSaveHandle, content);
        return true;
      } catch (_) {
        return false;
      }
    }

    var saveBtn = document.getElementById("ed-save-btn");
    if (saveBtn) {
      saveBtn.addEventListener("click", function () {
        overwriteLastNamedSave()
          .then(function (overwritten) {
            if (overwritten) return true;
            var format = saveFormatSelect ? saveFormatSelect.value : "pdf";
            return saveAs(format);
          })
          .catch(function () {
            return false;
          })
          .finally(function () {
            submitSaveAction();
          });
      });
    }

    var saveAsBtn = document.getElementById("ed-save-as-btn");
    if (saveAsBtn) {
      saveAsBtn.addEventListener("click", function () {
        var format = saveFormatSelect ? saveFormatSelect.value : "pdf";
        saveAs(format).catch(function () {});
      });
    }

    var loadAllBtn = document.getElementById("ed-load-all-btn");
    if (loadAllBtn) {
      loadAllBtn.addEventListener("click", function () {
        var picker = document.createElement("input");
        picker.type = "file";
        picker.accept = ".json,.csv,.html,.htm";
        picker.addEventListener("change", function () {
          var file = picker.files && picker.files[0];
          if (!file) return;
          readFileAsText(file)
            .then(function (text) {
              var name = (file.name || "").toLowerCase();
              var parsed;
              if (name.endsWith(".csv")) {
                parsed = parseCsvState(text);
              } else if (name.endsWith(".html") || name.endsWith(".htm")) {
                parsed = parseHtmlState(text);
              } else {
                parsed = JSON.parse(text);
              }
              var normalized = normalizeLoadedState(parsed);
              if (!Object.keys(normalized).length) {
                throw new Error("empty_state");
              }
              setStoredState(normalized);
              if (pageDocType) {
                restoreFormState(form, pageDocType);
                form.dispatchEvent(new Event("input", { bubbles: true }));
                form.dispatchEvent(new Event("change", { bubbles: true }));
              }
              alert("全フォームデータを読込しました。");
            })
            .catch(function () {
              alert("読込に失敗しました。JSON/CSV/HTMLファイルを確認してください。");
            });
        });
        picker.click();
      });
    }

    var clearBtn = document.getElementById("ed-clear-btn");
    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        clearCurrentDocInputs(form, pageDocType);
      });
    }

    var clearAllBtn = document.getElementById("ed-clear-all-btn");
    if (clearAllBtn) {
      clearAllBtn.addEventListener("click", function () {
        clearAllDocStatesAndCurrent(form, pageDocType);
      });
    }

    var autoPrint = document.body?.getAttribute("data-auto-print") === "1";
    if (autoPrint) {
      setTimeout(function () {
        window.print();
      }, 250);
    }
  });
})();
