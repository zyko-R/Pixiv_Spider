from abc import ABC, abstractmethod
import re
from Main import output
from Except.Secondary import *
from Request import Request


class ArtworkIDMixin(ABC):
    @abstractmethod
    def __init__(self, source_limit):
        self.source_limit = source_limit

    @abstractmethod
    def except_id(self):
        pass


class ByAuthorID(ArtworkIDMixin):
    def __init__(self, source_limit):
        self.source_limit = source_limit
        self.author_info = str(input('Enter Author(ID/Name)>? '))

    def except_id(self):
        author_name, author_id = get_info(self.author_info)
        url = [f'https://www.pixiv.net/ajax/user/{author_id}/profile/all?lang=zh']
        Request(url)
        id_list = re.findall(r"\d+", str(Request.resp_list['json'][0]['body']['illusts']))
        return author_name, id_list


class ByArtworkID(ArtworkIDMixin):
    def __init__(self, source_limit):
        self.source_limit = source_limit * 2
        self.artwork_id = str(input('Enter ArtworkID>? '))

    def except_id(self):
        url = [f'https://www.pixiv.net/ajax/illust/{self.artwork_id}/recommend/init?limit={self.source_limit}&lang=zh']
        artwork__list = Request(url).resp_list['json'][0]['body']['illusts']
        id_list = []
        for artwork in artwork__list:
            if 'id' in artwork:
                id_list.append(artwork['id'])
        return self.artwork_id, id_list


class ByTrace(ArtworkIDMixin):
    def except_id(self):
        def artwork_except(artwork_id, source_limit):
            url = [
                f'https://www.pixiv.net/ajax/illust/{artwork_id}/recommend/init?limit={source_limit}&lang=zh']
            Request(url)
            author_artwork_id_list = re.findall(r"\d+", str(Request.resp_list['json'][0]['body']['illusts']))
            return author_artwork_id_list

        id_list = []
        with open('./res/subscribe.json', 'r+') as f:
            _list = json.load(f)
        trace_list = [{
                'author_id': sub['author_id'], 'old_id': sub['artwork_id'],
                'new_ids': artwork_except(sub['artwork_id'], self.source_limit)
             } for sub in _list['subscribe']
        ]

        def yield_pending_ids(_trace_list):
            _pending_id_list = []
            for _trace in _trace_list:
                for new_id in _trace['new_ids']:
                    if new_id == _trace['old_id']:
                        break
                    _pending_id_list.append(new_id)
                _author_id = _trace['author_id']
                yield _author_id, _pending_id_list

        update_list = []
        for author_id, pending_id_list in yield_pending_ids(trace_list):
            if len(pending_id_list) != 0:
                id_list += pending_id_list
                update_list.append({'author_id': author_id, 'id': pending_id_list[0]})

        for update in update_list:
            for sub in _list['subscribe']:
                if sub['author_id'] == update['author_id']:
                    sub['artwork_id'] = update['id']
                    break
        with open('./res/subscribe.json', 'w+') as f:
            f.write(json.dumps(_list))
        return 'Update', id_list


class ByRanking(ArtworkIDMixin):
    def __init__(self, source_limit):
        self.source_limit = source_limit/2

    def except_id(self):
        def yield_id_list(ranking_url_list):
            html_list = Request(ranking_url_list).resp_list['html']
            for html in html_list:
                _id_list = re.findall('"data-type=".*?"data-id="(.*?)"', html)
                for i in range(1, int(len(_id_list) / 2)):
                    _id_list.pop(i)
                yield _id_list

        url_list = ['https://www.pixiv.net/ranking.php?mode=daily',
                    'https://www.pixiv.net/ranking.php?mode=daily_r18']
        id_list = []
        for each_id_list in yield_id_list(url_list):
            id_list += each_id_list
        return 'Ranking', id_list


class BySub(ArtworkIDMixin):
    def __init__(self, source_limit):
        self.source_limit = source_limit

    def except_id(self):
        def yield_id_list(_page_limit):
            for page in range(_page_limit):
                url = [f'https://www.pixiv.net/ajax/follow_latest/illust?p={page}&mode=all&lang=zh']
                ids = Request(url).resp_list['json'][0]['body']['page']['ids']
                yield ids

        page_limit = int(self.source_limit/60)
        id_list = [ids for ids in yield_id_list(page_limit)]
        return 'Sub', id_list


class PluginPackage:
    @staticmethod
    def shrink(id_list, _source_limit):
        _source_limit = len(id_list) if len(id_list) < _source_limit else _source_limit
        id_list = id_list[:_source_limit]
        return id_list

    def __init__(self, artwork_id_mixin):
        self.artwork_id_mixin = artwork_id_mixin

    def run(self):
        source_limit = int(input('How many artworks do you want >? '))
        plugin = self.artwork_id_mixin(source_limit)
        output(f'except ids: ', form=1, code=31, end='')
        file_name,  id_list = plugin.except_id()
        id_list = self.shrink(id_list, source_limit)
        output(f'{len(id_list)}', code=33, form=4, end='')
        output(f'[finish]', form=4, code=32)
        return file_name,  id_list


