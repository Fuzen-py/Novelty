from setuptools import setup

setup(
    name='Novelty',
    version='1.0.4',
    packages=['Novelty'],
    url='https://github.com/Fuzen-py/Novelty',
    license='MIT',
    author='Fuzen.py',
    author_email='',
    description='Python 3 Aiohttp Novelupdates Scraper',
    long_description='Based on Raitonoberu, Novelty is a Novelupdates scraper to provide a convenient access',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries'
    ],
    keywords="NovelUpdates asyncio aiohttp scraping Novelty",
    install_requires=['aiohttp', 'bs4', 'lxml'],
    entry_points={
        'console_scripts': [
            'novelty=Novelty:main'
        ]
    })
