import json
import os
import re
import shutil
import zipfile
from abc import abstractmethod, ABC

import aiofiles
import imageio
from lxml import etree

from PixivCrawler.Util.Requests.Proxy import Download
from PixivCrawler.Util.ThreadManager import ThreadLauncher, Thread, Async


class IFilterAPI(ABC):
    def __init__(self, id_list, html_list):
        self.id_list, self.html_list = id_list, html_list

    @abstractmethod
    def filter(self):
        pass


class IParseAPI(ABC):
    def __init__(self, id_list):
        self.id_list = id_list

    @abstractmethod
    def parse(self):
        pass


class IStoreAPI(ABC):
    def __init__(self, file_name, infos=(None,)):
        self.infos, self.file_name = infos, file_name

    @abstractmethod
    def store(self):
        pass


class FilterForm(IFilterAPI):
    def filter(self):
        gif_ids, img_ids = {'ids': [], 'html': []}, {'ids': [], 'html': []}
        for index in range(len(self.html_list)):
            try:
                tag = etree.HTML(self.html_list[index]).xpath('//head/title/text()')[0]
                ids = gif_ids if re.search(r'动图', tag) else img_ids
                ids['ids'].append(self.id_list[index])
                ids['html'].append(self.html_list[index])
            except AttributeError:
                pass
        return img_ids, gif_ids


class FilterType(IFilterAPI):
    def filter(self):
        nor_ids, r18_ids = {'ids': [], 'html': []}, {'ids': [], 'html': []}
        for index in range(len(self.html_list)):
            try:
                tag = etree.HTML(self.html_list[index]).xpath('//head/meta[@property="twitter:title"]/@content')[0]
                ids = r18_ids if re.search(r'\[R-18]', tag) else nor_ids
                ids['ids'].append(self.id_list[index])
                ids['html'].append(self.html_list[index])
            except AttributeError:
                pass
        return nor_ids, r18_ids


class ParseIMG(IParseAPI):
    def parse(self):
        def yield_url(_url_list):
            resp_list = Download.response(_url_list)['json']
            for group, _src_url_html in enumerate(resp_list):
                _src_url_list = re.findall(r'https://i\.pximg\.net/img-original/img/.*?_p\d+\..{3}', str(_src_url_html))
                yield _src_url_list, self.id_list[group]

        def yield_data(_id, _source_url_list):
            _bina_list = Download.response(_source_url_list)['bina']
            _name_list = [f'{_id}_p{_page}.{_source_url_list[_page][-3:]}'
                          for _page, _img_url in enumerate(_source_url_list)]
            yield _bina_list, _name_list

        img_groups = []
        url_list = [f'https://www.pixiv.net/ajax/illust/{_id}/pages?lang=zh' for _id in self.id_list]
        for source_url_list, _id in yield_url(url_list):
            for bina_list, name_list in yield_data(_id, source_url_list):
                img_groups.append((bina_list, name_list))
        return img_groups


class ParseGIF(IParseAPI):
    def parse(self):
        def yield_url(_url_list):
            url_data_list = Download.response(_url_list)['html']
            for group, url_data in enumerate(url_data_list):
                url_data = json.loads(url_data)
                try:
                    _zip_url = url_data["body"]["originalSrc"]
                except TypeError:
                    continue
                _delay = [item["delay"] for item in url_data["body"]["frames"]]
                _delay = sum(_delay) / len(_delay) / 1000
                _id = self.id_list[group]
                yield [_zip_url], _delay, _id

        _url_list = [f'https://www.pixiv.net/ajax/illust/{_id}/ugoira_meta?lang=zh' for _id in self.id_list]
        gif_url_list, delay_list, name_list = [], [], []

        for zip_url, delay, _id in yield_url(_url_list):
            delay_list.append(delay)
            name_list.append(_id)
            gif_url_list += zip_url
        gif_bina_list = Download.response(gif_url_list)['bina']
        return gif_bina_list, delay_list, name_list


class StoreIMG(IStoreAPI):
    def store(self):
        async def write_in(img_data, img_name):
            async with aiofiles.open(f'./{self.file_name}/{img_name}', 'wb+') as f:
                await f.write(img_data)

        for bina_list, name_list in self.infos:
            ThreadLauncher(Async(write_in, (bina_list, name_list)))


class StoreGIF(IStoreAPI):
    def store(self):
        def load_all_zip(_gif_bina_list, _gif_name_list):
            async def load_zip(_gif_bina, _gif_name):
                zip_path = f'./{self.file_name}/{_gif_name}.zip'
                async with aiofiles.open(zip_path, "wb+") as fp:
                    await fp.write(_gif_bina)

            ThreadLauncher(Async(load_zip, (_gif_bina_list, _gif_name_list)))

        def unzip_all_img(_gif_name_list):
            def unzip(file_path):
                with zipfile.ZipFile(file_path + '.zip', "r") as uz:
                    uz.extractall(file_path)
                os.unlink(file_path + '.zip')
                return file_path, uz.namelist()

            file_name_list = [f'./{self.file_name}/{_gif_name}' for _gif_name in _gif_name_list]
            _flames_infos = ThreadLauncher(Thread(unzip, (file_name_list,)))
            return _flames_infos

        def merge_all(_flames_infos, _delay_list):
            def merge_each(_file_path, _img_paths, _delay):
                flame_paths = [imageio.v3.imread(f'{_file_path}/{img}') for img in _img_paths]
                imageio.v2.mimsave(f'{_file_path}.gif', flame_paths, duration=_delay)
                shutil.rmtree(f'{_file_path}')

            file_path_list, img_paths_list = [], []
            for file_path, img_paths in _flames_infos:
                file_path_list.append(file_path)
                img_paths_list.append(img_paths)
            ThreadLauncher(Thread(merge_each, (file_path_list, img_paths_list, _delay_list)))

        gif_bina_list, delay_list, gif_name_list = self.infos
        load_all_zip(gif_bina_list, gif_name_list)
        flames_infos = unzip_all_img(gif_name_list)
        merge_all(flames_infos, delay_list)


class ZIPFile(IStoreAPI):
    def store(self):
        src_dir = f'./{self.file_name}'
        with zipfile.ZipFile('{src_dir}.zip', 'w', zipfile.ZIP_DEFLATED) as zipper:
            for path, _, files in os.walk(src_dir):
                for file in files:
                    zipper.write(os.path.join(path, file), os.path.join(path.replace(src_dir, ''), file))
        os.unlink(src_dir)
