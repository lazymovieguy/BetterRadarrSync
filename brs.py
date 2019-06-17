#!/usr/bin/env python

import requests
import json
from dateutil.parser import parse as date_parse
from dateutil.tz import tzutc
from datetime import datetime
from datetime import timezone
from time import sleep
import logging
import sys
import argparse
import urllib.parse
import signal

logger = logging.getLogger('brs')


class RadarrMovie:
    def __init__(self, title, added, qualityProfileId, titleSlug, tmdbId, path, monitored, images, profileId, year):
        self.title = title
        self.added = self._convert_date(added)
        self.qualityProfileId = qualityProfileId
        self.titleSlug = titleSlug
        self.tmdbId = tmdbId
        self.path = path
        self.monitored = monitored
        self.images = images
        self.profileId = profileId
        self.year = year

    def set_profile(self, profileId: int):
        self.qualityProfileId = profileId
        self.profileId = profileId

    def _convert_date(self, iso_8601):
        return date_parse(iso_8601)

    def __str__(self):
        return(str({'title': self.title,
                    'added': str(self.added),
                    'qualityProfileId': self.qualityProfileId,
                    'titleSlug': self.titleSlug,
                    'tmdbId': self.tmdbId,
                    'path': self.path,
                    'monitored': self.monitored,
                    'images': self.images,
                    'profileId': self.profileId,
                    'year': self.year}
                   )
               )

    def to_json(self):
        t = {
            'title': self.title,
            'qualityProfileId': self.qualityProfileId,
            'titleSlug': self.titleSlug,
            'tmdbId': self.tmdbId,
            'path': self.path,
            'monitored': self.monitored,
            'images': self.images,
            'profileId': self.profileId,
            'minimumAvailability': 'released',
            'year': self.year

        }
        logger.debug("t")
        return json.dumps(t)

    def __hash__(self):
        return self.tmdbId[0]

    def __eq__(self, other):
        return self.tmdbId == other.tmdbId


class RadarrServer:
    def __init__(self, scheme, host, port, key):
        self.scheme = scheme
        self.host = host
        self.port = port
        self.key = key
        self.session = requests.Session()
        self.profiles = self._get_profiles()
        self.sync_profile = None
        self.movies = []
        self.last_sync = None

    def setup(self):
        self.movies = []
        r = self.session.get("{}://{}:{}/api/movie?apikey={}".format(
            self.scheme,
            self.host,
            self.port,
            self.key)
        )
        self.last_sync = datetime.now(tzutc())
        for movie in r.json():
            parsed_movie = self._parse_movie(movie)
            logger.debug("Adding {} to {} inventory".format(
                parsed_movie.title, self.host))
            self.movies.append(parsed_movie)

    def drop_movies(self):
        self.movies = []

    def _parse_movie(self, movie):
        m = RadarrMovie(movie['title'],
                        movie['added'],
                        movie['qualityProfileId'],
                        movie['titleSlug'],
                        movie['tmdbId'],
                        movie['path'],
                        movie['monitored'],
                        movie['images'],
                        movie['profileId'],
                        movie['year']
                        )
        return m

    def add_movie(self, movie: RadarrMovie):
        movie.set_profile(self.profiles['HD-720p'])
        logger.debug(movie.to_json())
        self.session.post("{}://{}:{}/api/movie?apikey={}".format(
            self.scheme,
            self.host,
            self.port,
            self.key),
            data=movie.to_json()
        )

    def _get_profiles(self):
        r = self.session.get("{}://{}:{}/api/profile?apikey={}".format(
            self.scheme,
            self.host,
            self.port,
            self.key)
        )
        profiles = {}
        for profile in r.json():
            profiles[profile['name']] = profile['id']
        return profiles


