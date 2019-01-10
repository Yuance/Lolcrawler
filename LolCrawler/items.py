# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class Match(Item):

    seasonId = Field()
    queueId = Field()
    gameId = Field()
    participantIdentities = Field()
    gameVersion = Field()
    platformId = Field()
    gameMode = Field()
    mapId = Field()
    gameType = Field()
    teams = Field()
    participants = Field()
    gameDuration = Field()
    gameCreation = Field()
