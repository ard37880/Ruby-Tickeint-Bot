import nextcord
import logging
import os

from nextcord.ext import commands, tasks
from nextcord.ui import View, Button

intents = intents = nextcord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())


ticket_message = #ADD MESSAGE HERE
ticket_category = #ADD CATAGORY HERE
tiecket_channel = #ADD CHANNEL HERE

class CloseTicketButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(style=nextcord.ButtonStyle.red, label="Close Ticket")

    async def callback(self, interaction: nextcord.Interaction):
        # Check if the user has the "Reports" role
        staff_role = nextcord.utils.get(interaction.guild.roles, name="Staff")
        if staff_role in interaction.user.roles:
            # Start transcribing channel messages
            transcript = []
            async for message in interaction.channel.history(limit=100, oldest_first=True):  # Adjust limit as needed
                # Format each message and add it to the transcript list
                transcript.append(f"{message.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {message.author.display_name}: {message.content}")

            # Convert transcript list to a string and save to a .txt file
            transcript_content = "\n".join(transcript)
            transcript_file_name = f"{interaction.channel.name}-transcript.txt"
            with open(transcript_file_name, 'w', encoding='utf-8') as file:
                file.write(transcript_content)

            # Send the transcript to a specified log channel
            log_channel_id = 1214764984718852126  # Replace with your log channel ID
            log_channel = interaction.guild.get_channel(log_channel_id)
            if log_channel:  # Check if the log channel exists
                await log_channel.send(f"Transcript for closed ticket {interaction.channel.name}:", file=nextcord.File(transcript_file_name))

            # Now delete the ticket channel
            await interaction.channel.delete(reason=f"Ticket closed by {interaction.user.display_name}.")

            # Clean up local transcript file after sending
            os.remove(transcript_file_name)
        else:
            await interaction.response.send_message("Sorry, you do not have permission to close this ticket.", ephemeral=True)

class TicketView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(CloseTicketButton())

@bot.event
async def on_ready():
    message = await bot.get_channel(tiecket_channel).fetch_message(ticket_message)
    if "🎫" not in [reaction.emoji for reaction in message.reactions]:
        await message.add_reaction("🎫")

@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)
    channel = None  # Initialize channel to None

    # Check if the reaction is to the designated ticket message and not from a bot
    if payload.message_id == ticket_message and str(payload.emoji) == "🎫" and not user.bot:
        category = bot.get_channel(ticket_category)
        channel_name = f"{user.name}-ticket"

        # Check if a ticket channel already exists for the user
        for existing_channel in category.text_channels:
            if existing_channel.name.lower() == channel_name.lower():
                print("User already has a ticket open!")
                return  # Exit if the ticket already exists

        # Define permission overwrites for the new ticket channel
        member_role = nextcord.utils.get(guild.roles, name="Members")
        if member_role is None:
            print("Member role not found!")
            return

        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            user: nextcord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, manage_messages=True, read_message_history=True),
            member_role: nextcord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, manage_messages=True, read_message_history=True)
        }

        # Create the ticket channel
        channel = await category.create_text_channel(name=channel_name, overwrites=overwrites)

        if channel:
            embed = nextcord.Embed(
                title="Ticket Created!",
                description="Please describe your issue or request and someone will be with you shortly!",
                color=0x2b2d31        
            ) 
            embed.set_author(name=user.name + "#" + user.discriminator, icon_url=str(user.avatar.url))
            
            # Send the welcome message in the newly created ticket channel
            ticket_view = TicketView()  # Make sure TicketView class is defined elsewhere in your code
            await channel.send(user.mention, embed=embed, view=ticket_view)
            print("Ticket has been created!")

bot.run("YOUR_TOKEN_HERE")
