from __future__ import print_function, division
from obj_classes.lucci_user import LucciUser
from obj_classes.lucci_guild import LucciGuild
from obj_classes.lucci_server import LucciServer
from typing import Dict, List, Optional
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
task = None
async def check_rank(message : discord.Message):
    rankUpMessage = await servers[message.guild.id].checkRank(message.author, message.guild)
    currentGuild : LucciGuild = servers[message.guild.id].checkGuild(message.guild)
    if rankUpMessage != "":
        if currentGuild.botChannel > 0:
            channel : discord.TextChannel = bot.get_channel(currentGuild.botChannel)
            await channel.send(rankUpMessage)
        else:
            await message.channel.send(rankUpMessage)



# Get token
load_dotenv()
token=os.getenv("DISCORD_TOKEN")
uri=os.getenv("MONGO_URI")

async def register_guild(guild : discord.Guild):
    global servers
    global guildCount
    
    # Guild debug
    print(f"- id: {guild.id}, name: {guild.name}")

    servers[guild.id] = LucciServer(
        guild=guild, 
        address=uri
    )
    guildCount+=1

    # Register cookies
    @tree.command(name="cookies", description="Allows the user to check how many cookies they or another user have", guild=discord.Object(id=guild.id))
    async def cookies(interaction: discord.Interaction, target : discord.User = None):
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.cookies(interaction.user, target))

    # Register daily
    @tree.command(name="daily", description="Allows the user to collect a daily bonus", guild=discord.Object(id=guild.id))
    async def daily(interaction: discord.Interaction):
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.daily(interaction.user, interaction.guild))

    @tree.command(name="help", description="Displays help information for the bot", guild=discord.Object(id=guild.id))
    async def help(interaction : discord.Interaction):
        await interaction.response.defer()
        if interaction.guild.get_member(interaction.user.id).guild_permissions.administrator:
            await interaction.followup.send(os.getenv("ADMIN_HELP"))
        else:
            await interaction.followup.send(os.getenv("USER_HELP"))

    # Register leaderboard
    print(f"Registering leaderboard command with {guild.name}")
    @tree.command(name="leaderboard", description="Displays a list of users ranked by money earned", guild=discord.Object(id=guild.id))
    @discord.app_commands.choices(choice_option=[
        discord.app_commands.Choice(name='Cookies', value='cookie'),
        discord.app_commands.Choice(name='Exp', value='exp'),
        discord.app_commands.Choice(name='Rank', value='rank')
    ])
    async def leaderboard(interaction: discord.Interaction, choice_option: str = None):
        if not choice_option:
            choice_option = 'cookie'
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.leaderboard(interaction.guild, choice_option))

    # Register members
    print(f"Registering members command with {guild.name}")
    @tree.command(name="members", description="Prints information about the server's player count", guild=discord.Object(id=guild.id))
    async def members(interaction: discord.Interaction):
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.members(interaction.guild))

    # Register mug
    print(f"Registering mug command with {guild.name}")
    @tree.command(name="mug", description="Used to steal cookies from another player", guild=discord.Object(id=guild.id))
    async def mug(interaction: discord.Interaction, target : discord.User):
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.mug(interaction.guild, interaction.user, target))

    # Register next_rank
    print(f"Registering next_rank command with {guild.name}")
    @tree.command(name="nextrank", description="Displays how close the user is from reaching the next rank", guild=discord.Object(id=guild.id))
    async def next_rank(interaction: discord.Interaction, user :discord.User=None):
        if not user:
            user = interaction.user
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.next_rank(user, interaction.guild))

    # Register rps
    print(f"Registering rps command with {guild.name}")
    @tree.command(name="rps", description="Used to play rock, paper, scissors, to earn cookies", guild=discord.Object(id=guild.id))
    async def rps(interaction: discord.Interaction, bet : int):
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.rps(bet, interaction=interaction))

    # Register whoami
    print(f"Registering whoami command with {guild.name}")
    @tree.command(name="whoami", description="Prints out user's discord name and id", guild=discord.Object(id=guild.id))
    async def whoami(interaction: discord.Interaction):
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.whoami(interaction.user))
    
    # Register work
    print(f"Registering work command with {guild.name}")
    @tree.command(name="work", description="Allows the user to work to earn cookies", guild=discord.Object(id=guild.id))
    async def work(interaction: discord.Interaction):
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.work(interaction.user))

    @tree.command(
        name="add_rank_up_role", 
        description="""Used to assign roles to rank up levels.""", 
        guild=discord.Object(id=guild.id)
    )

    # Register Add Rank Up Role
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
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.add_rank_up_role(
            interaction.guild,
            rank,
            to_add,
            to_remove
        ))

    print(f"Registering list_rank_up_roles command with {guild.name}")
    @tree.command(
        name="list_rank_up_roles", 
        description="""Used to list out roles assigned for a given rank.""", 
        guild=discord.Object(id=guild.id)
    )
    @has_permissions(administrator=True)
    async def list_rank_up_roles(
        interaction : discord.Interaction, 
        rank : int
    ):
        """Used to list out roles assigned for a given rank

        Parameters
        -----------
        rank: int
            The specific rank to list roles for
        """
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.list_rank_up_roles(
            interaction.guild,
            rank
        ))

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
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.remove_rank_up_role(
            interaction.guild,
            rank,
            remove_from_add,
            remove_from_remove
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
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.set_bot_channel(interaction.guild, channel))

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
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.set_daily_limits(interaction.guild, daily_min, daily_max))

    print(f"Registering set_exp_cap command with {guild.name}")
    @tree.command(name="set_exp_cap", description="Used to set the amount of experience needed to reach lvl 100", guild=discord.Object(id=guild.id))
    @has_permissions(administrator=True)
    async def set_exp_cap(interaction : discord.Interaction, new_exp_cap : int):
        """Used to set the amount of experience needed to reach lvl 100. Sets 
        level up growth rate for the server

        Parameters
        -----------
        new_exp_cap: int
            The new amount of experience needed to reach max level
        """
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.set_exp_cap(interaction.guild, new_exp_cap))

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
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.set_pay_limits(interaction.guild, min_pay, max_pay))

    print(f"Registering set_rank command with {guild.name}")
    @tree.command(name="set_rank", description="Used to set a member's rank to the specified rank", guild=discord.Object(id=guild.id))
    @has_permissions(administrator=True)
    async def set_rank(interaction : discord.Interaction, user : discord.User, new_rank : int = 1):
        """Used to set a member's rank to the specified rank

        Parameters
        -----------
        user : discord.User
            The user to set rank for
        new_rank: int
            The rank to set the user's rank to
        """
        await interaction.response.defer()
        server : LucciServer = servers[interaction.guild.id]
        await interaction.followup.send(await server.set_rank(user, interaction.guild, new_rank))

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
    global rankUpMessage
    global task
    if message.author == bot.user:
        return
    if not  message.author.bot:
        try:
            # Rank check
            if task == None or task.done():
                task = bot.loop.create_task(check_rank(message))
            # Command check
            formatted : str = re.sub(r'[\t\r\ ]+', ' ', message.content.lower())

            # Register cookies
            if re.search(r'^\!cookies$', formatted):
                await message.channel.send(await servers[message.guild.id].cookies(message.author))
            
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
            
            if re.search(r'^\!rps\ [0-9]+$', formatted):
                await message.channel.send(await servers[message.guild.id].rps(int(formatted.split(' ')[1]), message=message))

            # Register !leaderboard
            if re.search(r'^\!leaderboard$', formatted):
                await message.channel.send(await servers[message.guild.id].leaderboard(message.guild, "cookie"))

            if re.search(r'^\!mug$', formatted):
                await message.channel.send("Cannot use mug like this due to optional paramters, use /mug instead")
            
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