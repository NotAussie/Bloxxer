# Cog
import guilded
from guilded.ext import commands
import json

# TODO: Fix this error
# Ignoring exception in command help:
# Traceback (most recent call last):
#   File "C:\Users\Ethan\Bloxxer\cogs\help.py", line 62, in help
#     metadata = await self.get_command_metadata(command_object)
# TypeError: object NoneType can't be used in 'await' expression
#
# During handling of the above exception, another exception occurred:
#
# Traceback (most recent call last):
#   File "C:\Users\Ethan\Bloxxer\venv\lib\site-packages\guilded\ext\commands\core.py", line 112, in wrapped
#     ret = await coro(*args, **kwargs)
#   File "C:\Users\Ethan\Bloxxer\cogs\help.py", line 67, in help
#     await ctx.send(f"An error occurred while trying to get the help embed for that command.\n```{error}```")
#   File "C:\Users\Ethan\Bloxxer\venv\lib\site-packages\guilded\abc.py", line 184, in send
#     data = await self._state.create_channel_message(
#   File "C:\Users\Ethan\Bloxxer\venv\lib\site-packages\guilded\http.py", line 559, in request
#     raise GuildedServerError(response, data)
# guilded.errors.GuildedServerError: 500 (InternalServerError): An unexpected error occured
#
# The above exception was the direct cause of the following exception:
#
# Traceback (most recent call last):
#   File "C:\Users\Ethan\Bloxxer\venv\lib\site-packages\guilded\ext\commands\bot.py", line 515, in invoke
#     await ctx.command.invoke(ctx)
#   File "C:\Users\Ethan\Bloxxer\venv\lib\site-packages\guilded\ext\commands\core.py", line 666, in invoke
#     await injected(*ctx.args, **ctx.kwargs)
#   File "C:\Users\Ethan\Bloxxer\venv\lib\site-packages\guilded\ext\commands\core.py", line 121, in wrapped
#     raise CommandInvokeError(exc) from exc
# guilded.ext.commands.errors.CommandInvokeError: Command raised an exception: GuildedServerError: 500 (InternalServerError): An unexpected error occured


# Custom help command
class HELP(commands.Cog):
    def __init__(self, bot):
        """Custom help command."""
        self.bot: commands.Bot = bot
        self.help_embed: guilded.Embed = guilded.Embed(
            title="📃 Help",
            description="Use `help <command>` to get more information about a command.",
            color=guilded.Colour.dark_theme_embed(),
        )
        self.command_data = json.load(open("commands.json", "r"))

    # Get command metadata
    def get_command_metadata(self, command: commands.Command):
        """Gets the command metadata from the commands.json file."""

        try:
            data = self.command_data[command.name]
        except KeyError:
            return None
        else:
            return data

    # Build the help embed
    async def construct_command_info(self, command: commands.Command, data: dict):
        """Constructs the help embed for a command."""
        embed = guilded.Embed(
            title=f"📃 Help for {command.name}",
            description=f"`{command.description}`",
            color=guilded.Colour.dark_theme_embed(),
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        # Add the command's usage and aliases to the embed (if it exists)
        if data is not None:
            embed.add_field(
                name="📕 Usage",
                value=f"`{command.name} " + data["usage"] + "`",
                inline=False,
            )
            embed.add_field(
                name="📃 Aliases", value=f"`{', '.join(command.aliases)}`", inline=False
            )
        else:
            embed.add_field(
                name="🛑 Error", value=f"`Unable to load metadata`", inline=False
            )

        return embed

    # Help command
    @commands.command(aliases=["h"], description="Shows the help message.")
    async def help(self, ctx: commands.Context, command: str = None):
        """Shows the help message."""

        # If no command is specified, send the help embed
        if command is None:
            embed = self.help_embed

            embed.add_field(
                name="💖 Verification",
                value="```verify <username>\nsetverifyrole <role/role-id>\nsetverifychannel <channel/channel-id>```",
                inline=False,
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            await ctx.reply(embed=embed)

        # If a command is specified, try to get the command's help embed
        else:
            try:
                command_object = self.bot.get_command(command)
                metadata = self.get_command_metadata(command_object)
                await ctx.reply(
                    embed=await self.construct_command_info(command_object, metadata)
                )
            except Exception as error:
                print(
                    f"An error occurred while trying to get the help embed for that command.\n```{error}```"
                )


# Setup function
def setup(bot):
    bot.add_cog(HELP(bot))
