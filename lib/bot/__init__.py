from asyncio import sleep
import sys, os
import shutil
from datetime import datetime
from pathlib import Path
from glob import glob
import discord
import asyncio
from discord import Embed, File
from discord import Intents
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown,
                                  MissingPermissions, MissingRole, MissingAnyRole, NotOwner)
from discord.ext.commands import when_mentioned_or
from git import Repo, rmtree
from ..db import db

OWNER_IDS = [322773637772083201, 840707271385284628]

COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]

IGNORE_EXCEPTIONS = (
CommandNotFound, BadArgument, MissingPermissions, MissingRole, MissingAnyRole, MissingRequiredArgument, NotOwner)


def get_prefix(bot, message):
    prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
    if prefix == None or prefix == '':
        db.execute("INSERT INTO guilds VALUES (?, ?)", message.guild.id, "?")
        db.commit()
        prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
    return when_mentioned_or(prefix)(bot, message)


def get_prefix_message(message):
    prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
    return prefix


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog pronto")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.cogs_ready = Ready()

        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)

        super().__init__(
            command_prefix=get_prefix,
            owner_ids=OWNER_IDS,
            intents=Intents.all(),
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f'lib.cogs.{cog}')
            print(f"{cog} cog carregado")

        print("Setup terminado")

    def update_db(self):
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                     ((guild.id,) for guild in self.guilds))
        for guild in self.guilds:
            for member in guild.members:
                if not member.bot:
                    db.execute("INSERT OR IGNORE INTO exp (UserID) VALUES (?)", member.id)
                    db.execute("INSERT OR IGNORE INTO expg (UniqueID) VALUES (?)",  str(member.id) + ':' + str(member.guild.id))



        db.commit()

    def run(self, version):
        self.VERSION = version

        self.setup()

        with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("Executando bot...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if self.ready:
            if ctx.command is not None and ctx.guild is not None:
                await self.invoke(ctx)
        else:
            pass
        # await ctx.send("Não estou pronto para receber comandos. Por favor, espere alguns segundos")

    async def on_connect(self):
        self.update_db()
        print("Bot conectado")

    async def on_disconnect(self):
        print("Bot disconectado")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_comand_error":
            await args[0].send("Algo deu Errado.")

        await self.stdout.send("Aconteceu algum erro.\n\n"
                               f"```\n{args}```")
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        elif isinstance(exc, asyncio.TimeoutError):
            await ctx.send("O tempo de react acabou.")

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f"Este comando está em cooldown. Tente denovo depois de {exc.retry_after:,.2f}s")

        elif hasattr(exc, "original"):

            # if isinstance(exc.original, HTTPException):
            #	await ctx.send("Não consegui enviar a mensagem")

            if isinstance(exc.original, Forbidden):
                await ctx.send("Eu não tenho permissões para fazer isso.")

            else:
                raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:

            self.stdout = self.get_channel(828070139760083018)
            # self.scheduler.add_job(self.print_message, CronTrigger(second="0,15,30,45"))
            self.scheduler.start()

            self.update_db()
            # embed = Embed(title="Now online!",
            # 	description= "O pai ta on",
            # 	colour=0xFF0000,
            # 	timestamp=datetime.utcnow()
            # 	)
            # fields = [("Name", "Value", True),
            # 			("Another Field", "Este field está próximo", True),
            # 			("Um field no-inline", "Aparece em row", False)]

            # for name, value, inline in fields:
            # 	embed.add_field(name=name, value=value, inline=inline)
            # embed.set_author(name="Hub Científico e Filosófico", icon_url='https://i.imgur.com/ThuCQSD.png')
            # embed.set_footer(text="This is a footer!")
            # embed.set_thumbnail(url='https://i.imgur.com/nsgbqmQ.gif')
            # embed.set_image(url= 'https://i.imgur.com/ThuCQSD.png')
            # await self.stdout.send(embed=embed)

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            await self.stdout.send("O pai ta on!")
            self.ready = True
            print("Bot pronto")

        else:
            await self.stdout.send("Meu sistema havia caído, mas reconectei.")
            print("Bot Reconectado")

    async def on_message(self, message):

        if not message.author.bot:
            await self.process_commands(message)
            prefix = get_prefix_message(message)
            if message.content.lower() == (f"{prefix}git pull sophia") and message.author.id in OWNER_IDS:
                unidade_local = 'C'
                canal = message.channel
                await canal.send(
                    '<:sasuke:824400439482777640> Me parece que você é o meu dono. Irei fazer unload nos Cogs...',
                    delete_after=4)
                for cog in COGS:
                    self.unload_extension(f'lib.cogs.{cog}')
                    print(f"{cog} cog descarregado")
                await canal.send('<:oi:716439178770120754>  Terminei de fazer unload nos Cogs', delete_after=4)
                await canal.send('<:kannasip:824394648943460412>  Irei clonar o meu repositório...', delete_after=4)

                HTTPS_REMOTE_URL = ''
                DEST_NAME = rf'{unidade_local}:\Sophia\github'
                try:
                    rmtree(Path(rf'{unidade_local}:/Sophia/github'))
                except:
                    pass

                Repo.clone_from(HTTPS_REMOTE_URL, DEST_NAME)
                await canal.send('Clonado com sucesso. Atualizando os arquivos')
                try:
                    shutil.rmtree(Path(f'{unidade_local}:\Sophia\lib'))
                except:
                    pass
                try:
                    rmtree(Path(f'{unidade_local}:\Sophia\github\.git'))
                except:
                    print('Não consegui remover o .git')

                destino = Path(f'{unidade_local}:/Sophia')
                src = Path(f'{unidade_local}:/Sophia/github/')
                shutil.copytree(src, destino, dirs_exist_ok=True)
                await canal.send(
                    '<a:verificado_laranja:818165297760567336> Arquivos atualizados. Irei reiniciar o meu sistema')
                try:
                    shutil.rmtree(Path(f'{unidade_local}:/Sophia/github'))
                except:
                    print('Não consegui remover a pasta github')
                db.commit()
                await sleep(5)
                os.system(rf'python {unidade_local}:\Sophia\restart.py')
                sys.exit(1)


bot = Bot()
