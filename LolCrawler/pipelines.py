# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import time
from scrapy.exceptions import DropItem
from LolCrawler.items import Match


class MySQLPipeline(object):

    def __init__(self, host, db, user, passwd):
        self.host = host
        self.db = db
        self.user = user
        self.passwd = passwd

    @classmethod
    def from_crawler(cls, crawler):

        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            db=crawler.settings.get('MYSQL_DBNAME'),
            user=crawler.settings.get('MYSQL_USER'),
            passwd=crawler.settings.get('MYSQL_PASSWD')
        )

    # def open_spider(self):
    #
    # def close_spider(self):

    # try:
    #     spider.connection = pymysql.connect(
    #         host=self.host,
    #         db=self.db,
    #         user=self.user,
    #         password=self.passwd,
    #         charset='utf8mb4',
    #         use_unicode=True)
    #
    #     with spider.connection.cursor() as cursor:
    #         cursor.execute(
    #             """select * from mainlist where title = %s and author = %s""",
    #             (item["title"],
    #              item["author"]
    #              ))
    #
    #         ret = cursor.fetchone()
    #         # if have same title and author in database already then pass
    #         if ret:
    #
    #             spider.my_logger.info("Already Exist in Database: {}".format(ret[0]))
    #             pass
    #
    #         else:
    #             cursor.execute(
    #                 """insert into mainlist(id, title,
    #                     author, content, source_url, site_url, site_ctime)
    #                   value (%s,%s,%s,%s,%s,%s,%s)""",
    #                 (item['id'],
    #                  item['title'],
    #                  item['author'],
    #                  item['content'],
    #                  item['source_url'],
    #                  item['site_url'],
    #                  item['create_time']
    #                  ))
    #
    #             spider.database_insert += 1
    #             spider.my_logger.info(
    #                 "Insert: {} for url: {}".format(item['id'], spider.allowed_domains[0]))
    #             # print("Article ", self.article_no, "item['source_url'], ", " Insert Complete")
    #
    #         spider.connection.commit()
    #         spider.successful += 1
    #         return item
    #
    # except Exception as ex:
    #     spider.my_logger.exception(ex)
    #     raise DropItem("Reconnection Failed, Database Error")

    def open_spider(self, spider):
        try:
            spider.connection = pymysql.connect(
                host=self.host,
                db=self.db,
                user=self.user,
                password=self.passwd,
                charset='utf8mb4',
                use_unicode=True)
        except Exception as ex:
            spider.my_logger.exception(ex)

    @staticmethod
    def close_spider(spider):

        # log_str = ""
        # log_str += '[Summary==================== '
        # log_str += 'Total New Articles Count: {} '.format(spider.new_article)
        # log_str += 'Total Processed Article Count: {} '.format(spider.article_no)
        # log_str += 'Total Invalid Article Count: {} '.format(spider.article_no - spider.successful)
        # log_str += 'Duplicate Count {} '.format(spider.duplicateCount)
        # # log_str += 'Error Processed Failed URL List: {} '.format(spider.error_list_url)
        # log_str += 'Processed Failed URL Count: {} '.format(len(spider.error_list_url))
        # log_str += 'Delete Extra Content Failed URL Count: {} '.format(len(spider.delete_failed_url))
        # log_str += 'Successful Insert into database count: {} '.format(spider.database_insert)
        # log_str += '============================ Summary Finished...]'

        # spider.my_logger.info(log_str)

        try:
            spider.connection.close()
        except Exception as ex:
            spider.my_logger.exception(ex)

    def process_item(self, item, spider):

        # if id is not set, the item is not handled from the itemloader service
        if item['id'] is None:
            raise DropItem("Crawled Article Skipped")

        if item.__class__ == Match:

            if not spider.connection:
                time_waited = 0
                # Reconnect to database if connection lost
                while not spider.connection:
                    try:
                        spider.connection = pymysql.connect(
                            host=self.host,
                            db=self.db,
                            user=self.user,
                            password=self.passwd,
                            charset='utf8mb4',
                            use_unicode=True)
                    except Exception as ex:
                        spider.my_logger.exception(ex)
                        time.sleep(5)
                        time_waited += 1
                        if time_waited == 10:
                            raise IOError("10 times Attempt has been used to reconnect to Database, failed..")

            try:
                with spider.connection.cursor() as cursor:
                    cursor.execute(
                        """select * from lolcrawler where gameId = %s""",
                        (item["gameId"]
                         ))

                    ret = cursor.fetchone()
                    # if have same title and author in database already then pass
                    if ret:
                        # self.cursor.execute(
                        #     """update mainlist set id = %s, title = %s,
                        #         author = %s, content = %s, source_url = %s""",
                        #     (item['id'],
                        #      item['title'],
                        #      item['author'],
                        #      item['content'],
                        #      item['source_url']
                        #      ))

                        # # log_print("Article Exists, id")
                        spider.my_logger.info("Already Exist in Database: {}".format(ret[0]))
                        pass

                    else:
                        cursor.execute(
                            """insert into lolcrawler(seasonId,
                                queueId,
                                gameId,
                                participantIdentities,
                                gameVersion,
                                platformId,
                                gameMode,
                                mapId,
                                gameType,
                                teams,
                                participants,
                                gameDuration,
                                gameCreation,
)
                              value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (   item['seasonId'],
                                item['queueId'],
                                item['gameId'],
                                item['participantIdentities'],
                                item['gameVersion'],
                                item['platformId'],
                                item['gameMode'],
                                item['mapId'],
                                item['gameType'],
                                item['teams'],
                                item['participants'],
                                item['gameDuration'],
                                item['gameCreation'],
                             ))

                        spider.database_insert += 1
                        spider.my_logger.info("Insert: {} for url: {}".format(item['id'], spider.allowed_domains[0]))
                        # print("Article ", self.article_no, "item['source_url'], ", " Insert Complete")

                    spider.connection.commit()

            except Exception as ex:
                spider.my_logger.exception(ex)
                spider.error_list_url.append(item['source_url'])
                spider.my_logger.info(item['content'])
                raise DropItem("Database Connection lost, article dropped, reconnect next article")

            spider.successful += 1
            return item


class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):

        if item['id'] in self.ids_seen:
            # print(item['title'], " Article duplicate found, pass")

            spider.my_logger.warning("Duplicate item found: {} for spider: {}"
                                     .format(item['id'].strip(), spider.allowed_domains[0]))
            spider.duplicateCount += 1
            raise DropItem("Duplicate item found: %s" % item['title'].strip())

        else:

            self.ids_seen.add(item['id'])
            return item