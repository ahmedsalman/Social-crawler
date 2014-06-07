#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
import io
import json
import os
from crawler import Crawler, Social
from datetime import timedelta
from flask import Flask, render_template, request, make_response, request, current_app, jsonify
from functools import update_wrapper


app = Flask(__name__)


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods
        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

#Route to show homepage
@app.route("/",methods=['GET'])
def index():
    return '<h1> Post request to /getdata with values <br> </h1> <p>url : url without http or www <br> urlno : url count </p>'


#Route to show homepage post data after doing somethings.
@app.route("/getdata",methods=['POST'])
@crossdomain(origin='*')
def index_post():
        crawler_object=Crawler()
        crawled_urls=list(set(crawler_object.crawl_start(str(request.form['url']),str(request.form['urlno']))))

        social_object=Social()
        social_counts=[]
        for url in crawled_urls:
            social_counts.append(social_object.social_data(url))
        return jsonify(links=social_counts)



@app.route("/count/<website>",methods=['GET'])
@crossdomain(origin='*')
def async(website):
    return str(cache.get(str(website)+'urlcount'))

@app.route("/current/<website>",methods=['GET'])
@crossdomain(origin='*')
def current(website):
    return str(cache.get(str(website)+'currenturl'))


@app.errorhandler(500)
def internal_error(error):
    return "500"


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)


