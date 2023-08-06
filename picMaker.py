import json
import os
import subprocess
from jinja2 import Template
from pathlib import Path


def load_json(filepath):
    if not os.path.isfile(filepath):
        print("The provided file path does not exist. Please try again.")
        return None

    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("The provided file is not valid JSON. Please try again.")
        return None



def format_count(count):
    return f"{count / 1000:.1f}k" if count >= 1000 else str(count)

html_template = Template("""
<!DOCTYPE html>
<html>
<head>
    <title>Minimal Page</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" />
</head>
<style>
body {
  background-color: rgb(135, 50, 50);
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  flex-direction: column;
  font-family:  Helvetica;

}

.container {
  min-height: 350px;
  display: flex;
  flex-direction: column;
  position: relative;
  padding: 30px;
}
.post-container{
  display: flex;
  flex-direction: row;
  max-width: 900px;                          
}

.mini-rectangle {
  background-color: white;
  display: flex;
  justify-content: left;
  flex-direction: row-reverse;
  padding: 0px 2px;
  width: auto;
  position: absolute;
  top: 0;
  box-shadow: 0px 10px 15px rgba(0, 0, 0, 0.2);

}

.post-awards-and-location {
  padding: 5px 0px;
  display: flex;
  flex-direction: row;
  font-size: 31px;
  align-items: center;
  color: rgb(166, 166, 166);
}

.post-awards{
  display: flex;
  padding: 0 15px;
  flex-direction: row;
}

.post-awards img {
  padding: 0 3px;
}

.mini-text {
  font-size: 30px;
  color: rgb(68, 68, 68);
  padding: 0;
}

.rectangle {
  background-color: white;
  width: 900px;
  display: flex;
  justify-content: space-between;
  flex-direction: row-reverse;
  padding: 0px 5px;
}

.rectangle:first-child {
  flex-direction: column;
  box-shadow: 0px 10px 15px rgba(0, 0, 0, 0.2);
  z-index: 2;
}

.vote-rectangle {
  background-color: white;
  display: flex;
  justify-content: space-between;
  flex-direction: row-reverse;
  padding: 15px;

}

.rectangle-text {
  text-align: left;
  font-size: 36px;
  color: rgb(29, 29, 29);
  margin-top: 0;
  padding: 15px 0px;
}


.vote-system {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.vote-button {
  cursor: pointer;
}

.vote-count {
  font-size: 36px;
  padding: 5px 0;
  color: black;
}

.post-details {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding: 10px 5px 5px 0px;
  font-size: 34px;

}

.post-details span {
  display: flex;
  align-items: center;
  font-size: 32px;
  color: rgb(207, 207, 207);
}

.post-details span i {
  margin-left: 5px;
  color: rgb(207, 207, 207);
  font-size: 32px;
}

.post-details .user {
  color:rgb(193, 193, 193);

}
.post-details .poster {
  color:rgb(71, 96, 129);
}
</style>
<body>
  <div class="container">
    <div class="post-container">
      <div class="rectangle">
        <div class="post-awards-and-location">
          <!-- Subreddit Name -->
          <span>/r/{{ subreddit_name }}</span>  
          <div class="post-awards">
            {% for award in post_awards %}
                <img src="{{ award }}" width="35px" height="35px">
            {% endfor %}
          </div>
        </div>
        <h1 class="rectangle-text">{{ title }}</h1>
          <div class="post-details">
            <span class="poster">By Anon</span>
            <span>{{ comment_count }} <i class="fas fa-comment"></i></span>
            <span class="user">@SeriousRedditTea</span>
          </div>
      </div>
      <div class="vote-rectangle">
        <div class="vote-system">
          <i class="fas fa-arrow-up vote-button .vote-up" style="color: rgb(217, 103, 16); font-size: 32px;"></i>
          <span class="vote-count">{{ vote_count }}</span>
            <i class="fas fa-arrow-down vote-button .vote-down"  style="color: rgb(59, 98, 143); font-size: 32px;"></i>
        </div>
      </div>
    </div>
  </div>
  <!-- <button id="screenshot-button">Take Screenshot</button> -->

</body>
</html>
""")
# Prompt the user for the JSON file path
filepath = input("Drag the JSON file here or paste the file path: ")

# Load the JSON
posts = load_json(filepath.strip("\""))

if posts is not None:
    subreddit_name = os.path.basename(filepath).split("_")[0]
    subreddit_directory = Path(f'{subreddit_name}_posts')

    for i, post in enumerate(posts):
        vote_count = format_count(post['vote_count'])
        comment_count = format_count(post['comment_count'])
        
        html = html_template.render(
            subreddit_name=subreddit_name,
            title=post['title'],
            post_awards=post['post_awards'],
            comment_count=comment_count,
            vote_count=vote_count,
        )

        # create a directory for the post
        post_title = post['title'][:32]  # Use the first 32 characters of the post title
        post_title = post_title.replace(" ", "_")  # Replace spaces with underscores
        post_directory = subreddit_directory / f'{i}_{post_title}'
        post_directory.mkdir(parents=True, exist_ok=True)


        # write to file
        with open(post_directory / 'post.html', 'w') as f:
            f.write(html)
        
        # write post content to a text file
        with open(post_directory / 'post_content.txt', 'w') as f:
            f.write(post['post_content'])

        # run the Node.js script
        post_html_file = post_directory / Path('post.html')
        print(post_html_file)
        node_script_path = os.path.join(os.getcwd(), 'imageScrape.js')
        # Call the Node.js script with the path to the post.html file
        os.system(f'node imageScrape.js "{post_html_file.resolve()}"')


