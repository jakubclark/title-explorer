import re
from datetime import date
from typing import List

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from .exceptions import TitleNotFound
from .logger import log

title_search_url = 'https://www.imdb.com/find'
title_url = 'https://www.imdb.com/title/'

month_to_num = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}


class Utils:

    @staticmethod
    def get_date(soup: BeautifulSoup):
        release_date = soup.find('a', title='See more release dates').text.strip()
        if 'TV' in release_date:
            # This is a tv show
            live_time = re.search(r'\(\d*–(\d*| )?\)', release_date)[0]
            live_time = re.sub('[()]', '', live_time)
            parts = live_time.split('–')
            start = parts[0]
            end = parts[1]

            return {
                'start_year': start,
                'end_year': end
            }
        else:
            release_date = re.sub(r'\(.*\)$', '', release_date).strip()
            day, month, year = release_date.split(' ')
            day = int(day)
            year = int(year)
            release_date = date(year, month_to_num[month], day)
            return {
                'release_date': release_date
            }

    @staticmethod
    def to_minutes(runtime):
        """
        Convert a runtime, in the form of 2h 12min to a number, in minutes
        """
        if 'h' in runtime:
            # more than 60 minute
            hours = int(re.search(r'\d*h', runtime)[0].split('h', 1)[0])

        else:
            hours = 0

        if 'min' in runtime:
            minutes = int(re.search(r'\d*min', runtime)[0].split('min', 1)[0])
        else:
            minutes = 0

        return hours * 60 + minutes

    @staticmethod
    def extract_persons(divs, field) -> List[str]:
        """
        Search for `field`, such as 'Director' or 'Stars'
        """

        def should_ignore(s):
            for reg in unneeded:
                if re.search(reg, str(s)):
                    return True
            return False

        unneeded = [r'\d* more credits', r'See full cast']

        res = []
        for div in divs:
            h4 = div.find('h4')
            if field in h4.text:
                for dir in div.find_all('a'):
                    if should_ignore(dir.text):
                        continue
                    res.append(dir.text.strip())
        return res


class MovieScraper:

    def __init__(self, session: ClientSession):
        self._session = session

    async def search_by_title(self, title: str):
        log.debug(f'Scraping for title="{title}"')
        params = {
            's': 'tt',
            'q': title
        }
        async with self._session.get(title_search_url, params=params) as response:
            txt = await response.text()

        soup = BeautifulSoup(txt, features='html.parser')
        find_results = soup.find_all('tr', class_='findResult')

        movies = []

        for result in find_results:
            image = result.find('img')['src']
            title = result.find('td', class_='result_text').find('a').text
            href = result.find('td', class_='result_text').find('a')['href']
            imdb_id = re.split(r'/', href, 3)[2]

            title = {
                'title': title,
                'image': image,
                'id': imdb_id
            }

            movies.append(title)
        return movies

    async def get_title(self, id: str):
        log.debug(f'Scraping for id="{id}"')
        url = f'{title_url}{id}'
        async with self._session.get(url) as response:
            if response.status == 404:
                raise TitleNotFound(f'No such title with id={id}')
            txt = await response.text()

        soup = BeautifulSoup(txt, features='html.parser')

        title = soup.find('h1').contents[0].strip()
        rating = soup.find('div', class_='ratingValue').text.strip()
        rating = float(rating.split('/')[0])
        runtime = soup.find('time').text.strip()
        runtime_mins = Utils.to_minutes(runtime)

        genre_links = soup.find('div', class_='subtext').find_all('a')[:-1]
        genres = [genr.text for genr in genre_links]

        release_date = Utils.get_date(soup)

        divs = soup.find_all('div', class_='credit_summary_item')

        directors = Utils.extract_persons(divs, 'Director')
        writers = Utils.extract_persons(divs, 'Writer')
        creators = Utils.extract_persons(divs, 'Creator')
        stars = Utils.extract_persons(divs, 'Star')

        story_line = soup.find('div', class_='summary_text').text.strip()

        res = {
            'title': title,
            'rating': rating,
            'runtime': runtime,
            'runtime_mins': runtime_mins,
            'genres': genres,
            'release_date': release_date,
            'creators': creators,
            'directors': directors,
            'writers': writers,
            'stars': stars,
            'story_line': story_line,
        }

        return res
