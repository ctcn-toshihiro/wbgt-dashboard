#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions 用 WBGT データ処理スクリプト（2地点対応版）
2 時間毎に WBGT データを取得して各地点の HTML ファイルを生成
"""

import requests
import json
import os
from datetime import datetime, timedelta
import traceback

# 観測地点の設定
STATIONS = {
    "abashiri": {
        "station_id": "17341",
        "name": "網走",
        "filename": "abashiri.html",
        "json_filename": "wbgt_data_abashiri.json",
    },
    "kushiro": {
        "station_id": "19432",
        "name": "釧路",
        "filename": "kushiro.html",
        "json_filename": "wbgt_data_kushiro.json",
    },
    "hachinohe": {
        "station_id": "31602",
        "name": "八戸",
        "filename": "hachinohe.html",
        "json_filename": "wbgt_data_hachinohe.json",
    },
    "ishinomaki": {
        "station_id": "34292",
        "name": "石巻",
        "filename": "ishinomaki.html",
        "json_filename": "wbgt_data_ishinomaki.json",
    },
    "tateyama": {
        "station_id": "45401",
        "name": "館山",
        "filename": "tateyama.html",
        "json_filename": "wbgt_data_tateyama.json",
    },
}


def download_wbgt_data(station_id):
    """指定した観測地点のWBGTデータをダウンロードして解析"""
    url = f"https://www.wbgt.env.go.jp/prev15WG/dl/yohou_{station_id}.csv"

    try:
        print(f"  📡 データ取得中: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        csv_content = response.text

        lines = csv_content.strip().split("\n")

        # ヘッダー行（時刻情報）
        header = lines[0].split(",")
        time_stamps = [ts.strip() for ts in header[2:] if ts.strip()]

        # データ行
        data_line = lines[1].split(",")
        actual_station_id = data_line[0].strip()
        update_time = data_line[1].strip()

        # WBGT値を取得
        wbgt_values = []
        for val in data_line[2:]:
            val = val.strip()
            if val:
                try:
                    wbgt_values.append(int(val))
                except ValueError:
                    print(f"    ⚠️ 無効な値をスキップ: {val}")

        # 時刻を解析（JST基準で処理）
        parsed_data = []
        for i, ts in enumerate(time_stamps):
            if i >= len(wbgt_values):
                break

            if len(ts) == 10:  # YYYYMMDDHH
                try:
                    year = int(ts[:4])
                    month = int(ts[4:6])
                    day = int(ts[6:8])
                    hour = int(ts[8:10])

                    # 24時の処理
                    if hour == 24:
                        dt = datetime(year, month, day) + timedelta(days=1)
                    elif hour > 24:
                        extra_days = hour // 24
                        hour = hour % 24
                        dt = datetime(year, month, day, hour) + timedelta(
                            days=extra_days
                        )
                    else:
                        dt = datetime(year, month, day, hour)

                    # JST 時刻として扱う（UTC 変換は行わない）
                    parsed_data.append(
                        {
                            "time": dt.isoformat(),
                            "year": dt.year,
                            "month": dt.month,
                            "day": dt.day,
                            "hour": dt.hour,
                            "minute": dt.minute,
                            "wbgt": wbgt_values[i] / 10.0,  # 表示用に10で割る
                        }
                    )

                except ValueError as e:
                    print(f"    ⚠️ 時刻解析エラー: {ts} - {e}")

        print(f"  ✅ データ取得成功: {len(parsed_data)} 件のデータポイント")

        return {
            "station_id": actual_station_id,
            "update_time": update_time,
            "data": parsed_data,
            "last_updated": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"  ❌ データ取得エラー: {e}")
        return None


def generate_html(wbgt_data, station_name, station_key):
    """HTMLダッシュボードを生成"""
    if not wbgt_data:
        print(f"  ❌ {station_name}: データなしのためHTML生成をスキップ")
        return None

    # 現在の値と統計情報を計算
    current_wbgt = wbgt_data["data"][0]["wbgt"] if wbgt_data["data"] else 0
    max_wbgt = max([d["wbgt"] for d in wbgt_data["data"]]) if wbgt_data["data"] else 0
    min_wbgt = min([d["wbgt"] for d in wbgt_data["data"]]) if wbgt_data["data"] else 0

    # 危険レベルの判定
    if current_wbgt >= 31:
        danger_level = "運動は原則中止"
        danger_color = "#800080"
        danger_message = "特別の場合以外は運動を中止する"
    elif current_wbgt >= 28:
        danger_level = "厳重警戒"
        danger_color = "#FF0000"
        danger_message = "激しい運動や持久走などは避け、10〜20分おきに休憩・水分補給を"
    elif current_wbgt >= 25:
        danger_level = "警戒"
        danger_color = "#FF6600"
        danger_message = "積極的に休憩をとり、適宜水分・塩分を補給する"
    elif current_wbgt >= 21:
        danger_level = "注意"
        danger_color = "#0066CC"
        danger_message = "熱中症の兆候に注意し、運動の合間に水分・塩分を補給する"
    else:
        danger_level = "ほぼ安全"
        danger_color = "#28A745"
        danger_message = "適宜水分・塩分の補給を行う"

    # JavaScriptデータを準備
    chart_data = json.dumps(wbgt_data["data"])

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WBGT 予報ダッシュボード - {station_name}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #f0f0f0;
        }}
        .title {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .subtitle {{
            font-size: 1.2em;
            color: #7f8c8d;
        }}
        .location-info {{
            background: #e8f4f8;
            border: 1px solid #3498db;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .location-name {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2980b9;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            border-left: 5px solid #007bff;
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stat-label {{
            font-size: 1.1em;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .danger-card {{
            background: {danger_color};
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .danger-level {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .danger-message {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
        }}
        .update-info {{
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legend-color {{
            width: 20px;
            height: 4px;
            border-radius: 2px;
        }}
        .auto-update-status {{
            background: #e8f5e8;
            border: 1px solid #4caf50;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .auto-update-status .status-icon {{
            color: #4caf50;
            font-size: 1.2em;
            margin-right: 8px;
        }}
        .navigation {{
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .nav-button {{
            display: inline-block;
            padding: 10px 20px;
            margin: 0 10px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s ease;
        }}
        .nav-button:hover {{
            background: #0056b3;
        }}
        .nav-button.current {{
            background: #28a745;
        }}
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                padding: 20px;
            }}
            .title {{
                font-size: 2em;
            }}
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            .nav-button {{
                display: block;
                margin: 5px 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">WBGT予報ダッシュボード</div>
            <div class="subtitle">観測地点: {wbgt_data['station_id']}</div>
        </div>
        
        <div class="navigation">
            <strong>観測地点切替:</strong><br>
            <a href="abashiri.html" class="nav-button">網走</a>
            <a href="kushiro.html" class="nav-button">釧路</a>
            <a href="hachinohe.html" class="nav-button">八戸</a>
            <a href="ishinomaki.html" class="nav-button">石巻</a>
            <a href="tateyama.html" class="nav-button">館山</a>
        </div>

        <div class="location-info">
            <div class="location-name">{station_name}</div>
            <div>観測地点コード: {wbgt_data['station_id']}</div>
        </div>
        
        <div class="auto-update-status">
            <span class="status-icon">🔄</span>
            <strong>自動更新中:</strong> JST 9:00-21:00 の間、2 時間毎にデータを更新しています
        </div>
        
        <div class="danger-card">
            <div class="danger-level">{danger_level}</div>
            <div class="danger-message">{danger_message}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" style="color: {danger_color};">{current_wbgt:.1f}°C</div>
                <div class="stat-label">現在の WBGT</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #dc3545;">{max_wbgt:.1f}°C</div>
                <div class="stat-label">予報最高値</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #28a745;">{min_wbgt:.1f}°C</div>
                <div class="stat-label">予報最低値</div>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="wbgtChart"></canvas>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background-color: #28A745;"></div>
                <span>ほぼ安全 (21未満)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #0066CC;"></div>
                <span>注意 (21〜25未満)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #FF6600;"></div>
                <span>警戒 (25〜28未満)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #FF0000;"></div>
                <span>厳重警戒 (28〜31未満)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #800080;"></div>
                <span>運動は原則中止 (31以上)</span>
            </div>
        </div>
        
        <div class="update-info">
            <p>データ更新: {wbgt_data['update_time']}</p>
            <p>最終生成: {datetime.fromisoformat(wbgt_data['last_updated']).strftime('%Y年%m月%d日 %H:%M:%S')}</p>
            <p>※ JST 9:00-21:00 の間、2時間毎に自動更新されます</p>
            <p>※環境省「熱中症予防情報サイト」（https://www.wbgt.env.go.jp/）の WBGT データを加工して作成</p>
        </div>
    </div>

    <script>
        const data = {chart_data};
        
        const ctx = document.getElementById('wbgtChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: data.map(d => {{
                    // 直接 JST 時刻として扱う（タイムゾーン変換なし）
                    return d.month + '/' + d.day + ' ' + 
                           d.hour.toString().padStart(2, '0') + ':' + 
                           d.minute.toString().padStart(2, '0');
                }}),
                datasets: [{{
                    label: 'WBGT予報値',
                    data: data.map(d => d.wbgt),
                    borderColor: '#2196F3',
                    backgroundColor: 'transparent',
                    borderWidth: 3,
                    pointBackgroundColor: '#2196F3',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    tension: 0.3
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        title: {{
                            display: true,
                            text: '時刻 (JST)'
                        }}
                    }},
                    y: {{
                        beginAtZero: false,
                        min: Math.min(...data.map(d => d.wbgt)) - 2,
                        max: Math.max(...data.map(d => d.wbgt)) + 2,
                        title: {{
                            display: true,
                            text: 'WBGT (°C)'
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return value + '°C';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        callbacks: {{
                            title: function(context) {{
                                const dataPoint = data[context[0].dataIndex];
                                return dataPoint.year + '年' + 
                                       dataPoint.month + '月' + 
                                       dataPoint.day + '日 ' + 
                                       dataPoint.hour.toString().padStart(2, '0') + ':' + 
                                       dataPoint.minute.toString().padStart(2, '0') + ' (JST)';
                            }},
                            label: function(context) {{
                                return 'WBGT: ' + context.parsed.y.toFixed(1) + '°C';
                            }}
                        }}
                    }}
                }},
                annotation: {{
                    annotations: {{
                        line1: {{
                            type: 'line',
                            yMin: 25,
                            yMax: 25,
                            borderColor: '#FF6600',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            label: {{
                                content: '警戒レベル',
                                enabled: true,
                                position: 'end'
                            }}
                        }},
                        line2: {{
                            type: 'line',
                            yMin: 28,
                            yMax: 28,
                            borderColor: '#FF0000',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            label: {{
                                content: '厳重警戒レベル',
                                enabled: true,
                                position: 'end'
                            }}
                        }},
                        line3: {{
                            type: 'line',
                            yMin: 31,
                            yMax: 31,
                            borderColor: '#800080',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            label: {{
                                content: '運動中止レベル',
                                enabled: true,
                                position: 'end'
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // ページロード時に最新の更新時刻を表示
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('{station_name} WBGT Dashboard loaded');
            console.log('Data points:', data.length);
            console.log('Last update:', '{wbgt_data['last_updated']}');
        }});
    </script>
</body>
</html>"""

    return html_content