class BetterRaddarSync:
    def __init__(self):
        self.setup_logger()
        parser = argparse.ArgumentParser(
            description='BetterRadarrSync',
            usage='''brs <command> [<args>]

The most commonly used brs commands are:
   profiles     Lists profiles on a Radarr Instance
   syncronize         Syncs movies matching a profile from instance x to instance y
   help         Invokes help command
''')
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def profiles(self):
        parser = argparse.ArgumentParser(
            description='Lists profiles on a Radarr Instance')
        parser.add_argument('url',
                            help='Radarr url to list profiles from; Ex.http://127.0.0.1',
                            type=str)
        parser.add_argument('--port',
                            help='Port to use; Default: 80',
                            type=int, default=80)
        parser.add_argument('key',
                            help='API key', type=str)
        parser.add_argument('-v',
                            help='Verbosity Level; Default: INFO',
                            choices=['INFO', 'WARNING', 'ERROR', 'CRITICAL', 'DEBUG'], default='INFO')
        args = parser.parse_args(sys.argv[2:])
        if vars(args)['v'] is not 'INFO':
            self.set_log_level(vars(args)['v'])
        url = self.parse_url(vars(args)['url'])
        source = RadarrServer(url.scheme, url.netloc, vars(args)[
                              'port'], vars(args)['key'])
        source.setup()
        print(','.join(list(source.profiles.keys())))

    def syncronize(self):
        parser = argparse.ArgumentParser(
            description='Syncs movies matching a profile from instance x to instance y')
        parser.add_argument('src-url',
                            help='Radarr url to sync from; Ex.http://127.0.0.1',
                            type=str)
        parser.add_argument('--src-port',
                            help='Port to use; Default: 80',
                            type=int, default=80)
        parser.add_argument('src-key',
                            help='API key', type=str)
        parser.add_argument('--src-profile',
                            help='Profile to sync; Default: Ultra-HD',
                            type=str, default='Ultra-HD')
        parser.add_argument('dest-url',
                            help='Radarr url to sync to; Ex. http://127.0.0.1')
        parser.add_argument('--dest-port',
                            help='Port to use; Default: 80',
                            type=int, default=80)
        parser.add_argument('dest-key',
                            help='API key', type=str)
        parser.add_argument('--dest-profile',
                            help='Profile to sync; Default: HD-720p',
                            type=str, default='HD-720p')
        parser.add_argument('-v',
                            help='Verbosity Level; Default: INFO',
                            choices=['INFO', 'WARNING', 'ERROR', 'CRITICAL', 'DEBUG'], default='INFO')
        args = parser.parse_args(sys.argv[2:])
        if vars(args)['v'] is not 'INFO':
            self.set_log_level(vars(args)['v'])

        src_url = self.parse_url(vars(args)['src-url'])
        dest_url = self.parse_url(vars(args)['dest-url'])

        # Create connections and setup
        source = RadarrServer(src_url.scheme, src_url.netloc, vars(args)[
                              'src_port'], vars(args)['src-key'])
        source.sync_profile = vars(args)['src_profile']
        dest = RadarrServer(dest_url.scheme, dest_url.netloc, vars(args)[
                            'dest_port'], vars(args)['dest-key'])
        dest.sync_profile = vars(args)['dest_profile']
        sync(source, dest)

    def parse_url(self, url):
        return urllib.parse.urlparse(url)

    def setup_logger(self):
        # Setup Logging
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
        logger.info("Starting Up")

    def set_log_level(self, level):
        logger.info("Switching log level to: {}".format(level))
        logger.setLevel(level)


def sync(source, dest):
    dest.setup()
    last_sync = datetime.now(tzutc())
    while True:
        sleep(1)
        sync_start = datetime.now(tzutc())
        source.setup()
        for movie in source.movies:
            if movie.profileId == source.profiles['Ultra-HD'] and movie not in dest.movies:
                logger.info("Adding {} to {}".format(movie.title, dest.host))
                dest.add_movie(movie)
                logger.info("Added {} to {}".format(movie.title, dest.host))
                dest.setup()
        logger.info("Sync took {}".format(datetime.now(tzutc()) - sync_start))
        source.last_sync = sync_start


def signal_handler(signal, frame):
    print('Shutting down!')
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    BetterRaddarSync()