import csv
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import tldextract
import pandas as pd
from colorama import Fore, Style
from selenium.common.exceptions import WebDriverException


# Constants
TIMEOUT_SECONDS = 10
DATASET_PATH = "202405.csv"
# Path to chromedriver
# (download from https://googlechromelabs.github.io/chrome-for-testing/)
CHROMEDRIVER_PATH = "chromedriver-mac-arm64/chromedriver"


start_time = time.time()


# Function to check if request is an actual URL or embedded data
def is_embedded_data(request_url):
    # Check if the URL starts with "data:"
    if request_url.startswith("data:"):
        return True
    return False


# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# Enable performance logging for insights into network requests
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

# Start WebDriver
service = ChromeService(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Set timeouts
# Timeout for page load
driver.set_page_load_timeout(TIMEOUT_SECONDS)
# Timeout for script execution
driver.set_script_timeout(TIMEOUT_SECONDS)

# List to store all requests
all_requests = []

# List to store all script statistics
script_statistics_errors = []

# Import dataset
df = pd.read_csv(DATASET_PATH)

# Loop through each URL in the dataset
for index, row in enumerate(df.itertuples(), start=0):
    url = row.origin
    print(f"Fetching url {
          index+1} of {len(df)} - ({url})")

    try:
        # Visit the URL
        driver.get(url)
        # Wait for the page to load and requests to complete
        time.sleep(TIMEOUT_SECONDS)

        # Get performance logs
        logs = driver.get_log("performance")

        # Process logs and extract request details
        for entry in logs:
            log = json.loads(entry["message"])["message"]
            if log["method"] == "Network.requestWillBeSent":
                request = log["params"]["request"]
                method = request["method"]
                request_url = request["url"]
                # headers = request['headers']
                all_requests.append(
                    {
                        "page": url,
                        "method": method,
                        "full_url": request_url,
                        "subdomain": tldextract.extract(request_url).subdomain,
                        "domain": tldextract.extract(request_url).domain,
                        "suffix": tldextract.extract(request_url).suffix,
                        # "headers": headers
                    }
                )
    except WebDriverException as e:
        print(Fore.RED + f"Error fetching URL {url}: {e.msg}" + Style.RESET_ALL)
        script_statistics_errors.append(
            {
                "page": url,
                "error": e.msg,
            }
        )
        continue


# Save requests to a CSV file
with open("requests.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Page", "Method", "Full URL", "Subdomain", "Domain", "Suffix"])
    # writer.writerow(["Method", "URL", "Headers"])
    for request in all_requests:
        if not is_embedded_data(request["full_url"]):
            writer.writerow(
                [
                    request["page"],
                    request["method"],
                    request["full_url"],
                    request["subdomain"],
                    request["domain"],
                    request["suffix"],
                ]
            )
            # writer.writerow([request["method"], request["url"], json.dumps(request["headers"])])

# Quit the driver
driver.quit()

end_time = time.time()

# Summarize and save script statistics to json file
with open("script_statistics_errors.json", "w") as file:
    start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
    end_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))
    time_taken = end_time - start_time
    time_taken_str = time.strftime("%H:%M:%S", time.gmtime(time_taken))
    statistics = {
        "number_of_errors": len(script_statistics_errors),
        "time_taken": time_taken_str,
        "start_time": start_time_str,
        "end_time": end_time_str,
        "errors": script_statistics_errors,
    }
    json.dump(statistics, file, indent=4)
