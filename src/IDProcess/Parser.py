import re
import json

from Main import output
from abc import ABC, abstractmethod
from lxml import etree
from Request import Request


class MiddleMixin(ABC):
    @abstractmethod
    def process_id(self, id_list):
        pass


class MiddlePackage(MiddleMixin):
    def process_id(self, id_list):

        ids_normal = {'img': [], 'gif': []}
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
                    ids_normal['gif' if gif_tag.find('动图') != -1 else 'img'].append(_id)
                output('#', code=33, form=4, end='')
            except IndexError:
                pass

        return ids_normal, ids_r18


class MiddleCaller:
    @classmethod
    def __init__(cls, id_list, middle_mixin):
        cls.Result = []
        if len(id_list) > 0:
            output('process ids: ', form=1, code=31, end='')
            cls.Result = middle_mixin.process_id(id_list)
            output(f'[finish]', form=4, code=32)


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
        else:
            pass


class Parser:
    @staticmethod
    def except_author_info(_author_info) -> ():
        try:
            if re.match("^[0-9]*$", _author_info) is not None:
                author_id = _author_info
                url = [f'https://www.pixiv.net/users/{author_id}']
                Request(url)
                html = Request.resp_list['html'][0]
                name_data = etree.HTML(html).xpath('//head/title/text()')[0]
                author_name = re.findall('(.*?) - pixiv', name_data)[0]
            else:
                author_name = _author_info
                url = [f'https://www.pixiv.net/search_user.php?nick={author_name}&s_mode=s_usr']
                Request(url)
                html = Request.resp_list['html'][0]
                id_data = etree.HTML(html).xpath('//h1/a[@target="_blank"][@class="title"]/@href')[0]
                author_id = re.findall(r'\w+/(\d+)', id_data)[0]
            return author_name, author_id
        except IndexError:
            output('Please enter correct parameter', code=31, form=1)
            exit()
