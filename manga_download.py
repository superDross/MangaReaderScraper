import custom_exceptions
import requests
import bs4
import os

MANGA_URL = 'http://mangareader.net'
HERE = os.path.dirname(os.path.realpath(__file__))


def get_manga_volume_links(manga, volume):
    ''' Get HTML urls of a given manga volumes pages.'''
    link = "{}/{}/{}".format(MANGA_URL, manga, volume)
    url = get_url_text(link)
    check_volume_exists(url, manga, volume)
    all_volume_links = url.find_all('option')
    all_page_links = [MANGA_URL+page.get('value') for page in all_volume_links]
    print('Preparing to download {} pages of {} volume {}'.format(
          len(all_page_links), manga, volume))
    return all_page_links


def check_volume_exists(url, manga, volume):
    error_msg = url.find('div', id='relatedheader')
    if error_msg:
        if error_msg.text.find('not published'):
            raise custom_exceptions.VolumeDoesntExist(manga, volume)


def get_total_volumes(manga):
    ''' Get HTML urls for all manga volumes.'''
    try:
        link = '{}/{}'.format(MANGA_URL, manga)
        manga_url = get_url_text(link)
        volume_tags = manga_url.find('div', id='chapterlist').find_all('a')
        volume_links = [MANGA_URL+vol.get('href') for vol in volume_tags]
        print('Preparing to download {} voumes of {}'.format(
              len(volume_links), manga))
        return volume_links
    except requests.exceptions.HTTPError as e:
        raise custom_exceptions.MangaDoesntExist(manga)


def get_url_text(link):
    ''' Download the text from a given link.'''
    req = requests.get(link)
    req.raise_for_status()
    url = bs4.BeautifulSoup(req.text, features='lxml')
    return url


def download_page(url, page_title):
    ''' Download jpg from the given url.'''
    img_url = url.find('img').get('src')
    img_data = requests.get(img_url).content
    print('Saving {}'.format(page_title))
    with open(page_title, 'wb') as handler:
        handler.write(img_data)


def download_volume(manga, volume):
    ''' Download all pages of a given volume.'''
    manga_volume_links = get_manga_volume_links(manga, volume)
    page_num = 1
    for page_link in manga_volume_links:
        jpg_filename = '{}{}_{}_{}.jpg'.format(
                        HERE+'/jpgs/', manga, volume, page_num, '.jpg')
        if not os.path.isfile(jpg_filename):
            page_url = get_url_text(page_link)
            download_page(page_url, jpg_filename)
            page_num += 1


def download_all_volumes(manga):
    ''' Download all pages and volumes.'''
    all_volumes = get_total_volumes(manga)
    all_volume_numbers = [vol.split("/")[-1] for vol in all_volumes]
    for volume in all_volume_numbers:
        download_volume(manga, volume)
