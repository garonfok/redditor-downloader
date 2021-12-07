import argparse
import timeit
import toml
from time import sleep
from datetime import datetime as dt
from downloader import RedditorDownloader


def main():

    __version__ = toml.load("pyproject.toml")["tool"]["poetry"]["version"]

    default_dir = "./redditor-downloader/downloads"

    parser = argparse.ArgumentParser(
        description="Downloads all of a reddit user's image/video submissions."
    )
    parser.add_argument(
        "-v", "--version", help="show version", action="version", version=(__version__)
    )
    parser.add_argument(
        "username", nargs="+", help="the username(s) of the reddit user to download"
    )
    parser.add_argument(
        "-p",
        "--path",
        default=default_dir,
        help=f"the path to download the submissions to (default path: '{default_dir}')",
    )
    parser.add_argument(
        "-I", "--images", help="download image only", action="store_true"
    )
    parser.add_argument("-G", "--gifv", help="download GIFV only", action="store_true")
    parser.add_argument(
        "-V", "--videos", help="download video only", action="store_true"
    )
    parser.add_argument(
        "-c",
        "--continuous",
        metavar="SECONDS",
        type=int,
        help="run this program continuously, waiting for a given number of seconds in between cycles",
    )
    args = parser.parse_args()

    chosen_dir = args.path
    redditors = args.username

    for redditor in redditors:
        client = RedditorDownloader(redditor, chosen_dir)
        client.validate_username()
        client.validate_dir()

    print()

    while True:
        start_time = timeit.default_timer()

        for redditor in redditors:
            print(f"Downloading u/{redditor}'s submissions...")

            client = RedditorDownloader(redditor, chosen_dir)

            if not any([args.images, args.gifv, args.videos]):
                client.download_all()
            if args.images:
                client.download("images")
            if args.gifv:
                client.download("gifv")
            if args.videos:
                client.download("videos")

            print(f"Finished downloading u/{redditor}'s submissions.\n")

        end_time = timeit.default_timer()
        elapsed_time = end_time - start_time
        print(f"Finished in {elapsed_time:.2f} seconds.")
        print(f"Finished downloading requested redditor(s) at {dt.now()}")

        if not args.continuous:
            break
        else:
            print(f"Sleeping for {args.continuous} seconds...")
            sleep(args.continuous)


if __name__ == "__main__":
    main()
