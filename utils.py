import os
import zipfile
from kaggle.api.kaggle_api_extended import KaggleApi

def extract_nested_zip(zip_path, extract_to, processed_files=None):
    """
    Recursively extracts nested .zip files in a directory, ignoring __MACOSX and other unnecessary files.

    Args:
        zip_path (str): Path to the initial .zip file.
        extract_to (str): Directory to extract the files into.
        processed_files (set): A set to keep track of processed zip files.
    """
    if processed_files is None:
        processed_files = set()

    # Check if the current zip file has already been processed
    if zip_path in processed_files:
        print(f"Skipping already processed file: {zip_path}")
        return

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extract all files except those in __MACOSX
        for file in zip_ref.namelist():
            if not file.startswith("__MACOSX/"):
                zip_ref.extract(file, extract_to)
    processed_files.add(zip_path)  # Mark this zip as processed
    os.remove(zip_path)  # Remove the processed zip file

    # Recursively handle nested zip files
    for root, _, files in os.walk(extract_to):
        for file in files:
            if file.endswith(".zip"):
                nested_zip_path = os.path.join(root, file)
                print(f"Extracting nested zip: {nested_zip_path}")
                extract_nested_zip(nested_zip_path, root, processed_files)


def download_competition_data(competition_name, output_dir="data"):
    """
    Downloads data for a Kaggle competition, saving it in the specified directory.

    Args:
        competition_name (str): The name of the Kaggle competition (e.g., "new-york-city-taxi-fare-prediction").
        output_dir (str): The directory to save the downloaded data.
    """
    # Get the absolute path of the output directory
    full_output_dir = os.path.abspath(output_dir)

    # Check if the directory exists and contains meaningful files
    if os.path.exists(full_output_dir):
        files = [f for f in os.listdir(full_output_dir) if not f.startswith(".")]
        print(f"Checking contents of '{full_output_dir}'... Found: {files}")
        if len(files) > 0:
            print(f"Data already exists in '{full_output_dir}'. Skipping download.")
            return

    # Initialize Kaggle API
    api = KaggleApi()
    api.authenticate()

    # Create the directory if it doesn't exist
    os.makedirs(full_output_dir, exist_ok=True)

    # Download competition files
    print(f"Downloading dataset for competition: {competition_name}")
    api.competition_download_files(competition_name, path=full_output_dir)

    # Unzip the downloaded files
    zip_path = os.path.join(full_output_dir, f"{competition_name}.zip")
    if os.path.exists(zip_path):
        print(f"Extracting top-level zip file: {zip_path}")
        extract_nested_zip(zip_path, full_output_dir)
        print(f"Dataset extracted to: {full_output_dir}")
    else:
        print(f"No zip file found at: {zip_path}")