from datetime import datetime, timedelta
import time
import config.config as config
import discord
from discord import Embed, Colour, DMChannel, User, Forbidden, NotFound, HTTPException
import json
from discord.ui import Button, View
import pymongo
client = pymongo.MongoClient(config.mongodb)
database = client['main']
collection_users = database.get_collection("users")
collection_guilds = database.get_collection("guilds")

async def kick_user(ctx,member,reason):
    await member.kick(reason=reason)
    return True
async def ban_user(ctx,member,reason):
    await member.ban(reason=reason)
    return True

async def verification_log(user,interaction,status):
    try:
        guild_data = collection_guilds.find_one({'guild_id':interaction.guild.id})
        if guild_data['log_channel'] != None:
            channel = interaction.guild.get_channel(guild_data['log_channel'])
            embed = discord.Embed(title=f"{user}'s Verification Results:")
            embed.set_footer(text=user.name, icon_url=user.avatar.url)
            embed.set_thumbnail(url=interaction.guild.icon.url or None)
            description= f'**Member**: {user} ({user.id})\n**Creation**: `{user.created_at.strftime("%H:%M %p %B %d, %Y")}`'
            if status == 'Verified':
                embed.color = config.embed_color_success
                embed.description = description+f"\n**Status**: {status}"
                await channel.send(embed=embed)
            elif status == 'Blacklisted':
                embed.color = config.embed_color_danger
                embed.description = description+f"\n**Status**: {status}"
                await channel.send(embed=embed)
            elif status == 'Unverified':
                embed.color = config.embed_color_danger
                embed.description = description+f"\n**Status**: {status}"
                await channel.send(embed=embed)
            elif status == 'UnverifiedAge':
                embed.color = config.embed_color_danger
                embed.description = description+f"\n**Status**: Kicked (Min Age`)"
                await channel.send(embed=embed)
            elif status == 'Alt':
                embed.color = config.embed_color_danger
                embed.description = description+f"\n**Status**: Alt Account"
                await channel.send(embed=embed)
            
    except:
        pass

async def add_blacklist(ctx,member,reason):
    try:
        collection_users.find_one_and_update({
            "user_id": member.id},
            {"$set": {
            "verified": 'blacked',
            "reason": reason
            }})
        embed = discord.Embed(description=f'{config.warning_emoji} `{ctx.author}` *has been blacklisted for sending scam link!*',color=config.embed_color_danger)
        await ctx.channel.send(embed=embed)
    except:
        collection_users.insert_one({
            "user_id": member.id,
            "verified": 'blacked',
            "reason": reason
        })
        embed = discord.Embed(description=f'{config.warning_emoji} `{ctx.author}` *has been blacklisted for sending scam link!*',color=config.embed_color_danger)
        await ctx.channel.send(embed=embed)

async def timeout_user(ctx,member,reason,timeouttime):
    duration = timedelta(seconds=timeouttime)
    try:
        await member.timeout_for(duration,reason=reason)
    except HTTPException:
        await ctx.reply(
            'I failed to Timeout this member due to a Discord Server error'
        )
        return False
    return True

async def suggestion_utility(bot,ctx,suggestion,channel):
    try:
        embed = discord.Embed(title='Suggestion', description=f"{suggestion}",color=config.embed_color_burple)
        embed.set_author(name=ctx.author, url=ctx.author.avatar.url)
        embed.set_thumbnail(url=ctx.author.avatar.url)
        await channel.send(embed=embed)
        embed1 = discord.Embed(description="Suggestion has been sent to developers!",color=config.embed_color_success)
        await ctx.respond(embed=embed1, ephemeral=True)
    except:
        return False
    return True

async def log_channel_update(bot,ctx,channel):
    try:
        guild_data = collection_guilds.find_one({"guild_id": ctx.guild.id})
        if guild_data:
            collection_guilds.find_one_and_update({
                "guild_id": ctx.guild.id},
                {"$set": {
                "log_channel": channel.id,
            }})
            role_id = guild_data['role_id']
            role = ctx.guild.get_role(int(role_id))
            channel_id = guild_data['verification_channel']
            if guild_data["memberage"] != None:
                memberage = guild_data["memberage"]
                memberage_action = guild_data["memberage_action"]
                member_age = f'{memberage} (Action: *{memberage_action}*)'
            else:
                member_age = 'None'
            verification_channel = ctx.guild.get_channel(int(channel_id))
            embed=discord.Embed(title='Log channel updated successfully!',description=f'**Server Name**: {ctx.guild.name}\n**Verified Role**: {role.mention}\n**Verification Channel**: {verification_channel.mention}\n**Logs Channel**: {channel.mention}\n**Minimum account age**: {member_age}',color=config.embed_color_burple)
            embed.set_footer(text=ctx.author.name,icon_url=ctx.author.avatar.url)
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title='Error',description=f'This server is not using our verification. Type `/setup` to start using our verification in {ctx.guild.name}',color=config.embed_color_danger)
            embed.set_footer(text=ctx.author.name,icon_url=ctx.author.avatar.url)
            await ctx.respond(embed=embed,ephemeral=True)
    except:
        embed = discord.Embed(title='Error',description=f'This server is not using our verification. Type `/setup` to start using our verification in {ctx.guild.name}',color=config.embed_color_danger)
        embed.set_footer(text=ctx.author.name,icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed,ephemeral=True)

