#First try for creating a quizbot. Decided to rework the basics for a better, more sturdy version.


import os
import random
import shutil
from discord.ext import commands
import discord
from dotenv import load_dotenv

    #easy path delete
def remove(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))



    #loading Token
load_dotenv()
TOKEN = os.getenv("TOKEN")

    #cast to bot
bot =  commands.Bot(command_prefix="!")

#######################################################################
#parameters


team_characters = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ- "

safe_roles = 2
    #amount of roles that shouldn't be removed

text = "Antworten/Answers" 
    #set parent of new text channel, has to exist

voice = "Quizecke/Talk"
    #set parent of new voice channel, has to exist

ranking = "ranking"
    #path for ranking saves

storage = "speicher.txt"
    #store created teams; for correcting, has to exist

global welcome
welcome = True

intro_answers ="Heey, hier ist euer Antworten-Channel. Wenn ihr irgendwelche Fragen habt, stellt diese bitte im Allgemein Channel :) \n\n Heey, here is your answers channel. If you have any questions, please ask them in the Allgemein channel :)"

#######################################################################



@bot.command(name='add', help = "!add @Role @Mem1 @Mem2 @Mem3     Add Members to team @Role")
async def add(ctx,role: discord.Role, member1: discord.User = None, member2:discord.User = None, member3: discord.User = None, member4: discord.User = None):

    
        #check if author is admin
    if not ctx.author.top_role.permissions.administrator:

            #check if author has role
        if not role in ctx.author.roles:
            await ctx.send("Du bist leider nicht in diesem Team :/")
            return


    author = ctx.author
    guild = ctx.guild


        #give team members their role
    if member1 != None:
        await member1.add_roles(role)
    if member2 != None:
        await member2.add_roles(role)
    if member3 != None:
        await member3.add_roles(role)
    if member4 != None:
        await member4.add_roles(role)

    print("add Done")

@bot.command(name="welcome", help="!welcome")
async def welcome(ctx):
    global welcome 
    welcome = not welcome
    
    print("welcome Done")

@bot.command(name='group', help="!group <Name>                    Create team with NAME")
async def group(ctx, name):
     

        #check if author is admin or has less than 1 role (everyone is a role)
    if not ctx.author.top_role.permissions.administrator:
        if len(ctx.author.roles) > 1:
            return



        # get guild and author as well as team name
    name = ctx.message.content[7:]
    author = ctx.author
    guild = ctx.guild
    
    
    for i in name:
        if not i in team_characters:
            await ctx.send("Der Teamname enthält unzulässige Zeichen: "+i)
            return


        #open file for group names
    fd = open(storage, "a")
    fd.write(name+"\n")


        #checks
    if discord.utils.get(guild.roles, name = name):
        ctx.send("So sorry to say, but this goup name already exists :/")
    #TODO
   

        #create text and voice channel for groups in category
    tcategory = discord.utils.get(guild.channels, name = text)
    vcategory = discord.utils.get(guild.channels, name = voice)
    vname = "Talk "+name
    await tcategory.create_text_channel(name.lower())
    await vcategory.create_voice_channel(vname, user_limit = 4)

        #get ID of text and voice channel
    tchannel = discord.utils.get(guild.text_channels, name=name.lower().replace(" ","-"))
    vchannel = discord.utils.get(guild.voice_channels, name=vname)
    
        #create role and adjust permissions of channels
    rolename = name.replace(" ", " ")
    await guild.create_role(name = rolename, mentionable = True, hoist = True)
    role = discord.utils.get(guild.roles, name = rolename)
    await tchannel.set_permissions(guild.default_role, view_channel = False)
    await tchannel.set_permissions(role, view_channel = True)
    await vchannel.set_permissions(guild.default_role, view_channel = False)
    await vchannel.set_permissions(role, view_channel = True)

        #give role to creator
    await author.add_roles(role)


        #give role a colour
    g = random.randint(1000,16777215)
    await role.edit(name=name, colour=discord.Colour(g))


        #create point table for group and create directory for it
    if not os.path.isdir('ranking'):
        os.mkdir(ranking)
    fd2 = open(os.path.join(os.path.join(os.getcwd(),ranking),name), "a")
    fd2.write(name +"\n")
    fd2.write("0\n")
    fd2.close()

    
        #write a Hello in text channel
    global welcome
    if welcome:
        await tchannel.send(intro_answers)


    await ctx.send("Heeeey @"+str(ctx.author) + "\n I created your group c:")
    fd.close()
    print("Gruppe erstellt")


    #change table for points
@bot.command(name = "up", help = "!up @Role points                 Add points to team @Role")
async def update_points(ctx, group:discord.Role, punkte):
    
        #check if author is admin
    if not ctx.author.top_role.permissions.administrator:
        await ctx.send("Du hast keine Admin-Reche :/")
        return


    name = group.name
    print(name)

    fd = open(os.path.join(os.path.join(os.getcwd(),ranking),name), "a")
    fd.write(punkte + "\n")
    fd.close()
    print("up Done")

    #call table for ranking
#@bot.command(name =ranking)
#async def ranking(ctx):
#TODO


    #call table of points for each teame
@bot.command(name = "status", help ="!status @Role                    See points for team @Role")
async def update_points(ctx, role:discord.Role):
    
        #check if author is admin
    if not ctx.author.top_role.permissions.administrator:

            #check if author has role
        if not role in ctx.author.roles:
            await ctx.send("Du bist leider nicht in diesem Team :/")
            return

    name = role.name

        #get points of team out of ranking file
    fd1 = open(os.path.join(os.path.join(os.getcwd(),"ranking"),name),"r")
    data = fd1.readlines()

        #write points of team
    send = "  [ TEAM ]   "+ name +"\n\n"
    pts = 0
    for i in range(1,len(data)):
        send += "[ Round "+str(i)+" ]:    " + data[i] 
        pts += int(data[i][:-1])
    send += "\n[ TOTAL POINTS ]:  "+str(pts)
    await ctx.send(send)
    print("status Done")

    #fetch all solutions for this round in file
@bot.command(name = "fs")
async def fetch_solutions(ctx):
    
        #check if author is admin
    if not ctx.author.top_role.permissions.administrator:
        await ctx.send("Du hast keine Admin-Reche :/")
        return

        #get category of textchannels
    guild = ctx.guild
    tcateg = discord.utils.get(guild.channels, name = text)
    
        #open every text channel and fetch messages in file solutions
        #clear team history afterwards = no messages left in channel
    fd = open("solutions","a")
    for i in tcateg.text_channels:
        fd.write("\n \n "+ i.name+"\n")
        msg = await i.history(limit=100).flatten()
        for k in msg[::-1]:
            fd.write(k.content+"\n")
            await k.delete()
    print("fs done")


    #get all members in quizroom movd
#@bot.commands(name ="qm")
#async def move_to_quiz(ctx):
#TODO


    #move all quiz participants into their talk channels
#@bot.commands(name="tm")
#async def move_to_talk(ctx):
#TODO


    #reset the quiz, all groups gone
@bot.command(name="reset", help="!reset                           Resets Quizserver")
#@commands.has_permissions(administrator)
async def reset(ctx):
     
        #check if author is admin
    if not ctx.author.top_role.permissions.administrator:
        await ctx.send("Du hast keine Admin-Reche :/")
        return

    guild = ctx.guild
    fd = open(storage, "r")
    names = fd.readlines()

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

        #move fragen to ehemalige Quizrunden
    #TODO

        #delete point table
    remove(os.path.join(os.getcwd(),ranking))

    fd.close()
    os.remove(storage)
    print("reset Done")

bot.run(TOKEN)



