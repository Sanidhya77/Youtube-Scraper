from scraper import YouTubeScraper
import logging

def main():
    scraper = YouTubeScraper()
    
    # Option 1: Discover new channels
    print("1. Running discovery scraping...")
    scraper.run_discovery_scraping()
    
    # Option 2: Update existing channels
    print("2. Updating existing channels...")
    scraper.update_existing_channels()
    
    # Option 3: Scrape specific channel
    # scraper.scrape_channel_by_id("UCXuqSBlHAE6Xw-yeJA0Tunw")  # Example channel ID

if __name__ == "__main__":
    main()