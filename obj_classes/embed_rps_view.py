import asyncio
import discord
import random

class RPSView(discord.ui.View):
    def __init__(self, player: discord.User, bet : int):
        super().__init__(timeout=30)
        self.player = player
        self.bet = bet
        self.result = None
        self.event = asyncio.Event()

    async def _finish(self, interaction: discord.Interaction, choice: str):
        if interaction.user.id != self.player.id:
            await interaction.response.send_message(
                "This isn’t your game!", ephemeral=True
            )
            return

        bot_choice = random.choice(["Rock", "Paper", "Scissors"])
        if choice == bot_choice:
            outcome = "tie"
        elif (choice == "Rock" and bot_choice == "Scissors") or \
             (choice == "Paper" and bot_choice == "Rock") or \
             (choice == "Scissors" and bot_choice == "Paper"):
            outcome = "win"
        else:
            outcome = "lose"

        self.result = f"You chose **{choice}** | Bot chose **{bot_choice}** → {outcome}"

        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Rock Paper Scissors",
                description=self.result,
                color=discord.Color.blurple()
            ),
            view=None
        )

        self.event.set()

    @discord.ui.button(label="🪨 Rock", style=discord.ButtonStyle.primary)
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._finish(interaction, "Rock")

    @discord.ui.button(label="📜 Paper", style=discord.ButtonStyle.success)
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._finish(interaction, "Paper")

    @discord.ui.button(label="✂️ Scissors", style=discord.ButtonStyle.danger)
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._finish(interaction, "Scissors")