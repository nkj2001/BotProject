from dotenv import load_dotenv
import os
import discord
client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print("봇 사용 준비")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(f"메세지 수신: {message.content}")

@client.event
async def on_connect():
    print("--디스코드에 접속 되었습니다--")

@client.event
async def on_disconnect():
    print("--디스코드에서 연결이 끊어졌습니다--")

load_dotenv()
token = os.getenv("TOKEN")
client.run(token)