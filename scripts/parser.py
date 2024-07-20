import logging
from PIL import Image
from sd_parsers import ParserManager, PromptInfo

# Initialize the parser manager
parser_manager = ParserManager()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def parse_image_metadata(file_path):
    try:
        img = Image.open(file_path)

        prompt_info = parser_manager.parse(file_path)
        if not prompt_info:
            raise ValueError("No metadata found in image.")
        metadata = {
            "prompt": prompt_info.parameters,
            "workflow": prompt_info.metadata
        }
        return metadata
    except Exception as e:
        raise ValueError(f"Error extracting metadata: {e}")
