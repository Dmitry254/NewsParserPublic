import requests
import traceback

from pprint import pprint
from keys import twitter_bearer_token


def create_headers(twitter_bearer_token):
    headers = {"Authorization": f"Bearer {twitter_bearer_token}"}
    return headers


def create_url(keyword, start_date, end_date, max_results=10):

    search_url = "https://api.twitter.com/2/tweets/search/all" #Change to the endpoint you want to collect data from

    #change params based on the endpoint you are using
    query_params = {'query': keyword,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': max_results,
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
    return (search_url, query_params)


def connect_to_endpoint(url, headers, params, next_token=None):
    params['next_token'] = next_token   #params object received from create_url function
    response = requests.request("GET", url, headers=headers, params=params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


if __name__ == "__main__":
    headers = create_headers(twitter_bearer_token)
    keyword = ""
    start_time = ""
    end_time = ""
    max_results = 15

    search_url, query_params = create_url(keyword, start_time, end_time, max_results)
    response = connect_to_endpoint(search_url, headers, query_params)
    print(response)

    channel_id = ""
    group_name = ""