import discord
from discord.ext import commands, tasks

import random
import subprocess
import sys
import time
import datetime

from fuzzywuzzy import fuzz

import data
import util_text as ut
import util_parse as up
import util_discord

import aiohttp
import asyncio

print('------')
print("Initializing")
print('------')

prefixes = ["!"]
bot = commands.Bot(command_prefix=prefixes)
bot.remove_command("help")

# object that stores all the database credentials
cred = data.Credentials()

# object that stores the faq replies
faq = data.FAQReplies()

# object that handles all the feedback requests
feedback = data.Feedback()

# object that stores all the roles
roles = data.Roles()

# object for the faqchannel
faqchannel = data.FAQChannel()

# chances
fuzzy = [90,82]
mirnchance = 42

# # # # # # # # # # 
# S C H E D U L E #
# # # # # # # # # # 

# class RoleChecker(commands.Cog):

#     def __init__(self, bot):

#         self.bot = bot
#         self.printer.start()

#     def cog_unload(self):
#         self.printer.cancel()

#     @tasks.loop(hours=1)
#     async def printer(self):

#         print("TESTING")

#     @printer.before_loop
#     async def before_printer(self):
#         print('waiting...')
#         await self.bot.wait_until_ready()


async def echo_handler(reader, writer):

    data = await reader.readline()
    message = data.decode()
    addr = writer.get_extra_info('peername')
    msg = "Received %r from %r" % (message, addr)
    print(msg)

    table = message.replace("\n","").split(".|.")

    for i in range(len(table)):

        table[i] = table[i].split("-|-")

    table_request = up.lookup(table, "table_request")

    if table_request == "new":

        result = await newTable(table)

    elif table_request == "update":

        result = await updateTable(table)

    elif table_request == "delete":

        result = await deleteTable(table)

        
    result = result.encode()
    print("Send: %r" % result)
    writer.write(result)
    await writer.drain()

    print("Close the client socket")
    writer.close()


# # # # # # #
# ROLE ADD  #
# # # # # # #
@bot.event
async def on_raw_reaction_add(payload):

    # iterate through all the roles and check for a fitting one
    for role in roles.roles:
        
        # if the message id matches a role id, and the emoji is correct
        if payload.message_id == role.rolemsg and payload.emoji.name == role.emojiname:

            for server in cred.serverlist:

                if server.id == role.serverid:

                    # grab the user
                    user = discord.utils.get(server.members, id=payload.user_id)

            # if the user is not in the members of the role
            try:
                if user not in role.role.members:

                    # add the user to the role
                    await user.add_roles(role.role)
                    print("Added " + str(user) + " to " + str(role.role) +" role!")
                    return

                else:
                    print(str(user) + " already has the " + str(role.role) + " role!")
                    return
            except:
                pass

    return

# # # # # # # #
# # ROLE DEL  #
# # # # # # # #
@bot.event
async def on_raw_reaction_remove(payload):


    # iterate through all the roles and check for a fitting one
    for role in roles.roles:
        
        # if the message id matches a role id, and the emoji is correct
        if payload.message_id == role.rolemsg and payload.emoji.name == role.emojiname:

            for server in cred.serverlist:

                if server.id == role.serverid:

                    # grab the user
                    user = discord.utils.get(server.members, id=payload.user_id)

            # if the role is the master role:
            if role.isMaster == 1:

                # iterate through all the roles and kick the user out of every single one
                for role2 in roles.roles:
                    try:
                        await user.remove_roles(role2.role)
                    except:
                        pass

                print("Removed " + str(user) + " from all roles!")
                return

            else:

                # if the user is the members of the role
                if user in role.role.members:

                    # remove the user from the role
                    await user.remove_roles(role.role)
                    print("Removed " + str(user) + " from " + str(role.role) +" role!")
                    return

                else:
                    print(str(user) + " already removed from " +  str(role.role) + " role!")
                    return

    return

# # # # # # #
# SHUTDOWN  #
# # # # # # #
@bot.command(name="shutdown")
async def shutdown(ctx):
    if ctx.prefix == "!":
        if ctx.author.id == cred.admin:
            await ctx.send("Shutting down...")
            await bot.close()
        else:
            await ctx.message.channel.send("Computer sagt nein.")
            print(str(ctx.author) + " tried to access command !shutdown! " + str(ctx.author.id))
            return

# # # # # # #
#  RESTART  #
# # # # # # #
@bot.command(name="restart")
async def restart(ctx):
    if ctx.prefix == "!":
        if ctx.author.id == cred.admin:
           await ctx.message.channel.send("Restarting...")
           subprocess.Popen([sys.executable, "./restart.py"])
           await bot.close()
           return
        else:
            await ctx.message.channel.send("Computer sagt nein.")
            print(str(ctx.author) + " tried to access command !shutdown! " + str(ctx.author.id))
            return

# # # # # # #
#  UPDATE   #
# # # # # # #
@bot.command(name="update")
async def update(ctx):
    if ctx.prefix == "!":
        if ctx.author.id == cred.admin:
           await ctx.message.channel.send("Updating...")
           subprocess.Popen([sys.executable, "./update.py"])
           await bot.close()
           return
        else:
            await ctx.message.channel.send("Computer sagt nein.")
            print(str(ctx.author) + " tried to access command !shutdown! " + str(ctx.author.id))
            return

