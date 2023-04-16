from discord.ext import commands
import os
import json
from plexapi.server import PlexServer
import os
from dotenv import load_dotenv

load_dotenv()

PLEX_URL = os.getenv("PLEXURL")
PLEX_TOKEN = os.getenv("PLEXTOKEN")

plex = PlexServer(PLEX_URL, PLEX_TOKEN)

def getPlexLibrary():
# Get all movies in the server and their release year
    movies = []
    list = []
    for video in plex.library.section('Movies').all():
        movies.append({
            'title': video.title,
            'year': video.year
        })
    # Export the movie list to a JSON file
    with open('movie_list.json', 'w') as f:
        json.dump(movies, f)
    
    for movie in movies:
        list.append(f"{movie['title']} ({movie['year']})")
        print(list)
    
    return list
    