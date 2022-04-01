from time import sleep
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from bs4 import BeautifulSoup

from header import *
from handler import ErrorHandler
handler = ErrorHandler()

class DoubanMovieAPI:
    def __init__(self, retries=10):
        self._sess = requests.Session()
        self._url = "https://movie.douban.com/"
        self._retries = retries
        header = {
            'Host':'movie.douban.com',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language':'en-US,en;q=0.9',
            'Connection':'keep-alive',
            # 'Accept-Encoding':'gzip, deflate, br',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.4 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.4'
        }
        self._sess.headers.update(header)
    def request(self, params=""):
        for retry_i in range(self._retries):
            sleep(0.1)
            res = self._sess.get(self._url + params, verify=False, proxies=proxies)
            if res.ok: break
            elif res.status_code == 404: 
                handler.notify("Douban API 404", critical=False)
                break
            if retry_i == self._retries - 1: handler.notify("Douban API")
        return res

class DoubanData:
    def __init__(self, db, id):
        self._api = DoubanMovieAPI()
        self._db = db
        self._id = id
    
    def update(self, last_update_ts):
        self._ts = int(time.time())
        self._last_update_ts = last_update_ts
        self._get_data(self._id, 'wish')
        self._get_data(self._id, 'collect')
    
    def _get_data(self, id, category):
        def get_details(subject_id):
            params = "subject/{}".format(subject_id)
            res = self._api.request(params=params)
            if not res.ok: return "", None
            soup = BeautifulSoup(res.content, "html.parser")
            info = soup.find(name='div', attrs={"id": "info"}).text.strip().split('\n')
            info_len = len(info)
            is_series = False
            imdb_id = ""
            for i in range(info_len):
                if "IMDb" in info[i]: imdb_id += info[i].split(": ")[-1]
                if "集数" in info[i]: is_series = True
            if len(imdb_id) == 0: handler.notify(msg="No IMDb ID found", critical=False)
            return imdb_id, is_series
                
        params = "people/{}/{}".format(id, category)
        res = self._api.request(params=params)
        soup = BeautifulSoup(res.content, "html.parser")
        page_name = soup.head.title.text
        wish_num = int(page_name[page_name.rfind('(')+1: -2])

        for start_i in range(0, wish_num, 15):
            print(start_i)
            if start_i != 0:
                params = "people/{}/{}?start={}&sort=time&rating=all&filter=all&mode=grid".format(id, category, start_i)
                res = self._api.request(params=params)
                soup = BeautifulSoup(res.content, "html.parser")

            items = soup.find_all(name='div', attrs={"class": "item"})
            for item in items: 
                info = item.find(name='div', attrs={"class": "info"})
                title = info.find(name='li', attrs={"class": "title"})
                detail_link = title.a['href']
                date = title.find_next(name='span', attrs={"class": "date"})
                rating = 0
                if category == "collect": 
                    rating_str = date.find_previous(name='span')['class'][0]
                    if 'rating' in rating_str: rating = int(rating_str[6])
                    else: rating = -1

                date_ts = int(time.mktime(time.strptime(date.get_text(), "%Y-%m-%d")))
                if date_ts < self._last_update_ts: return

                subject_id = detail_link.split('/')[-2]
                imdb_id, is_series = get_details(subject_id)
                print(detail_link)
                if len(imdb_id) == 0: continue
                self._db.insert(db_tb_name, db_cols, (imdb_id, rating, int(is_series), None, self._ts))
                self._db.update(db_tb_name, 'rating', rating, 'imdb_id', imdb_id, self._ts)





            
    
