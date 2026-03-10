// ここに「柄モジュール」を登録していく。
// id は一意。loader は dynamic import で遅延ロードできる。

export const PATTERN_REGISTRY = [
  {
    id: "geo.checker",
    name: "Checker（テスト用）",
    category: "幾何",
    description: "プラグイン構造の動作確認用。チェック柄。",
    loader: () => import("./category_geometric/checker.js"),
  },
  // 矢絣
  {
    id: "trad.yagasuri",
    name: "矢絣（Yagasuri）",
    category: "伝統",
    description: "矢羽根の連続パターン（V波噛み合わせ / halfPitch / flip対応）。",
    loader: () => import("./category_traditional/yagasuri/index.js"),
  },
];
