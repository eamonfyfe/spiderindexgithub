import crochet
from flask import Flask, jsonify
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher

from spider.spider.spiders.Spider import Spider
crochet.setup()


app = Flask(__name__)
output_data = []
crawl_runner = CrawlerRunner()


@app.route("/")
def scrape():
    scrape_with_crochet()

    return jsonify(output_data)


@crochet.wait_for(timeout=60.0)
def scrape_with_crochet():
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    eventual = crawl_runner.crawl(
        Spider)
    return eventual  # returns a twisted.internet.defer.Deferred


def _crawler_result(item, response, spider):
    """
    We're using dict() to decode the items.
    Ideally this should be done using a proper export pipeline.
    """
    output_data.append(dict(item))


if __name__=='__main__':
    app.run('127.0.0.1', 5000)