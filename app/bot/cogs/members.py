import discord
from discord.ext import commands
from typing import List
from app.bot.db_queries import(
    get_member_total_xp,
    get_all_member_xp,
    get_inactive_members,
    get_members_by_rank,
    get_member_xp_history,
    get_inactive_members_by_rank_and_days
)

def paginate_lines(lines: List[str], max_chars=2000) -> List[str]:
    pages = []
    current = []
    current_len = 0
    for line in lines:
        l = line + "\n"
        if current_len + len(l) > max_chars:
            pages.append("".join(current).rstrip())
            current = [l]
            current_len = len(l)
        else:
            current.append(l)
            current_len += len(l)
    if current:
        pages.append("".join(current).rstrip())
    return pages

class InactivePaginationView(discord.ui.View):
    def __init__(self, pages: List[str], author_id: int, title: str, timeout: int = 120):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.author_id = author_id
        self.title = title
        self.index = 0

    def _build_embed(self) -> discord.Embed:
        embed = discord.Embed(title=self.title, description=self.pages[self.index], color=discord.Color.red())
        embed.set_footer(text=f"Page {self.index + 1}/{len(self.pages)}")
        return embed
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This pagination session isn't for you", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="⬅️ Prev", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index - 1) % len(self.pages)
        await interaction.response.edit_message(embed=self._build_embed(), view=self)

    @discord.ui.button(label="➡️ Next", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index + 1) % len(self.pages)
        await interaction.response.edit_message(embed=self._build_embed(), view=self)

    @discord.ui.button(label="⛔ Close", style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.edit_message(view=None)

    async def on_timeout(self):
        # remove buttons when view times out
        for child in self.children:
            child.disabled = True
        try:
            # edit original message if still present
            await self.message.edit(view=self)
        except Exception:
            pass

    # will be set by caller after sending the initial message
    message: discord.Message

class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="xp", description="Get a member's total xp")
    async def get_xp(self, ctx, rsn: str):
        member_data = get_member_total_xp(rsn)

        if not member_data or member_data['total_xp'] is None:
            await ctx.send(f"Member **{rsn}** not found or has no xp data.")
            return
        
        embed = discord.Embed(
            title=f"{member_data['rsn']}'s Stats",
            color=discord.Color.blue()
        )
        embed.add_field(name="Rank", value=member_data['rank'], inline=True)
        embed.add_field(name="Total XP", value=f"{member_data['total_xp']:,}", inline=True)
        embed.add_field(name="Last Updated", value=member_data['timestamp'], inline=False)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="leaderboard", description="Show the clan xp leaderboard")
    async def leaderboard(self, ctx):
        members = get_all_member_xp()

        if not members:
            await ctx.send("No members with xp data found.")
            return
        
        # Take top 10 members
        top_10 = members[:10]

        embed = discord.Embed(
            title="Clan XP Leaderboard",
            color=discord.Color.gold()
        )

        leaderboard_text = "\n".join(
            [f"{i+1}. {m['rsn']} - {m['total_xp']:,} XP ({m['rank']})" 
             for i, m in enumerate(top_10)]
        )
        embed.description = leaderboard_text

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="inactive", description="Show inactive members by rank and days")
    async def inactive(self, ctx, rank: str, days: int):
        if days < 1:
            await ctx.send("Days must be at least 1.")
            return
        
        inactive_members = get_inactive_members_by_rank_and_days(rank, days)

        if not inactive_members:
            await ctx.send(f"No **{rank}** members found inactive in {days}+ days.")
            return
        
        lines = [f"- {m['rsn']}: {m['current_xp']:,} XP (unchanged since {m['old_timestamp']})" 
                 for m in inactive_members]
        pages = paginate_lines(lines)
        title = f"Inactive {rank}s ({len(inactive_members)} - No XP gain in {days}+ days)"

        if len(pages) == 1:
            embed = discord.Embed(title=title, description=pages[0], color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        view = InactivePaginationView(pages=pages, author_id=ctx.author.id, title=title)
        initial_embed = view._build_embed()
        message = await ctx.send(embed=initial_embed, view=view)
        view.message = message

async def setup(bot):
    await bot.add_cog(MembersCog(bot))