import json
import os

from pathlib import Path
from dotenv import load_dotenv

TITLE = "RIS Synergy API"
DESCRIPTION = "Full API for RIS Synergy"
VERSION = "1.0"

# Load .env file from the folder above the script
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Environment variable for server URL
OPEN_API_SERVER_URL = os.getenv("OPEN_API_SERVER_URL", "https://default-url.com")


def merge_openapi_files(file_paths, output_file, new_title, new_description, version):
    """
    Merges multiple OpenAPI JSON files into one, updating the title in the output.

    Args:
        file_paths (list of str): Paths to OpenAPI JSON files to merge.
        output_file (str): Path for the output merged OpenAPI file.
        new_title (str): New title for the merged OpenAPI file.
        version (str): Version of the merged API.
    """
    merged_api = {
        "openapi": "3.0.1",
        "info": {
            "title": new_title,
            "description": new_description,
            "version": version,
        },
        "servers": [{"url": f"{OPEN_API_SERVER_URL}/ris-synergy"}],
        "paths": {},
        "components": {},
    }

    for file_path in file_paths:
        file_path = Path(file_path)
        if file_path.exists():
            with open(file_path, "r") as f:
                api_data = json.load(f)

            # Merge paths
            if "paths" in api_data:
                merged_api["paths"].update(api_data["paths"])

            # Merge components
            if "components" in api_data:
                if "components" not in merged_api:
                    merged_api["components"] = api_data["components"]
                else:
                    for comp_type, comp_data in api_data["components"].items():
                        if comp_type not in merged_api["components"]:
                            merged_api["components"][comp_type] = comp_data
                        else:
                            merged_api["components"][comp_type].update(comp_data)
        else:
            print(f"Warning: File not found - {file_path}")

    # Save merged API to output file
    output_file = Path(output_file)
    with open(output_file, "w") as f:
        json.dump(merged_api, f, indent=2)
    print(f"Merged API saved to {output_file}")


# Example usage
if __name__ == "__main__":
    # Base directory for app folder
    base_dir = Path(__file__).resolve().parent.parent / "app"

    # List of OpenAPI JSON files to merge
    input_files = [
        base_dir
        / "rissynergy"
        / "jsonschemas"
        / f"RIS-SYNERGY-info-api-{VERSION}-swagger.json",
        base_dir
        / "rissynergy"
        / "jsonschemas"
        / f"RIS-SYNERGY-org-unit_api-{VERSION}-swagger.json",
        base_dir
        / "rissynergy"
        / "jsonschemas"
        / f"RIS-SYNERGY-project-api-{VERSION}-swagger.json",
    ]
    # Output file path
    output_file = (
        base_dir / "rissynergy" / "jsonschemas" / f"ris-synergy-{VERSION}.json"
    )

    merge_openapi_files(
        input_files,
        output_file,
        new_title=TITLE,
        new_description=DESCRIPTION,
        version=VERSION,
    )
