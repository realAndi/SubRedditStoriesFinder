import praw
import json
from datetime import datetime
import os
import subprocess
from jinja2 import Template
from pathlib import Path
from dotenv import load_dotenv
from grabAudio import get_streamelements_speech
from selectDir import select_directory, select_audio_directory
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
import eyed3


load_dotenv()

reddit = praw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    user_agent="script:PostFinder:v0.0.1 (by /u/Andi1up)",
)



def get_posts(subreddit_name, sort_by, limit, score):
    subreddit = reddit.subreddit(subreddit_name)

    if sort_by.lower() == "hot":
        posts = subreddit.hot(limit=limit)
    elif sort_by.lower() == "rising":
        posts = subreddit.rising(limit=limit)
    elif sort_by.lower() == "top":
        posts = subreddit.top(limit=limit)
    else:
        print("Invalid sorting option.")
        return

    results = []
    for post in posts:
        if post.score > score:
            awards = [award['icon_url'] for award in post.all_awardings]
            results.append({
                "title": post.title,
                "vote_count": post.score,
                "comment_count": post.num_comments,
                "post_awards": awards,
                "post_content": post.selftext,
                "character_count": len(post.selftext)
            })

    return results


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

def display_header():
    print("""
    ####################################
    #                                  #
    #    HQ Reddit TikTok Bot   v1.0   #
    #                                  #
    ####################################
    """)


def getPosts():
  # Prompt the user for input
  subreddit_name = input("Enter the name of the subreddit to browse: ")
  sort_by = input("Sort by (Hot, Rising, Top): ")
  upvote_threshold = int(input("Enter an upvote threshold: "))

  # Retrieve the posts
  posts = get_posts(subreddit_name, sort_by, 500, upvote_threshold)

  # Create the output directory if it doesn't exist
  output_directory = Path('output')
  output_directory.mkdir(parents=True, exist_ok=True)

  subreddit_directory = output_directory / Path(f'{subreddit_name}_posts')

  # Generate the filename
  filename = output_directory / Path(f"{subreddit_name}_posts_{datetime.now().strftime('%Y_%m_%d')}.json")

  # Save to json
  with open(filename, 'w') as f:
      json.dump(posts, f, indent=4, sort_keys=True)

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
          # Add the post title as the first line
          f.write(post['title'] + "\n")
          
          # Add the post content, with each line indented by 4 spaces
          indented_content = "\n".join(["    " + line for line in post['post_content'].splitlines()])
          f.write(indented_content)


      # run the Node.js script
      post_html_file = post_directory / Path('post.html')
      node_script_path = os.path.join(os.getcwd(), 'imageScrape.js')
      # Call the Node.js script with the path to the post.html file
      print('--------------------------------------------------------------------------')
      print('Running node script for the post: ', post['title'])
      os.system(f'node imageScrape.js "{post_html_file.resolve()}"')
      print('--------------------------------------------------------------------------\n')


# Get Audio length
def get_audio_duration(filename):
    audio = eyed3.load(filename)
    return audio.info.time_secs

def calculate_total_duration(audio_files):
    # Calculate the sum of the duration of all audio clips
    total_duration = sum([get_audio_duration(file) for file in audio_files])

    # Calculate the total gap duration: 
    # (len(audio_files) - 1) for the number of gaps between clips
    # 0.5 seconds per gap, plus the additional 1-second gap for the first audio
    total_gaps_duration = (len(audio_files) - 1) * 0.5 + 1

    # Return the total duration
    return total_duration + total_gaps_duration

def seconds_to_minutes(seconds):
    """
    Convert seconds to a minutes:seconds format.
    """
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes)} minutes {int(seconds)} seconds"

