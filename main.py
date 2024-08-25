import os
import discord
from discord.ext import commands, tasks
import requests

from myserver import  server_on


ROBLOX_IDS = []  # ใส่ Roblox IDs ที่ต้องการตรวจสอบที่นี่


intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!',intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_roblox_status.start()

@tasks.loop(minutes=5)  # ตั้งให้บอทอัปเดตสถานะทุก 5 นาที
async def check_roblox_status():
    try:
        presence_response = requests.post(
            'https://presence.roblox.com/v1/presence/users',
            json={"userIds": ROBLOX_IDS}
        )

        if presence_response.status_code == 200:
            presence_data = presence_response.json()
            statuses = []

            for presence in presence_data['userPresences']:
                user_id = presence['userId']
                online_status = presence['userPresenceType']
                status_emoji = '🟢' if online_status == 2 else '🔴'
                user_info_response = requests.get(f'https://users.roblox.com/v1/users/{user_id}')
                if user_info_response.status_code == 200:
                    user_info = user_info_response.json()
                    username = user_info.get('name', 'Unknown')
                    statuses.append(f'{username}: {status_emoji}')
                else:
                    statuses.append(f'{user_id}: {status_emoji}')

            # ส่งสถานะไปยังช่องที่ต้องการ (เช่น general channel) ถ้าเป็นไปได้
            channel = discord.utils.get(bot.get_all_channels(), name='general')
            if channel:
                embed = discord.Embed(title="Roblox User Status", color=discord.Color.blue())
                for status in statuses:
                    user, emoji = status.split(': ')
                    embed.add_field(name=user, value=emoji, inline=False)
                await channel.send(embed=embed)
        else:
            print('ไม่สามารถตรวจสอบสถานะผู้ใช้ได้ในขณะนี้')

    except Exception as e:
        print(f'An error occurred: {e}')

@bot.command()
async def check(ctx):
    try:
        presence_response = requests.post(
            'https://presence.roblox.com/v1/presence/users',
            json={"userIds": ROBLOX_IDS}
        )

        if presence_response.status_code == 200:
            presence_data = presence_response.json()
            statuses = []

            for presence in presence_data['userPresences']:
                user_id = presence['userId']
                online_status = presence['userPresenceType']
                status_emoji = '🟢' if online_status == 2 else '🔴'
                user_info_response = requests.get(f'https://users.roblox.com/v1/users/{user_id}')
                if user_info_response.status_code == 200:
                    user_info = user_info_response.json()
                    username = user_info.get('name', 'Unknown')
                    statuses.append(f'{username}: {status_emoji}')
                else:
                    statuses.append(f'{user_id}: {status_emoji}')

            embed = discord.Embed(title="Roblox User Status", color=discord.Color.blue())
            for status in statuses:
                user, emoji = status.split(': ')
                embed.add_field(name=user, value=emoji, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send('ไม่สามารถตรวจสอบสถานะผู้ใช้ได้ในขณะนี้')

    except Exception as e:
        await ctx.send(f'An error occurred: {e}')
server_on()

bot.run(os.getenv('TOKEN'))
