# Flask Structure Design App
AI Development Rules

このドキュメントは
AIコード生成（Codex / Cursor / ChatGPT 等）に
プロジェクト構造を正しく理解させるためのルールです。

--------------------------------------------------

# PROJECT ROOT

THIS IS THE PROJECT ROOT

C:\Users\kokada\hello\


--------------------------------------------------

# DIRECTORY STRUCTURE

hello
 ├ app
 │   ├ __init__.py
 │   │
 │   ├ blueprints
 │   │   ├ cad
 │   │   │   ├ sections
 │   │   │   ├ plates
 │   │   │   └ beams
 │   │   │
 │   │   ├ documents
 │   │   │
 │   │   └ tools
 │   │
 │   ├ logic
 │   │   └ cad
 │   │
 │   ├ services
 │   │
 │   ├ utils
 │   │   └ blueprint_loader.py
 │   │
 │   ├ templates
 │   │
 │   └ static


--------------------------------------------------

# OLD DIRECTORY (DO NOT USE)

旧開発ディレクトリ

C:\Users\kokada\hello\my_flask_app\

このディレクトリは **使用しません**

すべての開発は

hello/

以下で行います。


--------------------------------------------------

# PROJECT PURPOSE

Flaskを使用した構造設計支援アプリ

主な目的

・CAD用 `.dat` コード生成  
・構造設計作業の自動化  
・将来的なSaaS化  


--------------------------------------------------

# APPLICATION STRUCTURE

多くのツールは次の構造

入力値  
↓  
計算 / ロジック処理  
↓  
テキストコード生成  
↓  
.dat保存


--------------------------------------------------

# FLASK ARCHITECTURE

Flask Blueprintモジュール構造

Blueprintは

routes.py

単位で作成する


--------------------------------------------------

# BLUEPRINT STRUCTURE

例

blueprints
 └ cad
     └ sections
         ├ routes.py
         ├ logic.py
         └ templates


Blueprint登録は

utils/blueprint_loader.py

から **自動登録する**


--------------------------------------------------

# CODE SEPARATION RULE

Flaskルートにロジックを書かない

役割

routes.py

HTTP処理のみ

logic/

計算処理

services/

外部処理  
ファイル生成  
保存処理

utils/

共通関数


--------------------------------------------------

# DEVELOPMENT PHASE

このプロジェクトは段階的に最適化する


Phase1  
Flask開発サーバー

Phase2  
無料クラウド公開テスト  
(Render等)

Phase3  
VPS本番環境

Phase4  
SaaS化


--------------------------------------------------

# CURRENT PHASE

現在のフェーズ

Phase1  
Flask開発サーバー


--------------------------------------------------

# CODE RULES

AIは次のルールを守る


・Flask標準構造を使用  
・Blueprintモジュール構造  
・過度な最適化をしない  
・段階的拡張可能な設計  
・クラウド対応を考慮  


--------------------------------------------------

# BLUEPRINT RULE

新しいツールは

blueprints/

以下に作成する


例

blueprints/cad/beam_tool/


構造

beam_tool
 ├ routes.py
 ├ logic.py
 └ templates


--------------------------------------------------

# FILE GENERATION RULE

CADコード生成は

logic/

または

services/

で行う


Flask routeでは生成処理を書かない


--------------------------------------------------

# AI EDITING RULE

AIがコードを編集する場合

必ず次を守る


編集対象ファイルを明確にする

例

app/__init__.py


新しいファイルは

hello/app/

以下に作成する


--------------------------------------------------

# FUTURE SaaS STRUCTURE

将来的な構造

hello
 ├ app
 ├ config
 ├ migrations
 ├ instance
 ├ tests
 ├ run.py


--------------------------------------------------

# IMPORTANT

AIは次を最優先で理解する


PROJECT ROOT

DIRECTORY TREE

TARGET FILE


この3つが提示されている場合
それを最優先で使用する