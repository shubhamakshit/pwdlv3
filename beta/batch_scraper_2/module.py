import os
import requests
import mainLogic.utils.glv_var as glv_var
from mainLogic.utils.dependency_checker import re_check_dependencies

# Try to import tqdm for progress bar, otherwise, proceed without it
try:
    from tqdm import tqdm
    _tqdm_available = True
except ImportError:
    _tqdm_available = False
    print("tqdm not found. Progress bar will not be displayed during downloads.")


# Initialize batch_api and debugger outside the class as per original code structure
batch_api = None
debugger = glv_var.debugger # Assuming debugger is always available through glv_var

try:
    # Ensure dependencies are checked and tokens are retrieved
    re_check_dependencies()
    token = glv_var.vars["prefs"].get("token_config", {})
    
    access_token = None
    try:
        access_token = token["access_token"]
    except KeyError:
        try:
            access_token = token["token"]
        except KeyError:
            debugger.error("Access token not found in 'access_token' or 'token' fields.")
    
    random_id = token.get("random_id", None)
    
    if access_token:
        try:
            from beta.batch_scraper_2.Endpoints import Endpoints
            if random_id is None:
                batch_api = Endpoints(verbose=False).set_token(access_token)
            else:
                batch_api = Endpoints(verbose=False).set_token(access_token, random_id=random_id)
        except Exception as e:
            debugger.error(f"Failed to create batch_api instance, maybe the access_token is not available or Endpoints class is missing: {e}")
            debugger.error("Scraper may not work as intended.")
    else:
        debugger.error("No valid access token available. batch_api instance will not be created.")

except Exception as e:
    debugger.error(f"An unexpected error occurred during batch_api initialization: {e}")
    debugger.error("Scraper may not work as intended.") 


class ScraperModule:
    """
    A module for scraping operations, including file downloads.
    """
    batch_api = batch_api
    debugger = debugger
    prefs = glv_var.vars["prefs"]

    def download_file(self, url: str, destination_folder: str = "./", filename: str = None, show_progress: bool = True):
        """
        Downloads a file from a given URL to a specified folder.

        Args:
            url (str): The URL of the file to download.
            destination_folder (str): The folder where the file will be saved. Defaults to current directory ("./").
            filename (str, optional): The name to save the file as. If None, it extracts
                                      the filename from the URL.
            show_progress (bool): Whether to display a progress bar using tqdm. Defaults to True.

        Returns:
            str: The full path to the downloaded file if successful, None otherwise.
        """
        if not url:
            self.debugger.error("Download URL cannot be empty.")
            return None

        # Create the destination folder if it doesn't exist
        os.makedirs(destination_folder, exist_ok=True)

        if filename is None:
            # Extract filename from URL
            filename = url.split('/')[-1].split('?')[0]
            if not filename: # Fallback if URL ends with '/' or has no valid filename part
                filename = "downloaded_file"
                self.debugger.warning(f"Could not determine filename from URL. Using default: '{filename}'")

        file_path = os.path.join(destination_folder, filename)

        self.debugger.debug(f"Attempting to download '{url}' to '{file_path}'")

        try:
            # Stream the download to handle large files efficiently
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            total_size_in_bytes = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte

            if _tqdm_available and show_progress:
                progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=f"Downloading {filename}")
            else:
                progress_bar = None

            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk: # filter out keep-alive new chunks
                        file.write(chunk)
                        if progress_bar:
                            progress_bar.update(len(chunk))
            
            if progress_bar:
                progress_bar.close()

            self.debugger.info(f"Successfully downloaded '{filename}' to '{file_path}'")
            return file_path

        except requests.exceptions.RequestException as e:
            self.debugger.error(f"Error downloading file from '{url}': {e}")
        except IOError as e:
            self.debugger.error(f"Error writing file to '{file_path}': {e}")
        except Exception as e:
            self.debugger.error(f"An unexpected error occurred during download: {e}")
        
        return None

# Example Usage (You can uncomment and modify this to test the function)
# if __name__ == "__main__":
#     scraper = ScraperModule()
#     if scraper.batch_api:
#         # Example URL for testing (replace with a real downloadable file URL)
#         test_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf" 
#         
#         # Download with default settings (to current folder, filename from URL, show progress)
#         downloaded_path = scraper.download_file(test_url)
#         print(f"Downloaded to: {downloaded_path}")

#         # Download to a specific folder with a custom filename, no progress
#         # custom_folder = "my_downloads"
#         # custom_filename = "sample_document.pdf"
#         # downloaded_path_custom = scraper.download_file(
#         #     test_url, 
#         #     destination_folder=custom_folder, 
#         #     filename=custom_filename, 
#         #     show_progress=False
#         # )
#         # print(f"Downloaded custom to: {downloaded_path_custom}")
#     else:
#         print("ScraperModule not initialized due to missing access token or Endpoints class.")

