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

    def download(self, download_flags: int):
        print(f"Fetching posts...")
        temp_log = []  # Account for duplicate posts/crossposts
        download_log = (
            self.get_log()
        )  # Permanently account for duplicate posts/crossposts
        bin_flags = bin(download_flags)[2::]  # Convert to binary
        for submission in self.reddit.redditor(self.username).submissions.new(
            limit=None
        ):
            if (
                submission.is_self is False  # Check if post is text only
                and submission.url not in download_log
                and submission.url not in temp_log
            ):

                time_iso = (
                    dt.utcfromtimestamp(submission.created_utc)
                    .isoformat()
                    .replace(":", ".")
                )  # Modified ISO8601 Format (YYYY-DD-MMTHH.MM.SS) for file parsing
                file_name = (
                    f'{time_iso}-{self.username}-{submission.url.split("/")[-1]}'
                )

                if (
                    bin_flags[0] == "1"
                    and any(i in submission.url for i in ["imgur.com", "i.redd.it"])
                    and not submission.url.endswith(".gifv")
                ):  # Check if post is an image
                    path = f"{self.download_dir}/images"
                    if "/a/" in submission.url:  # Check if post is an image album
                        response = requests.get(
                            f"{submission.url}/zip"
                        )  # TODO: Fix handling Imgur albums, currently inconsistent support
                        with open(f"{path}/{file_name}.zip", "wb") as f:
                            f.write(response.content)
                    else:
                        response = requests.get(submission.url)
                        with open(f"{path}/{file_name}", "wb") as f:
                            f.write(response.content)
                    print(f"Downloaded {submission.url}")
                    temp_log.append(submission.url)
                if (
                    bin_flags[1] == "1"
                    and any(i in submission.url for i in ["imgur.com"])
                    and submission.url.endswith(".gifv")
                ): # Check if post is a gifv
                    path = f"{self.download_dir}/gifv"
                    yt_opt = {
                        "outtmpl": f"{path}/{file_name}.%(ext)s",
                        "quiet": True,
                        "no_progress": True,
                        "no_warnings": True,
                    }
                    try:
                        with yt_dlp.YoutubeDL(yt_opt) as ydl:
                            ydl.download([submission.url])
                        print(f"Downloaded {submission.url}")
                    except Exception as e:
                        print(e)
                    temp_log.append(submission.url)
                if bin_flags[2] == "1" and any(
                    i in submission.url
                    for i in [
                        "v.redd.it",
                        "gifycat.com",
                        "redgifs.com",
                    ]
                ): # Check if post is a video
                    path = f"{self.download_dir}/videos"
                    yt_opt = {
                        "outtmpl": f"{path}/{file_name}.%(ext)s",
                        "quiet": True,
                        "no_progress": True,
                        "no_warnings": True,
                    }
                    try:
                        with yt_dlp.YoutubeDL(yt_opt) as ydl:
                            ydl.download([submission.url])
                        print(f"Downloaded {submission.url}")
                    except Exception as e:
                        print(e)
                    temp_log.append(submission.url)
        for _ in temp_log:
            self.log(_)
        print(f"Finished downloading posts.")

        if bin_flags[0] == "1":
            self.deduplicate(f"{self.download_dir}/images")
        if bin_flags[1] == "1":
            self.deduplicate(f"{self.download_dir}/gifv")
        if bin_flags[2] == "1":
            self.deduplicate(f"{self.download_dir}/videos")

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
            print(e)
            print(f"Error: Invalid username.")
            sys.exit(1)

    def validate_dir(self):
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir, exist_ok=True)
        if not os.path.exists(f"{self.download_dir}/downloads.log"):
            with open(f"{self.download_dir}/downloads.log", "w") as f:
                f.write("")
        paths = [
            f"{self.download_dir}/images",
            f"{self.download_dir}/gifv",
            f"{self.download_dir}/videos",
        ]
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)

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
