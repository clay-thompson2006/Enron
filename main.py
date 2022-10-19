import discord
import config.config as config
import time
from discord.ext import tasks
from cogs.timeout import timeout
from cogs.scam import scam_check
from cogs.utility import kick_user, ban_user,timeout_user, suggestion_utility,verify_update,verify,account_age_update,log_channel_update
from discord import Embed, Colour, DMChannel, User, Forbidden, NotFound, HTTPException
from discord.ui import Button, View
from discord import option
import json 
import datetime
import random   
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext import commands
import pymongo
from src.server import keep_alive

intents = discord.Intents().all()
bot = discord.Bot(intents=intents)
client = pymongo.MongoClient(config.mongodb)
database = client['main']
collection_users = database.get_collection("users")
collection_guilds = database.get_collection("guilds")


@tasks.loop(seconds=300)
async def update_status():
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="Sampath#6145"))
        time.sleep(20)
        await bot.change_presence(status=discord.Status.online,activity=discord.Activity(type=discord.ActivityType.listening, name=f'{len(bot.guilds)}'))

@bot.event
async def on_ready():
    print(f"Logged as {bot.user.name}({bot.user.id})")
    database_log = bot.get_channel(config.database_log_channel)
    database = discord.Embed(description=f'*{config.confirm_emoji} Database connected successfully!*',color=config.embed_color_success)
    await database_log.send(embed=database)    
    update_status.start()
    await verify_update(bot)

@bot.event
async def on_guild_join(guild):
    guild_log = bot.get_channel(config.guild_log_channel)
    embed = discord.Embed(description=f"{config.add_emoji} Joined `{guild.name} ({guild.id})`",color=config.embed_color_success)
    await guild_log.send(embed=embed)

@bot.event
async def on_guild_remove(guild):
    guild_log = bot.get_channel(config.guild_log_channel)
    embed = discord.Embed(description=f"{config.remove_emoji} Left `{guild.name} ({guild.id})`",color=config.embed_color_danger)
    await guild_log.send(embed=embed)

@bot.slash_command(description='Setup verification for server')
@discord.default_permissions(manage_guild=True)
async def setup(ctx,verification_channel:discord.Option(discord.TextChannel,description='Select a verification channel'), role: discord.Option(discord.Role, description='Select role to be added to user after verification')):
    await verify(bot,ctx,verification_channel,role)
    await verify_update(bot)

@bot.slash_command(description='Changes the setting for the minimum account age')
@discord.default_permissions(manage_guild=True)
async def account_age(ctx,days:discord.Option(int,description='Amount of days the user account to bypass the account-age restriction.'), action: discord.Option(str, description='The action I will take if the user does not bypass the account-age restriction.', choices=["Kick", "Ban", "None"])):
    await account_age_update(bot,ctx,days,action)        
    await verify_update(bot)


@bot.slash_command(description='Changes the setting for the log channel')
@discord.default_permissions(manage_guild=True)
async def update_logs(ctx,channel:discord.Option(discord.TextChannel,description='The verification channel users will use to be able to verify them selfs.')):
    await log_channel_update(bot,ctx,channel)        
    await verify_update(bot)

@bot.listen()
async def on_message(message):
    if message.author.bot or isinstance(message.channel, DMChannel):
        return
    await scam_check(message)


@bot.slash_command(description='Suggestion for bot')
@commands.cooldown(1, 5, commands.BucketType.user)
async def suggestion(ctx,suggestions:discord.Option(str, description='What you want to suggest?')):
    channel = bot.get_channel(config.suggestion_log_channel)
    await suggestion_utility(bot,ctx,suggestions,channel)

@bot.slash_command(description="Kick a member from the server")
@discord.default_permissions(kick_members=True)
async def kick(ctx,user:discord.Option(discord.Member, description="Please select a user to kick",required=True),reason:discord.Option(str, description="Why do you want to kick?",required=False)):
    if user.id == ctx.author.id:
        await ctx.respond(embed=discord.Embed(description=f"*You can't kick yourself*", color=config.embed_color_danger))
        return
    kick_embed = discord.Embed(description=f"*Please confirm to kick {user}*", color=config.embed_color_burple)
    confirm = Button(label="Confirm",style=discord.ButtonStyle.green)
    cancel = Button(label="Cancel",style=discord.ButtonStyle.red)
    view = View()
    view.add_item(confirm)
    view.add_item(cancel)
    async def button_callback(interaction):
        member = interaction.user
        if not member.id == ctx.author.id:
            return
        button1 = Button(label="Confirm",style=discord.ButtonStyle.green,disabled =True)
        button3 = Button(label="Cancel",style=discord.ButtonStyle.gray,disabled =True)
        view1 = View()
        view1.add_item(button1)
        view1.add_item(button3)
        responce_get = await kick_user(ctx,user,reason=reason)
        if responce_get == True:
            confirm_kick = discord.Embed(description=f"{config.confirm_emoji} {user} *has beeen kicked by* `{ctx.author}`",color=config.embed_color_success)
            await interaction.response.edit_message(embed=confirm_kick,view=view1) 
        else:
            pass
    async def button2_callback(interaction):
        member = interaction.user
        if not member.id == ctx.author.id:
            return
        button1 = Button(label="Confirm",style=discord.ButtonStyle.gray,disabled =True)
        button3 = Button(label="Cancel",style=discord.ButtonStyle.green,disabled =True)
        view1 = View()
        view1.add_item(button1)
        view1.add_item(button3)
        cancel_kick = discord.Embed(description=f"{config.error_emoji} Command has stopped.",color=config.embed_color_success)
        await interaction.response.edit_message(embed=cancel_kick,view=view1)
    await ctx.respond(embed=kick_embed, view=view)
    confirm.callback = button_callback
    cancel.callback = button2_callback


