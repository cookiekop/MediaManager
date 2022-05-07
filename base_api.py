from time import sleep
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from header import *
from handler import ErrorHandler
import random
handler = ErrorHandler()

class BaseAPI:
    def get_proxy():
        session_id = random.random()
        proxy_settings = settings['proxy_settings']
        super_proxy_url = ('http://%s-session-%s:%s@zproxy.lum-superproxy.io:%d' %
            (proxy_settings['username'], session_id, proxy_settings['passwd'], proxy_settings['port']))
        return {"http": super_proxy_url,
                "https": super_proxy_url}

    def __init__(self, retries=10):
        self._sess = requests.Session()
        self._retries = retries

    def request(self, url=None, params=""):
        if url is None: url = self._url 
        for retry_i in range(self._retries):
            sleep(0.1)
            res = self._sess.get(url + params, verify=False, proxies=BaseAPI.get_proxy())
            if res.ok: break
            elif res.status_code == 404: 
                handler.notify("API 404", critical=False)
                break
            if retry_i == self._retries - 1: handler.notify("API")
        return res
    
    def post(self, url, data):
        res = self._sess.post(url=url, data=data, verify=False, proxies=BaseAPI.get_proxy())
        return res