import json
import scrapy
import requests

def parse_match_body(spider, response_body):

    # parse response_body binary stream
    match = json.loads(response_body)
    player_list = match['participantIdentities']

    for item in player_list:

        player_id = item['player']['accountId']

        if player_id not in spider.unexplored_player_list:
            spider.unexplored_player_list.append(player_id)

    return match


def get_match_list_by_player_id(spider, player_id):

    api_request = spider.playerAPI + str(player_id) + "?api_key={}".format(spider.APIkey)

    yield scrapy.Request(api_request, callback=spider.parse_player)

