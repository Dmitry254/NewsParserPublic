import time
import traceback

from telethon.sync import TelegramClient

from telethon.tl.functions.messages import GetHistoryRequest

from telethon.errors.rpcerrorlist import ChannelPrivateError

from keys import tg_api_id, tg_api_hash
from database_test import create_connection, add_post_data
from pprint import pprint
from utils import *


def parse_posts(client, channel_id):
    channel = client.get_entity(channel_id)
    print(channel)
    history = client(GetHistoryRequest(
        peer=channel,
        offset_id=offset_id,
        offset_date=None,
        add_offset=0,
        limit=limit,
        max_id=0,
        min_id=0,
        hash=0
    ))
    # post = history.messages[target_post]
    # get_data_from_post(client, post)
    group_list = [None, -1, '', -1, '', [], [], '', '', [], [], [], [], [], '', '']
    print(history)
    for message in history.messages:
        try:
            post_data = message.to_dict()
            if post_data['_'] != "MessageService":
                grouped_id, time_post, link_post, views_post, text_post, photos, webpages, documents, videos, audios, \
                name_source, link_source, repost_text = get_data_from_post(client, message)
                print(group_list[0], grouped_id)
                if group_list[0] != grouped_id:
                    if group_list[0] is not None:
                        post_data = [group_name, group_list[1], group_list[2], group_list[3], group_list[4], group_list[5],
                                     group_list[6], group_list[7], group_list[8], group_list[9], group_list[10],
                                     group_list[11], group_list[12]]
                        print(post_data)
                        # add_post_data(connection, post_data)
                        if grouped_id is not None:
                            group_list = [grouped_id, time_post, link_post, views_post, text_post, photos, webpages, documents, videos, audios,
                                          name_source, link_source, repost_text]
                        else:
                            post_data = [group_name, time_post, link_post, views_post, text_post, photos, webpages, documents, videos, audios,
                                        name_source, link_source, repost_text]
                            print(post_data)
                            # add_post_data(connection, post_data)
                            group_list = [None, -1, '', -1, '', [], [], '', '', [], [], [], [], [], '', '']
                    else:
                        group_list = [grouped_id, time_post, link_post, views_post, text_post, photos, webpages, documents, videos, audios,
                                      name_source, link_source, repost_text]
                else:
                    if grouped_id is None:
                        post_data = [group_name, time_post, link_post, views_post, text_post, photos, webpages, documents, videos, audios,
                                     name_source, link_source, repost_text]
                        print(post_data)
                        # add_post_data(connection, post_data)
                    else:
                        print(photos)
                        if group_list[1] > time_post:
                            group_list[1] = time_post
                        if group_list[3] < views_post:
                            group_list[3] = views_post
                        if len(group_list[4]) < len(text_post):
                            group_list[4] = text_post
                        if photos:
                            group_list[5] = group_list[5] + photos
                        if webpages:
                            group_list[6] = group_list[6] + webpages
                        if documents:
                            group_list[7] = group_list[7] + documents
                        if videos:
                            group_list[8] = group_list[8] + videos
                        if audios:
                            group_list[9] = group_list[9] + audios
                        if len(group_list[10]) < len(name_source):
                            group_list[10] = name_source
                        if len(group_list[11]) < len(link_source):
                            group_list[11] = link_source
                        if message == history.messages[-1]:
                            post_data = [group_name, group_list[1], group_list[2], group_list[3], group_list[4], group_list[5],
                                         group_list[6], group_list[7], group_list[8], group_list[9], group_list[10],
                                         group_list[11], group_list[12]]
                            print(post_data)
                            # add_post_data(connection, post_data)
        except:
            traceback.print_exc()
            continue


