# import cv2
from calendar import c
import random
from time import sleep
import re
from pyunpack import Archive
import os
import shutil

from base_api import BaseAPI, handler
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from header import settings

class SubFinder(BaseAPI):
    SUB_EXT = ['srt', 'ass']
    MAX_SUB_NUM = 5
    def __init__(self):
        super(SubFinder, self).__init__(retries=1)

        self._tmp_dir = settings['tmp_dir']
        if os.path.exists(self._tmp_dir): shutil.rmtree(self._tmp_dir)
        os.mkdir(self._tmp_dir)

        self._url = "https://subhd.tv"
        header = {
            'Host':'subhd.tv',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language':'en-US,en;q=0.9',
            'Connection':'keep-alive',
            'Accept-Encoding':'gzip, deflate, br',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.4 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.4 facebookexternalhit/1.1 Facebot Twitterbot/1.0',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self._sess.headers.update(header)
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("no-sandbox")
        options.add_argument("disable-dev-shm-usage")
        # options.add_argument('proxy-server={}'.format(BaseAPI.get_proxy()['http']))
        options.experimental_options["prefs"] = {"download.default_directory": self._tmp_dir}
        self._driver = webdriver.Chrome(executable_path=settings['selenium_exe'], options=options)
        self._wait = WebDriverWait(self._driver, 10)

        
              
    def _solve_captcha(self):
        # bg_img_path = 'tmp/background.png'
        # s_img_path = 'tmp/sliding.png'
        # def findfic(target=bg_img_path, template=s_img_path):
        #     target_rgb = cv2.imread(target)
        #     target_gray = cv2.cvtColor(target_rgb, cv2.COLOR_BGR2GRAY)
        #     print(target_gray.shape)
        #     template_rgb = cv2.imread(template, 0)
        #     res = cv2.matchTemplate(target_gray, template_rgb, cv2.TM_CCOEFF_NORMED)
        #     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        #     if abs(1 - min_val) <= abs(1 - max_val):
        #         distance = min_loc[0]
        #     else:
        #         distance = max_loc[0]
        #     return distance
        
        def get_tracks(distance):
            v, t, sum = 20, 0.5, 0
            plus = []
            while sum < distance:
                s = v * t
                sum += s
                plus.append(round(s))
            return plus

        captcha_iframe = self._wait.until(lambda d: d.find_element(By.ID, "tcaptcha_iframe"))
        self._driver.switch_to.frame(captcha_iframe)
        # background_img_link = self._driver.find_element(By.ID, "cdn1").get_attribute('src')
        # sliding_img_link = self._driver.find_element(By.ID, "cdn2").get_attribute('src')
        # with open(bg_img_path, 'wb') as f1, open(s_img_path, 'wb') as f2:
        #     ret = requests.get(url=background_img_link)
        #     f1.write(ret.content)
        #     ret = requests.get(url=sliding_img_link)
        #     f2.write(ret.content)
        # distance = findfic()
        # print(distance)
        trajectory = get_tracks(207+random.randint(-10, 10))
        slider_element = self._wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div[class='tc-drag-button tc-drag-button-pc']"))
        )

        ac = ActionChains(self._driver)
        ac.click_and_hold(slider_element).perform()
        for track in trajectory:
            ac.move_by_offset(
                xoffset=track,
                yoffset=round(random.uniform(1.0, 3.0), 1)
            ).perform()
        sleep(1)
        ac.release(slider_element).perform()
        sleep(1)
        self._driver.switch_to.default_content()
        sleep(5)


    def get_sub(self, path, imdb_id, is_serie=False, name=None, name_map=None):
        handler.notify("Getting Sub for {} ...".format(imdb_id), critical=False)
        def check_download_finished():
            for fname in os.listdir(self._tmp_dir):
                if fname.endswith('.crdownload'): return False
            return True

        def relocate(from_path, cnt, file=None):
            if not is_serie:
                assert(name is not None)
                if file is not None:
                    f_ext = file.split('.')[-1]
                    shutil.copyfile(os.path.join(from_path, file), os.path.join(path, name+'.'+str(cnt)+'.'+f_ext))
                    cnt += 1
                else:
                    for dirpaths, dirnames, files in os.walk(from_path):
                        for file in files:
                            f_ext = file.split('.')[-1]
                            if f_ext not in SubFinder.SUB_EXT: continue
                            shutil.copyfile(os.path.join(dirpaths, file), os.path.join(path, name+'.'+str(cnt)+'.'+f_ext))  
                            cnt += 1
                        
            else:
                assert(file is None and name_map is not None)
                for dirpaths, dirnames, files in os.walk(from_path):
                    for file in files:
                        f_ext = file.split('.')[-1]
                        if f_ext not in SubFinder.SUB_EXT: continue
                        f_name = file[: file.rfind('.')]
                        pattern = re.compile(r'E\d+')  
                        ep_num = pattern.search(f_name).group()
                        ep_num = int(ep_num.split('E')[-1])
                        shutil.copyfile(os.path.join(dirpaths, file), os.path.join(path, name_map[ep_num]+'.'+str(cnt)+'.'+f_ext))  
                cnt += 1
            return cnt

        def unpack():
            cnt = 0
            workdir = self._tmp_dir
            for file in os.listdir(workdir):
                f_ext = file.split('.')[-1]
                if f_ext in ['7z', 'zip']: 
                    f_name = file[: file.rfind('.')]
                    extract_dir = os.path.join(workdir, f_name)
                    os.mkdir(extract_dir)
                    Archive(os.path.join(workdir, file)).extractall(extract_dir)
                    cnt = relocate(extract_dir, cnt)
                elif f_ext in SubFinder.SUB_EXT:
                    cnt = relocate(workdir, cnt, file=file)
            handler.notify("Got {} Subs!".format(cnt), critical=False)
                            
        ret = self.request(params="/search/{}".format(imdb_id))
        soup = BeautifulSoup(ret.content, "html.parser")
        subs = soup.find_all(name='div', attrs={"class": "float-start f16 fw-bold"})
        sub_cnt = 0
        for sub in subs: 
            if sub_cnt > SubFinder.MAX_SUB_NUM: break
            if is_serie:
                pattern = re.compile(r'E\d+')  
                ep_num = pattern.search(sub.text).group()
                if int(ep_num.split('E')[-1]) != 0: continue
            sub_id = sub.a['href'].split('/')[-1]
            self._driver.get("{}/a/{}".format(self._url, sub_id))
            # sleep(1)
            try:
                button = self._wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "button[class='btn btn-danger down']"))
            except NoSuchElementException:
                handler.notify("No Sub: {}".format(imdb_id), critical=False)
                return 
            # self._wait.until(EC.element_to_be_clickable(button))
            self._driver.execute_script("arguments[0].click();", button)
            # sleep(1)
            if button.get_attribute('id') == 'TencentCaptcha':
                while "下载中" not in button.text: 
                    handler.notify("SubHD Captcha!", critical=False)
                    self._solve_captcha()
                    # sleep(5)
                    button = self._wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "button[class='btn btn-danger down']"))
            while not check_download_finished(): sleep(2)
            sub_cnt += 1
        self._driver.quit()
        unpack()

if __name__ == '__main__':
    sf = SubFinder()
    sf.get_sub("tmp", "tt8228288", name="tt8228288")