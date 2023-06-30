import tweepy
import requests
import traceback

from datetime import datetime
from pprint import pprint
from keys import twitter_api_key, twitter_api_key_secret, twitter_bearer_token, twitter_access_token, twitter_access_token_secret
from database_test import create_connection, add_post_data
from utils import *


def get_posts():
    tweets = api.user_timeline(screen_name=user_name, tweet_mode='extended', count=limit, max_id=max_id)
    for tweet in tweets:
        print(tweet.id)
        tweet_data = tweet._json
        time_post, link_post, views_post, text_post, photos, webpages, documents, videos, audios, \
        name_source, link_source, repost_text = get_data_from_post(tweet_data)
        post_data = [user_name, time_post, link_post, views_post, text_post, photos, webpages, documents, videos, audios,
                     name_source, link_source, repost_text]
        # add_post_data(connection, post_data)
        print(post_data)


def get_data_from_post(tweet_data):
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
        id_tweet = tweet_data['id']
        link_post = f"https://twitter.com/{user_name}/status/{id_tweet}"

        time_post = int(datetime.strptime(tweet_data['created_at'], '%a %b %d %X +0000 %Y').timestamp())

        text_post = tweet_data['full_text']

        # views_post = tweet_data['text']

        pprint(tweet_data)

        photos, webpages, documents, videos, audios = get_attachments(tweet_data, photos, webpages, documents, videos, audios)

        if "retweeted_status" in tweet_data.keys():
            photos = photos + separate_repost_tag
            webpages = webpages + separate_repost_tag
            documents = documents + separate_repost_tag
            videos = videos + separate_repost_tag
            audios = audios + separate_repost_tag
            photos, webpages, documents, videos, audios = get_attachments(tweet_data['retweeted_status'], photos, webpages, documents, videos, audios)

            repost_text = tweet_data['retweeted_status']['full_text']
            name_source = tweet_data['retweeted_status']['user']['name']
            link_source = f"https://twitter.com/{name_source}"

    except KeyError:
        traceback.print_exc()
    except TypeError:
        traceback.print_exc()

    return time_post, link_post, views_post, text_post, photos, webpages, documents, videos, audios, \
           name_source, link_source, repost_text


def get_attachments(post_data, photos, webpages, documents, videos, audios):
    if 'extended_entities' in post_data.keys():
        media_types = post_data['extended_entities'].keys()
        if "media" in media_types:
            medias = post_data['extended_entities']['media']
            # print(medias)
            for media in medias:

                if media['type'] == "photo":
                    photo_name = str(media['id'])
                    photo_url = media['media_url']
                    photo_size = search_best_quality_photo(media['sizes'])
                    if photo_size < max_size:
                        download_photo(photo_url, photo_name)
                        print("Скачано фото " + photo_name)
                        photos = photos + photo_name + separate_elements_tag
                    else:
                        photos = photos + photo_url + separate_elements_tag

                if media['type'] == "video":
                    videos = videos + search_best_quality(media['video_info']['variants'])

                if media['type'] == "animated_gif":
                    if "video" in media['video_info']['variants'][-1]['content_type']:
                        gif_url = search_best_quality(media['video_info']['variants'])
                        documents = documents + gif_url + separate_parts_tag
                        documents = documents + separate_elements_tag
                        print(f"Добавлена гифка {gif_url}")
                    else:
                        gif_name = str(media['id'])
                        gif_url = media['video_info']['variants'][0]['url']
                        gif_size = search_best_quality_photo(media['sizes'])
                        gif_type = "mp4"
                        if gif_size < max_size:
                            download_doc(gif_url, gif_name, gif_type)
                            print("Скачана гифка " + gif_name)
                            documents = documents + gif_name + separate_parts_tag
                            documents = documents + gif_type + separate_elements_tag
                        else:
                            print("Добавлена гифка " + gif_url)
                            documents = documents + gif_url + separate_parts_tag
                            documents = documents + gif_type + separate_elements_tag

    if 'entities' in post_data.keys():
        media_types = post_data['entities'].keys()
        medias = post_data['entities']

        if "urls" in media_types:
            for media in medias['urls']:
                webpage_url = media['expanded_url']
                webpage_title = media['display_url']
                webpages = webpages + webpage_url + separate_parts_tag
                webpages = webpages + webpage_title + separate_parts_tag
                webpages = webpages + separate_elements_tag
    return photos, webpages, documents, videos, audios


def search_best_quality_photo(file_sizes):
    best_file_size = 0
    for file in file_sizes:
        file_size = file_sizes[file]['w'] * file_sizes[file]['h']
        if best_file_size < file_size:
            best_file_size = file_size
    return best_file_size


def search_best_quality(variants):
    best_file_size = -1
    best_file_url = ""
    for variant in variants:
        if "bitrate" in variant.keys():
            file_size = variant['bitrate']
            if file_size > best_file_size:
                best_file_size = file_size
                best_file_url = variant['url']
    return best_file_url


def download_photo(photo_url, photo_name):
    p = requests.get(photo_url)
    out = open(f"media\\twitter\\{photo_name}.jpg", "wb")
    out.write(p.content)
    out.close()


def download_doc(doc_url, doc_name, doc_type):
    p = requests.get(doc_url)
    out = open(f"media\\twitter\\{doc_name}.{doc_type}", "wb")
    out.write(p.content)
    out.close()


if __name__ == "__main__":
    max_size = 11000

    user_name = ''
    max_id = 0
    limit = 50

    auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_key_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    api = tweepy.API(auth)

    connection = create_connection()

    get_posts()
