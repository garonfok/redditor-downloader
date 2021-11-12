# Redditor-Downloader

Redditor-Downloader is a command-line tool used to download the image, gifv, or video posts of any given Redditor.

## Summary

- [Redditor-Downloader](#redditor-downloader)
  - [Summary](#summary)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installing](#installing)
    - [Environment Variables](#environment-variables)
    - [Poetry](#poetry)
    - [Pip](#pip)
  - [Usage](#usage)
  - [Changelog](#changelog)
  - [Built With](#built-with)
  - [License](#license)

## Features

- Customizable the detination path
- Automatically checks for and deletes duplicate files
- Have the program automatically run forever

## Requirements

This project was built with Poetry. However, you can install the necessary requirements using pip.

- Python 3.9.7+
- [Poetry](https://python-poetry.org) or [Pip](https://pypi.python.org/project.pip)
- [Reddit API Key](https://praw.readthedocs.io/en/stable/getting_started/authentication.html#oauth)

## Installing

### Environment Variables

Rename ".env.example" to ".env", and fill in the corresponding variable information from your Reddit API Key.

### Poetry

```shell
poetry install

```

### Pip

```shell
pip install -r requirements.txt

```

## Usage

```shell
python redditor-downloader [-h] [-p PATH] [-I] [-G] [-V] [-c] username
```

```shell
positional arguments:
  username              the username of the reddit user to download.

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  the path to download the submissions to (default path:
                        './redditor-downloader/downloads').
  -I, --images          download images only
  -G, --gifv            download GIFV files only
  -V, --videos          download videos only
  -c, --continuous      run this program forever
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

## Built With

- [Contributor Covenant](https://www.contributor-covenant.org/) - Used for the Code of Conduct
- [MIT](https://opensource.org/licenses/MIT) - Used to choose the license

## License

This project is licensed under the [MIT](LICENSE)
License.
