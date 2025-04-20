import os
from googleapiclient.discovery import build
import csv
import time

class YouTubeCommentCollector:
    def __init__(self, api_key):
        """
        Initialize YouTube Data API client
        
        Args:
            api_key (str): Google Developer API Key
        """
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def get_video_ids(self, search_query, max_results=50):
        """
        Search for videos related to sports in Arabic
        
        Args:
            search_query (str): Search term for sports content
            max_results (int): Maximum number of videos to retrieve
        
        Returns:
            list: List of video IDs
        """
        try:
            search_response = self.youtube.search().list(
                q=search_query,
                type='video',
                part='id',
                maxResults=max_results,
                relevanceLanguage='ar'  # Focus on Arabic content
            ).execute()
            
            return [item['id']['videoId'] for item in search_response.get('items', [])]
        except Exception as e:
            print(f"Error searching videos: {e}")
            return []
    
    def get_comments(self, video_id, max_comments=1000):
        """
        Retrieve comments for a specific video
        
        Args:
            video_id (str): YouTube video ID
            max_comments (int): Maximum number of comments to retrieve
        
        Returns:
            list: List of comment dictionaries
        """
        comments = []
        try:
            # First request
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=100,  # YouTube API max per request
                textFormat='plainText'
            )
            
            response = request.execute()
            
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'text': comment['textDisplay'],
                    'likes': comment.get('likeCount', 0),
                    'published_at': comment['publishedAt'],
                    'author': comment['authorDisplayName']
                })
            
            # Pagination for more comments
            while len(comments) < max_comments and 'nextPageToken' in response:
                request = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    pageToken=response['nextPageToken'],
                    maxResults=100,
                    textFormat='plainText'
                )
                response = request.execute()
                
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'text': comment['textDisplay'],
                        'likes': comment.get('likeCount', 0),
                        'published_at': comment['publishedAt'],
                        'author': comment['authorDisplayName']
                    })
                
                if len(comments) >= max_comments:
                    break
        
        except Exception as e:
            print(f"Error retrieving comments for video {video_id}: {e}")
        
        return comments[:max_comments]
    
    def collect_comments_to_csv(self, search_queries, output_file='youtube_sports_comments.csv'):
        """
        Collect comments from multiple searches and save to CSV
        
        Args:
            search_queries (list): List of sports-related search terms
            output_file (str): File to save comments
        
        Returns:
            int: Total number of comments collected
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Open CSV file with UTF-8 encoding to support Arabic
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            # Define CSV writer
            fieldnames = ['text', 'likes', 'published_at', 'author']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Total comments counter
            total_comments = 0
            
            # Iterate through search queries
            for query in search_queries:
                print(f"Searching for: {query}")
                
                # Get video IDs
                video_ids = self.get_video_ids(query)
                
                # Collect comments for each video
                for video_id in video_ids:
                    print(f"Collecting comments for video: {video_id}")
                    
                    # Get comments
                    video_comments = self.get_comments(video_id)
                    
                    # Write comments to CSV
                    for comment in video_comments:
                        try:
                            writer.writerow(comment)
                        except Exception as e:
                            print(f"Error writing comment: {e}")
                    
                    # Update total comments
                    total_comments += len(video_comments)
                    
                    # Pause to respect API limits
                    time.sleep(1)
        
        print(f"Total comments collected: {total_comments}")
        return total_comments

# Main execution
def main():

    # IMPORTANT: Replace with your actual Google Developer API Key
    API_KEY = 'AIzaSyD7uZkhPuYqKQ0gdCS20I2McNG3LboQCWU'
    
    # Sports-related search queries in Arabic
    
    sports_queries = [
      "#رياضة", "#كرة_القدم", "#كرة_السلة", "#تنس", "#ملاكمة", "#كرة_الطائرة",
    ]

   
   
    # Initialize collector
    collector = YouTubeCommentCollector(API_KEY)
    
    # Collect comments and save to CSV
    collector.collect_comments_to_csv(
        sports_queries, 
        output_file='./data/youtube_sports_comments.csv'
    )

if __name__ == '__main__':
    main()


# Key Points:

# 1. **Simple Data Collection**
#    - Directly saves comments to CSV
#    - No text cleaning or preprocessing
#    - Captures raw comments as-is

# 2. **What You'll Get**
#    - Comments in original format
#    - Metadata like likes, publish date, author
#    - UTF-8 encoding for Arabic text support

# 3. **Requirements**
#    - Google Developer API Key
#    - `google-api-python-client` library
#    - Python 3.x

# 4. **Important Preparation**
#    - Replace `'YOUR_GOOGLE_DEVELOPER_API_KEY'` with actual API key
#    - Install required library: `pip install google-api-python-client`

# 5. **Customization**
#    - Modify `sports_queries` for different search terms
#    - Adjust `max_comments` and `max_results` as needed

# Recommendations:
# - Start with few search queries
# - Monitor API quota usage
# - Be prepared for potential errors
# - Use a try/catch approach

# Would you like me to explain how to set up the Google Developer API key or modify the script for your specific needs?