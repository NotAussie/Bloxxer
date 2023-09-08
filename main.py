# Imports
import guilded
from guilded.ext import commands
import roblox
import motor
import pymongo
import toml
import os
import asyncio
import itertools
import string
import random
import traceback
import datetime


# Pull config
config = toml.load("./config.toml")

# Initialize the bot
bot = commands.Bot(
    command_prefix=config["guilded"]["settings"]["prefix"],
    experimental_event_style=True,
    help_command=None,
)

# Variables
commands_ran = 0


# Cog loader
def load_cogs():
    """Tries to load all cogs in the './cogs' folder."""

    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            try:
                bot.load_extension(f"cogs.{file.removesuffix('.py')}")
            except Exception as error:
                print(f"Error loading:\n- cogs/{file}\nError:\n- {error}")
            else:
                print(f"Loaded cogs/{file}")


@bot.event
async def on_command_completion(ctx: commands.Context):
    """Called when a command is successfully executed."""

    # Bump the command counter by one
    global commands_ran
    commands_ran += 1


# On ready
@bot.event
async def on_ready():
    """Called when the bot starts."""

    # Get the authenticated Roblox user
    client = roblox.Client(token=config["roblox"]["settings"]["token"])
    user = await client.get_authenticated_user()

    # Print the current Roblox and Guilded user information
    print(f"Logged in as {bot.user.name} ({bot.user.id}) [GUILDED]")
    print(f"Logged in as {user.name} ({user.id}) [ROBLOX]")

    # Spacer
    print("⩶⩶⩶⩶>")

    # Print package versions
    print(f"Guilded version: {guilded.__version__}")
    print(f"Roblox version: {roblox.__version__}")
    print(f"Motor version: {motor.version}")
    print(f"PyMongo version: {pymongo.__version__}")

    # Spacer
    print("⩶⩶⩶⩶>")

    # Load the cogs
    load_cogs()
    print("⩶⩶⩶⩶>")  # End spacer

    # Pull the presence data from the config
    statuses = itertools.cycle(config["guilded"]["settings"]["presence"]["statuses"])
    emotes = itertools.cycle(config["guilded"]["settings"]["presence"]["emotes"])

    # Status loop
    while True:
        try:
            # Get the next status and emote
            cached_status = next(statuses)
            cached_emote = next(emotes)

            # Replace placeholders
            cached_status = cached_status.replace("{servers}", str(len(bot.servers)))
            cached_status = cached_status.replace("{users}", str(len(bot.users)))
            cached_status = cached_status.replace("{commands-ran}", str(commands_ran))
            cached_status = cached_status.replace("{prefix}", str(bot.command_prefix))
            cached_status = cached_status.replace(
                "{support-server}",
                str(config["guilded"]["settings"]["support-server"]).removeprefix(
                    "https://guilded"
                ),
            )

            # Set the status
            await bot.set_status(emote=cached_emote, content=cached_status)
        except TypeError:
            pass
        await asyncio.sleep(10)

# On command error
@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    # Generate a error id
    error_id = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(6)
    )

    # Create a error file
    with open(f"./errors/{error_id}.txt", "w+") as error_file:
        error_file.write(str(f"User: {ctx.author.id} | Time: {datetime.datetime.utcnow().strftime('%d/%m/%Y : %H:%M:%S')} | Server count: {len(bot.servers)} | User count: {len(bot.users)}\n" + error.__str__()))

    # Send the error message
    await ctx.reply(
        embed=guilded.Embed(
            title="🛑 Error",
            description=f"I've ran into an error! If this continues report it in the support server with the error id `{error_id}`.",
            color=guilded.Colour.dark_theme_embed(),
        )
    )

# Run the bot
bot.run(config["guilded"]["settings"]["token"])
