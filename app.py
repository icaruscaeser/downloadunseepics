# Author: Icarus Caeser
# Created at 3:38 PM on 05/07/21

from flask import Flask, Request, request, Response, render_template, send_file
from downloadunseepics import DownloadUnsee, DownloadOldUnsee

import os
import logging
from selenium import webdriver
import config

app = Flask(__name__)

@app.route('/api/download/old_unsee')
def download_old_unsee():
    url = request.args.get('url')
    old_unsee = DownloadOldUnsee(url)
    downloaded_pics = old_unsee.download_pics()
    return send_file(downloaded_pics, attachment_filename='unsee.zip', mimetype='application/zip')


@app.route('/api/download/unsee')
def download_unsee():
    url = request.args.get('url')
    logging.debug(url)
    unsee = DownloadUnsee(url)
    downloaded_pics = unsee.download_pics()
    return send_file(downloaded_pics, attachment_filename='unsee.zip', mimetype='application/zip')


@app.route('/')
def index():
    return render_template('index.html', data=config.CONFIG_DATA)

@app.route('/test')
def test():
    return "tested";


if __name__ == '__main__':

    if config.DOWNLOAD_DIR not in os.listdir():
        print('Creating {} directory'.format(config.DOWNLOAD_DIR))
        os.mkdir(config.DOWNLOAD_DIR)

    if os.environ.get('staging'):

        config.IS_STAGING = True
        print('Staging environment')
        config.CONFIG_DATA['server_url'] = 'https://downloadunseepics.herokuapp.com'

        # refer https://medium.com/@mikelcbrowne/running-chromedriver-with-python-selenium-on-heroku-acc1566d161c
        config.GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
        config.CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

        config.CHROME_OPTIONS.add_argument('--disable-gpu')
        config.CHROME_OPTIONS.add_argument('--no-sandbox')
        config.CHROME_OPTIONS.binary_location = config.GOOGLE_CHROME_PATH

        # enable headless
        config.CHROME_OPTIONS.add_argument('--headless')

    port = int(os.environ.get('PORT', 5000))

    app.run(host='0.0.0.0', port=port, debug=not config.IS_STAGING)