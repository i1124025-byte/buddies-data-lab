import os
import csv
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build

def log_all_stats():
    api_key = os.environ.get('YT_API_KEY')
    if not api_key:
        print("Error: YT_API_KEY not found.")
        return
        
    youtube = build('youtube', 'v3', developerKey=api_key)

    # 既存のCSVから前回のデータを読み込む（差分計算用）
    file_path = 'daily_stats_log.csv'
    last_data = {}
    if os.path.exists(file_path):
        try:
            df_old = pd.read_csv(file_path)
            # 各動画の最新の再生数を取得
            for vid in df_old['video_id'].unique():
                last_val = df_old[df_old['video_id'] == vid].iloc[-1]['views']
                last_data[vid] = last_val
        except:
            pass # 初回やエラー時はスキップ
    
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
        "Nobady's fault": "fagRTasDcKo",

    }
    
    video_ids = list(target_videos.values())
    
    # API呼び出し (複数IDをカンマ区切りで一気に取得)
    res = youtube.videos().list(
        part="statistics,snippet",
        id=','.join(video_ids)
    ).execute()

    # 3. IDから「あなたが決めた曲名」を引けるように逆引き辞書を作る
    id_to_short_name = {v: k for k, v in target_videos.items()}

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_path = 'daily_stats_log.csv'
    file_exists = os.path.isfile(file_path)
    
    # 取得できた動画データを回す
    with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # 初回のみヘッダー作成
        if not file_exists:
            writer.writerow(['datetime', 'title', 'views', 'diff_views', 'likes', 'comments', 'video_id'])
            
        for item in res['items']:
            vid = item['id']
            short_name = id_to_short_name.get(vid, "Unknown")
            title = item['snippet']['title']
            views = int(item['statistics'].get('viewCount', 0))
            
            # 差分（時速）の計算
            diff = views - last_data.get(vid, views) 
            
            writer.writerow([
                now, short_name, views, diff,
                item['statistics'].get('likeCount'),
                item['statistics'].get('commentCount'),
                vid
            ])
            print(f"Logged: {title}")

if __name__ == "__main__":
    log_all_stats()