def process_station(station_key, station_config):
    """個別の観測地点を処理"""
    station_id = station_config["station_id"]
    station_name = station_config["name"]
    filename = station_config["filename"]
    json_filename = station_config["json_filename"]

    print(f"🏢 {station_name} ({station_id}) の処理を開始")

    # データを取得
    wbgt_data = download_wbgt_data(station_id)

    if wbgt_data:
        print(f"  📊 HTML ファイル生成中: {filename}")
        html_content = generate_html(wbgt_data, station_name, station_key)

        if html_content:
            # HTMLファイルを保存
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html_content)

            # JSONデータも保存（デバッグ用）
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(wbgt_data, f, ensure_ascii=False, indent=2)

            print(f"  ✅ {station_name}: ファイル生成完了")
            print(f"    - 現在WBGT: {wbgt_data['data'][0]['wbgt']:.1f}°C")
            print(f"    - データ更新: {wbgt_data['update_time']}")
            print(f"    - データ件数: {len(wbgt_data['data'])} 件")

            alert_message = generate_alert_message(wbgt_data["data"], station_name)

            return True, alert_message
            # return True
        else:
            print(f"  ❌ {station_name}: HTML生成に失敗")
            return False
    else:
        print(f"  ❌ {station_name}: データ取得に失敗")
        return False


