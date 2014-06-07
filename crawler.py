#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import grequests
import urllib2
import json
import sys
import re
import os
import time
from bs4 import BeautifulSoup
from flask import jsonify


class Crawler:

    def __init__(self):

                    # Error and default variables

        self.e1 = 'Url404'
        self.e2 = 'Error404'
        self.e3 = 'Sitemap404'
        self.crawl_depth = 50
        self.count = 0
        self.block_terms = ['#', 'null', '', None]
        self.stack_main = []
        self.stack_to_be_indexed = []
        self.stack_test = []
        self.block_terms_url = [
            'javascript:',
            '#',
            'javascript:;',
            None,
            '/',
            '',
            'javascript:void();',
            ]
        self.base_url = ''
        self.basenew_url = ''
        self.crawl_count = 50
        self.count_main = 0
        self.exclude = (
            '.mp3',
            '.png',
            '.jpg',
            '.gif',
            '.txt',
            '.pdf',
            '.jpeg',
            '.flv',
            '.mp4',
            '.zip',
            '.css',
            '.js',
            )

            # Add http/s prefix

    def URL(self, url):
        if 'http://' in url:
            return url
        elif 'https://' in url:
            return url
        elif 'http://' not in url:
            return 'http://' + url

            # Check for redirection to www/non-ww or somewhere else

    def mainURI(self, uri):
        uri = self.URL(uri)
        return requests.head(uri, allow_redirects=True).url

            # Retry attempt

    def retry(self, retry_attempt=3):
        self.count += 1

                # Disconnect after * retries

        if self.count == retry_attempt:
            self.count = 0
            return False

            # Initiate crawler first

    def crawl_start(self, url, count):
        url = self.mainURI(url)
        self.base_url = url
        if type(count) == int and int(count) < 151:
            self.crawl_count = count
        if self.base_url.endswith('/'):
            self.basenew_url = self.base_url[:-1]
        else:
            self.basenew_url = self.base_url
        try:
            data = requests.get(url, allow_redirects=True,
                                timeout=2.0).content
        except Exception:
            sys.exc_clear()
        if self.pull_links(data):
            return self.crawl_run()

            # Keep crawler running

    def crawl_run(self):
        for url in self.stack_to_be_indexed:
            if url.startswith(self.basenew_url):
                self.stack_main.append(str(url))
                if len(self.stack_main) == self.count_main:
                    break
            if len(list(set(self.stack_main))) >= self.crawl_count:
                break

                # Still we didnt reached our aim that is specified urls run again

        if len(list(set(self.stack_main))) < self.crawl_count \
            and len(self.stack_main) > self.count_main:
            self.stack_to_be_indexed = []
            self.stack_to_be_indexed = \
                self.pull_links(requests.get(self.stack_main[self.count_main],
                                allow_redirects=True,
                                timeout=2.0).content)
            self.count_main += 1
            self.crawl_run()
        return self.stack_main

            # Fetches all valid links from page using Beautiful Soup

    def pull_links(self, data):
        data = BeautifulSoup(data)
        self.stack_to_be_indexed = []
        for links in data.find_all('a'):
            if links.get('href') not in self.block_terms_url:
                if links.get('href').startswith(self.base_url) \
                    or links.get('href').startswith('http'):
                    link = str(links.get('href'))
                elif links.get('href').startswith('/'):
                    link = str(self.base_url) + str(links.get('href'
                            )[1:])
                else:
                    link = str(self.base_url) + str(links.get('href'))
                if link not in self.stack_main \
                    and not link.endswith(self.exclude):
                    self.stack_to_be_indexed.append(link)
        return self.stack_to_be_indexed


class Social:

    def facebook_like(self, content):
        data = json.loads(content)
        try:
            like = data['data'][0]['like_count']
        except KeyError:
            like = 0
        return {'fblike': like}

    def facebook_share(self, content):
        data = json.loads(content)
        try:
            share = data['data'][0]['share_count']
        except KeyError:
            share = 0
        return {'fbshare': share}

    def facebook_comment(self, content):
        data = json.loads(content)
        try:
            comment = data['data'][0]['comment_count']
        except KeyError:
            comment = 0
        return {'fbcomment': comment}

    def twitter_data(self, content):
        data = json.loads(content)
        return {'twitter': data['count']}

    def linkedin_data(self, content):
        try:
            data = json.loads(content)
            count = data['count']
        except ValueError:
            count = 0
            data = 0
        return {'linkedin': count}

    def pinterest_data(self, url):
        request = requests.get(url)
        if request.status_code == 200:
            jsonp = request.content
            content = jsonp[jsonp.index('(') + 1:jsonp.rindex(')')]
            data = json.loads(content)
            try:
                data = data['count']
            except KeyError:
                data = 0
            return {'pins': data}
        else:
            return {'pins': 0}

    def googleplus_data(self, content):
        regex = re.compile(r"{c:.*?,")
        data = str(regex.findall(content))
        data = data[data.find(':') + 1:data.find(',')].replace(' ', '')
        try:
            data = float(data)
        except:
            data = 0
        if isinstance(float(data), (int, long, float)):
            return {'plusone': float(data)}
        else:
            return {'plusone': 0}

        # # Get social data asynchronously from

    def social_data(self, url):

            # Social api urls to fetch counts

        social_urls = \
            ["https://graph.facebook.com/fql?q=SELECT%20url,%20share_count,%20like_count,%20comment_count,%20total_count,normalized_url,commentsbox_count,%20click_count%20FROM%20link_stat%20WHERE%20url='"
              + str(urllib2.quote(url)) + "'",
             'http://urls.api.twitter.com/1/urls/count.json?url='
             + str(urllib2.quote(url)) + '&callback=',
             'http://www.linkedin.com/countserv/count/share?url='
             + str(urllib2.quote(url)) + '&format=json',
             'https://plusone.google.com/_/+1/fastbutton?url='
             + str(urllib2.quote(url))]
        mainurl = {'url': url}

            # Pinterest sometime block continous requests to its server

        pinsurl = \
            'http://widgets.pinterest.com/v1/urls/count.json?source=6&url=' \
            + str(urllib2.quote(url))
        pins = self.pinterest_data(pinsurl)

        count = 0
        rs = (grequests.get(urls) for urls in social_urls)
        for response in grequests.map(rs):
            count += 1
            if count == 1:
                fblike = self.facebook_like(response.content)
                fbshare = self.facebook_share(response.content)
                fbcomment = self.facebook_comment(response.content)
            if count == 2:
                twitter = self.twitter_data(response.content)
            if count == 3:
                linkedin = self.linkedin_data(response.content)
            if count == 4:
                plusone = self.googleplus_data(response.content)
                return dict(mainurl.items() + fblike.items()
                            + fbshare.items() + fbcomment.items()
                            + twitter.items() + linkedin.items()
                            + pins.items() + plusone.items())
