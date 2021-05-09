#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This last project by getting EN monitor - 2021-05-01

import requests
from bs4 import BeautifulSoup
import logging
import request_EN
import random
import os
import pandas as pd
import time
import copy
import re
from lxml import html, etree

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def load_page_from_file(file_path=''):
    """
    Load html file to BS
    :param file_path: {str} - File path
    :return: soup {BeautifulSoup} - page for heading
    """
    with open(file_path, 'r') as f:
        contents = f.read()
        soup_lpff = BeautifulSoup(contents, 'lxml')
    return soup_lpff


def get_soup_old(url=None, to_file=False, file=None):
    print('Debug get_soup: {} - {} - {}'.format(URL_game, to_file, file))
    if url is not None:
        if to_file:
            en_ws.get_page_to_file(url, file)
            soup_out = load_page_from_file(file)
        else:
            en_ws.get_page(url)
            soup_out = BeautifulSoup(en_ws.resp.content, 'html.parser')
    else:
        soup_out = load_page_from_file(file)
    return soup_out


def clear_html_string(in_str):
    in_str = in_str.replace(u'\xa0', u' ')
    in_str = in_str.strip()
    in_str = ' '.join(in_str.split())
    return in_str


def get_answer_from_page(soup_pa=None, df_ob=None):
    """
    Transform EN-page of stats to table
    :param soup_pa: (BS object) page of EN
    :param df_ob: (Panda's DataFrame object) table of stats
    :return: df_ob (Panda's DataFrame object) table of stats
    """

    # Find TD elements contain Answer
    # td = soup_pa.select('td[class*="Text4"]')
    td = soup_pa.select('td[class*="Text4"], td[class*="yellow_green11"]')
    # MonitoringForm > table > tbody > tr:nth-child(5) > td > table > tbody > tr
    # trs = trs[4:]
    request_EN.save_bs_to_file(soup_pa, 'materials/p1.html')
    # print(td)

    if len(td) == 0:
        logger.info("Can't find a stats at page")
        request_EN.save_bs_to_file(soup_pa, 'materials/error.html')
    else:
        logger.info('stats found')

    # Drop page to blocks
    for l, t, c, a, d in zip(td[0::5], td[1::5], td[2::5], td[3::5], td[4::5]):
        l = clear_html_string(l.text)  # Number of level
        t = clear_html_string(t.text)  # Team and User
        u = clear_html_string(t[t.find("(") + 1:t.find(")")])  # User
        t = clear_html_string(t[:t.find('(') - 1])  # Team
        c = clear_html_string(c.text)  # Is correct answer
        a = clear_html_string(a.text)  # Answer
        d = clear_html_string(d.text)  # Date of answer

        # print('{}-{}-{}-{}'.format(l,t,a,d))

        df_ob = df_ob.append({'Level': l,
                              'Team': t,
                              'User': u,
                              'IsCorrect': c,
                              'Answer': a,
                              'Date': d},
                             ignore_index=True)

    return df_ob


def handling_dataframe(df_in=None):
    team_list = df_in['Team'].unique()
    levels_list = df_in['Level'].unique()
    pd.set_option('display.max_columns', 7)
    for team in team_list:
        for level in levels_list:
            select = df_in.loc[(df_in['Team'] == team) & (df_in['Level'] == level)]
            all_answer = len(select)
            select = df_in.loc[(df_in['Team'] == team) & (df_in['Level'] == level) & (df_in['IsCorrect'] == 'н')]
            uncor_anwser = len(select)

            print('{} ({})= A:{}, U:{}'.format(team, level, all_answer, uncor_anwser))


def login_en(game_id=None, login=None, password=None):
    en_ws = request_EN.WebSession()
    en_ws.login_en(login=os.getenv('en_login'), password=os.getenv('en_password'))  # Login
    return en_ws


def count_page(soup_in):
    # Count page of stats
    try:
        div = soup_in.select('#ctl03_divContent > div')
        count_page_list = div[0].text.replace(u'\xa0', u' ').split(' ')
        count_page = int(count_page_list[-1])
    except IndexError:
        count_page = 1
    return count_page

def get_monitoring():
    # Constants
    # url = "http://demo.en.cx/GameStat.aspx?type=own&gid=30415"
    URL_monitoring = 'http://72.en.cx/Administration/Games/ActionMonitor.aspx?gid=71529'
    game_id = '71529'

    # Creating an empty Data frame with column name only
    df_object = pd.DataFrame(columns=['Level', 'Team', 'User', 'IsCorrect', 'Answer', 'Date'])

    en_ws = login_en()  # Login EN
    # Get first page of monitor
    soup = en_ws.get_bs_from_url(url=URL_monitoring)

    # Count page of monitoring
    amount_page = count_page(soup)

    # Conversion page to DataFrame
    # First page
    df_object = get_answer_from_page(soup, df_object)
    # Next pages
    if amount_page > 1:
        for i in range(2, amount_page):
            time.sleep(2)
            link_page = 'http://72.en.cx/Administration/Games/ActionMonitor.aspx?' \
                        'gid={}&page={}'.format(game_id, i)
            # en_ws.get_page(url=link_page)  # Get page
            # soup = BeautifulSoup(en_ws.resp.content, 'html.parser')
            print(link_page)
            soup = en_ws.get_bs_from_url(url=link_page)
            df_object = get_answer_from_page(soup, df_object)

            # Save DataFrame to CSV
            # df_object.to_csv('materials/monitoring.csv')

            print(df_object.iloc[[0, -1]])

    # Save DataFrame to CSV
    df_object.to_csv('materials/monitoring.csv')


def parsing_stats(file_path='materials/monitoring.csv'):
    data_frame = pd.read_csv(file_path)
    handling_dataframe(data_frame)


if __name__ == '__main__':
    csv_file_path = 'materials/monitoring.csv'
    error_page_file_path = 'materials/error.html'
    game_id = '71529'
    URL_game = 'http://72.en.cx/GameDetails.aspx?gid={}'.format(game_id)
    URL_monitoring = 'http://72.en.cx/Administration/Games/ActionMonitor.aspx?gid={}'.format(game_id)
