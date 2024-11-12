import os
import asyncio
import discord
from discord.ext import commands
from plexapi.server import PlexServer
from Commands.spaceCommands import getSpace
from Data.plexLibrary import getPlexLibrary
from Commands.genresCommands import getGenres
from Commands.suggestionCommands import giveSuggestion
from Commands.plexCommands import processSuggestion, getSuggestion
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv('discordToken')
plex_url = os.getenv('PLEXURL')
plex_token = os.getenv('PLEXTOKEN')

intents = discord.Intents.default()
intents.message_content = True

class PlexBot(commands.Bot):
    async def setup_hook(self):
        self.loop.create_task(periodic_metadata_refresh())

bot = PlexBot(command_prefix='!', intents=intents)

suggestions = []

plex = PlexServer(plex_url, plex_token)
plexLibrary = getPlexLibrary(plex)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='plex')
async def plex_command(ctx):
    movieTitle, year = await getSuggestion(ctx, bot)
    await processSuggestion(ctx, suggestions, plexLibrary, movieTitle, year)

@bot.command(name='suggest')
async def suggest_command(ctx):
    await giveSuggestion(ctx, bot, suggestions, plexLibrary, plex)

@bot.command(name='genres')
async def genres_command(ctx):
    await getGenres(ctx, should_send_embed=True)

@bot.command(name='space')
async def space_command(ctx):
    await getSpace(ctx)

async def periodic_metadata_refresh():
    await bot.wait_until_ready()
    while not bot.is_closed():
        print("Refreshing Plex metadata...")
        plex.library.refresh()
        await asyncio.sleep(60)

bot.run(bot_token)
