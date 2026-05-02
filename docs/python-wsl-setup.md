# WSL2 + VSCode Python 環境構築ガイド

このプロジェクト（WBGT Dashboard）をWSL2上で開発するための環境構築手順です。

---

## 前提条件

- Windows 11 または Windows 10 (バージョン 2004 以降)
- WSL2 がインストール済み（Ubuntu 推奨）
- VSCode がインストール済み

---

## 1. WSL2 側の Python 確認

WSL ターミナルで以下を実行して Python が入っているか確認します。

```bash
python3 --version
# 例: Python 3.12.3
```

**Python がない場合のインストール:**

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

---

## 2. プロジェクトの依存ライブラリをインストール

このプロジェクトは `requests` ライブラリを使用します。

### 方法A: 仮想環境（推奨）

仮想環境を使うと、プロジェクトごとにライブラリを分離できます。

```bash
# プロジェクトディレクトリに移動
cd ~/project/wbgt-dashboard

# 仮想環境を作成（.venv という名前のフォルダに作られる）
python3 -m venv .venv

# 仮想環境を有効化
source .venv/bin/activate

# プロンプトが (.venv) に変わったことを確認
# ライブラリをインストール
pip install requests

# 無効化するとき
deactivate
```

### 方法B: システム全体にインストール

```bash
pip3 install requests
```

---

## 3. VSCode のインタープリター設定

VSCode がWindowsのPythonではなくWSL側のPythonを使うように設定します。

### 手順

1. VSCode で `Ctrl + Shift + P` を押してコマンドパレットを開く
2. `Python: インタープリターを選択` と入力して選択
3. 表示される一覧から以下のいずれかを選ぶ:
   - 仮想環境を作った場合: `.venv/bin/python` (推奨)
   - システムPythonの場合: `/usr/bin/python3`
4. 表示されない場合は「インタープリターのパスを入力」→ パスを手入力

### よくあるエラーと対処

| エラーメッセージ | 原因 | 対処 |
|---|---|---|
| `Could not resolve interpreter path 'C:\...\python.exe'` | WindowsのPythonパスが残っている | 上記手順でWSL側に切り替える |
| `ModuleNotFoundError: No module named 'requests'` | ライブラリ未インストール | `pip install requests` を実行 |

---

## 4. `.vscode/settings.json` で固定する（任意）

プロジェクトルートに `.vscode/settings.json` を作成すると、チーム全員が同じ設定を使えます。

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
}
```

仮想環境を使わない場合:

```json
{
  "python.defaultInterpreterPath": "/usr/bin/python3"
}
```

---

## 5. スクリプトのローカル実行確認

```bash
# 仮想環境を有効化した状態で
source .venv/bin/activate

# スクリプトを実行
python3 wbgt_processor.py
```

---

## 参考: インストール済みライブラリの確認

```bash
pip list
```

主要ライブラリ:

| ライブラリ | 用途 |
|---|---|
| `requests` | 気象庁APIへのHTTPリクエスト |