@bot.slash_command(description="Ban a member from the server")
@discord.default_permissions(ban_members=True)
async def ban(ctx,user:discord.Option(discord.Member, description="Please select a user to ban",required=True),reason:discord.Option(str, description="Why do you want to ban?",required=False)):
    if user.id == ctx.author.id:
        await ctx.respond(embed=discord.Embed(description=f"*You can't ban yourself*", color=config.embed_color_danger))
        return
    ban_embed = discord.Embed(description=f"*Please confirm to ban {user}*", color=config.embed_color_burple)
    confirm = Button(label="Confirm",style=discord.ButtonStyle.green)
    cancel = Button(label="Cancel",style=discord.ButtonStyle.red)
    view = View()
    view.add_item(confirm)
    view.add_item(cancel)
    async def button_callback(interaction):
        member = interaction.user
        if not member.id == ctx.author.id:
            return
        button1 = Button(label="Confirm",style=discord.ButtonStyle.green,disabled =True)
        button3 = Button(label="Cancel",style=discord.ButtonStyle.gray,disabled =True)
        view1 = View()
        view1.add_item(button1)
        view1.add_item(button3)
        responce_get = await ban_user(ctx,user,reason=reason)
        if responce_get == True:
            confirm_ban = discord.Embed(description=f"{config.confirm_emoji} {user} *has beeen banned by* `{ctx.author}`",color=config.embed_color_success)
            await interaction.response.edit_message(embed=confirm_ban,view=view1) 
        else:
            pass
    async def button2_callback(interaction):
        member = interaction.user
        if not member.id == ctx.author.id:
            return
        button1 = Button(label="Confirm",style=discord.ButtonStyle.gray,disabled =True)
        button3 = Button(label="Cancel",style=discord.ButtonStyle.green,disabled =True)
        view1 = View()
        view1.add_item(button1)
        view1.add_item(button3)
        cancel_ban = discord.Embed(description=f"{config.error_emoji} Command has stopped.",color=config.embed_color_success)
        await interaction.response.edit_message(embed=cancel_ban,view=view1)
    await ctx.respond(embed=ban_embed, view=view)
    confirm.callback = button_callback
    cancel.callback = button2_callback

@bot.slash_command(description="timeout a member")
@discord.default_permissions(ban_members=True)
@option("user", discord.Member, description="Whom you want timeout?")
@option("duration", description="How long they should be timed out?")
@option("duration_type", description="How long they should be timed out?", choices=["Seconds", "Hours", "Days"])
@option("reason", description="Why do you want timeout?",default=None)
async def timeout(ctx,user:discord.Member,duration:int,duration_type:str,reason:str):
    if user.id == ctx.author.id:
        await ctx.respond(embed=discord.Embed(description=f"*You can't timeout yourself*", color=config.embed_color_danger))
        return
    if reason == None:
        reason = "Not Provided"
    if duration_type == "Hours":
        time = int(duration)*3600
    elif duration_type == "Days":
        time = int(duration)*86400
    elif duration_type == "Seconds":
        time = int(duration)
    responce_check = await timeout_user(ctx,user,reason,time)
    if responce_check == True:
        timeout_embed = discord.Embed(description=f"*`{user}` has been timeout by `{ctx.author}`*", color=config.embed_color_success)
        timeout_embed.set_footer(text=f"Reason: {reason}")
        await ctx.respond(embed=timeout_embed)

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.delete()
        await ctx.send(
            'I dont have permissions to kick user', ephemeral=True
        )

@kick.error
async def ban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.delete()
        await ctx.send(
            'I dont have permissions to ban user', ephemeral=True
        )

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    if isinstance(error, commands.CommandOnCooldown):
        print(error)
        embed = discord.Embed(description="Command is on cooldown, Please try later",color=config.embed_color_danger)
        await ctx.respond(embed=embed)
    else:
        raise error 
keep_alive()
bot.run(config.bot_token)