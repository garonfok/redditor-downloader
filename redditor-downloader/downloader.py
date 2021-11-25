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

    def download(self, media_type):
        print(f"Fetching {media_type}...")
        temp_log = []
        download_log = self.get_log()
        path = f"{self.download_dir}/{media_type}"
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        for submission in self.reddit.redditor(self.username).submissions.new(
            limit=None
        ):
            if (
                submission.is_self is False
                and submission.url not in download_log
                and submission.url not in temp_log
            ):
                time_iso = dt.utcfromtimestamp(submission.created_utc).isoformat()
                file_name = (
                    f'{time_iso}-{self.username}-{submission.url.split("/")[-1]}'
                )
                if media_type == "images":
                    if any(
                        i in submission.url for i in ["imgur.com", "i.redd.it"]
                    ) and not submission.url.endswith(
                        ".gifv"
                    ):  # Conditional operator broken up to maintain consistency with video/gifv download
                        if "/a/" in submission.url:
                            response = requests.get(f"{submission.url}/zip")
                            with open(f"{path}/{file_name}.zip", "wb") as f:
                                f.write(response.content)
                        else:
                            response = requests.get(submission.url)
                            with open(f"{path}/{file_name}", "wb") as f:
                                f.write(response.content)
                        print(f"Downloaded {submission.url}")
                        self.log(submission.url)
                        temp_log.append(submission.url)
                else:  # Videos and GIFV
                    yt_opt = {
                        "outtmpl": f"{path}/{file_name}.%(ext)s",
                        "quiet": True,
                        "no_progress": True,
                        "no_warnings": True,
                    }
                    if (
                        media_type == "gifv"
                        and any(
                            i in submission.url for i in ["imgur.com"]
                        )  # Written for future expandability
                        and submission.url.endswith(".gifv")
                    ):
                        try:
                            with yt_dlp.YoutubeDL(yt_opt) as ydl:
                                ydl.download([submission.url])
                            print(f"Downloaded {submission.url}")
                        except Exception as e:
                            print(e)
                        self.log(submission.url)
                        temp_log.append(submission.url)
                    elif media_type == "videos" and any(
                        i in submission.url
                        for i in [
                            "v.redd.it",
                            "i.redd.it",
                            "gifycat.com",
                            "redgifs.com",
                        ]
                    ):
                        try:
                            with yt_dlp.YoutubeDL(yt_opt) as ydl:
                                ydl.download([submission.url])
                            print(f"Downloaded {submission.url}")
                        except Exception as e:
                            print(e)
                        self.log(submission.url)
                        temp_log.append(submission.url)

        print(f"Finished downloading {media_type}.")
        self.deduplicate(path)

    def download_all(self):
        self.download("images")
        self.download("gifv")
        self.download("videos")

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
