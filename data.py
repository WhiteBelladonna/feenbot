import sqlite3
import discord
import re
from sqlite3 import Error
import util_text as ut
import util_parse as up

# class that handles all the database interactions
class Database():

    # initializing class
    def __init__(self):
        
        # the path the database is stored at
        self.path = "./data/feenbot.db"
        self.color = 16738079

        return

    # function that opens up a connection to said database
    def db_conn(self):

        try:
            # create a connection and cursor and return it
            conn = sqlite3.connect(self.path)
            cursor = conn.cursor()
            return conn, cursor
        except Error as e:
            print(e)

    # function to get a value from the data table
    def getData(self, keyword):

        # connect
        conn, cursor = self.db_conn()

        # grab the value
        cursor.execute('''SELECT VALUE from fee_data WHERE ID=?''',(keyword,))
        result = cursor.fetchone()[0]

        print("Loaded " + keyword + " from faq_data.")

        # close the connection
        conn.close()

        return result

    # function to get all the faq values, triggers and responses
    def getFAQ(self):

        # connect
        conn, cursor = self.db_conn()

        # check if the category is active
        cursor.execute('''SELECT * from faq_list WHERE active=1''') 
        result = cursor.fetchall()

        items = []

        # fill the list with all items and ids
        for i in range(len(result)):

            items.append(result[i])

        print("Loaded faq replies from faq_list.")

        return items

    # function to get a value from the feedback table
    def getFEED(self, keyword):

        # connect
        conn, cursor = self.db_conn()

        # grab the value
        cursor.execute('''SELECT VALUE from faq_feedback WHERE ID=?''',(keyword,))
        result = cursor.fetchone()[0]

        print("Loaded " + keyword + " from faq_feedback.")

        # close the connection
        conn.close()

        return result

    # function to get a value from the roles table
    def getROLE(self):

        # connect
        conn, cursor = self.db_conn()

        # check if the category is active
        cursor.execute('''SELECT * from faq_roles''') 
        result = cursor.fetchall()

        items = []

        # fill the list with all items and ids
        for i in range(len(result)):

            items.append(result[i])

        return items

    # function to get a value from the faqchannel table
    def getFCHANNEL(self):

        # connect
        conn, cursor = self.db_conn()

        # check if the category is active
        cursor.execute('''SELECT * from faq_channel where active=1''') 
        result = cursor.fetchall()

        items = []

        # fill the list with all items and ids
        for i in range(len(result)):

            items.append(result[i])

        items = sorted(items, key=lambda x: x[0])

        print("Loaded faq channel from faq_list.")

        return items


# class that stores all the important credentials and server info
class Credentials(Database):

    def __init__(self):

        super(Credentials, self).__init__()

        self.token = self.getData("TOKEN")
        self.admin = int(self.getData("ADMIN"))
        self.serverid1 = int(self.getData("SERVER1"))
        self.serverid2 = int(self.getData("SERVER2"))
        self.server1 = None
        self.server2 = None
        self.gamemsg = self.getData("GAMEMSG")
        self.msgchan = int(self.getData("MSGCHAN"))

        return

    def grabAll(self, bot):

        self.server1 = bot.get_guild(self.serverid1)
        print("loaded Server: " + str(self.server1))
        self.server2 = bot.get_guild(self.serverid2)
        print("loaded Server: " + str(self.server2))

        return 

