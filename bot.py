import discord
from discord import app_commands
import re
import os

CATEGORY_NAME = 'Tickts'
MESSAGE = 'If you want to add credits, make sure to purchase them from https://leons-shop.mysellauth.com/'
PURCHASE_CHANNEL_ID = 1510326641619112209
VOUCH_CHANNEL_ID = 1510326642629677149
LEON_ID = 372966022954876929

vouch_count = 1
owners = set()

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.dm_messages = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync()
    print(f'Bot is online as {client.user}')


@client.event
async def on_guild_channel_create(channel):
    if channel.category and channel.category.name == CATEGORY_NAME:
        await channel.send(MESSAGE)


@client.event
async def on_message(message):
    global vouch_count

    if message.channel.id == VOUCH_CHANNEL_ID and not message.author.bot:
        try:
            await message.add_reaction('✅')
            await message.reply(f'# Vouch Number: {vouch_count} ✅')
            vouch_count += 1
        except Exception as e:
            print(f'Could not react/reply: {e}')

    if message.channel.id != PURCHASE_CHANNEL_ID:
        return
    if not message.embeds:
        return
    embed = message.embeds[0]
    if embed.description:
        text = embed.description
    elif embed.fields:
        text = ' '.join(f.name + ' ' + f.value for f in embed.fields)
    else:
        text = ''

    id_match = re.search(r'\(`(\d{17,19})`\)', text)
    product_match = re.search(r'\*\*Product:\*\*\s*(.+)', text, re.IGNORECASE)
    quantity_match = re.search(r'\*\*Quantity:\*\*\s*(.+)', text, re.IGNORECASE)
    price_match = re.search(r'\*\*Amount Paid:\*\*\s*(.+)', text, re.IGNORECASE)

    discord_id = int(id_match.group(1)) if id_match else None
    product = product_match.group(1).strip() if product_match else 'Product'
    quantity = quantity_match.group(1).strip() if quantity_match else '1'
    price = price_match.group(1).strip() if price_match else '?'

    if not discord_id:
        print('No Discord ID found')
        return

    try:
        user = await client.fetch_user(discord_id)
        await user.send(
            f'Thank you for your purchase! I would really appreciate it if you could paste this next message in <#{VOUCH_CHANNEL_ID}>!\n'
            f'+rep <@{LEON_ID}> bought {quantity}x {product} [{price}] thank you legit'
        )
        print(f'DM sent to {discord_id}')
    except Exception as e:
        print(f'Could not send DM: {e}')


SUPER_OWNER = 372966022954876929

@tree.command(name='resetvouch', description='Reset vouch counter')
@app_commands.describe(number='Start number')
async def resetvouch(interaction: discord.Interaction, number: int):
    if interaction.user.id not in owners:
        await interaction.response.send_message('You have no permission to use this command.', ephemeral=True)
        return
    global vouch_count
    vouch_count = number
    await interaction.response.send_message(f'Vouch counter reset to {vouch_count}', ephemeral=True)


@tree.command(name='vouchmsggen', description='Generate vouch message for a customer')
@app_commands.describe(user='The customer', product='Product name', price='Price', payment='Payment method')
async def vouchmsggen(interaction: discord.Interaction, user: discord.User, product: str, price: str, payment: str):
    if interaction.user.id not in owners:
        await interaction.response.send_message('You have no permission to use this command.', ephemeral=True)
        return
    try:
        await user.send(
            f'Thank you for your purchase! I would really appreciate it if you could paste this next message in <#{VOUCH_CHANNEL_ID}>!\n'
            f'+rep <@{LEON_ID}> bought {product} [{price}] {payment} thank you legit'
        )
        await interaction.response.send_message(f'DM sent to {user}', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'Could not send DM: {e}', ephemeral=True)


@tree.command(name='setowner', description='Add an owner')
@app_commands.describe(user='The user to add as owner')
async def setowner(interaction: discord.Interaction, user: discord.User):
    if interaction.user.id != SUPER_OWNER:
        await interaction.response.send_message('You are not authorized.', ephemeral=True)
        return
    owners.add(user.id)
    await interaction.response.send_message(f'{user} added as owner', ephemeral=True)


@tree.command(name='removeowner', description='Remove an owner')
@app_commands.describe(user='The user to remove')
async def removeowner(interaction: discord.Interaction, user: discord.User):
    if interaction.user.id != SUPER_OWNER:
        await interaction.response.send_message('You are not authorized.', ephemeral=True)
        return
    owners.discard(user.id)
    await interaction.response.send_message(f'{user} removed as owner', ephemeral=True)


client.run(os.environ['TOKEN'])