def get_data_from_post(client, post):
    print("---------------------------------")
    link_post = text_post = name_source = link_source = ""
    grouped_id = None
    time_post = 0
    views_post = -1
    photos = ""
    webpages = ""
    documents = ""
    videos = ""
    audios = ""
    repost_text = ""
    try:
        post_data = post.to_dict()
        pprint(post_data)

        link_post = f"https://t.me/{group_name}/{post_data['id']}"

        time_post = int(post_data['date'].timestamp())

        if "message" in post_data.keys():
            text_post = post_data['message']

        views_post = post_data['views']
        print(views_post)

        if post_data['grouped_id']:
            grouped_id = post_data['grouped_id']

        if post_data['media']:
            media_in_post = post_data['media'].keys()

            if "photo" in media_in_post:
                photo = post_data['media']['photo']
                photo_name = str(photo['id'])
                try:
                    size = photo['sizes'][-1]['sizes'][-1]
                except:
                    size = 12000000
                if size < max_size:
                    download_media(client, post, photo_name)
                    print("Скачано фото " + photo_name)
                    photos = photos + photo_name + separate_elements_tag
                else:
                    photos = photos + "Fail" + separate_elements_tag

            if "webpage" in media_in_post:
                webpage = post_data['media']['webpage']
                webpage_url = webpage['url']
                webpage_title = webpage['title']
                webpage_preview = ""
                webpages = webpages + webpage_url + separate_parts_tag
                webpages = webpages + webpage_title + separate_parts_tag
                if "photo" in webpage.keys():
                    try:
                        size = webpage['photo']['sizes'][-1]['sizes'][-1]
                    except:
                        size = 12000000
                    if size < max_size:
                        webpage_preview = f"{webpage['photo']['id']}"
                        download_media(client, post, webpage_preview)
                        print("Скачано фото " + webpage_preview)
                webpages = webpages + webpage_preview + separate_elements_tag
                print(webpages)

            if "document" in media_in_post:
                document = post_data['media']['document']
                download_name = str(document['id'])
                try:
                    size = document['size']

                    if "video" in document['mime_type']:
                        if size < max_size:
                            download_media(client, post, download_name)
                            print("Скачано видео " + download_name)
                            videos = videos + download_name + separate_elements_tag
                        else:
                            videos = videos + "Fail" + separate_elements_tag

                    if "audio" in document['mime_type']:
                        if size < max_size:
                            download_media(client, post, download_name)
                            print("Скачано аудио " + download_name)
                            audios = audios + download_name + separate_elements_tag
                        else:
                            audios = audios + "Fail" + separate_elements_tag

                except:

                    if "video" in document['mime_type']:
                        videos = videos + "Fail" + separate_elements_tag

                    if "audio" in document['mime_type']:
                        audios = audios + "Fail" + separate_elements_tag
                    print(videos)
                    print(audios)

        if post_data['fwd_from']:
            fwd_from_post = post_data['fwd_from']
            if fwd_from_post['from_id'] is not None:
                fwd_channel_id = fwd_from_post['from_id']['channel_id']
                try:
                    fwd_channel_info = client.get_entity(fwd_channel_id).to_dict()
                    name_source = fwd_channel_info['title']
                    link_source = f"https://t.me/{fwd_channel_info['username']}"
                except ChannelPrivateError:
                    name_source = "Приватный канал"
                    link_source = ""
            else:
                name_source = "Приватный канал"
                link_source = ""
            print(name_source, link_source)

    except KeyError:
        traceback.print_exc()
    except TypeError:
        traceback.print_exc()

    return grouped_id, time_post, link_post, views_post, text_post, photos, webpages, documents, videos, audios, \
           name_source, link_source, repost_text


def download_media(client, message, file_name):
    file_path = f"media\\telegram\\{file_name}"
    try:
        client.download_media(message, file_path)
        return True
    except:
        traceback.print_exc()
        return False


if __name__ == "__main__":
    max_size = 11000

    offset_id = 2485
    limit = 200
    total_messages = 0
    total_count_limit = 0

    target_post = 9

    group_name = ""

    # connection = create_connection()
    with TelegramClient('', tg_api_id, tg_api_hash) as client:
        parse_posts(client, group_name)

    # connection.close()
