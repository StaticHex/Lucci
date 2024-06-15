from __future__ import print_function, division
from obj_classes.lucci_user import LucciUser
from obj_classes.lucci_guild import LucciGuild
from obj_classes.lucci_server import LucciServer
from typing import Dict, List
import os
from dotenv import load_dotenv
#from discord.ext import commands
import discord # type: ignore
from discord.ext.commands import has_permissions
import re
import aiohttp
import asyncio

# Create a new bot
bot = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(bot)

# Create connection to the mongodb server
servers : LucciServer = {}
guildCount : int = 0

# Get token
load_dotenv()
token=os.getenv("DISCORD_TOKEN")

async def register_guild(guild : discord.Guild):
    global servers
    global guildCount
    
    # Guild debug
    print(f"- id: {guild.id}, name: {guild.name}")

    servers[guild.id] = LucciServer(guild)
    guildCount+=1

    # Register daily
    @tree.command(name="daily", description="Allows the user to collect a daily bonus", guild=discord.Object(id=guild.id))
    async def daily(interaction: discord.Interaction):
        await interaction.response.send_message(await servers[interaction.guild.id].daily(interaction.user, interaction.guild))

    @tree.command(name="help", description="Displays help information for the bot", guild=discord.Object(id=guild.id))
    async def help(interaction : discord.Interaction):
        if interaction.guild.get_member(interaction.user.id).guild_permissions.administrator:
            await interaction.response.send_message(os.getenv("ADMIN_HELP"))
        else:
            await interaction.response.send_message(os.getenv("USER_HELP"))

    # Register members
    print(f"Registering members command with {guild.name}")
    @tree.command(name="members", description="Prints information about the server's player count", guild=discord.Object(id=guild.id))
    async def members(interaction: discord.Interaction):
        await interaction.response.send_message(await servers[interaction.guild.id].members(interaction.guild))

    # Register next_rank
    print(f"Registering next_rank command with {guild.name}")
    @tree.command(name="nextrank", description="Displays how close the user is from reaching the next rank", guild=discord.Object(id=guild.id))
    async def next_rank(interaction: discord.Interaction):
        await interaction.response.send_message(await servers[interaction.guild.id].next_rank(interaction.user, interaction.guild))

    # Register richest
    @tree.command(name="richest", description="Displays a list of users ranked by money earned", guild=discord.Object(id=guild.id))
    async def richest(interaction: discord.Interaction):
            await interaction.response.send_message(await servers[interaction.guild.id].richest(interaction.guild))

    # Register whoami
    print(f"Registering whoami command with {guild.name}")
    @tree.command(name="whoami", description="Prints out user's discord name and id", guild=discord.Object(id=guild.id))
    async def whoami(interaction: discord.Interaction):
            await interaction.response.send_message(await servers[interaction.guild.id].whoami(interaction.user))
    
    # Register work
    print(f"Registering work command with {guild.name}")
    @tree.command(name="work", description="Allows the user to work to earn cookies", guild=discord.Object(id=guild.id))
    async def work(interaction: discord.Interaction):
        await interaction.response.send_message(await servers[interaction.guild.id].work(interaction.user))

    @tree.command(
        name="add_rank_up_role", 
        description="""Used to assign roles to rank up levels.""", 
        guild=discord.Object(id=guild.id)
    )
    @has_permissions(administrator=True)
    async def add_rank_up_role(
        interaction : discord.Interaction, 
        rank : int, 
        to_add : discord.Role = None, 
        to_remove : discord.Role = None
    ):
        """Used to assign new roles to rank up levels. Note, for now this is limited to one choice for add and
        remove due to discord limitations so just run the command multiple times, sorry :(

        Parameters
        -----------
        rank: int
            The specific rank to assign levels to
        to_add : List[discord.Role]
            A list of roles to add when the assigned rank is reached
        to_remove : List[discord.Role]
            A list of roles to remove when the assigned rank is reached
        """
        await interaction.response.send_message(await servers[interaction.guild.id].add_rank_up_role(
            interaction.guild,
            rank,
            to_add,
            to_remove
        ))

    print(f"Registering set_bot_channel command with {guild.name}")
    @tree.command(name="set_bot_channel", description="Used to set the channel id for the bot to publish status updates to", guild=discord.Object(id=guild.id))
    @has_permissions(administrator=True)
    async def set_bot_channel(interaction : discord.Interaction, channel : discord.TextChannel):
        """Used to set the channel id for the bot to publish status updates to

        Parameters
        -----------
        channel: discord.TextChannel
            the channel to target when posting status updates like level ups
        """
        await interaction.response.send_message(await servers[interaction.guild.id].set_bot_channel(interaction.guild, channel))

    print(f"Registering set_daily_limits command with {guild.name}")
    @tree.command(name="set_daily_limits", description="Used to set the max/min cookie values for the daily command", guild=discord.Object(id=guild.id))
    @has_permissions(administrator=True)
    async def set_daily_limits(interaction : discord.Interaction, daily_min : int = -1, daily_max : int = -1):
        """Used to set the max/min cookie values for the daily command

        Parameters
        -----------
        daily_min: int
            The minimum number of cookies to award for the daily command
        daily_max: int
            The maximum number of cookies to award for the daily command
        """
        await interaction.response.send_message(await servers[interaction.guild.id].set_daily_limits(interaction.guild, daily_min, daily_max))

    print(f"Registering set_pay_limits command with {guild.name}")
    @tree.command(name="set_pay_limits", description="Used to set the max/min cookie values for the work command", guild=discord.Object(id=guild.id))
    @has_permissions(administrator=True)
    async def set_pay_limits(interaction : discord.Interaction, min_pay : int = -1, max_pay : int = -1):
        """Used to set the max/min cookie values for the work command

        Parameters
        -----------
        min_pay: int
            The minimum number of cookies to award for the work command
        max_pay: int
            The maximum number of cookies to award for the work command
        """
        await interaction.response.send_message(await servers[interaction.guild.id].set_pay_limits(interaction.guild, min_pay, max_pay))
    
    print(f"Registering remove_rank_up_role command with {guild.name}")
    @tree.command(
        name="remove_rank_up_role", 
        description="""Used to remove roles to rank up levels.""", 
        guild=discord.Object(id=guild.id)
    )
    @has_permissions(administrator=True)
    async def remove_rank_up_role(
        interaction : discord.Interaction, 
        rank : int, 
        remove_from_add : discord.Role = None, 
        remove_from_remove : discord.Role = None
    ):
        """Used to assign new roles to rank up levels. Note, for now this is limited to one choice for add and
        remove due to discord limitations so just run the command multiple times, sorry :(

        Parameters
        -----------
        rank: int
            The specific rank to assign levels to
        remove_from_add : List[discord.Role]
            A list of roles to add when the assigned rank is reached
        remove_from_remove : List[discord.Role]
            A list of roles to remove when the assigned rank is reached
        """
        await interaction.response.send_message(await servers[interaction.guild.id].remove_rank_up_role(
            interaction.guild,
            rank,
            remove_from_add,
            remove_from_remove
        ))

    # Sync commands
    print(f"Syncing commands with {guild.name}")
    await tree.sync(guild=discord.Object(id=guild.id))

