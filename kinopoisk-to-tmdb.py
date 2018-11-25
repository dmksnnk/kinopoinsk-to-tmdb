import csv
import logging

import click
import requests
import tmdbsimple as tmdb

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class KPToTMDB:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.search = tmdb.Search()
        self._session_id = None
        self._acc = None

    def get_session_id(self):
        if not self._session_id:
            self._session_id = self._auth()
        return self._session_id

    def get_account(self):
        if not self._acc:
            self._acc = self._create_account()
        return self._acc

    def _auth(self):
        auth = tmdb.Authentication()
        auth.token_new()
        logger.info(f'Got token: {auth.request_token}')
        auth.token_validate_with_login(
            request_token=auth.request_token,
            username=self.username,
            password=self.password
            )
        auth.session_new(request_token=auth.request_token)
        logger.info(f'Got session: {auth.session_id}')
        return auth.session_id

    def _create_account(self):
        acc = tmdb.Account(self.get_session_id())
        info = acc.info()  # must do this
        logger.info(f'Acc info: {info}')
        return acc

    def get_movie_id(self, name):
        self.search.movie(query=name)
        try:
            return self.search.results[0]['id']
        except (IndexError, KeyError):
            return None

    @staticmethod
    def _get_watched_movies(filename):
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name = row[0]
                if name:
                    yield name

    def add_to_watchlist(self, movie_id):
        acc = self.get_account()
        try:
            r = acc.watchlist(media_id=movie_id, watchlist=True, media_type='movie')
        except requests.exceptions.HTTPError:
            logger.warning(f'HTTP Error for "{movie_id}"')
            return False
        else:
            logger.info(f'Movie "{movie_id}", ID {movie_id}. Status \"{r["status_message"]}\"')
            return True

    def add_to_watchlist_from(self, filename):
        failed = []
        for title in self._get_watched_movies(filename):
            movie_id = self.get_movie_id(title)
            if not movie_id:
                logger.warning(f'Can\'t find movie "{title}"')
                failed.append(title)
                continue

            ok = self.add_to_watchlist(movie_id)
            if not ok:
                failed.append(title)

        return failed

    @staticmethod
    def _get_rated_movies(filename):
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for name, rating in reader:
                if name:
                    yield name, rating

    def rate_movie(self, movie_id, rating):
        movie = tmdb.Movies(movie_id)
        try:
            r = movie.rating(session_id=self.get_session_id(), value=rating)
        except requests.exceptions.HTTPError:
            logger.warning(f'HTTP Error for "{movie_id}"')
            return False
        else:
            logger.info(f'Movie ID {movie_id} has been rated {rating}. Status \"{r["status_message"]}\"')
            return True

    def rate_movies_from(self, filename):
        failed = []
        for title, rating in self._get_rated_movies(filename):
            movie_id = self.get_movie_id(title)
            if not movie_id:
                logger.warning(f'Can\'t find movie "{title}"')
                failed.append(title)
                continue

            ok = self.rate_movie(movie_id, rating)
            if not ok:
                failed.append(title)
        return failed

@click.command()
@click.argument('filename', type=click.Path(exists=True, resolve_path=True, readable=True))
@click.option('-w', '--what', type=click.Choice(['votes', 'watchlist']), required=True, help='What to import from file')
@click.option('-k', '--api-key', type=str, required=True, help='API key from TMDB')
@click.option('-u', '--username', type=str, required=True, help='Username for TMDB account')
@click.option('-p', '--password', type=str, required=True, help='Password for TMDB account')
def main(filename, what, api_key, username, password):
    """Import votes or watchlist from FILENAME."""
    tmdb.API_KEY = api_key
    ktt = KPToTMDB(username, password)
    if what == 'votes':
        failed = ktt.rate_movies_from(filename)
    elif what == 'watchlist':
        failed = ktt.add_to_watchlist_from(filename)

    click.echo('Failed:\n{}'.format('\n'.join(failed)))


if "__name__" == main():
    main()
