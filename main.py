import discord
from discord.ext import commands
import requests
import os
import random
from plexServer import getPlexLibrary
from yts import search_yts_movies, print_movie_info
from discordCommands import send_embed
from plexapi.server import PlexServer
import shutil
import os
import math

# Define Discord bot with command prefix '!' and default intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

PLEX_URL = os.getenv("PLEXURL")
PLEX_TOKEN = os.getenv("PLEXTOKEN")

plex = PlexServer(PLEX_URL, PLEX_TOKEN)

# Create empty list to store user suggestions
suggestions = []

# Get a list of all the movies currently on the Plex account so that dulpicates are not downloaded
plexLibrary = getPlexLibrary()

# Event to print a message in console when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Command to add a movie to Plex server
@bot.command(name='plex')
async def add_suggestion(ctx):

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel
    await send_embed(ctx, f'Please enter the movie title', "Enter the title of the movie that you would like to add to the Plex server. \n\nPlease make sure that it is spelled correctly or else the search will not return the correct movie.", "orange")

    query = await bot.wait_for('message', check=check)
    movieTitle = query.content

    # Prompt user for movie title and year of release
    await send_embed(ctx, f'Please enter the movie year', "Enter the year that the movie was released.\n\nSome movies have the same name so it might not download the exact movie that you want to add. By adding the year of release we can make sure that we download the correct movie.", "orange")
    
    year_msg = await bot.wait_for('message', check=check)
    year = year_msg.content
    
    # Validate year input
    if len(year) > 4:
        await send_embed(ctx, f'Invalid year input.', "Please try again.", "red")
        return 0
    try:
        year = int(year) if year else None
    except ValueError:
        await send_embed(ctx, f'Invalid year input.', "Please try again.", "red")
        year = None
        return 0
    
    # Format movie title with year for searching
    requestedMovie = f'{movieTitle} ({year})'
    
    # If the requested movie is not already in the suggestions list and not in the Plex library, add it to the suggestions list and start downloading it
    if requestedMovie not in suggestions and requestedMovie not in plexLibrary:
        suggestions.append(requestedMovie)
        embed = discord.Embed(title=f'Downloading and Adding to Plex',description=f'{requestedMovie} is being downloaded and will be added to the Plex Server once it has completed.\n\nIf is not showing in the Plex Server after some time then try and refresh the metadata in Plex', color=discord.Color.green())
    # If the requested movie is already in the Plex library, let the user know and do not download it again 
    elif requestedMovie in plexLibrary:
        embed = discord.Embed(title=f'{requestedMovie} has already been added to Plex',description="This movie has already been added and will not download again.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return 0
    elif requestedMovie in suggestions and requestedMovie not in plexLibrary:
        embed = discord.Embed(title=f'{requestedMovie} has already been requested and is in the queue to download.', description="This movie has already been added and will not download again.\n\nThe movie is in the queue to be downloaded and will be added to the server shortly.",color=discord.Color.red())
        await ctx.send(embed=embed)
        return 0
    else:
        embed = discord.Embed(title=f'{requestedMovie} has already been added to Plex',description="This movie has already been added and will not download again.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return 0

    # Search for movie on YTS API
    movies = search_yts_movies(movieTitle, year)

    # If movie found, print movie info
    if movies:
        for movie in movies:
            print_movie_info(movie)
    else:
        await send_embed(ctx, f'{requestedMovie} was not found.', "The movie was not found. Check if the Title and Year are correct.\n\nIt is possible that a 1080p torrent is not availabe and will therefore not be picked up since we only download 1080p files.\n\nYou can also check if the movie is available on https://yts.mx/", "red")
        return 0
    await ctx.send(embed=embed)

# Command to return all available genres
@bot.command(name='genres')
async def allGenres(ctx):
    genre_list = ["All","Action","Adventure","Animation","Biography","Comedy","Crime","Documentary","Drama","Family","Fantasy","Film-Noir","Game-Show","History","Horror","Music","Musical","Mystery","News","Reality-TV","Romance","Sci-Fi","Sport","Talk-Show","Thriller","War","Western"]
    genreString = ""
    
    for i in genre_list:
        genreString = genreString + "\n" + i
    await send_embed(ctx, f'Available Genres', genreString, "orange")

# Command to return a suggested movie to the user based on the genre that they choose
@bot.command(name='suggest')
async def add_suggestion(ctx):
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel
    base_url = "https://yts.mx/api/v2/"
    search_url = base_url + "list_movies.json"
    genre_list = ["all","action","adventure","animation","biography","comedy","crime","documentary","drama","family","fantasy","film-noir","game-show","history","horror","music","musical","mystery","news","reality-tv","romance","sci-fi","sport","talk-show","thriller","war","western"]
    # Define dictionary to store suggested movies and their ratings
    suggested_movies = {}
    embed = discord.Embed(title=f'Please enter the Movie Genre', description="Not sure what to watch? \n\nEnter a genre and we will return a suggestion. You can download the movie if it looks interesting or skip to the next movie.", color=discord.Color.orange())
    await ctx.send(embed=embed)

    title_msg = await bot.wait_for('message', check=check)
    genre = title_msg.content

    if genre.lower() not in genre_list:
        embed = discord.Embed(title=f'Invalid Genre', description=f"To get a list of all genres type !genres", color=discord.Color.orange())
        await ctx.send(embed=embed)
        msg = await bot.wait_for('message', check=check)
        response = msg.content

    page = random.randint(1, 10)
    while True:

        # Send GET request to YTS API to search for movies with entered genre and rating of more than 7
        response = requests.get(search_url, params={"genre": genre, "age": "en", "quality":"1080p", "minimum_rating": 7, "sort_by": "download_count", "page": int(page)}).json()

        # Get list of movie dictionaries from API response
        try:
            movie_list = response["data"]["movies"]
        except:
            embed = discord.Embed(title=f'Oh No!', description=f"Looks like there was an error with the genre. Please try again with another Genre.", color=discord.Color.orange())
            await ctx.send(embed=embed)
            return 0

       # Filter out movies that have already been suggested or are already on the Plex server
        movie_list = [movie for movie in movie_list if movie["title"] not in suggested_movies and not plex.search(movie["title"])]

        # If no more movies available, exit loop
        if not movie_list:
            embed = discord.Embed(title=f'Oh No!', description=f"No more movies available on this page that have a 7+ rating. Exiting.", color=discord.Color.orange())
            await ctx.send(embed=embed)
            break

        # Randomly select a movie from the remaining list
        selected_movie = random.choice(movie_list)

        # Store movie title and rating in suggested_movies dictionary
        suggested_movies[selected_movie["title"]] = selected_movie["rating"]
        summary = selected_movie['summary']
        if summary == "":
            summary = "No Summary Available :("
        embed = discord.Embed(title=f'{selected_movie["title"]} ({selected_movie["year"]})', description=f"IMDB Rating: {selected_movie['rating']}\n\nSummary: {summary} \n\nType 'Y' to download the movie, type 'N' to skip or type 'X' to exit", color=discord.Color.orange())
        await ctx.send(embed=embed)

        # Print movie title and summary
        print(f"\nTitle: {selected_movie['title']}")
        print(f"Summary: {selected_movie['summary']}")
        print(selected_movie)
        
        msg = await bot.wait_for('message', check=check)
        response = msg.content
        if response.lower() != 'y':
            # If user says no, continue to next iteration of loop
            if response.lower() == "n":
                continue
            if response.lower() == "x":
                embed = discord.Embed(title=f'Exiting', description=f"Closing the request", color=discord.Color.orange())
                await ctx.send(embed=embed)
                return 0
            if response.lower() != "n":
                embed = discord.Embed(title=f'Invalid Response', description=f"Type 'Y' to download the movie or type 'N' to skip", color=discord.Color.orange())
                await ctx.send(embed=embed)
                msg = await bot.wait_for('message', check=check)
                response = msg.content
        
        if response.lower() == "y":
            query = selected_movie['title']

            year_input = selected_movie['year']

            suggestion_text = f'{query} ({year_input})'
            if suggestion_text not in suggestions and suggestion_text not in list:
                suggestions.append(suggestion_text)
                embed = discord.Embed(title=f'Downloading and Adding to Plex',description=f'{suggestion_text} is being downloaded and will be added to the Plex Server once it has completed.\n\nIf is not showing in the Plex Server after some time then try and refresh the metadata in Plex', color=discord.Color.green())
            elif suggestion_text in list:
                embed = discord.Embed(title=f'{suggestion_text} has already been added to Plex',description="This movie has already been added and will not download again.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return 0
            else:
                embed = discord.Embed(title=f'{suggestion_text} has already been added to Plex',description="This movie has already been added and will not download again.", color=discord.Color.red())
                await ctx.send(embed=embed)
                return 0

            try:
                year = int(year_input) if year_input else None
            except ValueError:
                embed = discord.Embed(title=f'Invalid year input.', description="Please try again.", color=discord.Color.red())
                await ctx.send(embed=embed)
                year = None
                return 0
            movies = search_yts_movies(query, year)

            if movies:
                for movie in movies:
                    print_movie_info(movie)
            else:
                embed = discord.Embed(title=f'{suggestion_text} was not found.',description="The movie was not found. Check if the Title and Year are correct.\n\nIt is possible that a 1080p torrent is not availabe and will therefore not be picked up since we only download 1080p files.\n\nYou can also check if the movie is available on https://yts.mx/", color=discord.Color.red())
            await ctx.send(embed=embed)
            print(suggestion_text)
            return 0

        # If user says yes, get more information about the movie from the YTS API and print it
        movie_id = selected_movie["id"]
        movie_url = base_url + f"movie_details.json?movie_id={movie_id}"
        movie_response = requests.get(movie_url).json()

# Command to return all available genres
@bot.command(name='space')
async def space(ctx):
    path = os.path.abspath(os.sep)  # Root directory for the current platform
    disk_usage = shutil.disk_usage(path)
    free_space = disk_usage.free

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if free_space < 1024.0:
            break
        free_space /= 1024.0

    free_space_formatted = f"{free_space:.2f} {unit}"

    print(f"Available disk space: {free_space_formatted} / 2.71 TB")
    percentageUse = 100 - free_space / 2710 * 100
    puse = round(percentageUse, 2)
    print(puse, "% Free")
    percentageFree = free_space / 2710 * 100
    puse2 = round(percentageFree, 2)
    print(puse2, "% Free")

    moviesPath = "D:\Plex Server\Movies"
    seriesPath = "D:\Plex Server\Series"

    m_total_size = 0
    for dirpath, dirnames, filenames in os.walk(moviesPath):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            m_total_size += os.path.getsize(file_path)

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if m_total_size < 1024.0:
            break
        m_total_size /= 1024.0
    m_folder_size_formatted = f"{m_total_size:.2f} {unit}"

    s_total_size = 0
    for dirpath, dirnames, filenames in os.walk(seriesPath):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            s_total_size += os.path.getsize(file_path)

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if s_total_size < 1024.0:
            break
        s_total_size /= 1024.0
    s_folder_size_formatted = f"{s_total_size:.2f} {unit}"

    print(f"Movies': {m_folder_size_formatted}")
    print(f"Series': {s_folder_size_formatted}")

    totalPath = "D:\Plex Server"

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(totalPath):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            total_size += os.path.getsize(file_path)

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if total_size < 1024.0:
            break
        total_size /= 1024.0
    folder_size_formatted = f"{total_size:.2f} {unit}"

    embed = discord.Embed(title=f'Available Space on Plex Drive', description=f"{puse}% Used\n{puse2}% Free\n\nAvailable disk space: {free_space_formatted} of 2.71 TB\n\nMovies: {m_folder_size_formatted}\nSeries: {s_folder_size_formatted}\n\nTotal size of Plex Server: {folder_size_formatted}", color=discord.Color.orange())
    await ctx.send(embed=embed)
bot.run(os.getenv('botToken'))