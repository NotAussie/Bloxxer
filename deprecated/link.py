raise DeprecationWarning

# import guilded
# import toml
# from guilded.ext import commands
# import Bloxed
# import roblox
#
#
# class LINK(commands.Cog):
#     def __init__(self, bot):
#         config = toml.load("config.toml")
#         self.bot: commands.Bot = bot
#         self.client = Bloxed.APIClient(config["guilded"]["settings"]["token"])
#         self.dataclient = Bloxed.Client(toml.load("config.toml"))
#         self.roblox = roblox.Client(token=config["roblox"]["settings"]["token"])
#
#     # Link command
#     @commands.command(
#         aliases=["connect", "relate"],
#         description="Links your Roblox account to your Guilded account.",
#     )
#     async def link(self, ctx: commands.Context):
#         # Send a loading message
#         loading_embed = guilded.Embed(
#             title="🔗 Linking your account...",
#             description="This could take a few seconds.",
#             colour=guilded.Colour.dark_theme_embed(),
#         )
#         msg = await ctx.reply(embed=loading_embed)
#
#         # Try to get the user's Roblox account
#         try:
#             data = await self.client.getch_user(ctx.author.id, ctx.guild.id)
#         except KeyError:
#             # If the user doesn't have a Roblox account linked, send an error message
#             error_embed = guilded.Embed(
#                 title="🛑 Error",
#                 description="You don't have a Roblox account linked, add one to your Guilded profile and try again. For a detailed guide, see [this](https://www.guilded.gg/bloxxerbot/groups/DvxMkpgz/channels/71c6a976-a240-4d7a-b984-fbb07a815f6a/docs/388319).",
#                 colour=guilded.Colour.dark_theme_embed(),
#             )
#             await msg.edit(embed=error_embed)
#             return
#         else:
#             # If the user has a Roblox account linked, send a success message
#             success_embed = guilded.Embed(
#                 title="✅ Success",
#                 description=f"Successfully linked you to `{data['username']}`.",
#                 colour=guilded.Colour.dark_theme_embed(),
#             )
#             await msg.edit(embed=success_embed)
#
#             # Check if the user is already in the database
#             try:
#                 fetched_data = await self.dataclient.fetch_user(ctx.author.id)
#             except ValueError:
#                 # If the user isn't in the database, add them
#                 await self.dataclient.create_user(
#                     data={
#                         "user_id": ctx.author.id,
#                         "roblox": {"username": data["username"], "id": data["id"]},
#                     }
#                 )
#                 return
#             else:
#                 # If the user is in the database, update their data
#                 fetched_data["roblox"]["username"] = data["username"]
#                 fetched_data["roblox"]["id"] = data["id"]
#                 await self.dataclient.update_user(
#                     user_id=ctx.author.id, data=fetched_data
#                 )
#         # Check if the user is already in the database
#         try:
#             fetched_data = await self.dataclient.getch_user(ctx.author.id)
#         except ValueError:
#             # If the user isn't in the database, add them
#             await self.dataclient.create_user(
#                 data={
#                     "user_id": ctx.author.id,
#                     "roblox": {"username": "none", "id": None},
#                 }
#             )
#             return
#         else:
#             # If the user is in the database, update their data
#             fetched_data["roblox"]["username"] = data["username"]
#             fetched_data["roblox"]["id"] = data["id"]
#             await self.dataclient.update_user(
#                 user_id=ctx.author.id, data=fetched_data
#             )
#
#
# def setup(bot):
#     bot.add_cog(LINK(bot))
