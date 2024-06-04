import pymongo
import pymongo.cursor
from obj_classes.lucci_user import LucciUser
from obj_classes.lucci_guild import LucciGuild
from typing import List
import discord
import random
import time
import math
import textwrap

class LucciServer:
    def __init__(self, address='localhost', port='27017', db='luccidb'):
        # Create connection to MongoDb
        print(f"Connecting to MongoDB at {address}:{port} ...")
        self.__client = pymongo.MongoClient(f"mongodb://{address}:{port}/")

        # Connect to the mongo database
        print(f"Connecting to {db} ...")
        self.__db = self.__client[db]

        # Check to make sure required collections exist, soft failures i.e. if
        # we fail, just create them
        print("Checking to make sure required collections exist ...")
        collections = self.__db.list_collection_names()

        # Check for and set up items database if it doesn't exist
        print("Checking 'items' exists ...")
        if 'items' not in collections:
            print(f"WARN: 'items' was not found in {db}, creating it now")
            self.__db.create_collection('items')
            
        else:
            print(f"PASS: 'items' found in {db}")

        # Check for and set up user database if it doesn't exist
        print("Checking 'users' exists ...")
        if 'users' not in collections:
            print(f"WARN: 'users' was not found in {db}, creating it now")
            self.__db.create_collection('users')
        else:
            print(f"PASS: 'users' found in {db}")
        
        # Display message to user that everything went ok
        print(f"{db} Successfully loaded and initialized and ready to use!")

    """
    ============================================================================
    = START METHODS RELATED TO USER                                            =
    = ------------------------------------------------------------------------ =
    ============================================================================    
    """      
    def __getUser(self, userId : int) -> LucciUser:
        foundUser : pymongo.cursor.Cursor = self.__db.get_collection('users').find_one({"id":userId})
        if not foundUser:
            return LucciUser(userId, "")
        return LucciUser(**foundUser)
    
    def __addUser(
        self,
        user : LucciUser
    ) -> None:
        self.__db.get_collection('users').insert_one(user.toDict())
    
    def __updateUser(self, user : LucciUser, fields : List[str] = []):
        userDict = user.toDict()
        if len(fields):    
            internal = {}
            for li in fields:
                internal[li] = userDict[li]
            self.__db.get_collection('users').update_one(
                {'id':user.id}, 
                { "$set": internal }
            )
        else:
            self.__db.get_collection('users').update_one(
                {'id':user.id}, 
                { "$set": userDict }
            )

    """
    ============================================================================
    = START METHODS RELATED TO GUILD                                           =
    = ------------------------------------------------------------------------ =
    ============================================================================    
    """   
    def __getGuild(self, guildId : int) -> LucciGuild:
        foundGuild : pymongo.cursor.Cursor = self.__db.get_collection('guilds').find_one({"id":guildId})
        if not foundGuild:
            return LucciGuild(guildId, "")
        return LucciGuild(**foundGuild)
    
    def __addGuild(
        self,
        guild : LucciGuild
    ) -> None:
        self.__db.get_collection('guilds').insert_one(guild.toDict())
    
    def __updateGuild(self, guild : LucciGuild, fields : List[str] = []):
        userDict = guild.toDict()
        if len(fields):    
            internal = {}
            for li in fields:
                internal[li] = userDict[li]
            self.__db.get_collection('guilds').update_one(
                {'id':guild.id}, 
                { "$set": internal }
            )
        else:
            self.__db.get_collection('guilds').update_one(
                {'id':guild.id}, 
                { "$set": userDict }
            )

    """
    ============================================================================
    = START HELPER METHODS                                                     =
    = ------------------------------------------------------------------------ =
    ============================================================================    
    """  
    def __checkUser(self, user : discord.User) -> LucciUser:
        player : LucciUser = self.__getUser(user.id)
        if not player.name:
            player.name = user.name
            self.__addUser(player)
        return player
    
    def checkGuild(self, guild : discord.Guild) -> LucciGuild:
        currentGuild : LucciGuild = self.__getGuild(guild.id)
        if not currentGuild.name:
            currentGuild.name = guild.name
            self.__addGuild(currentGuild)
        return currentGuild

    def __computeRank(self, exp : int, maxExp : int) -> int:
        m : int = (maxExp / 2154.43469003189)
        return int(math.pow(exp/m,3/5)) if exp < maxExp else maxExp
    
    def __computeExpToNext(self, rank : int, maxExp : int) -> int:
        m : int = (maxExp / 2154.43469003189)
        return int(m*math.pow(rank,5/3)) if rank < 100 else 0
        

    """
    ============================================================================
    = START AUTO COMMANDS                                                      =
    = ------------------------------------------------------------------------ =
    ============================================================================    
    """
    async def checkRank(self, user : discord.User, guild :discord.Guild) -> str:
        response : str = ""
        try:
            if user.bot == False:
                player : LucciUser = self.__checkUser(user)
                currentGuild : LucciGuild = self.checkGuild(guild)
                member : discord.Member = guild.get_member(user.id)
                player.exp += 1
                rank : int = self.__computeRank(player.exp, currentGuild.expCap)
                while rank > player.rank:
                    response = f"`{user.name}` Just reached Rank {rank}! Congratulations!"

                    # Rank up the player
                    player.rank += 1

                    strRank : str = str(rank)

                    # After ranking up, add and remove any roles the new rank adds/removes
                    if str(strRank) in currentGuild.roleMappings:
                        for roleId in currentGuild.roleMappings[strRank]['remove']:
                            await member.remove_roles(guild.get_role(roleId))
                        for roleId in currentGuild.roleMappings[strRank]['add']:
                            await member.add_roles(guild.get_role(roleId))
                    
                # Update the database
                self.__updateUser(player, ['exp','rank'])
        except:
            response = "Something went wrong :( please contact the developer and tell them you saw: CHERRY"
        return response
    
    
    """
    ============================================================================
    = START SERVER COMMANDS                                                    =
    = ------------------------------------------------------------------------ =
    ============================================================================
    """
    async def daily(self, user: discord.User, guild : discord.Guild) -> str:
        response : str = ""
        try:
            player : LucciUser = self.__checkUser(user)
            lucciGuild :LucciGuild = self.checkGuild(guild)

            # Get current time
            current : int = int(time.time())
            dt = current - player.lastDaily

            if dt > 86400:
                player.dailyCount+=1
                bonusCookies : int = round(random.randint(lucciGuild.dailyMin, lucciGuild.dailyMax)*(0.8*math.sqrt(player.dailyCount+1.5)))
                response = f"{user.mention} just collected their daily and got {bonusCookies} :cookie:."
                player.money += bonusCookies
                player.lastDaily = int(time.time())
                if dt < 172800:
                    if player.dailyCount > 1:
                        response += f" That's {player.dailyCount} days in a row, way to go!"
                else:
                    player.dailyCount = 1
            else:
                if dt < 86400:
                    hoursLeft : int = math.floor(24 - (dt / 3600 ))
                    minLeft : int = math.floor((3600 - (dt % 3600)) / 60)
                    secLeft : int = (3600 - (dt % 3600)) % 60
                    response = f"{user.mention} You already collected your daily. You can collect in: {hoursLeft} hours, {minLeft} minutes, and {secLeft} seconds."
            self.__updateUser(player, ['money','dailyCount','lastDaily'])
        except:
            response = "Something went wrong :( please contact the developer and tell them you saw: PINEAPPLE"
        return response

    async def members(self, guild : discord.Guild) -> str:
        response : str = ""
        try:
            statuses = {}
            for user in guild.members:
                if not user.bot:
                    if str(user.status) not in statuses:
                        statuses[str(user.status)] = 0
                    statuses[str(user.status)] += 1
            response = f"{guild.name} currently has {sum(statuses.values())} members\n"
            for status in statuses:
                response += f"**{status}:** {statuses[status]}\n"
        except:
            response = "Something went wrong :( please contact the developer and tell them you saw: STRAWBERRY"
        return response    

    async def next_rank(self, user : discord.User, guild : discord.Guild):
        response : str = ""
        try:
            player : LucciUser = self.__checkUser(user)
            server : LucciGuild = self.checkGuild(guild)
            toNext : int = self.__computeExpToNext(player.rank+1,server.expCap)
            bars : int = round(20*(player.exp/toNext))
            response = textwrap.dedent(f"""\
            {user.mention} You are currently Rank {player.rank}, you have {toNext-player.exp} to go until your next rank up
            `{player.exp}/{toNext} [{(bars*'|'):.<20}] {round(100*(player.exp/toNext))}%`\
            """)
        except:
            response = "Something went wrong :( please contact the developer and tell them you saw: WATERMELON"
        return response


        
    async def richest(self, guild: discord.Guild) -> str:
        response : str = ""
        try:
            ulist : List[LucciUser] = []
            for member in guild.members:
                if not member.bot:
                    player : LucciUser = self.__checkUser(member)
                    ulist.append(player)
            ulist = sorted(ulist, key=lambda x: x.money, reverse=True)[0:10]
            tokens = ['🥇', '🥈','🥉']
            resp=""
            for i, player in enumerate(ulist):
                token = (tokens[i] if i < len(tokens) else "  ")
                resp += f"{token} {(i+1):0>2} {player.name:.<40}{player.money}\n"
            response = f"```{resp}```"
        except:
            response =  "Something went wrong :( please contact the developer and tell them you saw: BANANA"
        return response
    
    async def set_daily_limits(self, guild : discord.Guild, daily_min : int = -1, daily_max : int = -1):
        response : str = ""
        try:
            lucciGuild : LucciGuild = self.checkGuild(guild)
            if daily_min >= 0 or daily_max >= 0:
                response = f"Success! "
                if daily_min >= 0:
                    response += f"Daily minimum was updated to be {daily_min} "
                    lucciGuild.dailyMin = daily_min
                if daily_max >= 0:
                    if daily_max >= lucciGuild.dailyMin:
                        response += f"Daily Maximum was updated to be {daily_max}"
                        lucciGuild.dailyMax = daily_max
                    else:
                        response += f"Daily maximum not updated, was less than {lucciGuild.dailyMin} which is set as the minimum"
                self.__updateGuild(lucciGuild, ["dailyMin","dailyMax"])
                
            else:
                response = "Warning: Must pass in either a `daily_min` or `daily_max` with this command"
        except:
            response = "Something went wrong :( please contact the developer and tell them you saw: DURIAN"
        return response
    
    async def set_pay_limits(self, guild : discord.Guild, min_pay : int = -1, max_pay : int = -1):
        response : str = ""
        try:
            lucciGuild : LucciGuild = self.checkGuild(guild)
            if min_pay >= 0 or max_pay >= 0:
                response = f"Success! "
                if min_pay >= 0:
                    response += f"Minimum pay for work was updated to be {min_pay} "
                    lucciGuild.dailyMin = min_pay
                if max_pay >= 0:
                    if max_pay >= lucciGuild.dailyMin:
                        response += f"Maximum pay for work was updated to be {max_pay}"
                        lucciGuild.dailyMax = max_pay
                    else:
                        response += f"Maximum pay not updated, was less than {lucciGuild.dailyMin} which is set as the minimum"
                self.__updateGuild(lucciGuild, ["dailyMin","dailyMax"])
                
            else:
                response = "Warning: Must pass in either a `min_pay` or `max_pay` with this command"
        except:
            response = "Something went wrong :( please contact the developer and tell them you saw: DRAGONFRUIT"
        return response

    async def set_bot_channel(self, guild : discord.Guild, channel : discord.TextChannel) -> str:
        response : str = ""
        try:
            currentGuild : LucciGuild = self.checkGuild(guild)
            currentGuild.botChannel = channel.id
            self.__updateGuild(currentGuild,['botChannel'])
            response = f"Success! From now on I'll post status updates to {channel.name}"
        except:
            response =  "Something went wrong :( please contact the developer and tell them you saw: LYCHEE"
        return response
    
    async def add_rank_up_role(
        self,
        guild : discord.Guild,
        rank : int,
        to_add : discord.Role,
        to_remove : discord.Role
    ) -> str:
        response = ""
        try:
            if to_add or to_remove:
                # Lookup guild
                lucciGuild : LucciGuild = self.checkGuild(guild)

                # If our guild has no prior mappings, initialize it
                if str(rank) not in lucciGuild.roleMappings:
                    lucciGuild.roleMappings[str(rank)] = {'add':[],'remove':[]}
                
                # Add new roles if applicable
                if to_add:
                    if to_add.id not in lucciGuild.roleMappings[str(rank)]['add']:
                        lucciGuild.roleMappings[str(rank)]['add'].append(to_add.id)
                    else:
                        response = f"Warning: {to_add.name} already in the role list for this rank, it will be skipped\n{response}"
                
                # Remove roles if applicable
                if to_remove:
                    if to_remove.id not in lucciGuild.roleMappings[str(rank)]['remove']:
                        lucciGuild.roleMappings[str(rank)]['remove'].append(to_remove.id)
                    else:
                        response = f"Warning: {to_remove.name} already in the role list for this rank, it will be skipped\n{response}"

                # Update database
                self.__updateGuild(lucciGuild,["roleMappings"])

                # Retroactively update members
                for member in guild.members:
                    if not member.bot:
                        user : LucciUser = self.__checkUser(member)
                        if to_add and user.rank >= rank and to_add not in member.roles:
                            await member.add_roles(to_add)
                        if to_remove:
                            if user.rank != rank and to_remove in member.roles:
                                await member.remove_roles(to_remove) 
                            elif user.rank == rank and to_remove not in member.roles:
                                await member.add_roles(to_remove)
                
                # if we made it this far and no warnings were present, go ahead and return success
                if response == "":
                    response = f"Success! updated role mappings for rank {rank}"
            else:
                response = "Error: Must specify either a role 'to_add' or 'to_remove' to use this command"
        except:
            response =  "Something went wrong :( please contact the developer and tell them you saw: KIWI" 
        return response

    async def remove_rank_up_role(
        self,
        guild : discord.Guild,
        rank : int,
        remove_from_add : discord.Role,
        remove_from_remove : discord.Role            
    ):
        response = ""
        try:
            if remove_from_add or remove_from_remove:
                # Lookup guild
                lucciGuild : LucciGuild = self.checkGuild(guild)

                rankStr : str = str(rank)

                # If our guild has no prior mappings, initialize it
                if str(rank) not in lucciGuild.roleMappings:
                    lucciGuild.roleMappings[rankStr] = {'add':[],'remove':[]}
                
                # Add new roles if applicable
                if remove_from_add:
                    if remove_from_add.id in lucciGuild.roleMappings[rankStr]['add']:
                        lucciGuild.roleMappings[rankStr]['add'].remove(remove_from_add.id)
                    else:
                        response = f"Warning: {remove_from_add.name} not found in the role list for this rank, it will be skipped\n{response}"
                
                # Remove roles if applicable
                if remove_from_remove:
                    if remove_from_remove.id in lucciGuild.roleMappings[rankStr]['remove']:
                        lucciGuild.roleMappings[rankStr]['remove'].remove(remove_from_remove.id)
                    else:
                        response = f"Warning: {remove_from_remove.name} not found in the role list for this rank, it will be skipped\n{response}"

                # Update database
                self.__updateGuild(lucciGuild,["roleMappings"])

                # Retroactively update members
                for member in guild.members:
                    if not member.bot:
                        if remove_from_add and remove_from_add in member.roles:
                            await member.remove_roles(remove_from_add)
                        if remove_from_remove and remove_from_remove in member.roles:
                            await member.remove_roles(remove_from_remove) 

                # if we made it this far and no warnings were present, go ahead and return success
                if response == "":
                    response = f"Success! updated role mappings for rank {rank}"
            else:
                response = "Error: Must specify either a role 'to_add' or 'to_remove' to use this command"
        except:
            response =  "Something went wrong :( please contact the developer and tell them you saw: COCONUT" 
        return response            
    
    async def whoami(self, user: discord.User) -> str:
        response : str = ""
        try:
            response = f"{user.mention}, you are {user.name} who has an id of {user.id}"
        except:
            response =  "Something went wrong :( please contact the developer and tell them you saw: ORANGE"
        return response

    async def work(self, user: discord.User) -> str:
        response : str = ""
        try:
            player : LucciUser = self.__checkUser(user)

            # Get current time
            current : int = int(time.time())
            dt = current - player.lastWork
            if dt < 3600:
                minLeft : int = math.floor((3600 - dt) / 60)
                secLeft : int = (3600 - dt) % 60
                response = f"{user.mention} You are already working. You must wait {minLeft} minutes and {secLeft} seconds before working agian."
            else:
                cookies : int = random.randint(10, 150)
                response = f"{user.mention} started working and earned {cookies} :cookie:"
                player.lastWork = int(time.time())
                player.money += cookies
                self.__updateUser(player, ['money','lastWork'])
        except:
            response =  "Something went wrong :( please contact the developer and tell them you saw: APPLE"
        return response

    def __del__(self):
        address, port = self.__client.address
        db = self.__db.name
        print(f"Closing connection to {db} on {address}:{port}")
        self.__client.close()