#sundew is dumb
#i love suraimubugbear
#RedstonerCKZ is cool

import discord
from discord.ext import commands
import asyncio
import time
import os
import subprocess
import socket
import re
from datetime import datetime
from dotenv import load_dotenv

### SETUP ###

load_dotenv()
intents=discord.Intents.all()
client=commands.Bot(command_prefix='!', intents=intents)

### FUNCTIONS ###

def secret(secret: str):
    return os.environ.get(secret)

def alphanumericKeystroke(string):
    for i in string:
        subprocess.Popen(f"nircmd sendkey {i} press", shell=True)
        time.sleep(0.05)

def keystrokePeriod():
    subprocess.Popen(f"nircmd sendkey period press", shell=True)
    time.sleep(0.05)

def keystrokeSpace():
    subprocess.Popen(f"nircmd sendkey spc press", shell=True)
    time.sleep(0.05)

def keystrokeEnter():
    subprocess.Popen(f"nircmd sendkey enter press", shell=True)
    time.sleep(0.05)

def stopServer(server):
    if server != "MZMP":
        subprocess.Popen(f"nircmd win activate title \"{server}\"", shell=True)
        time.sleep(0.5)
        keystrokePeriod()
        alphanumericKeystroke("stop")
        keystrokeSpace()
        alphanumericKeystroke("both")
        keystrokeEnter()
        subprocess.Popen(f"nircmd win settext title \"{server}\" \"{server} (TERMINATING)\"", shell=True)
    else:
        subprocess.Popen(f"nircmd win activate title \"{server}\"", shell=True)
        alphanumericKeystroke("stop")
        keystrokeEnter()
        subprocess.Popen(f"nircmd win settext title \"{server}\" \"{server} (TERMINATING)\"", shell=True)

def terminateWindow(window):
    subprocess.Popen(f"nircmd win sendmsg title \"{window}\" 0x10 0 0", shell=True)

def maxWindow(window):
    subprocess.Popen(f"nircmd win max title \"{window}\"", shell=True)

def minWindow(window):
    subprocess.Popen(f"nircmd win min title \"{window}\"", shell=True)

def ssWindow(window, destination):
    maxWindow(window)
    time.sleep(1)
    if destination=="clipboard":
        subprocess.Popen(f"nircmd savescreenshotwin *clipboard*", shell=True)
    else:
        subprocess.Popen(f"cd {destination} && nircmd savescreenshot ssOfWindow.png", shell=True)

def ssAndHide(window, destination):
    maxWindow(window)
    time.sleep(1)
    if destination=="clipboard":
        subprocess.Popen(f"nircmd savescreenshotwin *clipboard*", shell=True)
    else:
        subprocess.Popen(f"cd {destination} && nircmd savescreenshot ssOfWindow.png", shell=True)
    time.sleep(1)
    minWindow("ZMP")

### SMS ###

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
@dataclass
class SMS:
    number: str
    gateway: str
    subject: str
    body: str
    @property
    def recipient(self) -> str: return self.number + self.gateway
@dataclass
class Messenger:
    username: str
    password: str
    conn: smtplib.SMTP=None
    def open_conn(self):
        self.conn=smtplib.SMTP("smtp.gmail.com",587)
        self.conn.ehlo()
        self.conn.starttls()
        self.conn.ehlo
        self.conn.login(self.username, self.password)
    def close_conn(self): self.conn.close()
    def send_sms(self, msg, one_time=False):
        if one_time: self.open_conn()
        message=MIMEMultipart("alternative")
        message["From"]=self.username
        message["To"]= msg.recipient
        message["Subject"]=msg.subject
        message.attach(MIMEText(msg.body, "plain"))
        self.conn.sendmail(self.username, msg.recipient, message.as_string())
        if one_time: self.close_conn()
def sendSMS(messageSubject: str, messageBody: str):
    Messenger(secret("SMSUsername"), secret("SMSPassword")).send_sms(SMS(secret("SMSNumber"), secret("SMSCarrier"), messageSubject, f"\n{messageBody}\n"), one_time=True)

### EVENTS ###

## WHITELIST CLASSES ##

class WhitelistModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(discord.ui.InputText(label="Short Input", placeholder="Minecraft username", max_length=16, min_length=3), *args, **kwargs)
    async def callback(self, interaction: discord.Interaction):
        console=client.get_channel(950858523846271007)
        for i in interaction.user.roles:
            if "Java Player" in str(i):
                await console.send(f"whitelist add {self.children[0].value}")
            if "Bedrock Player" in str(i):
                await console.send(f"whitelist add .{self.children[0].value}")
        await interaction.response.defer()
        await asyncio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
        if 'already whitelisted' in content:
            result="U/ALRWL"
        elif 'to the whitelist' in content:
            result="S"
        elif 'player does not exist' in content:
            result="U/PDNE"
        elif 'whitelist add' in content:
            result="U/ERR"
        now=datetime.now()
        dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
        date, sep, time=dateTime.partition(" ")
        f=open("LOOKUP.txt", "r")
        contents=f.read()
        f.close()
        f=open("LOOKUP.txt", "a")
        lookupLink=f"ID{interaction.user.id}-MODAL.d{date}.t{time}.r{result}.u{self.children[0].value}"
        if lookupLink not in contents:
            f.write(f"{lookupLink}, ")
        f.close()
        if result=="U/ALRWL":
            role = interaction.guild.get_role(1004204386618196089)
            await interaction.user.add_roles(role)
            await interaction.followup.send("**You're already whitelisted!**\n\nIf you are having issues with connecting to the server, ask for help in one of the help channels.", ephemeral=True)
        if result=="U/ERR":
            await interaction.followup.send("**Whoops! Looks like there was an unknown error attempting to whitelist your account!**\nPlease try again.\nIf this error message appears again, ask for help in the help channels.", ephemeral=True)
        if result=="S":
            await interaction.followup.send(f"**Thanks for playing on the ZMP!**\nYour account should now be whitelisted. If it is not, or you are having any trouble connecting, ask for help in the help channels.", ephemeral=True)
            await asyncio.sleep(10)
            role = interaction.guild.get_role(1004204386618196089)
            await interaction.user.add_roles(role)
        if result=="U/PDNE":
            if "Bedrock Player" in str(i):
                await interaction.followup.send("**Whoops! Looks like there was an error attempting to whitelist your account!**\nBecause you are trying to whitelist a bedrock edition account, try attempting to join the server. After you have tried to connect, attempt to whitelist yourself again. If this error message persists, ask for help in the help channels!\nYou entered: \"{self.children[0].value}\"", ephemeral=True)
            else:
                await interaction.followup.send(f"**Whoops! Looks like there was an error attempting to whitelist your account!**\nPlease try again.\nMake sure you entered your name correctly!\nYou entered: \"{self.children[0].value}\"", ephemeral=True)

class WhitelistView(discord.ui.View, discord.ui.Select):
    @discord.ui.select(placeholder="Select an account type", min_values=1, max_values=1, options=[discord.SelectOption(label="Java", description="Select this option if you are attempting to whitelist a Java Minecraft account."), discord.SelectOption(label="Bedrock", description="Select this option if you are attempting to whitelist a Bedrock Minecraft account.")])
    async def callback(self, select, interaction: discord.Interaction):
        modal = WhitelistModal(title=f"Enter your {select.values[0]} Minecraft account username")
        await interaction.response.send_modal(modal)
        if select.values[0] == "Java":
            role = interaction.guild.get_role(1005248117920239761)
            await interaction.user.add_roles(role)
        else:
            role = interaction.guild.get_role(1005248031513399387)
            await interaction.user.add_roles(role)

## END WHITELIST CLASSES ##

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="with myself"))
    print(f'\n\nSuccessfully logged into Discord as "{client.user}"\nAwaiting user input...')
    whitelistChannel=client.get_channel(1046540324706734290)
    await whitelistChannel.purge(limit=1)
    await whitelistChannel.send("Please select an account type below. If you do not know your account type, or it is not listed, follow the guide given below:\n\nIf you play Minecraft on a desktop computer or laptop, you likely play Minecraft **JAVA** edition.\nIf you play Minecraft on a mobile device, console, you likely play Minecraft **BEDROCK** edition.\n\nIf you are still confused, open Minecraft to the starting page. The Minecraft logo may have \"JAVA EDITION\" below it. If it does not, you play Minecraft **BEDROCK** edition.", view=WhitelistView(timeout=None))

@client.event
async def on_message(ctx):
    smpServer=784131884376391700
    smpServerChannel=1039533600330231809
    zmpServerChannel=988411334876094464
    mainServer=870964644523692053
    loggerServer=1035798849551351818
    content=ctx.content
    author=ctx.author
    fromChannel=ctx.channel
    chatLoggerSignature="**​**"
    if ctx.channel.id==1042981935712047214:
        sendSMS(messageSubject="Forwarded message from Discord", messageBody=f"{ctx.author}:\n{content}")
    messageID=f"{ctx.guild.id}-{ctx.channel.id}-{ctx.id}"
    guild=client.get_guild(loggerServer)
    if ctx.guild.id != smpServer:
        if ctx.channel.id==zmpServerChannel:
            smpGuild=client.get_guild(smpServer)
            for channel in smpGuild.channels:
                channel=client.get_channel(channel.id)
                if channel.id==smpServerChannel:
                    if " | ZMP Discord]" not in content:
                        if " | ZMP]" not in content:
                            if " | Private SMP Discord]" not in content:
                                if ctx.author.id==987755796563628052:
                                    if content=="":
                                        embeds=ctx.embeds
                                        for embed in embeds:
                                            await channel.send(embed=embed)
                                    else:
                                        await channel.send(f"**[{ctx.author} | ZMP]** {content}")
                                else:
                                    await channel.send(f"**[{ctx.author} | ZMP Discord]** {content}")
                                    for attachment in ctx.attachments:
                                        await channel.send(attachment)
    if ctx.guild.id==smpServer:
        if ctx.channel.id==smpServerChannel:
            zmpGuild=client.get_guild(mainServer)
            for channel in zmpGuild.channels:
                channel=client.get_channel(channel.id)
                if channel.id==zmpServerChannel:
                    if " | ZMP Discord]" not in content:
                        if " | ZMP]" not in content:
                            if " | Private SMP Discord]" not in content:
                                if ctx.author.id != 991054210730692738:
                                    await channel.send(f"**[{ctx.author} | Private SMP Discord]** {content}")
                                    for attachment in ctx.attachments:
                                        await channel.send(attachment)
    if ctx.guild.id==mainServer:
        if "zoe" in ctx.content.lower() and ctx.guild:
            if "~Zoe" not in ctx.content and ctx.guild:
                if "[Discord |" not in ctx.content and ctx.guild:
                    if ctx.author.id != 968356025461768192:
                        print(ctx.author.id)
                        if chatLoggerSignature not in content:
                            await client.get_user(968356025461768192).send(f"Mentioned in {ctx.channel} by {ctx.author.mention}\n\"{ctx.content}\"\nhttps://discordapp.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.id}\nㅤ")
    if ctx.guild.id==mainServer:
        for channel in guild.channels:
            toChannel=discord.utils.get(client.get_all_channels(), id=channel.id)
            if f"{fromChannel}"==f"{toChannel}":
                channel=client.get_channel(channel.id)
                if content=="":
                    embeds=ctx.embeds
                    for embed in embeds:
                        await channel.send(embed=embed)
                else:
                    if chatLoggerSignature in content:
                        if not ctx.author.bot:
                            loggerMessage=await channel.send(f"**[{author}]** -- {messageID}\n{content}")
                            for attachment in ctx.attachments:
                                await channel.send(attachment)
                            loggerMessageID=f"{loggerMessage.guild.id}-{loggerMessage.channel.id}-{loggerMessage.id}"
                            savedLog=f"M.{messageID}.L.{loggerMessageID}, "
                            f=open("LOGGER.txt", "a")
                            f.write(f"{savedLog}")
                            f.close()
                    else:
                        loggerMessage=await channel.send(f"**[{author}]** -- {messageID}\n{content}")
                        for attachment in ctx.attachments:
                            await channel.send(attachment)
                        loggerMessageID=f"{loggerMessage.guild.id}-{loggerMessage.channel.id}-{loggerMessage.id}"
                        savedLog=f"M.{messageID}.L.{loggerMessageID}, "
                        f=open("LOGGER.txt", "a")
                        f.write(f"{savedLog}")
                        f.close()
    if not ctx.author.bot:
        guild=client.get_guild(mainServer)
        if ctx.guild.id==loggerServer:
            for channel in guild.channels:
                toChannel=discord.utils.get(client.get_all_channels(), id=channel.id)
                if f"{fromChannel}"==f"{toChannel}":
                    channel=client.get_channel(channel.id)
                    if content=="":
                        embeds=ctx.embeds
                        for embed in embeds:
                            await channel.send(embed=embed)
                    else:
                        await channel.send(f"{chatLoggerSignature}{content}")
    await client.process_commands(ctx)

@client.event
async def on_message_delete(ctx):
    messageID=f"{ctx.guild.id}-{ctx.channel.id}-{ctx.id}"
    loggerServer=1035798849551351818
    content=ctx.content
    f=open("LOGGER.txt")
    contents=f.read()
    author=ctx.author
    fromChannel=ctx.channel
    loggerArray=contents.split(", ")
    for i in loggerArray:
        if messageID in i:
            guild=client.get_guild(loggerServer)
            for channel in guild.channels:
                toChannel=discord.utils.get(client.get_all_channels(), id=channel.id)
                if f"{fromChannel}"==f"{toChannel}":
                    channel=client.get_channel(channel.id)
                    channel=client.get_channel(channel.id)
                    before, sep, id=i.partition(".L.")
                    guildID, sep, channelID_messageID=id.partition("-")
                    channelID, sep, messageID=channelID_messageID.partition("-")
                    msg=await channel.fetch_message(messageID)
                    now=datetime.now()
                    dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
                    content=msg.content
                    before, sep, content=content.partition("\n")
                    await msg.edit(content=f"**[{author}]** -- **DELETED MESSAGE** -- {dateTime}\n{content}")
    f.close()

@client.event
async def on_message_edit(ctx, after):
    loggerServer=1035798849551351818
    if ctx.guild.id != loggerServer:
        messageID=f"{ctx.guild.id}-{ctx.channel.id}-{ctx.id}"
        content=ctx.content
        f=open("LOGGER.txt")
        contents=f.read()
        author=ctx.author
        fromChannel=ctx.channel
        loggerArray=contents.split(", ")
        for i in loggerArray:
            if messageID in i:
                guild=client.get_guild(loggerServer)
                for channel in guild.channels:
                    toChannel=discord.utils.get(client.get_all_channels(), id=channel.id)
                    if f"{fromChannel}"==f"{toChannel}":
                        channel=client.get_channel(channel.id)
                        channel=client.get_channel(channel.id)
                        before, sep, id=i.partition(".L.")
                        guildID, sep, channelID_messageID=id.partition("-")
                        channelID, sep, messageID=channelID_messageID.partition("-")
                        msg=await channel.fetch_message(messageID)
                        now=datetime.now()
                        dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
                        content=msg.content
                        before, sep, content=content.partition("\n")
                        editedTo=after.content
                        messageID=f"{ctx.guild.id}-{ctx.channel.id}-{ctx.id}"
                        if (f"{toChannel}" != "⚡︱console"):
                            if (f"{toChannel}" != "⚡︱modded-console"):
                                if (f"{toChannel}" != "⚡︱build-console"):
                                    await msg.edit(content=f"**[{author}]** -- {messageID} -- **EDITED MESSAGE**\n~~{content}~~\n{editedTo}  `EDIT MADE AT:  {dateTime}`")
                                else:
                                    await msg.edit(content=f"{editedTo}")
                            else:
                                await msg.edit(content=f"{editedTo}")
                        else:
                            await msg.edit(content=f"{editedTo}")
        f.close()

@client.event
async def on_guild_channel_delete(channel):
    loggerServer=1035798849551351818
    if channel.guild.id != loggerServer:
        guild=client.get_guild(loggerServer)
        channel=discord.utils.get(guild.channels, name=f"{str(channel)}")
        await channel.send("**DELETED CHANNEL**")

@client.event
async def on_guild_channel_create(channel):
    loggerServer=1035798849551351818
    if channel.guild.id != loggerServer:
        guild=client.get_guild(loggerServer)
        category=discord.utils.get(guild.categories, name=f"{str(channel.category)}")
        await guild.create_text_channel(f"{channel}", category=category)

@client.event
async def on_guild_channel_update(before, after):
    loggerServer=1035798849551351818
    guild=client.get_guild(loggerServer)
    channel=discord.utils.get(guild.channels, name=f"{str(after)}")
    category=discord.utils.get(guild.categories, name=f"{str(after.category)}")
    if before.guild.id != loggerServer:
        await channel.edit(name=f"{str(after.name)}", topic=f"{str(after.topic)}", category=category)

