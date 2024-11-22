import discord
from discord import app_commands
import re

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, argument: str) -> int:
        matches = time_regex.findall(argument.lower())
        if len(matches) == 0:
            try:
                return int(argument)
            except Exception as e:
                raise e
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                raise KeyError
            except ValueError:
                raise ValueError
        return time