async def account_age_update(bot,ctx,days,action):
    try:
        guild_data = collection_guilds.find_one({"guild_id": ctx.guild.id})
        if guild_data:
            collection_guilds.find_one_and_update({
                "guild_id": ctx.guild.id},
                {"$set": {
                "memberage": days,
                "memberage_action": action
            }})
            role_id = guild_data['role_id']
            role = ctx.guild.get_role(int(role_id))
            channel_id = guild_data['verification_channel']
            channel = ctx.guild.get_channel(int(channel_id))
            if guild_data['log_channel'] != None:
                log_channel_id = guild_data['log_channel']
                log_channel = ctx.guild.get_channel(int(channel_id))
                log_channel_mention = log_channel.mention
            else:
                log_channel_mention = 'None'
            embed=discord.Embed(title='Minimum account age updated successfully!',description=f'**Server Name**: {ctx.guild.name}\n**Verified Role**: {role.mention}\n**Verification Channel**: {channel.mention}\n**Logs Channel**: {log_channel_mention}\n**Minimum account age**: {days} (Action: *{action}*)',color=config.embed_color_burple)
            embed.set_footer(text=ctx.author.name,icon_url=ctx.author.avatar.url)
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title='Error',description=f'This server is not using our verification. Type `/setup` to start using our verification in {ctx.guild.name}',color=config.embed_color_danger)
            embed.set_footer(text=ctx.author.name,icon_url=ctx.author.avatar.url)
            await ctx.respond(embed=embed,ephemeral=True)
    except:
        embed = discord.Embed(title='Error',description=f'This server is not using our verification. Type `/setup` to start using our verification in {ctx.guild.name}',color=config.embed_color_danger)
        embed.set_footer(text=ctx.author.name,icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed,ephemeral=True)

async def verify_update(bot):
    view = discord.ui.View(timeout=None)
    for obj in collection_guilds.find():  
        role_id = obj['role_id']
        view.remove_item(verify_callback(role_id))
    for obj in collection_guilds.find():
        role_id = obj['role_id']
        view.add_item(verify_callback(role_id))
    bot.add_view(view)

class verify_callback(discord.ui.Button):
    def __init__(self, role: int):
        super().__init__(
            label='Verify',
            style=discord.ButtonStyle.primary,
            custom_id=str(role),
        )

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        role = interaction.guild.get_role(int(self.custom_id))
        try:
            user_data = collection_users.find_one({"user_id": user.id})
            guild_data= collection_guilds.find_one({"guild_id": interaction.guild.id})
            if user_data:
                pass
            else:
                collection_users.insert_one({
                "user_id": user.id,
                "verified": None
                })
                pass
        except:
            collection_users.insert_one({
                "user_id": user.id,
                "verified": None
            })
            pass
        if not guild_data['memberage'] == None:
            creation_data = user.created_at
            if time.time() - creation_data.timestamp() > int(guild_data['memberage'])*86400:
                pass
            else:
                action = guild_data['memberage_action']
                if not action == None:
                    if action == 'Kick':
                        await user.kick(reason=f'User age is less than `*{guild_data["memberage"]} days*` ')
                        await verification_log(user,interaction,status='UnverifiedAge')
                    elif action == 'Ban':
                        await user.ban(reason=f'User age is less than `*{guild_data["memberage"]} days*`')
                        await verification_log(user,interaction,status='UnverifiedAge')
        user_data = collection_users.find_one({"user_id": user.id})
        if role is None:
            return
        if role not in user.roles:
            if user_data['verified'] == True:
                    await user.add_roles(role)
                    await interaction.response.send_message(
                        f"You have been verified!",
                        ephemeral=True,
                    )
                    await verification_log(user,interaction,status='Verified')
            else:
                if user_data['verified'] == 'blacked':
                    await interaction.response.send_message(
                        f"You have been blacklisted for {user_data['reason']}!",
                        ephemeral=True,
                    )
                    await verification_log(user,interaction,status='Blacklisted')
                elif user_data['verified'] == 'Alt':
                    await interaction.response.send_message(
                        f"Our system has flagged your account as Alt account!",
                        ephemeral=True,
                    )
                    await verification_log(user,interaction,status='Alt')
                embed = discord.Embed(description=f'**This server is protected by Enron, ANTI-ALT account. You must verify to access the server.**',color=config.embed_color_primary)
                embed.add_field(name='Server',value=interaction.guild.name)
                embed.add_field(name='Status',value='Click here to verify!',inline=False)
                embed.add_field(name='By Clicking, you accept our',value='Privacy policy & ToS')
                embed.add_field(name='Need verification help?',value=f'[Support]({config.support})',inline=False)
                embed.add_field(name='Invite verification',value=f'[Invite Enron]({config.invite})',inline=False)
                await user.send(embed=embed)
                await verification_log(user,interaction,status='Unverified')
        elif role in user.roles:
            await interaction.response.send_message(
                    f"You are already verified!",
                    ephemeral=True,
                )

