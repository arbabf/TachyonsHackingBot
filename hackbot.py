# bot.py
import os
import string
import random
import sqlite3
import time
import math
from dotenv import load_dotenv
from discord.ext import commands
from keep_alive import keep_alive

conn = sqlite3.connect('bot.db')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS games(
   guildid TEXT,
   gamestatus INT,
   guesses INT,
   answer TEXT,
   charset TEXT,
   starttime INT);
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

def get_charset(guildid):
    return c.execute("SELECT charset FROM games WHERE guildid=?", (str(guildid),)).fetchone()[0]

def update_charset(guildid, new_charset):
    c.execute("UPDATE games SET charset=? WHERE guildid=?", (new_charset, str(guildid),))
    conn.commit()

def get_starttime(guildid):
    return c.execute("SELECT starttime FROM games WHERE guildid=?", (str(guildid),)).fetchone()[0]

def update_starttime(guildid, new_starttime):
    c.execute("UPDATE games SET starttime=? WHERE guildid=?", (new_starttime, str(guildid),))
    conn.commit()


@bot.command(name='hack')
async def start_hack(ctx, *args):
    """
    Initiates a hacking game.
    Input: variable set of arguments.
    """
    guild = ctx.message.guild
    arg_attempt = 6
    # parse args (or just the one arg, anyway)
    if (len(args) > 0):
        try:
            arg_attempt = int(args[0])
            if arg_attempt < 4 or arg_attempt > 12:
                raise ValueError
        except:
            await ctx.send("Number of turns must be a number between 4 and 12.")
            return
    # start the hacking process
    if get_status(guild) is None:
        c.execute("INSERT INTO games VALUES (?, ?, ?, ?, ?, ?)", (str(guild), 0, arg_attempt, "", "", 0))
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
        update_guesses(guild, arg_attempt)
        for item in array:
            char_response = "".join([char_response, item])
        response = ("The available letters are: {0}\nYou have {1} guesses.").format(char_response, str(get_guesses(guild)))
        update_charset(guild, char_response)
        update_status(guild, True)
        update_starttime(guild, time.perf_counter())
        await ctx.send(response)
    else:
        await ctx.send("A game is already in progress!")

@bot.command(name='quit')
async def quit(ctx):
    """
    Quits the current game.
    """
    guild = ctx.message.guild
    if get_status(guild) == False:
        await ctx.send("No game is in progress!")
    else:
        await ctx.send("Game has been stopped. Answer was: {0}".format(get_answer(guild)))
        update_status(guild, False)

@bot.event
async def on_message(message):
    """
    Process the given message, check if it is three characters long, and compare it against the answer.
    """
    guild = message.guild
    if message.author != bot.user:
        if get_status(guild) == True and len(message.content) == 3:
            correct = ""
            if message.content == get_answer(guild):
                diff = time.perf_counter() - get_starttime(guild)
                min = math.floor(diff/60)
                sec = diff % 60
                await message.channel.send("Correct!\nTime taken: {}:{:0>2d}".format(str(min), int(sec)))
                update_status(guild, False)
            else:
                charset = get_charset(guild)
                for i in range(3):
                    char = message.content[i]
                    if charset.find(char) != -1:
                        for j in range(3):
                            if message.content[i] == get_answer(guild)[j]:
                                if i == j:
                                    correct = "".join([correct, "!"])
                                else:
                                    correct = "".join([correct, "?"])
                    else:
                        await message.channel.send("One or more of the characters is not part of the given character set.")
                        return
                update_guesses(guild, get_guesses(guild) - 1)
                if get_guesses(guild) == 0:
                    await message.channel.send("You have run out of guesses. The answer was: {0}".format(get_answer(guild)))
                    update_status(guild, False)
                    return
                correct = ("".join(sorted(correct)))[::-1] # reverse this string to fit with tachyons notation
                await message.channel.send("**[{0}]**\nGuesses left: {1}".format(correct, str(get_guesses(guild))))
        await bot.process_commands(message)

bot.remove_command("help")

@bot.command(name='help')
async def help(ctx):
    await ctx.send("""```Guess the correct 3-character answer from the provided 6 characters to win. Similar to Mastermind/Bulls and Cows.
- !hack: start a new game   
    - optional: number of turns, from 4 to 12
- !quit: quits current game
- !help: displays this message
'?' - right character, wrong place
'!' - right character, right place```""")
bot.run(TOKEN)