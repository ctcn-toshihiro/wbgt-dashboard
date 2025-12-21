# wbgt-dashboard

## 3 地点 WBGT 予報ダッシュボード セットアップ

### 準備するもの

- GitHub アカウント
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
├── kushiro.html                      # 釧路のダッシュボード（自動生成）
├── ishinomaki.html                   # 石巻のダッシュボード（自動生成）
├── tateyama.html                     # 館山のダッシュボード（自動生成）
├── wbgt_data_kushiro.json            # 釧路のデータ（自動生成）
├── wbgt_data_ishinomaki.json         # 石巻のデータ（自動生成）
├── wbgt_data_tateyama.json           # 館山のデータ（自動生成）
├── wbgt_summary.json                 # 概要データ（自動生成）
├── error_report.json                 # エラーレポート（自動生成）
├── alert_message.txt                 # 警戒レベル通知（自動生成）
└── README.md                         # このファイル
```

#### 2. GitHub Pages を有効化

1. リポジトリの `Settings` タブをクリック
2. 左サイドバーの `Pages` をクリック
3. Source を `Deploy from a branch` に設定
4. Branch を `gh-pages` に設定
5. `Save` をクリック

#### 3. GitHub Actions の権限設定

1. リポジトリの `Settings` タブをクリック
2. 左サイドバーの `Actions` → `General` をクリック
3. `Workflow permissions` で `Read and write permissions` を選択
4. `Save` をクリック

#### 4. 初回実行

1. リポジトリの `Actions` タブをクリック
2. `Update WBGT Dashboard` ワークフローをクリック
3. `Run workflow` ボタンで手動実行

### 完成！

約 2-3 分後に以下の URL でダッシュボードにアクセスできます：

**インデックスページ（地点選択）**

[https://ctcn-toshihiro.github.io/wbgt-dashboard/](https://ctcn-toshihiro.github.io/wbgt-dashboard/)

### 観測地点

このダッシュボードでは以下の 3 地点の WBGT 予報を提供しています：

| 地点名 | 観測地点コード | 所在地 | ダッシュボードURL |
|--------|----------------|--------|-------------------|
| 釧路   | 19432          | 北海道 | [kushiro.html](https://ctcn-toshihiro.github.io/wbgt-dashboard/kushiro.html) |
| 石巻   | 34292          | 宮城県 | [ishinomaki.html](https://ctcn-toshihiro.github.io/wbgt-dashboard/ishinomaki.html) |
| 館山   | 45401          | 千葉県 | [tateyama.html](https://ctcn-toshihiro.github.io/wbgt-dashboard/tateyama.html) |

### 自動更新スケジュール

- **更新頻度**: JST 08:45〜20:45 の間、毎時 45 分に自動更新
- **データソース**: 環境省「熱中症予防情報サイト」（https://www.wbgt.env.go.jp/）

### 生成されるファイル

#### 閲覧用 HTML ファイル
- `index.html` - 地点選択ページ
- `kushiro.html` - 釧路のダッシュボード
- `ishinomaki.html` - 石巻のダッシュボード
- `tateyama.html` - 館山のダッシュボード

#### データファイル（JSON）
- `wbgt_data_kushiro.json` - 釧路の詳細データ
- `wbgt_data_ishinomaki.json` - 石巻の詳細データ
- `wbgt_data_tateyama.json` - 館山の詳細データ
- `wbgt_summary.json` - 全地点の概要データ
- `alert_message.txt` - 警戒レベル予測通知

### WBGT（湿球黒球温度）について

WBGT は熱中症予防を目的とした暑さ指数で、以下のレベルで評価されます：

| WBGT 値 | 危険レベル | 対応 |
|---------|------------|------|
| 31°C～  | 運動中止   | 外出を控え、涼しい場所で過ごす |
| 28-30°C | 厳重警戒   | 激しい運動は避け、こまめに水分補給 |
| 25-27°C | 警戒       | 運動時は定期的に休憩を取る |
| ～24°C  | 注意       | 適度な水分補給を心がける |
