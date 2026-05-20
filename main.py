import discord
from discord.ext import commands
from openai import OpenAI
import config
import json
import requests
import urllib.parse

# Discord setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# AI setup
client_ai = OpenAI(
    api_key=config.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# Memory
try:
    with open("memory.json", "r") as f:
        memory = json.load(f)
except:
    memory = {}

# Online status
@bot.event
async def on_ready():

    print(f"{bot.user} online!")

    await bot.change_presence(
        activity=discord.Game("Deeps AI")
    )

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")

    except Exception as e:
        print(e)

# Slash command AI
@bot.tree.command(
    name="ai",
    description="Chat dengan Deeps AI"
)
async def ai(interaction: discord.Interaction, prompt: str):

    await interaction.response.defer()

    user_id = str(interaction.user.id)

    if user_id not in memory:
        memory[user_id] = []

    # simpan user chat
    memory[user_id].append({
        "role": "user",
        "content": prompt
    })

    # personality AI
    messages = [
        {
            "role": "system",
            "content": (
                "Nama kamu Deeps. "
                "Kamu AI Discord modern yang ramah, santai, pintar, "
                "dan membantu user."
            )
        }
    ]

    # ambil memory terakhir
    messages.extend(memory[user_id][-10:])

    try:

        response = client_ai.chat.completions.create(
            model=config.MODEL,
            messages=messages
        )

        answer = response.choices[0].message.content

        # simpan jawaban AI
        memory[user_id].append({
            "role": "assistant",
            "content": answer
        })

        # simpan file memory
        with open("memory.json", "w") as f:
            json.dump(memory, f)

        # embed modern
        embed = discord.Embed(
            title="Deeps AI",
            description=answer,
            color=0x5865F2
        )

        embed.set_footer(
            text=f"Requested by {interaction.user}"
        )

        await interaction.followup.send(embed=embed)

    except Exception as e:

        await interaction.followup.send(
            f"Error: {e}"
        )

# image generator
@bot.tree.command(
    name="image",
    description="Generate AI image"
)
async def image(
    interaction: discord.Interaction,
    prompt: str
):

    await interaction.response.defer()

    try:

        encoded_prompt = urllib.parse.quote(prompt)

        image_url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        )

        embed = discord.Embed(
            title="Deeps Image AI",
            description=f"Prompt: {prompt}",
            color=0x5865F2
        )

        embed.set_image(url=image_url)

        await interaction.followup.send(
            embed=embed
        )

    except Exception as e:

        await interaction.followup.send(
            f"Error: {e}"
        )

# Help command
@bot.command()
async def helpme(ctx):

    embed = discord.Embed(
        title="Deeps Help",
        description="Daftar command bot",
        color=0x5865F2
    )

    embed.add_field(
        name="/ai",
        value="Chat dengan AI",
        inline=False
    )

    await ctx.send(embed=embed)

# Run bot
bot.run(config.DISCORD_TOKEN)