async def verify(bot,ctx,verification_channel,role):
        async def callback(interaction):
            user = interaction.user
            role = interaction.guild.get_role(int(interaction.custom_id))
            try:
                user_data = collection_users.find_one({"user_id": user.id})
                guild_data = collection_guilds.find_one({"guild_id": interaction.guild.id})
                if user_data:
                    pass
                else:
                    collection_users.insert_one({
                    "user_id": user.id,
                    "verified": None
                    })
            except:
                collection_users.insert_one({
                    "user_id": user.id,
                    "verified": None
                })
            if guild_data['memberage'] != None:
                creation_data = user.created_at
                if time.time() - creation_data.timestamp() > int(guild_data['memberage'])*86400:
                    pass
                else:
                    action = guild_data['memberage_action']
                    if not action == None:
                        if action == 'Kick':
                            await user.kick(reason=f'User age is less than `*{guild_data["memberage"]} days*`')
                            await verification_log(user,interaction,status='UnverifiedAge')
                        elif action == 'Ban':
                            await user.ban(reason=f'User age is less than `*{guild_data["memberage"]} days*`')
            user_data = collection_users.find_one({"user_id": user.id})
            if role is None:
                return
            if role not in user.roles:
                if user_data['verified'] == True:
                    await user.add_roles(role)
                    await interaction.response.send_message(
                        f"You have been verified!",
                        ephemeral=True,
                    )
                    await verification_log(user,interaction,status='Verified')
                else:
                    if user_data['verified'] == 'blacked':
                        await interaction.response.send_message(
                            f"You have been blacklisted for {user_data['reason']}!",
                            ephemeral=True,
                        )
                        await verification_log(user,interaction,status='Blacklisted')
                    elif user_data['verified'] == 'Alt':
                        await interaction.response.send_message(
                            f"Our system has flagged your account as Alt account!",
                            ephemeral=True,
                        )
                        await verification_log(user,interaction,status='Alt')
                    embed = discord.Embed(title=f'This server is protected by Enron, ANTI-ALT account. You must verify to access the server.',color=config.embed_color_primary)
                    embed.add_field(name='Server',value=interaction.guild.name)
                    embed.add_field(name='Status',value='Click here to verify!')
                    embed.add_field(name='By Clicking, you accept our',value='Privacy policy & ToS')
                    embed.add_field(name='Need verification help?',value=f'[Support]({config.support})')
                    embed.add_field(name='Invite verification',value=f'[Invite Enron]({config.invite})')
                    await user.send(embed=embed)
                    await verification_log(user,interaction,status='Unverified')
        button1 = Button(label="Verify",style=discord.ButtonStyle.green, custom_id=str(role.id))
        button1.callback = callback
        view1 = View(timeout=None)
        view1.add_item(button1)
        embed1=discord.Embed(title='Setup Completed',description=f'**Server Name**: {ctx.guild.name}\n**Verified Role**: {role.mention}\n**Verification Channel**: {verification_channel.mention}\n**Logs Channel**: None\n**Minimum account age**: None',color=config.embed_color_burple)
        embed1.set_footer(text=ctx.author.name,icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed1)
        embed=discord.Embed(title=f'{config.confirm_emoji} Verification Required',description=f'To gain access to `{ctx.guild.name}` you need to prove you are a human by completing verification. Click the button below to get started!',color=config.embed_color_burple)
        embed.set_thumbnail(url=ctx.guild.icon.url)
        await verification_channel.send(embed=embed,view=view1)
        try:
            guild_data = collection_guilds.find_one({"guild_id": ctx.guild.id})
            if guild_data:
                collection_guilds.find_one_and_update({
                "guild_id": ctx.guild.id},
                {"$set": {
                "verification_channel": verification_channel.id,
                "role_id": role.id
                }})
                pass
            else:
                collection_guilds.insert_one({
                "guild_id": ctx.guild.id,
                "verification_channel": verification_channel.id,
                "role_id": role.id,
                "log_channel":None,
                "memberage":None
                })
                pass
        except:
            collection_guilds.insert_one({
            "guild_id": ctx.guild.id,
            "verification_channel": verification_channel.id,
            "role_id": role.id,
            "log_channel":None,
            "memberage":None
            })
            pass
        await verify_update(bot)
        return True
