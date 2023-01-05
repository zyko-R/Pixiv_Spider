import re
import json
import urllib3
from lxml import etree
import nest_asyncio
from Main import *
from Pipeline import Pipeline
from Request import Request

urllib3.disable_warnings()
nest_asyncio.apply()


class Parser:
    class Ex:
        IMG_FORM = 'IMG'
        GIF_FORM = "GIF"

        @staticmethod
        def download_proxy(_id_list, form, file_name):
            if len(_id_list) != 0:
                if form == Parser.Ex.IMG_FORM:
                    _download_infos = Parser.Ex.package_img(_id_list)
                    Pipeline.process_img(_download_infos, file_name)
                else:
                    _download_infos = Parser.Ex.package_gif(_id_list)
                    Pipeline.process_gif(_download_infos, file_name)
            else:
                pass

        @staticmethod
        def package_img(_id_list):
            output(f'expect IMG: ', form=1, code=31, end='')
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

            output(f'[finish]', form=4, code=32)
            return download_infos

        @staticmethod
        def package_gif(_id_list):
            output(f'expect GIF: ', form=1, code=31, end='')
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

            output(f'[finish]', form=4, code=32)
            return download_infos

    @staticmethod
    def except_ids(author_id, source_limit):
        url = f'https://www.pixiv.net/ajax/user/{author_id}/profile/all?lang=zh'
        Request([url])
        id_list = re.findall(r"\d+", str(Request.resp_list['json'][0]['body']['illusts']))
        source_limit = len(id_list) if len(id_list) < source_limit else source_limit
        id_list = id_list[:source_limit]
        output('except id: ', code=31, form=1, end='')
        output(f'{source_limit}', code=33, form=4, end='')
        output(f'[finish]', form=4, code=32)
        return id_list

    @staticmethod
    def group_ids(id_list):
        output('grouping ids: ', form=1, code=31, end='')
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
        output(f'[finish]', form=4, code=32)
        return ids_normal, ids_r18

    @staticmethod
    def except_author_info(author_info) -> ():
        if re.match("^[0-9]*$", author_info) is not None:
            author_id = author_info
            url = f'https://www.pixiv.net/users/{author_id}'
            Request([url])
            html = Request.resp_list['html'][0]
            name_data = etree.HTML(html).xpath('//head/title/text()')[0]
            author_name = re.findall('(.*?) - pixiv', name_data)[0]
        else:
            author_name = author_info
            url = f'https://www.pixiv.net/search_user.php?nick={author_name}&s_mode=s_usr'
            Request([url])
            html = Request.resp_list['html'][0]
            id_data = etree.HTML(html).xpath('//h1/a[@target="_blank"][@class="title"]/@href')
            author_id = re.findall(r'\w+/(\d+)', id_data)[0]
        return author_name, author_id


