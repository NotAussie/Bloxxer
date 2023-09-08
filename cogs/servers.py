import guilded
import toml
from guilded.ext import commands
from datetime import datetime
import Bloxed


# now = datetime.now()
# formatted_time = now.strftime('%I:%M:%S %p')


class SERVERS(commands.Cog):
    def __init__(self, bot):
        """Server events cog."""
        self.bot: commands.Bot = bot
        self.config = toml.load("./config.toml")
        self.client = Bloxed.Client(toml.load("config.toml"))

    # On server added, create the server in the database and send a thank-you message
    @commands.Cog.listener()
    async def on_bot_add(self, event: guilded.BotAddEvent):
        """Called when the bot is added to a server."""

        # Get the server's default channel
        ch = await self.bot.getch_channel(event.server.default_channel_id)

        # Create the thank-you embed
        embed = guilded.Embed(
            title="👋 Thanks for adding me!",
            description="Thanks for adding Bloxxer, the easy and powerful Roblox connection bot.",
            color=guilded.Colour.dark_theme_embed(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(
            name="📕 Prefix",
            value=f"My prefix is `{self.bot.command_prefix}`.",
            inline=False,
        )
        embed.add_field(
            name="📃 Commands",
            value=f"Use `{self.bot.command_prefix}help` to see my commands.",
            inline=False,
        )
        embed.add_field(
            name="🤝 Support",
            value=f"My support server is .gg/[BloxxerBot]({self.config['guilded']['settings']['support-server']}).",
            inline=False,
        )
        embed.add_field(
            name="💖 Server number",
            value=f"You're number `{len(self.bot.servers)}`.",
            inline=False,
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=f"🤖 This is an automated message.")

        # Send the thank-you message
        try:
            await ch.send(embed=embed)
        except guilded.Forbidden:
            # Pass if the bot can't send a message
            pass

        # Default server data
        default_settings = {
            "guild_id": event.server.id,
            "settings": {
                "verification": {"role": None, "channel": None, "enabled": False}
            },
        }

        # Check if the server is already in the database
        try:
            await self.client.getch_guild(event.server.id)
        except ValueError:
            # Create the server in the database as it doesn't exist
            await self.client.create_guild(data=default_settings)
            return
        else:
            # If the server is already in the database, update the server's data to the default settings
            await self.client.update_guild(
                guild_id=event.server.id, data=default_settings
            )
            return


def setup(bot):
    bot.add_cog(SERVERS(bot))