# class that stores all the FAQ Data
class FAQReplies(Database):

    def __init__(self):

        super(FAQReplies, self).__init__()

        self.objects = []
        self.help_de = None
        self.help_en = None

        for item in self.getFAQ():
            trig_de = item[4]
            trig_en = item[5]
            text_de = item[6]
            text_en = item[7]

            self.objects.append(FAQObject(text_de=text_de, text_en=text_en, cl="Reply", trig_de=trig_de, trig_en=trig_en))

        self.genHelp()

        return

    def genHelp(self):

        help_de = []
        for item in self.objects:
            help_de.append(item.trig_de)

        embed1 = discord.Embed(color=self.color)
        embed1.add_field(name="FAQ Befehl:", value="f!aq + Suchwort", inline=False)
        embed1.add_field(name="Suchworte:", value=ut.kwdstring(help_de), inline=False)
        embed1.add_field(name="Feedback Einreichen:", value="f!eedback + _kompletter_ feedback Text", inline=False)
        embed1.add_field(name="English Commands:", value="Type fe!help", inline=False)
        embed1.set_footer(text="FAQBot created by Demolite®")

        help_en = []
        for item in self.objects:
            help_en.append(item.trig_en)

        embed2 = discord.Embed(color=self.color)
        embed2.add_field(name="FAQ Command:", value="fe!aq + Keyword", inline=False)
        embed2.add_field(name="Keywords:", value=ut.kwdstring(help_en), inline=False)
        embed2.add_field(name="Leave some Feedback:", value="f!eedback + _complete_ feedback text", inline=False)
        embed2.set_footer(text="FAQBot created by Demolite®")

        self.help_de = embed1
        self.help_en = embed2

        return

class FAQChannel(Database):

    def __init__(self):

        super(FAQChannel, self).__init__()

        self.objects = []

        for item in self.getFCHANNEL():
            heading = item[1]
            text_de = item[2]

            self.objects.append(FAQObject(text_de=text_de, cl="Channel", heading=heading))


# faq object class that represents a faq reply or a channel
class FAQObject():

    def __init__(self, text_de, text_en=None, cl="Reply", title=None, trig_de=None, trig_en=None, heading=None):

        self.color = 16738079

        if cl == "Reply":
            self.trig_de = self.parseList(trig_de)
            self.trig_en = self.parseList(trig_en)
            self.text_de = self.parseText(text_de)
            self.text_en = self.parseText(text_en)
            self.embed_de = self.genBed(self.text_de)
            self.embed_en = self.genBed(self.text_en)

        elif cl == "Channel":
            self.title = title
            self.text = self.parseText(text_de)
            self.heading = ut.createHeader(heading)
            self.embed_faq = self.genBed(self.text)
        
        return
        
    def parseList(self, array):

        return array.split(',')
        
    # function that generates a textarray with titles and text, based on the inputs
    def parseText(self, text):

        parsed = []
        if text is not None:
            titles = re.findall(r'{.+}\n', text)
            texts = re.sub(r'{.+}\n',"!.+", text)
            texts = texts.split("!.+")

            for i in range(len(titles)):

                title = titles[i].replace("{", "").replace("}\n", "")
                text = texts[i+1]

                parsed.append([title, text])

        return parsed

    # function tha generates an embed with titles and text
    def genBed(self, array):

        embed = discord.Embed(color=self.color)
        embed2 = None

        for i in range(len(array)):

            embed.add_field(name=array[i][0], value=array[i][1], inline=False)

        return embed


# class that handles all the feedback items
class Feedback(Database):

    def __init__(self):

        super(Feedback, self).__init__()

        self.channelid = int(self.getFEED("channel"))
        self.userid = int(self.getFEED("user"))
        self.channel = None
        self.user = None

        return

    # function that creates an embed for the feedback
    def genBed(self, ctx):

        author = "<@"+str(ctx.message.author.id)+">"
        creation = ut.createDate(ctx.message.created_at)
        header = "Neues Feedback vom " + creation
        message = ctx.message.content[9:]
        feedback = "Feedback von User: {} \n\n".format(author)
        feedback = feedback + message

        embed = discord.Embed(color=self.color)
        embed.add_field(name=header, value=feedback, inline=False)

        return embed

    def grabAll(self, bot, server):

        self.channel = bot.get_channel(self.channelid)
        print("Loaded Feedback Channel: " + str(self.channel))
        self.user = discord.utils.get(server.members, id=self.userid)
        print("Loaded Feedback Target: " + str(self.user))

        return


# class that handles all the role items
class Roles(Database):

    def __init__(self):

        super(Roles, self).__init__()

        self.roles = []

        for item in self.getROLE():

            self.roles.append(Role(item[1], item[2], item[3], item[4]))

        return

    def grabAll(self, bot, server):

        for role in self.roles:
            role.role = discord.utils.get(server.roles, id=role.roleid)
            role.emoji = discord.utils.get(server.emojis, name=role.emojiname)
            print("Loaded Role: " + str(role.role) + " and corresponding emoji: " + str(role.emoji.name))

        return

