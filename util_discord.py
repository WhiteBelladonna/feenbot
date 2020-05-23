import discord
from datetime import datetime
import util_parse as up
import util_text as ut

class gameTable():

    def __init__(self, server):

        self.server = server
        self.table_id = None
        self.table_title = None
        self.table_system = None
        self.table_lead = None
        self.table_teaser = None
        self.table_start = None
        self.table_duration = None

        return

    async def createTable(self, table):

        # get all the values from the passed table
        self.table_id = up.lookup(table, "table_id")
        self.table_title = up.lookup(table, "table_title")
        self.table_system = up.lookup(table, "table_system")
        self.table_lead = up.lookup(table, "table_lead")
        self.table_teaser = ut.cleanHTML(up.lookup(table, "table_teaser"))
        self.table_start = up.lookup(table, "table_start")
        self.table_duration = up.lookup(table, "table_duration")

        # create a string to be used as a name for the table id channel
        self.table_start_time = datetime.fromtimestamp(int(self.table_start))
        self.table_start_text = str(self.table_start_time.hour).zfill(2) + str(self.table_start_time.minute).zfill(2) + "-uhr"
        self.info = "__Start " + self.table_start_text

        # create the category name and shorten it if needed (longer than 22 chars)
        if len(self.table_title) > 22:
            self.category_name = self.table_title[:22] + ".." + "-" + str(self.table_id)
        
        else:
            self.category_name = self.table_title[:22] + "-" + str(self.table_id)

        # create a category for the game name
        await self.server.create_category_channel(name=self.category_name)

        # get the category as an object
        self.category = discord.utils.get(self.server.categories, name=self.category_name)
        self.role = discord.utils.get(self.server.roles, id=712381285867323414)

        # set the correct permissions for the category
        await self.category.set_permissions(self.server.default_role, read_messages=False, send_messages=False)
        await self.category.set_permissions(self.role, read_messages=True, send_messages=True)

        # create new text and voice channels in the category
        overwrites = {
            self.server.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
            self.role: discord.PermissionOverwrite(send_messages=False, read_messages=True)
        }

        await self.category.create_text_channel(name=self.info, overwrites=overwrites)
        await self.category.create_text_channel(name="spieltisch")
        await self.category.create_voice_channel(name="spieltisch")
        await self.category.create_voice_channel(name="stille kammer")

        # get the status channel as an update
        await self.infoMessage(self.category)

        return


    async def updateTable(self, old, table):

        # get all the values from the passed table
        self.table_id = up.lookup(table, "table_id")
        self.table_title = up.lookup(table, "table_title")
        self.table_system = up.lookup(table, "table_system")
        self.table_lead = up.lookup(table, "table_lead")
        self.table_teaser = ut.cleanHTML(up.lookup(table, "table_teaser"))
        self.table_start = up.lookup(table, "table_start")
        self.table_duration = up.lookup(table, "table_duration")

        # get the old category name from the fetched table list and convert it into the discord standard notation
        self.old_table_title = up.lookup(old, "table_title")
        self.old_table_id = up.lookup(old, "table_id")

        if len(self.old_table_title) > 22:
            self.old_cat_name = self.old_table_title[:22] + ".." + "-" + str(self.old_table_id)
        
        else:
            self.old_cat_name = self.old_table_title[:22] + "-" + str(self.old_table_id)

        # create a string to be used as a name for the table id channel
        self.table_start_time = datetime.fromtimestamp(int(self.table_start))
        self.table_start_text = str(self.table_start_time.hour).zfill(2) + str(self.table_start_time.minute).zfill(2) + "-uhr"
        self.info = "__Start " + self.table_start_text

        if len(self.table_title) > 22:
            self.category_name = self.table_title[:22] + ".." + "-" + str(self.table_id)
        
        else:
            self.category_name = self.table_title[:22] + "-" + str(self.table_id)

        # get the category as an object
        self.category = discord.utils.get(self.server.categories, name=self.old_cat_name)

        if self.category is not None:
            await self.category.edit(name=self.category_name)

        else:
            return "NOTFOUND"

        # get the status channel as an update
        await self.infoMessage(self.category)

        return

    async def infoMessage(self, category, newname=None):

        for channel in category.channels:

            if channel.name.startswith("__"):

                if newname is not None:

                    await channel.edit(name=newname)

                async for message in channel.history(limit=40):

                    await message.delete()

                embed = discord.Embed(title=self.table_title, colour=4360181)

                embed.add_field(name="Runde:", value=self.table_title, inline=False)
                embed.add_field(name="System:", value=self.table_system, inline=False)
                embed.add_field(name="Leiter:", value=str(self.table_lead), inline=False)

                starttime = str(self.table_start_time.strftime('%a')) + " " + str(self.table_start_time.hour).zfill(2) + ":" + str(self.table_start_time.minute).zfill(2)

                embed.add_field(name="Start:", value=starttime, inline=False)

                duration = "ca." + str(self.table_duration) + " Stunden"

                embed.add_field(name="Dauer:", value=duration, inline=False)

                link = "https://feencon.conservices.de/spielrunden_details&id=" + str(self.table_id) + ".html"

                linktext = "Zur runde geht es [hier](" + link + ")"

                embed.add_field(name="Rundenlink:", value=linktext, inline=False)
                
                await channel.send("", embed=embed)

        return

    async def deleteTable(self, old, table):

        # get the old category name from the fetched table list and convert it into the discord standard notation
        self.old_table_title = up.lookup(old, "table_title")
        self.old_table_id = up.lookup(old, "table_id")

        if len(self.old_table_title) > 22:
            self.old_cat_name = self.old_table_title[:22] + ".." + "-" + str(self.old_table_id)
        
        else:
            self.old_cat_name = self.old_table_title[:22] + "-" + str(self.old_table_id)

        # get the category as an object
        self.category = discord.utils.get(self.server.categories, name=self.old_cat_name)

        if self.category is not None:

            for channel in self.category.channels:

                await channel.delete()

            await self.category.delete()

        else:

            for category in self.server.categories:

                if category.name.endswith("-" + str(self.old_table_id)):

                    for channel in category.channels:

                        await channel.delete()

                    await category.delete()

        return


