# TachyonsHackingBot
A bot designed for the fan game Tachyons (https://spektor.itch.io/tachyon), for practice on hacking on their Discord server. Based on Mastermind/Bulls and Cows.

Requires the ability to read and send messages.

https://discord.com/api/oauth2/authorize?client_id=795471473295753216&permissions=68672&scope=bot

Commands:
- !hack: starts a new game
optional: number of turns between 4 and 12
- !quit: quits current game
- !help: displays help message

Must pip install discord before modifying the code. The code requires a .env file placed in the same directory, with a line for DISCORD_TOKEN, taken from Discord's bot creation page.
