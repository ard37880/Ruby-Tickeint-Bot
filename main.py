import nextcord
import apikeys 
import logging

from nextcord.ext import commands, tasks
from nextcord.ui import View, Button
from apikeys import discord_bot_token

intents = intents = nextcord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())


ticket_message = YOUR MESSAGE ID HERE
ticket_category = YOUR CATEGORY ID HERE
tiecket_channel = YOUR CHANNEL ID HERE

@bot.event
async def on_ready():
    message = await bot.get_channel(tiecket_channel).fetch_message(ticket_message)
    if "🎫" not in [reaction.emoji for reaction in message.reactions]:
        await message.add_reaction("🎫")

@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)

    if payload.message_id == ticket_message and str(payload.emoji) == "🎫" and not user.bot:
        message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if "🎫" not in [reaction.emoji for reaction in message.reactions]:
            await message.add_reaction
        else:
            await message.remove_reaction(payload.emoji, user)
        category = bot.get_channel(ticket_category)
        channel_name = f"{user.name}-ticket"

        for channel in category.text_channels:
            if channel.name.lower() == channel_name.lower():
                print("User already has a ticket open!")
                return
        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            user: nextcord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)
        }

        channel = await category.create_text_channel(name=channel_name, overwrites=overwrites)
        embed = nextcord.Embed(
            title="Ticket Created!",
            description="Please describe your issue or request and someone will be with you shortly!",
            color=0x2b2d31        
        ) 
        embed.set_author(name=user.name+"#"+user.discriminator, icon_url=str(user.avatar.url))
        message = await channel.send(user.mention,embed=embed)
        print("Ticket has been created!") 

bot.run(discord_bot_token)
