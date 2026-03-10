export function createInitialState() {
  return {
    app: {
      currentPatternId: null,
      canvasSize: 1536,
      tileSize: 512,
    },
    common: {
      seed: 1,
      bg: "#0b0d12",
      fg: "#e7e7ea",
    },
    // パターンごとの状態はここに入る（patternId => state）
    patterns: {},
  };
}

export function clone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

export class History {
  constructor(limit = 50) {
    this.limit = limit;
    this.stack = [];
    this.index = -1;
  }
  push(snapshot) {
    // index 以降を破棄してから追加
    this.stack = this.stack.slice(0, this.index + 1);
    this.stack.push(snapshot);
    if (this.stack.length > this.limit) {
      this.stack.shift();
    } else {
      this.index++;
    }
    // shift した場合 index は末尾に合わせる
    this.index = this.stack.length - 1;
  }
  canUndo() { return this.index > 0; }
  canRedo() { return this.index < this.stack.length - 1; }
  undo() {
    if (!this.canUndo()) return null;
    this.index--;
    return this.stack[this.index];
  }
  redo() {
    if (!this.canRedo()) return null;
    this.index++;
    return this.stack[this.index];
  }
}
