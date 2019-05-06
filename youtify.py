import spotipy
import spotipy.util as util
import httplib2
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser
from oauth2client import tools
import requests

REDIRECT_URI = "http://localhost"

GOOGLEAPI_KEY = "" # Your Google API Key

CLIENT_SECRETS_FILE = "client_secret.json" # Path to the client_secret JSON file for Google API
MISSING_CLIENT_SECRETS_MESSAGE = "MISSING client_secret.json FILE"

YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


scope = 'user-library-read playlist-read-private playlist-read-collaborative'

username = input("\nYour spotify username: ")
CLIENT_ID = "a41a697994864dfd96f027b7fc29abea"
CLIENT_SECRET = "78eca370ef0947baa7570fa80c7f5ed8"

def Show_Songs(playlist_dict):
    c = 0
    for item in playlist_dict["items"]: 
    
        try:
            song_name = str(item["track"]["name"]) + " "
            c += 1
        except:
            return c 

        for artist in item["track"]["artists"]:
            try:
                song_name += str(artist["name"]) + " "
            except:
                return c
        print(song_name)
    
    return c

def Get_SongId_From_Youtube(song_name):
    url = "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q=" + song_name.replace(" " , "+") + "&key=" + GOOGLEAPI_KEY
    res = requests.get(url)
    data = res.json()
    try:
        song_id = (data['items'][0]['id']['videoId'])
    except:
        return None
    return song_id


def Process_Songs(playlist_dict, youtube, playlist_id):
    for item in playlist_dict["items"]: 
        song_id = ""
        try:
            song_name = str(item["track"]["name"]) + " "
        except:
            return

        for artist in item["track"]["artists"]:
            try:
                song_name += str(artist["name"]) + " "
            except:
                return

        song_id = Get_SongId_From_Youtube(song_name)
        if song_id != None:
            Add_to_Playlist(youtube, song_id, playlist_id)



def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("oauth2.json")
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage,  tools.argparser.parse_args())

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()))

def Add_to_Playlist(youtube,videoID,playlistID):
    add_video_request=youtube.playlistItems().insert(
    part="snippet",
    body={
        'snippet': {
            'playlistId': playlistID, 
            'resourceId': {
                    'kind': 'youtube#video',
                'videoId': videoID
                }
         }
        }
).execute()

def Get_SongsInPlaylist(username, playlist_id):
    c = 0
    playlist_dict = sp.user_playlist(user=username, playlist_id=playlist_id, fields = ["tracks","next"])
    tracks = playlist_dict["tracks"]
    c += Show_Songs(tracks)
    while(tracks["next"]):
        tracks = sp.next(tracks)
        c += Show_Songs(tracks)
    return c

def Process_SongsInPlaylist(username, playlist_id, youtube_id):
    youtube = get_authenticated_service()
    print("\nOK, aggiungo subito le canzoni alla playlist...\n")
    playlist_dict = sp.user_playlist(user=username, playlist_id=playlist_id, fields = ["tracks","next"])
    tracks = playlist_dict["tracks"]
    Process_Songs(tracks, youtube,youtube_id)
    while(tracks["next"]):
        tracks = sp.next(tracks)
        Process_Songs(tracks, youtube, youtube_id)



token = util.prompt_for_user_token(username, scope, client_id=CLIENT_ID , client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)


if token:
    sp = spotipy.Spotify(auth=token)
    print("Looking for available playlists...\n")
    results = sp.user_playlists(username)
    print("Found these playlists: \n")
    for elem in results["items"]:
        print(elem['name'])
    
    playlist_id = ""
    playlist_name = input("\nWhat playlist should i copy? \n\n>>")
    print("OK...")
    for elem in results["items"]:
        if elem["name"].find(playlist_name) != -1:
            try:
                playlist_id = elem["id"]
            except:
                break
    print("\nLooking for songs in the playlist...")
    count = Get_SongsInPlaylist(username, playlist_id)

    print("\n\nFound " + str(count) + " songs!\n")
        
    SONGREQUEST_PLAYLIST_ID = input("Insert the Youtube Playlist ID, which you can find in the Youtube URL of the Playlist\n\n>>")
    
    Process_SongsInPlaylist(username, playlist_id, SONGREQUEST_PLAYLIST_ID)

    print("\nEnded!\n")
else:
    print("Can't get token for " + username)
