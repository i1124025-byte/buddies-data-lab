import os
import csv
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build

def log_all_stats():
    api_key = os.environ.get('YT_API_KEY')
    if not api_key:
        return
        
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # --- 階層構造のパス作成 ---
    now_dt = datetime.now()
    year_str = now_dt.strftime('%Y')       # '2026'
    month_str = now_dt.strftime('%Y-%m')   # '2026-03'
    
    # 保存フォルダ: logs/2026
    log_dir = os.path.join('logs', year_str)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir) # logsフォルダも年フォルダも一気に作成
        
    # ファイルパス: logs/2026/stats_2026-03.csv
    file_path = os.path.join(log_dir, f'stats_{month_str}.csv')

    # --- 曲名リスト (target_videos) はそのまま ---
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

    # 2. 過去データの読み込み（差分計算用）
    last_views = {}
    if os.path.exists(file_path):
        try:
            df_old = pd.read_csv(file_path)
            if not df_old.empty:
                last_views = df_old.groupby('video_id')['views'].last().to_dict()
        except Exception as e:
            print(f"Read error: {e}")

    # 3. API実行
    video_ids = [v for v in target_videos.values() if v]
    res = youtube.videos().list(part="statistics", id=','.join(video_ids)).execute()
    
    id_to_short = {v: k for k, v in target_videos.items()}
    now_str = now_dt.strftime('%Y-%m-%d %H:%M:%S')
    file_exists = os.path.isfile(file_path)
    
    # 4. 書き込み
    with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['datetime', 'title', 'views', 'diff_views', 'likes', 'comments', 'video_id'])
            
        for item in res['items']:
            vid = item['id']
            short_name = id_to_short.get(vid, "Unknown")
            stats = item['statistics']
            current_views = int(stats.get('viewCount', 0))
            diff = current_views - last_views.get(vid, current_views)
            
            writer.writerow([now_str, short_name, current_views, diff, stats.get('likeCount', 0), stats.get('commentCount', 0), vid])

if __name__ == "__main__":
    log_all_stats()
