import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv
from pretty_help import PrettyHelp
from loguru import logger

# this is for pretty help #

ending_note = "For additional assistance, contact a moderator."
color = 0x00FF00



# the bots intents #
intents = nextcord.Intents.all()
intents.guild_messages = True
bot = commands.Bot(command_prefix='!', intents=nextcord.Intents.all(),help_command=PrettyHelp())

# this is for the logger #
logger.add("logs/file.log", level="TRACE")

# this is the on ready event #
@bot.event
async def on_ready():
    print(f'{bot.user.name} is online.')
    logger.info("Wadder ModMail is online.")

# this is the on message event #
@bot.event
async def on_message(message):
    # Log the message
    logger.info(f"{message.author}: {message.content}")

    # Process the message as usual
    await bot.process_commands(message)

# this is the start of the modmail bot #
if __name__ == '__main__':
    bot.load_extension('cogs.waddermodmail') 
    bot.run('MTA3NTE0NDgyODMzMDk3MTE4Ng.GoO7_2.KmJKfemVuGhl0yon9OT73Z-15ZNg_YC-qcmJu0')

