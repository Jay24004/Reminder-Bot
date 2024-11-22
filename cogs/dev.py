import discord
from discord import app_commands
from discord.ext import commands
from typing import List


@app_commands.user_install()
@app_commands.allowed_installs(guilds=False, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
class Dev(commands.GroupCog, name="dev", description="Dev commands"):
    def __init__(self, bot):
        self.bot = bot

    async def cog_auto_complete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        _list = [
            app_commands.Choice(name=extention, value=extention)
            for extention in self.bot.extensions
            if current.lower() in extention.lower()
        ]
        return _list[:24]

    @staticmethod
    async def is_dev(interaction: discord.Interaction):
        if interaction.user.id in interaction.client.owner_ids:
            return True
        await interaction.response.send_message(
            embed=discord.Embed(
                description="You are not a developer",
                color=interaction.client.default_color,
            ),
            ephemeral=True,
        )
        return False

    @app_commands.command(name="reload", description="Reloads a cog")
    @app_commands.autocomplete(cog=cog_auto_complete)
    @app_commands.default_permissions(administrator=True)
    @app_commands.check(is_dev)
    async def reload(self, interaction: discord.Interaction, cog: str):
        await interaction.response.send_message(
            embed=discord.Embed(
                description=f"Reloading cog `{cog}`...",
                color=interaction.client.default_color,
            )
        )
        try:
            await self.bot.reload_extension(cog)
            await interaction.edit_original_response(
                embed=discord.Embed(
                    description=f"Successfully reloaded cog `{cog}`",
                    color=interaction.client.default_color,
                ),
            )
        except Exception as e:
            await interaction.edit_original_response(
                content=None,
                embed=discord.Embed(
                    description=f"Error while reloading cog `{cog}`: {e}",
                    color=interaction.client.default_color,
                ),
            )

    @app_commands.command(name="sync", description="Syncs a guild/gobal command")
    @app_commands.check(is_dev)
    async def sync(self, interaction: discord.Interaction, guild_id: str = None):
        if guild_id is None:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="Syncing global commands...",
                    color=interaction.client.default_color,
                )
            )
            await interaction.client.tree.sync()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    description="Successfully synced global commands",
                    color=interaction.client.default_color,
                )
            )
        else:
            if guild_id == "*":
                guild = interaction.guild
            else:
                guild = await interaction.client.fetch_guild(int(guild_id))
                if guild is None:
                    return await interaction.response.send_message(
                        embed=discord.Embed(
                            description="Invalid guild id",
                            color=interaction.client.default_color,
                        )
                    )
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"Syncing guild commands for `{guild.name}`...",
                    color=interaction.client.default_color,
                )
            )
            await interaction.client.tree.sync(guild=guild)
            await interaction.edit_original_response(
                embed=discord.Embed(
                    description=f"Successfully synced guild commands for `{guild.name}`",
                    color=interaction.client.default_color,
                )
            )


async def setup(bot):
    await bot.add_cog(Dev(bot))
