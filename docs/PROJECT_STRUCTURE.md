# Flask Structure Design App
PROJECT STRUCTURE

このドキュメントは
プロジェクトの設計構造を説明します。


--------------------------------------------------

# PROJECT ROOT

C:\Users\kokada\hello\


--------------------------------------------------

# DIRECTORY STRUCTURE

hello
 ├ app
 │   ├ __init__.py
 │
 │   ├ blueprints
 │   │
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
 │
 └ docs


--------------------------------------------------

# APPLICATION TYPE

このアプリは

構造設計支援ツール

です。


主な機能

・CAD用 `.dat` コード生成  
・構造設計作業の自動化  
・設計書類作成  


--------------------------------------------------

# TOOL ARCHITECTURE

各ツールは基本的に次の構造です


入力値
↓
計算処理
↓
テキストコード生成
↓
.dat保存


--------------------------------------------------

# BLUEPRINT ARCHITECTURE

すべてのツールは

Flask Blueprint

として実装する


Blueprintの基本構造


example_tool
 ├ routes.py
 ├ logic.py
 └ templates


--------------------------------------------------

# BLUEPRINT CATEGORY

Blueprintは次のカテゴリに分類される


cad/

CADコード生成ツール


documents/

書類生成ツール


tools/

補助ツール


--------------------------------------------------

# CAD TOOLS

CADツール例


cad
 ├ sections
 │
 ├ plates
 │
 └ beams


用途

断面作図  
プレート作図  
梁部材作図


--------------------------------------------------

# LOGIC LAYER

計算処理は

app/logic/

に配置する


例

logic
 └ cad
     └ beam_calculation.py


--------------------------------------------------

# SERVICE LAYER

サービス層の役割


ファイル生成  
保存処理  
外部処理


例

services
 └ dat_generator.py


--------------------------------------------------

# UTILS LAYER

共通処理


Blueprint自動登録  
共通関数


例

utils
 └ blueprint_loader.py


--------------------------------------------------

# TEMPLATE STRUCTURE

HTMLテンプレートは

templates/

に配置


Blueprint用テンプレートは

Blueprintディレクトリ内でも可


--------------------------------------------------

# NEW TOOL RULE

新しいツールを追加する場合


blueprints/

以下に作成する


例


blueprints/cad/new_beam_tool/


構造


new_beam_tool
 ├ routes.py
 ├ logic.py
 └ templates


--------------------------------------------------

# ROUTE RULE

Flask routeでは

計算処理を書かない


役割


routes.py

HTTP処理


logic.py

計算処理


services/

ファイル処理


--------------------------------------------------

# FUTURE SAAS STRUCTURE

将来の構造


hello
 ├ app
 ├ config
 ├ migrations
 ├ instance
 ├ tests
 ├ run.py


--------------------------------------------------

# IMPORTANT

AIは次の順序で理解する


PROJECT RULES
↓
PROJECT STRUCTURE
↓
TASK