def create_index_html():
    """インデックス HTML ファイルを生成"""
    print("📄 インデックスページを生成中...")

    index_html = (
        """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WBGT 予報ダッシュボード - 地点選択</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
        }
        .header {
            margin-bottom: 40px;
        }
        .title {
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        .subtitle {
            font-size: 1.2em;
            color: #7f8c8d;
            margin-bottom: 20px;
        }
        .description {
            font-size: 1em;
            color: #5a6c7d;
            line-height: 1.6;
            margin-bottom: 40px;
        }
        .stations-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        .station-card {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 30px;
            border-radius: 15px;
            border-left: 5px solid #007bff;
            transition: all 0.3s ease;
            text-decoration: none;
            color: inherit;
            display: block;
        }
        .station-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }
        .station-name {
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .station-id {
            font-size: 0.9em;
            color: #6c757d;
            margin-bottom: 15px;
        }
        .station-status {
            display: inline-block;
            padding: 5px 15px;
            background: #28a745;
            color: white;
            border-radius: 20px;
            font-size: 0.8em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
            font-size: 0.9em;
        }
        .auto-update-info {
            background: #e8f5e8;
            border: 1px solid #4caf50;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .update-icon {
            color: #4caf50;
            font-size: 1.5em;
            margin-bottom: 10px;
        }
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                padding: 30px 20px;
            }
            .title {
                font-size: 2em;
            }
            .stations-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">WBGT 予報ダッシュボード</div>
            <div class="subtitle">熱中症予防情報 - 観測地点選択</div>
            <div class="description">
                環境省の WBGT データを基に、各観測地点の熱中症予防情報を提供します。<br>
                下記から確認したい地点を選択してください。
            </div>
        </div>
        
        <div class="auto-update-info">
            <div class="update-icon">🔄</div>
            <strong>自動更新システム</strong><br>
            JST 9:00-21:00 の間、2時間毎にデータを自動更新しています
        </div>
        
        <div class="stations-grid">
            <a href="abashiri.html" class="station-card">
                <div class="station-name">網走</div>
                <div class="station-id">観測地点コード: 17341</div>
                <div class="station-status">運用中</div>
            </a>
            <a href="kushiro.html" class="station-card">
                <div class="station-name">釧路</div>
                <div class="station-id">観測地点コード: 19432</div>
                <div class="station-status">運用中</div>
            </a>
            <a href="hachinohe.html" class="station-card">
                <div class="station-name">八戸</div>
                <div class="station-id">観測地点コード: 31602</div>
                <div class="station-status">運用中</div>
            </a>
            <a href="ishinomaki.html" class="station-card">
                <div class="station-name">石巻</div>
                <div class="station-id">観測地点コード: 34292</div>
                <div class="station-status">運用中</div>
            </a>
            <a href="tateyama.html" class="station-card">
                <div class="station-name">館山</div>
                <div class="station-id">観測地点コード: 45401</div>
                <div class="station-status">運用中</div>
            </a>
        </div>
        
        <div class="footer">
            <p>※このサイトは環境省「熱中症予防情報サイト」のデータを加工して作成しています</p>
            <p>※WBGT（湿球黒球温度）: 熱中症予防を目的とした暑さ指数</p>
            <p>最終更新: """
        + datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        + """</p>
        </div>
    </div>
</body>
</html>"""
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print("  ✅ インデックスページ生成完了: index.html")


def create_summary_json():
    """全地点の概要データを含む JSON ファイルを生成"""
    print("📊 概要データファイルを生成中...")

    summary_data = {
        "generated_at": datetime.now().isoformat(),
        "stations": {},
        "total_stations": len(STATIONS),
        "update_schedule": "JST 9:00-21:00, every 2 hours",
    }

    for station_key, station_config in STATIONS.items():
        json_filename = station_config["json_filename"]

        if os.path.exists(json_filename):
            try:
                with open(json_filename, "r", encoding="utf-8") as f:
                    station_data = json.load(f)

                if station_data and "data" in station_data and station_data["data"]:
                    current_wbgt = station_data["data"][0]["wbgt"]
                    max_wbgt = max([d["wbgt"] for d in station_data["data"]])
                    min_wbgt = min([d["wbgt"] for d in station_data["data"]])

                    # 危険レベルの判定
                    if current_wbgt >= 31:
                        danger_level = "運動は原則中止"
                    elif current_wbgt >= 28:
                        danger_level = "厳重警戒"
                    elif current_wbgt >= 25:
                        danger_level = "警戒"
                    elif current_wbgt >= 21:
                        danger_level = "注意"
                    else:
                        danger_level = "ほぼ安全"

                    summary_data["stations"][station_key] = {
                        "name": station_config["name"],
                        "station_id": station_data["station_id"],
                        "current_wbgt": current_wbgt,
                        "max_wbgt": max_wbgt,
                        "min_wbgt": min_wbgt,
                        "danger_level": danger_level,
                        "update_time": station_data["update_time"],
                        "data_points": len(station_data["data"]),
                        "html_file": station_config["filename"],
                    }
                else:
                    summary_data["stations"][station_key] = {
                        "name": station_config["name"],
                        "station_id": station_config["station_id"],
                        "error": "No data available",
                    }
            except Exception as e:
                print(f"    ⚠️ {station_key} データ読み込みエラー: {e}")
                summary_data["stations"][station_key] = {
                    "name": station_config["name"],
                    "station_id": station_config["station_id"],
                    "error": str(e),
                }
        else:
            summary_data["stations"][station_key] = {
                "name": station_config["name"],
                "station_id": station_config["station_id"],
                "error": "Data file not found",
            }

    with open("wbgt_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)

    print("  ✅ 概要データファイル生成完了: wbgt_summary.json")
    return summary_data


# def check_update_time():
#    """更新時刻をチェック（JST 9:00-21:00 の間のみ実行）"""
#    now = datetime.now()
#    hour = now.hour
#
#    print(f"⏰ 現在時刻: {now.strftime('%Y年%m月%d日 %H:%M:%S')} JST")
#
#    if 9 <= hour <= 21:
#        print("  ✅ 更新時間内です（JST 9:00-21:00）")
#        return True
#    else:
#        print("  ⏸️ 更新時間外です（JST 9:00-21:00 以外）")
#        print("  ℹ️ 夜間の更新はスキップされます")
#        return False
def check_update_time():
    return True  # ← テスト用に常にTrueを返す


def generate_alert_message(wbgt_data, station_name):
    from datetime import datetime, timedelta

    now = datetime.now()
    target_time = (now + timedelta(hours=2)).replace(minute=0, second=0, microsecond=0)
    threshold = 20.0

    # 2時間後のインデックスを探す
    start_index = next(
        (
            i
            for i, d in enumerate(wbgt_data)
            if datetime.fromisoformat(d["time"]) == target_time
        ),
        None,
    )
    if start_index is None or wbgt_data[start_index]["wbgt"] < threshold:
        return ""

    # 警戒レベル継続時間を調べる
    duration = 0
    recovery_time = None
    for i in range(start_index, len(wbgt_data)):
        if wbgt_data[i]["wbgt"] >= threshold:
            duration += 1
        else:
            recovery_time = wbgt_data[i]["time"]
            recovery_value = wbgt_data[i]["wbgt"]
            break

    start_time = wbgt_data[start_index]["time"][-8:-3]
    end_time = recovery_time[-8:-3] if recovery_time else "未定"
    hours = duration * 3

    msg = f"📍 {station_name}\n"
    msg += f"🔺 2時間後（{start_time}）にWBGTが{wbgt_data[start_index]['wbgt']:.1f}℃に達する見込みです。\n"
    msg += f"🕒 警戒レベルは約{hours}時間（{start_time}〜{end_time}）続く見込みです。\n"
    if recovery_time:
        msg += f"🔻 {end_time}にはWBGTが{recovery_value:.1f}℃に下がり、通常レベルに戻る見込みです。\n"
    return msg


def main():
    """メイン処理"""
    print("🚀 WBGT データ処理スクリプト開始")
    print("=" * 50)

    try:
        # 更新時刻チェック
        if not check_update_time():
            print("⏹️ 更新時間外のため処理を終了します")
            return

        print(f"📍 処理対象地点: {len(STATIONS)} 地点")

        # 各地点の処理
        alert_messages = []
        success_count = 0
        # for station_key, station_config in STATIONS.items():
        #    print(f"\n{'='*30}")
        #    if process_station(station_key, station_config):
        #        success_count += 1
        for station_key, station_config in STATIONS.items():
            print(f"\n{'='*30}")
            success, alert_message = process_station(station_key, station_config)
            if success:
                success_count += 1
                if alert_message:
                    alert_messages.append(alert_message)

        print(f"\n{'='*50}")
        print(f"📊 処理結果: {success_count}/{len(STATIONS)} 地点成功")

        # インデックスページ生成
        print(f"\n{'='*30}")
        create_index_html()

        # 概要データ生成
        print(f"\n{'='*30}")
        summary_data = create_summary_json()

        # 通知メッセージ出力
        if alert_messages:
            print(f"\n{'='*30}")
            print("📣 警戒レベル予測通知を生成中...")

            with open("alert_message.txt", "w", encoding="utf-8") as f:
                f.write(
                    f"🌡️ WBGT予測通知（{datetime.now().strftime('%Y-%m-%d %H:%M')} 時点）\n\n"
                )
                f.write("\n".join(alert_messages))
                f.write(
                    "\n📊 ダッシュボード：https://ctcn-toshihiro.github.io/wbgt-dashboard/\n"
                )

            print("✅ 通知メッセージを alert_message.txt に出力しました")

        # 処理結果の表示
        print(f"\n{'='*50}")
        print("📋 処理完了サマリー:")
        print(f"  - 成功地点数: {success_count}/{len(STATIONS)}")
        print(f"  - 生成ファイル:")
        print(f"    • index.html (インデックスページ)")
        print(f"    • wbgt_summary.json (概要データ)")

        for station_key, station_config in STATIONS.items():
            if (
                station_key in summary_data["stations"]
                and "error" not in summary_data["stations"][station_key]
            ):
                station_summary = summary_data["stations"][station_key]
                print(f"    • {station_config['filename']} ({station_config['name']})")
                print(f"      - 現在WBGT: {station_summary['current_wbgt']:.1f}°C")
                print(f"      - 危険レベル: {station_summary['danger_level']}")
                print(f"      - データ件数: {station_summary['data_points']} 件")

        print(f"\n🎉 全ての処理が正常に完了しました！")

        # GitHub Actions での環境変数設定
        if os.getenv("GITHUB_ACTIONS") == "true":
            print(f"\n🔧 GitHub Actions 環境変数を設定中...")

            # 成功率を環境変数に設定
            success_rate = (success_count / len(STATIONS)) * 100
            print(f"WBGT_SUCCESS_RATE={success_rate:.1f}")

            # 最新の WBGT 値を環境変数に設定
            for station_key in STATIONS:
                if (
                    station_key in summary_data["stations"]
                    and "current_wbgt" in summary_data["stations"][station_key]
                ):
                    wbgt_value = summary_data["stations"][station_key]["current_wbgt"]
                    danger_level = summary_data["stations"][station_key]["danger_level"]
                    print(f"WBGT_{station_key.upper()}={wbgt_value:.1f}")
                    print(f"DANGER_{station_key.upper()}={danger_level}")

    except Exception as e:
        print(f"\n❌ 処理中にエラーが発生しました:")
        print(f"エラー内容: {str(e)}")
        print(f"スタックトレース:")
        traceback.print_exc()

        # GitHub Actions でのエラー処理
        if os.getenv("GITHUB_ACTIONS") == "true":
            print(f"::error::WBGT data processing failed: {str(e)}")
            # 処理は続行（部分的な成功の可能性があるため）

        # 最低限のエラー情報を含むファイルを生成
        try:
            error_data = {
                "error": True,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat(),
                "partial_success": [],
            }

            # 部分的に成功したファイルをチェック
            for station_key, station_config in STATIONS.items():
                if os.path.exists(station_config["filename"]):
                    error_data["partial_success"].append(station_key)

            with open("error_report.json", "w", encoding="utf-8") as f:
                json.dump(error_data, f, ensure_ascii=False, indent=2)

            print("  📄 エラーレポートを生成しました: error_report.json")

        except Exception as report_error:
            print(f"  ⚠️ エラーレポート生成も失敗: {report_error}")


def test_single_station(station_key):
    """単一地点のテスト用関数"""
    if station_key not in STATIONS:
        print(f"❌ 無効な地点キー: {station_key}")
        print(f"利用可能な地点: {list(STATIONS.keys())}")
        return

    print(f"🧪 テストモード: {station_key} のみ処理")
    station_config = STATIONS[station_key]

    if process_station(station_key, station_config):
        print(f"✅ {station_key} のテストが成功しました")
    else:
        print(f"❌ {station_key} のテストが失敗しました")


if __name__ == "__main__":
    import sys

    # コマンドライン引数でテストモードを指定可能
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # 全地点のテスト（時間制限なし）
            print("🧪 テストモード: 全地点処理（時間制限なし）")
            for station_key, station_config in STATIONS.items():
                print(f"\n{'='*30}")
                process_station(station_key, station_config)
        elif sys.argv[1].startswith("--test-"):
            # 特定地点のテスト
            station_key = sys.argv[1][7:]  # "--test-" を除去
            test_single_station(station_key)
        elif sys.argv[1] == "--help":
            print("WBGT データ処理スクリプト")
            print("使用方法:")
            print("  python wbgt_processor.py              # 通常実行")
            print("  python wbgt_processor.py --test       # 全地点テスト")
            print("  python wbgt_processor.py --test-ishinomaki # 大阪のみテスト")
            print("  python wbgt_processor.py --test-tateyama # 東京のみテスト")
            print("  python wbgt_processor.py --help       # ヘルプ表示")
        else:
            print(f"❌ 無効なオプション: {sys.argv[1]}")
            print("--help でヘルプを表示")
    else:
        # 通常実行
        main()
