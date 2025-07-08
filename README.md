# wbgt-dashboard
## 2 地点 WBGT 予報ダッシュボード セットアップ

### 準備するもの

- GitHub アカウント（無料）
- ブラウザ

### セットアップ手順

#### 1. ファイル構成

作成したリポジトリに以下のファイルを追加：

```
wbgt-dashboard/
├── .github/
│   └── workflows/
│       └── wbgt-processing.yml       # GitHub Actions設定
├── wbgt_processor.py                 # データ処理スクリプト
├── index.html                        # インデックスページ（自動生成）
├── ishinomaki.html                   # 石巻のダッシュボード（自動生成）
├── tateyama.html                     # 館山のダッシュボード（自動生成）
├── wbgt_data_ishinomaki.json         # 石巻のデータ（自動生成）
├── wbgt_data_tateyama.json           # 館山のデータ（自動生成）
├── wbgt_summary.json                 # 概要データ（自動生成）
├── error_report.json                 # エラーレポート（自動生成）
└── README.md                         # このファイル
```

#### 2. GitHub Pages を有効化

1. リポジトリの「Settings」タブをクリック
2. 左サイドバーの「Pages」をクリック
3. Source を「Deploy from a branch」に設定
4. Branch を「gh-pages」に設定
5. 「Save」をクリック

#### 3. GitHub Actions の権限設定

1. リポジトリの「Settings」タブをクリック
2. 左サイドバーの「Actions」→「General」をクリック
3. 「Workflow permissions」で「Read and write permissions」を選択
4. 「Save」をクリック

#### 4. 初回実行

1. リポジトリの「Actions」タブをクリック
2. 「Update WBGT Dashboard」ワークフローをクリック
3. 「Run workflow」ボタンで手動実行

### 完成！

約 2-3 分後に以下の URL でダッシュボードにアクセスできます：

**インデックスページ（地点選択）**

```
https://ctcn-toshihiro.github.io/wbgt-dashboard/
```
