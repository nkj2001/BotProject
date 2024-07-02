import sys, os
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
modules_path = os.path.join(parent_dir, "modules")
sys.path.append(modules_path)

import config
import json
import asyncio
import yt_dlp
import youtube
import gpt_song
import discord
from discord.ext import commands
from discord.ui import View
from discord.utils import get

ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "temp/%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerros": False,
    "logtostderr": False,
    "quite": True,
    "no_warnings": True,
    "default_search": "auto",
}

ffmpeg_options = {
    "options": "-vn"
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class MusicButtons(View):
    def __init__(self, parent, ctx, timeout):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.parent = parent
    
    @discord.ui.button(label="⏮", style=discord.ButtonStyle.green)
    async def do_prev(self, interaction, button):
        await interaction.response.defer()
        self.voice = get(self.parent.bot.voice_clients, guild=self.ctx.guild)
        if self.voice.is_playing():
            self.parent.current_index -= 2
            self.voice.stop()

    @discord.ui.button(label="⏭", style=discord.ButtonStyle.green)
    async def do_next(self, interaction, button):
        await interaction.response.defer()
        self.voice = get(self.parent.bot.voice_clients, guild=self.ctx.guild)
        if self.voice.is_playing():
            self.voice.stop()

    @discord.ui.button(label="⏸", style=discord.ButtonStyle.green)
    async def do_pause(self, interaction, button):
        self.voice = get(self.parent.bot.voice_clients, guild=self.ctx.guild)
        status = ""
        if not self.voice.is_playing():
            button.label = "⏸"
            self.voice.resume()
            status = "재생"
        else:
            button.label = "▶"
            self.voice.pause()
            status = "일시중지"
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"```diff\n현재 {status} 상태입니다.```")
    
    @discord.ui.button(label="⏹", style=discord.ButtonStyle.green)
    async def do_stop(self, interaction, button):
        self.voice = get(self.parent.bot.voice_clients, guild=self.ctx.guild)
        status = ""
        if self.voice.is_playing():
            self.parent.stop_playing = True
            self.voice.stop()
            status = "중지 되었습니다."
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f"```diff\n{status}```")
    
    @discord.ui.button(label="#️⃣", style=discord.ButtonStyle.green)
    async def do_list(self, interaction, button):
        await interaction.response.defer()
        self.voice = get(self.parent.bot.voice_clients, guild=self.ctx.guild)
        if self.voice.is_playing():
            list_str = ""
            for i, item in enumerate(self.parent.current_play_list):
                if i == self.parent.current_index:
                    list_str += f"{i+1}. {item} ***(재생중)***\n"
                else:
                    list_str += f"{i+1}. {item}\n"
            
            async def callback_save(interaction):
                if len(self.parent.current_play_list) == 0:
                    await interaction.response.send_message("재생 목록이 비어있습니다.")
                    return
                
                def check(m):
                    return m.author == interaction.user and m.channel == interaction.channel
                
                await interaction.response.send_message("저장될 앨범명을 입력하세요.")
                try:
                    message = await self.parent.bot.wait_for('message', timeout=30, check=check)
                except asyncio.TimeoutError:
                    await interaction.followup.send("입력 시간이 초과 되었습니다.")
                    return
                else:
                    name = message.content

                if not await self.parent.save_album_folder(name):
                    await interaction.followup.send("```이미 존재하는 앨범입니다.```")
                    return
                await interaction.followup.send(f"```{name} 앨범이 저장되었습니다.```")

            async def callback_load(interaction):
                await interaction.response.defer()
                await self.parent._load_album(self.ctx)

            view = View()
            btn_save = discord.ui.Button(style=discord.ButtonStyle.red, label="앨범저장")
            btn_load = discord.ui.Button(style=discord.ButtonStyle.red, label="앨범불러오기")
            btn_save.callback = callback_save
            btn_load.callback = callback_load
            view.add_item(btn_save)
            view.add_item(btn_load)
            embed = discord.Embed(title="재생목록", description=list_str, color=0xc600ff)
            message = await self.ctx.send(embed=embed, view=view)
            for i in range(1, min(len(self.parent.current_play_list)+1, 10)):
                await message.add_reaction(f"{i}\N{combining enclosing keycap}")

