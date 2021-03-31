import db_bot as db
import os
import random
import shutil
from discord.ext import commands
import discord
from dotenv import load_dotenv
import sqlite3


#######################################################################################
# parameters

#database tables
teams = """CREATE TABLE IF NOT EXISTS teams (
            role integer PRIMARY KEY,
            name text NOT NULL,  
            text_channel integer NOT NULL,
            voice_channel integer NOT NULL,
            round1 integer NOT NULL,
            round2 integer NOT NULL,
            round3 integer NOT NULL,
            round4 integer NOT NULL,
            points integer NOT NULL
        );"""

members = """CREATE TABLE IF NOT EXISTS members (
        id integer PRIMARY KEY,
        name text NOT NULL,
        team integer NOT NULL
        );"""

    #FILE for database
database = "Datenbank.db"

    #allowed characters for teams
team_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890?-!=()[]"

    #boolean for greeting in text_channel of each team
global welcome
welcome = False

    #greeting which comes if welcome == True
greeting = "Hey .___."

    # category where all answer channels are
text = "Antworten/Answers"

    #category where all voice channels are
voice = "Quizecke/Talk"

    # maximum amount of players in one team
max_team = 4

    # amount of roles that are not deleted with reset
safe_roles = 2


######################################################################################
#Delete path and all files in path

def remove(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))


######################################################################################
# Bot start


    #get Token of Bot
load_dotenv()
token = os.getenv("TOKEN")
bot = commands.Bot(command_prefix = "!")

    #changing the boolean for welcome
@bot.command(name="welcome", help="!welcome")
async def welcome(ctx):

    global welcome
    welcome = not welcome
    print(f"WELCOME: changed to {welcome}")


    #creating db and every file to allow team-creating
@bot.command(name="init", help = "!init")
async def init(ctx):

    if not ctx.author.top_role.permissions.administrator:
        await ctx.send("You need power to do this :)")
        return

    try:
        con = db.create_connection(database)
        db.create_table(con, teams)
        db.create_table(con, members)
        await ctx.send("We are ready to go Sir!")
        print("INIT SUCCESS \n")
    except:
        print("INIT ERROR\n")
    finally:
        con.close()

    return



##########################################################################################
#bot create a group

@bot.command(name='group', help="!group <Name>                    Create team with NAME")
async def group(ctx, name):
    
    admin = ctx.author.top_role.permissions.administrator
    name = ctx.message.content[7:]
    author = ctx.author
    guild = ctx.guild
    con = db.create_connection(database)

        #check if name consists of illegal characters
    for i in name:
        if not i in team_characters:
            await ctx.send("Temname enthält unzulässiges Zeichen: "+i+"\n Team name has illegal character: "+i)

        #check if user is already in another team
    ls = db.fetch_members(con, author.id, "team")
    if len(ls) > 0:
        await ctx.send("Du bist leider bereits teil eines anderen Teams. \nVerwende !leave um dein Team jetztiges Team zu verlassen :P \n\nYou are already part of a team. Use !leave to leave your current team.")
        return


        #create role, voice channel, text channel
    try:
            #create role and fetch categories for channels
        role = await guild.create_role(name = name, mentionable = True, hoist = True)
        tcategory = discord.utils.get(guild.channels, name = text)
        vcategory = discord.utils.get(guild.channels, name = voice)
        
            #create text and voice channel
        vname = "Talk "+ name
        tchannel = await tcategory.create_text_channel(name.lower())
        vchannel = await vcategory.create_voice_channel(vname, user_limit = max_team)
    except:
        print("GROUP ERROR: Creating role, tchannel and vchannel")
        return

        
        #changing permissions to role and channel
    try:
        await tchannel.set_permissions(guild.default_role, view_channel = False)
        await tchannel.set_permissions(role, view_channel = True)
        await vchannel.set_permissions(guild.default_role, view_channel = False)
        await vchannel.set_permissions(role, view_channel = True)

            #give author role and change color
        await author.add_roles(role)
        await role.edit(name =name, colour = discord.Colour(random.randint(1000,16777215)))
    except:
        print("GROUP ERROR: Changing permissions for role and channels")
        return

    
        #add every data to database
    try:
        db.add_team(con, role.id, name, tchannel.id, vchannel.id)
        db.add_member(con, author.id, author.name, role.id)
    except:
        print("GROUP ERROR: Storing in Database failed")
        return

    global welcome
    if welcome:
        await tchannel.send(greeting)

    await ctx.send("Heeeeey @"+str(ctx.author)+"\n I created your group c:")
    con.close()
    print("GROUP SUCCESS\n")
    return

