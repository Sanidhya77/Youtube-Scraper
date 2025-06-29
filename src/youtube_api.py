from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time
import logging
from config import Config

class YouTubeAPI:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=Config.YOUTUBE_API_KEY)
        self.quota_used = 0
    
    def get_channel_details(self, channel_id=None, username=None, custom_url=None):
        try:
            if channel_id:
                request = self.youtube.channels().list(
                    part='snippet,statistics,brandingSettings,topicDetails',
                    id=channel_id
                )
            elif username:
                request = self.youtube.channels().list(
                    part='snippet,statistics,brandingSettings,topicDetails',
                    forUsername=username
                )
            elif custom_url:
                # First search for the channel
                search_response = self.youtube.search().list(
                    q=custom_url,
                    type='channel',
                    part='id',
                    maxResults=1
                ).execute()
                
                if not search_response['items']:
                    return None
                
                channel_id = search_response['items'][0]['id']['channelId']
                return self.get_channel_details(channel_id=channel_id)
            
            response = request.execute()
            self.quota_used += 1
            
            if response['items']:
                return self._format_channel_data(response['items'][0])
            return None
            
        except HttpError as e:
            logging.error(f"YouTube API error: {e}")
            return None
    
    def get_channel_videos(self, channel_id, max_results=50):
        try:
            videos = []
            next_page_token = None
            
            while len(videos) < max_results:
                request = self.youtube.search().list(
                    part='id',
                    channelId=channel_id,
                    type='video',
                    order='date',
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                )
                
                response = request.execute()
                self.quota_used += 100
                
                video_ids = [item['id']['videoId'] for item in response['items']]
                
                if video_ids:
                    video_details = self.get_video_details(video_ids)
                    videos.extend(video_details)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                time.sleep(Config.DELAY_BETWEEN_REQUESTS)
            
            return videos[:max_results]
            
        except HttpError as e:
            logging.error(f"Error fetching videos: {e}")
            return []
    
    def get_video_details(self, video_ids):
        try:
            if isinstance(video_ids, str):
                video_ids = [video_ids]
            
            request = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids)
            )
            
            response = request.execute()
            self.quota_used += 1
            
            return [self._format_video_data(item) for item in response['items']]
            
        except HttpError as e:
            logging.error(f"Error fetching video details: {e}")
            return []
    
    def _format_channel_data(self, channel_data):
        snippet = channel_data['snippet']
        statistics = channel_data.get('statistics', {})
        
        return {
            'channel_id': channel_data['id'],
            'channel_name': snippet['title'],
            'description': snippet.get('description', ''),
            'subscriber_count': int(statistics.get('subscriberCount', 0)),
            'total_views': int(statistics.get('viewCount', 0)),
            'video_count': int(statistics.get('videoCount', 0)),
            'profile_image_url': snippet['thumbnails']['high']['url'],
            'country': snippet.get('country'),
            'custom_url': snippet.get('customUrl'),
            'last_scraped': 'now()'
        }
    
    def _format_video_data(self, video_data):
        snippet = video_data['snippet']
        statistics = video_data.get('statistics', {})
        
        return {
            'video_id': video_data['id'],
            'title': snippet['title'],
            'description': snippet.get('description', ''),
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'comment_count': int(statistics.get('commentCount', 0)),
            'duration': video_data['contentDetails']['duration'],
            'published_at': snippet['publishedAt'],
            'thumbnail_url': snippet['thumbnails']['high']['url'],
            'category_id': int(snippet.get('categoryId', 0)),
            'tags': snippet.get('tags', [])
        }
    
    def search_channels(self, query, max_results=50):
        try:
            request = self.youtube.search().list(
                part='id,snippet',
                q=query,
                type='channel',
                maxResults=max_results,
                order='relevance'
            )
            
            response = request.execute()
            self.quota_used += 100
            
            channels = []
            for item in response['items']:
                channel_details = self.get_channel_details(
                    channel_id=item['id']['channelId']
                )
                if channel_details:
                    channels.append(channel_details)
                
                time.sleep(Config.DELAY_BETWEEN_REQUESTS)
            
            return channels
            
        except HttpError as e:
            logging.error(f"Error searching channels: {e}")
            return []