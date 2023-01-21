import json
import os
import re
import shutil
import zipfile
from abc import abstractmethod, ABC

import aiofiles
import aiofiles.os
import imageio
from lxml import etree

from PixivCrawler.Util.Requests.Proxy import Download
from PixivCrawler.Crawler.SemiCrawler.HandlerCell.Template import IFilter, IStore, IParse
from PixivCrawler.Util.ThreadManager import ThreadLauncher, Thread, Async


def colour_str(message, code, form=0):
    return f'\033[{form};{code}m{message}\033[0m'


class IProcessIMP(ABC):
    @abstractmethod
    def process(self):
        pass


class DoGroupID(IFilter):
    def filter_ids(self):
        nor_img, r18_img, nor_gif, r18_gif = [], [], [], []

        def extract_tag_(_html, _id):
            try:
                _gif_tag = etree.HTML(_html).xpath('//head/title/text()')[0]
                _r18_tag = etree.HTML(_html).xpath('//head/meta[@property="twitter:title"]/@content')[0]
                return _gif_tag, _r18_tag, _id
            except(IndexError, AttributeError):
                return '', '', ''

        def package(_gif_tag, _r18_tag, _id):
            if re.search(r'动图', _gif_tag):
                r18_gif.append(_id) if re.search(r'\[R-18]', _r18_tag) else nor_gif.append(_id)
            else:
                r18_img.append(_id) if re.search(r'\[R-18]', _r18_tag) else nor_img.append(_id)

        url_list = [f'https://www.pixiv.net/artworks/{_id}' for _id in self.id_list]
        html_list = Download.response(url_list)['html']
        for index in range(len(html_list)):
            html, _id = html_list[index], self.id_list[index]
            gif_tag, r18_tag, _id = extract_tag_(html, _id)
            package(gif_tag, r18_tag, _id)
        print()
        print(colour_str(f'[NOR]: [IMG]{len(nor_img)}, [GIF]{len(nor_gif)}', form=0, code=32))
        print(colour_str(f'[R18]: [IMG]{len(r18_img)}, [GIF]{len(r18_gif)}', form=0, code=32))
        return nor_img, r18_img, nor_gif, r18_gif


class DoParseIMG(IParse):
    def parse_ids(self):
        def yield_url(_url_list):
            resp_list = Download.response(_url_list)['json']
            for group, _src_url_html in enumerate(resp_list):
                _src_url_list = re.findall(r'https://i\.pximg\.net/img-original/img/.*?_p\d+\..{3}', str(_src_url_html))
                yield _src_url_list, self.id_list[group]

        def yield_data(_source_url_list):
            for _page, _img_url in enumerate(_source_url_list):
                _suffix = _source_url_list[_page][-3:]
                yield _suffix, _page

        url_list = [f'https://www.pixiv.net/ajax/illust/{_id}/pages?lang=zh' for _id in self.id_list]
        img_url_list, name_list = [], []
        for source_url_list, _id in yield_url(url_list):
            for suffix, page in yield_data(source_url_list):
                name_list.append(f'{_id}_p{page}.{suffix}')
            img_url_list += source_url_list
        img_bina_list = Download.response(img_url_list)['bina']
        return img_bina_list, name_list


class DoParseGIF(IParse):
    def parse_ids(self):
        def yield_url(_url_list):
            url_data_list = Download.response(_url_list)['html']
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
        gif_url_list, delay_list, name_list = [], [], []

        for zip_url, delay, _id in yield_url(_url_list):
            delay_list.append(delay)
            name_list.append(_id)
            gif_url_list += zip_url
        gif_bina_list = Download.response(gif_url_list)['bina']
        return gif_bina_list, delay_list, name_list


class DoStoreIMG(IStore):
    def store(self):
        async def write_in(img_data, img_name):
            async with aiofiles.open(f'./{self.file_name}/{img_name}', 'wb+') as f:
                await f.write(img_data)

        img_bina_list, name_list = self.download_infos
        ThreadLauncher(Async(write_in, (img_bina_list, name_list)))


class DoStoreGIF(IStore):
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

        gif_bina_list, delay_list, gif_name_list = self.download_infos
        load_all_zip(gif_bina_list, gif_name_list)
        flames_infos = unzip_all_img(gif_name_list)
        merge_all(flames_infos, delay_list)
