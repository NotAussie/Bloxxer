from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
import aiohttp
from cachetools import TTLCache


class APIClient:
    def __init__(self, token: str):
        self.token = token
        self.cache = TTLCache(maxsize=1000, ttl=300)

    # Get user
    async def fetch_user(self, user_id: str, server_id: str):
        # Get the user's roblox from the Guilded api (Requires authentication)
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            async with session.get(
                    f"https://www.guilded.gg/api/v1/servers/{server_id}/members/{user_id}/social-links/roblox",
                    headers=headers,
            ) as response:
                data = await response.json()
                # print(data)
                # exit()

                try:
                    dummy = data["NotFoundError"]

                except KeyError:
                    try:
                        username = data["socialLink"]["handle"]
                        uid = data["socialLink"]["serviceId"]
                    except KeyError:
                        raise ValueError("Internal error: Invalid response from Guilded API")
                    return_data = {
                        "username": username,
                        "id": uid,
                    }
                    return return_data
                else:
                    raise ValueError("User not found.")

    # Getch user
    async def getch_user(self, user_id: str, server_id: str):
        """Gets a users from cache or if not cached, gets from the api"""

        # Check if the guild is in the cache
        if user_id in self.cache:
            return self.cache[user_id]

        # Fetch the guild from the api
        try:
            user = await self.fetch_user(user_id, server_id)
        except ValueError:
            raise ValueError("User not found.")

        # Cache the guild and return it
        self.cache[user_id] = user
        return user


class Client:
    def __init__(self, config: dict):
        self.client = AsyncIOMotorClient(config["mongodb"]["settings"]["uri"])
        self.db = self.client[config["mongodb"]["settings"]["database"]]
        self.guilds = self.db["guilds"]
        self.users = self.db["users"]
        self.premium = self.db["products"]
        self.cache = TTLCache(maxsize=1000, ttl=60)

    # Fetch server
    async def fetch_guild(self, guild_id: str):
        """Fetches a guild from the database."""

        # Fetch the guild
        guild = await self.guilds.find_one({"guild_id": guild_id})

        # If the guild is not in the database, return an error
        if not guild:
            raise ValueError("Guild not found in database.")

        # Return the guild
        return guild

    # Get server
    async def getch_guild(self, guild_id: str):
        """Fetches a guild from cache or if not cached, gets from the database"""

        # Check if the guild is in the cache
        if guild_id in self.cache:
            return self.cache[guild_id]

        # Fetch the guild from the database
        guild = await self.fetch_guild(guild_id)

        # If the guild is not in the database, return an error
        if not guild:
            raise ValueError("Guild not found in database.")

        # Cache the guild and return it
        self.cache[guild_id] = guild
        return guild

    # Create guild
    async def create_guild(self, data: dict):
        """Creates a guild in the database."""

        # Create the guild
        await self.guilds.insert_one(data)

    # Update guild
    async def update_guild(self, guild_id: str, data: dict):
        """Updates a guild in the database."""

        # Update the guild
        await self.guilds.update_one({"guild_id": guild_id}, {"$set": data})

    # Create user
    async def create_user(self, data: dict):
        """Creates a user in the database."""

        # Create the user
        await self.users.insert_one(data)

    # Fetch user
    async def fetch_user(self, user_id: str):
        """Fetches a user from the database."""

        # Fetch the user
        user = await self.users.find_one({"user_id": user_id})

        # If the user is not in the database, return an error
        if not user:
            raise ValueError("User not found in database.")

        # Return the user
        return user

    # Getch user
    async def getch_user(self, user_id: str):
        """Gets a guild from cache or if not cached, gets from the database"""

        # Check if the guild is in the cache
        if user_id in self.cache:
            return self.cache[user_id]

        # Fetch the guild from the database
        user = await self.fetch_user(user_id)

        # If the guild is not in the database, return an error
        if not user:
            raise ValueError("Guild not found in database.")

        # Cache the guild and return it
        self.cache[user_id] = user
        return user

    # Update user
    async def update_user(self, user_id: str, data: dict):
        """Updates a user in the database."""

        # Update the user
        await self.users.update_one({"user_id": user_id}, {"$set": data})
