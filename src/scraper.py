import logging
import time
from datetime import datetime, timedelta
from youtube_api import YouTubeAPI
from database import DatabaseManager
from config import Config

class YouTubeScraper:
    def __init__(self):
        self.youtube_api = YouTubeAPI()
        self.db = DatabaseManager()
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
    
    def scrape_channel_by_id(self, channel_id):
        """Scrape a single channel by ID"""
        try:
            logging.info(f"Scraping channel: {channel_id}")
            
            # Get channel details
            channel_data = self.youtube_api.get_channel_details(channel_id=channel_id)
            if not channel_data:
                logging.error(f"Could not fetch channel data for {channel_id}")
                return False
            
            # Insert/update channel in database
            creator_record = self.db.insert_creator(channel_data)
            if not creator_record:
                logging.error(f"Could not save channel data for {channel_id}")
                return False
            
            # Get recent videos
            videos = self.youtube_api.get_channel_videos(channel_id, max_results=20)
            
            # Add creator_id to videos
            for video in videos:
                video['creator_id'] = creator_record['id']
            
            # Insert videos
            if videos:
                self.db.insert_videos(videos)
                logging.info(f"Saved {len(videos)} videos for channel {channel_id}")
            
            logging.info(f"Successfully scraped channel: {channel_data['channel_name']}")
            return True
            
        except Exception as e:
            logging.error(f"Error scraping channel {channel_id}: {e}")
            return False
    
    def scrape_channels_by_search(self, queries, max_channels_per_query=10):
        """Scrape channels based on search queries"""
        all_channels = []
        
        for query in queries:
            logging.info(f"Searching for channels with query: {query}")
            
            channels = self.youtube_api.search_channels(
                query, 
                max_results=max_channels_per_query
            )
            
            for channel_data in channels:
                creator_record = self.db.insert_creator(channel_data)
                if creator_record:
                    all_channels.append(creator_record)
                    logging.info(f"Added channel: {channel_data['channel_name']}")
                
                # Respect rate limits
                time.sleep(Config.DELAY_BETWEEN_REQUESTS)
        
        return all_channels
    
    def update_existing_channels(self):
        """Update data for existing channels"""
        creators = self.db.get_creators_to_update(limit=50)
        
        for creator in creators:
            if self.youtube_api.quota_used >= Config.YOUTUBE_QUOTA_LIMIT * 0.9:
                logging.warning("Approaching quota limit, stopping updates")
                break
            
            self.scrape_channel_by_id(creator['channel_id'])
            time.sleep(Config.DELAY_BETWEEN_REQUESTS)
    
    def run_discovery_scraping(self):
        """Run initial discovery scraping"""
        # Define search queries for different niches
        search_queries = [
            "tech reviewer",
            "beauty influencer",
            "fitness youtuber",
            "gaming content creator",
            "cooking channel",
            "travel vlogger",
            "educational content",
            "music artist",
            "comedy creator",
            "lifestyle blogger"
        ]
        
        logging.info("Starting discovery scraping...")
        discovered_channels = self.scrape_channels_by_search(
            search_queries, 
            max_channels_per_query=5
        )
        
        logging.info(f"Discovery complete. Found {len(discovered_channels)} channels")
        return discovered_channels