import json
from abc import ABC, abstractmethod
import re
from Main import output
from Process.Request import Request


class FocusedMixin(ABC):
    @staticmethod
    def shrink(id_list, _source_limit):
        _source_limit = len(id_list) if len(id_list) < _source_limit else _source_limit
        id_list = id_list[:_source_limit]
        return id_list

    @abstractmethod
    def except_id(self, param, _source_limit):
        pass


class ExceptAuthorID(FocusedMixin):
    def except_id(self, param, _source_limit):
        url = [f'https://www.pixiv.net/ajax/user/{param}/profile/all?lang=zh']
        Request(url)
        id_list = re.findall(r"\d+", str(Request.resp_list['json'][0]['body']['illusts']))
        id_list = self.shrink(id_list, _source_limit)

        output(f'{_source_limit}', code=33, form=4, end='')
        return {'author id': param, 'id_list': id_list}


class FocusedExceptCaller:
    Result = []

    @classmethod
    def __init__(cls, param, _source_limit, except_mixin):
        cls.Result = []
        output(f'except ids({param}): ', form=1, code=31, end='')
        cls.Result = except_mixin.except_id(param, _source_limit)
        output(f'[finish]', form=4, code=32)


class IncrementMixin(ABC):
    @staticmethod
    def shrink(id_list, _source_limit):
        _source_limit = len(id_list) if len(id_list) < _source_limit else _source_limit
        id_list = id_list[:_source_limit]
        return id_list

    @abstractmethod
    def except_id(self, _source_limit):
        pass


class ExceptAuthorTrace(IncrementMixin):
    def except_id(self, _source_limit):
        update_list = []
        with open('./res/subscribe.json', 'r+') as f:
            _list = json.load(f)
        trace_list = [{
                'author_id': sub['author_id'], 'old_id': sub['artwork_id'],
                'new_ids': FocusedExceptCaller(sub['author_id'], _source_limit, ExceptAuthorID()).Result['id_list']
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

        for author_id, pending_id_list in yield_pending_ids(trace_list):
            if len(pending_id_list) != 0:
                update_list.append({'author_id': author_id, 'id_list': pending_id_list})

        for update in update_list:
            for sub in _list['subscribe']:
                if sub['author_id'] == update['author_id']:
                    sub['artwork_id'] = update['id_list'][0]
                    break
        with open('./res/subscribe.json', 'w+') as f:
            f.write(json.dumps(_list))

        return update_list


class ExceptRanking(IncrementMixin):
    def except_id(self, _source_limit):
        def yield_id_list(ranking_url_list):
            html_list = Request(ranking_url_list).resp_list['html']
            for html in html_list:
                _id_list = re.findall('"data-type=".*?"data-id="(.*?)"', html)
                for i in range(1, int(len(_id_list) / 2)):
                    _id_list.pop(i)
                _id_list = self.shrink(_id_list, _source_limit)
                output(f'{len(id_list)}', code=33, form=4, end='')
                yield _id_list

        url_list = ['https://www.pixiv.net/ranking.php?mode=daily',
                    'https://www.pixiv.net/ranking.php?mode=daily_r18']
        id_list = []
        for each_id_list in yield_id_list(url_list):
            id_list += each_id_list
        return id_list


class ExceptAuthorSub(IncrementMixin):
    def except_id(self, _source_limit):
        def yield_id_list(_page_limit):
            for page in range(_page_limit):
                url = [f'https://www.pixiv.net/ajax/follow_latest/illust?p={page}&mode=all&lang=zh']
                ids = Request(url).resp_list['json'][0]['body']['page']['ids']
                yield ids

        page_limit = int(_source_limit/60)
        id_list = [ids for ids in yield_id_list(page_limit)]
        id_list = self.shrink(id_list, _source_limit)
        output(f'{len(id_list)}', code=33, form=4, end='')
        return id_list


class IncrementExceptCaller:
    Result = []

    @classmethod
    def __init__(cls, _source_limit, except_mixin):
        cls.Result = []
        output(f'except ids: ', form=1, code=31, end='')
        cls.Result = except_mixin.except_id(_source_limit)
        output(f'[finish]', form=4, code=32)



