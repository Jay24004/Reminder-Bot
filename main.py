import logging
import os
import asyncio
import logging.handlers
from motor.motor_asyncio import AsyncIOMotorClient
from humanfriendly import format_timespan
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord import app_commands

load_dotenv()

discord.utils.setup_logging(
    handler=logging.handlers.RotatingFileHandler(
        filename="bot.log", maxBytes=1000000, backupCount=5, encoding="utf-8"
    ),
    formatter=logging.Formatter(
        "%(asctime)s:%(levelname)s:%(name)s: %(message)s", "%d-%m-%Y %H:%M:%S"
    ),
    root=True,
)

intesnts = discord.Intents.default()


class Botbase(commands.Bot):
    def __init__(self, application_id, sync: bool = True):
        super().__init__(
            intents=intesnts,
            command_prefix=".",
            case_insensitive=False,
            owner_ids=[int(i) for i in os.environ.get("OWNER_IDS").split(",")],
            activity=discord.Activity(type=discord.ActivityType.custom, name="Startup"),
            status=discord.Status.idle,
            help_command=None,
            application_id=application_id,
        )
        self.default_color = 0x2B2D31
        self.connection_url = os.environ.get("MONGO")
        self.mongo = AsyncIOMotorClient(self.connection_url)
        self.db = self.mongo["Database"]
        self.link_emoji = os.environ.get("LINK_EMOJI")

    async def setup_hook(self):
        for file in os.listdir("cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                await self.load_extension(f"cogs.{file[:-3]}")


bot = Botbase(os.environ.get("APP_ID"), False)


async def main():
    await bot.start(
        os.environ.get("TOKEN"),
    )


@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user.name} | {bot.user.id}")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name="reminders"
        ),
        status=discord.Status.online,
    )
    await bot.tree.sync()
    for guild in bot.guilds:
        await bot.tree.sync(guild=guild)


@bot.tree.command(name="ping", description="Check bots latency")
async def ping(interaction):
    await interaction.response.send_message("Pong!")
    await interaction.edit_original_response(
        content=None,
        embed=discord.Embed(description=f"Ping {bot.latency * 1000.0:.2f}ms"),
    )


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: Exception):
    if isinstance(error, app_commands.errors.CommandOnCooldown):
        return await interaction.response.send_message(
            f"Command on cooldown, try again in {format_timespan(error.retry_after)}",
            ephemeral=True,
        )
    elif isinstance(error, app_commands.errors.CommandNotFound):
        return await interaction.response.send_message(
            "Command not found", ephemeral=True
        )
    elif isinstance(error, app_commands.errors.NoPrivateMessage):
        return await interaction.response.send_message(
            "Command not available in DMs", ephemeral=True
        )
    elif isinstance(error, app_commands.errors.MissingPermissions):
        return await interaction.response.send_message(
            "You are missing permissions", ephemeral=True
        )
    elif isinstance(error, app_commands.errors.TransformerError):
        return await interaction.response.send_message(
            "An error occurred while processing your input", ephemeral=True
        )
    else:
        raise error


asyncio.run(main())
