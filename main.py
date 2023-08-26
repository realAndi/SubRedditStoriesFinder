import praw
import json
from datetime import datetime
import os
import subprocess
from jinja2 import Template
from pathlib import Path
from dotenv import load_dotenv
from grabAudio import get_streamelements_speech, get_amazon_polly_speech
from selectDir import select_directory, select_audio_directory
import nltk
from nltk.tokenize import sent_tokenize
import eyed3
from makeVideo import make_video
import shutil
from PIL import Image, ImageDraw, ImageFilter

load_dotenv()
useCaptions = True

reddit = praw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    user_agent="script:PostFinder:v0.0.1 (by /u/Andi1up)",
)

def pathSelection(isAudio=False):
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
          if isAudio:
            selection = select_audio_directory(selected_main_folder, is_subfolder=True)
          else:
            selection = select_directory(selected_main_folder, is_subfolder=True)
          
          if selection == "BACK":
              selected_main_folder = None
              continue
          selected_post_folder = selection

      if selected_post_folder:
          print(f"\nYou've selected: {selected_post_folder.name}")
          return selected_post_folder


def get_posts(subreddit_name, sort_by, limit, score):
    subreddit = reddit.subreddit(subreddit_name)

    if sort_by.lower() == "hot":
        posts = subreddit.hot(limit=limit)
    elif sort_by.lower() == "rising":
        posts = subreddit.rising(limit=limit)
    elif sort_by.lower() == "top":
        print("For 'Top' posts, select time period: 'all', 'year', 'month', 'week', 'day', 'hour'")
        time_period = input("Enter time period: ")
        posts = subreddit.top(time_filter=time_period, limit=limit)
    else:
        print("Invalid sorting option.")
        return

    results = []
    for post in posts:
        if post.score > score:
            awards = [award['icon_url'] for award in post.all_awardings][:5]
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

