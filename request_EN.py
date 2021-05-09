#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
from bs4 import BeautifulSoup
from lxml import html, etree
import aiohttp
import asyncio
import cProfile

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def save_bs_to_file(soup=None, file_path=None):
    """
    Just save BS Soup to file
    :param soup: (BS object) Page of WebSite
    :param file_path: (str) File path
    :return: pass
    """
    if file_path is None:
        file_path = 'materials/temp.html'
    with open(file_path, "w", encoding='utf-8') as file:
        file.write(str(soup.prettify()))
    pass


def get_bs_from_file(file_path=None):
    """
    Get BS page from file
    :param file_path: {str} - File path
    :return: soup {BeautifulSoup} - page for heading
    """
    with open(file_path, 'r') as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'lxml')
    return soup


class WebSession(object):
    """
    Class for handling requests from site
    """

    def __init__(self, url=None):
        self.url = url
        self.resp = None
        self.page = None
        self.session = requests.session()

        self.login = None
        self.password = None

        self.session.headers.update({
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
            'User-Agent': 'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0',
            'Connection': 'keep-alive'})

    def set_login(self, login=None):
        self.login = login

    def set_password(self, password=None):
        self.password = password

    def _request_wrapper(self, resp=None):
        """Wraps Requests for handling known exceptions."""
        if resp is not None:
            if 'login.aspx' in resp.url:
                logger.info('Need to log in {}'.format(resp.url))
                return False
            elif 200 == resp.status_code:
                self.resp = resp
                return True
            else:
                logger.info('Failed to load the page')
                return resp.status_cod

    def get_resp(self, url=None):
        """
        Main function for get a response to the request
        :param url: (str) Url for request
        :return: (resp) The response from the request
        """
        if url is None:
            url = self.url
        resp = self.session.get(url)
        return self._request_wrapper(resp)

    def get_html_requests(self):
        parser = html.HTMLParser(encoding='utf-8')
        page = html.fromstring(self.resp.content, parser=parser)
        return page

    def page_to_file(self, file_path=None):
        """
        JUST Save the resulting page to file
        :param file_path: (str) File path
        :return: None
        """
        if file_path is None:
            file_path = 'materials/temp.html'
        with open(file_path, 'w') as file:
            file.write(self.resp.text)
        pass

    def get_page_to_file(self, url='http://72.en.cx', file_name=None):
        """
        Send request and Save the resulting page to file
        :param url: (str) Link
        :param file_name: (str) File path for save page
        :return: pass
        """
        self.get_resp(url)
        self.page_to_file(file_name)
        pass

    def get_bs_from_url(self, url='http://72.en.cx'):
        """
        Get BS page from the url
        :param url: (str) Url for request
        :return: (BS object) Soup
        """
        self.get_resp(url)
        soup = BeautifulSoup(self.resp.content, "html.parser")
        return soup

    def check_login(self, domain='72'):
        url = 'http://{0}.en.cx/UserDetails.aspx'.format(domain)
        resp = self.session.get(url)
        if resp.url == url:
            return True
        else:
            return False

    def login_en(self, domain='72', login=None, password=None):
        """
        Method login on encounter website
        """
        if login is None:
            login = self.login

        if password is None:
            password = self.password

        if (domain is not None) and \
                (login is not None) and \
                (password is not None):

            url = 'http://{0}.en.cx/Login.aspx?return=%%2f'.format(domain)
            userdata = {
                'socialAssign': 0,
                'Login': login,
                'Password': password,
                'EnButton1': 'Вход',
                'ddlNetwork': 1
            }

            resp = self.session.get(url)
            resp = self.session.post(url, data=userdata)

            # Check LogIN
            # Данный код основывается на том что при авторизации
            # у нас будет переадресация на главную старницу
            if resp.history:
                logger.info("LogIN")
                return True
            else:
                logger.info("LogOUT")
                return False
        else:
            logger.info('Bad args for login')
            return None

def main():
    en_ws = WebSession()
    save_bs_to_file(soup, 'materials/test.html')



if __name__ == '__main__':
    main()