def audioGen():
    output_dir = Path("output")
    current_dir = output_dir

    # Initialize main and post folder selections as None
    selected_main_folder = None
    selected_post_folder = None
    while True:
        # Step 1: If no main folder is selected, show main folder options
        if not selected_main_folder:
            selection = select_directory(current_dir, is_subfolder=False)
            if selection == "BACK":
                print("Exiting.")
                exit()
            selected_main_folder = selection

        # Step 2: If main folder is selected but post folder isn't, show post folder options
        elif not selected_post_folder:
            selection = select_directory(selected_main_folder, is_subfolder=True)
            if selection == "BACK":
                selected_main_folder = None
                continue
            selected_post_folder = selection

        if selected_post_folder:
            print(f"\nYou've selected: {selected_post_folder.name}")
            break

    # Prompt user to revise the post_content.txt
    print("\nBefore proceeding, please ensure that you've revised 'post_content.txt' to ensure the TTS is smooth.")
    print("Some general advice:")
    print("   * Remove any special characters from the post, rewrite some sentences if you have to.")
    print("   * If posting on TikTok, be sure you replace swear words or any triggering words")
    print("   * If the desired post exceeds 5000 characters, assume it will be over 3-4 minutes.")
    input("Press ENTER when you're ready to continue...")

    # Create 'audio' sub-folder inside the post folder
    audio_folder = selected_post_folder / "audio"
    audio_folder.mkdir(exist_ok=True)

    print("\n'audio' folder has been created.")

    # Prompt user to choose a voice
    while True:
        voice_choice = input("\nPlease choose a voice: \n1. Male (Matthew)\n2. Female (Joanne)\nEnter your choice (1/2): ")
        if voice_choice == "1":
            voice = "Matthew"
            break
        elif voice_choice == "2":
            voice = "Joanna"
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    with open(selected_post_folder / 'post_content.txt', 'r') as f:
      content = f.read()

    audio_folder = selected_post_folder / "audio"
    audio_folder.mkdir(exist_ok=True)

    # Replace newlines with periods
    content = content.replace('\n', '. ')
    
    # Tokenize the content into sentences
    sentences = sent_tokenize(content)
    generated_audio_files = []
    # Generate audio for each sentence and save
    for idx, sentence in enumerate(sentences, 1):
      audio_filename = get_streamelements_speech(sentence, voice, audio_folder)
      # Move the audio file to the 'audio' directory and rename
      new_filename = audio_folder / f"{idx}_sentence.mp3"
      os.rename(audio_filename, new_filename)
      generated_audio_files.append(new_filename)
      print(f"Audio for sentence {idx} saved as: {new_filename}")

    print('Audio Files successfully made!')
    # After the loop, calculate and print the total duration
    total_duration = calculate_total_duration(generated_audio_files)
    formatted_duration = seconds_to_minutes(total_duration)
    print(f"Total duration of all audio clips (with gaps): {formatted_duration}")


def makeVideo():
    output_dir = Path("output")
    current_dir = output_dir

    # Initialize main and post folder selections as None
    selected_main_folder = None
    selected_post_folder = None
    while True:
        # Step 1: If no main folder is selected, show main folder options
        if not selected_main_folder:
            selection = select_audio_directory(current_dir, is_subfolder=False)
            if selection == "BACK":
                print("Exiting.")
                exit()
            selected_main_folder = selection

        # Step 2: If main folder is selected but post folder isn't, show post folder options
        elif not selected_post_folder:
            selection = select_audio_directory(selected_main_folder, is_subfolder=True)
            if selection == "BACK":
                selected_main_folder = None
                continue
            selected_post_folder = selection

        # If a post folder with audio is selected, proceed to the next steps
        if selected_post_folder:
            print(f"\nYou've selected: {selected_post_folder.name}")
            break

    audio_folder = selected_post_folder / "audio"
    audio_files = list(audio_folder.glob("*.mp3"))

    total_duration = calculate_total_duration(audio_files)
    formatted_duration = seconds_to_minutes(total_duration)
    print(f"Total duration of all audio clips (with gaps): {formatted_duration}")

    subprocess.run(["python", "makeVideo.py", str(selected_post_folder), str(total_duration)], check=True)



def main():
  # Display the header
  display_header()

  while True:
      # Display the options menu
      print("\nPlease select an option:")
      print("1. Grab and scrape posts from Reddit, (Generates Title Card and Text file for the post)")
      print("2. Generate audio TTS for posts")
      print("3. Make Video")
      print("4. Exit")
      
      # Get user's choice
      choice = input("Enter your option (1/2/3/4): ")

      if choice == "1":
          getPosts()
      elif choice == "2":
          audioGen()
      elif choice == "3":
          makeVideo()
      elif choice == "4":
          print("Exiting.")
          break
      else:
          print("Invalid option. Please try again.")


if __name__ == "__main__":
  main()

