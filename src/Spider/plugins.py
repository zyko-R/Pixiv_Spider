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
        pending_list = [{
                'author_id': sub['author_id'], 'old_id': sub['artwork_id'],
                'new_ids': FocusedExceptCaller(sub['author_id'], _source_limit, ExceptAuthorID()).Result['id_list']
             } for sub in _list['subscribe']
        ]
        for pending in pending_list:
            id_list = []
            for new_id in pending['new_ids']:
                if new_id == pending['old_id']:
                    break
                id_list.append(new_id)
            if len(id_list) != 0:
                update_list.append({'author_id': pending['author_id'], 'id_list': id_list})
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
        def parser(html):
            _id_list = re.findall('"data-type=".*?"data-id="(.*?)"', html)
            for i in range(1, int(len(_id_list) / 2)):
                _id_list.pop(i)
            _id_list = self.shrink(_id_list, _source_limit)
            return _id_list

        url = ['https://www.pixiv.net/ranking.php?mode=daily', 'https://www.pixiv.net/ranking.php?mode=daily_r18']
        nor_id_list = parser(Request(url).resp_list['html'][0])
        r18_id_list = parser(Request(url).resp_list['html'][1])
        id_list = nor_id_list + r18_id_list
        output(f'{len(id_list)}', code=33, form=4, end='')
        return id_list


class ExceptAuthorSub(IncrementMixin):
    def except_id(self, _source_limit):
        id_list = []
        page = 0
        while len(id_list) < _source_limit:
            page += 1
            url = [f'https://www.pixiv.net/ajax/follow_latest/illust?p={page}&mode=all&lang=zh']
            id_list += Request(url).resp_list['json'][0]['body']['page']['ids']
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



