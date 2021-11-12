import argparse
import time
from downloader import RedditorDownloader


if __name__ == "__main__":

    default_dir = "./redditor-downloader/downloads"

    parser = argparse.ArgumentParser(
        description="Downloads all of a reddit user's image/video submissions."
    )
    parser.add_argument("username", help="the username of the reddit user to download.")
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
        "-c", "--continuous", help="run this program forever", action="store_true"
    )
    args = parser.parse_args()

    chosen_dir = args.path
    redditor = args.username

    RedditorDownloader(redditor, chosen_dir).validate_username()

    client = RedditorDownloader(redditor, chosen_dir)

    client.validate_dir()

    while(True):
        if not any([args.images, args.gifv, args.videos]):
            client.download_all()
        if args.images:
            client.download_images()
        if args.gifv:
            client.download_gifv()
        if args.videos:
            client.download_videos()

        if not args.continuous:
            break
        else:
            print("Sleeping for 5 minutes...")
            time.sleep(300) # 5 minutes
