import requests  # 导入requests包
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from time import sleep
import csv
import cfscrape
from tqdm import trange

item_num = 24
page_num = 124

proxies = {
    "https": "http://127.0.0.1:20171"
}

scraper = cfscrape.create_scraper()

# 获取特定页码的url,按照最近更新排序


def getPageurl(pageNum):
    url = "https://jable.tv/categories/chinese-subtitle/?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from={}".format(
        str(pageNum))
    return url

# 获取特定item的选择器


def getSelector(itemNum):
    selector = "#list_videos_common_videos_list > div > section > div > div:nth-child({}) > div > div.detail".format(
        itemNum)
    return selector


def parseActor(raw: str):
    raw = raw.replace('～',' ').replace('！',' ').replace('x',' ').split(' ')
    return "".join(raw[1:-1]), raw[-1]


def parseLookLike(raw: str):
    raw = raw.replace(" ", "").split('\n')
    return raw[1], raw[2]


# 主方法
# 用于爬取特定数据
current_page_soup = ""
current_num = 0


def getData(pageNum, itemNum):
    global current_num
    global current_page_soup
    if pageNum == current_num:
        data = current_page_soup.select(getSelector(itemNum))
        for item in data:
            href = item.h6.a.get("href")
            title, actor = parseActor(item.h6.a.text)
            fanhao = urlparse(href).path.split("/")[2]
            total_look, total_like = parseLookLike(item.p.text)
            return {
                'fanhao': fanhao,
                'title': title,
                'actor': actor,
                'url': href,
                'likes': total_like,
                'looks': total_look
            }
    else:
        current_num = pageNum

        requests.adapters.DEFAULT_RETRIES = 20
        s = requests.session()
        s.keep_alive = False
        strtext = scraper.get(getPageurl(pageNum), proxies=proxies).content
        # strhtml = requests.get(getPageurl(pageNum),proxies=proxies)
        # soup=BeautifulSoup(strhtml.text,'lxml')
        soup = BeautifulSoup(strtext, 'lxml')

        current_page_soup = soup
        data = soup.select(getSelector(itemNum))
        for item in data:
            href = item.h6.a.get("href")
            title, actor = parseActor(item.h6.a.text)
            fanhao = urlparse(href).path.split("/")[2]
            total_look, total_like = parseLookLike(item.p.text)
            return {
                'fanhao': fanhao,
                'title': title,
                'actor': actor,
                'url': href,
                'likes': total_like,
                'looks': total_look
            }


def main():
    with open('data.csv', "w", encoding='utf-8', newline="") as f:
        fieldnames = ['fanhao', 'title', 'actor', 'url', 'likes', 'looks']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
    for page in trange(1, page_num+1):
        with open('data.csv', "a+", encoding='utf-8', newline="") as f:
            fieldnames = ['fanhao', 'title', 'actor', 'url', 'likes', 'looks']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            for item in range(1, item_num+1):
                data = getData(page, item)
                if data is not None:
                    writer.writerow(data)


main()
