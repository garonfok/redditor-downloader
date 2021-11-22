import praw
import os
import requests
import sys
import yt_dlp
from datetime import datetime as dt
from dotenv import load_dotenv
from hashlib import md5

load_dotenv()


class RedditorDownloader:
    def __init__(self, username, download_dir):
        self.username = username
        self.download_dir = f"{download_dir}/{username}"
        self.reddit = praw.Reddit(
            client_id=os.environ.get("REDDIT_CLIENT_ID"),
            client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
            password=os.environ.get("REDDIT_PASSWORD"),
            user_agent=os.environ.get("REDDIT_USER_AGENT"),
            username=os.environ.get("REDDIT_USERNAME"),
        )

    def download_images(self):
        print("Fetching images...")
        temp_log = []
        download_log = self.get_log()
        path = f"{self.download_dir}/images"
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        for submission in self.reddit.redditor(self.username).submissions.new(
            limit=None
        ):
            if submission.is_self is False:
                time_iso = dt.utcfromtimestamp(submission.created_utc).isoformat()
                file_name = (
                    f'{self.username}-{time_iso}-{submission.url.split("/")[-1]}'
                )

                if (
                    any(i in submission.url for i in ["imgur.com", "i.redd.it"])
                    and not submission.url.endswith(".gifv")
                    and submission.url not in download_log
                    and submission.url not in temp_log
                ):
                    if "/a/" in submission.url:
                        response = requests.get(f"{submission.url}/zip")
                        with open(f"{path}/{file_name}.zip", "wb") as f:
                            f.write(response.content)
                        print(f"Downloaded {submission.url}")
                        with open(f"{self.download_dir}/downloads.log", "a") as f:
                            f.write(f"{submission.url}\n")
                    else:
                        response = requests.get(submission.url)
                        with open(f"{path}/{file_name}", "wb") as f:
                            f.write(response.content)
                        print(f"Downloaded {submission.url}")
                        with open(f"{self.download_dir}/downloads.log", "a") as f:
                            f.write(f"{submission.url}\n")
                    temp_log.append(submission.url)
        print("Finished downloading all images.")
        self.deduplicate(path)

    def download_gifv(self):
        print("Fetching gifv files...")
        temp_log = []
        download_log = self.get_log()
        path = f"{self.download_dir}/gifv"
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        for submission in self.reddit.redditor(self.username).submissions.new(
            limit=None
        ):
            if submission.is_self is False:
                time_iso = dt.utcfromtimestamp(submission.created_utc).isoformat()
                file_name = (
                    f'{self.username}-{time_iso}-{submission.url.split("/")[-1]}'
                )
                yt_opt = {
                    "outtmpl": f"{path}/{file_name}.%(ext)s",
                    "quiet": True,
                    "no_progress": True,
                    "no_warnings": True,
                }

                if (
                    "imgur.com" in submission.url
                    and submission.url.endswith(".gifv")
                    and submission.url not in download_log
                    and submission.url not in temp_log
                ):
                    try:
                        with yt_dlp.YoutubeDL(yt_opt) as ydl:
                            ydl.download([submission.url])
                        print(f"Downloaded {submission.url}")
                    except Exception as e:
                        print(e)
                    print(f"Downloaded {submission.url}")
                    with open(f"{self.download_dir}/downloads.log", "a") as f:
                        f.write(f"{submission.url}\n")
                    temp_log.append(submission.url)
        print("Finished downloading all gifv files as .mp4.")
        self.deduplicate(path)

    def download_videos(self):
        print("Fetching videos...")
        temp_log = []
        download_log = self.get_log()
        path = f"{self.download_dir}/videos"
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        for submission in self.reddit.redditor(self.username).submissions.new(
            limit=None
        ):
            if submission.is_self is False:
                time_iso = dt.utcfromtimestamp(submission.created_utc).isoformat()
                video_id = submission.url.split("/")[-1]
                file_name = f"{self.username}-{time_iso}-{video_id}"
                yt_opt = {
                    "outtmpl": f"{path}/{file_name}.%(ext)s",
                    "quiet": True,
                    "no_progress": True,
                    "no_warnings": True,
                }
                if (
                    any(i in submission.url for i in ["i.redd.it", "redgifs.com"])
                    and submission.url not in download_log
                    and submission.url not in temp_log
                ):
                    try:
                        with yt_dlp.YoutubeDL(yt_opt) as ydl:
                            ydl.download([submission.url])
                        print(f"Downloaded {submission.url}")
                    except Exception as e:
                        print(e)
                    self.log(submission.url)
                    temp_log.append(submission.url)

        print("Finished downloading all videos.")
        self.deduplicate(path)

    def download_all(self):
        self.download_images()
        self.download_gifv()
        self.download_videos()

    def log(self, link):
        with open(f"{self.download_dir}/downloads.log", "a") as f:
            f.write(f"{link}\n")

    def get_log(self):
        with open(f"{self.download_dir}/downloads.log", "r") as f:
            return f.read().splitlines()

    def validate_username(self):
        print(f'Validating username "{self.username}"...')
        try:
            self.reddit.redditor(self.username).id
            print(f'Username "{self.username}" is valid.')
            return
        except Exception as e:
            print(f"Error: Invalid username.")
            sys.exit(1)

    def validate_dir(self):
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir, exist_ok=True)
        if not os.path.exists(f"{self.download_dir}/downloads.log"):
            with open(f"{self.download_dir}/downloads.log", "w") as f:
                f.write("")

    def deduplicate(self, path):
        print("Deduplicating...")
        files = os.listdir(path)

        memo = []
        for file in files:
            with open(f"{path}/{file}", "rb") as f:
                hash = md5(f.read()).hexdigest()
                if hash in memo:
                    print(f"Duplicate found! Removing {path}/{file}")
                    os.remove(f"{path}/{file}")
                else:
                    memo.append(hash)
        print("Finished dedeuplicating.")
