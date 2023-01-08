import re
import json
from Main import output
from abc import ABC, abstractmethod
from lxml import etree
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from Process.Request import Request
from selenium.webdriver.edge.options import Options


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
    @abstractmethod
    def process_id(self, id_list):
        pass


class MiddlePackage(MiddleMixin):
    def process_id(self, id_list):

        ids_nor = {'img': [], 'gif': []}
        ids_r18 = {'img': [], 'gif': []}
        url_list = [f'https://www.pixiv.net/artworks/{_id}' for _id in id_list]
        Request(url_list)
        for group in range(len(Request.resp_list['html'])):
            html, _id = Request.resp_list['html'][group], id_list[group]
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
        log = f"""
        [NOR]: [IMG]{len(ids_nor['img'])}, [GIF]{len(ids_nor['gif'])}
        [R18]: [IMG]{len(ids_r18['img'])}, [GIF]{len(ids_r18['gif'])}"""
        output(log, form=0, code=32)
        return ids_nor, ids_r18


class MiddleCaller:
    @classmethod
    def __init__(cls, id_list, middle_mixin):
        cls.Result = []
        if len(id_list) > 0:
            output('process ids: ', form=1, code=31, end='')
            cls.Result = middle_mixin.process_id(id_list)


class PackageMixin(ABC):
    @abstractmethod
    def package(self, id_list):
        pass


class PackageIMG(PackageMixin):
    def package(self, _id_list):
        download_infos = []
        _url_list = [f'https://www.pixiv.net/ajax/illust/{_id}/pages?lang=zh' for _id in _id_list]
        Request(_url_list)

        json_list = Request.resp_list['json']
        for group in range(len(json_list)):
            page_urls = re.findall(r'https://i\.pximg\.net/img-original/img/.*?_p\d+\..{3}', str(json_list[group]))
            Request(page_urls)
            img_bina = Request.resp_list['bina']
            for page in range(len(img_bina)):
                img_data, suffix, _id, page = img_bina[page], page_urls[page][-3:], _id_list[group], page
                download_infos.append((img_data, suffix, _id, page))
                output('#', code=33, form=4, end='')

        return download_infos


class PackageGIF(PackageMixin):
    def package(self, _id_list):
        download_infos = []
        _url_list = [f'https://www.pixiv.net/ajax/illust/{_id}/ugoira_meta?lang=zh' for _id in _id_list]
        Request(_url_list)

        url_data_list = Request.resp_list['html']
        for group in range(len(url_data_list)):
            url_data = json.loads(url_data_list[group])
            zip_url = url_data["body"]["originalSrc"]
            Request([zip_url])
            delay = [item["delay"] for item in url_data["body"]["frames"]]
            gif_bina, _id, delay = Request.resp_list['bina'][0], _id_list[group], sum(delay) / len(delay) / 1000
            download_infos.append((gif_bina, _id, delay))
            output('#', code=33, form=4, end='')

        return download_infos


class PackageCaller:
    Result = []

    @classmethod
    def __init__(cls, id_list, package_mixin):
        cls.Result = []
        if len(id_list) > 0:
            output(f'expect source: ', form=1, code=31, end='')
            cls.Result = package_mixin.package(id_list)
            output(f'[finish]', form=4, code=32)


class SecondINFOMixin(ABC):
    @abstractmethod
    def except_(self, param):
        pass


class SecondINFOAuthorName(SecondINFOMixin):
    def except_(self, param):
        try:
            url = [f'https://www.pixiv.net/users/{param}']
            Request(url)
            html = Request.resp_list['html'][0]
            name_data = etree.HTML(html).xpath('//head/title/text()')[0]
            return re.findall('(.*?) - pixiv', name_data)[0]
        except IndexError:
            output('Please enter correct parameter', code=31, form=1)
            exit()


class SecondINFOAuthorID(SecondINFOMixin):
    def except_(self, param):
        try:
            url = [f'https://www.pixiv.net/search_user.php?nick={param}&s_mode=s_usr']
            Request(url)
            html = Request.resp_list['html'][0]
            id_data = etree.HTML(html).xpath('//h1/a[@target="_blank"][@class="title"]/@href')[0]
            return re.findall(r'\w+/(\d+)', id_data)[0]
        except IndexError:
            output('Please enter correct parameter', code=31, form=1)
            exit()


class SecondINFOCaller:
    Result = []

    @classmethod
    def __init__(cls, param, second_info_mixin):
        cls.Result = []
        cls.Result = second_info_mixin.except_(param)