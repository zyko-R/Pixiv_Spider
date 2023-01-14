import re
import json
from abc import ABC, abstractmethod
from lxml import etree
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from Request import Request
from selenium.webdriver.edge.options import Options
from Main import output


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
            Request(url)
            code = json.dumps(Request.resp_list['json'][0])
            cls.login_success = False if code.find('error') == -1 else True
        except (TypeError, json.decoder.JSONDecodeError):
            cls.login_success = False


class MiddleMixin(ABC):
    Result = []

    def __init__(self, id_list):
        self.id_list = id_list
        if len(self.id_list) > 0:
            output('process ids: ', form=1, code=31, end='')
            self.Result = self.process_id()
            output(f'[finish]', form=4, code=32)

    @abstractmethod
    def process_id(self):
        pass


class MiddlePackage(MiddleMixin):
    def process_id(self):
        ids_nor = {'img': [], 'gif': []}
        ids_r18 = {'img': [], 'gif': []}
        url_list = [f'https://www.pixiv.net/artworks/{_id}' for _id in self.id_list]
        Request(url_list)
        for group in range(len(Request.resp_list['html'])):
            html, _id = Request.resp_list['html'][group], self.id_list[group]
            try:
                gif_tag = etree.HTML(html).xpath('//head/title/text()')[0]
                r18_tag = etree.HTML(html).xpath('//head/meta[@property="twitter:title"]/@content')[0]
                if r18_tag.find('R-18') != -1:
                    ids_r18['gif' if gif_tag.find('动图') != -1 else 'img'].append(_id)
                else:
                    ids_nor['gif' if gif_tag.find('动图') != -1 else 'img'].append(_id)
                output('#', code=33, form=4, end='')
            except(IndexError, AttributeError):
                pass
        output('[finish]', form=0, code=32)
        output(f'[NOR]: [IMG]{len(ids_nor["img"])}, [GIF]{len(ids_nor["gif"])}', form=0, code=32)
        output(f'[R18]: [IMG]{len(ids_r18["img"])}, [GIF]{len(ids_r18["gif"])}', form=0, code=32)
        return ids_nor, ids_r18


class PackageMixin(ABC):
    Result = []

    def __init__(self, id_list):
        self.id_list = id_list
        if len(self.id_list) > 0:
            output(f'expect source: ', form=1, code=31, end='')
            self.Result = self.package()
            output(f'[finish]', form=4, code=32)

    @abstractmethod
    def package(self):
        pass


class PackageIMG(PackageMixin):
    def package(self):
        def yield_url(_url_list):
            resp_list = Request(_url_list).resp_list['json']
            for group, _src_url_html in enumerate(resp_list):
                _src_url_list = re.findall(r'https://i\.pximg\.net/img-original/img/.*?_p\d+\..{3}', str(_src_url_html))
                yield _src_url_list, self.id_list[group]

        def yield_data(_source_url_list):
            resp_list = Request(_source_url_list).resp_list['bina']
            for _page, _img_data in enumerate(resp_list):
                _suffix = _source_url_list[_page][-3:]
                yield _img_data, _suffix, _page

        url_list = [f'https://www.pixiv.net/ajax/illust/{_id}/pages?lang=zh' for _id in self.id_list]
        download_infos = []
        for source_url_list, _id in yield_url(url_list):
            for img_data, suffix, page in yield_data(source_url_list):
                download_infos.append((img_data, f'{_id}_p{page}.{suffix}'))
                output('#', code=33, form=4, end='')
        return download_infos


class PackageGIF(PackageMixin):
    def package(self):
        def yield_url(_url_list):
            url_data_list = Request(_url_list).resp_list['html']
            for group, url_data in enumerate(url_data_list):
                url_data = json.loads(url_data)
                try:
                    _zip_url = url_data["body"]["originalSrc"]
                    _delay = [item["delay"] for item in url_data["body"]["frames"]]
                    _delay = sum(_delay) / len(_delay) / 1000
                    _id = self.id_list[group]
                    yield [_zip_url], _delay, _id
                except TypeError:
                    pass

        _url_list = [f'https://www.pixiv.net/ajax/illust/{_id}/ugoira_meta?lang=zh' for _id in self.id_list]
        download_infos = []
        for zip_url, delay, _id in yield_url(_url_list):
            gif_bina = Request(zip_url).resp_list['bina'][0]
            download_infos.append((gif_bina, delay, _id))
            output('#', code=33, form=4, end='')
        return download_infos