@client.event
async def on_member_join(member):
    channel=client.get_channel(id=870965737613828136)
    await channel.send(f"Welcome to the ZMP, {member.mention}!")
    channel=client.get_channel(id=870977081717170206)
    await channel.send(f"{member.mention} joined")
    role=discord.utils.get(client.guild.roles, id=1005258287442309224)
    member.add_roles(role)
    print(f"{member} joined")
    #not found
    f=open("LOOKUP.txt")
    contents=f.read().lower()
    contents=contents.split(", ")
    for i in contents:
        if member.id in i:
            found=True
            notFound=False
            rawData=i
        else:
            notFound=True
    if notFound==True:
        if found==False:
            pass
    if found==True:
        console=client.get_channel(950858523846271007)
        before, sep, user=rawData.partition(".u")
        await console.send(f"whitelist add {user}")
        role=discord.utils.get(client.guild.roles, id=1004204386618196089)
        member.add_roles(role)
        role=discord.utils.get(client.guild.roles, id=1005254886142787696)
        member.add_roles(role)
        role=discord.utils.get(client.guild.roles, id=1005258287442309224)
        member.remove_roles(role)
    f.close()

@client.event
async def on_member_remove(member):
    channel=client.get_channel(id=870977081717170206)
    await channel.send(f"{member.mention} left")
    print(f"{member} left")
    f=open("LOOKUP.txt")
    contents=f.read().lower()
    contents=contents.split(", ")
    for i in contents:
        if member.id in i:
            found=True
            notFound=False
            rawData=i
        else:
            notFound=True
    if notFound==True:
        if found==False:
            print(f"{member} was never whitelisted, and therefore could not be unwhitelisted.")
    if found==True:
        console=client.get_channel(950858523846271007)
        before, sep, user=rawData.partition(".u")
        await console.send(f"whitelist remove {user}")
    f.close()

### DISCORD ###

@client.command()
@commands.has_any_role("Owner", "Admin")
async def reload(ctx):
    def check_rule(message: discord.Message):
        return message.author.id==ctx.message.author.id
    channel=ctx.channel
    emb=discord.Embed(color=discord.Color.orange(), title="**Reload Bot?**", description=f"Are you sure you want to reload this bot?\nTo continue with reload, type 'yes'.\nTo cancel the reload, type 'no'.")
    await channel.send(embed=emb)
    try:
        answer=(await client.wait_for('message', check=check_rule, timeout=20)).content
    except (asyncio.exceptions.TimeoutError, discord.ext.commands.errors.CommandInvokeError):
        await ctx.send("Took too long to answer. Reload canceled")
        return
    if answer=='yes':
        if ctx.author.id != 968356025461768192:
            now=datetime.now()
            dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
            date, sep, time=dateTime.partition(" ")
            sendSMS(messageSubject="ZMP ALERT", messageBody=f"{date} | {time}\n\nTag: {ctx.author} | ID: {ctx.author.id} | Name: {ctx.author.nick}\n\nUser issued command:\n\"{ctx.message.content}\"")
        channel=ctx.channel
        emb=discord.Embed(color=discord.Color.red(), title="**Reloading**", description=f"Starting new instance...")
        await channel.send(embed=emb)
        path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\bot\\main.py"
        subprocess.Popen(f"start cmd /k \"python3 {path}\"", shell=True)
        print("\nBot reloaded")
        await client.close()
        exit()
    elif answer=='no':
        channel=ctx.channel
        emb=discord.Embed(color=discord.Color.green(), title="**Reload Canceled**", description=f"You canceled the reload process")
        await channel.send(embed=emb)
    else:
        channel=ctx.channel
        emb=discord.Embed(color=discord.Color.green(), title="**Reload Canceled**", description=f"Invalid input. Reload canceled.")
        await channel.send(embed=emb)

@client.slash_command()
@commands.has_any_role("Owner", "Admin")
async def create_whitelist_option(ctx: discord.ApplicationContext):
    await ctx.send("Please select an account type below. If you do not know your account type, or it is not listed, follow the guide given below:\n\nIf you play Minecraft on a desktop computer or laptop, you likely play Minecraft **JAVA** edition.\nIf you play Minecraft on a mobile device, console, you likely play Minecraft **BEDROCK** edition.\n\nIf you are still confused, oprn Minecraft to the starting page. The Minecraft logo may have \"JAVA EDITION\" below it. If it does not, you play Minecraft **BEDROCK** edition.", view=WhitelistView(timeout=None))

@client.command()
async def ip(ctx):
    await ctx.send("play.zmp.lol")

@client.command()
async def hurt(ctx, *, user):
    await ctx.send(f"{user} rn:")
    await ctx.send("https://tenor.com/view/parks-and-rec-ron-swanson-screaming-scream-screams-gif-21763857")

@client.command()
async def link(ctx):
    await ctx.send("https://discord.gg/zmp")
    
@client.command()
async def invite(ctx):
    await ctx.send("https://discord.gg/zmp")

@client.command()
@commands.has_any_role("Owner", "Admin", "Moderator")
async def suspend(ctx, user: discord.Member=None, revoke=""):
    suspendedRole=discord.utils.get(ctx.message.guild.roles, id=1009836529146921070)
    if revoke.lower()=="off":
        f=open(f"{user.id}_roles.txt")
        if f.mode=='r':
            contents=f.read()
            roles=contents.split(", ")
            for i in roles:
                await user.add_roles(discord.utils.get(ctx.message.guild.roles, name=f'{i}'))
            await user.remove_roles(discord.utils.get(ctx.message.guild.roles, name=f'SUSPENDED'))
            print(f"\n{ctx.author} ended {user}'s suspention\n")
        f.close()
    else:
        if ctx.author.top_role <= user.top_role:
            await ctx.send(f"You cannot suspend that user")
        elif suspendedRole not in user.roles:
            await ctx.send(f"{user} was suspended")
            f=open(f"{user.display_name}_roles.txt", "w+")
            userRoles=user.roles
            userArray=""
            for i in userRoles:
                userArray=f"{userArray}, {i}"
            userArray=userArray[2:].split(", ")
            userArray=str(userArray)
            before, sep, userArray=userArray.partition("['@everyone', '")
            userArray, sep, after=userArray.partition("']")
            userArray=userArray.replace("'", "")
            f.write(f"{userArray}")
            f.close()
            userArray=userArray.split(", ")
            for i in userArray:
                await user.remove_roles(discord.utils.get(ctx.message.guild.roles, name=f'{i}'))
            await user.add_roles(discord.utils.get(ctx.message.guild.roles, name=f'SUSPENDED'))
            print(f"\n{ctx.author} suspended {user}\n")
        else:
            await ctx.send(f"{user} is already suspended.")

@client.command()
@commands.has_any_role("Owner", "Admin", "Moderator")
async def lookup(ctx, user, mode="generic"):
    if (mode!="generic") and not (ctx.author.top_role > discord.utils.get(ctx.message.guild.roles, name=f'Moderator')):
        await ctx.send("You do not have permission to use that subcommand")
    if mode=="generic":
        user=user.lower()
        f=open("LOOKUP.txt")
        contents=f.read().lower()
        found=False
        notFound=True
        contents=contents.split(", ")
        for i in contents:
            if user in i:
                found=True
                notFound=False
                rawData=i
            else:
                notFound=True
        if notFound==True:
            if found==False:
                await ctx.send("FOUND NO POSSIBLE CORRELATION")
        if found==True:
            console=client.get_channel(950858523846271007)
            before, sep, link1=rawData.partition("-")
            link1, sep, link2=link1.partition("-")
            link2, sep, link3=link2.partition("-")
            link3, sep, after=link3.partition(".d")
            link=f"https://discord.com/channels/{link1}/{link2}/{link3}"
            if link3=="message_id_get_err":
                link=f"Error fetching message link:\n{link}"
            before, sep, userID=rawData.partition("id")
            userID, sep, after=userID.partition("-")
            before, sep, date=rawData.partition(".d")
            date, sep, after=date.partition(".t")
            before, sep, time=rawData.partition(".t")
            time, sep, after=time.partition(".r")
            before, sep, result=rawData.partition(".r")
            result, sep, after=result.partition(".u")
            before, sep, user=rawData.partition(".u")
            userName=await client.fetch_user(userID)
            await console.send(f"seen {user}")
            await asyncio.sleep(2)
            content=(await console.history(limit=1).flatten())[0].content
            result=result.upper()
            if result=="U/ALRWL":
                result="Already whitelisted"
            if result=="U/PDNE":
                result="Player does not exist"
            if result=="U/ERR":
                result="Unknown error"
            if result=="S":
                result="Success"
            if "/seen" in content:
                if "was never on this server" not in content:
                    before, sep, uuid=content.partition("UUID: ")
                    uuid, sep, after=uuid.partition("\n")
                    before, sep, location=content.partition("Location: ")
                    location, sep, after=location.partition("```")
                    if "Player has also been known as: " in content:
                        before, sep, knownAs=content.partition("Player has also been known as: ")
                        knownAs, sep, after=knownAs.partition("\n  [")
                    if "offline" in content:
                        before, sep, session=content.partition(" has been offline since ")
                        session, sep, after=session.partition(".")
                        session=f"offline for {session}"
                        await ctx.send(f"FOUND POSSIBLE CORRELATION:\n`Discord ID: {userID}`\n`Discord Name: {userName}`\n`Minecraft Name: {user}`\n`Minecraft UUID: {uuid}`\n`Log off location: {location}`\n`Session: {session}`\n`Whitelist date: {date}`\n`Whitelist time: {time}`\n`Result of whitelist attempt: {result}`\n```{rawData}```\n{link}")
                    if "online" in content:
                        before, sep, session=content.partition(" has been online since ")
                        session, sep, after=session.partition(".")
                        session=f"online for {session}"
                        await console.send(f"coords {user}")
                        await asyncio.sleep(2)
                        content=(await console.history(limit=1).flatten())[0].content
                        before, sep, world=content.partition("Current World: ")
                        world, sep, after=world.partition("\n")
                        before, sep, x=content.partition("X: ")
                        x, sep, after=x.partition(" ")
                        before, sep, y=content.partition("Y: ")
                        y, sep, after=y.partition(" ")
                        before, sep, z=content.partition("Z: ")
                        z, sep, after=z.partition(" ")
                        location=f"({world}, {x}, {y}, {z})"
                        await ctx.send(f"FOUND POSSIBLE CORRELATION:\n`Discord ID: {userID}`\n`Discord Name: {userName}`\n`Minecraft Name: {user}`\n`Minecraft UUID: {uuid}`\n`Location: {location}`\n`Session: {session}`\n`Date: {date}`\n`Time: {time}`\n`Result of command: {result}`\n```{rawData}```\n{link}")
                else:
                    await ctx.send(f"FOUND POSSIBLE CORRELATION:\n`Discord ID: {userID}`\n`Discord Name: {userName}`\n`Minecraft Name: {user}`\n`Date: {date}`\n`Time: {time}`\n`Result of command: {result}`\n```{rawData}```\n{link}")
            else:
                await ctx.send(f"FOUND POSSIBLE CORRELATION:\n`Discord ID: {userID}`\n`Discord Name: {userName}`\n`Minecraft Name: {user}`\n`Date: {date}`\n`Time: {time}`\n`Result of command: {result}`\n```{rawData}```\n{link}")
        f.close()

@client.command()
@commands.has_any_role("Owner")
async def verify(ctx):
    role=discord.utils.get(ctx.message.guild.roles, id=1005254886142787696)
    for m in ctx.message.guild.members:
        await m.add_roles(role)
        print(f"\n\n\nVerified {m}\n\n\n")

@client.command()
@commands.has_any_role("Owner", "Admin", "Moderator")
async def ping(ctx):
    await ctx.send(f'Pong!\n{round(client.latency * 1000)}ms')
    print(f'\nBot pinged. {round(client.latency * 1000)}ms is the current ping time between "{client.user}" and Discord Services.')

@client.command()
@commands.has_any_role("Owner", "Moderator", "Admin")
async def purge(ctx, limit=50, member: discord.Member=None):
    await ctx.message.delete()
    msg=[]
    try:
        limit=int(limit)
    except:
        return await ctx.send("You didn't specify a limit")
    if not member:
        await ctx.channel.purge(limit=limit)
        print(f'\n{limit} messages were deleted using the purge command.')
        return await ctx.send(f"{ctx.author} purged {limit} messages", delete_after=3)
    async for m in ctx.channel.history():
        if len(msg)==limit:
            break
        if m.author==member:
            msg.append(m)
    await ctx.channel.delete_messages(msg)
    print(f"\n{limit} of {member}'s messages were deleted by {ctx.author} via the purge command.")
    await ctx.send(f"Purged {limit} of {member.mention}'s messages.", delete_after=3)

@client.command()
@commands.has_any_role("Owner", "Admin", "Moderator")
async def kick(ctx, member: discord.Member, *, reason=None):
    if ctx.author.top_role > member.top_role:
        await member.kick(reason=reason)
        await ctx.message.delete()
        emb=discord.Embed(color=discord.Color.green(), title="**User kicked**", description=f"User {member} was kicked by {ctx.author} with reason:\n{reason}.")
        await ctx.send(embed=emb)
        id=ctx.author.id
        user=client.get_user(id)
        await member.send(f'You were kicked from the server by {user}.\nReason: {reason}')
    else:
        await ctx.send(f'You cannot kick that user.')

@client.command()
@commands.has_any_role("Owner", "Admin", "Moderator")
async def ban(ctx, member: discord.Member, *, reason=None):
    if ctx.author.top_role > member.top_role:
        await member.ban(reason=reason)
        emb=discord.Embed(color=discord.Color.green(), title="**User banned**", description=f"User {member} was banned by {ctx.author} with reason:\n{reason}.")
        await ctx.send(embed=emb)
        id=ctx.author.id
        user=client.get_user(id)
        await member.send(f'You were banned from the server by {user}.\nReason: {reason}.')
    else:
        await ctx.send(f'You cannot ban that user.')

@client.command()
@commands.has_any_role("Owner", "Admin")
async def unban(ctx, *, member):
    memberName, memberNumber=member.split('# ')
    bannedUsers=await ctx.guild.bans()
    for ban_entry in bannedUsers:
        user=ban_entry.user
        if (user.name, user.discriminator)==(memberName, memberNumber):
            await ctx.guild.unban(user)
            await ctx.channel.send(f'A user was unbanned.')
            return

@client.command()
@commands.has_any_role("Owner", "Admin")
async def kill(ctx):
    def check_rule(message: discord.Message):
        return message.author.id==ctx.message.author.id
    channel=ctx.channel
    emb=discord.Embed(color=discord.Color.orange(), title="**Terminate Bot?**", description=f"Are you sure you want to terminate this bot?\nTo continue with termination, type 'yes'.\nTo cancel the termination, type 'no'.")
    await channel.send(embed=emb)
    try:
        answer=(await client.wait_for('message', check=check_rule, timeout=20)).content
    except (asyncio.exceptions.TimeoutError, discord.ext.commands.errors.CommandInvokeError):
        await ctx.send("Took too long to answer. Termination canceled")
        return
    if answer=='yes':
        if ctx.author.id != 968356025461768192:
            now=datetime.now()
            dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
            date, sep, time=dateTime.partition(" ")
            sendSMS(messageSubject="ZMP ALERT", messageBody=f"{date} | {time}\n\nTag: {ctx.author} | ID: {ctx.author.id} | Name: {ctx.author.nick}\n\nUser issued command:\n\"{ctx.message.content}\"")
        channel=ctx.channel
        emb=discord.Embed(color=discord.Color.red(), title="**Terminating**", description=f"Process terminating...")
        await channel.send(embed=emb)
        await client.close()
        print("\nBot terminated")
    elif answer=='no':
        channel=ctx.channel
        emb=discord.Embed(color=discord.Color.green(), title="**Termination Canceled**", description=f"You canceled the termination process")
        await channel.send(embed=emb)
    else:
        channel=ctx.channel
        emb=discord.Embed(color=discord.Color.green(), title="**Termination Canceled**", description=f"Invalid input. Termination canceled.")
        await channel.send(embed=emb)

@client.command()
async def membercount(ctx):
    humanCount=len([m for m in ctx.guild.members if not m.bot])
    botCount=len([m for m in ctx.guild.members if m.bot])
    total=len([m for m in ctx.guild.members])
    channel=ctx.channel
    await channel.send(f"**ZMP member count**\nHumans:{humanCount}\nBots: {botCount}\nTotal: {total}")

@client.command()
@commands.is_owner()
async def terminal(ctx, mode, *, command):
    if mode=="window":
        subprocess.Popen(f"start cmd /k \"{command}\"", shell=True)
    if mode=="output":
        output=os.popen(f'{command}').read()
        await ctx.send(f"```{output}```")

### ZMP ###

