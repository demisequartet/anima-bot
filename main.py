import requests
import tweepy
import MySQLdb
import datetime
import time
import math
import re
import schedule


# do not push GitHub!


def getInfo():
    url = "https://api.p2pquake.net/v2/jma/quake?min_scale=20&max_scale=20"
    data = requests.get(url).json()

    return data


def tweet(content):
    apikey = ""
    apikeysec = ""
    bearertoken = ""
    accesstoken = ""
    accesstokensecret = ""

    client = tweepy.Client(consumer_key=apikey, consumer_secret=apikeysec,
                           access_token=accesstoken, access_token_secret=accesstokensecret)

    print(client)

    client.create_tweet(text=content)


def connectDB():
  # docker run --rm -d -e MYSQL_ROOT_PASSWORD=my-secret-pw -p 3306:3306 --name mysql mysql:5.7 --character-set-server=utf8mb4 --collation-server=utf8mb4_general_ci

    # データベースへの接続とカーソルの生成
    connection = MySQLdb.connect(
        host='localhost',
        port=3306,
        user='anima',
        passwd='anima',
        db='anima',
        # テーブル内部で日本語を扱うために追加
        charset='utf8'
    )
    cursor = connection.cursor()

    # 保存を実行
    connection.commit()

    # 接続を閉じる
    connection.close()


def getCurrentTime():
    # unix time ミリ秒切り捨て
    ut = math.floor(time.time())
    # print(ut)
    return ut


def strTimeToUnixTime(str):
    str = removeMilliseconds(str)
    # str = str.replace("/", "-").replace(" ", "-").replace(":", "-")
    str = re.sub('[/ :]', '-', str)
    # print(str)
    year, month, day, hour, minute, second = str.split("-")
    dt = datetime.datetime(int(year), int(month), int(
        day), int(hour), int(minute), int(second))

    # print(dt.timestamp())

    return dt.timestamp()


def removeMilliseconds(str):

    index = str.find(".")

    # print(str[:index])
    return str[:index]


def main():
    print(f'現在時刻: {datetime.datetime.now()}')

    # tweet()
    # connectDB()
    datas = getInfo()
    # print(datas)

    # print(datas[0]["created_at"])
    # print(datas[0]["points"])

    now_time = getCurrentTime()

    earthquake_time = strTimeToUnixTime(datas[0]["created_at"])

    diff = now_time - earthquake_time

    print(
        f"now_time: {now_time} earthquake_time: {earthquake_time} diff: {diff}")

    pref = "大阪府"  # 本来は，ユーザーが指定した都道府県がこの値にはいるようにする

    flag = [point["scale"] == 20 and point["pref"]
            == pref for point in datas[0]["points"]]

    if any(flag):
        if diff < 10:
            print(f'{pref}で震度2の場所が存在します')
            # tweet(f'{pref}で震度2の場所が存在します')
        else:
            print(f'{pref}で10秒以内に震度2の地震は起きておりません')


if __name__ == "__main__":
    schedule.every(5).seconds.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
