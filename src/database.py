from supabase import create_client, Client
from config import Config
import logging

class DatabaseManager:
    def __init__(self):
        self.supabase: Client = create_client(
            Config.SUPABASE_URL, 
            Config.SUPABASE_KEY
        )
    
    def insert_creator(self, creator_data):
        try:
            result = self.supabase.table('creators').upsert(
                creator_data, 
                on_conflict='channel_id'
            ).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logging.error(f"Error inserting creator: {e}")
            return None
    
    def insert_videos(self, videos_data):
        try:
            result = self.supabase.table('videos').upsert(
                videos_data, 
                on_conflict='video_id'
            ).execute()
            return result.data
        except Exception as e:
            logging.error(f"Error inserting videos: {e}")
            return None
    
    def get_creators_to_update(self, limit=100):
        try:
            result = self.supabase.table('creators')\
                .select('*')\
                .order('last_scraped', desc=False)\
                .limit(limit)\
                .execute()
            return result.data
        except Exception as e:
            logging.error(f"Error fetching creators: {e}")
            return []