# # # # # # #
# NEW TABLE #
# # # # # # #
async def newTable(table):

    # get the game id from the received id object
    table_id = up.lookup(table, "table_id")

    channel = bot.get_channel(cred.statuschan)

    # check if the game with the given id already exists in the database
    if data.Games().getGame(table_id = table_id) == None:

        data.Games().newGame(table)

        # create a new game room with all the bells and whistles
        ct = util_discord.gameTable(cred.server1)
        
        await ct.createTable(table)

        await channel.send("New game **" + ct.table_title + "** has been created!")

        return "GameCreated;" + str(ct.invite)
        # now also returns the invite

    # if it already exists, return an error code
    else:

        await channel.send("Game with the id **" + table_id + "** already exists!")

        return "AlreadyExists;"

    return

# # # # # # #
# UPD TABLE #
# # # # # # #
async def updateTable(newtable):

    # get the game id from the received id object
    table_id = up.lookup(newtable, "table_id")

    channel = bot.get_channel(cred.statuschan)

    # check if the game with the given id already exists in the database
    if data.Games().getGame(table_id = table_id) is not None:

        old = data.Games().updateGame(newtable)

        if old is not None:

            # create a new game room with all the bells and whistles
            ct = util_discord.gameTable(cred.server1)
            
            await ct.updateTable(old, newtable)

            await channel.send("Game **" + ct.old_cat_name + "** has been updated to **" + ct.table_title + "**!")

            return "GameUpdated;"

    # if it already exists, return an error code
    else:

        await channel.send("Game with the id **" + table_id + "** does not exist!")

        return "GameNotFound;"

    return


# # # # # # #
# DEL TABLE #
# # # # # # #
async def deleteTable(newtable):

    # get the game id from the received id object
    table_id = up.lookup(newtable, "table_id")

    channel = bot.get_channel(cred.statuschan)

    # check if the game with the given id already exists in the database
    if data.Games().getGame(table_id = table_id) is not None:

        old = data.Games().deleteGame(newtable)

        if old is not None:

            # create a new game room with all the bells and whistles
            ct = util_discord.gameTable(cred.server1)
            
            await ct.deleteTable(old, newtable)

            await channel.send("Game **" + ct.old_cat_name + "** has been deleted!")

            return "GameDeleted;"

    # if it already exists, return an error code
    else:

        await channel.send("Game with the id **" + table_id + "** does not exist!")

        return "GameNotFound;"

    return 

# # # # # # #
# ! PRUNE ! #
# # # # # # #
@bot.command(name="prune")
async def prune(ctx):
    if ctx.prefix == "!":
        if ctx.author.id == cred.admin:
            async for message in ctx.channel.history(limit=50):
                await message.delete()
            return
        else:
            await ctx.message.channel.send("Computer sagt nein.")
            print(str(ctx.author) + " tried to access command prune! " + str(ctx.author.id))
            return

# # # # # # # 
# FIX PERMS #
# # # # # # # 

@bot.command(name="fix")
async def fix(ctx):

    if ctx.prefix == "!":
        if ctx.author.id == cred.admin:

            await ctx.message.channel.send("Repariere Berechtigungen für Händlerkanäle..")

            start = datetime.datetime.now()

            utd = util_discord.Permissions(cred.server2)

            await utd.readPerms()

            end = datetime.datetime.now()

            duration = end-start

            await ctx.message.channel.send("Berechtigungen repariert. Dauer: " + str(duration.total_seconds()) + " Sekunden")

            return

@bot.command(name="fixRoles")
async def fixRoles(ctx):

    if ctx.prefix == "!":
        if ctx.author.id == cred.admin:

            await ctx.message.channel.send("Repariere Berechtigungen für Händlerrollen..")

            start = datetime.datetime.now()

            utd = util_discord.Permissions(cred.server2)

            await utd.fixServerPerms()

            end = datetime.datetime.now()

            duration = end-start

            await ctx.message.channel.send("Berechtigungen repariert. Dauer: " + str(duration.total_seconds()) + " Sekunden")

            return


@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    channel = bot.get_channel(cred.msgchan)

    await bot.process_commands(message)

    if message.guild is None and message.author != bot.user:

        msg = str(message.author) + " hat eine Nachricht hinterlassen: \n" + message.content

        await channel.send(msg)

# bot.add_cog(RoleChecker(bot))

@bot.event
async def on_ready():
    print('-----------')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('-----------')
    # get the items needed for running the bot
    cred.grabAll(bot)
    roles.grabAll(bot, cred.serverlist)
    feedback.grabAll(bot, cred.server1)
    #roles.grabAll(bot, cred.server)
    await bot.change_presence(activity=discord.Game(name=cred.gamemsg))
    print('-----------')
    print("Ready!")
    print('-----------')

    port = 10000
    while True:
        try:
            await bot.loop.create_task(asyncio.start_server(echo_handler, '127.0.0.1', port, loop=bot.loop))
            print("Launched TCP Server on port: " + str(port))
            break
        except:
            print("Launching TCP on port: " + str(port) + " has failed. Retrying...")
            port += 1
            pass

bot.run(cred.token, bot=True, reconnect=True)

