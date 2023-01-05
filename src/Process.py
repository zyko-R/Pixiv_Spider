import json
import shutil
import os
import requests
import urllib3
from time import sleep
from selenium import webdriver
from json import JSONDecodeError
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import nest_asyncio
from Main import *
from Parser import Parser
from Pipeline import Pipeline
from Request import Request

urllib3.disable_warnings()
nest_asyncio.apply()


class Trailblazer:
    login_success = False
    login_info_correct = True

    @classmethod
    def login_proxy(cls):
        output('login: ', code=31, form=1, end='')
        cls.__reload_cookie()
        while not cls.login_success:
            output('Failed', form=4, code=31)
            output('retrying: ', form=1, code=31, end='')
            cls.__simulated_login()
            cls.__reload_cookie()
            cls.login_info_correct = False
        cls.login_info_correct = True
        output('Success', form=4, code=32)

    @classmethod
    def __simulated_login(cls):
        if cls.login_info_correct:
            with open('./res/id&password.json', 'r') as fr:
                login_info = json.load(fr)
        else:
            login_info = {
                'login_id': str(input("\nenter your pixiv id >?")),
                'login_password': str(input('enter your password >?'))
            }
            with open('res/id&password.json', 'w') as f:
                f.write(json.dumps(login_info))

        login_id, login_password = login_info['login_id'], login_info['login_password']
        bro = webdriver.Edge(service=Service("../res/msedgedriver"))
        bro.get('https://accounts.pixiv.net/login?return_to=https://www.pixiv.net')
        attr_key = '[@class="sc-bn9ph6-1 hJBrSP"]'
        pixiv_id = bro.find_element(By.XPATH, f'//*{attr_key}/input[@autocomplete="username"]')
        pixiv_id.send_keys(login_id)
        password = bro.find_element(By.XPATH, f'//*{attr_key}/input[@autocomplete="current-password"]')
        password.send_keys(login_password)
        login = bro.find_element(By.XPATH, '//button[@type="submit"]')
        login.click()
        sleep(1)
        with open('res/cookies.json', 'w') as f:
            f.write(json.dumps(bro.get_cookies()))

    @classmethod
    def __reload_cookie(cls):
        try:
            with open('res/cookies.json', 'r') as fr:
                cookies_list = json.load(fr)
            cookie_list = [item["name"] + "=" + item["value"] for item in cookies_list]
            cookie_str = ';'.join(item for item in cookie_list)
        except JSONDecodeError:
            print('cookies.json: VOID')
            return
        except TypeError:
            print('cookies.json: INCORRECT FORMAT')
            return

        Request.headers['cookie'] = cookie_str
        url = 'https://www.pixiv.net/ajax/top/illust?mode=all&lang=zh'
        with requests.session() as spider:
            with spider.get(headers=Request.headers, url=url) as resp:
                code = str(resp.json)
        cls.login_success = False if code.find('200') == -1 else True


class Run:
    def start(self):
        Trailblazer.login_proxy()

        author_info = str(input('Author(ID/Name)>? '))
        self.img_limit = int(input("How many sources do you want>? "))

        author_name, self.author_id = Parser.except_author_info(author_info)
        if author_name.find(r'/') != -1:
            author_name = 'ERROR'

        self.r18_file_name = f'[R18]{author_name}'
        self.nor_file_name = f'[NOR]{author_name}'

        if os.path.exists(f'./{self.r18_file_name}'):
            shutil.rmtree(f'./{self.r18_file_name}')
        if os.path.exists(f'./{self.nor_file_name}'):
            shutil.rmtree(f'./{self.nor_file_name}')

    def end(self):
        pass
        if os.path.exists(f'./{self.r18_file_name}'):
            Pipeline.zip(self.r18_file_name)
            shutil.rmtree(f'./{self.r18_file_name}')
        if os.path.exists(f'./{self.nor_file_name}'):
            Pipeline.zip(self.nor_file_name)
            shutil.rmtree(f'./{self.nor_file_name}')

    def run(self):
        id_list = Parser.except_ids(self.author_id, self.img_limit)
        ids_normal, ids_r18 = Parser.group_ids(id_list)
        Parser.Ex.download_proxy(ids_normal['img'], form=Parser.Ex.IMG_FORM, file_name=self.nor_file_name)
        Parser.Ex.download_proxy(ids_normal['gif'], form=Parser.Ex.GIF_FORM, file_name=self.nor_file_name)
        Parser.Ex.download_proxy(ids_r18['img'], form=Parser.Ex.IMG_FORM, file_name=self.r18_file_name)
        Parser.Ex.download_proxy(ids_r18['gif'], form=Parser.Ex.GIF_FORM, file_name=self.r18_file_name)