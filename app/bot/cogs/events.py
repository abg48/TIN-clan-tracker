import os
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from app.external.sheets import log_item, undo_item, item_cache

async def item_name_autocomplete(interaction: discord.Interaction, current: str):
    suggestions = [item for item in item_cache.get_items() if current.lower() in item.lower()]
    return [app_commands.Choice(name=item, value=item) for item in suggestions[:25]]

def get_team_number(member: discord.Member):
    for role in member.roles:
        if role.name.startswith("Team ") and role.name[5:].isdigit():
            return role.name
    return None

class UndoDropView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Undo", style=discord.ButtonStyle.danger, custom_id="undo_drop")
    async def undo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = interaction.message.content
        
        try:
            submitter_id = int(content.split("<@")[1].split(">")[0])
        except (IndexError, ValueError):
            submitter_id = None

        admin_role = discord.utils.get(interaction.guild.roles, name="Admin+")
        is_admin = admin_role in interaction.user.roles
        is_submitter = interaction.user.id == submitter_id

        if not is_admin and not is_submitter:
            await interaction.response.send_message("You can not undo another players drop.", ephemeral=True)
            return

        try:
            drop_id = content.split("Drop ID: ")[1].split("\n")[0]
        except IndexError:
            await interaction.response.send_message("Could not read drop ID from message.", ephemeral=True)
            return
        
        success = False
        try:
            success = undo_item(drop_id)
        except Exception as e:
            await interaction.response.send_message(f"Error undoing drop: {e}", ephemeral=True)
            return
        
        button.disabled = True

        if success:
            await interaction.response.edit_message(
                content = f"~~{content}~~\n-# Drop `{drop_id}` has been removed.",
                view = self
            )
        else:
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f"Drop '{drop_id}' could not be undone (not found).", ephemeral=True)

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            item_cache.sync_items()
        except Exception as e:
            print(f"[EventsCog] Warning: failed to sync item cache on startup: {e}")

    @app_commands.command(name="logdrop", description="Log a players drop to the spreadsheet")
    @app_commands.autocomplete(item_name=item_name_autocomplete)
    async def logdrop(self, interaction: discord.Interaction, item_name: str, proof: discord.Attachment):
        if item_name not in item_cache.get_items():
            await interaction.response.send_message(f"**{item_name}** is not a valid drop. Use the autocomplete suggestions or ping admin+ if you believe this is an error.", ephemeral=True)
            return
        
        if not proof.content_type or not proof.content_type.startswith("image/"):
            await interaction.response.send_message("Proof must be an image file.", ephemeral=True)
            return
        
        team = get_team_number(interaction.user)
        if team is None:
            await interaction.response.send_message("You are not assigned to a team.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        user = interaction.user.display_name
        timestamp = datetime.utcnow().isoformat()
        
        try:
            archive_channel_id = int(os.environ["PROOF_ARCHIVE_CHANNEL_ID"])
            archive_channel = self.bot.get_channel(archive_channel_id)
            archive_message = await archive_channel.send(
                f"Drop proof | {item_name} | {interaction.user.mention} | {timestamp}",
                file=await proof.to_file()
            )
            
            drop_id = log_item(item_name, user, timestamp, team)

            await archive_message.edit(
                content=f"Drop proof | {item_name} | {interaction.user.mention} | {timestamp}\nDrop ID: {drop_id}",
                view=UndoDropView()
            )

            await interaction.followup.send(
                f"Logged **{item_name}** for {interaction.user.mention}. Drop ID: {drop_id}",
                view=UndoDropView(),
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"Failed to log event, please try again or ping admin+", ephemeral=True)
    
    @app_commands.command(name="eventdbsync", description="Sync the event item database with the spreadsheet")
    async def eventdbsync(self, interaction: discord.Interaction):
        try:
            item_cache.sync_items()
            await interaction.response.send_message("Event item database synced successfully.")
        except Exception as e:
            await interaction.response.send_message("Failed to sync event item database", ephemeral=True)

async def setup(bot):
    await bot.add_cog(EventsCog(bot))