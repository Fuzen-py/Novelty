#!/bin/env python3
"""Novel Updates Data Fetching"""
import asyncio
from bs4 import BeautifulSoup
import aiohttp
from sys import argv


class Novel:
    """Novel Object"""

    def __init__(self, **kwargs):
        """Creation of Novel Object"""
        for k in kwargs.keys():
            setattr(self, k, kwargs.get(k))
        self.__dict__ = kwargs

    @property
    def format(self):
        return ('{self.title}\n'
                'Aliases: {self.aliases}\n'
                'Type: {self.type}\n'
                'Rating: {self.rating}\n'
                'Year: {self.year}\n'
                'Authors: {self.authors}\n'
                'Tags: {self.tags}\n'
                'Publisher: {self.publisher}\n'
                'English Publisher: {self.english_publisher}\n'
                'Description:\n'
                '{self.description}\n\n\n'
                'Licensed: {self.licensed}\n'
                'Novel Status: {self.novel_status}\n'
                'Completely Translated: {self.completely_translated}\n'
                'Cover: {self.cover}\n'
                'Artists: {self.artists}\n'
                'Link: {self.link}\n').format(self=self)


class Novelty:
    # Baseurl for novelupdates
    BASEURL = 'http://www.novelupdates.com/'

    def __init__(self, user_agent=None, session=None):
        # Set default user-agent
        self.headers = user_agent or {"User-Agent": "RSS Reader"}
        self.loop = asyncio.get_event_loop()
        # Give the user the option of using their own client session
        self.session = session or aiohttp.ClientSession(headers=self.headers,
                                                        loop=self.loop)
        self.__cache__ = {}

    def __del__(self):
        self.session.close()
        if not self.loop.is_closed():
            self.loop.close()

    async def __search(self, term: str, max_results: int=1, sleep_time: int=7, interval: int=4):
        search = []
        page_range = []
        async with self.session.get(self.BASEURL,
                                    params={'s': term,
                                            'post_type': 'seriesplan'}) as r:
            # If the response is 200 OK
            if r.status == 200:
                soup = BeautifulSoup(await r.text(), 'lxml')
                search += [x.get('href')
                           for x in soup.find_all(
                              'a', class_='w-blog-entry-link')
                           if x is not None][0: max_results]
                if not (max_results >= 17):
                    pages = soup.find_all('a', class_='page-numbers')
                    if len(pages) > 0:
                        possible_pages = []
                        for x in pages:
                            if x.span is not None and x.span.string is not None and x.span.string.isdigit():
                                possible_pages.append(int(x.span.string))
                        if len(possible_pages) > 0:
                            max_pages = 1
                            for p in possible_pages:
                                if p > max_pages:
                                    max_pages = p
                            if max_results != -1:
                                while (
                                        max_pages * 10) - max_results > max_results:
                                    max_pages -= 1
                        page_range += list(range(2, max_pages + 1))
                        # Return the link that we need
            else:
                # Raise an error with the response status
                raise aiohttp.ClientResponseError(r.status)
        if len(page_range) == 0:
            return search
        else:
            counter = 0
            for page in page_range:
                counter += 1
                async with self.session.get(url='{}/page/{}/'.format(self.BASEURL, page),
                                            params={'s': term, 'post_type': 'seriesplan'}) as r:
                    if r.status == 200:
                        soup = BeautifulSoup(await r.text(), 'lxml')
                        search += [x.get('href')
                                   for x in soup.find_all(
                                      'a', class_='w-blog-entry-link')
                                   if x is not None][0: max_results]
                    else:
                        raise aiohttp.ClientResponseError(r.status)
            if counter % interval == 0:
                await asyncio.sleep(sleep_time)
        return list(set(search))

    async def search(self, term: str, max_results: int=1, as_dict: bool=False, sleep_time: int=7,
                     interval: int=4):
        """
        This function parses information from __search returns and then return it as a object in a list/dict.

        :param sleep_time: How many seconds to sleep every X searches
        :param interval: Perform sleep every x searches
        :param term: The novel to search for and parse.
        :param max_results: Maximum results returned (if set to 0, will return all).
        :param as_dict: if as_dict is true, it will return as a dict with the Title as a key else, it returns as a list
        """
        # Type Checking
        assert isinstance(term, str)
        assert isinstance(max_results, (float, int))
        assert isinstance(as_dict, bool)
        assert max_results >= 0
        #Set Max Results to Unlimited if 0
        if max_results == 0:
            max_results = -1
        results = []
        search = await self.__search(term=term, max_results=max_results, sleep_time=sleep_time, interval=interval)
        counter = 0
        if len(search) >= 4:
            print('Will take at least',
                  int(str(float(len(search) / interval)).rsplit('.',
                                                                maxsplit=1)[0]) * sleep_time,
                  'to parse. sleeps',
                  sleep_time,
                  'seconds every',
                  interval,
                  'searches')

        for url in search:
            counter += 1
            async with self.session.get(url) as r:
                # If the response is OK
                if r.status == 200:
                    # The information to parse
                    parse_info = BeautifulSoup(await r.text(), 'lxml')
                    # Error Prevention
                    artists = parse_info.find(
                        'a', class_='genre', id='artiststag')
                    if artists is not None:
                        artists = artists.string
                    english_publisher = parse_info.find(
                        'a', class_='genre', id='myepub')
                    if english_publisher is not None:
                        try:
                            english_publisher = english_publisher.children.string
                        except AttributeError:
                            english_publisher = ' '.join(
                                str(x) for x in list(english_publisher))
                    # cannot be found.
                    publisher = parse_info.find(
                        'a', class_='genre', id='myopub')
                    if publisher is not None:
                        publisher = publisher.string
                    licensed = parse_info.find('div', id='showlicensed').string
                    if licensed is not None:
                        licensed = True if licensed.strip() == 'Yes' else False
                    year = parse_info.find('div', id='edityear').string
                    if year is not None:
                        year = year.strip()
                    novel_status = parse_info.find(
                        'div', id='editstatus').string
                    if novel_status is not None:
                        novel_status = novel_status.strip()
                    _type = parse_info.find('a', class_='genre type')
                    if _type is not None:
                        _type = _type.string
                    rating = parse_info.find(class_='uvotes')
                    if rating is not None:
                        rating = rating.string
                    # Creat Novel Object and Append to list
                    results.append(Novel(title=parse_info.find('h4', class_='seriestitle new').string,
                                         cover=None if parse_info.find('img').get(
                                             'src') == 'http://www.novelupdates.com/img/noimagefound.jpg' else
                                         parse_info.find('img').get('src'),
                                         type=_type,
                                         genre=[x.string.strip() for x in
                                                list(parse_info.find_all('div', id='seriesgenre')[0].children) if
                                                (x.string is not None) and len(x.string.strip()) > 0],
                                         tags=[x.string.strip() for x in
                                               list(parse_info.find_all('div', id='showtags')[0].children) if
                                               (x.string is not None) and len(x.string.strip()) > 0],
                                         language=parse_info.find('a', class_='genre lang').string,
                                         authors=list(set(
                                             [x.string.strip() for x in parse_info.find_all('a', id='authtag') if
                                              x.string is not None])),
                                         artists=artists,
                                         year=year,
                                         novel_status=novel_status,
                                         licensed=licensed,
                                         completely_translated=True if len(list(
                                             parse_info.find('div', id='showtranslated').descendants)) > 1 else False,
                                         publisher=publisher,
                                         english_publisher=english_publisher,
                                         description=' '.join([x.string.strip() for x in list(
                                             parse_info.find('div', id='editdescription').children) if
                                                               x.string is not None]),
                                         aliases=[x.string.strip() for x in parse_info.find('div', id='editassociated')
                                                  if
                                                  x.string is not None],
                                         link=url,
                                         rating=rating))
                    if len(search) > counter:
                        if counter % interval == 0:
                            await asyncio.sleep(sleep_time)
                else:
                    # Raise an error with the response status
                    raise aiohttp.ClientResponseError(r.status)
        if as_dict:
            # Make Results a dict
            old_results = results
            results = {}
            for novel in old_results:
                results[novel.title] = novel
        return results

    @staticmethod
    def format(results: list):
        assert isinstance(results, (list, dict))
        v = []
        if isinstance(results, dict):
            for x in results.keys():
                v.append(results.get(x))
        else:
            v = results
        msg = 'Results:\n'
        counter = 1
        for x in v:
            msg += ('{counter}. {x.title}\n'
                    'Aliases: {x.aliases}\n\',\n'
                    'Type: {x.type}\n'
                    'Rating: {x.rating}\n'
                    'Authors: {x.authors}\n'
                    'Tags: {x.tags}\n'
                    'Publisher: {x.publisher}\n'
                    'English Publisher: {x.english_publisher}\n'
                    'Description:\n'
                    '{x.description}\n'
                    '\n'
                    '\n'
                    'Licensed: {x.licensed}\n'
                    'Novel Status: {x.novel_status}\n'
                    'Completely Translated: {x.completely_translated}\n'
                    'Cover: {x.cover}\n'
                    'Artists: {x.artists}\n'
                    'Link: {x.link}\n').format(counter=counter, x=x)
        return msg


def main():
    search = ' '.join(argv[1:]).strip()
    print('Searching for', search, '......')
    N = Novelty()
    loop = asyncio.get_event_loop()
    try:
        print((loop.run_until_complete(N.search(search)))[0].format)
    except IndentationError:
        print('Failed to find results for', search)

if __name__ == '__main__':
    main()
