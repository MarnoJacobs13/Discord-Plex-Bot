import discord

async def send_embed(ctx, x, y, z):
    if z == "orange":
        z = discord.Color.orange()
    elif z == "red":
        z = discord.Color.red()
    elif z == "green":
        z = discord.Color.green()
    embed = discord.Embed(title=x, description=y, color=z)
    await ctx.send(embed=embed)