import brawlstats
import discord
from discord.ext import commands
from discord.ext import tasks
from discord_components import DiscordComponents, Button, ButtonStyle
from discord.utils import get
import sqlite3

connection = sqlite3.connect('server.db')
cursor = connection.cursor()

bs = brawlstats.Client(
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjYyMjY0ZGE4LTFmN2EtNGIxMy04NWIzLWE5MzZjNzIzYWYxOCIsImlhdCI6MTY0MDgxNTgzNiwic3ViIjoiZGV2ZWxvcGVyL2I1MTIxNTg1LTIxODItNzRkNS0xZWQxLTc5MGFkMzk1NDQ1NiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMTg4LjEyMy4yMzEuNzkiXSwidHlwZSI6ImNsaWVudCJ9XX0.7eA4cWKYjhgkHQJ4HfM4m7jMxTY6TzxRHmMhXs-LG-uFBSz5YirMwHSQcJpJG1vYDHjiWnPrWsNTAxiMnKM_-Q')

client = commands.Bot(command_prefix=".", intents=discord.Intents.all())


@client.event
async def on_ready():
    cursor.execute("""CREATE TABLE IF NOT EXISTS bs_info (
        name TEXT,
        id INT,
        bs_id TEXT
    )""")
    for guild in client.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM bs_info WHERE id = {member.id}").fetchone() is None and get(guild.roles,
                                                                                                           id=778608048808656937) not in member.roles:
                cursor.execute(f"INSERT INTO bs_info VALUES ('{member}', {member.id}, 'None')")
                connection.commit()
            else:
                pass
    DiscordComponents(client)
    print("BOSS IS HERE")


@client.event
async def on_member_join(member):
    if cursor.execute(f"SELECT id FROM bs_info WHERE id = {member.id}").fetchone() is None and get(
            client.guilds[0].roles, id=778608048808656937) not in member.roles:
        cursor.execute(f"INSERT INTO bs_info VALUES ('{member}', {member.id}, 'None')")
        connection.commit()
    else:
        pass


@client.command()
async def verify(ctx, arg):
    if cursor.execute(f"SELECT bs_id FROM bs_info WHERE id = {ctx.author.id}").fetchone()[0] == "None":
        try:
            _arg = str(arg)
            _arg = _arg.upper()
            _arg = _arg.replace("O", "0")
            player = bs.get_profile(_arg)
            embed = discord.Embed()
            embed.description = (f"Ник: {player.name}\n\n"
                                 f"ID:  {_arg}\n\n"
                                 f"Трофеи: {player.trophies}\n\n"
                                 f"Клуб: {player.club.name}")

            await ctx.send(embed=embed, components=[
                Button(style=ButtonStyle.green, label="Это я!"),
                Button(style=ButtonStyle.red, label="Что-то не то!")
            ])
            interaction = await client.wait_for("button_click")
            if interaction.component.label == "Это я!":
                cursor.execute(f"UPDATE bs_info SET bs_id = '{_arg}' WHERE id = {ctx.author.id}")
                connection.commit()
                emb = discord.Embed(
                    description=f"{ctx.author.mention} привязка прошла успешно!"
                )
                await interaction.respond(embed=emb)
            elif interaction.component.label == "Что-то не то!":
                emb = discord.Embed(
                    description=f"{ctx.author.mention} понял!"
                )
                await interaction.respond(embed=emb)

        except Exception as _exception:
            print(_exception)
            embed2 = discord.Embed()
            embed2.description = (f"{ctx.author.mention}\n\n"
                                  f"Вы ввели неправильный тэг!")
            await ctx.send(embed=embed2)
    else:
        emb = discord.Embed(
            description=f"{ctx.author.mention} вы уже привязали свой тэг!"
        )
        await ctx.send(embed=emb)

@verify.error
async def verify_error(ctx, error):
    if "arg is a required argument that is missing." in str(error):
        emb=discord.Embed(
            description=f"{ctx.author.mention} использование:\n\n"
                        f".verify <тэг>"
        )
        await ctx.send(embed=emb)

token = "OTIzOTY5OTQyMDUzODcxNzA2.YcXwEA.7BlfAe4WcDU5YDZemlJG1WJyjUg"
client.run(token)