@client.command()
@commands.has_any_role("Owner", "Admin", "Moderator")
async def co(ctx, *, params):
    console=client.get_channel(950858523846271007)
    def check(m: discord.Message):
        return m.channel.id=="950858523846271007"
    command="co"
    if params.lower().startswith("lookup") or params.lower().startswith("l"):
        command="co l"
        if "action:" in params.lower():
            before, sep, add=params.lower().partition("action:")
            add, sep, after=add.partition(" ")
            command=f"{command} action:{add}"
        if "include:" in params.lower():
            before, sep, add=params.lower().partition("include:")
            add, sep, after=add.partition(" ")
            command=f"{command} include:{add}"
        if "radius:" in params.lower():
            before, sep, add=params.lower().partition("radius:")
            add, sep, after=add.partition(" ")
            command=f"{command} radius:{add}"
        if "time:" in params.lower():
            before, sep, add=params.lower().partition("time:")
            add, sep, after=add.partition(" ")
            command=f"{command} time:{add}"
        if "user:" in params.lower():
            before, sep, add=params.lower().partition("user:")
            add, sep, after=add.partition(" ")
            command=f"{command} user:{add}"
    elif params.lower().startswith("rollback"):
        command="co rollback"
        if "action:" in params.lower():
            before, sep, add=params.lower().partition("action:")
            add, sep, after=add.partition(" ")
            command=f"{command} action:{add}"
        if "include:" in params.lower():
            before, sep, add=params.lower().partition("include:")
            add, sep, after=add.partition(" ")
            command=f"{command} include:{add}"
        if "radius:" in params.lower():
            before, sep, add=params.lower().partition("radius:")
            add, sep, after=add.partition(" ")
            command=f"{command} radius:{add}"
        if "time:" in params.lower():
            before, sep, add=params.lower().partition("time:")
            add, sep, after=add.partition(" ")
            command=f"{command} time:{add}"
        if "user:" in params.lower():
            before, sep, add=params.lower().partition("user:")
            add, sep, after=add.partition(" ")
            command=f"{command} user:{add}"
    elif params.lower().startswith("purge"):
        before, sep, user=params.lower().partition("purge ")
        command=f"co rollback {user} t:9w r:#global"
    await console.send(command)
    await asyncio.sleep(2)
    content=(await console.history(limit=1).flatten())[0].content
    if content.lower().startswith("co"):
        await asyncio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
    if content.lower().startswith("co"):
        await asyncio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
    if content.lower().startswith("co"):
        await asyncio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
    await ctx.send(content)

@client.command()
@commands.has_any_role("Owner", "Admin")
async def stop(ctx):
    console=client.get_channel(950858523846271007)
    await console.send("stop")
    stopServer("ZMP")

@client.command()
@commands.has_any_role("Owner", "Admin")
async def estop(ctx, server):
    def check_rule(message: discord.Message):
        return message.author.id==ctx.message.author.id
    channel=ctx.channel
    emb=discord.Embed(color=discord.Color.orange(), title="**Terminate Server?**", description=f"**WARNING**: Terminating this server may result in **corrupt world files**. It is recommended you use !stop instead of !estop. Do you wish to proceed?\nTo continue with termination, type 'yes'.\nTo cancel the termination, type 'no'.")
    await channel.send(embed=emb)
    try:
        answer=(await client.wait_for('message', check=check_rule, timeout=20)).content
    except (asyncio.exceptions.TimeoutError, discord.ext.commands.errors.CommandInvokeError):
        await ctx.send("Took too long to answer. Termination canceled")
        return
    if answer=='yes':
        channel=ctx.channel
        emb=discord.Embed(color=discord.Color.red(), title="**Terminating**", description=f"Process terminating...")
        await channel.send(embed=emb)
        terminateWindow(server)
        if ctx.author.id != 968356025461768192:
            now=datetime.now()
            dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
            date, sep, time=dateTime.partition(" ")
            sendSMS(messageSubject="ZMP ALERT", messageBody=f"{date} | {time}\n\nTag: {ctx.author} | ID: {ctx.author.id} | Name: {ctx.author.nick}\n\nUser issued command:\n\"{ctx.message.content}\"")
    elif answer=='no':
        channel=ctx.channel
        emb=discord.Embed(color=discord.Color.green(), title="**Termination Canceled**", description=f"You canceled the termination process")
        await channel.send(embed=emb)
    else:
        channel=ctx.channel
        emb=discord.Embed(color=discord.Color.green(), title="**Termination Canceled**", description=f"Invalid input. Termination canceled.")
        await channel.send(embed=emb)

