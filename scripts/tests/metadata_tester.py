import logging
from sd_parsers import ParserManager, PromptInfo
from PIL import Image
import json
import pprint

# Initialize the parser manager
from typing import Any, Dict, List

parser_manager = ParserManager()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extract_metadata(image_path):
    try:
        # Open the image
        img = Image.open(image_path)

        # Parse the image directly using the parser manager
        prompt_info = parser_manager.parse(img)
        # pprint.pp(prompt_info)

        if prompt_info:
            metadata = format_metadata(prompt_info)
            cfg_scale = get_float(prompt_info.parameters, 'cfg')
            steps = get_int(prompt_info.parameters, 'steps')
            width, height = img.size
            positive_prompt = get_prompt_text(prompt_info.prompts)
            negative_prompt = get_prompt_text(prompt_info.negative_prompts)
            clip_skip = get_int(prompt_info.parameters, 'clip')
            return prompt_info, metadata, cfg_scale, steps, width, height, positive_prompt, negative_prompt, clip_skip
        else:
            return prompt_info, "No metadata found.", 0.0, 0, 0.0, 0.0, "", "", 0
    except Exception as e:
        logging.exception("Error processing image")
        return f"Error processing image: {str(e)}", "", 0.0, 0, 0.0, 0.0, "", "", 0


def format_metadata(prompt_info: PromptInfo):
    metadata_parts = []

    # Models
    if prompt_info.models:
        model_text = '\n'.join([model.name for model in prompt_info.models])
        metadata_parts.append(f"Models:\n{model_text}")

    # Samplers
    if prompt_info.samplers:
        sampler_names = '\n'.join([sampler.name for sampler in prompt_info.samplers])
        metadata_parts.append(f"Samplers:\n{sampler_names}")
        for sampler in prompt_info.samplers:
            for param, value in sampler.parameters.items():
                metadata_parts.append(f"{param.title()}: {value}")

    # Prompts
    if prompt_info.prompts:
        prompt_text = '\n'.join([prompt.value for prompt in prompt_info.prompts])
        metadata_parts.append(f"Prompts:\n{prompt_text}")

    # Negative Prompts
    if prompt_info.negative_prompts:
        negative_prompt_text = '\n'.join([prompt.value for prompt in prompt_info.negative_prompts])
        metadata_parts.append(f"Negative Prompts:\n{negative_prompt_text}")

    # Additional metadata
    if prompt_info.metadata:
        additional_metadata = '\n'.join([f"{k}: {v}" for k, v in prompt_info.metadata.items()])
        metadata_parts.append(f"Additional Metadata:\n{additional_metadata}")

    # Unmodified parameters
    if prompt_info.parameters:
        params_text = '\n'.join([f"{k}: {v}" for k, v in prompt_info.parameters.items()])
        metadata_parts.append(f"Parameters:\n{params_text}")

    return '\n\n'.join(metadata_parts)


def get_float(parameters, key):
    try:
        return float(parameters.get(key, 0.0))
    except (ValueError, TypeError):
        return 0.0


def get_int(parameters, key):
    try:
        return int(parameters.get(key, 0))
    except (ValueError, TypeError):
        return 0


def get_prompt_text(prompts):
    if prompts:
        return '\n'.join([prompt.value for prompt in prompts])
    return ""


def extract_metadata_type2(file_path: str) -> Dict[str, Any]:
    try:
        img = Image.open(file_path)
        # Extract metadata using sd_parsers
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


def convert_keys_to_strings(d):
    if isinstance(d, dict):
        return {str(k): convert_keys_to_strings(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [convert_keys_to_strings(i) for i in d]
    else:
        return d


def find_positive_prompt_data(metadata: Dict[str, Any]) -> List[str]:
    output_data = []

    # Checking in both 'prompt' and 'workflow' sections for relevant nodes
    for key, section in metadata.items():
        if key == 'workflow' and isinstance(section, dict):
            if "nodes" in section:
                for node in section["nodes"]:
                    if node.get("type") == "ShowText|pysssss" and node.get("properties", {}).get("Node name for S&R") == "ShowText|pysssss":
                        widgets_values = node.get("widgets_values", [])
                        for widget in widgets_values:
                            if isinstance(widget, list):
                                text_value = widget[0]
                                output_data.append(text_value)

        elif isinstance(section, dict):
            for subkey, subsection in section.items():
                if subkey == 'workflow' and isinstance(subsection, dict):
                    if "nodes" in subsection:
                        for node in subsection["nodes"]:
                            if node.get("type") == "ShowText|pysssss" and node.get("properties", {}).get("Node name for S&R") == "ShowText|pysssss":
                                widgets_values = node.get("widgets_values", [])
                                for widget in widgets_values:
                                    if isinstance(widget, list):
                                        text_value = widget[0]
                                        output_data.append(text_value)

    return output_data


if __name__ == "__main__":
    image_path = r"C:\ComfyUI\output\test_dst\ComfyUI_0039.png"
    #SD image
    # image_path = r"C:\Output\images\characters\martin_van_buren\00013-2740811720.png"
    raw_metadata, metadata, cfg_scale, steps, width, height, positive_prompt, negative_prompt, clip_skip = extract_metadata(image_path)

    temp_metadata = extract_metadata_type2(image_path)
    metadata_str_keys = convert_keys_to_strings(temp_metadata)

    prompt_data = find_positive_prompt_data(metadata_str_keys)
    if len(prompt_data) > 0:
        positive_prompt = prompt_data[0]

    print("Prompt Data:", prompt_data)
    print("CFG Scale:", cfg_scale)
    print("Steps:", steps)
    print("Width:", width)
    print("Height:", height)
    print("Positive Prompt:", positive_prompt)
    print("Negative Prompt:", negative_prompt)
    print("Clip Skip:", clip_skip)
