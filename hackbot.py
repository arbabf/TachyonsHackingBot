# bot.py
import os
import discord
import string
import random
import sqlite3
from dotenv import load_dotenv
from discord.ext import commands
from keep_alive import keep_alive

conn = sqlite3.connect('bot.db')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS games(
   guildid TEXT,
   gamestatus INT,
   guesses INT,
   answer TEXT);
""")
conn.commit()

keep_alive()
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

#various getters/setters
def get_status(guildid):
    tup = c.execute("SELECT gamestatus FROM games WHERE guildid=?", (str(guildid),)).fetchone()
    # new guilds will return None so as not to crash
    if tup is None:
        return None
    return tup[0]

def update_status(guildid, new_status):
    c.execute("UPDATE games SET gamestatus=? WHERE guildid=?", (new_status, str(guildid),))
    conn.commit()

def get_answer(guildid):
    return c.execute("SELECT answer FROM games WHERE guildid=?", (str(guildid),)).fetchone()[0]

def update_answer(guildid, new_answer):
    c.execute("UPDATE games SET answer=? WHERE guildid=?", (new_answer, str(guildid),))
    conn.commit()

def get_guesses(guildid):
    return c.execute("SELECT guesses FROM games WHERE guildid=?", (str(guildid),)).fetchone()[0]

def update_guesses(guildid, new_guesses):
    c.execute("UPDATE games SET guesses=? WHERE guildid=?", (new_guesses, str(guildid),))
    conn.commit()

@bot.command(name='hack')
async def start_hack(ctx):
    guild = ctx.message.guild
    #start hacking
    if get_status(guild) is None:
        c.execute("INSERT INTO games VALUES (?, ?, ?, ?)", (str(guild), 0, 6, ""))
        conn.commit()
    if get_status(guild) == False:
        char_list = string.ascii_letters + string.digits
        #remove l, I since their discord equivalents look too much the same
        char_list = char_list.replace("l", "")
        char_list = char_list.replace("I", "")
        #get answer
        array = random.sample(char_list, 6)
        update_answer(guild, "".join(random.sample(array, 3)))
        char_response = ""
        for item in array:
            char_response += item
        response = ("The available letters are: " + char_response)
        update_guesses(guild, 6)
        update_status(guild, True)
        await ctx.send(response)
    else:
        await ctx.send("A game is already in progress!")

@bot.command(name='quit')
async def quit(ctx):
    #quit, it's pretty obvious
    guild = ctx.message.guild
    if get_status(guild) == False:
        await ctx.send("No game is in progress!")
    else:
        await ctx.send("Game has been stopped. Answer was: " + get_answer(guild))
        update_status(guild, False)

@bot.event
async def on_message(message):
    # retrieve message during hacking game
    guild = message.guild
    if message.author != bot.user:
        if get_status(guild) == True and len(message.content) == 3:
            correct = ""
            if message.content == get_answer(guild):
                await message.channel.send("Correct!")
                update_status(guild, False)
            else:
                update_guesses(guild, get_guesses(guild) - 1)
                if get_guesses(guild) == 0:
                    await message.channel.send("You have run out of guesses. The answer was: " + get_answer(guild))
                    update_status(guild, False)
                    return
                for i in range(3):
                    for j in range(3):
                        if message.content[i] == get_answer(guild)[j]:
                            if i == j:
                                correct += "!"
                            else:
                                correct += "?"
                correct = ("".join(sorted(correct)))[::-1] # reverse this string to fit with tachyons notation
                await message.channel.send("Guesses left: " + str(get_guesses(guild)) + ", [" + correct + "]")
        await bot.process_commands(message)

bot.remove_command("help")

@bot.command(name='help')
async def help(ctx):
    await ctx.send("```\nGuess the correct 3-character answer from the provided 6 characters to win. Similar to Mastermind/Bulls and Cows.\n - !hack: start a new game\n - !quit: quits current game\n - !help: displays this message\n```")

bot.run(TOKEN)