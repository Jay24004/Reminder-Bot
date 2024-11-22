import discord
import datetime
from discord.ext import commands, tasks
from discord import app_commands, Interaction
from utils.transformer import TimeConverter
from humanfriendly import format_timespan
from utils.converters import chunk
from utils.db import Document
from utils.paginator import Paginator


@app_commands.user_install()
@app_commands.allowed_installs(guilds=False, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
class Reminder(commands.GroupCog, name="reminder"):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = Document(bot.db, "reminders")
        self.bot.reminders = self.reminders
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.stop()

    async def generate_id(self, user: discord.User | discord.Member):
        return int(
            str(user.id)[:8]
            + str(discord.utils.utcnow().timestamp()).replace(".", "")[-4:]
        )

    @tasks.loop(seconds=10)
    async def check_reminders(self):
        reminders = await self.reminders.get_all()
        reminders_dms = {}
        for reminder in reminders:
            if reminder["time"] < datetime.datetime.utcnow():
                if reminder["user"] not in reminders_dms.keys():
                    reminders_dms[reminder["user"]] = []

                reminders_dms[reminder["user"]].append(reminder)

        for dms, reminder in reminders_dms.items():
            user = self.bot.get_user(dms)
            view = discord.ui.View()
            if not isinstance(user, discord.User):
                user = await self.bot.fetch_user(dms)

            embed = discord.Embed(title="Reminders", color=self.bot.default_color)
            for rem in reminder:
                embed.add_field(
                    name=f"Reminder ID: {rem['_id']}",
                    value=f"Message: {rem['message']}",
                    inline=False,
                )
                if len(view.children) < 20:
                    emoji = self.bot.link_emoji if self.bot.link_emoji else "🔗"
                    view.add_item(
                        discord.ui.Button(
                            style=discord.ButtonStyle.url,
                            label=f"Rem. ID: {rem['_id']}",
                            url=rem["url"],
                            emoji=emoji,
                        )
                    )
            try:
                await user.send(embed=embed, view=view)
            except discord.Forbidden:
                pass

            for rem in reminder:
                await self.reminders.delete(rem)

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="set", description="Set a reminder")
    @app_commands.describe(
        time="The time in seconds to set the reminder",
        message="The message to be sent when the reminder is triggered",
    )
    async def set_reminder(
        self,
        interaction: Interaction,
        time: app_commands.Transform[int, TimeConverter],
        message: str,
    ):
        try:
            reminder_id = await self.generate_id(interaction.user)
            data = {
                "_id": reminder_id,
                "time": datetime.datetime.utcnow() + datetime.timedelta(seconds=time),
                "message": message,
                "user": interaction.user.id,
                "url": None,
            }
            await self.reminders.insert(data=data)
        except Exception as e:
            return await interaction.response.send_message(
                f"An error occured: {e}", ephemeral=True
            )

        await interaction.response.send_message(
            f"Okay I have added a reminder with ID `{reminder_id}` which will trigger in {format_timespan(time)}",
            ephemeral=False,
        )
        msg = await interaction.original_response()
        data["url"] = msg.jump_url
        await self.reminders.update(data)

    @app_commands.command(name="list", description="List all reminders")
    async def list_reminders(self, interaction: Interaction):
        reminders = await self.reminders.find_many_by_custom(
            {"user": interaction.user.id}
        )
        if not reminders:
            return await interaction.response.send_message(
                "You have no reminders set", ephemeral=True
            )

        reminders = sorted(reminders, key=lambda x: x["time"])
        chunked = chunk(reminders, 5)
        i = 1
        pages = []
        for chunks in chunked:
            embed = discord.Embed(
                title="Reminders", color=self.bot.default_color, description=""
            )
            for reminder in chunks:
                time = reminder["time"]
                timestamp = int(time.timestamp())
                embed.description += f"{i}: {reminder['message']}\n> <t:{timestamp}:R> (<t:{timestamp}:f>) \n"
                i += 1
                pages.append(embed)

        await Paginator(interaction=interaction, pages=pages).start(
            embeded=True, timeout=30, quick_navigation=False, hidden=True
        )

    @app_commands.command(name="delete", description="Delete a reminder")
    @app_commands.describe(reminder_id="The reminder to delete")
    async def delete_reminder(self, interaction: Interaction, reminder_id: int):
        reminder = await self.reminders.find_one_by_custom(
            {"id": reminder_id, "user": interaction.user.id}
        )
        if not reminder:
            return await interaction.response.send_message(
                "Reminder not found", ephemeral=True
            )

        await self.reminders.delete(reminder)
        await interaction.response.send_message(
            "Reminder has been deleted", ephemeral=True
        )

    @app_commands.command(name="clear", description="Clear all reminders")
    async def clear_reminders(self, interaction: Interaction):
        reminders = await self.reminders.find_many_by_custom(
            {"user": interaction.user.id}
        )
        if not reminders:
            return await interaction.response.send_message(
                "You have no reminders set", ephemeral=True
            )

        await self.reminders.delete_many(reminders)
        await interaction.response.send_message(
            "All reminders have been deleted", ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Reminder(bot))
