# -*- coding:utf-8 -*-
#!/usr/bin/env python3
import requests
import json
import os
import time
from transmission_rpc import Client

#change_torrent

TrackersListUrl = [
    'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt',
    'https://cdn.staticaly.com/gh/XIU2/TrackersListCollection/master/best.txt'
]

transmission_rpc_host='192.168.12.248'
transmission_rpc_username = '520xcy'
transmission_rpc_passwd = 'Xcy8444973'
transmission_rpc_port = 9091

Filter_List = [
    'htm', 'html', 'apk', 'url', '直播大秀平台', '网址', '地址', 'APP'
]


def update_trackersList():
    TrackersList_text = ''
    for x in TrackersListUrl:
        req = requests.get(x)
        TrackersList_text += req.text

    TrackersList = [x for x in TrackersList_text.splitlines() if len(x) > 1]

    trackersList_json = {
        'last_time': time.time(),
        'TrackersList': TrackersList
    }

    with open('tracker_list.json', 'w+') as f:
        # f.write(TrackersList_text)
        json.dump(trackersList_json, f)  #存储json文件
    return trackersList_json


def get_track_list():

    #判断文件是否存在
    json_exists = os.path.exists('tracker_list.json')
    trackersList_json = ''

    if json_exists:  #存在
        print('tracker_list.json 文件存在！')
        try:
            with open('tracker_list.json', 'r') as f:
                trackersList_json = json.load(f)  #读取文件

        except Exception as e:
            pass
    else:  #不存在
        print('tracker_list.json 文件不存在！')
        trackersList_json = update_trackersList()

    #计算是否更新本地trackerlist缓存
    if (time.time() - trackersList_json['last_time']
        ) / 3600 > 12:  #trackersList更新时间大于于12个小时

        trackersList_json = update_trackersList()

    return trackersList_json


def tracker_Add(client, torrent, trackersList):

    try:
        # client.change_torrent(torrent.id, trackerRemove=range(300)) #清空trackersList
        client.change_torrent(torrent.id, trackerAdd=trackersList)

        print(f'{torrent.id}-{torrent.name}:添加成功')
    except Exception as e:
        print(f'{torrent.id}-{torrent.name}:添加tracker出错！')

    # '''一个一个添加，以防整体添加时一个出错，后续的无法添加'''
    # for tl in trackersList:
    #     try:
    #         # client.change_torrent(torrent.id, trackerRemove=range(300)) #清空trackersList
    #         client.change_torrent(torrent.id, trackerAdd=[tl])

    #         print(f'{torrent.id}-{torrent.name}:添加tracker:{tl}')
    #     except Exception as e:
    #         print(f'{torrent.id}-{torrent.name}:添加tracker出错！ {tl}')


def tracker_Clean(client, torrent):
    try:
        client.change_torrent(torrent.id,
                              trackerRemove=range(300))  #清空trackersList

        print(f'{torrent.id}-{torrent.name}:清空trackersList!')
    except Exception as e:
        print(f'{torrent.id}-{torrent.name}:清空trackersList出错!')


def filter_file(client, torrent):
    '''过滤垃圾文件'''
    #过滤文件
    unwant_list = []
    for file_id, file in enumerate(torrent.files()):
        for f_s in Filter_List:
            # print(f'{file_id}-{file.name}:{str(file.name).find(f_s)}')
            if str(file.name).find(f_s) > -1:
                unwant_list.append(file_id)
                break
                # print(f'不下载：{file.name}')

    if len(unwant_list) > 0:
        client.change_torrent(torrent.id, files_unwanted=unwant_list)
        print(f'{torrent.id}-{torrent.name}:过滤垃圾文件！')
    else:
        print(f'{torrent.id}-{torrent.name}:没有需要过滤的垃圾文件！')
    unwant_list = []


def torrent_add_trackers():
    trackersList_json = get_track_list()
    trackersList = trackersList_json['TrackersList']
    # print(trackersList)
    client = Client(host=transmission_rpc_host,
                    port=transmission_rpc_port,
                    username=transmission_rpc_username,
                    password=transmission_rpc_passwd)
    torrents = client.get_torrents()
    for t in torrents:
        
        tracker_Clean(client,t) # tracker clean

        
        tracker_Add(client, t, trackersList) ## trackerAdd
        filter_file(client, t)#过滤垃圾文件


if __name__ == "__main__":
    torrent_add_trackers()