class MusicPlayer(commands.Cog):
    '''유튜브 음악 재생 봇'''
    def __init__(self, bot):
        self.bot = bot
        self.current_index = 0
        self.current_play_list = []
        self.stop_playing = False
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user != self.bot.user:
            message = reaction.message
            emoji = reaction.emoji
            if emoji.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9', '10')) and "\N{combining enclosing keycap}" in emoji:
                number = int("".join(filter(str.isdigit, emoji)))
                if number <= len(self.current_play_list):
                    self.current_index = number - 2
                    ctx = await self.bot.get_context(message)
                    voice = get(self.bot.voice_clients, guild=ctx.guild)
                    if voice.is_playing():
                        voice.stop()

    @commands.command(name="play", aliases=["p", "재생"], help="유튜브 음악을 재생합니다.")
    async def play(self, ctx, *, param):
        if not ctx.message.author.voice:
            await ctx.send("음성 채널에 먼저 접속해주세요.")
            return
        else:
            channel = ctx.message.author.voice.channel
            voice = get(self.bot.voice_clients, guild=ctx.guild)
            if not voice or not voice.is_connected():
                await channel.connect()
                voice = get(self.bot.voice_clients, guild=ctx.guild)

        self.current_play_list.append(param)
        await ctx.send(f"```재생목록에 추가 : {param}```")
        if not voice.is_playing():
            await self.__play(ctx)
    
    async def __play(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("음성 채널에 먼저 접속해주세요.")
            return
        else:
            channel = ctx.message.author.voice.channel
            voice = get(self.bot.voice_clients, guild=ctx.guild)
            if not voice or not voice.is_connected():
                await channel.connect()
                voice = get(self.bot.voice_clients, guild=ctx.guild)
            
        if self.current_index >= len(self.current_play_list):
            self.current_index = 0
        
        results = youtube.search_youtube(self.current_play_list[self.current_index])
        if not isinstance(results, list):
            await ctx.send("검색 결과가 없습니다.")
            return

        data = results[0]
        url = f"https://www.youtube.com/watch?v={data.get('vid')}"
        music_info = youtube.youtube_music_info(url)
        music_info["vid"] = data.get("vid")
        music_info["vthumb"] = data.get("vthumb")
        yt_info = ytdl.extract_info(url, download=True)
        filename = ytdl.prepare_filename(yt_info)
        play_source = discord.FFmpegPCMAudio(filename, **ffmpeg_options)
        voice.play(play_source, after=lambda e: asyncio.run_coroutine_threadsafe(self.after_play(ctx), self.bot.loop))

        _prev = youtube.search_youtube(self.current_play_list[self.current_index-1])
        next_index = 0 if self.current_index + 1 >= len(self.current_play_list) else self.current_index + 1
        _next = youtube.search_youtube(self.current_play_list[next_index])

        buttons = MusicButtons(self, ctx, timeout=180)
        embed = await self.get_album(ctx, music_info, _prev[0], _next[0])
        await ctx.send(embed=embed, view=buttons)
    
    async def get_album(self, ctx, data, prev_data=None, next_data=None):
        embed = discord.Embed(title=data.get("title_text"), color=discord.Color.blue())
        vurl = f"https://www.youtube.com/watch?v={data.get('vid')}"
        embed.set_image(url=data.get('vthumb'))
        embed.add_field(name="조회수", value=data.get("view_count"), inline=True)
        embed.add_field(name="게시일", value=data.get("pub_date"), inline=True)
        embed.add_field(name="곡제목", value=data.get("vtitle"), inline=False)
        embed.add_field(name="가수", value=data.get("vsubtitle"), inline=False)
        embed.add_field(name="앨범", value=data.get("vsecondary_subtitle"), inline=False)
        if prev_data is not None:
            embed.add_field(name="이전곡", value=f"[{prev_data['vtitle']}](https://www.youtube.com/watch?v={prev_data['vid']})", inline=True)
        if next_data is not None:
            embed.add_field(name="다음곡", value=f"[{next_data['vtitle']}](https://www.youtube.com/watch?v={next_data['vid']})", inline=True)
        embed.set_author(name="유튜브 링크", url=vurl, icon_url="https://www.freepnglogos.com/uploads/youtube-logo-hd-8.png")
        return embed

    async def after_play(self, ctx):
        print(f"after_play: {self.current_index}")
        if self.stop_playing:
            self.stop_playing = False
            return
        self.current_index += 1
        await self.__play(ctx)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(f"on_voice_state_update: {member} {before} {after}")
        if before.channel and not after.channel:
            channel = before.channel
            if len(before.channel.members) == 1:
                voice = get(self.bot.voice_clients, guild=channel.guild)
                if voice:
                    await voice.disconnect()
                    print(">>> 음성채널에서 나감 <<<<")
    
    @commands.command(name="save", aliases=["s", "저장"], help="현재 재생중인 플레이리스트를 저장합니다.")
    async def save_album(self, ctx, *, name):
        if len(self.current_play_list) == 0:
            await ctx.send("재생 목록이 비어있습니다.")
            return
        
        if not await self.save_album_folder(name):
            await ctx.send("```이미 존재하는 앨범입니다.```")
            return
        await ctx.send(f"```{name} 앨범이 저장되었습니다.```")
    
    async def save_album_folder(self, name):
        target_dir = f"{current_dir}/album"
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        save_file_name = f"{target_dir}/{name}.txt"
        if os.path.exists(save_file_name):
            return False
        with open(save_file_name, "w", encoding="utf-8") as f:
            for item in self.current_play_list:
                f.write(f"{item}\n")
        return True

    @commands.command(name="album", aliases=["al", "앨범불러오기"], help="저장된 앨범 목록을 보여줍니다.")
    async def load_album(self, ctx):
        await self._load_album(ctx)

    async def _load_album(self, ctx):
        target_dir = f"{current_dir}/album"
        if not os.path.exists(target_dir):
            await ctx.send("```저장된 앨범이 없습니다.```")
            return
        file_list = os.listdir(target_dir)
        albums = [file for file in file_list if file.endswith(".txt")]
        if len(albums) == 0:
            await ctx.send("```저장된 앨범이 없습니다.```")
            return
        
        async def select_callback(interaction):
            value = interaction.data["values"][0]
            file_path = f"{target_dir}/{value}.txt"
            temp_list = []
            albums_list = ""
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    temp_list.append(line.strip())
                    albums_list += f"{i+1}. {line.strip()}\n"
            embed = discord.Embed(title=f"{value} 앨범", description=albums_list, color=0xc600ff)
            btn_play = discord.ui.Button(label="▶", style=discord.ButtonStyle.green)
            btn_delete = discord.ui.Button(label="🗑", style=discord.ButtonStyle.red)
            
            async def callback_play(interaction):
                await interaction.response.edit_message(view=None)
                self.current_play_list = []
                self.current_play_list = temp_list
                await self.__play(ctx)
            
            async def callback_delete(interaction):
                await interaction.response.edit_message(view=None)
                os.remove(file_path)
                await ctx.send(f"```{value} 앨범이 삭제되었습니다.```")

            btn_play.callback = callback_play
            btn_delete.callback = callback_delete
            view = View()
            view.add_item(btn_play)
            view.add_item(btn_delete)
            await interaction.response.send_message(embed=embed, view=view)
            
        options = []
        for i, album in enumerate(albums):
            #test.txt
            albums[i] = album[:-4]
            file_path = f"{target_dir}/{album}"
            lines = 0
            with open(file_path, "r", encoding="utf-8") as f:
                lines = sum(1 for t in f if t.strip() != "")
            options.append(discord.SelectOption(label=f"{album[:-4]} ({lines}곡)", value=f"{album[:-4]}"))
        select_menu = discord.ui.Select(
            placeholder="앨범을 선택해주세요.",
            min_values=1,
            max_values=1,
            options=options,
        )
        select_menu.callback = select_callback
        view = View()
        view.add_item(select_menu)
        await ctx.send(view=view)
    
    @commands.command(name="gplay", aliases=["gp", "추천"], help="GPT를 이용한 음악 추천")
    async def gplay(self, ctx, *, param):
        if not ctx.message.author.voice:
            await ctx.send("음성 채널에 먼저 들어가주세요.")
            return
        else:
            channel = ctx.message.author.voice.channel
            voice = get(self.bot.voice_clients, guild=ctx.guild)
            if not voice or not voice.is_connected():
                await channel.connect()
                voice = get(self.bot.voice_clients, guild=ctx.guild)
        
        v = gpt_song.get_song_complete(param)
        j = json.loads(v)
        songs = j.get("songs")
        if len(songs) == 0:
            await ctx.send("검색 결과가 없습니다.")
            return
        
        self.current_play_list = []
        song_list = ""
        for i, song in enumerate(songs):
            completion = f"{song.get('title')} {song.get('artist')}"
            song_list += f"{i+1}. {completion}\n"
            self.current_play_list.append(completion)
        await ctx.send(f"재생 목록에 추가: {song_list}")
        if not voice.is_playing():
            await self.__play(ctx)

    @commands.command(name="add_channel", aliases=["ac", "채널등록"], help="음악관련 명령을 현재 채널에서만 사용 가능하게 합니다.")
    @commands.has_role("음악관리자")
    async def add_channel(self, ctx):
        channel_id = ctx.channel.id
        guild_id = str(ctx.guild.id)

        if guild_id not in config.channel_list:
            config.channel_list[guild_id] = []
        else:
            _list = config.channel_list[guild_id]
            if channel_id in _list:
                await ctx.send(f"```{ctx.channel.name} 채널이 이미 음악 재생 채널에 등록되어 있습니다.```")
                return
        config.channel_list[guild_id].append(channel_id)
        await config.save_channel_list()
        await ctx.send(f"```{ctx.channel.name} 채널을 음악 재생 채널로 등록했습니다.```")

    @commands.command(name="add_voice", aliases=["av", "음성등록"], help="음성 채널을 음악 재생 채널로 등록합니다.")
    @commands.has_role("음악관리자")
    async def add_voice(self, ctx):
        channel_id = ctx.author.voice.channel.id
        guild_id = str(ctx.guild.id)

        if guild_id not in config.voice_list:
            config.voice_list[guild_id] = []
        else:
            _list = config.voice_list[guild_id]
            if channel_id in _list:
                await ctx.send(f"```{ctx.author.voice.channel.name} 채널이 이미 음악 재생 채널에 등록되어 있습니다.```")
                return
        config.voice_list[guild_id].append(channel_id)
        await config.save_voice_list()
        await ctx.send(f"```{ctx.author.voice.channel.name} 채널을 음악 재생 채널로 등록했습니다.```")
    
    @commands.command(name="remove_channel", aliases=["rc", "채널삭제"], help="명령어를 사용한 채널을 음악 재생 채널에서 삭제합니다.")
    @commands.has_role("음악관리자")
    async def remove_channel(self, ctx):
        channel_id = ctx.channel.id
        guild_id = str(ctx.guild.id)
        if guild_id not in config.channel_list:
            await ctx.send(f"```{ctx.channel.name} 채널이 음악 재생 채널에 등록되어있지 않습니다.")
            return
        _list = config.channel_list.get(guild_id)
        if channel_id not in _list:
            await ctx.send(f"```{ctx.channel.name} 채널이 음악 재생 채널에 등록되어있지 않습니다.")
            return
        config.channel_list[guild_id].remove(channel_id)
        await config.save_channel_list()
        await ctx.send(f"```{ctx.channel.name} 채널을 음악 재생 채널에서 삭제했습니다.")
    
    @commands.command(name="remove_voice", aliases=["rv", "음성삭제"], help="음성 채널을 음악 재생 채널에서 삭제합니다.")
    @commands.has_role("음악관리자")
    async def remove_voice(self, ctx):
        channel_id = ctx.author.voice.channel.id
        guild_id = str(ctx.guild.id)
        if guild_id not in config.voice_list:
            await ctx.send(f"```{ctx.author.voice.channel.name} 채널이 음악 재생 채널에 등록되어있지 않습니다.")
            return
        _list = config.voice_list.get(guild_id)
        if channel_id not in _list:
            await ctx.send(f"```{ctx.author.voice.channel.name} 채널이 음악 재생 채널에 등록되어있지 않습니다.")
            return
        config.voice_list[guild_id].remove(channel_id)
        await config.save_voice_list()
        await ctx.send(f"```{ctx.author.voice.channel.name} 채널을 음악 재생 채널에서 삭제했습니다.")
    
    @commands.command(name="list_channel", aliases=["lc", "채널목록"], help="음악 재생 채널 목록을 보여줍니다.")
    @commands.has_role("음악관리자")
    async def list_channel(self, ctx):
        guild_id = str(ctx.guild.id)
        _list = config.channel_list.get(guild_id)
        if _list is None:
            return
        channel_names = ""
        for i, channel_id in enumerate(_list):
            channel = self.bot.get_channel(channel_id)
            channel_names += f"{i+1}. {channel.name}\n"
        await ctx.send(f"```{channel_names}```")
    
    @commands.command(name="list_voice", aliases=["lv", "음성목록"], help="음악 재생 채널 목록을 보여줍니다.")
    @commands.has_role("음악관리자")
    async def list_voice(self, ctx):
        guild_id = str(ctx.guild.id)
        _list = config.voice_list.get(guild_id)
        if _list is None:
            return
        channel_names = ""
        for i, channel_id in enumerate(_list):
            channel = self.bot.get_channel(channel_id)
            channel_names += f"{i+1}. {channel.name}\n"
        await ctx.send(f"```{channel_names}```")

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))