##########################################################################################
# bot add members to group

@bot.command(name="add", help = "!add @Mem1 @Mem2 @Mem3     Add Members to your team")
async def add(ctx, member1: discord.User = None, member2:discord.User = None, member3: discord.User = None, member4: discord.User = None):
    
    author = ctx.author
    guild = ctx.guild
    con = db.create_connection(database)

    try:
        team = db.fetch_members(con, author.id, "team")[0][0]
        role = discord.utils.get(guild.roles, id = team)
    except:
        print("ADD ERROR: could not fetch team or role")
        return

    nr = ""
        #give team members their role
    if member1 != None and len(db.fetch_members(con, member1.id, "team")) == 0:
        db.add_member(con, member1.id, member1.name, team)
        await member1.add_roles(role)
        nr += str(member1)
    if member2 != None and len(db.fetch_members(con, member2.id, "team")) == 0:
        await member2.add_roles(role)
        db.add_member(con, member2.id, member2.name, team)
        nr += ", "+ str(member2)
    if member3 != None and len(db.fetch_members(con, member3.id, "team")) == 0:
        await member3.add_roles(role)
        db.add_member(con, member3.id, member3.name, team)
        nr += ", " + str(member3)
    if member4 != None and len(db.fetch_members(con, member4.id, "team")) == 0:
        await member4.add_roles(role)
        db.add_member(con, member4.id, member4.name, team)
        nr += ", " + str(member4)

    await ctx.send("Added " + nr + " to " + str(role))
    con.close()
    print("ADD SUCCESS \n")
    return


##########################################################################################


#@bot.command(name =show_members)
#async def show_members(ctx):
#TODO


#@bot.command(name =change_name)
#async def change_name(ctx):
#TODO


#@bot.command(name='leave', help = "!leave"             You leave your current team)
#async def leave(ctx):
#TODO


#@bot.command(name = "up", help = "!up @Role points                 Add points to team @Role")
#async def update_points(ctx, group:discord.Role, punkte):
#TODO


#@bot.command(name =ranking)
#async def ranking(ctx):
#TODO


#@bot.command(name = "status", help ="!status @Role                    See points for team @Role")
#async def update_points(ctx, role:discord.Role):
#TODO


#@bot.command(name = "fs", help = "!fs      Fetch all messages in tchannel")
#async def fetch_solutions(ctx):
#TODO


#@bot.command(name = "control", help = "!control       Creates HTTPS Server to correct submissions")
#async def control(ctx):
#TODO

############################################################################################
# bot reset quiz


@bot.command(name="reset", help="!reset                           Resets Quizserver")
async def reset(ctx):
    
    if not ctx.author.top_role.permissions.administrator:
        await("Not enough power :/")
        return
    
    guild = ctx.guild
    author = ctx.author
    
    if os.path.isfile(database):
        remove(database)

            #delete text channels
    categ = discord.utils.get(guild.channels, name = text)
    for i in categ.channels:
        await i.delete()

        #delete voice channels
    categ = discord.utils.get(guild.channels, name = voice)
    for i in categ.channels:
        await i.delete()

        #delete roles
    for i in guild.roles[1:-safe_roles]:
        await i.delete()

    print("RESET SUCCESS \n")

    await init(ctx)
    return


bot.run(token)










