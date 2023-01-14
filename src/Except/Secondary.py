import json
from lxml import etree
from Except.Primary import *
from Request import Request


def subscribe():
    def write_in(author_id):
        sub_list = {'subscribe': []}
        try:
            with open('./res/subscribe.json', 'r+') as f:
                sub_list = json.load(f)
        except (TypeError, json.decoder.JSONDecodeError):
            pass
        for sub in sub_list['subscribe']:
            if author_id == sub['author_id']:
                return
        name, new_id = PluginPackage(ByAuthorID).run()
        sub_list['subscribe'].append({'author_id': author_id, 'artwork_id': new_id})
        with open('./res/subscribe.json', 'w') as f:
            f.write(json.dumps(sub_list))

    def auto_subscribe(user_id):
        url = [f'https://www.pixiv.net/ajax/user/{user_id}'
               f'/following?offset=0&limit=100&rest=show&tag=&acceptingRequests=0&lang=zh']
        user_list = Request(url).resp_list['json'][0]
        for user in user_list['body']['users']:
            write_in(user['userId'])

    match str(input('Auto synchronize -type 1, Manual -type 2 >? ')):
        case '1':
            auto_subscribe(str(input("Enter Your Pixiv Id>? ")))
        case '2':
            write_in(str(input('Enter Author(ID/Name)>?')))


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
        cls.Result = second_info_mixin.except_(param)


def get_info(author_info):
    if re.match("^[0-9]*$", author_info) is not None:
        author_name = SecondINFOCaller(author_info, SecondINFOAuthorName()).Result
        author_id = author_info
    else:
        author_id = SecondINFOCaller(author_info, SecondINFOAuthorID()).Result
        author_name = author_info
    return author_name, author_id
