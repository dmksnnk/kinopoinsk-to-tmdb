
Script to import votes and watchlist from [kinopoisk](https://kinopoisk.ru) to [TMDB](https://www.themoviedb.org).

## Requirements

First, install requirements:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python kinopoisk-to-tmdb.py [OPTIONS] FILENAME
```

Options are:

```
  -w, --what [votes|watchlist]  What to import from file  required]
  -k, --api-key TEXT            API key from TMDB  [required]
  -u, --username TEXT           Username for TMDB account  [required]
  -p, --password TEXT           Password for TMDB account  [required]
```