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

                duration = "ca. " + str(self.table_duration) + " Stunden"

                embed.add_field(name="Dauer:", value=duration, inline=False)

                link = "https://feencon.conservices.de/spielrunden_details&id=" + str(self.table_id) + ".html"

                linktext = "Zum Rundenaushang geht es [hier](" + link + ")"

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


class Permissions():

    def __init__(self, server):

        self.groups = {
            "Fairy Pearls": 699293101080182877,
            "Würfel-Meister": 699311346055118863,
            "Fabienne Siegmund": 699316903578959934,
            "Schirakis Illustrationen": 699317010697551962,
            "Karsten Zingsheim": 699317086270259271,
            "Phantagrafie": 699317137000497204,
            "Die Zeitreisende": 699317176921751723,
            "Drachenwinter": 699322902142648434,
            "Bernhard Hennen und Robert Corvus": 699317214146330704,
            "storylike Gmbh": 699317397445673162,
            "Vanessa Tolentino": 699317299831636100,
            "Elegance of Crafting": 699317454312308817,
            "CATcraft": 699317546314104933,
            "Lysandra Books Verlag": 699317594922156062,
            "Heinrich Tüffers Verlag": 699317635736666174,
            "Truant UG": 699317649758486588,
            "Yvis Nerd and Geek World": 699317674546692177,
            "Sphärenmeisters Spiele": 699317676350373890,
            "Uhrwerk Verlag": 699317677587693638,
            "Pegasus Spiele GmbH": 699317680137699400,
            "Shadodex - Verlag der Schatten": 699317681295196230,
            "Paper Adventures e.V.": 699317696634028144,
            "Janika Hoffmann": 699317697954971719,
            "Tiny Demons": 699317699075113010,
            "Jessica Bernett": 699317699280633921,
            "Verlag Torsten Low": 699317699934945281,
            "Francis Bergen": 699317701470060584,
            "Florian Clever": 699317701939691560,
            "Lisa Dröttboom": 699317702308921356,
            "Glauconar Yue": 699317703801831495,
            "Artificus": 699317704070397992,
            "Märchenspinnerei": 699317704976498849,
            "Ulf Fildebrandt": 699317705781674119,
            "Don Kringel": 699317706763272224,
            "Laura Kier": 699317707354407002,
            "Sandra Florean": 699317708042534913,
            "Atelier Tag Eins": 699317709099368579,
            "Nordlichtphantasten": 699317709820788846,
            "Jeanette Peters": 699317710823096351,
            "Katha's Artworks": 699317711498510429,
            "Lars Czekalla & Janina Robben": 699317712278650881,
            "Chrissis Traumladen": 699317713142546554,
            "Philipp Börner": 699317713776017540,
            "hartplastikbehaelter": 699317715009273857,
            "Linestyle Artwork": 699317715529367582,
            "Minni": 699317716225490985,
            "JP Stories": 699317717676851401,
            "NordCon GbR": 699317717995356270,
            "Metwabe": 699317719065165896,
            "HeldenWelten": 699317720289771590,
            "52": 699317720990351460,
            "53": 699317722093453403,
            "54": 699317722680393859,
            "55": 699317723792015431,
            "56": 699317724332949565,
            "57": 699317725155164281,
            "58": 699317726447140954,
            "59": 699317726694473779,
            "60": 699317727579471974,
            "61": 699317728514801685,
            "62": 699317729169113149,
            "63": 699317729785675818,
            "64": 699317730867806340,
            "65": 699317731953999902,
            "66": 699317732621156402,
            "67": 699317733590040647,
            "68": 699317734281969806,
            "69": 699317735074562114,
            "70": 699317736047771688,
            "71": 699317736853078066,
            "72": 699317738190929972,
            "73": 699317738308370443,
            "74": 699317739499814943,
            "75": 699317740435013703,
            "76": 699317741919928442,
            "77": 699317742515257406,
            "78": 699317744176332890,
            "79": 699317744734306504,
            "80": 699317745564778567,
            "81": 699317747099631657,
            "82": 699317747259015189,
            "83": 699317748353859616,
            "84": 699317750048489553,
            "85": 699320538245628055,
            "86": 699320517160861706,
            "87": 699320518859423785,
            "88": 699320520386281542,
            "89": 699320521925460028,
            "90": 699320523607244931,
            "91": 699320525054410834,
            "92": 699320526551908397,
            "93": 699320530897076365,
            "94": 699320532809547806,
            "95": 699320534764224702,
            "96": 699320536366448661,
            "97": 699320515478814742,
            "98": 699320893289267312,
            "99": 699320897961459814,
            }

        self.roles = {
            "guests": 699280541798760469,
            "editor": 699241660034318407,
            "team": 699276860713992302,
        }

        self.server = server

        self.vendor_cat = discord.PermissionOverwrite(
            read_messages = True,
            send_messages = True,
            read_message_history = True,
            manage_messages = True,
            mute_members= True,
            deafen_members= True,
            move_members= True,
            priority_speaker=True
        )

        self.default_cat = discord.PermissionOverwrite(
            read_messages = False,
            send_messages = False,
            read_message_history = False
        )

        self.guest_cat = discord.PermissionOverwrite(
            read_messages = True,
            send_messages = True,
            read_message_history = True
        )

        self.guest_txt = discord.PermissionOverwrite(
            read_messages = True,
            send_messages = False,
            read_message_history = True
        )

        self.team_cat = discord.PermissionOverwrite(
            read_messages = True,
            send_messages = True,
            read_message_history = True
        )

        self.team_txt = discord.PermissionOverwrite(
            read_messages = True,
            send_messages = False,
            read_message_history = True
        )

        self.vendor_txt = discord.PermissionOverwrite(
            read_messages = True,
            send_messages = True,
            read_message_history = True,
            manage_messages = True
        )

        self.vendor_role = discord.Permissions(
            create_instant_invite = False,
            kick_members = False,
            ban_members = False,
            administrator = False,
            manage_channels = False,
            manage_guild = False,
            add_reactions = True,
            view_audit_log = False,
            priority_speaker = False,
            stream = True,
            read_messages = True,
            view_channel = True,
            send_messages = True,
            send_tts_messages = False,
            manage_messages = False,
            embed_links = True,
            attach_files = True,
            read_message_history = True,
            mention_everyone = False,
            external_emojis = True,
            view_guild_insights = False,
            connect = True,
            speak = True,
            mute_members = False,
            deafen_members = False,
            move_members = False,
            use_voice_activation = True,
            change_nickname = True,
            manage_nicknames = False,
            manage_roles = False,
            manage_permissions = False,
            manage_webhooks = False,
            manage_emojis = False,
        )

        return

    async def readPerms(self):

        print("\n Fixing Permissions for:")

        for category in self.server.categories:

            if category.name in self.groups:
                print("\n------------------------")
                print(category.name + "\n")

                vendorID = self.groups.get(category.name)
                guestID = self.roles.get("guests")
                editorID = self.roles.get("editor")
                teamID = self.roles.get("team")

                print("Fetching Roles:")

                vendorrole = discord.utils.get(self.server.roles, id=vendorID)
                guestrole = discord.utils.get(self.server.roles, id=guestID)
                editorrole = discord.utils.get(self.server.roles, id=editorID)
                teamrole = discord.utils.get(self.server.roles, id=teamID)

                print("   - " + vendorrole.name)
                print("   - " + guestrole.name)
                print("   - " + editorrole.name)
                print("   - " + teamrole.name)

                print("\nApplying new Permissions")
                
                if len(category.name) == 2:
                    await category.set_permissions(self.server.default_role,  overwrite=self.default_cat)
                    await category.set_permissions(vendorrole, overwrite=self.vendor_cat)
                    await category.set_permissions(guestrole, overwrite=self.guest_cat)
                    await category.set_permissions(editorrole, read_messages=True, send_messages=True, read_message_history=True)

                else:
                    await category.set_permissions(self.server.default_role, overwrite=self.default_cat)
                    await category.set_permissions(vendorrole, overwrite=self.vendor_cat)
                    await category.set_permissions(guestrole, overwrite=self.guest_cat)
                    await channel.set_permissions(teamrole, overwrite=self.team_cat)

                print("\nApplying Sync to Channels:")

                for channel in category.channels:

                    print("   - " + channel.name)

                    await channel.edit(sync_permissions=True)

                if len(category.name) > 2:

                    print("\nEditing Vendor Channel")

                    for channel in category.channels:

                        if channel.name.startswith("stand-von"):

                            print("   - " + channel.name)

                            await channel.edit(sync_permissions=False)
                            await channel.set_permissions(guestrole, overwrite=self.guest_txt)
                            await channel.set_permissions(teamrole, overwrite=self.team_txt)
                            await channel.set_permissions(vendorrole, overwrite=self.vendor_txt)

                else:

                    print("\nLeerer Stand")
                    
        return


    async def fixServerPerms(self):

        print("\n Fixing Permissions for:")

        for role in self.server.roles:

            if role.name in self.groups:

                print("\n------------------------")
                print(role.name + "\n")
                
                await role.edit(permissions=self.vendor_role)

        return
