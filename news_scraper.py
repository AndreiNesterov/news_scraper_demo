### News parser demo
### By Andrei Nesterov

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re

def _get_time_threshold(min:str) -> str:
    '''
    Getting the datetime threshold for If-Modified-Since;
    Calculates the time difference between current datetime and indicated N minutes
    min: int; last modified since N minutes
    Returns str; format: 'Mon, 01 Jan 2025 00:00:00 GMT' (according to If-Modified-Since docs)
    '''
    
    current_datetime = datetime.utcnow()
    last_updated_datetime = current_datetime - timedelta(minutes=min)
    
    return last_updated_datetime.strftime("%a, %d %b %Y %H:%M:%S GMT")


def _parse_urls(time_threshold:str) -> list:
    '''
    Collecting all article URLs from the main page 'https://text.npr.org/'
    time_threshold: str; output of _get_time_threshold
    Returns a list of str; all urls on the main page
    '''

    url = "https://text.npr.org/"

    all_urls = []
    
    headers = {"If-Modified-Since": time_threshold}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Parsing new articles...")
        soup = BeautifulSoup(response.text, "html.parser")
        all_urls = [url + article_url['href'].lstrip('/') for article_url in soup.find('div',{'class':'topic-container'}).find_all('a',{'class':'topic-title'})]
        print(f"Found {len(all_urls)} articles to parse")
    else:
        print(f'There has been no updates since {time_threshold}. ')

    return all_urls

def _parse_single_article(article_url:str) -> list:
	'''
	Getting data for a single article: title, author, date
	article_url: str; 
	Returns a list of str ['title','author','date']
	'''

	article_data = []

	date_pattern = r'\w* \d{1,2}, \d{4}'

	response_article = requests.get(article_url) # not using If-Modified-Since here

	if response_article.ok == True:
		soup_article = BeautifulSoup(response_article.text, "html.parser")
		
		# getting header
		header = soup_article.find('div',{'class':'story-head'})
		
		# title
		title = header.h1.text
		article_data.append(title)

		# author
		author = header.find_all('p')[0].text.replace('By ','')
		article_data.append(author)

		# date
		raw_date = header.find_all('p')[1].text
		re_date = re.findall(date_pattern, raw_date)[0]
		# required date format
		date = datetime.strptime(re_date, "%B %d, %Y").strftime("%Y-%m-%d")
		article_data.append(date)

	return article_data









    