"""
An Object Based scraper for NovelUpdates to rip information from the page
"""
from .novelty import Novelty
import asyncio
from sys import argv
__version__ = "1.0.4"
__author__ = 'Fuzen.py'
__license__ = 'MIT'
__copyright__ = 'Copyright 2016 Fuzen'
__title__ = 'Novelty'


def main():
    """For command line execution"""
    search = ' '.join(argv[1:]).strip()
    print('Searching for', search, '......')
    n = Novelty()
    loop = asyncio.get_event_loop()
    try:
        print((loop.run_until_complete(n.search(search)))[0].format)
    except IndentationError:
        print('Failed to find results for', search)
