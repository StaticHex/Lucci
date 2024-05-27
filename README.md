# Lucci v1.0

Social discord bot. Helps manage roles and boosts engagement 

## About

Lucci is a social engagement discord bot designed to keep users interacting with
the server while also providing some fun extras for users to do. The bot is split
into several major components to suit this purpose

### Rank System

The rank system is really the crux of this bot. The rank system allows roles to
be assigned/removed automatically the more users chat. This provides a way for
servers to 'age' their players automatically meaning certain channels can be
locked down for new users which can prevent trolling and also encourage
engagement 

### Shop System (Not Yet Implemented)

The shop system while not yet implemented is planned to allow users to purchase
items and roles using cookies which are earned through games, daily bonuses,
and working. Server owners will have full autonomy over items and effects

### Games (Not Yet Implemented)

Games provide entertainment for users as well as a way to keep users engaged in
the server. Some games will mirror casino games such as blackjack and slots
while others like truth or dare will facilitate discussion

## Dependencies

* Python 3.12 or later
* MongoDB
* The `discord` python module
* The `dotenv` python module
* The `pymongo` python module

## Future Release TODO

* Implement Shop
* Implement Games
* Code Cleanup
* Add 

## Installation instruction

1. If not installed, install python 3.12
2. Install MongoDB
3. Install all required python modules using pip
4. Upload html docs somewhere they're publically accessible
5. Create a new file called `.env` and add the following to it

```
DISCORD_TOKEN=<token for bot>
USER_HELP=<url to userdoc_EE8B01.html>
ADMIN_HELP=<url to admindoc_CB4E4A.html>
```

## Setup

1. Run `/set_bot_channel <your channel name>` on your server to select the 
channel you wish level up commands to be sent to. If no channel is sent it will
simply use the current channel.
2. [Optional] If using automatic role assignment based on rank, run  
`/add_rank_up_role <rank> <role to add on rank up> <role to remove on rank up>`
on your server to set up roles for each rank. Unfortunately, discord's api doesn't
allow me to pass lists of items so the command will have to be run multiple times
as it's only possible to add one rank to add and one rank to remove at once.
Inversely, if you make a mistake when using this command or later decide you
don't want a specific role associated with a given rank you can run 
`/remove_rank_up_role <role to stop adding on rank up> <role to stop removing on
rank up>`
3. [Optional] By default, the daily command is set up to give the user between
50 and 150 cookies (give or take a few based on streak multipliers). If you wish
to change this you can by running `/set_daily_limits <lower limit> <upper limit>`
4. [Optional] By default, the work command is set up to pay the user between 50
and 150 cookies per use. If you wish you can change these values by running
`/set_pay_limits <lower limit> <upper limit>`

## User Commands

#### daily
Allows the user to collect a daily bonus

#### members
Prints metrics about the server's player count

#### next_rank
Displays how close the user is from reaching the next rank

#### richest
Displays a list of users ranked by money earned

#### whoami
Prints out user's discord name and id

#### work
Allows the user to work to earn cookies\

# Admin Commands

#### add_rank_up_role `rank:Number` `to_add:discord.Role` `to_remove:discord.Role`
Used to assign new roles to rank up levels. Note, for now this is limited to one choice for add and remove due to discord limitations so just run the command multiple times, sorry :(

Parameters:
- `rank : Number [Required]` - The rank to add role mappings to
- `to_add : discord.Role [Optional]` - A role to add when the specified rank is reached
- `to_remove : discord.Role [Optional]` - A role to remove when the specified rank is reached

#### set_bot_channel `channel:TextChannel`
Used to set the channel for the bot to post updates to

Parameters:
- `channel : TextChannel [Required]` - The channel to set as the channel for the bot to operate on

#### set_daily_limits `daily_min:Number` `daily_max:Number`
Used to set the max/min cookie values for the daily command

Parameters:
- `daily_min : Number [Optional]` - The minimum number of cookies to award for the daily command
- `daily_max : Number [Optional]` - The minimum number of cookies to award for the daily command

#### set_pay_limits `min_pay:Number` `max_pay:Number`
Used to set the max/min cookie values for the daily command

Parameters:
- `min_pay : Number [Optional]` - The minimum number of cookies to award for the work command
- `max_pay : Number [Optional]` - The minimum number of cookies to award for the work command

#### remove_rank_up_role `rank:Number` `remove_from_add:discord.Role` `remove_from_remove:discord.Role`
Used to assign new roles to rank up levels. Note, for now this is limited to one choice for add and remove due to discord limitations so just run the command multiple times, sorry :(

Parameters:
- `rank: Number [Required]` - The rank to remove role mappings from
- `remove_from_add: discord.Role [Optional]` - Remove one of the roles from the roles added when the specified rank is reached
- `remove_from_remove: discord.Role [Optional]` - Remove one of the roles from the roles removed when the specified rank is reached
