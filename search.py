''' Search MangaReader.net for a given query and allows the user to select from the results.'''
import re
from tabulate import tabulate
from utils import get_html_from_url
from config import MANGA_URL


def get_search_url(query, manga_type=0, manga_status=0, order=0,
                   genre='0000000000000000000000000000000000000'):
    ''' Scrape and return HTML page with search results.'''
    url = f'''{MANGA_URL}/search/?w={query}&rd={manga_type}
               &status={manga_status}&order=0&genre={genre}&p=0'''
    url = get_html_from_url(url)
    return url


def to_dataframe(url):
    ''' Select information for each manga in the search results
        and return as a DataFrame.
    '''
    url_list = url.find_all('div', {'class': 'mangaresultitem'})
    manga_info = []
    key = 1
    for result in url_list:
        # split is required as some mangas have multiple titles
        title = result.find('div', {'class': 'manga_name'}).text
        manga_url = result.find('div', {'class': 'manga_name'}).find('a').get('href')
        chapters = result.find('div', {'class': 'chapter_count'}).text
        manga_type = result.find('div', {'class': 'manga_type'}).text.split("(")[0]
        manga_info.append([str(key), title.replace('\n', ''), re.sub("\D", "", chapters),
                           manga_type, manga_url.replace('/', '')])
        key += 1
    return manga_info


def select_manga(table_data):
    ''' Ask user which manga in the search results they wish to download.'''
    columns = ['', 'Title', 'Volumes','Type']
    table = tabulate([x[:-1] for x in table_data],
                     headers=columns,
                     tablefmt='psql')
    print(table)
    manga_num = input('Select manga number\n')
    key, title, volumes, mtype, url = table_data[int(manga_num)-1]
    print(f'\n{title} has been selected for download.\n')
    return url


def search_and_get_url(query):
    ''' Search MangaReader for a given query and return the web url
        for the user selected manga.
    '''
    url = get_search_url(query)
    table_data = to_dataframe(url)
    selected_manga_url = select_manga(table_data)
    return selected_manga_url
