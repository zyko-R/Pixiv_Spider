import asyncio

import aiohttp
from aiohttp import ContentTypeError
from aiohttp import TCPConnector
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import json


def asy_launch(asy_method, params_list, call_back=None):
    p_list = [[] for i in range(len(params_list[0]))]
    for param_list in params_list:
        for i in range(len(param_list)):
            p_list[i].append(param_list[i])

    task_list = []
    loop = asyncio.get_event_loop()
    for params in p_list:
        task = loop.create_task(asy_method(*tuple(params)))
        if call_back is not None:
            task.add_done_callback(call_back)
        task_list.append(task)
    try:
        loop.run_until_complete(asyncio.wait(task_list))
    except ValueError:
        pass


def output(message, code, form=0, end='\n'):
    print(f'\033[{form};{code}m{message}\033[0m', end=end)


class Request:
    headers = {
        'Referer': 'https://www.pixiv.net',
        'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54'
    }
    resp_list = {}

    @classmethod
    def __init__(cls, url_list):
        cls.resp_list = cls.download(url_list)

    @classmethod
    def download(cls, url_list):
        html_list, bina_list, json_list = [], [], []

        async def _except(_url, *args):
            async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as asy_spider:
                async with await asy_spider.get(url=_url, headers=cls.headers) as resp:
                    try:
                        html = await resp.text()
                        html_list.append(html)
                    except (ContentTypeError, UnicodeDecodeError):
                        pass
                    try:
                        bina = await resp.read()
                        bina_list.append(bina)
                    except ContentTypeError:
                        pass
                    try:
                        _json = await resp.json()
                        json_list.append(_json)
                    except ContentTypeError:
                        pass

        asy_launch(_except, (url_list,), call_back=None)
        return {'html': html_list, 'bina': bina_list, 'json': json_list}


class Login:
    login_success = False
    login_info_correct = True

    @classmethod
    def __init__(cls):
        output('login: ', code=31, form=1, end='')
        cls.__reload_cookie()
        while not cls.login_success:
            output('Failed-Retrying', form=4, code=31)
            cls.__simulated_login(cls.login_info())
            cls.__reload_cookie()
            cls.login_info_correct = False
        cls.login_info_correct = True
        output('Success', form=4, code=32)

    @classmethod
    def login_info(cls):
        login_info = {}
        if cls.login_info_correct:
            try:
                with open('./res/id&password.json', 'r+') as f:
                    login_info = json.load(f)
            except Exception:
                cls.login_info_correct = False
        if not cls.login_info_correct:
            login_info = {
                'login_id': str(input("\nenter your pixiv id >? ")),
                'login_password': str(input('enter your password >? '))
            }
            print('please wait a second')
            with open('./res/id&password.json', 'w+') as f:
                f.write(json.dumps(login_info))
        return login_info

    @classmethod
    def __simulated_login(cls, login_info):
        login_id, login_password = login_info['login_id'], login_info['login_password']
        bro = webdriver.Edge(service=Service("../res/msedgedriver"), options=Options().add_argument('--headless'))
        bro.get('https://accounts.pixiv.net/login?return_to=https://www.pixiv.net')
        attr_key = '[@class="sc-bn9ph6-1 hJBrSP"]'
        pixiv_id = bro.find_element(By.XPATH, f'//*{attr_key}/input[@autocomplete="username"]')
        pixiv_id.send_keys(login_id)
        password = bro.find_element(By.XPATH, f'//*{attr_key}/input[@autocomplete="current-password"]')
        password.send_keys(login_password)
        login = bro.find_element(By.XPATH, '//button[@type="submit"]')
        login.click()
        sleep(5)
        with open('./res/cookies.json', 'w+') as f:
            f.write(json.dumps(bro.get_cookies()))

    @classmethod
    def __reload_cookie(cls):
        try:
            with open('./res/cookies.json', 'r+') as fr:
                cookies_list = json.load(fr)
            cookie_list = [item["name"] + "=" + item["value"] for item in cookies_list]
            cookie_str = ';'.join(item for item in cookie_list)
            Request.headers['cookie'] = cookie_str
            url = ['https://www.pixiv.net/ajax/top/illust?mode=all&lang=zh']
            code = json.dumps(Request(url).resp_list['json'][0])
            cls.login_success = False if code.find('error') == -1 else True
        except (TypeError, json.decoder.JSONDecodeError):
            cls.login_success = False
