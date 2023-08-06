This script is designed to browse Reddit subreddits based on user input, gather the top, hot, or rising posts (also based on user input), and create HTML templates for these posts. These HTML templates are then used to take screenshots for visualizing the post data.
Requirements

    Python 3.6 or above
    Node.js
    Playwright (Node.js library)
    PRAW (Python Reddit API Wrapper)
    Jinja2 (Python templating library)
    Python-dotenv (Python library to read environment variables)

TODO:
```
  Create automated video's with captions
```


Installation

```
git clone https://github.com/realAndi/SubRedditStoriesFinder/
```


Install the required Python dependencies.
```
pip install praw jinja2 python-dotenv
```

Install Node.js if it is not already installed. 

Install Playwright via npm (Node.js package manager).
```
 npm install playwright
```
Setup

    Create a new Reddit 'script' application from here. Note the client_id and client_secret.

    In the root directory of the project, create a .env file.

    Add your Reddit credentials to the .env file. Replace 'your_client_id' and 'your_client_secret' with your actual Reddit credentials.

    arduino

    REDDIT_CLIENT_ID='your_client_id'
    REDDIT_CLIENT_SECRET='your_client_secret'

Usage

Run the script main.py and follow the on-screen prompts. The script will ask you for:

    The subreddit you want to browse.

    How you want to sort the posts (Hot, Rising, Top).

    A threshold for upvotes (only posts with upvotes above this number will be included).


After running the script, it will save a .json file with the data from the posts. It will also create a directory with HTML templates for each post and a corresponding screenshot.
Note

    Never share your Reddit client ID and secret or push them to a public repository.
    If you're not familiar with creating a Reddit application to get your client_id and client_secret, you can find more information in the PRAW documentation.

