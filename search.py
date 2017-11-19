''' Search MangaReader.net for a given query and allows the user to select from the results.'''
from download import get_url_text
from config import MANGA_URL
from tabulate import tabulate
import pandas as pd
import re


def get_search_url(query, manga_type=0, manga_status=0, order=0,
                   genre='0000000000000000000000000000000000000'):
    ''' Scrape and return HTML page with search results.'''
    link = '{}/search/?w={}&rd={}&status={}&order=0&genre={}&p=0'.format(
          MANGA_URL, query, manga_type, manga_status, order, genre)
    url = get_url_text(link)
    return url


def to_dataframe(url):
    ''' Select information for each manga in the search results
        and return as a DataFrame.
    '''
    url_list = url.find_all('div', {'class': 'mangaresultitem'})
    manga_info = []
    for result in url_list:
        # split is required as some mangas have multiple titles
        title = result.find('h3').text.split(',')[0]
        manga_link = result.find('h3').find('a').get('href').replace('/', '')
        chapters = result.find('div', {'class': 'chapter_count'}).text
        genre = result.find('div', {'class': 'manga_genre'}).text
        manga_type = result.find('div', {'class': 'manga_type'}).text.split("(")[0]
        manga_info.append([title, re.sub("\D", "", chapters),
                           genre, manga_type, manga_link])
    columns = ['Title', 'Volumes', 'Genre', 'Type', 'Link']
    df = pd.DataFrame(manga_info, columns=columns)
    return df


def select_manga(df):
    ''' Ask user which manga in the search results they wish to download.'''
    pretty_table = tabulate(df[['Title', 'Volumes', 'Type']],
                            headers='keys', tablefmt='psql')
    print(pretty_table)
    manga_num = input('Select manga number\n')
    selected_manga = df.iloc[[manga_num]]
    print('{} has been selected for download.'.format(selected_manga['Title'].to_string(index=False)))
    selected_manga_link = selected_manga['Link'].to_string(index=False)
    return selected_manga_link


def search_and_get_link(query):
    ''' Search MangaReader for a given query and return the web link
        for the user selected manga.
    '''
    url = get_search_url(query)
    df = to_dataframe(url)
    selected_manga_link = select_manga(df)
    return selected_manga_link
