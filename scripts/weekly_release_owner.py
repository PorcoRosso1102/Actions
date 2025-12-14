
import requests
import json
from datetime import date, timedelta
import os


def send_msg_to_host(robot_url, email):
    msgtype = 'text'
    json = {
        "msgtype": msgtype,
        msgtype: {
            "content": "版本Release Owner",
            "mentioned_list": [email]
        }
    }
    requests.post(robot_url, json=json)


def send_msg_to_maintainer(robot_url):
    msgtype = 'text'
    json = {
        "msgtype": msgtype,
        msgtype: {
            "content": "❌❌❌ 发版机器人挂了",
            "mentioned_list": ["zhengchengzhao@xiaohongshu.com"]
        }
    }
    requests.post(robot_url, json=json)


def send_at_all_msg(robot_url, title):
    json = {
        "msgtype": "text",
        "text": {
            "content": title,
            "mentioned_mobile_list": ["@all"]
        }
    }
    requests.post(robot_url, json=json)


def increment_index():
    with open(json_path(), "r+") as f:
        data = json.load(f)

        # 每两次换一个人
        count = data['current_count']
        data['current_count'] = valid_count(count)

        index = data['current_index']
        hosts = data['hosts']
        data['current_index'] = valid_index(index, hosts, count)

        # unrelease_managers = data["unrelease_managers"]
        # unrelease_index = data["unrelease_index"]
        # data['unrelease_index'] = valid_index(unrelease_index, unrelease_managers)

        f.seek(0)
        json.dump(data, f)
        f.truncate()

def valid_count(count):
    return (count + 1) % 2

def valid_index(index, users, count):
    index = index % len(users)
    # 每两次 index+1
    if (count % 2 == 0):
        return (index) % len(users)
    else:
        return (index + 1) % len(users)


def json_path():
    return '.github/scripts/cache.json'


def card_data():
    result = {
        "host": {
            "name": "罗梭(郑成钊)",
            "email": "zhengchengzhao@xiaohongshu.com"
        }
    }
    with open(json_path(), "r") as f:
        data = json.load(f)

        hosts = data['hosts']
        index = data['current_index']
        result["host"] = current_user(hosts, index)

        unrelease_managers = data["unrelease_managers"]
        unrelease_index = data["unrelease_index"]
        result["unrelease_manager"] = current_user(unrelease_managers, unrelease_index)

        result["next_manager"] = current_user(unrelease_managers, unrelease_index + 1)

    return result


def current_user(users, index):
    valid_index = index % len(users)
    return users[valid_index]


def common_headers():
    return {
        'content-type': 'application/json',
        'cookie': cookie,
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'sec-fetch-site': 'same-origin',
        'accept': 'application/json, text/plain, */*',
        'authorization': authorization,
        'content-length': '117',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'macOS',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-b3-traceid': 'e888af0666364d76',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Host': 'docs.xiaohongshu.com',
    }


def copy_redoc():
    url = url_from("/docgateway/api/document/copy")
    main_headers = common_headers()
    origin_shortcut_id = os.environ.get('REDOC_ORIGIN_SHORTCUT_ID')
    params = {
        "originShortcutId": origin_shortcut_id
    }
    result = requests.post(url=url, data=json.dumps(
        params), headers=main_headers)
    print(result.status_code, " ======== status code")
    if result.status_code != 200:
        return None
    result = result.json()
    print(result, "======== result")
    data = result['data']
    print(data, "======== data")
    shortcutId = data['shortcutId']
    if shortcutId is None:
        return
    move_redoc(shortcutId)
    return url_from("/doc/") + shortcutId


def move_redoc(shortcutId):
    url = url_from("/docgateway/api/menu/moveShortcut")
    main_headers = common_headers()
    # 目标目录的id
    short_cut_id = os.environ.get('REDOC_SHORTCUT_ID')
    space_id = os.environ.get('REDOC_SPACE_ID')
    params = {
        "shortcutId": shortcutId,
        "toParentId": short_cut_id,
        "toSpaceId": space_id,
        "preShortcutId": ""
    }
    result = requests.post(url=url, data=json.dumps(
        params), headers=main_headers)
    if result.status_code != 200:
        return None
    return url_from("/doc/") + shortcutId


def url_from(path):
    domain = os.environ.get('REDOC_DOMAIN')
    return domain + path


def page_title():
    today = date.today()
    monday = today
    while monday.weekday() != 0:
        monday += timedelta(-1)
    friday = monday + timedelta(4)
    return str(monday).replace('-', '.') + "~" + str(friday).replace('-', '.')



def send_text_notice(robot_url, redoc_link, title):
    content = "### 周会\n {}\n\n  [周报链接]({})\n请各位同学及时填写周报".format(title, redoc_link)

    json = {
    "msgtype": "markdown",
    "markdown": {
        "content": content,
        "mentioned_list":["@all"]
        }
    }
    requests.post(robot_url, json=json)


def should_execute():
    """判断是否应该执行main函数"""
    with open(json_path(), "r+") as f:
        data = json.load(f)

        # 每两次执行一次
        cycle = data['week_cycle']
        data['week_cycle'] = valid_count(cycle)

        f.seek(0)
        json.dump(data, f)
        f.truncate()

    # 返回是否应该执行
    return cycle % 2 == 1


def redoc_creator_main():
    
    robot_url = robot_url = os.environ.get('ROBOT_URL')
    send_msg_to_maintainer(robot_url)

#    """判断是否应该执行, 每两周执行一次"""
#    # if not should_execute():
#    #     print("跳过本周执行")
#    #     return None
#    
#    global authorization
#    authorization = os.environ.get('REDOC_TOKEN')
#
#    global cookie
#    cookie = os.environ.get('REDOC_COOKIE')
#
#    robot_url = robot_url = os.environ.get('ROBOT_URL')
#
#    redoc_link = copy_redoc()
#    if redoc_link is None:
#        send_msg_to_maintainer(robot_url)
#    else:
#        # 发送周报链接至企业微信
#        title = page_title()
#        send_text_notice(robot_url, redoc_link, title)
#        increment_index()


if __name__ == "__main__":
    redoc_creator_main()
