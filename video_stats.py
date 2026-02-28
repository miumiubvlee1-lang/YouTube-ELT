import requests
import json
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv(dotenv_path="/Users/selinavu/YouTube-ELT/api_key.env")

api_key = os.getenv("api_key")
channel_handle = "MrBeast"
maxResults = 50


def get_playlist_id():

    try:
            
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel_handle}&key={api_key}"

        response = requests.get(url)
        response.raise_for_status()
        response_output = response.json()
        # data = json.dumps(response_output, indent=4)
        #print(data)
        # with open("video_stats.json", "w") as file:
        #     file.write(data)
        channel_items=response_output["items"][0]
        channel_playlistID = channel_items['contentDetails']['relatedPlaylists']['uploads']
        print(channel_playlistID)
        return channel_playlistID
    except requests.exceptions.RequestException as e:
        raise e
    

def get_video_id(playlistID):
    
    video_ids = []
    pageToken = None
   
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistID}&key={api_key}"
    
    try:
        while True:
            url = base_url

            if pageToken:
                url += f"&pageToken={pageToken}" #setting up code to get pageToken from below, insert into url
            response = requests.get(url)
            response.raise_for_status()
            response_output = response.json()

            for item in response_output.get('items',[]): #using [] in parameter to ensure prevent program from crashing even when ID is not found
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            pageToken = response_output.get('nextPageToken') # grab next page token from json file until no more token found, then break loop
            if not pageToken:
                break
        return video_ids

    except requests.exceptions.RequestException as e:
        raise e


def extract_video_data(video_ids):

    extracted_video = []

    def batch_list(video_id_lst, batch_size):
        for video_id in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[video_id: video_id+batch_size]
    
    
    try:
        for batch in batch_list(video_ids, maxResults):
            video_ids_str = ",".join(batch)
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={api_key}"    
            response = requests.get(url)
            response.raise_for_status()
            response_output = response.json()

            for item in response_output.get('items',[]):
                video_id = item['id']
                snippet = item['snippet']
                content_details = item['contentDetails']
                m_statistics = item['statistics']
                video_data = {
                    "video_id" : video_id,
                    "title" : snippet['title'] , 
                    "publishedAt" : snippet['publishedAt'],
                    "duration" : content_details['duration'],
                    "viewCount" : m_statistics.get('viewCount', None), #there are videos with no view/like/comment count available, putting none os default value in case no value found
                    "likeCount" : m_statistics.get('likeCount', None),
                    "commentCount" : m_statistics.get('commentCount', None)
                }
                extracted_video.append(video_data)

        return extracted_video

    except requests.exceptions.RequestException as e:
        raise e
    
def save_to_json(extracted_videos):
    file_path = f"/Users/selinavu/YouTube-ELT/data/YT_data_{date.today()}.json"
    with open(file_path, "w", encoding="utf-8") as json_outfile:
        json.dump(extracted_videos, json_outfile, indent=4, ensure_ascii=False)



if __name__ == "__main__":
    # print("get_playlist_id function is beginning execution")
    playlistID = get_playlist_id()
    videoID = get_video_id(playlistID)
    # print(extract_video_data(videoID))
    extractedVIDEO = extract_video_data(videoID)
    save_to_json(extractedVIDEO)

# else:
#     print("get_playlist-_id won't be executed")

        