@client.command()
@commands.has_any_role("Owner", "Admin", "Moderator", "Helper")
async def status(ctx):
    path=(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\public")
    ssAndHide("ZMP", f"{path}")
    console=client.get_channel(950858523846271007)
    await ctx.send("Diagnosing...")
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result=sock.connect_ex(('127.0.0.1',25565))
    if result==0:
        await ctx.send("ㅤ\nServer open on local host")
        sock.close()
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip=socket.gethostbyname("play.zmp.lol")
        result=sock.connect_ex((ip,25565))
        if result==0:
            await ctx.send("ㅤ\nServer domain response check passed")
            await console.send("ping")
            await asyncio.sleep(2)
            content=(await console.history(limit=1).flatten())[0].content
            if content != "ping" and "```" in content:
                await ctx.send("ㅤ\nDiscordSRV console response check passed")
            else:
                await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                await asyncio.sleep(2)
                content=(await console.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await asyncio.sleep(2)
                    content=(await console.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed")
        else:
            await ctx.send("ㅤ\nServer domain response check failed")
    else:
        await ctx.send("ㅤ\nServer is not open on local host")
        await ctx.send("ㅤ\n**SERVER OFFLINE**")
    await ctx.send(file=discord.File(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\public\ssOfWindow.png"))
    os.remove(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\public\ssOfWindow.png")

@client.command()
@commands.has_any_role("Owner", "Admin", "Moderator")
async def start(ctx):
    console=client.get_channel(950858523846271007)
    await ctx.send("Diagnosing issue...")
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result=sock.connect_ex(('127.0.0.1',25565))
    if result==0:
        await ctx.send("ㅤ\nServer open on local host")
        sock.close()
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip=socket.gethostbyname("play.zmp.lol")
        result=sock.connect_ex((ip,25565))
        if result==0:
            await ctx.send("ㅤ\nServer domain response check passed")
            await console.send("ping")
            await asyncio.sleep(2)
            content=(await console.history(limit=1).flatten())[0].content
            if content != "ping" and "```" in content:
                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                await ctx.send("ㅤ\nServer is running")
                await ctx.send("ㅤ\nNo issues found")
                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
            else:
                await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                await asyncio.sleep(2)
                content=(await console.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    await ctx.send("ㅤ\nServer is running")
                    await ctx.send("ㅤ\nNo issues found")
                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await asyncio.sleep(2)
                    content=(await console.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed.")
                        role=discord.utils.find(lambda r: r.name=='Owner', ctx.message.guild.roles)
                        if role not in ctx.author.roles:
                            await ctx.send("ㅤ\nAlerting owner...")
                            user=client.get_user(968356025461768192)
                            msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
                            before, sep, msg=str(msg).partition("<Message id=")
                            msg, sep, after=str(msg).partition(" channel=<")
                            msg=await ctx.channel.fetch_message(msg)
                            for i in range(10):
                                n=(i * 10)
                                await msg.edit(content=f"ㅤ\nAlerting owner... {n}%")
                                await user.send(f"Server is offline")
                            await msg.edit(content=f"ㅤ\nAlerting owner... 100%")
                            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
        else:
            await ctx.send("ㅤ\nServer domain response check failed")
            await ctx.send("ㅤ\nStarting Dynamic IP address updater...")
            os.startfile(r"C:\Users\Overdrive\Desktop\apps\DDNS.exe")
    else:
        await ctx.send("ㅤ\nServer is not open on local host")
        await ctx.send("ㅤ\nStarting server...")
        path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\public\\1--START.cmd"
        subprocess.Popen(f"start /wait cmd /c {path}1--START.cmd", shell=True)
        await ctx.send("ㅤ\nServer startup initiated")
        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
        if ctx.author.id != 968356025461768192:
            now=datetime.now()
            dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
            date, sep, time=dateTime.partition(" ")
            sendSMS(messageSubject="ZMP ALERT", messageBody=f"{date} | {time}\n\nTag: {ctx.author} | ID: {ctx.author.id} | Name: {ctx.author.nick}\n\nUser issued command:\n\"{ctx.message.content}\"")
    sock.close()

'''
@client.command()
async def whitelist(ctx, version, *, tag):
    if ctx.channel.id==989939438824071178:
        if version.lower()=="java":
            command=f"whitelist add {tag}"
        elif version.lower()=="bedrock":
            bTag=tag.replace(" ", "_")
            command=f"whitelist add .{bTag}"
        await asyncio.sleep(2)
        console=client.get_channel(950858523846271007)
        await console.send(command)
        content=(await console.history(limit=1).flatten())[0].content
        if 'already whitelisted' in content:
            result="U/ALRWL"
            if version.lower()=="java":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
            elif version.lower()=="bedrock":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
            await ctx.message.add_reaction("✅")
            await ctx.message.add_reaction("⚠️")
            now=datetime.now()
            dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
            date, sep, time=dateTime.partition(" ")
            f=open("LOOKUP.txt", "r")
            contents=f.read()
            f.close()
            f=open("LOOKUP.txt", "a")
            lookupLink=f"ID{ctx.author.id}-{ctx.guild.id}-{ctx.channel.id}-{ctx.message.id}.d{date}.t{time}.r{result}.u{tag}"
            if lookupLink not in contents:
                f.write(f"{lookupLink}, ")
            f.close()
            member=ctx.message.author
            role=discord.utils.get(ctx.message.guild.roles, id=1004204386618196089)
            await member.add_roles(role)
            await ctx.author.send("**You're already whitelisted!**\n\nIf you are having issues with connecting to the server, ask for help in one of the help channels.")
        elif 'to the whitelist' in content:
            result="S"
            if version.lower()=="java":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
            elif version.lower()=="bedrock":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
            await ctx.message.add_reaction("✅")
            now=datetime.now()
            dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
            date, sep, time=dateTime.partition(" ")
            f=open("LOOKUP.txt", "r")
            contents=f.read()
            f.close()
            f=open("LOOKUP.txt", "a")
            lookupLink=f"ID{ctx.author.id}-{ctx.guild.id}-{ctx.channel.id}-{ctx.message.id}.d{date}.t{time}.r{result}.u{tag}"
            if lookupLink not in contents:
                f.write(f"{lookupLink}, ")
            f.close()
            member=ctx.message.author
            role=discord.utils.get(ctx.message.guild.roles, id=1004204386618196089)
            await member.add_roles(role)
        elif 'player does not exist' in content:
            result="U/PDNE"
            await ctx.author.send("**That didnt work!**\n\nBe sure you entered the right tag, including capitalization!\nIf you are trying to join on bedrock, try to join before trying to whitelist yourself!")
            await ctx.message.add_reaction("❌")
            now=datetime.now()
            dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
            date, sep, time=dateTime.partition(" ")
            f=open("LOOKUP.txt", "r")
            contents=f.read()
            f.close()
            f=open("LOOKUP.txt", "a")
            lookupLink=f"ID{ctx.author.id}-{ctx.guild.id}-{ctx.channel.id}-{ctx.message.id}.d{date}.t{time}.r{result}.u{tag}"
            if lookupLink not in contents:
                f.write(f"{lookupLink}, ")
            f.close()
            if version.lower()=="java":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
            elif version.lower()=="bedrock":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
        elif 'whitelist add' in content:
            result="U/ERR"
            await asyncio.sleep(2)
            content=(await console.history(limit=1).flatten())[0].content
            if 'already whitelisted' in content:
                result="U/ALRWL"
                if version.lower()=="java":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
                elif version.lower()=="bedrock":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
                await ctx.message.add_reaction("✅")
                await ctx.message.add_reaction("⚠️") 
                now=datetime.now()
                dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
                date, sep, time=dateTime.partition(" ")
                f=open("LOOKUP.txt", "r")
                contents=f.read()
                f.close()
                f=open("LOOKUP.txt", "a")
                lookupLink=f"ID{ctx.author.id}-{ctx.guild.id}-{ctx.channel.id}-{ctx.message.id}.d{date}.t{time}.r{result}.u{tag}"
                if lookupLink not in contents:
                    f.write(f"{lookupLink}, ")
                f.close()
                member=ctx.message.author
                role=discord.utils.get(ctx.message.guild.roles, id=1004204386618196089)
                await member.add_roles(role)
                await ctx.author.send("**You're already whitelisted!**\n\nIf you are having issues with connecting to the server, ask for help in one of the help channels.")
            elif 'to the whitelist' in content:
                result="S"
                if version.lower()=="java":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
                elif version.lower()=="bedrock":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
                await ctx.message.add_reaction("✅")
                now=datetime.now()
                dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
                date, sep, time=dateTime.partition(" ")
                f=open("LOOKUP.txt", "r")
                contents=f.read()
                f.close()
                f=open("LOOKUP.txt", "a")
                lookupLink=f"ID{ctx.author.id}-{ctx.guild.id}-{ctx.channel.id}-{ctx.message.id}.d{date}.t{time}.r{result}.u{tag}"
                if lookupLink not in contents:
                    f.write(f"{lookupLink}, ")
                f.close()
                member=ctx.message.author
                role=discord.utils.get(ctx.message.guild.roles, id=1004204386618196089)
                await member.add_roles(role)
            elif 'player does not exist' in content:
                result="U/PDNE"
                await ctx.author.send("**That didnt work!**\n\nBe sure you entered the right tag, including capitalization!\nIf you are trying to join on bedrock, try to join before trying to whitelist yourself!")
                await ctx.message.add_reaction("❌") 
                now=datetime.now()
                dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
                date, sep, time=dateTime.partition(" ")
                f=open("LOOKUP.txt", "r")
                contents=f.read()
                f.close()
                f=open("LOOKUP.txt", "a")
                lookupLink=f"ID{ctx.author.id}-{ctx.guild.id}-{ctx.channel.id}-{ctx.message.id}.d{date}.t{time}.r{result}.u{tag}"
                if lookupLink not in contents:
                    f.write(f"{lookupLink}, ")
                f.close()
                if version.lower()=="java":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
                elif version.lower()=="bedrock":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
            elif 'whitelist add' in content:
                result="U/ERR"
                await asyncio.sleep(4)
                content=(await console.history(limit=1).flatten())[0].content
                if 'already whitelisted' in content:
                    result="U/ALRWL"
                    if version.lower()=="java":
                        print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
                    elif version.lower()=="bedrock":
                        print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
                    await ctx.message.add_reaction("✅")
                    member=ctx.message.author
                    role=discord.utils.get(ctx.message.guild.roles, id=1004204386618196089)
                    await member.add_roles(role)
                    await ctx.message.add_reaction("⚠️")               
                    now=datetime.now()
                    dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
                    date, sep, time=dateTime.partition(" ")
                    f=open("LOOKUP.txt", "r")
                    contents=f.read()
                    f.close()
                    f=open("LOOKUP.txt", "a")
                    lookupLink=f"ID{ctx.author.id}-{ctx.guild.id}-{ctx.channel.id}-{ctx.message.id}.d{date}.t{time}.r{result}.u{tag}"
                    if lookupLink not in contents:
                        f.write(f"{lookupLink}, ")
                    f.close()
                    await ctx.author.send("**You're already whitelisted!**\n\nIf you are having issues with connecting to the server, ask for help in one of the help channels.")
                elif 'to the whitelist' in content:
                    result="S"
                    if version.lower()=="java":
                        print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
                    elif version.lower()=="bedrock":
                        print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
                    await ctx.message.add_reaction("✅")
                    now=datetime.now()
                    dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
                    date, sep, time=dateTime.partition(" ")
                    f=open("LOOKUP.txt", "r")
                    contents=f.read()
                    f.close()
                    f=open("LOOKUP.txt", "a")
                    lookupLink=f"ID{ctx.author.id}-{ctx.guild.id}-{ctx.channel.id}-{ctx.message.id}.d{date}.t{time}.r{result}.u{tag}"
                    if lookupLink not in contents:
                        f.write(f"{lookupLink}, ")
                        f.close()
                    member=ctx.message.author
                    role=discord.utils.get(ctx.message.guild.roles, id=1004204386618196089)
                    await member.add_roles(role)
                elif 'player does not exist' in content:
                    result="U/PDNE"
                    await ctx.author.send("**That didnt work!**\n\nBe sure you entered the right tag, including capitalization!\nIf you are trying to join on bedrock, try to join before trying to whitelist yourself!")
                    await ctx.message.add_reaction("❌")
                    now=datetime.now()
                    dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
                    date, sep, time=dateTime.partition(" ")
                    f=open("LOOKUP.txt", "r")
                    contents=f.read()
                    f.close()
                    f=open("LOOKUP.txt", "a")
                    lookupLink=f"ID{ctx.author.id}-{ctx.guild.id}-{ctx.channel.id}-{ctx.message.id}.d{date}.t{time}.r{result}.u{tag}"
                    if lookupLink not in contents:
                        f.write(f"{lookupLink}, ")
                        f.close()
                    if version.lower()=="java":
                        print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
                    elif version.lower()=="bedrock":
                        print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
                elif 'whitelist add' in content:
                    result="U/ERR"
                    await ctx.message.add_reaction("❌")
                    now=datetime.now()
                    dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
                    date, sep, time=dateTime.partition(" ")
                    f=open("LOOKUP.txt", "r")
                    contents=f.read()
                    f.close()
                    f=open("LOOKUP.txt", "a")
                    lookupLink=f"ID{ctx.author.id}-{ctx.guild.id}-{ctx.channel.id}-{ctx.message.id}.d{date}.t{time}.r{result}.u{tag}"
                    if lookupLink not in contents:
                        f.write(f"{lookupLink}, ")
                        f.close()
                    await ctx.author.send("Sorry, but you were unable to be whitelisted at this time. Please contact Zoe for further information.")
                    if version.lower()=="java":
                        print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - unknown error\n----WHITELIST----\n\n")
                    elif version.lower()=="bedrock":
                        print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - unknown error\n----WHITELIST----\n\n")
'''

@client.command()
@commands.has_any_role("Owner", "Admin", "luckperms", "Moderator", "Head Moderator", "Helper", "Staff")
async def vip(ctx, user):
    console=client.get_channel(950858523846271007)
    await console.send(f"eplaytime {user}")
    await asyncio.sleep(4)
    content=(await console.history(limit=1).flatten())[0].content
    if "week" in content:
        await console.send(f"lp user {user} group add superstar")
        await ctx.send(f"{user} is now a SUPERSTAR!")
    elif "day" in content and "hour" in content:
        days, sep, after=content.partition("days")
        before, sep, days=days.partition(f"Playtime of ")
        before, sep, days=days.partition(f": ")
        hours, sep, after=content.partition("hours")
        before, sep, hours=hours.partition(f"Playtime of ")
        before, sep, hours=hours.partition(f"days ")
        if int(days) >= 4 and int(hours) >= 4 and int(days) < 5:
            await console.send(f"lp user {user} group add superstar")
            await ctx.send(f"{user} is now a SUPERSTAR!")
        if int(days) >= 5:
            await console.send(f"lp user {user} group add superstar")
            await ctx.send(f"{user} is now a SUPERSTAR!")
        if int(days) >= 2 and int(hours) >= 2:
            await console.send(f"lp user {user} group add star")
            await ctx.send(f"{user} is now a STAR!")
        if int(days)==1 and int(hours) < 2:
            await console.send(f"lp user {user} group add vip+")
            await ctx.send(f"{user} is now a VIP+!")
    elif "day" in content and "hour" not in content:
        days, sep, after=content.partition("days")
        before, sep, days=days.partition(f"Playtime of ")
        before, sep, days=days.partition(f": ")
        if int(days) >= 5:
            await console.send(f"lp user {user} group add superstar")
            await ctx.send(f"{user} is now a SUPERSTAR!")
        if int(days) >= 3 and int(days) < 5:
            await console.send(f"lp user {user} group add star")
            await ctx.send(f"{user} is now a STAR!")
        if int(days) >= 1 and int(days) < 3:
            await console.send(f"lp user {user} group add vip+")
            await ctx.send(f"{user} is now a VIP+!")
    elif "hours" in content and "day" not in content:
        hours, sep, after=content.partition("hours")
        before, sep, hours=hours.partition(f"Playtime of ")
        before, sep, hours=hours.partition(f": ")
        if "minutes" in content:
            minutes, sep, after=content.partition(" minute")
            before, sep, minutes=minutes.partition("hour")
            before, sep, minutes=minutes.partition(" ")
            if int(hours) >= 10 and int(hours) < 20:
                await console.send(f"lp user {user} group add vip")
                await ctx.send(f"{user} is now a VIP!")
            elif int(hours) >= 20 and int(hours) < 50:
                await console.send(f"lp user {user} group add vip+")
                await ctx.send(f"{user} is now a VIP+!")
            elif int(hours) >= 50 and int(hours) < 100:
                await console.send(f"lp user {user} group add star")
                await ctx.send(f"{user} is now a STAR!")
            elif int(hours) >= 100:
                await console.send(f"lp user {user} group add superstar")
                await ctx.send(f"{user} is now a SUPERSTAR!")
            elif int(hours) < 5:
                await ctx.send(f"That user doesn't have enough time for VIP status.\n{user} has {hours} hours, {minutes} minutes online.")
        else:
            if int(hours) >= 5 and int(hours) < 10:
                await console.send(f"lp user {user} group add vip")
                await ctx.send(f"{user} is now a VIP")
            elif int(hours) >= 10 and int(hours) < 50:
                await console.send(f"lp user {user} group add vip+")
                await ctx.send(f"{user} is now a VIP+")
            elif int(hours) >= 50 and int(hours) < 100:
                await console.send(f"lp user {user} group add star")
                await ctx.send(f"{user} is now a STAR")
            elif int(hours) >= 100:
                await console.send(f"lp user {user} group add superstar")
                await ctx.send(f"{user} is now a SUPERSTAR")
            elif int(hours) < 5:
                await ctx.send(f"That user doesn't have enough time for VIP status.\n{user} has {hours} hours online.")
    else:
        if "minutes" in content and "day" not in content:
            minutes, sep, after=content.partition(" minute")
            before, sep, minutes=minutes.partition("hour")
            before, sep, minutes=minutes.partition(" ")
            await ctx.send(f"That user doesn't have enough time for VIP status\n{user} has {minutes} minutes online.")
        elif "seconds" in content and "minutes" in content and "day" not in content:
            minutes, sep, after=content.partition(" minute")
            before, sep, minutes=minutes.partition("hour")
            before, sep, minutes=minutes.partition(" ")
            seconds, sep, after=content.partition(" second")
            before, sep, seconds=seconds.partition("minute")
            before, sep, seconds=seconds.partition(" ")
            await ctx.send(f"That user doesn't have enough time for VIP status\n{user} has {minutes} minutes, {seconds} seconds online.")
        elif "seconds" in content and "day" not in content:
            seconds, sep, after=content.partition(" second")
            before, sep, seconds=seconds.partition("minute")
            before, sep, seconds=seconds.partition(" ")
            await ctx.send(f"That user doesn't have enough time for VIP status\n{user} has {seconds} seconds online. (lol)")
        elif "Player not found" in content:
            await ctx.send(f"Error: Invalid user")
        else:
            await ctx.send(f"Process exited with an unknown error")

@client.command()
@commands.has_any_role("Owner", "Admin")
async def lockdown(ctx, mode="staff"):
    console=client.get_channel(950858523846271007)
    await console.send("whitelist list")
    await asyncio.sleep(2)
    content=(await console.history(limit=1).flatten())[0].content
    a=content.split("There are ",1)[1]
    before, sep, after=a.partition(" whitelisted players: ")
    whitelistCount=""
    for m in before:
        if m.isdigit():
            whitelistCount=whitelistCount + m
    before, sep, after=after.partition("\n")
    before, sep, after=before.partition("```")
    array=before.split(", ")
    owners=["OverdriveZR"]
    admins=["Dimensional_Duck"]
    mods=["Mxnsoo", "sundew001", "Champthekitten"]
    helpers=["nebula00"]
    if mode != "end" and mode != "backup" and mode != "restore":
        num=0
        if ctx.author.id != 968356025461768192:
            now=datetime.now()
            dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
            date, sep, time=dateTime.partition(" ")
            sendSMS(messageSubject="ZMP ALERT", messageBody=f"{date} | {time}\n\nTag: {ctx.author} | ID: {ctx.author.id} | Name: {ctx.author.nick}\n\nUser issued command:\n\"{ctx.message.content}\"")
        f=open(f"WLbackup{whitelistCount}.txt", "w+")
        await console.send("whitelist list")
        await asyncio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
        before, sep, content=content.partition("players: ")
        content, sep, after=content.partition("\n")
        content, sep, after=content.partition("```")
        f.write(content)
        f.close()
        print(f"{ctx.author} created a backup")
        for fname in os.listdir():
            if fname.startswith("WLbackup"):
                if num <= int(re.search(r'\d+', fname).group(0)):
                    num=int(re.search(r'\d+', fname).group(0))
        await ctx.send(f"A backup was created, consisting of {num} player accounts")
        await ctx.send("Initiating lockdown...")
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        add=100/num
        players=0
        for i in array:
            players=players + 1
            percent=percent + add
            await console.send(f"whitelist remove {i}")
            await msg.edit(content=f"Initiating lockdown... {round(percent)}%")
        f.close()
    if mode != "end" and mode != "backup" and mode != "restore":
        await console.send("kickall")
    if mode != "end" and mode != "backup" and mode != "restore":
        await ctx.send(f"Lockdown started. Whitelisting {mode}")
    if mode=="owners":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    elif mode=="admins":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        for i in admins:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in admins:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    elif mode=="mods":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        for i in mods:
            count += 1
        for i in admins:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in mods :
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in admins:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    elif mode=="helpers":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        for i in helpers:
            count += 1
        for i in mods:
            count += 1
        for i in admins:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in helpers:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in mods :
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in admins:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    elif mode=="staff":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        for i in helpers:
            count += 1
        for i in mods:
            count += 1
        for i in admins:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in helpers:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in mods :
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in admins:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    if mode != "end" and mode != "backup" and mode != "restore":
        await ctx.send(f"{mode} whitelisted. Lockdown complete.")
        print(f"\n{ctx.author} started a lockdown\n")
    elif mode=="end":
        f=open("lockdown_whitelist.txt")
        if f.mode=='r':
            contents=f.read()
            array=contents.split(", ")
            await ctx.send("Ending lockdown. Rewhitelisting players...")
            for i in owners:
                await console.send(f"whitelist add {i}")
            for i in admins:
                await console.send(f"whitelist add {i}")
            for i in mods:
                await console.send(f"whitelist add {i}")
            for i in helpers:
                await console.send(f"whitelist add {i}")
            for i in array:
                await console.send(f"whitelist add {i}")
            f.close()
            os.remove("lockdown_whitelist.txt")
            print(f"\n{ctx.author} ended a lockdown\n")
            await ctx.send("Lockdown ended")
    elif mode=="restore":
        num=0
        for fname in os.listdir():
            if fname.startswith("WLbackup"):
                if num <= int(re.search(r'\d+', fname).group(0)):
                    num=int(re.search(r'\d+', fname).group(0))
        f=open(f"WLbackup{num}.txt")
        if f.mode=='r':
            contents=f.read()
            array=contents.split(", ")
            await ctx.send(f"Restoring to backup of {num} whitelisted players")
            msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
            before, sep, msg=str(msg).partition("<Message id=")
            msg, sep, after=str(msg).partition(" channel=<")
            msg=await ctx.channel.fetch_message(msg)
            percent=0
            add=100/num
            players=0
            for i in array:
                players=players + 1
                percent=percent + add
                await console.send(f"whitelist add {i}")
                await msg.edit(content=f"Restoring to backup of {num} whitelisted players\n{round(percent)}%  ({players}/{num})")
            f.close()
            await ctx.send("Whitelist successfully restored")
            print(f"\n{ctx.author} restored the whitelist\n")
    elif mode=="backup":
        num=0
        f=open(f"WLbackup{whitelistCount}.txt", "w+")
        await console.send("whitelist list")
        await asyncio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
        before, sep, content=content.partition("players: ")
        content, sep, after=content.partition("\n")
        content, sep, after=content.partition("```")
        f.write(content)
        f.close()
        print(f"{ctx.author} created a backup")
        for fname in os.listdir():
            if fname.startswith("WLbackup"):
                if num <= int(re.search(r'\d+', fname).group(0)):
                    num=int(re.search(r'\d+', fname).group(0))
        await ctx.send(f"A backup was created, consisting of {num} player accounts")
    if mode != "end":
        f=open("lockdown_whitelist.txt", "w+")
        for i in array:
            f.write(f"{i}, ")
        f.close()

@client.command()
@commands.has_any_role("Owner", "Admin", "Moderator")
async def remwl(ctx, version, *, tag):
    if version.lower()=="java":
        command=f"whitelist remove {tag}"
        print(f"{tag} was removed from the whitelist")
    elif version.lower()=="bedrock":
        bTag=tag.replace(" ", "_")
        command=f"whitelist remove .{bTag}"
        print(f"{bTag} was removed from the whitelist")
    channel=client.get_channel(950858523846271007)
    await channel.send(command)

@client.command()
@commands.has_any_role("Owner", "Moderator", "Admin")
async def mcban(ctx, tag, *, reason="None given"):
    print(f"{tag} was removed banned from the minecraft server by {ctx.author} with reason \"Banned by {ctx.author} in Discord with reason: {reason}\"")
    channel=client.get_channel(950858523846271007)
    await channel.send(f"ban {tag} Banned by {ctx.author} in Discord with reason: {reason}")
    await ctx.send(f"Banned {tag} with reason \"{reason}\"")
    f=open("LOOKUP.txt")
    contents=f.read().lower()
    contents=contents.split(", ")
    found=False
    notFound=True
    for i in contents:
        if tag.lower() in i:
            found=True
            notFound=False
            rawData=i
        else:
            notFound=True
    if notFound==True:
        if found==False:
            pass
    if found==True:
        before, sep, userID=rawData.partition("id")
        userID, sep, after=userID.partition("-")
        user=await client.fetch_user(userID)

        await ctx.send(f"{tag} was banned from the Minecraft server. Would you like to ban them on Discord?\nUsername: {user}")
        def check_rule(message: discord.Message):
            return message.author.id==ctx.message.author.id
        try:
            answer=(await client.wait_for('message', check=check_rule, timeout=20)).content
        except (asyncio.exceptions.TimeoutError, discord.ext.commands.errors.CommandInvokeError):
            await ctx.send("Took too long to answer. User will not be banned.")
            return
        if answer.lower()=='yes':
            guild = client.get_guild(870964644523692053)
            member = await guild.fetch_member(id)
            await member.ban(reason=reason)
        elif answer.lower()=='no':
            await ctx.send("User will not be banned.")
        else:
            await ctx.send("User will not be banned. Invalid input.")












    f.close()

@client.command()
@commands.has_any_role("Owner", "Moderator", "Admin")
async def mcunban(ctx, tag):
    print(f"{tag} was removed unbanned from the minecraft server by {ctx.author}")
    channel=client.get_channel(950858523846271007)
    await channel.send(f"pardon {tag}")
    await ctx.send(f"Unbanned {tag}")

@client.command()
@commands.has_any_role("Owner", "Moderator", "Admin")
async def mcpardon(ctx, tag):
    print(f"{tag} was removed unbanned from the minecraft server by {ctx.author}")
    channel=client.get_channel(950858523846271007)
    await channel.send(f"pardon {tag}")
    await ctx.send(f"Unbanned {tag}")

@client.command()
@commands.has_any_role("Owner", "Admin")
async def lp(ctx, *, params):
    console=client.get_channel(950858523846271007)
    if params.lower().startswith("editor"):
        await console.send("lp editor")
        await asyncio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
        if "https://luckperms.net/editor/" in content:
            before, sep, editor=content.partition("https://luckperms.net/editor/")
            editor, sep, after=editor.partition("\n")
            if "```" in editor:
                editor, sep, after=editor.partition("```")
                await ctx.author.send(f"https://luckperms.net/editor/{editor}")
            else:
                await ctx.author.send(editor)
        else:
            await asyncio.sleep(2)
            content=(await console.history(limit=1).flatten())[0].content
            if "https://luckperms.net/editor/" in content:
                before, sep, editor=content.partition("https://luckperms.net/editor/")
                editor, sep, after=editor.partition("\n")
                if "```" in editor:
                    editor, sep, after=editor.partition("```")
                    await ctx.author.send(f"https://luckperms.net/editor/{editor}")
                else:
                    await ctx.author.send(editor)
            else:
                await asyncio.sleep(2)
                content=(await console.history(limit=1).flatten())[0].content
                if "https://luckperms.net/editor/" in content:
                    if "https://luckperms.net/editor/" in content:
                        before, sep, editor=content.partition("https://luckperms.net/editor/")
                        editor, sep, after=editor.partition("\n")
                        if "```" in editor:
                            editor, sep, after=editor.partition("```")
                        await ctx.author.send(f"https://luckperms.net/editor/{editor}")
                    else:
                        await ctx.author.send(editor)
                else:
                    ctx.author.send("unable to get Luckperms Data")
    elif params.lower().startswith("user "):
        before, sep, after=params.partition("user ")
        username, sep, params=after.partition(" ")
        if params.lower().startswith("group "):
            before, sep, params=params.partition("group ")
            if params.lower().startswith("addrem "):
                before, sep, params=params.partition("addrem ")
                add, sep, rem=params.partition(" ")
                await console.send(f"lp user {username} group add {add}")
                await console.send(f"lp user {username} group remove {rem}")
            elif params.lower().startswith("add "):
                before, sep, add=params.partition("add ")
                await console.send(f"lp user {username} group add {add}")
            elif params.lower().startswith("rem "):
                before, sep, rem=params.partition("rem ")
                await console.send(f"lp user {username} group remove {rem}")
        elif params.lower().startswith("permission "):
            before, sep, params=params.partition("permission ")
            if params.lower().startswith("add "):
                before, sep, permission=params.partition("add ")
                await console.send(f"lp user {username} permission set {permission} true")
            elif params.lower().startswith("rem "):
                before, sep, permission=params.partition("rem ")
                await console.send(f"lp user {username} permission set {permission} false")

@client.command()
@commands.has_any_role("Owner", "Admin")
async def console(ctx, display, *, cmd):
    channel=client.get_channel(950858523846271007)
    await channel.send(cmd)
    console=client.get_channel(950858523846271007)
    await asyncio.sleep(2)
    content=(await console.history(limit=1).flatten())[0].content
    if display=="true":
        await ctx.send(content)
    else:
        pass

@client.command()
@commands.has_any_role("Owner", "Admin")
async def server(ctx, mode, command=""):
    if ctx.author.id != 968356025461768192:
        now=datetime.now()
        dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
        date, sep, time=dateTime.partition(" ")
        sendSMS(messageSubject="ZMP ALERT", messageBody=f"{date} | {time}\n\nTag: {ctx.author} | ID: {ctx.author.id} | Name: {ctx.author.nick}\n\nUser issued command:\n\"{ctx.message.content}\"")
    console=client.get_channel(950858523846271007)
    if mode.lower()=="action":
        if command.lower()=="start":
            await ctx.send("Diagnosing issue...")
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result=sock.connect_ex(('127.0.0.1',25565))
            if result==0:
                await ctx.send("ㅤ\nServer open on local host")
                sock.close()
                sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ip=socket.gethostbyname("play.zmp.lol")
                result=sock.connect_ex((ip,25565))
                if result==0:
                    await ctx.send("ㅤ\nServer domain response check passed")
                    await console.send("ping")
                    await asyncio.sleep(2)
                    content=(await console.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await asyncio.sleep(2)
                        content=(await console.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            await ctx.send("ㅤ\nServer is running")
                            await ctx.send("ㅤ\nNo issues found")
                            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await asyncio.sleep(2)
                            content=(await console.history(limit=1).flatten())[0].content
                            if content != "ping" and "```" in content:
                                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                                await ctx.send("ㅤ\nServer is running")
                                await ctx.send("ㅤ\nNo issues found")
                                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                            else:
                                await ctx.send("ㅤ\nDiscordSRV console response check failed.")
                                role=discord.utils.find(lambda r: r.name=='Owner', ctx.message.guild.roles)
                                if role not in ctx.author.roles:
                                    await ctx.send("ㅤ\nAlerting owner...")
                                    user=client.get_user(968356025461768192)
                                    msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
                                    before, sep, msg=str(msg).partition("<Message id=")
                                    msg, sep, after=str(msg).partition(" channel=<")
                                    msg=await ctx.channel.fetch_message(msg)
                                    for i in range(10):
                                        n=(i * 10)
                                        await msg.edit(content=f"ㅤ\nAlerting owner... {n}%")
                                        await user.send(f"Server is offline")
                                    await msg.edit(content=f"ㅤ\nAlerting owner... 100%")
                                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nServer domain response check failed")
                    await ctx.send("ㅤ\nStarting Dynamic IP address updater...")
                    os.startfile(r"C:\Users\Overdrive\Desktop\apps\DDNS.exe")
            else:
                await ctx.send("ㅤ\nServer is not open on local host")
                await ctx.send("ㅤ\nStarting server...")
                path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\public\\1--START.cmd"
                subprocess.Popen(f"start /wait cmd /c {path}1--START.cmd", shell=True)
                await ctx.send("ㅤ\nServer startup initiated")
                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
            sock.close()
        elif mode.lower()=="stop":
            await ctx.send("Stopping server...")
            stopServer("ZMP")
            await ctx.send("ㅤ\nServer stopped")
    elif mode.lower()=="get":
        if command=="status":
            await ctx.send("Diagnosing...")
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result=sock.connect_ex(('127.0.0.1',25565))
            if result==0:
                await ctx.send("ㅤ\nServer open on local host")
                sock.close()
                sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ip=socket.gethostbyname("play.zmp.lol")
                result=sock.connect_ex((ip,25565))
                if result==0:
                    await ctx.send("ㅤ\nServer domain response check passed")
                    await console.send("ping")
                    await asyncio.sleep(2)
                    content=(await console.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await asyncio.sleep(2)
                        content=(await console.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await asyncio.sleep(2)
                            content=(await console.history(limit=1).flatten())[0].content
                            if content != "ping" and "```" in content:
                                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            else:
                                await ctx.send("ㅤ\nDiscordSRV console response check failed")
                else:
                    await ctx.send("ㅤ\nServer domain response check failed")
            else:
                path=(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\public")
                ssAndHide("ZMP", f"{path}")
                await ctx.send("ㅤ\nServer is not open on local host")
                await ctx.send("ㅤ\n**SERVER OFFLINE**")
            sock.close()
            await ctx.send(file=discord.File(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\public\ssOfWindow.png"))
            os.remove(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\public\ssOfWindow.png")
        elif command.lower()=="whitelist":
            await console.send("whitelist list")
            await asyncio.sleep(4)
            content=(await console.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("players: ")
            content, sep, after=content.partition("\n")
            content, sep, after=content.partition("```")
            if content=="":
                await asyncio.sleep(2)
            else:
                pass
            await ctx.send(f"```{content}```")
        elif command.lower()=="players":
            await console.send("list")
            await asyncio.sleep(4)
            content=(await console.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("/list")
            before, sep, content=content.partition("] ")
            content, sep, after=content.partition("```")
            if content=="":
                await asyncio.sleep(2)
            else:
                pass
            await ctx.send(f"```{content}```")
        elif command.lower()=="tps":
            await console.send("tps")
            await asyncio.sleep(4)
            content=(await console.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("] ")
            content, sep, after=content.partition("```")
            if content=="":
                await asyncio.sleep(2)
            else:
                pass 
            await ctx.send(f"```{content}```")
    elif mode.lower()=="start":
        await ctx.send("Diagnosing issue...")
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result=sock.connect_ex(('127.0.0.1',25565))
        if result==0:
            await ctx.send("ㅤ\nServer open on local host")
            sock.close()
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip=socket.gethostbyname("play.zmp.lol")
            result=sock.connect_ex((ip,25565))
            if result==0:
                await ctx.send("ㅤ\nServer domain response check passed")
                await console.send("ping")
                await asyncio.sleep(2)
                content=(await console.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    await ctx.send("ㅤ\nServer is running")
                    await ctx.send("ㅤ\nNo issues found")
                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await asyncio.sleep(2)
                    content=(await console.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await asyncio.sleep(2)
                        content=(await console.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            await ctx.send("ㅤ\nServer is running")
                            await ctx.send("ㅤ\nNo issues found")
                            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed.")
                            role=discord.utils.find(lambda r: r.name=='Owner', ctx.message.guild.roles)
                            if role not in ctx.author.roles:
                                print(ctx.author.id)
                                await ctx.send("ㅤ\nAlerting owner...")
                                user=client.get_user(968356025461768192)
                                msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
                                before, sep, msg=str(msg).partition("<Message id=")
                                msg, sep, after=str(msg).partition(" channel=<")
                                msg=await ctx.channel.fetch_message(msg)
                                for i in range(10):
                                    n=(i * 10)
                                    await msg.edit(content=f"ㅤ\nAlerting owner... {n}%")
                                    await user.send(f"Server is offline")
                                await msg.edit(content=f"ㅤ\nAlerting owner... 100%")
                                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
            else:
                await ctx.send("ㅤ\nServer domain response check failed")
                await ctx.send("ㅤ\nStarting Dynamic IP address updater...")
                os.startfile(r"C:\Users\Overdrive\Desktop\apps\DDNS.exe")
        else:
            await ctx.send("ㅤ\nServer is not open on local host")
            await ctx.send("ㅤ\nStarting server...")
            path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\public\\1--START.cmd"
            subprocess.Popen(f"start /wait cmd /c {path}1--START.cmd", shell=True)
            await ctx.send("ㅤ\nServer startup initiated")
            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
        sock.close()
    elif mode.lower()=="get":
        if command=="status":
            await ctx.send("Diagnosing...")
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result=sock.connect_ex(('127.0.0.1',25565))
            if result==0:
                await ctx.send("ㅤ\nServer open on local host")
                sock.close()
                sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ip=socket.gethostbyname("play.zmp.lol")
                result=sock.connect_ex((ip,25565))
                if result==0:
                    await ctx.send("ㅤ\nServer domain response check passed")
                    await console.send("ping")
                    await asyncio.sleep(2)
                    content=(await console.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await asyncio.sleep(2)
                        content=(await console.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await asyncio.sleep(2)
                            content=(await console.history(limit=1).flatten())[0].content
                            if content != "ping" and "```" in content:
                                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            else:
                                print("ㅤ\nDiscordSRV console response check failed")
                else:
                    await ctx.send("ㅤ\nServer domain response check failed")
            else:
                await ctx.send("ㅤ\nServer is not open on local host")
            sock.close()
    elif mode.lower()=="stop":
        await ctx.send("Stopping server...")
        stopServer("ZMP")
        await ctx.send("ㅤ\nServer stopped")

### BUILD SERVER ###

@client.command()
@commands.has_any_role("Owner", "Admin")
async def buildstop(ctx):
    await client.get_channel(1026654816996446278).send("stop")

@client.command(pass_context=True)
@commands.has_any_role("Owner", "Admin", "Moderator")
async def buildwhitelist(ctx, version, *, tag):
    if version.lower()=="java":
        command=f"whitelist add {tag}"
    elif version.lower()=="bedrock":
        bTag=tag.replace(" ", "_")
        command=f"whitelist add .{bTag}"
    channel=discord.utils.get(ctx.author.guild.text_channels, name="⚡︱build-console")
    await channel.send(command)
    await asyncio.sleep(2)
    console=client.get_channel(1026654816996446278)
    content=(await console.history(limit=1).flatten())[0].content
    if 'already whitelisted' in content:
        if version.lower()=="java":
            print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
        elif version.lower()=="bedrock":
            print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
        await ctx.message.add_reaction("✅")
        await ctx.message.add_reaction("⚠️")
        await ctx.author.send("**You're already whitelisted!**\n\nIf you are having issues with connecting to the server, ask for help in one of the help channels.")
    elif 'to the whitelist' in content:
        if version.lower()=="java":
            print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
        elif version.lower()=="bedrock":
            print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
        await ctx.message.add_reaction("✅")
    elif 'player does not exist' in content:
        await ctx.author.send("**That didnt work!**\n\nBe sure you entered the right tag, including capitalization!\nIf you are trying to join on bedrock, try to join before trying to whitelist yourself!")
        await ctx.message.add_reaction("❌")
        if version.lower()=="java":
            print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
        elif version.lower()=="bedrock":
            print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
    elif 'whitelist add' in content:
        await asyncio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
        if 'already whitelisted' in content:
            if version.lower()=="java":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
            elif version.lower()=="bedrock":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
            await ctx.message.add_reaction("✅")
            await ctx.message.add_reaction("⚠️")
            await ctx.author.send("**You're already whitelisted!**\n\nIf you are having issues with connecting to the server, ask for help in one of the help channels.")
        elif 'to the whitelist' in content:
            if version.lower()=="java":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
            elif version.lower()=="bedrock":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
            await ctx.message.add_reaction("✅")
        elif 'player does not exist' in content:
            await ctx.author.send("**That didnt work!**\n\nBe sure you entered the right tag, including capitalization!\nIf you are trying to join on bedrock, try to join before trying to whitelist yourself!")
            await ctx.message.add_reaction("❌")
            if version.lower()=="java":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
            elif version.lower()=="bedrock":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
        elif 'whitelist add' in content:
            await asyncio.sleep(4)
            content=(await console.history(limit=1).flatten())[0].content
            if 'already whitelisted' in content:
                if version.lower()=="java":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
                elif version.lower()=="bedrock":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
                await ctx.message.add_reaction("✅")
                await ctx.message.add_reaction("⚠️")
                await ctx.author.send("**You're already whitelisted!**\n\nIf you are having issues with connecting to the server, ask for help in one of the help channels.")
            elif 'to the whitelist' in content:
                if version.lower()=="java":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
                elif version.lower()=="bedrock":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
                await ctx.message.add_reaction("✅")
            elif 'player does not exist' in content:
                await ctx.author.send("**That didnt work!**\n\nBe sure you entered the right tag, including capitalization!\nIf you are trying to join on bedrock, try to join before trying to whitelist yourself!")
                await ctx.message.add_reaction("❌")
                if version.lower()=="java":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
                elif version.lower()=="bedrock":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
            elif 'whitelist add' in content:
                await ctx.message.add_reaction("❌")
                await ctx.author.send("Sorry, but you were unable to be whitelisted at this time. Please contact Zoe for further information.")
                if version.lower()=="java":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - unknown error\n----WHITELIST----\n\n")
                elif version.lower()=="bedrock":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - unknown error\n----WHITELIST----\n\n")

@client.command()
@commands.has_any_role("Owner", "Admin", "Moderator", "Helper")
async def buildstatus(ctx):
    buildconsole=client.get_channel(1026654816996446278)
    await ctx.send("Diagnosing...")
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result=sock.connect_ex(('127.0.0.1',25567))
    if result==0:
        await ctx.send("ㅤ\nServer open on local host")
        sock.close()
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip=socket.gethostbyname("build.zmp.lol")
        result=sock.connect_ex((ip,25567))
        if result==0:
            await ctx.send("ㅤ\nServer domain response check passed")
            await buildconsole.send("ping")
            await asyncio.sleep(2)
            content=(await buildconsole.history(limit=1).flatten())[0].content
            if content != "ping" and "```" in content:
                await ctx.send("ㅤ\nDiscordSRV console response check passed")
            else:
                await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                await asyncio.sleep(2)
                content=(await buildconsole.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await asyncio.sleep(2)
                    content=(await buildconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed")
        else:
            await ctx.send("ㅤ\nServer domain response check failed")
    else:
        await ctx.send("ㅤ\nServer is not open on local host")
        await ctx.send("ㅤ\n**SERVER OFFLINE**")
    path=(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\build")
    ssAndHide("BUILD", f"{path}")
    await ctx.send(file=discord.File(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\build\ssOfWindow.png"))
    os.remove(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\build\ssOfWindow.png")

@client.command()
@commands.has_any_role("Owner", "Admin", "Moderator")
async def buildstart(ctx):
    buildconsole=client.get_channel(1026654816996446278)
    await ctx.send("Diagnosing issue...")
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result=sock.connect_ex(('127.0.0.1',25567))
    if result==0:
        await ctx.send("ㅤ\nServer open on local host")
        sock.close()
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip=socket.gethostbyname("build.zmp.lol")
        result=sock.connect_ex((ip,25567))
        if result==0:
            await ctx.send("ㅤ\nServer domain response check passed")
            await buildconsole.send("ping")
            await asyncio.sleep(2)
            content=(await buildconsole.history(limit=1).flatten())[0].content
            if content != "ping" and "```" in content:
                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                await ctx.send("ㅤ\nServer is running")
                await ctx.send("ㅤ\nNo issues found")
                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
            else:
                await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                await asyncio.sleep(2)
                content=(await buildconsole.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    await ctx.send("ㅤ\nServer is running")
                    await ctx.send("ㅤ\nNo issues found")
                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await asyncio.sleep(2)
                    content=(await buildconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed.")
                        role=discord.utils.find(lambda r: r.name=='Owner', ctx.message.guild.roles)
                        if role not in ctx.author.roles:
                            await ctx.send("ㅤ\nAlerting owner...")
                            user=client.get_user(968356025461768192)
                            msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
                            before, sep, msg=str(msg).partition("<Message id=")
                            msg, sep, after=str(msg).partition(" channel=<")
                            msg=await ctx.channel.fetch_message(msg)
                            for i in range(10):
                                n=(i * 10)
                                await msg.edit(content=f"ㅤ\nAlerting owner... {n}%")
                                await user.send(f"Server is offline")
                            await msg.edit(content=f"ㅤ\nAlerting owner... 100%")
                            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
        else:
            await ctx.send("ㅤ\nServer domain response check failed")
            await ctx.send("ㅤ\nStarting Dynamic IP address updater...")
            os.startfile(r"C:\Users\Overdrive\Desktop\apps\DDNS.exe")
    else:
        await ctx.send("ㅤ\nServer is not open on local host")
        await ctx.send("ㅤ\nStarting server...")
        path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\build\\1--START.cmd"
        subprocess.Popen(f"start /wait cmd /c {path}1--START.cmd")
        await ctx.send("ㅤ\nServer startup initiated")
        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
    sock.close()

@client.command()
async def buildip(ctx):
    await ctx.send("build.zmp.lol:25567")

@client.command()
@commands.has_any_role("Owner", "Admin")
async def buildlockdown(ctx, mode="staff"):
    console=client.get_channel(1026654816996446278)
    await console.send("whitelist list")
    await asyncio.sleep(2)
    content=(await console.history(limit=1).flatten())[0].content
    a=content.split("There are ",1)[1]
    before, sep, after=a.partition(" whitelisted players: ")
    whitelistCount=""
    for m in before:
        if m.isdigit():
            whitelistCount=whitelistCount + m
    before, sep, after=after.partition("\n")
    before, sep, after=before.partition("```")
    array=before.split(", ")
    owners=["OverdriveZR"]
    admins=["Dimensional_Duck"]
    mods=["Mxnsoo", "Swampyemerson"]
    helpers=["doggey200000", "FoxtatoThePotato"]
    if mode != "end" and mode != "backup" and mode != "restore":
        if ctx.author.id != 968356025461768192:
            now=datetime.now()
            dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
            date, sep, time=dateTime.partition(" ")
            sendSMS(messageSubject="ZMP ALERT", messageBody=f"{date} | {time}\n\nTag: {ctx.author} | ID: {ctx.author.id} | Name: {ctx.author.nick}\n\nUser issued command:\n\"{ctx.message.content}\"")
        num=0
        f=open(f"buildWLbackup{whitelistCount}.txt", "w+")
        await console.send("whitelist list")
        await asyncio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
        before, sep, content=content.partition("players: ")
        content, sep, after=content.partition("\n")
        content, sep, after=content.partition("```")
        f.write(content)
        f.close()
        print(f"{ctx.author} created a backup")
        for fname in os.listdir():
            if fname.startswith("WLbackup"):
                if num <= int(re.search(r'\d+', fname).group(0)):
                    num=int(re.search(r'\d+', fname).group(0))
        await ctx.send(f"A backup was created, consisting of {num} player accounts")
        await ctx.send("Initiating lockdown")
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        add=100/num
        players=0
        for i in array:
            players=players + 1
            percent=percent + add
            await console.send(f"whitelist remove {i}")
            await msg.edit(content=f"Initiating lockdown... {round(percent)}%")
        f.close()
    if mode != "end" and mode != "backup" and mode != "restore":
        await console.send("kickall")
    if mode != "end" and mode != "backup" and mode != "restore":
        await ctx.send(f"Lockdown started. Whitelisting {mode}")
    if mode=="owners":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    elif mode=="admins":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        for i in admins:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in admins:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    elif mode=="mods":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        for i in mods:
            count += 1
        for i in admins:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in mods :
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in admins:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    elif mode=="helpers":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        for i in helpers:
            count += 1
        for i in mods:
            count += 1
        for i in admins:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in helpers:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in mods :
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in admins:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    elif mode=="staff":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        for i in helpers:
            count += 1
        for i in mods:
            count += 1
        for i in admins:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in helpers:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in mods :
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in admins:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    if mode != "end" and mode != "backup" and mode != "restore":
        await ctx.send(f"{mode} whitelisted. Lockdown complete.")
        print(f"\n{ctx.author} started a lockdown\n")
    elif mode=="end":
        f=open("buildlockdown_whitelist.txt")
        if f.mode=='r':
            contents=f.read()
            array=contents.split(", ")
            await ctx.send("Ending lockdown. Rewhitelisting players...")
            for i in owners:
                await console.send(f"whitelist add {i}")
            for i in admins:
                await console.send(f"whitelist add {i}")
            for i in mods:
                await console.send(f"whitelist add {i}")
            for i in helpers:
                await console.send(f"whitelist add {i}")
            for i in array:
                await console.send(f"whitelist add {i}")
            f.close()
            os.remove("buildlockdown_whitelist.txt")
            print(f"\n{ctx.author} ended a lockdown\n")
            await ctx.send("Lockdown ended")
    elif mode=="restore":
        num=0
        for fname in os.listdir():
            if fname.startswith("WLbackup"):
                if num <= int(re.search(r'\d+', fname).group(0)):
                    num=int(re.search(r'\d+', fname).group(0))
        f=open(f"buildWLbackup{num}.txt")
        if f.mode=='r':
            contents=f.read()
            array=contents.split(", ")
            await ctx.send(f"Restoring to backup of {num} whitelisted players")
            msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
            before, sep, msg=str(msg).partition("<Message id=")
            msg, sep, after=str(msg).partition(" channel=<")
            msg=await ctx.channel.fetch_message(msg)
            percent=0
            add=100/num
            players=0
            for i in array:
                players=players + 1
                percent=percent + add
                await console.send(f"whitelist add {i}")
                await msg.edit(content=f"Restoring to backup of {num} whitelisted players\n{round(percent)}%  ({players}/{num})")
            f.close()
            await ctx.send("Whitelist successfully restored")
            print(f"\n{ctx.author} restored the whitelist\n")
    elif mode=="backup":
        num=0
        f=open(f"buildWLbackup{whitelistCount}.txt", "w+")
        await console.send("whitelist list")
        await asyncio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
        before, sep, content=content.partition("players: ")
        content, sep, after=content.partition("\n")
        content, sep, after=content.partition("```")
        f.write(content)
        f.close()
        print(f"{ctx.author} created a backup")
        for fname in os.listdir():
            if fname.startswith("WLbackup"):
                if num <= int(re.search(r'\d+', fname).group(0)):
                    num=int(re.search(r'\d+', fname).group(0))
        await ctx.send(f"A backup was created, consisting of {num} player accounts")
    if mode != "end":
        f=open("buildlockdown_whitelist.txt", "w+")
        for i in array:
            f.write(f"{i}, ")
        f.close()

@client.command()
@commands.has_any_role("Owner", "Admin", "Moderator")
async def buildremwl(ctx, version, *, tag):
    if version.lower()=="java":
        command=f"whitelist remove {tag}"
        print(f"{tag} was removed from the whitelist")
    elif version.lower()=="bedrock":
        bTag=tag.replace(" ", "_")
        command=f"whitelist remove .{bTag}"
        print(f"{bTag} was removed from the whitelist")
    channel=discord.utils.get(ctx.author.guild.text_channels, name="⚡︱build-console")
    await channel.send(command)

@client.command()
@commands.has_any_role("Owner", "Moderator", "Admin")
async def buildmcban(ctx, tag, *, reason="None given"):
    print(f"{tag} was removed banned from the minecraft server by {ctx.author} with reason \"Banned by {ctx.author} in discord with reason: {reason}\"")
    channel=discord.utils.get(ctx.author.guild.text_channels, name="⚡︱build-console")
    await channel.send(f"ban {tag} Banned by {ctx.author} in discord with reason: {reason}")
    await ctx.send(f"Banned {tag} with reason \"{reason}\"")

@client.command()
@commands.has_any_role("Owner", "Moderator", "Admin")
async def buildmcunban(ctx, tag):
    print(f"{tag} was removed unbanned from the minecraft server by {ctx.author}")
    channel=discord.utils.get(ctx.author.guild.text_channels, name="⚡︱build-console")
    await channel.send(f"pardon {tag}")
    await ctx.send(f"Unbanned {tag}")

@client.command()
@commands.has_any_role("Owner", "Moderator", "Admin")
async def buildmcpardon(ctx, tag):
    print(f"{tag} was removed unbanned from the minecraft server by {ctx.author}")
    channel=discord.utils.get(ctx.author.guild.text_channels, name="⚡︱build-console")
    await channel.send(f"pardon {tag}")
    await ctx.send(f"Unbanned {tag}")

@client.command()
@commands.has_any_role("Owner", "Admin")
async def buildlp(ctx, *, params):
    buildconsole=client.get_channel(1026654816996446278)
    if params.lower().startswith("editor"):
        await buildconsole.send("lp editor")
        await asyncio.sleep(2)
        content=(await buildconsole.history(limit=1).flatten())[0].content
        if "https://luckperms.net/editor/" in content:
            before, sep, editor=content.partition("https://luckperms.net/editor/")
            editor, sep, after=editor.partition("\n")
            if "```" in editor:
                editor, sep, after=editor.partition("```")
                await ctx.author.send(f"https://luckperms.net/editor/{editor}")
            else:
                await ctx.author.send(editor)
        else:
            await asyncio.sleep(2)
            content=(await buildconsole.history(limit=1).flatten())[0].content
            if "https://luckperms.net/editor/" in content:
                before, sep, editor=content.partition("https://luckperms.net/editor/")
                editor, sep, after=editor.partition("\n")
                if "```" in editor:
                    editor, sep, after=editor.partition("```")
                    await ctx.author.send(f"https://luckperms.net/editor/{editor}")
                else:
                    await ctx.author.send(editor)
            else:
                await asyncio.sleep(2)
                content=(await buildconsole.history(limit=1).flatten())[0].content
                if "https://luckperms.net/editor/" in content:
                    if "https://luckperms.net/editor/" in content:
                        before, sep, editor=content.partition("https://luckperms.net/editor/")
                        editor, sep, after=editor.partition("\n")
                        if "```" in editor:
                            editor, sep, after=editor.partition("```")
                        await ctx.author.send(f"https://luckperms.net/editor/{editor}")
                    else:
                        await ctx.author.send(editor)
                else:
                    ctx.author.send("unable to get Luckperms Data")
    elif params.lower().startswith("user "):
        before, sep, after=params.partition("user ")
        username, sep, params=after.partition(" ")
        if params.lower().startswith("group "):
            before, sep, params=params.partition("group ")
            if params.lower().startswith("addrem "):
                before, sep, params=params.partition("addrem ")
                add, sep, rem=params.partition(" ")
                await buildconsole.send(f"lp user {username} group add {add}")
                await buildconsole.send(f"lp user {username} group remove {rem}")
            elif params.lower().startswith("add "):
                before, sep, add=params.partition("add ")
                await buildconsole.send(f"lp user {username} group add {add}")
            elif params.lower().startswith("rem "):
                before, sep, rem=params.partition("rem ")
                await buildconsole.send(f"lp user {username} group remove {rem}")
        elif params.lower().startswith("permission "):
            before, sep, params=params.partition("permission ")
            if params.lower().startswith("add "):
                before, sep, permission=params.partition("add ")
                await buildconsole.send(f"lp user {username} permission set {permission} true")
            elif params.lower().startswith("rem "):
                before, sep, permission=params.partition("rem ")
                await buildconsole.send(f"lp user {username} permission set {permission} false")

@client.command()
@commands.has_any_role("Owner", "Admin")
async def buildconsole(ctx, display, *, cmd):
    channel=discord.utils.get(ctx.author.guild.text_channels, name="⚡︱build-console")
    await channel.send(cmd)
    console=client.get_channel(1026654816996446278)
    await asyncio.sleep(2)
    content=(await console.history(limit=1).flatten())[0].content
    if display=="true":
        await ctx.send(content)
    else:
        pass

@client.command()
@commands.has_any_role("Owner", "Admin")
async def buildserver(ctx, mode, command=""):
    if ctx.author.id != 968356025461768192:
        now=datetime.now()
        dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
        date, sep, time=dateTime.partition(" ")
        sendSMS(messageSubject="ZMP ALERT", messageBody=f"{date} | {time}\n\nTag: {ctx.author} | ID: {ctx.author.id} | Name: {ctx.author.nick}\n\nUser issued command:\n\"{ctx.message.content}\"")
    buildconsole=client.get_channel(1026654816996446278)
    if mode.lower()=="action":
        if command.lower()=="start":
            await ctx.send("Diagnosing issue...")
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result=sock.connect_ex(('127.0.0.1',25567))
            if result==0:
                await ctx.send("ㅤ\nServer open on local host")
                sock.close()
                sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ip=socket.gethostbyname("build.zmp.lol")
                result=sock.connect_ex((ip,25567))
                if result==0:
                    await ctx.send("ㅤ\nServer domain response check passed")
                    await buildconsole.send("ping")
                    await asyncio.sleep(2)
                    content=(await buildconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await asyncio.sleep(2)
                        content=(await buildconsole.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            await ctx.send("ㅤ\nServer is running")
                            await ctx.send("ㅤ\nNo issues found")
                            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await asyncio.sleep(2)
                            content=(await buildconsole.history(limit=1).flatten())[0].content
                            if content != "ping" and "```" in content:
                                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                                await ctx.send("ㅤ\nServer is running")
                                await ctx.send("ㅤ\nNo issues found")
                                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                            else:
                                await ctx.send("ㅤ\nDiscordSRV console response check failed.")
                                role=discord.utils.find(lambda r: r.name=='Owner', ctx.message.guild.roles)
                                if role not in ctx.author.roles:
                                    await ctx.send("ㅤ\nAlerting owner...")
                                    user=client.get_user(968356025461768192)
                                    msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
                                    before, sep, msg=str(msg).partition("<Message id=")
                                    msg, sep, after=str(msg).partition(" channel=<")
                                    msg=await ctx.channel.fetch_message(msg)
                                    for i in range(10):
                                        n=(i * 10)
                                        await msg.edit(content=f"ㅤ\nAlerting owner... {n}%")
                                        await user.send(f"Server is offline")
                                    await msg.edit(content=f"ㅤ\nAlerting owner... 100%")
                                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nServer domain response check failed")
                    await ctx.send("ㅤ\nStarting Dynamic IP address updater...")
                    os.startfile(r"C:\Users\Overdrive\Desktop\apps\DDNS.exe")
            else:
                await ctx.send("ㅤ\nServer is not open on local host")
                await ctx.send("ㅤ\nStarting server...")
                path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\build\\1--START.cmd"
                subprocess.Popen(f"start /wait cmd /c {path}1--START.cmd")
                await ctx.send("ㅤ\nServer startup initiated")
                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
            sock.close()
        elif mode.lower()=="stop":
            await ctx.send("Stopping server...")
            await buildconsole.send("stop")
            await ctx.send("ㅤ\nServer stopped")
    elif mode.lower()=="get":
        if command=="status":
            await ctx.send("Diagnosing...")
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result=sock.connect_ex(('127.0.0.1',25567))
            if result==0:
                await ctx.send("ㅤ\nServer open on local host")
                sock.close()
                sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ip=socket.gethostbyname("build.zmp.lol")
                result=sock.connect_ex((ip,25567))
                if result==0:
                    await ctx.send("ㅤ\nServer domain response check passed")
                    await buildconsole.send("ping")
                    await asyncio.sleep(2)
                    content=(await buildconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await asyncio.sleep(2)
                        content=(await buildconsole.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await asyncio.sleep(2)
                            content=(await buildconsole.history(limit=1).flatten())[0].content
                            if content != "ping" and "```" in content:
                                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            else:
                                await ctx.send("ㅤ\nDiscordSRV console response check failed")
                else:
                    await ctx.send("ㅤ\nServer domain response check failed")
            else:
                await ctx.send("ㅤ\nServer is not open on local host")
                await ctx.send("ㅤ\n**SERVER OFFLINE**")
            sock.close()
            path=(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\build")
            ssAndHide("BUILD", f"{path}")
            await ctx.send(file=discord.File(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\build\ssOfWindow.png"))
            os.remove(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\build\ssOfWindow.png")
        elif command.lower()=="whitelist":
            await buildconsole.send("whitelist list")
            await asyncio.sleep(4)
            content=(await buildconsole.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("players: ")
            content, sep, after=content.partition("\n")
            content, sep, after=content.partition("```")
            if content=="":
                await asyncio.sleep(2)
            else:
                pass
            await ctx.send(f"```{content}```")
        elif command.lower()=="players":
            await buildconsole.send("list")
            await asyncio.sleep(4)
            content=(await buildconsole.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("/list")
            before, sep, content=content.partition("] ")
            content, sep, after=content.partition("```")
            if content=="":
                await asyncio.sleep(2)
            else:
                pass
            await ctx.send(f"```{content}```")
        elif command.lower()=="tps":
            await buildconsole.send("tps")
            await asyncio.sleep(4)
            content=(await buildconsole.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("] ")
            content, sep, after=content.partition("```")
            if content=="":
                await asyncio.sleep(2)
            else:
                pass 
            await ctx.send(f"```{content}```")
    elif mode.lower()=="start":
        await ctx.send("Diagnosing issue...")
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result=sock.connect_ex(('127.0.0.1',25567))
        if result==0:
            await ctx.send("ㅤ\nServer open on local host")
            sock.close()
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip=socket.gethostbyname("build.zmp.lol")
            result=sock.connect_ex((ip,25567))
            if result==0:
                await ctx.send("ㅤ\nServer domain response check passed")
                await buildconsole.send("ping")
                await asyncio.sleep(2)
                content=(await buildconsole.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    await ctx.send("ㅤ\nServer is running")
                    await ctx.send("ㅤ\nNo issues found")
                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await asyncio.sleep(2)
                    content=(await buildconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await asyncio.sleep(2)
                        content=(await buildconsole.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            await ctx.send("ㅤ\nServer is running")
                            await ctx.send("ㅤ\nNo issues found")
                            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed.")
                            role=discord.utils.find(lambda r: r.name=='Owner', ctx.message.guild.roles)
                            if role not in ctx.author.roles:
                                print(ctx.author.id)
                                await ctx.send("ㅤ\nAlerting owner...")
                                user=client.get_user(968356025461768192)
                                msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
                                before, sep, msg=str(msg).partition("<Message id=")
                                msg, sep, after=str(msg).partition(" channel=<")
                                msg=await ctx.channel.fetch_message(msg)
                                for i in range(10):
                                    n=(i * 10)
                                    await msg.edit(content=f"ㅤ\nAlerting owner... {n}%")
                                    await user.send(f"Server is offline")
                                await msg.edit(content=f"ㅤ\nAlerting owner... 100%")
                                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
            else:
                await ctx.send("ㅤ\nServer domain response check failed")
                await ctx.send("ㅤ\nStarting Dynamic IP address updater...")
                os.startfile(r"C:\Users\Overdrive\Desktop\apps\DDNS.exe")
        else:
            await ctx.send("ㅤ\nServer is not open on local host")
            await ctx.send("ㅤ\nStarting server...")
            path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\build\\1--START.cmd"
            subprocess.Popen(f"start /wait cmd /c {path}1--START.cmd")
            await ctx.send("ㅤ\nServer startup initiated")
            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
        sock.close()
    elif mode.lower()=="get":
        if command=="status":
            await ctx.send("Diagnosing...")
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result=sock.connect_ex(('127.0.0.1',25567))
            if result==0:
                await ctx.send("ㅤ\nServer open on local host")
                sock.close()
                sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ip=socket.gethostbyname("build.zmp.lol")
                result=sock.connect_ex((ip,25567))
                if result==0:
                    await ctx.send("ㅤ\nServer domain response check passed")
                    await buildconsole.send("ping")
                    await asyncio.sleep(2)
                    content=(await buildconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await asyncio.sleep(2)
                        content=(await buildconsole.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await asyncio.sleep(2)
                            content=(await buildconsole.history(limit=1).flatten())[0].content
                            if content != "ping" and "```" in content:
                                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            else:
                                print("ㅤ\nDiscordSRV console response check failed")
                else:
                    await ctx.send("ㅤ\nServer domain response check failed")
            else:
                await ctx.send("ㅤ\nServer is not open on local host")
            sock.close()
    elif mode.lower()=="stop":
        await ctx.send("Stopping server...")
        await buildconsole.send("stop")
        await ctx.send("ㅤ\nServer stopped")

### MZMP ###

@client.command()
@commands.has_any_role("Owner", "Admin")
async def mzmpstop(ctx):
    await client.get_channel(1006963820830404658).send("stop")

@client.command(pass_context=True)
@commands.has_any_role("Owner", "Admin", "Moderator")
async def mzmpwhitelist(ctx, version, *, tag):
    if version.lower()=="java":
        command=f"whitelist add {tag}"
    elif version.lower()=="bedrock":
        bTag=tag.replace(" ", "_")
        command=f"whitelist add .{bTag}"
    channel=discord.utils.get(ctx.author.guild.text_channels, name="⚡︱modded-console")
    await channel.send(command)
    await asyncio.sleep(2)
    console=client.get_channel(1006963820830404658)
    content=(await console.history(limit=1).flatten())[0].content
    if 'already whitelisted' in content:
        if version.lower()=="java":
            print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
        elif version.lower()=="bedrock":
            print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
        await ctx.message.add_reaction("✅")
        await ctx.message.add_reaction("⚠️")
        await ctx.author.send("**You're already whitelisted!**\n\nIf you are having issues with connecting to the server, ask for help in one of the help channels.")
    elif 'to the whitelist' in content:
        if version.lower()=="java":
            print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
        elif version.lower()=="bedrock":
            print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
        await ctx.message.add_reaction("✅")
    elif 'player does not exist' in content:
        await ctx.author.send("**That didnt work!**\n\nBe sure you entered the right tag, including capitalization!\nIf you are trying to join on bedrock, try to join before trying to whitelist yourself!")
        await ctx.message.add_reaction("❌")
        if version.lower()=="java":
            print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
        elif version.lower()=="bedrock":
            print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
    elif 'whitelist add' in content:
        await asyncio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
        if 'already whitelisted' in content:
            if version.lower()=="java":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
            elif version.lower()=="bedrock":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
            await ctx.message.add_reaction("✅")
            await ctx.message.add_reaction("⚠️")
            await ctx.author.send("**You're already whitelisted!**\n\nIf you are having issues with connecting to the server, ask for help in one of the help channels.")
        elif 'to the whitelist' in content:
            if version.lower()=="java":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
            elif version.lower()=="bedrock":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
            await ctx.message.add_reaction("✅")
        elif 'player does not exist' in content:
            await ctx.author.send("**That didnt work!**\n\nBe sure you entered the right tag, including capitalization!\nIf you are trying to join on bedrock, try to join before trying to whitelist yourself!")
            await ctx.message.add_reaction("❌")
            if version.lower()=="java":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
            elif version.lower()=="bedrock":
                print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
        elif 'whitelist add' in content:
            await asyncio.sleep(4)
            content=(await console.history(limit=1).flatten())[0].content
            if 'already whitelisted' in content:
                if version.lower()=="java":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
                elif version.lower()=="bedrock":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  RESOLVED: User is already whitelisted\n----WHITELIST----\n\n")
                await ctx.message.add_reaction("✅")
                await ctx.message.add_reaction("⚠️")
                await ctx.author.send("**You're already whitelisted!**\n\nIf you are having issues with connecting to the server, ask for help in one of the help channels.")
            elif 'to the whitelist' in content:
                if version.lower()=="java":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
                elif version.lower()=="bedrock":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  SUCCESSFUL: User was added to the whitelist\n----WHITELIST----\n\n")
                await ctx.message.add_reaction("✅")
            elif 'player does not exist' in content:
                await ctx.author.send("**That didnt work!**\n\nBe sure you entered the right tag, including capitalization!\nIf you are trying to join on bedrock, try to join before trying to whitelist yourself!")
                await ctx.message.add_reaction("❌")
                if version.lower()=="java":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
                elif version.lower()=="bedrock":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - player does not exist\n----WHITELIST----\n\n")
            elif 'whitelist add' in content:
                await ctx.message.add_reaction("❌")
                await ctx.author.send("Sorry, but you were unable to be whitelisted at this time. Please contact Zoe for further information.")
                if version.lower()=="java":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {tag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - unknown error\n----WHITELIST----\n\n")
                elif version.lower()=="bedrock":
                    print(f"\n\n----WHITELIST----\n{ctx.author} attempted to whitelist {bTag}...\nSTATUS:\n  UNSUCCESSFUL: User was not added to the whitelist - unknown error\n----WHITELIST----\n\n")

@client.command()
@commands.has_any_role("Owner", "Admin", "Moderator", "Helper")
async def mzmpstatus(ctx):
    mzmpconsole=client.get_channel(1006963820830404658)
    await ctx.send("Diagnosing...")
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result=sock.connect_ex(('127.0.0.1',25566))
    if result==0:
        await ctx.send("ㅤ\nServer open on local host")
        sock.close()
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip=socket.gethostbyname("modded.zmp.lol")
        result=sock.connect_ex((ip,25566))
        if result==0:
            await ctx.send("ㅤ\nServer domain response check passed")
            await mzmpconsole.send("ping")
            await asyncio.sleep(2)
            content=(await mzmpconsole.history(limit=1).flatten())[0].content
            if content != "ping" and "```" in content:
                await ctx.send("ㅤ\nDiscordSRV console response check passed")
            else:
                await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                await asyncio.sleep(2)
                content=(await mzmpconsole.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await asyncio.sleep(2)
                    content=(await mzmpconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed")
        else:
            await ctx.send("ㅤ\nServer domain response check failed")
    else:
        await ctx.send("ㅤ\nServer is not open on local host")
        await ctx.send("ㅤ\n**SERVER OFFLINE**")
    
    path=(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\modded")
    ssAndHide("MODDED", f"{path}")
    await ctx.send(file=discord.File(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\modded\ssOfWindow.png"))
    os.remove(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\modded\ssOfWindow.png")
@client.command()

@commands.has_any_role("Owner", "Admin", "Moderator")
async def mzmpstart(ctx):
    mzmpconsole=client.get_channel(1006963820830404658)
    await ctx.send("Diagnosing issue...")
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result=sock.connect_ex(('127.0.0.1',25566))
    if result==0:
        await ctx.send("ㅤ\nServer open on local host")
        sock.close()
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip=socket.gethostbyname("modded.zmp.lol")
        result=sock.connect_ex((ip,25566))
        if result==0:
            await ctx.send("ㅤ\nServer domain response check passed")
            await mzmpconsole.send("ping")
            await asyncio.sleep(2)
            content=(await mzmpconsole.history(limit=1).flatten())[0].content
            if content != "ping" and "```" in content:
                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                await ctx.send("ㅤ\nServer is running")
                await ctx.send("ㅤ\nNo issues found")
                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
            else:
                await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                await asyncio.sleep(2)
                content=(await mzmpconsole.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    await ctx.send("ㅤ\nServer is running")
                    await ctx.send("ㅤ\nNo issues found")
                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await asyncio.sleep(2)
                    content=(await mzmpconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed.")
                        role=discord.utils.find(lambda r: r.name=='Owner', ctx.message.guild.roles)
                        if role not in ctx.author.roles:
                            await ctx.send("ㅤ\nAlerting owner...")
                            user=client.get_user(968356025461768192)
                            msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
                            before, sep, msg=str(msg).partition("<Message id=")
                            msg, sep, after=str(msg).partition(" channel=<")
                            msg=await ctx.channel.fetch_message(msg)
                            for i in range(10):
                                n=(i * 10)
                                await msg.edit(content=f"ㅤ\nAlerting owner... {n}%")
                                await user.send(f"Server is offline")
                            await msg.edit(content=f"ㅤ\nAlerting owner... 100%")
                            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
        else:
            await ctx.send("ㅤ\nServer domain response check failed")
            await ctx.send("ㅤ\nStarting Dynamic IP address updater...")
            os.startfile(r"C:\Users\Overdrive\Desktop\apps\DDNS.exe")
    else:
        await ctx.send("ㅤ\nServer is not open on local host")
        await ctx.send("ㅤ\nStarting server...")
        path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\mzmp\\1--START.cmd"
        subprocess.Popen(f"start /wait cmd /c {path}1--START.cmd", shell=True)
        await ctx.send("ㅤ\nServer startup initiated")
        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
    sock.close()

@client.command()
async def mzmpip(ctx):
    await ctx.send("modded.zmp.lol:25566")

@client.command()
@commands.has_any_role("Owner", "Admin")
async def mzmplockdown(ctx, mode="staff"):
    console=client.get_channel(1006963820830404658)
    await console.send("whitelist list")
    await asyncio.sleep(2)
    content=(await console.history(limit=1).flatten())[0].content
    a=content.split("There are ",1)[1]
    before, sep, after=a.partition(" whitelisted players: ")
    whitelistCount=""
    for m in before:
        if m.isdigit():
            whitelistCount=whitelistCount + m
    before, sep, after=after.partition("\n")
    before, sep, after=before.partition("```")
    array=before.split(", ")
    owners=["OverdriveZR"]
    admins=["Dimensional_Duck"]
    mods=["Mxnsoo", "Swampyemerson"]
    helpers=["doggey200000", "FoxtatoThePotato"]
    if mode != "end" and mode != "backup" and mode != "restore":
        if ctx.author.id != 968356025461768192:
            now=datetime.now()
            dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
            date, sep, time=dateTime.partition(" ")
            sendSMS(messageSubject="ZMP ALERT", messageBody=f"{date} | {time}\n\nTag: {ctx.author} | ID: {ctx.author.id} | Name: {ctx.author.nick}\n\nUser issued command:\n\"{ctx.message.content}\"")
        num=0
        f=open(f"MZMPWLbackup{whitelistCount}.txt", "w+")
        await console.send("whitelist list")
        await asyncio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
        before, sep, content=content.partition("players: ")
        content, sep, after=content.partition("\n")
        content, sep, after=content.partition("```")
        f.write(content)
        f.close()
        print(f"{ctx.author} created a backup")
        for fname in os.listdir():
            if fname.startswith("WLbackup"):
                if num <= int(re.search(r'\d+', fname).group(0)):
                    num=int(re.search(r'\d+', fname).group(0))
        await ctx.send(f"A backup was created, consisting of {num} player accounts")
        await ctx.send("Initiating lockdown")
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        add=100/num
        players=0
        for i in array:
            players=players + 1
            percent=percent + add
            await console.send(f"whitelist remove {i}")
            await msg.edit(content=f"Initiating lockdown... {round(percent)}%")
        f.close()
    if mode != "end" and mode != "backup" and mode != "restore":
        await console.send("kickall")
    if mode != "end" and mode != "backup" and mode != "restore":
        await ctx.send(f"Lockdown started. Whitelisting {mode}")
    if mode=="owners":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    elif mode=="admins":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        for i in admins:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in admins:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    elif mode=="mods":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        for i in mods:
            count += 1
        for i in admins:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in mods :
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in admins:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    elif mode=="helpers":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        for i in helpers:
            count += 1
        for i in mods:
            count += 1
        for i in admins:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in helpers:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in mods :
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in admins:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    elif mode=="staff":
        msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
        before, sep, msg=str(msg).partition("<Message id=")
        msg, sep, after=str(msg).partition(" channel=<")
        msg=await ctx.channel.fetch_message(msg)
        percent=0
        count=0
        for i in owners:
            count += 1
        for i in helpers:
            count += 1
        for i in mods:
            count += 1
        for i in admins:
            count += 1
        add=100/count
        players=0
        for i in owners:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in helpers:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in mods :
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
        for i in admins:
            players += 1
            percent=percent + add
            await console.send(f"whitelist add {i}")
            await msg.edit(content=f"Whitelisting {mode}... {round(percent)}%")
    if mode != "end" and mode != "backup" and mode != "restore":
        await ctx.send(f"{mode} whitelisted. Lockdown complete.")
        print(f"\n{ctx.author} started a lockdown\n")
    elif mode=="end":
        f=open("MZMPlockdown_whitelist.txt")
        if f.mode=='r':
            contents=f.read()
            array=contents.split(", ")
            await ctx.send("Ending lockdown. Rewhitelisting players...")
            for i in owners:
                await console.send(f"whitelist add {i}")
            for i in admins:
                await console.send(f"whitelist add {i}")
            for i in mods:
                await console.send(f"whitelist add {i}")
            for i in helpers:
                await console.send(f"whitelist add {i}")
            for i in array:
                await console.send(f"whitelist add {i}")
            f.close()
            os.remove("MZMPlockdown_whitelist.txt")
            print(f"\n{ctx.author} ended a lockdown\n")
            await ctx.send("Lockdown ended")
    elif mode=="restore":
        num=0
        for fname in os.listdir():
            if fname.startswith("WLbackup"):
                if num <= int(re.search(r'\d+', fname).group(0)):
                    num=int(re.search(r'\d+', fname).group(0))
        f=open(f"MZMPWLbackup{num}.txt")
        if f.mode=='r':
            contents=f.read()
            array=contents.split(", ")
            await ctx.send(f"Restoring to backup of {num} whitelisted players")
            msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
            before, sep, msg=str(msg).partition("<Message id=")
            msg, sep, after=str(msg).partition(" channel=<")
            msg=await ctx.channel.fetch_message(msg)
            percent=0
            add=100/num
            players=0
            for i in array:
                players=players + 1
                percent=percent + add
                await console.send(f"whitelist add {i}")
                await msg.edit(content=f"Restoring to backup of {num} whitelisted players\n{round(percent)}%  ({players}/{num})")
            f.close()
            await ctx.send("Whitelist successfully restored")
            print(f"\n{ctx.author} restored the whitelist\n")
    elif mode=="backup":
        num=0
        f=open(f"MZMPWLbackup{whitelistCount}.txt", "w+")
        await console.send("whitelist list")
        await asyncio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
        before, sep, content=content.partition("players: ")
        content, sep, after=content.partition("\n")
        content, sep, after=content.partition("```")
        f.write(content)
        f.close()
        print(f"{ctx.author} created a backup")
        for fname in os.listdir():
            if fname.startswith("WLbackup"):
                if num <= int(re.search(r'\d+', fname).group(0)):
                    num=int(re.search(r'\d+', fname).group(0))
        await ctx.send(f"A backup was created, consisting of {num} player accounts")
    if mode != "end":
        f=open("MZMPlockdown_whitelist.txt", "w+")
        for i in array:
            f.write(f"{i}, ")
        f.close()

@client.command()
@commands.has_any_role("Owner", "Admin", "Moderator")
async def mzmpremwl(ctx, version, *, tag):
    if version.lower()=="java":
        command=f"whitelist remove {tag}"
        print(f"{tag} was removed from the whitelist")
    elif version.lower()=="bedrock":
        bTag=tag.replace(" ", "_")
        command=f"whitelist remove .{bTag}"
        print(f"{bTag} was removed from the whitelist")
    channel=discord.utils.get(ctx.author.guild.text_channels, name="⚡︱modded-console")
    await channel.send(command)

@client.command()
@commands.has_any_role("Owner", "Moderator", "Admin")
async def mzmpmcban(ctx, tag, *, reason="None given"):
    print(f"{tag} was removed banned from the minecraft server by {ctx.author} with reason \"Banned by {ctx.author} in discord with reason: {reason}\"")
    channel=discord.utils.get(ctx.author.guild.text_channels, name="⚡︱modded-console")
    await channel.send(f"ban {tag} Banned by {ctx.author} in discord with reason: {reason}")
    await ctx.send(f"Banned {tag} with reason \"{reason}\"")

@client.command()
@commands.has_any_role("Owner", "Moderator", "Admin")
async def mzmpmcunban(ctx, tag):
    print(f"{tag} was removed unbanned from the minecraft server by {ctx.author}")
    channel=discord.utils.get(ctx.author.guild.text_channels, name="⚡︱modded-console")
    await channel.send(f"pardon {tag}")
    await ctx.send(f"Unbanned {tag}")

@client.command()
@commands.has_any_role("Owner", "Moderator", "Admin")
async def mzmpmcpardon(ctx, tag):
    print(f"{tag} was removed unbanned from the minecraft server by {ctx.author}")
    channel=discord.utils.get(ctx.author.guild.text_channels, name="⚡︱modded-console")
    await channel.send(f"pardon {tag}")
    await ctx.send(f"Unbanned {tag}")

@client.command()
@commands.has_any_role("Owner", "Admin")
async def mzmplp(ctx, *, params):
    mzmpconsole=client.get_channel(1006963820830404658)
    if params.lower().startswith("editor"):
        await mzmpconsole.send("lp editor")
        await asyncio.sleep(2)
        content=(await mzmpconsole.history(limit=1).flatten())[0].content
        if "https://luckperms.net/editor/" in content:
            before, sep, editor=content.partition("https://luckperms.net/editor/")
            editor, sep, after=editor.partition("\n")
            if "```" in editor:
                editor, sep, after=editor.partition("```")
                await ctx.author.send(f"https://luckperms.net/editor/{editor}")
            else:
                await ctx.author.send(editor)
        else:
            await asyncio.sleep(2)
            content=(await mzmpconsole.history(limit=1).flatten())[0].content
            if "https://luckperms.net/editor/" in content:
                before, sep, editor=content.partition("https://luckperms.net/editor/")
                editor, sep, after=editor.partition("\n")
                if "```" in editor:
                    editor, sep, after=editor.partition("```")
                    await ctx.author.send(f"https://luckperms.net/editor/{editor}")
                else:
                    await ctx.author.send(editor)
            else:
                await asyncio.sleep(2)
                content=(await mzmpconsole.history(limit=1).flatten())[0].content
                if "https://luckperms.net/editor/" in content:
                    if "https://luckperms.net/editor/" in content:
                        before, sep, editor=content.partition("https://luckperms.net/editor/")
                        editor, sep, after=editor.partition("\n")
                        if "```" in editor:
                            editor, sep, after=editor.partition("```")
                        await ctx.author.send(f"https://luckperms.net/editor/{editor}")
                    else:
                        await ctx.author.send(editor)
                else:
                    ctx.author.send("unable to get Luckperms Data")
    elif params.lower().startswith("user "):
        before, sep, after=params.partition("user ")
        username, sep, params=after.partition(" ")
        if params.lower().startswith("group "):
            before, sep, params=params.partition("group ")
            if params.lower().startswith("addrem "):
                before, sep, params=params.partition("addrem ")
                add, sep, rem=params.partition(" ")
                await mzmpconsole.send(f"lp user {username} group add {add}")
                await mzmpconsole.send(f"lp user {username} group remove {rem}")
            elif params.lower().startswith("add "):
                before, sep, add=params.partition("add ")
                await mzmpconsole.send(f"lp user {username} group add {add}")
            elif params.lower().startswith("rem "):
                before, sep, rem=params.partition("rem ")
                await mzmpconsole.send(f"lp user {username} group remove {rem}")
        elif params.lower().startswith("permission "):
            before, sep, params=params.partition("permission ")
            if params.lower().startswith("add "):
                before, sep, permission=params.partition("add ")
                await mzmpconsole.send(f"lp user {username} permission set {permission} true")
            elif params.lower().startswith("rem "):
                before, sep, permission=params.partition("rem ")
                await mzmpconsole.send(f"lp user {username} permission set {permission} false")

@client.command()
@commands.has_any_role("Owner", "Admin")
async def mzmpconsole(ctx, display, *, cmd):
    channel=discord.utils.get(ctx.author.guild.text_channels, name="⚡︱modded-console")
    await channel.send(cmd)
    console=client.get_channel(1006963820830404658)
    await asyncio.sleep(2)
    content=(await console.history(limit=1).flatten())[0].content
    if display=="true":
        await ctx.send(content)
    else:
        pass

@client.command()
@commands.has_any_role("Owner", "Admin")
async def mzmpserver(ctx, mode, command=""):
    if ctx.author.id != 968356025461768192:
        now=datetime.now()
        dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
        date, sep, time=dateTime.partition(" ")
        sendSMS(messageSubject="ZMP ALERT", messageBody=f"{date} | {time}\n\nTag: {ctx.author} | ID: {ctx.author.id} | Name: {ctx.author.nick}\n\nUser issued command:\n\"{ctx.message.content}\"")
    mzmpconsole=client.get_channel(1006963820830404658)
    if mode.lower()=="action":
        if command.lower()=="start":
            await ctx.send("Diagnosing issue...")
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result=sock.connect_ex(('127.0.0.1',25566))
            if result==0:
                await ctx.send("ㅤ\nServer open on local host")
                sock.close()
                sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ip=socket.gethostbyname("modded.zmp.lol")
                result=sock.connect_ex((ip,25566))
                if result==0:
                    await ctx.send("ㅤ\nServer domain response check passed")
                    await mzmpconsole.send("ping")
                    await asyncio.sleep(2)
                    content=(await mzmpconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await asyncio.sleep(2)
                        content=(await mzmpconsole.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            await ctx.send("ㅤ\nServer is running")
                            await ctx.send("ㅤ\nNo issues found")
                            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await asyncio.sleep(2)
                            content=(await mzmpconsole.history(limit=1).flatten())[0].content
                            if content != "ping" and "```" in content:
                                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                                await ctx.send("ㅤ\nServer is running")
                                await ctx.send("ㅤ\nNo issues found")
                                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                            else:
                                await ctx.send("ㅤ\nDiscordSRV console response check failed.")
                                role=discord.utils.find(lambda r: r.name=='Owner', ctx.message.guild.roles)
                                if role not in ctx.author.roles:
                                    await ctx.send("ㅤ\nAlerting owner...")
                                    user=client.get_user(968356025461768192)
                                    msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
                                    before, sep, msg=str(msg).partition("<Message id=")
                                    msg, sep, after=str(msg).partition(" channel=<")
                                    msg=await ctx.channel.fetch_message(msg)
                                    for i in range(10):
                                        n=(i * 10)
                                        await msg.edit(content=f"ㅤ\nAlerting owner... {n}%")
                                        await user.send(f"Server is offline")
                                    await msg.edit(content=f"ㅤ\nAlerting owner... 100%")
                                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nServer domain response check failed")
                    await ctx.send("ㅤ\nStarting Dynamic IP address updater...")
                    os.startfile(r"C:\Users\Overdrive\Desktop\apps\DDNS.exe")
            else:
                await ctx.send("ㅤ\nServer is not open on local host")
                await ctx.send("ㅤ\nStarting server...")
                path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\mzmp\\1--START.cmd"
                subprocess.Popen(f"start /wait cmd /c {path}1--START.cmd", shell=True)
                await ctx.send("ㅤ\nServer startup initiated")
                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
            sock.close()
        elif mode.lower()=="stop":
            await ctx.send("Stopping server...")
            await mzmpconsole.send("stop")
            await ctx.send("ㅤ\nServer stopped")
    elif mode.lower()=="get":
        if command=="status":
            await ctx.send("Diagnosing...")
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result=sock.connect_ex(('127.0.0.1',25566))
            if result==0:
                await ctx.send("ㅤ\nServer open on local host")
                sock.close()
                sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ip=socket.gethostbyname("modded.zmp.lol")
                result=sock.connect_ex((ip,25566))
                if result==0:
                    await ctx.send("ㅤ\nServer domain response check passed")
                    await mzmpconsole.send("ping")
                    await asyncio.sleep(2)
                    content=(await mzmpconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await asyncio.sleep(2)
                        content=(await mzmpconsole.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await asyncio.sleep(2)
                            content=(await mzmpconsole.history(limit=1).flatten())[0].content
                            if content != "ping" and "```" in content:
                                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            else:
                                await ctx.send("ㅤ\nDiscordSRV console response check failed")
                else:
                    await ctx.send("ㅤ\nServer domain response check failed")
            else:
                await ctx.send("ㅤ\nServer is not open on local host")
                await ctx.send("ㅤ\n**SERVER OFFLINE**")
            sock.close()
            path=(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\modded")
            ssAndHide("MODDED", f"{path}")
            await ctx.send(file=discord.File(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\modded\ssOfWindow.png"))
            os.remove(r"C:\Users\Overdrive\Desktop\MINECRAFT_SERVERS\modded\ssOfWindow.png")
        elif command.lower()=="whitelist":
            await mzmpconsole.send("whitelist list")
            await asyncio.sleep(4)
            content=(await mzmpconsole.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("players: ")
            content, sep, after=content.partition("\n")
            content, sep, after=content.partition("```")
            if content=="":
                await asyncio.sleep(2)
            else:
                pass
            await ctx.send(f"```{content}```")
        elif command.lower()=="players":
            await mzmpconsole.send("list")
            await asyncio.sleep(4)
            content=(await mzmpconsole.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("/list")
            before, sep, content=content.partition("] ")
            content, sep, after=content.partition("```")
            if content=="":
                await asyncio.sleep(2)
            else:
                pass
            await ctx.send(f"```{content}```")
        elif command.lower()=="tps":
            await mzmpconsole.send("tps")
            await asyncio.sleep(4)
            content=(await mzmpconsole.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("] ")
            content, sep, after=content.partition("```")
            if content=="":
                await asyncio.sleep(2)
            else:
                pass 
            await ctx.send(f"```{content}```")
    elif mode.lower()=="start":
        await ctx.send("Diagnosing issue...")
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result=sock.connect_ex(('127.0.0.1',25566))
        if result==0:
            await ctx.send("ㅤ\nServer open on local host")
            sock.close()
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip=socket.gethostbyname("modded.zmp.lol")
            result=sock.connect_ex((ip,25566))
            if result==0:
                await ctx.send("ㅤ\nServer domain response check passed")
                await mzmpconsole.send("ping")
                await asyncio.sleep(2)
                content=(await mzmpconsole.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    await ctx.send("ㅤ\nServer is running")
                    await ctx.send("ㅤ\nNo issues found")
                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await asyncio.sleep(2)
                    content=(await mzmpconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await asyncio.sleep(2)
                        content=(await mzmpconsole.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            await ctx.send("ㅤ\nServer is running")
                            await ctx.send("ㅤ\nNo issues found")
                            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed.")
                            role=discord.utils.find(lambda r: r.name=='Owner', ctx.message.guild.roles)
                            if role not in ctx.author.roles:
                                print(ctx.author.id)
                                await ctx.send("ㅤ\nAlerting owner...")
                                user=client.get_user(968356025461768192)
                                msg=await ctx.channel.fetch_message(ctx.channel.last_message_id)
                                before, sep, msg=str(msg).partition("<Message id=")
                                msg, sep, after=str(msg).partition(" channel=<")
                                msg=await ctx.channel.fetch_message(msg)
                                for i in range(10):
                                    n=(i * 10)
                                    await msg.edit(content=f"ㅤ\nAlerting owner... {n}%")
                                    await user.send(f"Server is offline")
                                await msg.edit(content=f"ㅤ\nAlerting owner... 100%")
                                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
            else:
                await ctx.send("ㅤ\nServer domain response check failed")
                await ctx.send("ㅤ\nStarting Dynamic IP address updater...")
                os.startfile(r"C:\Users\Overdrive\Desktop\apps\DDNS.exe")
        else:
            await ctx.send("ㅤ\nServer is not open on local host")
            await ctx.send("ㅤ\nStarting server...")
            path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\mzmp\\1--START.cmd"
            subprocess.Popen(f"start /wait cmd /c {path}1--START.cmd", shell=True)
            await ctx.send("ㅤ\nServer startup initiated")
            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
        sock.close()
    elif mode.lower()=="get":
        if command=="status":
            await ctx.send("Diagnosing...")
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result=sock.connect_ex(('127.0.0.1',25566))
            if result==0:
                await ctx.send("ㅤ\nServer open on local host")
                sock.close()
                sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ip=socket.gethostbyname("modded.zmp.lol")
                result=sock.connect_ex((ip,25566))
                if result==0:
                    await ctx.send("ㅤ\nServer domain response check passed")
                    await mzmpconsole.send("ping")
                    await asyncio.sleep(2)
                    content=(await mzmpconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await asyncio.sleep(2)
                        content=(await mzmpconsole.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await asyncio.sleep(2)
                            content=(await mzmpconsole.history(limit=1).flatten())[0].content
                            if content != "ping" and "```" in content:
                                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            else:
                                print("ㅤ\nDiscordSRV console response check failed")
                else:
                    await ctx.send("ㅤ\nServer domain response check failed")
            else:
                await ctx.send("ㅤ\nServer is not open on local host")
            sock.close()
    elif mode.lower()=="stop":
        await ctx.send("Stopping server...")
        await mzmpconsole.send("stop")
        await ctx.send("ㅤ\nServer stopped")

@client.event
async def on_raw_reaction_add(payload):
    if payload.message_id==1005259643326582805:
        channel=client.get_channel(payload.channel_id)
        message=await channel.fetch_message(payload.message_id)
        user=client.get_user(payload.user_id)
        emoji=client.get_emoji(1005266474778247219)
        await message.remove_reaction(emoji, user)
    emojiName=str(payload)
    emojiName, sep, after=emojiName.partition("event_type=")
    before, sep, emojiName=emojiName.partition("animated=")
    before, sep, emojiName=emojiName.partition("name='")
    emojiName, sep, after=emojiName.partition("' id")
    user=str(payload)
    before, sep, user=user.partition("member=<Member id=")
    user, sep, after=user.partition("bot=")
    before, sep, user=user.partition("name='")
    user, sep, after=user.partition("' discriminator='")
    discriminator=str(payload)
    before, sep, discriminator=discriminator.partition("discriminator='")
    discriminator, sep, after=discriminator.partition("' bot=")
    serverID=str(payload)
    before, sep, serverID=serverID.partition("guild=<Guild id=")
    serverID, sep, after=serverID.partition(" name='")
    serverName=str(payload)
    before, sep, serverName=serverName.partition("guild=<Guild id=")
    before, sep, serverName=serverName.partition(" name='")
    serverName, sep, after=serverName.partition("'")
    print(f"{user}#{discriminator} added reaction ({emojiName}) in server {serverName} ({serverID}).")
    f=open("recentReactions.txt", "a", encoding="utf-8")
    f.write(f"{emojiName}, ")
    f.close()
    f=open("recentReactions.txt", "r", encoding="utf-8")
    contents=f.read()
    if secret("reactionCombo") in contents:
        f.close()
        owner_channel=client.get_channel(990393301247098900)
        now=datetime.now()
        dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
        date, sep, time=dateTime.partition(" ")
        sendSMS(messageSubject="URGENT ZMP ALERT", messageBody=f"{date} | {time}\n\nTag: {user}#{discriminator}\nUser initiated a server-wide halt. All servers have stopped, and the discord bot has been closed.\"")
        stopServer("ZMP")
        await asyncio.sleep(2)
        stopServer("MZMP")
        await asyncio.sleep(2)
        stopServer("BUILD")
        await owner_channel.send(f"**WARNING**\n\n**All servers have halted.**\n{user}#{discriminator} initiated this lockdown by reporting that **Zoe's account has been hacked.**\n**DO NOT TRUST ANY MESSAGES FROM ZOE AT THIS TIME**\nOnly after the servers have started should you trust her account.\nThis bot will now terminate.")
        os.remove("recentReactions.txt")
        await client.close()
    reactions=secret("reactionCombo").split(", ")
    for i in reactions:
        if i not in emojiName:
            f.close()
            os.remove("recentReactions.txt")
    else:
        f.close()

client.run(secret("TOKEN"))
