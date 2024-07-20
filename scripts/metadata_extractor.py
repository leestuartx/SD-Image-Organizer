import json
from typing import Any, Dict, List
from PIL import Image
from sd_parsers import ParserManager

# Initialize the parser manager
parser_manager = ParserManager()


def extract_metadata(file_path: str) -> Dict[str, Any]:
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


def get_workflow_node_data(metadata, node_type="ShowText|pysssss", node_key="Node name for S&R", node_name="ShowText|pysssss"):
    out_found_names = []

    for key, section in metadata.items():
        if key == 'prompt' and isinstance(section, dict):
            for subkey, subsection in section.items():
                if subkey == 'workflow' and isinstance(subsection, dict):
                    print(subsection)
                    if "nodes" in subsection:
                        print('found nodes')
                        for node in subsection["nodes"]:
                            if node.get("type") == node_type and node.get("properties", {}).get(node_key) == node_name:
                                widgets_values = node.get("widgets_values", [])
                                for widget in widgets_values:
                                    if isinstance(widget, list):
                                        text_value = widget[0]
                                        out_found_names.append(text_value)

        elif isinstance(section, dict):
            for subkey, subsection in section.items():
                if subkey == 'workflow' and isinstance(subsection, dict):
                    if "nodes" in section:
                        for node in section["nodes"]:
                            if node.get("type") == node_type and node.get("properties", {}).get(node_key) == node_name:
                                widgets_values = node.get("widgets_values", [])
                                for widget in widgets_values:
                                    if isinstance(widget, list):
                                        text_value = widget[0]
                                        out_found_names.append(text_value)

    return out_found_names


def find_particular_keywords(metadata: Dict[str, Any], keywords: List[str]) -> List[str]:
    out_found_names = []

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
                                for keyword in keywords:
                                    if keyword.lower() in text_value.lower():
                                        out_found_names.append(keyword)

        elif isinstance(section, dict):
            for subkey, subsection in section.items():
                if subkey == 'workflow' and isinstance(subsection, dict):
                    if "nodes" in section:
                        for node in section["nodes"]:
                            if node.get("type") == "ShowText|pysssss" and node.get("properties", {}).get("Node name for S&R") == "ShowText|pysssss":
                                widgets_values = node.get("widgets_values", [])
                                for widget in widgets_values:
                                    if isinstance(widget, list):
                                        text_value = widget[0]
                                        for keyword in keywords:
                                            if keyword.lower() in text_value.lower():
                                                out_found_names.append(keyword)

    return out_found_names