class Games(Database):

    def __init__(self):
        super(Games, self).__init__()

        return

    def getGame(self, table_id):

        conn, cursor = self.db_conn()

        # try to find the game in the table
        cursor.execute('''SELECT * from fee_games WHERE table_id=?''',(table_id,))
        result = cursor.fetchone()

        if result is not None:
            result = result[0]

        # close the connection
        conn.close()

        return result

    def newGame(self, data):

        conn, cursor = self.db_conn()

        values = (
            int(up.lookup(data, "table_id")),
            up.lookup(data, "table_title"),
            up.lookup(data, "table_system"),
            up.lookup(data, "table_lead"),
            up.lookup(data, "table_teaser"),
            int(up.lookup(data, "table_start")),
            int(up.lookup(data, "table_duration")))

        sql = '''INSERT INTO fee_games(table_id, table_title, table_system, table_lead, table_teaser, table_start, table_duration) VALUES (?,?,?,?,?,?,?)'''

        cursor.execute(sql, values)

        conn.commit()

        # close the connection
        conn.close()

        return 

    def updateGame(self, data):

        # create a connection and a cursor
        conn, cursor = self.db_conn()

        # store the table id
        table_id = up.lookup(data, "table_id")

        # try to find the game in the table and store the game
        cursor.execute('''SELECT * from fee_games WHERE table_id=?''',(table_id,))
        result = cursor.fetchone()

        # create a variable for the fetched results
        newresult = None

        # store the fetched results in an array
        if result is not None:
            newresult = [
                ["table_id", result[0]],
                ["table_title", result[1]],
                ["table_system", result[2]],
                ["table_lead", result[3]],
                ["table_teaser", result[4]],
                ["table_start", int(result[5])],
                ["table_duration", int(result[6])]
            ]

        values = (
            up.lookup(data, "table_title"),
            up.lookup(data, "table_system"),
            up.lookup(data, "table_lead"),
            up.lookup(data, "table_teaser"),
            int(up.lookup(data, "table_start")),
            int(up.lookup(data, "table_duration")),
            int(up.lookup(data, "table_id")))
            
        sql = '''UPDATE fee_games set table_title=?, table_system=?, table_lead=?, table_teaser=?, table_start=?, table_duration=? WHERE table_id =?'''

        cursor.execute(sql, values)

        conn.commit()

        #close the connection
        conn.close()

        return newresult

    def deleteGame(self, data):

        print("deleting")

        conn, cursor = self.db_conn()

        # store the table id
        table_id = up.lookup(data, "table_id")

        # try to find the game in the table
        cursor.execute('''SELECT * from fee_games WHERE table_id=?''',(table_id,))
        result = cursor.fetchone()

        newresult = None

        # store the fetched results in an array
        if result is not None:
            newresult = [
                ["table_id", result[0]],
                ["table_title", result[1]],
                ["table_system", result[2]],
                ["table_lead", result[3]],
                ["table_teaser", result[4]],
                ["table_start", result[5]],
                ["table_duration", result[6]]
            ]
            
        cursor.execute('''DELETE FROM fee_games WHERE table_id=?''',(table_id,))

        conn.commit()

        #close the connection
        conn.close()

        return newresult


class Role(Database):

    def __init__(self, roleid, rolemsg, roleemojiname, ismaster):

        self.roleid = int(roleid)
        self.role = None
        self.rolemsg = int(rolemsg)
        self.emojiname = roleemojiname
        self.emoji = None
        self.isMaster = int(ismaster)

        return

class Log(Database):
    def __init__(self, msg, aud=None):
        super(Log, self).__init__()

        self.msg = msg
        self.aud = aud

        self.message = None
        self.embed = None

        self.gen_message()

        return

    def gen_message(self):

        self.message = "A message has been deleted!"

        self.embed = discord.Embed(color=self.color)

        self.stats = "Message Author: <@" + str(self.msg.author.id)+"> \n Mod: <@" + str(self.aud.user.id) + "> \n Channel: " + str(self.msg.channel)

        self.embed.add_field(name="Stats: " , value=self.stats)

        self.embed.add_field(name="Message:", value=self.msg.content, inline=False)

        return