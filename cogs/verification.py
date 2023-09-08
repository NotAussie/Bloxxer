import guilded
from guilded.ext import commands
import toml
import Bloxed
import roblox


class VERIFICATION(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.dbclient: Bloxed.Client = Bloxed.Client(toml.load("config.toml"))
        self.roblox: roblox.Client = roblox.Client(toml.load("config.toml")["roblox"]["settings"]["token"])
        self.apiclient: Bloxed.APIClient = Bloxed.APIClient(toml.load("config.toml")["guilded"]["settings"]["token"])

    @commands.Cog.listener()
    async def on_member_join(self, event: guilded.MemberJoinEvent):
        # Get the server's data
        data = await self.dbclient.getch_guild(event.server.id)

        # Check if verification is enabled
        if data["settings"]["verification"]["enabled"]:
            # Check if a verification channel is set
            if data["settings"]["verification"]["channel"] is not None:
                # Get the channel
                channel = await self.bot.getch_channel(
                    data["settings"]["verification"]["channel"]
                )

                # Send the verification message
                embed = guilded.Embed(
                    title="🔒 Verification",
                    description=f"Please verify by running `{self.bot.command_prefix}verify` command.",
                    colour=guilded.Colour.dark_theme_embed(),
                )
                embed.add_field(
                    name="👤 Mention", value=f"{event.member.mention}", inline=False
                )
                embed.set_footer(text=f"🤖 This is an automated message.")
                await channel.send(embed=embed, private=True)

    # Set channel command
    @commands.command(description="Sets the verification channel.")
    async def setverifychannel(self, ctx: commands.Context, channel: str):
        # Check if the user has manage channel permissions
        if not ctx.author.server_permissions.manage_channels:
            # Send an error message
            embed = guilded.Embed(
                title="🛑 Error",
                description="You don't have the `Manage Channels` permission.",
                colour=guilded.Colour.dark_theme_embed(),
            )
            await ctx.reply(embed=embed)
            return

        try:
            # Check a channel was mentioned
            dummy = ctx.message.channel_mentions[0]
        except IndexError:
            try:
                # Try to get the channel
                ch = await ctx.server.getch_channel(channel)
            except guilded.NotFound:
                # Send an error message
                embed = guilded.Embed(
                    title="🛑 Error",
                    description=f"Channel `{channel}` not found.",
                    colour=guilded.Colour.dark_theme_embed(),
                )
                await ctx.reply(embed=embed)
            except guilded.InvalidData:
                # Send an error message
                embed = guilded.Embed(
                    title="🛑 Error",
                    description=f"Channel `{channel}` is not from this server.",
                    colour=guilded.Colour.dark_theme_embed(),
                )
                await ctx.reply(embed=embed)
            else:
                # Get the server's data
                data = await self.dbclient.fetch_guild(ctx.guild.id)

                # Set the channel
                data["settings"]["verification"]["channel"] = ch.id
                await self.dbclient.update_guild(guild_id=ctx.guild.id, data=data)

                # Send a success message
                embed = guilded.Embed(
                    title="✅ Success",
                    description=f"Successfully set the verification channel to `{ch.name}`.",
                    colour=guilded.Colour.dark_theme_embed(),
                )
                await ctx.reply(embed=embed)

        else:
            # Get the channel
            channel = ctx.message.channel_mentions[0]

            # Get the server's data
            data = await self.dbclient.fetch_guild(ctx.guild.id)

            # Set the channel
            data["settings"]["verification"]["channel"] = channel.id
            await self.dbclient.update_guild(guild_id=ctx.guild.id, data=data)

            # Send a success message
            embed = guilded.Embed(
                title="✅ Success",
                description=f"Successfully set the verification channel to `{channel.name}`.",
                colour=guilded.Colour.dark_theme_embed(),
            )
            await ctx.reply(embed=embed)

    # Enable/disable command
    @commands.command(description="Enables/disables verification.")
    async def toggleverification(self, ctx: commands.Context, enabled: bool):
        # Check if the user has manage server permissions
        if not ctx.author.server_permissions.manage_server:
            # Send an error message
            embed = guilded.Embed(
                title="🛑 Error",
                description="You don't have the `Manage Server` permission.",
                colour=guilded.Colour.dark_theme_embed(),
            )
            await ctx.reply(embed=embed)
            return

        # Get the server's data
        data = await self.dbclient.fetch_guild(ctx.guild.id)

        # Set verification
        data["settings"]["verification"]["enabled"] = enabled
        await self.dbclient.update_guild(guild_id=ctx.guild.id, data=data)

        # Send a success message
        embed = guilded.Embed(
            title="✅ Success",
            description=f"Successfully {'enabled' if enabled else 'disabled'} verification.",
            colour=guilded.Colour.dark_theme_embed(),
        )
        await ctx.reply(embed=embed)

    # Set role command
    @commands.command(description="Sets the verification role.")
    async def setverifyrole(self, ctx: commands.Context, role: str):
        try:
            # Check a role was mentioned
            dummy = ctx.message.raw_role_mentions[0]
        except IndexError:
            # Check if a valid id role was given
            try:
                fetched_role = await ctx.guild.getch_role(int(role))
            except guilded.NotFound:
                # Send an error message
                embed = guilded.Embed(
                    title="🛑 Error",
                    description=f"Role `{role}` not found.",
                    colour=guilded.Colour.dark_theme_embed(),
                )
                await ctx.reply(embed=embed)
            except ValueError:
                # Send an error message
                embed = guilded.Embed(
                    title="🛑 Error",
                    description=f"Role `{role}` is invalid.",
                    colour=guilded.Colour.dark_theme_embed(),
                )
                await ctx.reply(embed=embed)
        else:
            # Get the role
            role = await ctx.guild.getch_role(ctx.message.raw_role_mentions[0])

            # Get the server's data
            data = await self.dbclient.fetch_guild(ctx.guild.id)

            # Set the role
            data["settings"]["verification"]["role"] = role.id
            await self.dbclient.update_guild(guild_id=ctx.guild.id, data=data)

            # Send a success message
            embed = guilded.Embed(
                title="✅ Success",
                description=f"Successfully set the verification role to `{role.name}`.",
                colour=guilded.Colour.dark_theme_embed(),
            )
            await ctx.reply(embed=embed)

    # Verify command
    @commands.command(description="Verifies your Roblox account.")
    async def verify(self, ctx: commands.Context):
        # Try to get the user's Roblox account from the database
        try:
            data = await self.apiclient.getch_user(ctx.author.id, ctx.guild.id)
        except ValueError:
            # Send an error message
            embed = guilded.Embed(
                title="🛑 Error",
                description=f"You don't have a Roblox account linked, link one to your Guilded account then retry.",
                colour=guilded.Colour.dark_theme_embed(),
            )
            await ctx.reply(embed=embed)
        else:
            # Get the server's data
            server_data = await self.dbclient.fetch_guild(ctx.guild.id)

            # Check if verification is enabled
            if server_data["settings"]["verification"]["enabled"]:
                if ctx.channel.id == server_data["settings"]["verification"]["channel"]:
                    # Get the user's Roblox account
                    roblox_user = await self.roblox.get_user(data["id"])

                    # Check if the server has a role set
                    if server_data["settings"]["verification"]["role"] is not None:
                        # Get the server's role
                        role = await ctx.guild.getch_role(data["settings"]["verification"]["role"])

                        # Add the role to the user
                        await ctx.author.add_role(role)

                    # Send a success message
                    embed = guilded.Embed(
                        title="✅ Success",
                        description=f"Successfully verified you as `{roblox_user.name}`.",
                        colour=guilded.Colour.dark_theme_embed(),
                    )
                    await ctx.reply(embed=embed)
                else:
                    # Send an error message
                    ch = await self.bot.getch_channel(server_data["settings"]["verification"]["channel"])
                    embed = guilded.Embed(
                        title="🛑 Error",
                        description=f"Please run this command in the verification [channel]({ch.jump_url}.",
                        colour=guilded.Colour.dark_theme_embed(),
                    )
                    await ctx.reply(embed=embed)
            else:
                # Send an error message
                embed = guilded.Embed(
                    title="🛑 Error",
                    description=f"Verification is not enabled.",
                    colour=guilded.Colour.dark_theme_embed(),
                )
                await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(VERIFICATION(bot))
