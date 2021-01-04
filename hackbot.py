# bot.py
import os
import discord
import string
import random
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')
answer = ""
gameStarted = False
guesses = 6
@bot.command(name='hack')
async def start_hack(ctx):
    #start hacking
    global gameStarted
    if not gameStarted:
        global answer
        global guesses
        char_list = string.ascii_letters + string.digits
        char_list = char_list.replace("l", "")
        char_list = char_list.replace("I", "")
        array = random.sample(char_list, 6)
        answer = "".join(random.sample(array, 3))
        char_response = ""
        for item in array:
            char_response += item
        response = ("The available letters are: " + char_response)
        guesses = 6
        gameStarted = True
        await ctx.send(response)
    else:
        await ctx.send("A game is already in progress!")

@bot.command(name='quit')
async def quit(ctx):
    #quit, it's pretty obvious
    global gameStarted
    if not gameStarted:
        await ctx.send("No game is in progress!")
    else:
        await ctx.send("Game has been stopped. Answer was: " + answer)
        gameStarted = False

@bot.event
async def on_message(message):
    # retrieve message during hacking game
    global gameStarted
    global guesses
    if message.author != bot.user:
        if gameStarted and len(message.content) == 3:
            correct = ""
            if message.content == answer:
                await message.channel.send("Correct!")
                gameStarted = False
            else:
                guesses -= 1
                if guesses == 0:
                    await message.channel.send("You have run out of guesses. The answer was: " + answer)
                    return
                for i in range(3):
                    for j in range(3):
                        if message.content[i] == answer[j]:
                            if i == j:
                                correct += "!"
                            else:
                                correct += "?"
                correct = "".join(sorted(correct))
                await message.channel.send("Guesses left: " + str(guesses) + ", [" + correct + "]")
        await bot.process_commands(message)

bot.run(TOKEN)