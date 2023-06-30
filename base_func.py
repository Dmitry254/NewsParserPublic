import vk_api
import random
import time
import requests
import json

from keys import vk_api_service_key, vk_api_client_key
from datetime import datetime, timedelta


def vk_auth():
    vk_bot = vk_api.VkApi(token=vk_api_service_key)
    vk_bot._auth_token()
    vk_bot.get_api()

    vk_client_bot = vk_api.VkApi(token=vk_api_client_key)
    vk_client_bot._auth_token()
    vk_client_bot.get_api()

    return vk_bot, vk_client_bot


def get_video_player(vk_client_bot, owner_id, video_id, access_key):
    video = vk_client_bot.method("video.get", {"owner_id": owner_id, "videos": f"{owner_id}_{video_id}_{access_key}"})
    return video['items'][0]['player']