def add_rounded_corners_with_shadow(im, rad, shadow_offset=(10, 10), shadow_opacity=0.6, blur_radius=8):
    # Add rounded corners first
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)

    # Convert the image to RGBA for handling transparency
    if im.mode != 'RGBA':
        im = im.convert('RGBA')

    # Generate shadow
    shadow = Image.new('RGBA', im.size, (0, 0, 0, 0))
    shadow_alpha = im.split()[3]
    shadow.paste((0, 0, 0, int(255 * shadow_opacity)), (0, 0), mask=shadow_alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    shadow_offset_img = Image.new('RGBA', im.size, (0, 0, 0, 0))
    shadow_offset_img.paste(shadow, shadow_offset)

    # Combine shadow and image
    combined = Image.alpha_composite(shadow_offset_img, im)
    return combined

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
  max-width: 686px;  
}
.post-container{
  display: flex;
  flex-direction: row;
  max-width: 686px;                          
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
  max-width: 686px;  
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
    #############################
    #                           #
    #    HQ Reddit TikTok Bot   #
    #                           #
    #############################
    """)


def getPosts():
  # Prompt the user for input
  subreddit_name = input("Enter the name of the subreddit to browse: ")
  sort_by = input("Sort by (Hot, Rising, Top): ")
  upvote_threshold = int(input("Enter an upvote threshold: "))

  # Retrieve the posts
  posts = get_posts(subreddit_name, sort_by, 100, upvote_threshold)

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
        # Check if post['title'] ends with a period, question mark, or exclamation mark
        title = post['title']
        if title[-1] not in ['.', '?', '!']:
            title += '.'
        
        # Remove all line breaks in post_content
        post_content = post['post_content'].replace('\n', ' ').replace('\r', '')
        
        # Add the post title and content to the file
        f.write(title + ' ' + post_content)



      # run the Node.js script
      post_html_file = post_directory / Path('post.html')
      node_script_path = os.path.join(os.getcwd(), 'imageScrape.js')
      # Call the Node.js script with the path to the post.html file
      print('--------------------------------------------------------------------------')
      print('Running node script for the post: ', post['title'])
      os.system(f'node imageScrape.js "{post_html_file.resolve()}"')
      print('--------------------------------------------------------------------------\n')

      # Round the image
      image_path = post_directory / "title_card.png"
      image = Image.open(image_path)
      image = add_rounded_corners_with_shadow(image, 15)  
      image.save(post_directory / "title_card.png")


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
    selected_post_folder = pathSelection()
    print(selected_post_folder)
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
    nltk.download('punkt')

    # Tokenize the content into sentences
    sentences = sent_tokenize(content)
    generated_audio_files = []
    # Generate audio for each sentence and save
    for idx, sentence in enumerate(sentences, 1):
      # Use this if you have AWS CLI setup for a neural TTS
      audio_filename = get_amazon_polly_speech(sentence, voice, audio_folder)
      # Use this if you want the free standard TTS. It's good, but not the same as other typical reddit videos.
      # audio_filename = get_streamelements_speech(sentence, voice, audio_folder)  
    
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


def makeVideo(useCaptions):
    selected_post_folder = pathSelection(True)

    audio_folder = selected_post_folder / "audio"
    audio_files = list(audio_folder.glob("*.mp3"))

    total_duration = calculate_total_duration(audio_files)
    formatted_duration = seconds_to_minutes(total_duration)
    print(f"Total duration of all audio clips (with gaps): {formatted_duration}")

    processed_video = make_video(str(selected_post_folder), str(total_duration), useCaptions)

def main():
    # Display the header
    display_header()

    while True:
        # Display the options menu
        print("\nPlease select an option:")
        print("1. Grab and scrape posts from Reddit, (Generates Title Card and Text file for the post)")
        print("2. Generate audio TTS for posts")
        print("3. Make Video")
        print("4. Clear output folder")
        print("5. Experimental Options")
        print("6. Exit")

        # Get user's choice
        choice = input("Enter your option (1/2/3/4/5/6): ")

        if choice == "1":
            getPosts()
        elif choice == "2":
            audioGen()
        elif choice == "3":
            makeVideo(useCaptions)
        elif choice == "4":
            clearOutputFolder()
        elif choice == "5":
            experimentalOptions()
        elif choice == "6":
            print("Exiting.")
            break
        else:
            print("Invalid option. Please try again.")


def clearOutputFolder():
    output_folder_path = './output'
    confirmation = input("Are you sure you want to delete the output folder? \nDoing so will remove all made videos and saved posts.\nThis action is not undoable.\n(Y/N): ")
    
    if confirmation.lower() == 'y':
        for filename in os.listdir(output_folder_path):
            file_path = os.path.join(output_folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        print("Output folder cleared.")
    else:
        print("Action cancelled.")


def experimentalOptions():
    global useCaptions
    while True:
        # Display the options
        print("Please select an option")
        print("1. Edit Post Title Card")
        if useCaptions:
            print("2. Disable Captions (For people who want to use CapCut for captions.)")
        else:
            print("2. Enable Captions (Captions are still buggy.)")
        print("3. Exit")

        # Get user's choice
        choice = input("Enter your option (1/2/3): ")

        if choice == "1":
            editTitleCard()
        elif choice == "2":
            useCaptions = not useCaptions  # Toggle the value
            if useCaptions:
                print("Captions enabled.")
            else:
                print("Captions disabled.")
        elif choice == "3":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")


def editTitleCard():
    selected_post_folder = pathSelection()
    edit_contents_of_selected_folder(selected_post_folder)
    

def edit_contents_of_selected_folder(selected_post_folder):
    # File paths
    html_path = selected_post_folder / "post.html"
    txt_path = selected_post_folder / "post_content.txt"
    
    # Step 1: Edit post.html using string operations
    new_text = ""
    with open(html_path, 'r', encoding='utf-8') as file:
        content = file.read()

        # Check if the 'rectangle-text' class exists in the file
        start_tag = '<h1 class="rectangle-text">'
        end_tag = '</h1>'
        
        # Locate the start and end of the content for the class
        start_index = content.find(start_tag)
        end_index = content.find(end_tag, start_index)
        
        if start_index != -1 and end_index != -1:
            # Extract the current content
            current_text = content[start_index+len(start_tag):end_index]
            
            # Get user input to replace the content
            new_text = input("Enter the new text for the title card: ")
            
            # Replace the content in the whole HTML
            content = content.replace(current_text, new_text, 1) # replace only the first occurrence

            # Write the updated content back to post.html
            with open(html_path, 'w', encoding='utf-8') as file:
                file.write(content)
    
    # Step 2: Edit post_content.txt
    with open(txt_path, 'r', encoding='utf-8') as file:
        txt_content = file.readlines()
        
    # Replace the first sentence (assuming first line is the first sentence)
    txt_content[0] = new_text + '\n'
    
    with open(txt_path, 'w', encoding='utf-8') as file:
        file.writelines(txt_content)
    
    print("Title card and post content successfully edited!")

    print('--------------------------------------------------------------------------')
    print('Running node script for the post: ', new_text)
    os.system(f'node imageScrape.js "{html_path.resolve()}"')
    print('--------------------------------------------------------------------------\n')

    # Round the image
    image_path = selected_post_folder / "title_card.png"
    image = Image.open(image_path)
    image = add_rounded_corners_with_shadow(image, 15)  
    image.save(selected_post_folder / "title_card.png")





if __name__ == "__main__":
  main()

