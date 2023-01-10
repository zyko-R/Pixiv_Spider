from ExceptID.Primary import *


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


def get_info(author_info):
    if re.match("^[0-9]*$", author_info) is not None:
        author_name = SecondINFOCaller(author_info, SecondINFOAuthorName()).Result
        author_id = author_info
    else:
        author_id = SecondINFOCaller(author_info, SecondINFOAuthorID()).Result
        author_name = author_info
    return author_name, author_id