from time import sleep
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from bs4 import BeautifulSoup

from header import *
from handler import ErrorHandler
import random
handler = ErrorHandler()

class DoubanMovieAPI:
    def get_proxy():
        session_id = random.random()
        proxy_settings = settings['proxy_settings']
        super_proxy_url = ('http://%s-session-%s:%s@zproxy.lum-superproxy.io:%d' %
            (proxy_settings['username'], session_id, proxy_settings['passwd'], proxy_settings['port']))
        return {"http": super_proxy_url,
                "https": super_proxy_url}

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
            res = self._sess.get(self._url + params, verify=False, proxies=DoubanMovieAPI.get_proxy())
            if res.ok: break
            elif res.status_code == 404: 
                handler.notify("Douban API 404", critical=False)
                break
            if retry_i == self._retries - 1: handler.notify("Douban API")
        return res

class DoubanData:
    def __init__(self, db, ids):
        self._api = DoubanMovieAPI()
        self._db = db
        self._ids = ids
    
    def update(self, last_update_ts):
        self._ts = int(time.time())
        self._last_update_ts = last_update_ts
        for id in self._ids:
            self._get_data(id, 'wish')
            self._get_data(id, 'collect')
    
    def _get_data(self, id, category):
        def get_details(subject_id):
            params = "subject/{}".format(subject_id)
            res = self._api.request(params=params)
            if not res.ok: return "", None, None, None

            soup = BeautifulSoup(res.content, "html.parser")
            info = soup.find(name='div', attrs={"id": "info"})
            info_texts = info.text.strip().split('\n')
            is_series = False
            season_num = None
            serie_imdb_id = None
            imdb_id = ""
            for info_text in info_texts:
                if "IMDb" in info_text: imdb_id += info_text.split(": ")[-1]
                if "集数" in info_text: is_series = True
                if "季数" in info_text: 
                    try:
                        season_info = info.find(name="select", attrs={"id": "season"}).find_all(name="option")
                    except AttributeError: handler.notify("Season INFO.", critical=False)
                    else: 
                        for season in season_info:
                            if season.get("selected", None) is not None: season_num = int(season.text)
                        if season_num != 1: 
                            serie_douban_id = season_info[0]["value"]
                            db_data = self._db.query(db_tb_name, "douban_id={}".format(serie_douban_id))
                            if len(db_data) == 1: serie_imdb_id = db_data[0][0]
                            else: serie_imdb_id = get_details(serie_douban_id)[0]
                                            
            if len(imdb_id) == 0: handler.notify(msg="No IMDb ID found", critical=False)
            if is_series and serie_imdb_id is None: serie_imdb_id = imdb_id
            if is_series and season_num is None: season_num = 1
            return imdb_id, is_series, season_num, serie_imdb_id

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
                print(detail_link)
                imdb_id, is_series, season_num, serie_imdb_id = get_details(subject_id)
                if len(imdb_id) == 0: continue
                if is_series:
                    assert(season_num is not None and serie_imdb_id is not None)
                    if season_num == 1: assert(imdb_id == serie_imdb_id)
                    else: assert(imdb_id != serie_imdb_id)
                self._db.insert(db_tb_name, db_cols, 
                                (imdb_id, subject_id, rating, int(is_series), season_num, serie_imdb_id, None, self._ts))
                self._db.update(db_tb_name, 'rating', rating, 'imdb_id', imdb_id, self._ts)
                self._db.update(db_tb_name, 'douban_id', subject_id, 'imdb_id', imdb_id, self._ts)
                self._db.update(db_tb_name, 'season_num', season_num, 'imdb_id', imdb_id, self._ts)
                self._db.update(db_tb_name, 'serie_imdb_id', serie_imdb_id, 'imdb_id', imdb_id, self._ts)



            
    
