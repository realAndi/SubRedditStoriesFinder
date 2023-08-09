# Reddit to Mobile Short Videos

This script is designed to browse Reddit subreddits based on user input, gather the top, hot, or rising posts (also based on user input), and create HTML templates for these posts. These HTML templates are then used to take screenshots for visualizing the post data.

# Requirements

    Python 3.10 or above
    Node.js
    Reddit Account
    ffmpeg

### TODO:
```
  Make animated captions bounce in
  Use AI to make post revisions and determine if to was written by a male or female.
  Different solution for title cards.
```

# Installation

Clone the repo
```
git clone https://github.com/realAndi/SubRedditStoriesFinder/
```


Install the required Python dependencies.
```
pip install -r requirements.txt
```

Install Node.js if it is not already installed. 

Install Playwright via npm (Node.js package manager).
```
 npm install playwright
```
# Setup

    Create a new Reddit 'script' application from here. Note the client_id and client_secret.

    In the root directory of the project, create a .env file.

    Add your Reddit credentials to the .env file. Replace 'your_client_id' and 'your_client_secret' with your actual Reddit credentials.

    REDDIT_CLIENT_ID='your_client_id'
    REDDIT_CLIENT_SECRET='your_client_secret'

# Usage

## Step 1

Run the script main.py and follow the on-screen prompts. The script will ask you for:

    The subreddit you want to browse.

    How you want to sort the posts (Hot, Rising, Top).

    A threshold for upvotes (only posts with upvotes above this number will be included).


After running the script, it will save a .json file with the data from the posts. It will also create a directory with HTML templates for each post and a corresponding screenshot.
Note

    Never share your Reddit client ID and secret or push them to a public repository.
    If you're not familiar with creating a Reddit application to get your client_id and client_secret, you can find more information in the PRAW documentation.

Saving screenshots is a Node.js function. Yes its a backwards solution, but I believe it's fun to do it like this. If you want to customize the layout, play with the folder "WebPage" and see the title card you can make!

## Step 2

After scraping the desired subreddit, run `main.py` again and select the 2nd option. In the 2nd option, you will be prompted to select a voice type, male or female. Depending on the content given, you should choose accordingly. The script will remind you to manually look over the `post_content.txt` to make sure there isn't anything that can potentially disrupt the TTS. Things such as special characters, extra periods, typo's. Once that's done, you will get a large output of audio files in the subfolders. Please don't delete them.

## Step 3

After grabbing the necessary audio files, go ahead and run `main.py` and select the 3rd option. The 3rd option will by default download a minecraft parkour video (Thank you bbswitzer), and select a random segment to start from. It will as well crop the video for mobile devices, and attach captions. The process should take upto 3 minutes max.
