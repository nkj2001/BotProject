import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests
import cv2
from openai import OpenAI
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=OPENAI_KEY)

class ImageProcess(commands.Cog):
    '''이미지 봇'''
    def __init__(self, bot):
        self.bot = bot
        self.attachment_url = None
        self.attachment_file = None
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if len(message.attachments) > 0:
            for file in message.attachments:
                ext = file.filename.split(".")[-1]
                if ext.lower() in ["jpg", "png"]:
                    r = requests.get(file.url)
                    save_image_file = f"img.{ext}"
                    with open(save_image_file, "wb") as f:
                        f.write(r.content)
                    self.attachment_url = file.url
                    self.attachment_file = save_image_file

                    view = discord.ui.View()
                    btn_gpt = discord.ui.Button(style=discord.ButtonStyle.blurple, label="분석")
                    btn_ocr = discord.ui.Button(style=discord.ButtonStyle.blurple, label="OCR")
                    btn_bw = discord.ui.Button(style=discord.ButtonStyle.green, label="흑백")
                    btn_flip = discord.ui.Button(style=discord.ButtonStyle.green, label="뒤집기")
                    btn_invert = discord.ui.Button(style=discord.ButtonStyle.green, label="반전")

                    btn_gpt.callback = self.cb_gpt
                    btn_ocr.callback = self.cb_ocr
                    btn_bw.callback = self.cb_bw
                    btn_flip.callback = self.cb_flip
                    btn_invert.callback = self.cb_invert

                    view.add_item(btn_gpt)
                    view.add_item(btn_ocr)
                    view.add_item(btn_bw)
                    view.add_item(btn_flip)
                    view.add_item(btn_invert)
                    await message.channel.send("🎞 기능을 선택하세요.", view=view)
        
    def descript_image(self, prompt, image_url):
        response = client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message.content
    
    async def cb_gpt(self, it):
        await it.response.send_message("분석중입니다..", ephemeral=True)
        r = self.descript_image("이미지에 대해 자세히 설명해줘.", file.url)
        await it.edit_original_response(content=r)
    
    async def cb_ocr(self, it):
        await it.response.send_message("문자 분석중입니다..", ephemeral=True)
        r = self.descript_image("이미지에 보이는 모든 글자를 추출해줘.", file.url)
        await it.edit_original_response(content=r)
    
    async def cb_bw(self, it):
        await it.response.send_message("흑백처리중 입니다..", ephemeral=True)
        cv_image = cv2.imread(save_image_file)
        img_gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite("opencv_grey.jpg", img_gray)
        await it.edit_original_response(content="흑백처리가 완료되었습니다.", attachments=[discord.File("opencv_grey.jpg")])
    
    async def cb_flip(self, it):
        await it.response.send_message("뒤집기 중 입니다..", ephemeral=True)
        cv_image = cv2.imread(save_image_file)
        img_flip = cv2.flip(cv_image, 1)
        cv2.imwrite("opencv_flip.jpg", img_flip)
        await it.edit_original_response(content="뒤집기가 완료되었습니다.", attachments=[discord.File("opencv_flip.jpg")])
    
    async def cb_invert(self, it):
        await it.response.send_message("반전 중 입니다..", ephemeral=True)
        cv_image = cv2.imread(save_image_file)
        img_invert = cv2.bitwise_not(cv_image)
        cv2.imwrite("opencv_invert.jpg", img_invert)
        await it.edit_original_response(content="반전이 완료되었습니다.", attachments=[discord.File("opencv_invert.jpg")])

async def setup(bot):
    await bot.add_cog(ImageProcess(bot))