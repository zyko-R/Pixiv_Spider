from Main import output
from IDProcess.Parser import *
from IDProcess.Pipeline import *
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from Request import Request
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
                with open('../../res/id&password.json', 'r+') as f:
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
        sleep(3)
        with open('./res/cookies.json', 'w') as f:
            f.write(json.dumps(bro.get_cookies()))

    @classmethod
    def __reload_cookie(cls):
        try:
            with open('./res/cookies.json', 'w+') as fr:
                cookies_list = json.load(fr)
            cookie_list = [item["name"] + "=" + item["value"] for item in cookies_list]
            cookie_str = ';'.join(item for item in cookie_list)
            Request.headers['cookie'] = cookie_str
            url = ['https://www.pixiv.net/ajax/top/illust?mode=all&lang=zh']
            Request(url)
            code = json.dumps(Request.resp_list['json'][0])
            cls.login_success = False if code.find('error') == -1 else True
        except TypeError:
            cls.login_success = False
        except json.decoder.JSONDecodeError:
            cls.login_success = False


class Crawler:
    def __init__(self, id_list, _author_info):
        self.author_info = _author_info
        self.id_list = id_list
        self.author_id = None
        self.r18_file_name = None
        self.nor_file_name = None

    def work(self):
        self.start()
        self.middle()
        self.end()

    def start(self):
        author_name, self.author_id = Parser.except_author_info(self.author_info)
        if author_name.find(r'/') != -1:
            author_name = 'ERROR'
        self.r18_file_name = f'[R18]{author_name}'
        self.nor_file_name = f'[NOR]{author_name}'

    def end(self):
        if os.path.exists(f'./{self.r18_file_name}'):
            Pipeline.zip(self.r18_file_name)
            shutil.rmtree(f'./{self.r18_file_name}')
        if os.path.exists(f'./{self.nor_file_name}'):
            Pipeline.zip(self.nor_file_name)
            shutil.rmtree(f'./{self.nor_file_name}')

    def middle(self):
        ids_nor, ids_r18 = MiddleCaller(self.id_list, MiddlePackage()).Result
        result = PackageCaller(ids_nor['img'], PackageIMG()).Result
        WriteCaller(result, self.nor_file_name, WriteIMG())
        result = PackageCaller(ids_r18['img'], PackageIMG()).Result
        WriteCaller(result, self.r18_file_name, WriteIMG())
        result = PackageCaller(ids_nor['gif'], PackageGIF()).Result
        WriteCaller(result, self.nor_file_name, WriteGIF())
        result = PackageCaller(ids_r18['gif'], PackageGIF()).Result
        WriteCaller(result, self.r18_file_name, WriteGIF())