@bot.event
async def on_ready():
    global guildCount

    print("Checking server list:")
    for guild in bot.guilds:
        await register_guild(guild)
    print(f"Serveassist found in {guildCount} guilds")

@bot.event
async def on_guild_join(guild : discord.Guild):
    global guildCount
    print(f"Updating server list with {guild.name}")
    await register_guild(guild)
    print(f"Serveassist found in {guildCount} guilds after adding {guild.name}")

@bot.event
async def on_guild_remove(guild : discord.Guild):
    global guildCount
    guildCount -= 1
    print(f"{guild.name} just de-registered, Lucci now used in {guildCount} guilds")
    tree.clear_commands(guild=guild)

@bot.event
async def on_message(message : discord.Message):
    if message.author == bot.user:
        return
    if not  message.author.bot:
        try:
            # Rank check
            rankUpMessage : str = await servers[message.guild.id].checkRank(message.author, message.guild)
            currentGuild : LucciGuild = servers[message.guild.id].checkGuild(message.guild)
            if rankUpMessage != "":
                if currentGuild.botChannel > 0:
                    channel : discord.TextChannel = bot.get_channel(currentGuild.botChannel)
                    await channel.send(rankUpMessage)
                else:
                    await message.channel.send(rankUpMessage)

            # Command check
            formatted : str = re.sub(r'[\t\r\ ]+', '', message.content.lower())
            # Register !daily
            if re.search(r'^\!daily$', formatted):
                await message.channel.send(await servers[message.guild.id].daily(message.author, message.guild))

            # Register !help
            if re.search(r'^\!help$', formatted):
                if message.guild.get_member(message.author.id).guild_permissions.administrator:
                    await message.channel.send(os.getenv("ADMIN_HELP"))
                else:
                    await message.channel.send(os.getenv("USER_HELP"))

            # Register !members
            if re.search(r'^\!members$', formatted):
                await message.channel.send(await servers[message.guild.id].members(message.guild))

            # Register !next_rank
            if re.search(r'^\!nextrank$', formatted):
                await message.channel.send(await servers[message.guild.id].next_rank(message.author, message.guild))

            # Register !richest
            if re.search(r'^\!richest$', formatted):
                await message.channel.send(await servers[message.guild.id].richest(message.guild))
            
            # Register !whoami
            if re.search(r'^\!whoami$', formatted):
                await message.channel.send(await servers[message.guild.id].whoami(message.author))

            # Register !work
            if re.search(r'^\!work$', formatted):
                await message.channel.send(await servers[message.guild.id].work(message.author))

        except:
            response = servers[message.guild.id].logError("CORNUCOPIA")
            await message.channel.send(response)

# Run bot
bot.run(token)