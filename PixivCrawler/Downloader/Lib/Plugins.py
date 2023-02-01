import json
import os
from time import sleep

from requests import session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service


def colorstr(message, code, form=0):
    return f'\033[{form};{code}m{message}\033[0m'


class Login:
    res_path = os.path.normpath('PixivCrawler/Downloader/Lib')
    login_url, id_xpath, password_xpath, submit_xpath = \
        ('https://accounts.pixiv.net/login?return_to=https://www.pixiv.net',
         '//*[@class="sc-bn9ph6-1 hJBrSP"]/input[@autocomplete="username"]',
         '//*[@class="sc-bn9ph6-1 hJBrSP"]/input[@autocomplete="current-password"]',
         '//button[@type="submit"]')
    login_success, login_info_correct = False, True
    AutoLogin = True

    class Wrapper:
        def __init__(self, auto_login=True): self.AutoLogin = auto_login

        def __call__(self, get):
            def login(request):
                Login.AutoLogin = self.AutoLogin
                if not Login.login_success:
                    print(colorstr('logining: ', code=31, form=1), end='')
                    Login.check_cookie()
                    while not Login.login_success:
                        Login.write_cookie()
                        Login.check_cookie()
                        Login.login_info_correct = False
                    print(colorstr('[Success]', code=32, form=1))
                return get(request)
            return login

    @classmethod
    def write_cookie(cls):
        def sli_login():
            login_info = None
            try:
                with open(os.path.normpath(f'{cls.res_path}/id&password.json'), 'r+') as fr:
                    login_info = json.load(fr)
            except (TypeError, json.decoder.JSONDecodeError, FileNotFoundError):
                cls.login_info_correct = False
            if not cls.login_info_correct:
                login_info = {
                    'login_id': str(input("\nenter your pixiv id >? ")),
                    'login_password': str(input('enter your password >? '))
                }
                with open(os.path.normpath(f'{cls.res_path}/cookie.json'), 'w+') as fw:
                    fw.write(json.dumps(login_info))

            bro = webdriver.Edge(service=Service(os.path.normpath(f'{cls.res_path}/msedgedriver')))
            bro.get(cls.login_url)
            bro.find_element(By.XPATH, cls.id_xpath).send_keys(login_info['login_id'])
            bro.find_element(By.XPATH, cls.password_xpath).send_keys(login_info['login_password'])
            bro.find_element(By.XPATH, cls.submit_xpath).click()
            sleep(3)
            return ';'.join([item["name"] + "=" + item["value"] for item in bro.get_cookies()])

        def write_cookie(_cookie):
            with open(os.path.normpath(f'{cls.res_path}/cookie.txt'), 'w+') as f:
                f.write(_cookie)

        write_cookie(sli_login() if cls.AutoLogin else str('Please enter your pixiv_cookie >? '))

    @classmethod
    def check_cookie(cls):
        from PixivCrawler.Downloader.Request import Request
        try:
            with open(os.path.normpath(f'{cls.res_path}/cookie.txt'), 'r+') as fr:
                Request.headers['cookie'] = fr.readline()
            with session().get(headers=Request.headers, url=cls.login_url) as resp:
                Login.login_success = True if resp.url != cls.login_url else False
        except (TypeError, json.decoder.JSONDecodeError, FileNotFoundError):
            Login.login_success = False
