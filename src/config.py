import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # API Rate Limits
    YOUTUBE_QUOTA_LIMIT = 10000  # Daily quota
    REQUESTS_PER_MINUTE = 100
    
    # Scraping Configuration
    BATCH_SIZE = 50
    RETRY_ATTEMPTS = 3
    DELAY_BETWEEN_REQUESTS = 1  # seconds