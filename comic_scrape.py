import time
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd

# Create a cloudscraper session to bypass Cloudflare
scraper = cloudscraper.create_scraper()

# URL to scrape
BASE_URL = "https://cmro.travis-starnes.com/groups.php?page={}&list_type=1&limit=30&order_listing=1&group_name=1"
OUTPUT_FILE = "cmro_appearances.csv"  # Output filename for the CSV file

# List to store the data for all pages
all_data = []

# Send the GET request to fetch the page with the Cloudflare scraper
for page in range(1, 61):
    response = scraper.get(BASE_URL.format(page))

    # Check if the request was successful
    if response.status_code == 200:
        print(f"Successfully retrieved page {page}.")
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find the div with the class "full_width_container_centered"
        container = soup.find("body", {"class": "body_design"}) \
                        .find("div", {"class": "main_body_container"}) \
                        .find("div", {"class": "main_section"}) \
                        .find("div", {"class": "full_width_container_centered"})

        # Check if the container is found
        if container:
            # Find all rows inside the container (each row is wrapped in a div with class "list_detail_body")
            rows = container.find_all("div", {"class": "list_detail_body"})
            
            # Loop through each row and extract the relevant details
            for row in rows:
                order = row.find("div", {"class": "list_detail_order_block"}).text.strip() if row.find("div", {"class": "list_detail_order_block"}) else ""
                published = row.find("div", {"class": "list_detail_publish_block"}).text.strip() if row.find("div", {"class": "list_detail_publish_block"}) else ""
                title = row.find("div", {"class": "list_detail_title_block"}).text.strip() if row.find("div", {"class": "list_detail_title_block"}) else ""

                # Append the extracted data to the list
                all_data.append([order, published, title])

        else:
            print(f"Container with class 'full_width_container_centered' not found on page {page}.")
    
    elif response.status_code == 429:
        print(f"Rate limit exceeded on page {page}, retrying after a short delay...")
        time.sleep(10)  # Wait for 10 seconds before retrying
        continue  # Retry the current page

    else:
        print(f"Failed to retrieve page {page} with status code {response.status_code}")
        break

# After all pages are scraped, save the data to a CSV file
if all_data:
    columns = ["Order", "Published", "Title"]
    df = pd.DataFrame(all_data, columns=columns)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Data saved to {OUTPUT_FILE}")
else:
    print("No data found.")
