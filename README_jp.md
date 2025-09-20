# Prompt Template Parser

[![Pytest](https://github.com/nobucshirai/prompt-template-parser/actions/workflows/pytest.yml/badge.svg)](https://github.com/nobucshirai/prompt-template-parser/actions/workflows/pytest.yml)

**Prompt Template Parser** は、拡張 Markdown で記述したファイルをインタラクティブな HTML ページへ変換する Python 製ツールです。生成されたページ上で、各種カスタム入力要素を使って動的に構造化されたプロンプトを作成できます。

## 特長

- **拡張 Markdown の変換**  
  拡張 Markdown を、インタラクティブ要素を備えた完結な HTML ドキュメントに変換します。
- **インラインのテキスト入力**  
  二重の角括弧構文（`[[label: default text]]`）で 1 行のテキスト入力欄を生成します。
- **複数行テキスト入力（テキストエリア）**  
  三重の角括弧構文（`[[[label: default text]]]`）で複数行のテキストエリアを生成します。
- **インラインの整数入力**  
  `<<integer_value>>` の構文で小さな数値入力欄を挿入します。  
- **ファイルアップロード入力**  
  `(())` の構文でファイル読み込み要素を挿入します。選択されたファイルは読み込まれ、その内容が最終プロンプトに含まれます。
- **チェックボックス**  
  Markdown のチェックボックス `[ ]`（未チェック）および `[x]`（チェック済み）をインタラクティブなチェックボックスに変換します。
- **逐語（Verbatim）ブロック**  
  三重の波括弧（`{{{ ... }}}`）で囲んだ内容の整形を保ちます。複数行の内容は `<pre><code>` で、1 行のみの場合はインラインの `<code>` でレンダリングされます。
- **インラインコメント**  
  `(* comment *)` を記述すると、HTML には表示されますが生成プロンプトからは除外されるコメントを挿入できます。
- **言語指定**  
  `#lang:ja#` の構文で日本語を指定できます（デフォルトは英語）。
- **動的な CSS・JavaScript の生成**  
  生成される HTML には、使用されているインタラクティブ要素に応じて必要最小限の CSS ルールと JavaScript 関数のみが自動的に含まれます。

## インストール

リポジトリをクローンします：

```bash
git clone https://github.com/nobucshirai/prompt-template-parser.git
cd prompt-template-parser
````

## 使い方

### コマンドラインインターフェイス

拡張 Markdown ファイル（`input.md`）をインタラクティブな HTML ファイルへ変換します：

```bash
python3 prompt_template_parser.py input.md
```

出力ファイル名を指定する場合：

```bash
python3 prompt_template_parser.py input.md -o output.html
```

*出力ファイルを指定しない場合、入力ファイルと同名の拡張子 `.html` のファイルが生成されます。出力先に同名ファイルが存在する場合は、上書き前に確認が求められます。*

### Web インターフェイス

本リポジトリにはクライアントサイド版のパーサーも含まれています。ブラウザで [`prompt_template_parser.html`](prompt_template_parser.html) を開き、拡張構文を含む Markdown ファイルを選択してボタンをクリックすると、インタラクティブな HTML プロンプトを生成・ダウンロードできます。

## サンプル入力

本ツールの機能を示す 2 つのサンプル Markdown を同梱しています。

* **sample\_input\_1.md**
  議事録用のプロンプトジェネレーターを例示します。複数行テキストエリアやファイルアップロードを用いて、構造化された議事録ドキュメントを構築します。対応する HTML（[sample\_input\_1.html](sample_input_1.html)）で生成 UI を確認できます。

* **sample\_input\_2.md**
  CLI ツール向けプロンプトジェネレーターの例です。インラインのテキスト入力、チェックボックス、逐語コードブロックを含みます。生成 UI は [sample\_input\_2.html](sample_input_2.html) に示されています。

## ライセンス

このプロジェクトは MIT ライセンスの下で提供されます。詳細は [LICENSE](LICENSE) を参照してください。
