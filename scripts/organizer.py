import os
import logging
import shutil
import json
from typing import Any, Dict, List
from scripts.metadata_extractor import extract_metadata, find_particular_keywords, get_workflow_node_data
from sd_parsers import ParserManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the parser manager
parser_manager = ParserManager()

def load_keywords(file_path):
    with open(file_path, 'r') as f:
        keywords = [line.strip() for line in f if line.strip()]
    return keywords

def increment_filename(filepath):
    base, ext = os.path.splitext(filepath)
    counter = 1
    new_filepath = base + "(" + str(counter) + ")" + ext
    while os.path.exists(new_filepath):
        counter += 1
        new_filepath = base + "(" + str(counter) + ")" + ext
    return new_filepath

def convert_keys_to_strings(d):
    if isinstance(d, dict):
        return {str(k): convert_keys_to_strings(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [convert_keys_to_strings(i) for i in d]
    else:
        return d

def move_file_to_category(file_path, output_dir, category, name):
    category_dir = os.path.join(output_dir, category, name.replace(' ', '_').lower())
    os.makedirs(category_dir, exist_ok=True)
    dest_path = os.path.join(category_dir, os.path.basename(file_path))
    if os.path.exists(dest_path):
        dest_path = increment_filename(dest_path)
    shutil.move(file_path, dest_path)
    print("Moved " + file_path + " to " + dest_path)

def organize_images(base_path, output_dir, node_defaults):
    character_keywords = load_keywords('./wildcards/characters.txt')
    location_keywords = load_keywords('./wildcards/locations.txt')

    for root, dirs, files in os.walk(base_path):
        if 'characters' in dirs:
            dirs.remove('characters')  # Exclude 'characters' directory

        if 'locations' in dirs:
            dirs.remove('locations')  # Exclude 'locations' directory

        for file in files:
            if file.lower().endswith('.png'):
                file_path = os.path.join(root, file)
                #print("Processing file: " + file_path)
                try:
                    metadata = extract_metadata(file_path)
                    metadata_str_keys = convert_keys_to_strings(metadata)

                    #print("Metadata for " + file + ":")
                    #print(json.dumps(metadata_str_keys, indent=4))

                    # Look for the specific CharacterNames in nodes in the metadata
                    found_character_names = find_particular_keywords(
                        metadata_str_keys,
                        character_keywords,
                        node_type=node_defaults['node_type'],
                        node_key=node_defaults['node_key'],
                        node_name=node_defaults['node_name']
                    )

                    #print("Found Character Names: " + str(found_character_names))

                    if found_character_names:
                        # Move the images into the correct character directories
                        for name in found_character_names:
                            move_file_to_category(file_path, output_dir, 'characters', name)
                            break  # Exit the loop after moving the file

                    else:
                        # Look for the specific Location Names from the txt file within nodes in the metadata
                        found_location_names = find_particular_keywords(
                            metadata_str_keys,
                            location_keywords,
                            node_type=node_defaults['node_type'],
                            node_key=node_defaults['node_key'],
                            node_name=node_defaults['node_name']
                        )

                        if found_location_names:
                            print("Found Location Names: " + str(found_location_names))
                            for name in found_location_names:
                                move_file_to_category(file_path, output_dir, 'locations', name)
                                break  # Exit the loop after moving the file

                    # This is the fallback to use the positive prompt
                    if not found_character_names:
                        found_names = []
                        prompt_info = parser_manager.parse(file_path)
                        if prompt_info:
                            for character in character_keywords:
                                if any(character in prompt.value for prompt in prompt_info.prompts):
                                    found_names.append(character)
                            if found_names:
                                for name in found_names:
                                    move_file_to_category(file_path, output_dir, 'characters', name)
                                    break
                            else:
                                for location in location_keywords:
                                    if any(location in prompt.value for prompt in prompt_info.prompts):
                                        found_names.append(location)
                                if found_names:
                                    for name in found_names:
                                        move_file_to_category(file_path, output_dir, 'locations', name)
                                        break

                except ValueError as ve:
                    logging.error("ValueError reading file: " + file_path + ": " + str(ve))
                    logging.error("Problematic metadata: " + str(prompt_info.parameters if prompt_info else 'N/A'))
                except Exception as e:
                    logging.exception("Error processing file " + file + ": " + str(e))
