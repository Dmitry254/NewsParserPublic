import time

import requests
import traceback

from pprint import pprint
from base_func import vk_auth, get_video_player
from database_test import create_connection, add_post_data
from utils import *


def get_post_by_id(vk_bot, owner_id, post_id):
    posts = vk_bot.method("wall.getById", {"posts": f"{owner_id}_{post_id}"})
    pprint(posts[0])


def get_posts(vk_bot, group_id):
    posts = vk_bot.method("wall.get", {"owner_id": group_id, "offset": offset_id, "count": limit, "filter": "owner"})
    print(posts)
    for post in posts['items']:
        time_post, link_post, views_post, text_post, photos, webpages, documents, videos, audios, \
        name_source, link_source, repost_text = get_data_from_post(post)
        post_data = [target_group, time_post, link_post, views_post, text_post, photos, webpages, documents, videos, audios,
                     name_source, link_source, repost_text]
        # add_post_data(connection, post_data)
        # print(post_data)


def get_data_from_post(post_data):
    print("---------------------------------")
    link_post = text_post = name_source = link_source = ""
    time_post = 0
    views_post = -1
    photos = ""
    webpages = ""
    documents = ""
    videos = ""
    audios = ""
    repost_text = ""
    try:
        # pprint(post_data)
        link_post = f"https://vk.com/{group_name}?w=wall{target_group}_{post_data['id']}"

        time_post = post_data['date']

        text_post = post_data['text']

        views_post = post_data['views']['count']
        print(views_post)

        if "attachments" in post_data.keys():
            photos, webpages, documents, videos, audios = get_attachments(post_data, photos, webpages, documents, videos, audios)

        if "copy_history" in post_data.keys():
            for copy_history in post_data['copy_history']:
                if "attachments" in copy_history.keys():
                    photos = photos + separate_repost_tag
                    webpages = webpages + separate_repost_tag
                    documents = documents + separate_repost_tag
                    videos = videos + separate_repost_tag
                    audios = audios + separate_repost_tag
                    photos, webpages, documents, videos, audios = get_attachments(copy_history, photos, webpages, documents, videos, audios)

                name_source = copy_history['from_id']
                link_source = f"https://vk.com/club{abs(copy_history['from_id'])}"
                repost_text = copy_history['text']

    except KeyError:
        traceback.print_exc()
    except TypeError:
        traceback.print_exc()

    return time_post, link_post, views_post, text_post, photos, webpages, documents, videos, audios, \
           name_source, link_source, repost_text


def get_attachments(post_data, photos, webpages, documents, videos, audios):
    for media in post_data['attachments']:

        if media['type'] == "photo":
            photo_name = str(media['photo']['id'])
            photo_url, photo_size = search_best_quality(media['photo']['sizes'])
            if photo_size < max_size:
                download_photo(photo_url, photo_name)
                print("Скачано фото " + photo_name)
                photos = photos + photo_name + separate_elements_tag
            else:
                photos = photos + photo_url + separate_elements_tag

        if media['type'] == "video":
            videos = videos + get_video_player(vk_client_bot, media['video']['owner_id'], media['video']['id'], media['video']['access_key']) + separate_elements_tag

        if media['type'] == "doc":
            doc_name = str(media['doc']['id'])
            doc_size = media['doc']['size']
            doc_url = media['doc']['url']
            doc_type = media['doc']['ext']
            if doc_size < max_size:
                download_doc(doc_url, doc_name, doc_type)
                print("Скачан документ " + doc_name)
                documents = documents + doc_name + separate_parts_tag
                documents = documents + doc_type + separate_elements_tag
            else:
                documents = documents + doc_url + separate_parts_tag
                documents = documents + doc_type + separate_elements_tag

        if media['type'] == "link":
            webpage_url = media['link']['url']
            webpage_title = media['link']['title']
            webpage_preview = ""
            webpages = webpages + webpage_url + separate_parts_tag
            webpages = webpages + webpage_title + separate_parts_tag
            if "photo" in media['link']:
                link_preview_name = str(media['link']['photo']['id'])
                link_preview_url, link_preview_size = search_best_quality(media['link']['photo']['sizes'])
                if link_preview_size < max_size:
                    download_photo(link_preview_url, link_preview_name)
                    print("Скачано превью " + link_preview_name)
                    webpage_preview = link_preview_name
                else:
                    webpage_preview = link_preview_url
            webpages = webpages + webpage_preview + separate_elements_tag

        if media['type'] == "audio":
            audios = audios + f"{media['audio']['title']}\n{media['audio']['artist']}" + separate_elements_tag
    return photos, webpages, documents, videos, audios


def search_best_quality(file_sizes):
    best_file_size = 0
    best_file_url = ""
    for file in file_sizes:
        file_size = file['height'] * file['width']
        if file_size > best_file_size:
            best_file_size = file_size
            best_file_url = file['url']
    return best_file_url, best_file_size


def download_photo(photo_url, photo_name):
    p = requests.get(photo_url)
    out = open(f"media\\vk\\{photo_name}.jpg", "wb")
    out.write(p.content)
    out.close()


def download_doc(doc_url, doc_name, doc_type):
    p = requests.get(doc_url)
    out = open(f"media\\vk\\{doc_name}.{doc_type}", "wb")
    out.write(p.content)
    out.close()


if __name__ == "__main__":
    max_size = 11000
    offset_id = 0
    limit = 200

    vk_bot, vk_client_bot = vk_auth()

    target_group = 0
    group_name = ""

    # connection = create_connection()
    # get_post_by_id(vk_bot, target_group, 24899)
    get_posts(vk_bot, target_group)
