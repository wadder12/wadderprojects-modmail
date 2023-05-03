import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv
from pretty_help import PrettyHelp
from loguru import logger

ending_note = "For additional assistance, contact a moderator."
color = 0x00FF00

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')


intents = nextcord.Intents.all()
intents.guild_messages = True
bot = commands.Bot(command_prefix='!', intents=nextcord.Intents.all(),help_command=PrettyHelp())


logger.add("logs/file.log", level="TRACE")


@bot.event
async def on_ready():
    print(f'{bot.user.name} is online.')
    logger.info("Wadder ModMail is online.")


@bot.event
async def on_message(message):
    # Log the message
    logger.info(f"{message.author}: {message.content}")

    # Process the message as usual
    await bot.process_commands(message)


if __name__ == '__main__':
    bot.load_extension('cogs.waddermodmail')  # Assuming the ModMail cog is in a file named "modmail.py"
    bot.run(TOKEN)

