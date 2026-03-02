import os
import csv
import json
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build

def log_all_stats():
    # --- 1. 日本時間 (JST) の設定 ---
    # GitHub ActionsのUTC時間をJST(+9時間)に変換
    jst = timezone(timedelta(hours=9))
    now_dt = datetime.now(jst)
    
    year_str = now_dt.strftime('%Y')
    month_str = now_dt.strftime('%Y-%m')
    now_str = now_dt.strftime('%Y-%m-%d %H:%M:%S')

    # --- パス設定 ---
    log_dir = os.path.join('logs', year_str)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    file_path = os.path.join(log_dir, f'stats_{month_str}.csv')
    cache_path = 'last_run_stats.json'

    # --- 2. キャッシュ読み込み ---
    last_views = {}
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            last_views = json.load(f)

    # --- 3. YouTube API 実行 ---
    api_key = os.environ.get('YT_API_KEY')
    youtube = build('youtube', 'v3', developerKey=api_key)
    
        # --- 取得したい楽曲リスト (曲名: 動画ID) ---
    target_videos = {
        "光源": "7pusekGNE-o",
        "The growing up train": "Rk54JNn7Qw4",
        "木枯らしは泣かない": "aQ1iXj4oXfI",
        "Unhappy birthday構文": "hBfDlIN0WtI",
        "Alter ego": "gQ7l_hav-bA",
        "港区パセリ": "aLu4oyQ2zdw",
        "死んだふり": "WNH_ReRMt5k",
        "Make or Break": "nTxTTZ0QLrI",
        "Addiction": "ReuFa_D1Vok",
        "Nightmare症候群": "Grx5AhU14QU",
        "Nothing special": "WdUBD5slEnc",
        "UDAGAWA GENERATION": "qP52sh7PzYA",
        "本質的なこと": "iZhbx2mcmug",
        "僕は僕を好きになれない": "Ktu_LGjGd7A",
        "I want tomorrow to come": "",
        "引きこもる時間はない": "KYvq8-xY1Gg",
        "愛し合いなさい": "MAP3cnAexxM",
        "自業自得": "Rs-Y9MtHsoo",
        "何度　LOVE SONGの歌詞を読み返しただろう": "tltXZSiAAdQ",
        "油を注せ！": "x9a0_2aGeWU",
        "何歳の頃に戻りたいのか？": "7xx66mR_HeE",
        "君がサヨナラ言えたって・・・": "1SQWKDr_GfA",
        "隙間風よ": "5Z4emyH-fME",
        "マモリビト": "I8JZbNTl5rM",
        "承認欲求": "x_BjvhMW9TE",
        "ドローン旋回中": "rNwzfyr07SM",
        "静寂の暴力": "uhbvX4GUrpE",
        "Start over!": "YJRFD1AdaUE",
        "夏の近道": "nV1DHIWSdEo",
        "Cool": "XEKPn3WbksE",
        "桜月": "zKLgrxHDgls",
        "その日まで": "F2lWsUJotmc",
        "摩擦係数": "D8piCp9XMKA",
        "車間距離": "MKXSWXlSOB0",
        "僕のジレンマ": "ZBk4V-uqcXs",
        "五月雨よ": "3boaeE3dwMs",
        "無言の宇宙": "7GZGTse6dUs",
        "Dead end": "FEfJB32wvsk",
        "流れ弾": "drCopBcrxRM",
        "思ったよりも寂しくない": "D0W44Z3D3wo",
        "偶然の答え": "_ZCf_iLMwn0",
        "BAN": "fPZ37t3nvco",
        "Buddies": "yT5S7Cy5cCE",
        "なぜ　恋をして来なかったんだろう？": "S4gEJIyLHlM",
        "Nobady's fault": "fagRTasDcKo"
    }
    
    video_ids = [v for v in target_videos.values() if v]
    res = youtube.videos().list(part="statistics", id=','.join(video_ids)).execute()
    
    id_to_short = {v: k for k, v in target_videos.items()}
    file_exists = os.path.isfile(file_path)
    current_stats_to_cache = {}

    # --- 4. 書き込み ---
    with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['datetime', 'title', 'views', 'diff_views', 'likes', 'comments', 'video_id'])
            
        for item in res['items']:
            vid = item['id']
            short_name = id_to_short.get(vid, "Unknown")
            views = int(item['statistics'].get('viewCount', 0))
            
            # JSONにデータがあれば差分を計算、なければ0
            last_val = last_views.get(vid, views)
            diff = views - last_val
            
            writer.writerow([now_str, short_name, views, diff, item['statistics'].get('likeCount', 0), item['statistics'].get('commentCount', 0), vid])
            current_stats_to_cache[vid] = views

    # キャッシュ更新
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(current_stats_to_cache, f, indent=4)

if __name__ == "__main__":
    log_all_stats()
