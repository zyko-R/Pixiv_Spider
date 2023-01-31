import asyncio
import json
import os
import re
import shutil
import zipfile
from abc import abstractmethod, ABC

import imageio
from lxml import etree

from PixivCrawler.Downloader.PluginsXProxy import Download


class PendingData:
    def __init__(self, *args):  self.Method, self.MethodParam = self.method(), args

    @abstractmethod
    def method(self): return self.VoidMethod

    class Method:
        def __init__(self, *args): self.params = self.params(*args)

        @abstractmethod
        def params(self, *args): return args

        @abstractmethod
        def fn_ea(self, *args): pass

        def close(self, *args): return args

    class VoidMethod(Method):
        def params(self): return [], []

        def fn_ea(self, l1, l2): return [None]


class FFilterForm(PendingData):
    def method(self): return self.FilterForm

    class FilterForm(PendingData.Method):
        def params(self, id_list):
            url_list = [f'https://www.pixiv.net/artworks/{_id}' for _id in id_list]
            html_list = Download.response(url_list)['html']
            return id_list, html_list

        def fn_ea(self, _id, html):
            try:
                tag = etree.HTML(html).xpath('//head/title/text()')[0]
                tag = 'GIF' if re.search(r'动图', tag) else 'IMG'
            except AttributeError:
                tag = 'NONE'
            return tag, _id

        def close(self, tag_list, id_list):
            gif_ids, img_ids = [], []
            for tag, _id in zip(tag_list, id_list):
                match tag:
                    case 'IMG':
                        img_ids.append(_id)
                    case 'GIF':
                        gif_ids.append(_id)
            return img_ids, gif_ids


class FFilterType(PendingData):
    def method(self): return self.FilterType

    class FilterType(PendingData.Method):
        def params(self, id_list):
            url_list = [f'https://www.pixiv.net/artworks/{_id}' for _id in id_list]
            html_list = Download.response(url_list)['html']
            return id_list, html_list

        def fn_ea(self, _id, html):
            try:
                tag = etree.HTML(html).xpath('//head/meta[@property="twitter:title"]/@content')[0]
                tag = 'R18' if re.search(r'\[R-18]', tag) else 'NOR'
            except AttributeError:
                tag = 'NONE'
            return tag, _id

        def close(self, tag_list, id_list):
            nor_ids, r18_ids = [], []
            for tag, _id in zip(tag_list, id_list):
                match tag:
                    case 'NOR':
                        nor_ids.append(_id)
                    case 'R18':
                        r18_ids.append(_id)
            return nor_ids, r18_ids


class FParseIMG(PendingData):
    def method(self): return self.ParseIMG

    class ParseIMG(PendingData.Method):
        def params(self, id_list): return [id_list]

        def fn_ea(self, _id):
            asyncio.set_event_loop(asyncio.new_event_loop())
            _json = Download.response([f'https://www.pixiv.net/ajax/illust/{_id}/pages?lang=zh'])['json'][0]
            src_urls = re.findall(r'https://i\.pximg\.net/img-original/img/.*?_p\d+\..{3}', str(_json))
            _bytes_list = Download.response(src_urls)['bytes']
            name_list = [f'{_id}_p{page}.{src_url[-3:]}' for page, src_url in enumerate(src_urls)]
            return _bytes_list, name_list


class FParseGIF(PendingData):
    def method(self): return self.ParseGIF

    class ParseGIF(PendingData.Method):
        def params(self, id_list):
            return [id_list]

        def fn_ea(self, _id):
            asyncio.set_event_loop(asyncio.new_event_loop())
            html = Download.response([f'https://www.pixiv.net/ajax/illust/{_id}/ugoira_meta?lang=zh'])['html'][0]
            url_data = json.loads(html)
            try:
                zip_url = url_data["body"]["originalSrc"]
            except TypeError:
                return None, None, None
            _bytes = Download.response([zip_url])['bytes'][0]
            semi_delay = [item["delay"] for item in url_data["body"]["frames"]]
            delay = sum(semi_delay) / len(semi_delay) / 1000
            return _bytes, delay, _id

        def close(self, bytes_list, delay_list, id_list):
            effective_index = [i for i, _ in filter(lambda x: isinstance(x[1], bytes), enumerate(bytes_list))]
            return [[e[i] for i in effective_index] for e in [bytes_list, delay_list, id_list]]


class FStoreIMG(PendingData):
    def method(self): return self.StoreIMG

    class StoreIMG(PendingData.Method):
        file_name = None

        def params(self, file_name, bytes_list_list, name_list_list):
            self.file_name = file_name
            if not os.path.exists(f'./{file_name}'):
                os.mkdir(f'./{file_name}')
            return bytes_list_list, name_list_list

        def fn_ea(self, bytes_list, name_list):
            asyncio.set_event_loop(asyncio.new_event_loop())
            for _bytes, name in zip(bytes_list, name_list):
                with open(f'./{self.file_name}/{name}', 'wb+') as f:
                    f.write(_bytes)


class FStoreGIF(PendingData):
    def method(self): return self.StoreGIF

    class StoreGIF(PendingData.Method):
        file_name = None

        def params(self, file_name, bytes_list, delay_list, name_list):
            self.file_name = file_name
            if not os.path.exists(f'./{file_name}'):
                os.mkdir(f'./{file_name}')
            return bytes_list, delay_list, name_list

        def fn_ea(self, _bytes, delay, name):
            asyncio.set_event_loop(asyncio.new_event_loop())
            file_path = f'./{self.file_name}/{name}'
            with open(f'{file_path}.zip', "wb+") as f:
                f.write(_bytes)

            with zipfile.ZipFile(f'{file_path}.zip', 'r') as uz:
                uz.extractall(file_path)
                img_paths = uz.namelist()
            os.unlink(f'{file_path}.zip')

            flame_paths = [imageio.v3.imread(f'{file_path}/{img}') for img in img_paths]
            imageio.v2.mimsave(f'{file_path}.gif', flame_paths, duration=delay)
            shutil.rmtree(f'{file_path}')
