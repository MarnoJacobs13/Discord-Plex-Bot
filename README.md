Discord-Plex Movie Request Bot
A Discord bot that allows users to request movies from YTS, download them automatically via torrent, and add them directly to your Plex server. Simplify media requests and keep your Plex library updated effortlessly.

Features
Movie Requests: Users can request movies within your Discord server, and the bot will handle the download process.
Automated Downloads: Integrates with YTS for direct movie downloads via torrent.
Plex Integration: Automatically adds downloaded movies to your Plex library for seamless playback.

Requirements
Make sure you have the following set up:

Python 3.8+
Plex Media Server (configured and accessible via the Plex API)
Discord Server (where the bot will operate)
BitTorrent Client (for downloading movies)

Discord Setup
Create a New Application in the Discord Developer Console.
Add Permissions to the bot:

Send Messages
Read Message History
Use Slash Commands
Configure OAuth2 Scopes:

Under OAuth2 settings, add the following scopes:
identity
openid
messages.read
bot
Install the Bot on your Discord server by generating an invite link in the Developer Console and inviting it to your server.

Plex Setup
To find the Plex URL and Plex Token, right click on a movie in your plex server and click on "Get Info". Click on "View XML". Copy the URL. The Plex URL will be the first value and the token will be at the end.

Bittorrent Setup
Update the "Put new downloads in" preference to the path of your Plex Movies folder

ENV
Create a .env file in the root of the project:
PLEXURL = 'plex url' # eg https://192-123-4-567.aaaaaaaaaaaaaaaaaaaaaa.plex.direct:12345/
PLEXTOKEN = 'plex token'
discordToken = 'discord bot token'
moviesPath = "path to folder containing plex movies"
plexMovieServer = "name of plex server"
seriesPath = "path to folder containing plex series"
rootPath = "path to root folder containing movies / series subfolders"

Running the Bot
To start the bot, simply run the main.py file
To request a movie, send "!plex" in the discord server
You will then be prompted to enter the name of the movie
After providing the name you will have to provide the year of the movie as well
The bot will only download movies from YTS so if the movies are not on there then it will not be downloaded
