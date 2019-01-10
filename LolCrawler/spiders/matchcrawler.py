import scrapy
import json
import time
from LolCrawler.loader import itemloader as it

class matchcrawler(scrapy.Spider):

    APIkey = "RGAPI-0c7b8d0e-592e-4880-bbd4-a8a70c5f725e"
    matchAPI = "https://na1.api.riotgames.com/lol/match/v3/matches/"
    playerAPI = "https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/"

    unexplored_player_list = []
    end_Index = 1
    max_degree = 2
    degree = 0

    name = "MatchCrawler"
    allowed_domains = ["na1.api.riotgames.com"]
    start_urls = ['https://na1.api.riotgames.com/lol/match/v3/matches/2585565772?api_key={}'.format(APIkey)]

    def parse(self, response):

        '''main match parser, and trace this match's players'''
        match = it.parse_match_body(self, response.body)
        print("MatchID: {}".format(match['gameId']))

        print("Enter players of this match")
        '''trace players of a match'''

        while self.unexplored_player_list:

            player_id = self.unexplored_player_list.pop()
            print("For Player: %s", player_id)
            time.sleep(1)
            api_request = self.playerAPI + str(player_id) + "?endIndex={}".format(self.end_Index) + "&api_key={}".format(self.APIkey)

            yield scrapy.Request(api_request, callback=self.parse_player)


    def parse_player(self, response):

        '''call player api and parse the result using scrapy HTTP Requests'''
        match_list = json.loads(response.body)
        print(match_list)
        match_list = match_list['matches']

        print("Matches: ")
        for match in match_list:

            match_id = match['gameId']
            print(match_id)
            time.sleep(1)
            api_request = self.matchAPI + str(match_id) + "?api_key={}".format(self.APIkey)
            yield scrapy.Request(api_request, callback=self.parse)

        self.degree += 1
        if self.degree == self.max_degree:
            print("Degree Reached... Player list clear..")
            self.unexplored_player_list = []












