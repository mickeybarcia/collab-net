# pip install lxml
import re
from bs4 import BeautifulSoup, SoupStrainer
import requests
import csv
from datetime import date, datetime
import lxml.html
from dateutil.rrule import rrule, DAILY
import pandas as pd
import re
import uuid
from multiprocessing import Pool, Manager
import sys
import time

sys.setrecursionlimit(100000)
umd_url = "http://umdmusic.com/default.asp?Lang=English&Chart=D"
session = requests.Session()

def define_artists(artists_string):  
    artists_dict = {}
    artists_string = artists_string.replace(".", "")
    # for char in [" x ", " / ", " and ", ", ", " with ", " + "]:
    #     artists_string = artists_string.replace(char, " & ")
    for char in [" x ", " / ", " and ", ", ", " with ", " + ", " feat "]:
        artists_string = artists_string.replace(char, " & ")
    # artists_string = artists_string.replace("feat ", "featuring ")
    artists = artists_string.split("featuring")
    artists_dict["artists"] = list(map(str.strip, artists[0].split(" & ")))
    # if len(artists) == 2:
    #     artists_dict["featuring"] = list(map(str.strip, artists[1].split(" & ")))
    return artists_dict

def scrape_row_details(row, date):  
    song_dict = { "date": date }
    col_num = 0
    for cell in row.children:
        if cell.name == "td":
            if col_num == 4:
                title = cell.contents[0].string.strip().lower()
                song_dict["title"] = title
                artists_string = cell.contents[2].string.strip().lower()
                song_dict["artists"] = define_artists(artists_string)
                song_dict["title_full"] = title + " - " + artists_string
            elif col_num == 5: 
                song_dict["entry_date"] = cell.contents[0].strip()
            elif col_num == 6:
                song_dict["entry_position"] = cell.contents[0].strip()
            elif col_num == 7:
                song_dict["peak_position"] = cell.contents[0].strip()
            elif col_num == 8:
                song_dict["total_weeks"] = cell.contents[0].strip()
                break
            col_num += 1
    return song_dict

def soup_scrape(date):
    chart_songs = []
    request_path = umd_url + "&ChDay=" + str(date.day) + "&ChMonth=" + str(date.month) + "&ChYear=" + str(date.year) + "&ChBand=&ChSong="
    html = session.get(request_path).content
    soup = BeautifulSoup(html, "lxml")
    table = soup.find_all(text=re.compile("Display Chart Table"))[0]
    while table.name != "table":
        table = table.next_element
    for row in table.children:
        if row.name == "tr" and len(list(row.children)) == 18:
            chart_songs.append(scrape_row_details(row, date))
    return chart_songs

def collapse(charts_list):
    song_data = {}
    for chart in charts_list:
        for song in chart:
            title = song["title"]
            date = song["date"]
            if (title in song_data and song_data[title]["date"] < date) or title not in song_data:
                song_data[title] = song
    return song_data


class ChartsScrape:

    def __init__(self, first_year="2020", last_year="2022"):
        self.first_year = first_year
        self.last_year = last_year
        self.chart_map = {}

    def save(self):
        charts_df = pd.DataFrame(self.chart_map.values())
        del charts_df['date']
        charts_df.to_csv('charts.csv', sep='\t')

    def run(self):
        # get list of days to scrape from
        start_dt = datetime.strptime(self.first_year, '%Y')
        end_dt = datetime.strptime(self.last_year + "-12-31", '%Y-%m-%d')
        days = rrule(DAILY, dtstart=start_dt, until=end_dt)
        
        # scrape each day in parallel
        start = time.time()
        with Pool() as p:
            charts_list = p.map(soup_scrape, days)
        end = time.time()
        print("seconds spent scraping: " + str(end - start))

        # format and save chart csv
        self.chart_map = collapse(charts_list)
        self.save()
