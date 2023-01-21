import json
import os
from abc import abstractmethod
from time import sleep

from requests import session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service

from PixivCrawler.Util.Requests.Requester import Requester, IDownloader


def colour_str(message, code, form=0):
    return f'\033[{form};{code}m{message}\033[0m'


class Download(IDownloader):
    __requester = Requester()

    @classmethod
    def response(cls, url_list):
        return Login(cls.__requester).response(url_list)


class IDownloaderDecorator(IDownloader):
    def __init__(self, downloader):
        self.decorated_downloader = downloader

    def response(self, url_list):
        self.decor()
        return self.decorated_downloader.response(url_list)

    @abstractmethod
    def decor(self):
        pass


class Login(IDownloaderDecorator):
    res_path = os.path.normpath('PixivCrawler/Util/Requests/res')
    login_url, id_xpath, password_xpath, submit_xpath = \
        ('https://accounts.pixiv.net/login?return_to=https://www.pixiv.net',
         '//*[@class="sc-bn9ph6-1 hJBrSP"]/input[@autocomplete="username"]',
         '//*[@class="sc-bn9ph6-1 hJBrSP"]/input[@autocomplete="current-password"]',
         '//button[@type="submit"]')
    login_success = False
    login_info_correct = True

    def __simulated_login(self):
        login_info = None
        try:
            with open(os.path.normpath(f'{self.res_path}/id&password.json'), 'r+') as fr:
                login_info = json.load(fr)
        except BaseException:
            self.login_info_correct = False
        if not self.login_info_correct:
            login_info = {
                'login_id': str(input("\nenter your pixiv id >? ")),
                'login_password': str(input('enter your password >? '))
            }
            with open(os.path.normpath(f'{self.res_path}/cookie.json'), 'w+') as fw:
                fw.write(json.dumps(login_info))
        bro = webdriver.Edge(service=Service(os.path.normpath(f'{self.res_path}/msedgedriver')))
        bro.get(self.login_url)
        bro.find_element(By.XPATH, self.id_xpath).send_keys(login_info['login_id'])
        bro.find_element(By.XPATH, self.password_xpath).send_keys(login_info['login_password'])
        bro.find_element(By.XPATH, self.submit_xpath).click()
        sleep(3)
        with open(os.path.normpath(f'{self.res_path}/cookie.json'), 'w+') as f:
            f.write(json.dumps(bro.get_cookies()))

    def __reload_cookie(self):
        try:
            with open(os.path.normpath(f'{self.res_path}/cookie.json'), 'r+') as fr:
                cookies_list = json.load(fr)
            cookie_list = [item["name"] + "=" + item["value"] for item in cookies_list]
            cookie_str = ';'.join(item for item in cookie_list)
            Requester.headers['cookie'] = cookie_str
            with session().get(headers=Requester.headers, url=self.login_url) as resp:
                Login.login_success = True if resp.url != self.login_url else False
        except (TypeError, json.decoder.JSONDecodeError):
            Login.login_success = False

    def decor(self):
        if self.login_success:
            return
        print(colour_str('logining: ', code=31, form=1), end='')
        while True:
            self.__reload_cookie()
            if self.login_success:
                break
            self.__simulated_login()
            self.login_info_correct = False
        print(colour_str('Success', code=32, form=4))
