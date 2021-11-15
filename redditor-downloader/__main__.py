import argparse
import time
from downloader import RedditorDownloader


if __name__ == "__main__":

    default_dir = "./redditor-downloader/downloads"

    parser = argparse.ArgumentParser(
        description="Downloads all of a reddit user's image/video submissions."
    )
    parser.add_argument(
        "username", nargs="+", help="the username(s) of the reddit user to download."
    )
    parser.add_argument(
        "-p",
        "--path",
        default=default_dir,
        help=f"the path to download the submissions to (default path: '{default_dir}').",
    )
    parser.add_argument(
        "-I", "--images", help="download images only", action="store_true"
    )
    parser.add_argument(
        "-G", "--gifv", help="download GIFV files only", action="store_true"
    )
    parser.add_argument(
        "-V", "--videos", help="download videos only", action="store_true"
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
        for redditor in redditors:
            print(f"Downloading u/{redditor}'s submissions...")

            client = RedditorDownloader(redditor, chosen_dir)

            if not any([args.images, args.gifv, args.videos]):
                client.download_all()
            if args.images:
                client.download_images()
            if args.gifv:
                client.download_gifv()
            if args.videos:
                client.download_videos()

            print(f"Finished downloading u/{redditor}'s submissions.\n")

        if not args.continuous:
            break
        else:
            print(f"Sleeping for {args.continuous} seconds...")
            time.sleep(args.continuous)
