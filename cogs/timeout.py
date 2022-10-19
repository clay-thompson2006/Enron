import datetime
import config.config as config
import discord
from discord import Embed, Colour, DMChannel, User, Forbidden, NotFound, HTTPException
from cogs.utility import add_blacklist

async def timeout(ctx,member,reason):
    await ctx.delete(reason="Scam Link")
    duration = datetime.timedelta(minutes=config.timeout_time)
    try:
        await member.timeout_for(duration,reason=reason)
    except HTTPException:
        await ctx.reply(
            'Scam detected, but I failed to Timeout this member due to a Discord Server error'
        )
        return False
    embed = discord.Embed(description=f'{config.warning_emoji} `{ctx.author}` *has been timeout for sending scam link!*',color=config.embed_color_danger)
    await add_blacklist(ctx,member,reason='sending scam links')
    await ctx.channel.send(embed=embed)