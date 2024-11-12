import requests
import os

def search_yts_movies(query, year=None):
    url = "https://yts.mx/api/v2/list_movies.json"
    payload = {
        "query_term": query,
        "limit": 50
    }
    if year:
        payload["year"] = year

    response = requests.get(url, params=payload)
    data = response.json()

    if data["status"] == "ok" and data["data"]["movie_count"] > 0:
        return [movie for movie in data["data"]["movies"] if movie["title"].lower() == query.lower() and (not year or movie["year"] == year)]
    else:
        return []

def get_1080p_torrent_url(torrents):
    for torrent in torrents:
        if torrent["quality"] == "1080p":
            return torrent["url"]
    return None

def download_torrent_file(url):
    response = requests.get(url)
    with open("movie.torrent", "wb") as f:
        f.write(response.content)

def print_movie_info(movie):
    print(f"Title: {movie['title']}")
    print(f"Year: {movie['year']}")
    print(f"URL: https://yts.mx/movie/{movie['slug']}")

    torrent_url_1080p = get_1080p_torrent_url(movie['torrents'])
    if torrent_url_1080p:
        print(f"1080p Torrent URL: {torrent_url_1080p}")
        download_torrent_file(torrent_url_1080p)
        os.startfile("movie.torrent")

    print("\n")