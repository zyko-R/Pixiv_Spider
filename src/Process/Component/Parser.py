import re
import json
from abc import ABC, abstractmethod
from lxml import etree
from Downloader import Request


def output(message, code, form=0, end='\n'):
    print(f'\033[{form};{code}m{message}\033[0m', end=end)


class MiddleMixin(ABC):
    def __init__(self, id_list):
        self.id_list = id_list

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
    def __init__(self, id_list):
        self.id_list = id_list

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
        img_bina_list, name_list = [], []
        for source_url_list, _id in yield_url(url_list):
            for img_data, suffix, page in yield_data(source_url_list):
                img_bina_list.append(img_data)
                name_list.append(f'{_id}_p{page}.{suffix}')
                output('#', code=33, form=4, end='')
        return img_bina_list, name_list


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
        gif_bina_list, delay_list, name_list = [], [], []

        for zip_url, delay, _id in yield_url(_url_list):
            delay_list.append(delay)
            name_list.append(_id)
            gif_bina = Request(zip_url).resp_list['bina'][0]
            gif_bina_list.append(gif_bina)
            output('#', code=33, form=4, end='')
        return gif_bina_list, delay_list, name_list
