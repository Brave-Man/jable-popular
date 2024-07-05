import json
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from tqdm import trange

url = "http://localhost:8191/v1"
headers = {"Content-Type": "application/json"}

item_num = 24
page_num = 1131


def getPageurl(pageNum):
    url = "https://jable.tv/hot/?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=video_viewed&from={}".format(
        str(pageNum)
    )
    return url


def getSelector(itemNum):
    selector = "#list_videos_common_videos_list > div > section > div > div:nth-child({}) > div > div.detail".format(
        itemNum
    )
    return selector


def parseActor(raw: str):
    raw = raw.replace("～", " ").replace("！", " ").replace("x", " ").split(" ")
    return "".join(raw[1:-1]), raw[-1]


def parseLookLike(raw: str):
    raw = raw.replace(" ", "").replace("\t", "").split("\n")
    return raw[1], raw[2]


# 主方法
# 用于爬取特定数据
current_page_soup = ""
current_num = 0


def getData(pageNum, itemNum):
    global current_num
    global current_page_soup
    global data
    if pageNum == current_num:
        data = current_page_soup.select(getSelector(itemNum))
        for item in data:
            href = item.h6.a.get("href")
            title, actor = parseActor(item.h6.a.text)
            fanhao = urlparse(href).path.split("/")[2]
            total_look, total_like = parseLookLike(item.p.text)
            return {
                "fanhao": fanhao,
                "title": title,
                "actor": actor,
                "url": href,
                "likes": total_like,
                "looks": total_look,
            }
    else:
        current_num = pageNum

        requests.adapters.DEFAULT_RETRIES = 20
        s = requests.session()
        s.keep_alive = False

        data = {"cmd": "request.get", "url": getPageurl(pageNum), "maxTimeout": 60000}
        response = requests.post(url, headers=headers, json=data)
        json_data = json.loads(response.text)
        strtext = json_data["solution"]["response"]
        soup = BeautifulSoup(strtext, "lxml")

        current_page_soup = soup
        data = soup.select(getSelector(itemNum))
        for item in data:
            href = item.h6.a.get("href")
            title, actor = parseActor(item.h6.a.text)
            fanhao = urlparse(href).path.split("/")[2]
            total_look, total_like = parseLookLike(item.p.text)
            return {
                "fanhao": fanhao,
                "title": title,
                "actor": actor,
                "url": href,
                "likes": total_like,
                "looks": total_look,
            }


def main():
    with open("data.csv", "w", encoding="utf-8", newline="") as f:
        fieldnames = ["fanhao", "title", "actor", "url", "likes", "looks"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
    for page in trange(1, page_num + 1):
        with open("data.csv", "a+", encoding="utf-8", newline="") as f:
            fieldnames = ["fanhao", "title", "actor", "url", "likes", "looks"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            for item in range(1, item_num + 1):
                data = getData(page, item)
                if data is not None:
                    writer.writerow(data)


main()
