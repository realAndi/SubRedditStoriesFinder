from pathlib import Path
import re
import os

def select_directory(parent_dir, is_subfolder=False):
    """
    Lists all subdirectories of parent_dir and lets the user select one.
    Returns the selected directory's Path object or 'BACK' if user chooses to go back.
    """
    sub_dirs = [dir for dir in parent_dir.iterdir() if dir.is_dir()]

    # Format the names based on whether it's a main folder or subfolder
    if is_subfolder:
        formatted_names = [re.sub(r'^\d*_', '', dir.name).replace('_', ' ') for dir in sub_dirs]
    else:
        formatted_names = [dir.name.replace('_posts', '') for dir in sub_dirs]

    print("\nAvailable Folders:")
    for idx, name in enumerate(formatted_names, 1):
        print(f"{idx}. {name}")
    if is_subfolder:
        print("0. Go back\n")
    else:
        print("0. Exit\n")

    while True:
        try:
            selected_index = int(input("Select a folder by its number: "))
            if 0 <= selected_index <= len(sub_dirs):
                break
            else:
                print("Invalid selection. Please choose a number from the list.")
        except ValueError:
            print("Please enter a valid number.")

    if selected_index == 0:
        return "BACK"

    return sub_dirs[selected_index - 1]


def select_audio_directory(parent_dir, is_subfolder=False):
    """
    Lists all subdirectories of parent_dir and lets the user select one.
    Returns the selected directory's Path object or 'BACK' if user chooses to go back.
    """
    if is_subfolder:
        # Include only directories that have a non-empty 'audio' subfolder
        sub_dirs = [dir for dir in parent_dir.iterdir() 
                    if dir.is_dir() 
                    and (dir / 'audio').exists() 
                    and any((dir / 'audio').iterdir())]
    else:
        sub_dirs = [dir for dir in parent_dir.iterdir() if dir.is_dir()]

    # Format the names based on whether it's a main folder or subfolder
    if is_subfolder:
        formatted_names = [re.sub(r'^\d*_', '', dir.name).replace('_', ' ') for dir in sub_dirs]
    else:
        formatted_names = [dir.name.replace('_posts', '') for dir in sub_dirs]

    print("\nAvailable Folders:")
    for idx, name in enumerate(formatted_names, 1):
        print(f"{idx}. {name}")
    if is_subfolder:
        print("0. Go back\n")
    else:
        print("0. Exit\n")

    while True:
        try:
            selected_index = int(input("Select a folder by its number: "))
            if 0 <= selected_index <= len(sub_dirs):
                break
            else:
                print("Invalid selection. Please choose a number from the list.")
        except ValueError:
            print("Please enter a valid number.")

    if selected_index == 0:
        return "BACK"

    return sub_dirs[selected_index - 1]
