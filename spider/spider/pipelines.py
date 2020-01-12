# -*- coding: utf-8 -*-

import pydocumentdb.document_client as document_client


class SpiderPipeline(object):

    def __init__(self, docdb_host, docdb_db, docdb_coll, docdb_mkey):
        self.docdb_host = docdb_host
        self.docdb_db = docdb_db
        self.docdb_coll = docdb_coll
        self.docdb_mkey = docdb_mkey

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            # accesssing variables defined in settings.py
            docdb_host=crawler.settings.get('DOCDB_HOST'),
            docdb_db=crawler.settings.get('DOCDB_DB'),
            docdb_coll=crawler.settings.get('DOCDB_COLLECTION'),
            docdb_mkey=crawler.settings.get('DOCDB_MASTER_KEY')
        )  # -> args of def __init__

    # executed in starting spider
    def open_spider(self, spider):
        # create documentDb client instance
        self.client = document_client.DocumentClient(self.docdb_host,
                                                     {'masterKey': self.docdb_mkey})
        # create a database if not yet created
        database_definition = {'id': self.docdb_db}
        databases = list(self.client.QueryDatabases({
            'query': 'SELECT * FROM root r WHERE r.id=@id',
            'parameters': [
                {'name': '@id', 'value': database_definition['id']}
            ]
        }))
        feeddb = None
        if (len(databases) > 0):
            feeddb = databases[0]
        else:
            print("database is created:%s" % self.docdb_db)
            feeddb = self.client.CreateDatabase(database_definition)

        # create a collection if not yet created
        collection_definition = {'id': self.docdb_coll}
        collections = list(self.client.QueryCollections(
            feeddb['_self'],
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    {'name': '@id', 'value': collection_definition['id']}
                ]
            }))
        self.feedcoll = None
        if len(collections) > 0:
            self.feedcoll = collections[0]
        else:
            print("collection is created:%s" % self.docdb_coll)
            self.feedcoll = self.client.CreateCollection(
                feeddb['_self'], collection_definition)

    # executed in ending spider
    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        document_definition = {
            'text': item['text'],
            'author': item['author']}

        self.client.CreateDocument(
            self.feedcoll['_self'], document_definition)
        return item
