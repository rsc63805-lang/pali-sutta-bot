import tweepy
import json
import os
import hashlib
from datetime import datetime, timezone

def get_tweet_index(tweets_count):
    now = datetime.now(timezone.utc)
    hour = now.hour
    # 1日4回: 0時, 6時, 12時, 18時 → スロット0-3
    slot = hour // 6
    # 日付ベースのシード
    day_seed = now.strftime("%Y-%m-%d")
    seed = hashlib.md5(f"{day_seed}-{slot}".encode()).hexdigest()
    return int(seed, 16) % tweets_count

def create_tweet_text(tweet_data, lang):
    if lang == "ja":
        text = tweet_data["ja"]
        source = tweet_data["source_ja"]
    else:
        text = tweet_data["en"]
        source = tweet_data["source_en"]

    full_text = f"{text}\n\n— {source}"

    # 280文字制限チェック（日本語は1文字=2としてカウントされる）
    if len(full_text) > 280:
        full_text = full_text[:277] + "..."

    return full_text

def main():
    # 環境変数からAPIキーを取得
    client = tweepy.Client(
        consumer_key=os.environ["API_KEY"],
        consumer_secret=os.environ["API_KEY_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"],
    )

    # ツイートデータ読み込み
    with open("tweets.json", "r", encoding="utf-8") as f:
        tweets = json.load(f)

    index = get_tweet_index(len(tweets))
    tweet_data = tweets[index]

    # 日本語ツイート
    ja_text = create_tweet_text(tweet_data, "ja")
    ja_response = client.create_tweet(text=ja_text)
    print(f"JA tweet posted: {ja_response.data['id']}")

    # 英語ツイートをリプライとしてぶら下げる
    en_text = create_tweet_text(tweet_data, "en")
    en_response = client.create_tweet(
        text=en_text,
        in_reply_to_tweet_id=ja_response.data["id"]
    )
    print(f"EN tweet posted: {en_response.data['id']}")

if __name__ == "__main__":
    main()
