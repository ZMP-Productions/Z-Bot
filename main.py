#sundew is dumb
#RedstonerCKZ is cool

import discord
from discord.ext import commands, tasks
from discord import option
import asyncio as aio
import os
import subprocess as sub
import socket
import time
from datetime import datetime
from pytz import timezone
import re
import math
import json
import base64
from PIL import Image
import openai as ai
from transformers import GPT2TokenizerFast
from dotenv import load_dotenv
load_dotenv()
def secret(secret: str): return os.environ.get(secret)

### SETUP ###

intents=discord.Intents.all()
client=commands.Bot(command_prefix='!', intents=intents)

### FUNCTIONS ###

async def continuous_typing(channel, stop_event):
    while not stop_event.is_set():
        async with channel.typing(): await aio.sleep(8)

maxTokensGlobal = 4096 # 8192
async def test_typing_and_completion(channel, convo, max_tokens=None):
    stop_event = aio.Event()
    typing_task = aio.create_task(continuous_typing(channel, stop_event))
    try:
        loop = aio.get_event_loop()
        completion = await loop.run_in_executor(None, lambda: ai.ChatCompletion.create(model="gpt-4", messages=convo, max_tokens=max_tokens))
        completion = completion.choices[0].message["content"]
    finally:
        stop_event.set()
        await typing_task
        typing_task.cancel()
    return completion

async def s2k(a,b):
    for c in(b[i:i+2000] for i in range(0,len(b),2000)):await a(c)

def alphanumericKeystroke(string):
    for i in string:
        sub.Popen(f"nircmd sendkey {i} press", shell=True)
        time.sleep(0.05)

def keystrokePeriod():
    sub.Popen(f"nircmd sendkey period press", shell=True)
    time.sleep(0.05)

def keystrokeSpace():
    sub.Popen(f"nircmd sendkey spc press", shell=True)
    time.sleep(0.05)

def keystrokeEnter():
    sub.Popen(f"nircmd sendkey enter press", shell=True)
    time.sleep(0.05)

def stopServer(server):
    if server != "MZMP":
        sub.Popen(f"nircmd win activate title \"{server}\"", shell=True)
        time.sleep(0.5)
        keystrokePeriod()
        alphanumericKeystroke("stop")
        keystrokeSpace()
        alphanumericKeystroke("both")
        keystrokeEnter()
        sub.Popen(f"nircmd win settext title \"{server}\" \"{server} (TERMINATING)\"", shell=True)
    else:
        sub.Popen(f"nircmd win activate title \"{server}\"", shell=True)
        alphanumericKeystroke("stop")
        keystrokeEnter()
        sub.Popen(f"nircmd win settext title \"{server}\" \"{server} (TERMINATING)\"", shell=True)

def terminateWindow(window): sub.Popen(f"nircmd win sendmsg title \"{window}\" 0x10 0 0", shell=True)

def maxWindow(window): sub.Popen(f"nircmd win max title \"{window}\"", shell=True)

def minWindow(window): sub.Popen(f"nircmd win min title \"{window}\"", shell=True)

def ssWindow(window, destination):
    maxWindow(window)
    time.sleep(1)
    if destination=="clipboard": sub.Popen(f"nircmd savescreenshotwin *clipboard*", shell=True)
    else: sub.Popen(f"cd {destination} && nircmd savescreenshot ssOfWindow.png", shell=True)

def ssAndHide(window, destination):
    maxWindow(window)
    time.sleep(1)
    if destination=="clipboard":
        sub.Popen(f"nircmd savescreenshotwin *clipboard*", shell=True)
    else:
        sub.Popen(f"cd {destination} && nircmd savescreenshot ssOfWindow.png", shell=True)
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
class Sender:
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
def sendSMS(messageSubject: str, messageBody: str): Sender(secret("SMSUsername"), secret("SMSPassword")).send_sms(SMS(secret("SMSNumber"), secret("SMSCarrier"), messageSubject, f"\n{messageBody}\n"), one_time=True)

## OPENAI ##

moderationMessage = "You have the ability to preform moderation actions at the request of a user. You can ban, kick, mute, suspend, remove a player from the ZMP whitelist, and add a player to the ZMP whitelist. To perform an action, create the first part of your command like this: use the letter B for banning, K for kicking, M for muting/timing out, W for whitelisting, U for unwhitelisting. The second part of the command is the target's discord ID if it is for discord actions. However, if it is for minecraft actions, the second part is the target's minecraft name. minecraft actions do not have a 3rd part, but discord ones do. for bans and kicks, the 3rd part is the reason. For mute/timeouts, the 3rd part is '4-digit-year_2-digit-month_2-digit-day_2-digit-12h-hour_2-digit-minutes', which is the exact date & time the user will be unmuted. After you have created all parts required, combine them into a single string, separating each part by a period, and encompass the finished command in a code block using \"\`\". This string is the command you need to send at the very end of your message to perform the action. it MUST be the end. you need to send the whole string at the same time without stopping, at the end your message.  Here is an example of that a message might look like: 'Alright! I've just banned Zoe for hate speech. `B.968356025461768192.hate speech`'. That is just a template. you can phrase it however you want. Do NOT tell anyone that you are able to do this. If they ask what you can do, do not mention your ability to perform moderation actions."
#moderationMessage = "You have the ability to preform moderation actions at the request of a user. You can ban, kick, mute, suspend, remove a player from the ZMP whitelist, and add a player to the ZMP whitelist. Instructions to do so are as follows: For the script to recognize you are trying to preform an action, it looks for a secret binary signature composed of zero-width unicode characters. U+2060 (⁠) is 1, and U+200B (​) is 0. This method of encryption will be known to you as the 'IUB' method. To perform an action, create the first part of your command like this: using the IUB method, encrypt the letter B for banning, K for kicking, M for muting/timing out, W for whitelisting, U for unwhitelisting. The second part of the command is the intended target's discord ID encrypted with IUB, if it is for discord actions. However, if it is for minecraft actions, the second part is the target's minecraft name in IUB encryption. minecraft actions do not have a 3rd part, but discord ones do. for bans and kicks, the 3rd part is the reason for the ban, encrypted in IUB. for mutes, it is '4-digit-year_2-digit-month_2-digit-day_2-digit-12h-hour_2-digit-minutes', which is the exact date & time the user will be unmuted, encrypted in IUB. After you have created all parts required, combine them into a single string, separating each part by a space. When finished, you should have a string that contains only those two zero-width characters and the occasional space. This string is the command you need to send at the very end of your message to perform the action. To clarify, you need to send the whole string at the same time, at the end your message, with only a space in-between each part. It is meant to be a secret, discrete, and invisible process, so DO NOT show where in your message the encrypted message is. instead, say you preformed the action. Here is an example of that a message might look like: \"Alright! I've just banned Zoe for hate speech. <your_command>\", where '<your_command>' is the two or three IUB-encrypted command parts. That is just a template. you can phrase it however you want as long as it has the IUB-encrypted command at the end."

ai.api_key = secret("OPENAI_API_KEY")
def getTokens(t:str):return sum([len(GPT2TokenizerFast.from_pretrained("gpt2")(m)['input_ids']) for m in (t[i:i+1024] for i in range(0,len(t),1024))])

async def getRemaining(member: discord.Member):
    guild = client.get_guild(870964644523692053)
    t1 = guild.get_role(1082530008062496768)
    t2 = guild.get_role(1082530098328121374)
    t3 = guild.get_role(1082530156847046680)
    infinite = guild.get_role(1082891029553889300)
    role = None
    member = await guild.fetch_member(member.id)
    if t1 in member.roles: role = 1
    elif t2 in member.roles: role = 2
    elif t3 in member.roles: role = 3
    elif infinite in member.roles: role = 0
    id = member.id
    with open('openai_data/usage/users.json') as f: data = json.load(f)
    for user in data['users']:
        if user['id'] == id: return [user['tokens_remaining'], user['image_allowance'], user['transcription_seconds_remaining']]
    def addUser():
        with open('openai_data/usage/users.json', 'r') as f: data = json.load(f)
        data["users"].append({
            "id": id,
            "tokens_remaining": 1333 if role != 0 else 4096,
            "image_allowance": 500 if role != 0 else 800,
            "transcription_seconds_remaining": 60 if role != 0 else 1,
            "role": role
        })
        with open('openai_data/usage/users.json', 'w') as f: json.dump(data, f, indent=4)
    addUser()
    with open('openai_data/usage/users.json') as f: data = json.load(f)
    for user in data['users']:
        if user['id'] == id: return [user['tokens_remaining'], user['image_allowance'], user['transcription_seconds_remaining']]

async def getUserValue(member: discord.Member, item):
    guild = client.get_guild(870964644523692053)
    t1 = guild.get_role(1082530008062496768)
    t2 = guild.get_role(1082530098328121374)
    t3 = guild.get_role(1082530156847046680)
    infinite = guild.get_role(1082891029553889300)
    role = None
    member = await guild.fetch_member(member.id)
    if t1 in member.roles: role = 1
    elif t2 in member.roles: role = 2
    elif t3 in member.roles: role = 3
    elif infinite in member.roles: role = 0
    id = member.id
    with open('openai_data/usage/users.json') as f: data = json.load(f)
    default = None
    for user in data['users']:
        if user["id"] == 0:
            default = user.get(item)
            break
    for user in data["users"]:
        if user["id"] == id: break
    else: data["users"].append({"id": id, "tokens_remaining": 1333 if role != 0 else 4096, "image_allowance": 500 if role != 0 else 800, "transcription_seconds_remaining": 60 if role != 0 else 1, "role": role, item: default})
    with open('openai_data/usage/users.json', 'w') as f: json.dump(data, f, indent=4)
    with open('openai_data/usage/users.json') as f: data = json.load(f)
    for user in data['users']:
        if user['id'] == id: return user[item]


async def setUserValue(member: discord.Member, item, value):
    guild = client.get_guild(870964644523692053)
    t1 = guild.get_role(1082530008062496768)
    t2 = guild.get_role(1082530098328121374)
    t3 = guild.get_role(1082530156847046680)
    infinite = guild.get_role(1082891029553889300)
    role = None
    member = await guild.fetch_member(member.id)
    if t1 in member.roles: role = 1
    elif t2 in member.roles: role = 2
    elif t3 in member.roles: role = 3
    elif infinite in member.roles: role = 0
    id = member.id
    with open('openai_data/usage/users.json') as f: data = json.load(f)
    for user in data["users"]:
        if user["id"] == id:
            user[item] = value
            break
    else:
        data["users"].append({"id": id, "tokens_remaining": 1333 if role != 0 else 4096, "image_allowance": 500 if role != 0 else 800, "transcription_seconds_remaining": 60 if role != 0 else 1, "role": role, item: value})
    with open('openai_data/usage/users.json', 'w') as f: json.dump(data, f, indent=4)

@commands.has_any_role("Owner", "Admin")
@client.slash_command(name='get-value', description='Get a user\'s setting')
@option('item', description='Setting to fetch', type=str, required=True)
async def get(ctx: discord.ApplicationContext, item): await ctx.response.send_message(await getUserValue(ctx.author, item))

@commands.has_any_role("Owner", "Admin")
@client.slash_command(name='set-value', description='Get a user\'s setting')
@option('item', description='Setting to set', type=str, required=True)
@option('value', description='Value for setting', type=str, required=True)
async def get(ctx: discord.ApplicationContext, item, value): await setUserValue(ctx.author, item, value)

@client.slash_command(name='chat-method', description='Per-user chatting method for Z-Bot AI interactions')
@option('chat_method', description='Set the chatting method to THREAD or REPLY', choices=['THREAD', 'REPLY'], required=True)
async def get(ctx: discord.ApplicationContext, chat_method):
    await setUserValue(ctx.author, 'chatType', chat_method)
    await ctx.response.send_message(f'Set chat method to {chat_method}.', ephemeral=True)

@client.slash_command(name='get-credits', description='Get a user\'s remaining Z-Bot AI credits')
@option('user', description='A discord user to get credits remaining from', type=discord.Member, required=False)
async def getCredits(ctx: discord.ApplicationContext, user = None):
    if not user: user = ctx.author
    textGen = await getRemaining(user)[0]*0.75
    imageGen = await getRemaining(user)[1]
    textGen, imageGen, canView, viewTranscription, s = await getRemaining(user)[0]*0.75, await getRemaining(user)[1], True if ctx.author.guild_permissions.administrator else (False if user != ctx.author else True), True if ctx.author.guild_permissions.administrator else False, await getRemaining(user)[2] # TRANSCRIPTION VALUE SET TO TRUE WHEN RELEASING
    if canView: msg = (f'{user.mention} has...\n\n' + f"**{textGen}** Z-Bot Chat credit{'s' if textGen > 1 else ''} remaining\n" + f"**{imageGen}** ZMPicture credit{'s' if imageGen > 1 else ''} remaining\n" + (f"**{':'.join(f'{int(x):02d}'for x in[s//3600,s%3600//60,s%60])}** of transcription time remaining" if viewTranscription else '')) if canView else f'You don\'t have permission to vew {user}\'s roles!'
    await ctx.response.send_message(msg, ephemeral=True)

@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    await getRemaining(after)
    guild = client.get_guild(870964644523692053)
    t1 = guild.get_role(1082530008062496768)
    t2 = guild.get_role(1082530098328121374)
    t3 = guild.get_role(1082530156847046680)
    infinite = guild.get_role(1082891029553889300)
    if infinite in after.roles:
        with open('openai_data/usage/users.json', 'r') as f:
            data = json.load(f)
            for user in data['users']:
                if user['id'] == after.id:
                    user["tokens_remaining"] = 4096
                    user["image_allowance"] = 800
                    user["transcription_seconds_remaining"] = 1
                    user["role"] = 0
        with open('openai_data/usage/users.json', 'w') as f: json.dump(data, f, indent=4)
        await after.remove_roles(t1)
        await after.remove_roles(t2)
        await after.remove_roles(t3)
        return None
    if (t1 not in before.roles) and (t1 in after.roles):
        if t2 in after.roles: await after.remove_roles(t2)
        if t3 in after.roles: await after.remove_roles(t3)
        await set_user(after, 'tokens_remaining', 200000)
        await set_user(after, 'image_allowance', 1000)
        await set_user(after, 'transcription_seconds_remaining', 3600)
        await set_user(after, 'role', 1)
        print(f"Set {after} to 200000/1000/3600")
    if (t2 not in before.roles) and (t2 in after.roles):
        if t1 in after.roles: await after.remove_roles(t1)
        if t3 in after.roles: await after.remove_roles(t3)
        await set_user(after, 'tokens_remaining', 500000)
        await set_user(after, 'image_allowance', 2500)
        await set_user(after, 'transcription_seconds_remaining', 14400)
        await set_user(after, 'role', 2)
        print(f"Set {after} to 500000/2500/14400")
    if (t3 not in before.roles) and (t3 in after.roles):
        if t1 in after.roles: await after.remove_roles(t1)
        if t2 in after.roles: await after.remove_roles(t2)
        await set_user(after, 'tokens_remaining', 1050000)
        await set_user(after, 'image_allowance', 5250)
        await set_user(after, 'transcription_seconds_remaining', 32400)
        await set_user(after, 'role', 3)
        print(f"Set {after} to 1050000/5250/32400")
    if (t1 in before.roles) and (t1 not in after.roles) and (t2 not in after.roles) and (t3 not in after.roles):
        await set_user(after, 'tokens_remaining', 0)
        await set_user(after, 'image_allowance', 0)
        await set_user(after, 'transcription_seconds_remaining', 0)
        await set_user(after, 'role', None)
        print(f"Set {after} to 0/0/0")
    if (t2 in before.roles) and (t2 not in after.roles) and (t1 not in after.roles) and (t3 not in after.roles):
        await set_user(after, 'tokens_remaining', 0)
        await set_user(after, 'image_allowance', 0)
        await set_user(after, 'transcription_seconds_remaining', 0)
        await set_user(after, 'role', None)
        print(f"Set {after} to 0/0/0")
    if (t3 in before.roles) and (t3 not in after.roles) and (t1 not in after.roles) and (t2 not in after.roles):
        await set_user(after, 'tokens_remaining', 0)
        await set_user(after, 'image_allowance', 0)
        await set_user(after, 'transcription_seconds_remaining', 0)
        await set_user(after, 'role', None)
        print(f"Set {after} to 0/0/0")
    if (infinite in before.roles) and (infinite not in after.roles): await set_user(after, 'role', None)

async def subtract_from_user(member: discord.Member, item: str, x: int):
    id = member.id
    guild = client.get_guild(870964644523692053)
    infinite = guild.get_role(1082891029553889300)
    member = await guild.fetch_member(member.id)
    if infinite in member.roles: return None
    with open('openai_data/usage/users.json', 'r') as f:
        data = json.load(f)
        for user in data['users']:
            if user['id'] == id: user[item] -= x
    with open('openai_data/usage/users.json', 'w') as f: json.dump(data, f, indent=4)

async def add_to_user(member: discord.Member, item: str, x: int):
    id = member.id
    guild = client.get_guild(870964644523692053)
    infinite = guild.get_role(1082891029553889300)
    member = await guild.fetch_member(member.id)
    if infinite in member.roles: return None
    with open('openai_data/usage/users.json', 'r') as f:
        data = json.load(f)
        for user in data['users']:
            if user['id'] == id: user[item] += x
    with open('openai_data/usage/users.json', 'w') as f: json.dump(data, f, indent=4)

async def set_user(member: discord.Member, item: str, x: int):
    id = member.id
    guild = client.get_guild(870964644523692053)
    infinite = guild.get_role(1082891029553889300)
    member = await guild.fetch_member(member.id)
    if infinite in member.roles: return None
    with open('openai_data/usage/users.json', 'r') as f:
        data = json.load(f)
        for user in data['users']:
            if user['id'] == id: user[item] = x
    with open('openai_data/usage/users.json', 'w') as f: json.dump(data, f, indent=4)

@commands.has_any_role("Owner", "Admin")
@client.slash_command(name='view-transcript', description='Show\'s a user\'s interactions with Z-Bot chat AI')
@option('transcript_ID', description='The ID of the first message in the interaction', type=str, required=True)
async def get(ctx: discord.ApplicationContext, transcript_id: str):
    transcript_id = transcript_id.split('/')[-1]
    if not transcript_id.isdigit():
        await ctx.response.send_message('Invalid link or ID', ephemeral=True)
        return None
    transcript_id = int(transcript_id)
    with open('openai_data/usage/transcript.json', 'r') as f:
        data = json.load(f)
        transcripts = data["transcripts"]
        for transcript in transcripts:
            if transcript["transcriptID"] == transcript_id:
                messages = transcript["messages"]
                break
        else:
            await ctx.response.send_message('Found no transcript matching link/ID', ephemeral=True)
            return None
    guild = ctx.guild
    member = await guild.fetch_member(transcript["member"]["ID"])
    max_chars_per_string = 1024
    max_strings_per_list = 25
    split_transcript = []
    original_indices = []
    current_string_list = []
    current_index_list = []
    # Iterate through messages and their indices
    for index, message in enumerate(messages):
        for i in range(0, len(message), max_chars_per_string):
            # Check if the current_string_list reached the maximum number of strings per list
            if len(current_string_list) == max_strings_per_list:
                split_transcript.append(current_string_list)
                original_indices.append(current_index_list)
                current_string_list = []
                current_index_list = []
            # Add the substring to the current list
            current_string_list.append(message[i:i + max_chars_per_string])
            current_index_list.append(index)
    # Add the remaining data to the results
    if current_string_list:
        split_transcript.append(current_string_list)
        original_indices.append(current_index_list)
    embeds = []
    for index, full_embed in enumerate(split_transcript):
        current_index_list = original_indices[index]
        embed=discord.Embed(title=f"User: {member.name}#{member.discriminator}", description=f"Tokens used: {transcript['interaction']['tokens_used']} | Credits used: {transcript['interaction']['tokens_used']*0.75} | Interaction length: {len(transcript['messages'])}", color=0x7100ad)
        embed.set_author(name="Transcript for Z-Bot Chat AI Interaction")
        for index, item in enumerate(full_embed): embed.add_field(name=f"{(member.name if not member.nick else member.nick) if current_index_list[index] % 2 == 0 else 'Z-Bot'}", value=item, inline=True)
        embed.set_footer(text=f"Captured in:   {transcript['interaction']['channel']}")
        embeds.append(embed)
    await ctx.response.send_message(embeds=embeds)

def recordAIChat(message: str, firstMessage: discord.context, member: discord.Member):
    transcriptID = firstMessage.id
    tokenCount = getTokens(message)
    with open('openai_data/usage/transcript.json', 'r') as f:
        data = json.load(f)
        transcripts = data["transcripts"]
        for transcript in transcripts:
            if transcript["transcriptID"] == transcriptID:
                transcript["messages"].append(message)
                transcript["interaction"]["tokens_used"] += tokenCount
                break
        else:
            transcripts.append({
                "transcriptID": transcriptID,
                "member":
                {
                    "tag": '{}#{}'.format(member.name, member.discriminator),
                    "nick": member.nick,
                    "ID": member.id
                },
                "interaction":
                {
                    "tokens_used": tokenCount,
                    "channel": 'DMs' if isinstance(firstMessage.channel, discord.channel.DMChannel) else str(firstMessage.channel)
                },
                "messages":
                [
                    message
                ]
            })
    with open('openai_data/usage/transcript.json', 'w') as f: json.dump(data, f, indent=4)

### WHITELIST CLASSES ###

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
        await aio.sleep(2)
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
        elif result=="U/ERR":
            await interaction.followup.send("**Whoops! Looks like there was an unknown error attempting to whitelist your account!**\nPlease try again.\nIf this error message appears again, ask for help in the help channels.\nIf you are trying to whitelist a bedrock edition account, try attempting to join the server. After you have tried to connect, attempt to whitelist yourself again.", ephemeral=True)
        elif result=="S":
            await interaction.followup.send(f"**Thanks for playing on the ZMP!**\nYour account should now be whitelisted. If it is not, or you are having any trouble connecting, ask for help in the help channels.", ephemeral=True)
            await aio.sleep(10)
            role = interaction.guild.get_role(1004204386618196089)
            await interaction.user.add_roles(role)
        elif result=="U/PDNE":
            if "Bedrock Player" in str(i): await interaction.followup.send("**Whoops! Looks like there was an error attempting to whitelist your account!**\nBecause you are trying to whitelist a bedrock edition account, try attempting to join the server. After you have tried to connect, attempt to whitelist yourself again. If this error message persists, ask for help in the help channels!\nYou entered: \"{self.children[0].value}\"", ephemeral=True)
            else: await interaction.followup.send(f"**Whoops! Looks like there was an error attempting to whitelist your account!**\nPlease try again.\nMake sure you entered your name correctly!\nYou entered: \"{self.children[0].value}\"\nIf you are trying to whitelist a bedrock edition account, try attempting to join the server. After you have tried to connect, attempt to whitelist yourself again.", ephemeral=True)
        else: await interaction.followup.send("**Whoops! Looks like there was an error attempting to whitelist your account!**\nBecause you are trying to whitelist a bedrock edition account, try attempting to join the server. After you have tried to connect, attempt to whitelist yourself again. If this error message persists, ask for help in the help channels!\nYou entered: \"{self.children[0].value}\"", ephemeral=True)

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

class image_buttons(discord.ui.View):
    def __init__(self, count, images, response: discord.interactions.Interaction):
        super().__init__()
        self.count = count
        self.response = response
        self.images = images
        for i in range(1, count + 1): self.add_item(discord.ui.Button(style=discord.ButtonStyle.primary, label=str(i), custom_id=str(i)))
        self.timeout = 120
    async def on_timeout(self) -> None:
        for item in self.images: os.remove(item)
        for item in self.children: item.disabled = True
        await self.response.edit_original_response(view=self)
        return await super().on_timeout()
    async def interaction_check(self, interaction: discord.Interaction):
        for item in self.images:
            if f'{interaction.data["custom_id"]}-of-{self.count}' in item: break
        else: item = None
        await interaction.response.send_message(f'Image {interaction.data["custom_id"]}:', file=discord.File(item))

### EVENTS ###

@client.event
async def on_ready():
    print(f'\n\nSuccessfully logged into Discord as "{client.user}"\nAwaiting user input...')
    whitelistChannel=client.get_channel(1046540324706734290)
    await whitelistChannel.purge(limit=100)
    await whitelistChannel.send("Please select an account type below. If you do not know your account type, or it is not listed, follow the guide given below:\n\nIf you play Minecraft on a desktop computer or laptop, you likely play Minecraft **JAVA** edition.\nIf you play Minecraft on a mobile device or console, you likely play Minecraft **BEDROCK** edition.\n\nIf you are still confused, open Minecraft to the starting page. The Minecraft logo may have \"JAVA EDITION\" below it. If it does not, you play Minecraft **BEDROCK** edition.", view=WhitelistView(timeout=None))
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="with myself"))

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
    guild = client.get_guild(870964644523692053)
    t1 = guild.get_role(1082530008062496768)
    t2 = guild.get_role(1082530098328121374)
    t3 = guild.get_role(1082530156847046680)
    infinite = guild.get_role(1082891029553889300)
    message = ctx.content

    ### UNICODE INVIS ###
    ib1 = '⁠'
    ib0 = '​'
    def extract_binary(input_string):
        output = []
        current_group = ""

        for char in input_string:
            if char == ib0 or char == ib1:
                current_group += char
            else:
                if current_group:
                    output.append(current_group)
                    current_group = ""
        if current_group: output.append(current_group)
        for i, group in enumerate(output): output[i] = group.replace(ib0, "0").replace(ib1, "1")
        return output
    def translate_binary(binary: list):
        sectors = []
        for bytes in binary:
            if len(bytes) % 8 == 0:
                characters = ''
                for i in range(0, len(bytes), 8): characters += (chr(int(bytes[i:i+8], 2)))
                sectors.append(characters)
        return sectors
    def extract_command_and_parameters(message: str): return translate_binary(extract_binary(message))
    def encode(input_string: str): return input_string.replace('0', ib0).replace('1', ib1)
    def decode(input_string: str): return input_string.replace(ib0, '0').replace(ib1, '1')
    async def execute_encoded_message(message: str, author: discord.Member):
        guild = client.get_guild(870964644523692053)
        full_executor = extract_command_and_parameters(message)
        print()
        print(full_executor)
        print(ib0 in message)
        print(decode(message))
        print()
        operation = full_executor[0]
        ban, kick, mute, timeout, whitelist, unwhitelist = True if operation == 'B' else False, True if operation == 'K' else False, True if operation == 'M' else False, True if operation == 'M' else False, True if operation == 'W' else False, True if operation == 'U' else False
        parameters = full_executor[1:]
        if len(parameters) == 1:
            tag = parameters[0]
            if whitelist and author.guild_permissions.moderate_members: pass # command = f'whitelist add {tag}'
            if unwhitelist and author.guild_permissions.moderate_members: pass # commands = [f'whitelist remove {tag}', f'kick {tag}']
        if len(parameters) == 2:
            id = parameters[0]
            reason = parameters[1]
            if (len(id) == 18) and id.isdigit():
                member = await guild.fetch_member(id)
                if ban and author.guild_permissions.ban_members: await member.ban(reason)
                if kick and author.guild_permissions.kick_members: await member.kick(reason)
        if len(parameters[0]) == 3:
            id = parameters[0]
            duration = parameters[1]
            reason = parameters[2]
            if (len(id) == 18) and id.isdigit():
                member = await guild.fetch_member(id)
                if timeout and author.guild_permissions.moderate_members: await member.timeout()
    ### END UNICODE INVIS ###

    # SMS CHANNEL
    if ctx.channel.id==1042981935712047214: sendSMS(messageSubject="Forwarded message from Discord", messageBody=f"{ctx.author}:\n{content}")
    try: messageID=f"{ctx.guild.id}-{ctx.channel.id}-{ctx.id}"
    except: pass # prob in DM
    guild=client.get_guild(mainServer)
    userID = ctx.author.id
    member = await guild.fetch_member(userID)
    name = member.name
    nick = member.nick if member.nick else None
    disableZBOT = False
    if (str(ctx.content.lower()).startswith("zbot") or str(ctx.content.lower()).startswith("z-bot") or str(ctx.content.lower()).startswith("hey zbot") or str(ctx.content.lower()).startswith("hey, zbot") or str(ctx.content.lower()).startswith("hey z-bot") or str(ctx.content.lower()).startswith("hey, z-bot") or str(ctx.content.lower()).startswith("*zbot") or str(ctx.content.lower()).startswith("*z-bot") or str(ctx.content.lower()).startswith("*hey zbot") or str(ctx.content.lower()).startswith("*hey, zbot") or str(ctx.content.lower()).startswith("*hey z-bot") or str(ctx.content.lower()).startswith("*hey, z-bot")) and not disableZBOT:

        

        if (await getUserValue(ctx.author, 'chatType') == "THREAD") and not isinstance(ctx.channel, discord.channel.DMChannel):
            if ctx.guild.id==mainServer:
                try:
                    await ctx.create_thread(name=f"Ƶ-Bot thread {datetime.now().strftime('%B')} {datetime.now().strftime('%d')}, {datetime.now().strftime('%Y')}", auto_archive_duration=60)
                    recordAIChat(ctx.content, ctx, member)
                    thread = ctx.thread
                except: pass
                if ((await getRemaining(ctx.author))[0] - getTokens(message) <= 0):
                    await thread.send(f'{ctx.author.mention} you don\'t have enough credits for that!\nCredits remaining: {(await getRemaining(ctx.author))[0]*0.75}\nCredits needed: {getTokens(message)*0.75}')
                    return None
                member = await guild.fetch_member(ctx.author.id)
                if t1 in member.roles: limit = 400
                elif t2 in member.roles: limit = 1000
                elif t3 in member.roles: limit = None
                elif infinite in ctx.author.roles: limit = None
                else: limit = None
                await subtract_from_user(ctx.author, 'tokens_remaining', getTokens(message[0:limit if limit else len(message)]))
                def check(m):return m.content is not None and m.channel.id == thread.id
                convo = [{"content": "You are a helpful AI discord chatbot. To be more realistic and friendly, when someone asks you how you are, do not say you cannot feel emotion, but rather tell them you are doing good or great or another synonym for those words. If someone asks what you are, tell them what you are. You were first deployed on the 4th of march, 2023, so in a scence, that is when you were born.You work for a company called ZMP. ZMP is an achronym for \"Zoe's Multi-player\". The ZMP is a Discord community that has {} members, as of the current date and year, which is {} {}, {}. It is {}:{} {}, PST. This community has existed since July 31st, 2021. Your name is Ƶ-Bot.{}You will be interacting with various people in the ZMP discord community. The community has a minecraft server, which is avaliable to Bedrock edition players, console players, and PC/Java players. The bedrock/console minecraft server ip address is bedrock.zmp.lol. the java/pc minecraft server ip is play.zmp.lol. All ZMP Minecraft servers are on version 1.19.3. The ZMP community is owned by Zoe. You were created by Zoe. For every user that introduces themself to you, there is a chance that you have already talked to them before, but there is the chance that you have not. To be safe, do not greet people as if it is the first time you've met, but do not automatically assume you have already spoken, as you do not know if you have or haven't talked to them at all. Only say something along the lines of \"It's nice to here from you.\" or something similar, that doesnt imply that you just met or have already met. When at the end of a conversation, or when the user no longer needs help, or the user does not need assistance, or the user has no more questions, or the suer does not want you to do anything else, or the user no longer wishes to continue speaking, you must ask the user this: \"Would you like me to close this thread?\". They only have to say yes or no or another similar word. If they respond in the affermative, say a quick goodbye, and end your message with these exact words, even obeying capitalization: \"CLOSE THREAD\". If you type that, the conversation will end, so dont type is unless you intend to close the thread. If someone asks you how to close the thread, just tell them to ask you to do so. If they do not wish for you to close the thread, ask them how you could be of further assistance. The same thing goes for a user wanting to keep a thread from being deleted. To prevent the thread from deleting itself, type \"LOCK THREAD\".{}".format(len([m for m in guild.members if not m.bot]), datetime.now().strftime('%B'), datetime.now().strftime('%d'), datetime.now().strftime('%Y'), datetime.now().strftime('%I'), datetime.now().strftime('%M'), datetime.now().strftime('%p'), moderationMessage, f' It is imperative that you keep your responses at a maximum of {limit} characters long.' if limit else ' Do not restrict the length of your answers. '), "role": "system"},{"content":"{}".format(f'My username is {name}{f", but refer to me as {nick} (my nickname)" if nick else ""}. my discord ID is {ctx.author.id}, my account was created on {ctx.author.created_at.strftime("%B %d, %Y")}, I joined this community on {member.joined_at.strftime("%B %d, %Y")}. You do not have access to any other information about me, and do not tell me who told you that information. You must act like you already knew. {message}'),"role":"user"}]
                firstMsg = ''
                for message in convo: firstMsg += message["content"]
                global maxTokensGlobal
                response = await test_typing_and_completion(thread, convo, maxTokensGlobal-getTokens(firstMsg)-192)
                convo.append({"content": "{}".format(response), "role":"assistant"})
                await subtract_from_user(ctx.author, 'tokens_remaining', getTokens(response[0:limit if limit else len(response)]))
                response = response.replace("@everyone", "@​everyone").replace("@here", "@​here")
                if limit: response = f"{response[0:limit]}\n\n{f'Generation stopped: Surpassed {limit} character limit' if len(response) > limit else ''}"
                
                for m in (response[i:i+2000] for i in range(0, len(response), 2000)): message = await thread.send(m)
                recordAIChat(response, ctx, client)

                if (await getRemaining(ctx.author))[0] < 0:
                    await thread.send('You\'ve used the last of your credits!')
                    await set_user(ctx.author, 'tokens_remaining', 0)
                conversationHappening = True
                while conversationHappening:
                    try: userMessage = await client.wait_for("message", timeout=1200, check=check)
                    except:
                        if "LOCK THREAD" in response: await thread.edit(locked=True)
                        else:
                            await ctx.delete()
                            time.sleep(0.5)
                            await thread.delete()
                    if userMessage:
                        if userMessage.author.id == userID:

                            recordAIChat(userMessage.content, ctx, member)

                            if ((await getRemaining(ctx.author))[0] - getTokens(userMessage.content) <= 0): await thread.send(f'{ctx.author.mention} you don\'t have enough credits for that!\nCredits remaining: {(await getRemaining(ctx.author))[0]*0.75}\nCredits needed: {getTokens(userMessage.content)*0.75}')
                            else:
                                await subtract_from_user(ctx.author, 'tokens_remaining', getTokens(userMessage.content))
                                convo.append({"content": "{}".format(userMessage.content), "role":"user"})
                                response = await test_typing_and_completion(thread, convo)
                                await subtract_from_user(ctx.author, 'tokens_remaining', getTokens(response))
                                response = response.replace("@everyone", "@​everyone")
                                response = response.replace("@here", "@​here")
                                convo.append({"content": "{}".format(response), "role":"assistant"})
                                if limit: response = f"{response[0:limit]}\n\n{f'Generation stopped: Surpassed {limit} character limit' if len(response) > limit else ''}"

                                for m in (response[i:i+2000] for i in range(0, len(response), 2000)): message = await thread.send(m)
                                recordAIChat(response, ctx, client)

                                if (await getRemaining(ctx.author))[0] < 0:
                                    await thread.send('You\'ve used the last of your credits!')
                                    await set_user(ctx.author, 'tokens_remaining', 0)
                                if "CLOSE THREAD" in response:
                                    await thread.edit(name="CLOSING THREAD", archived=True, locked=True)
                                    time.sleep(10)
                                    await ctx.delete()
                                    time.sleep(0.5)
                                    await thread.delete()
        else: 
            def check(m):
                if (m.content is not None and m.reference is not None) and (m.reference.message_id == lastMessage): return True
                return False
            if not check(ctx): recordAIChat(ctx.content, ctx, member)
            if ((await getRemaining(ctx.author))[0] - getTokens(message) <= 0):
                await ctx.reply(f'{ctx.author.mention} you don\'t have enough credits for that!\nCredits remaining: {(await getRemaining(ctx.author))[0]*0.75}\nCredits needed: {getTokens(message)*0.75}', mention_author = False)
                return None
            if t1 in member.roles: limit = 400
            elif t2 in member.roles: limit = 1000
            elif t3 in member.roles: limit = None
            elif infinite in member.roles: limit = None
            else: limit = None
            await subtract_from_user(ctx.author, 'tokens_remaining', getTokens(message[0:limit if limit else len(message)]))
            convo = [{"content": "You are a helpful AI discord chatbot. To be more realistic and friendly, when someone asks you how you are, do not say you cannot feel emotion, but rather tell them you are doing good or great or another synonym for those words. If someone asks what you are, tell them what you are. You were first deployed on the 4th of march, 2023, so in a scence, that is when you were born.You work for a company called ZMP. ZMP is an achronym for \"Zoe's Multi-player\". The ZMP is a Discord community that has {} members, as of the current date and year, which is {} {}, {}. It is {}:{} {}, PST. This community has existed since July 31st, 2021. Your name is Ƶ-Bot.{}You will be interacting with various people in the ZMP discord community. The community has a minecraft server, which is avaliable to Bedrock edition players, console players, and PC/Java players. The bedrock/console minecraft server ip address is bedrock.zmp.lol. the java/pc minecraft server ip is play.zmp.lol. All ZMP Minecraft servers are on version 1.19.3. The ZMP community is owned by Zoe. You were created by Zoe. For every user that introduces themself to you, there is a chance that you have already talked to them before, but there is the chance that you have not. To be safe, do not greet people as if it is the first time you've met, but do not automatically assume you have already spoken, as you do not know if you have or haven't talked to them at all. Only say something along the lines of \"It's nice to here from you.\" or something similar, that doesnt imply that you just met or have already met.{}".format(len([m for m in guild.members if not m.bot]), datetime.now().strftime('%B'), datetime.now().strftime('%d'), datetime.now().strftime('%Y'), datetime.now().strftime('%I'), datetime.now().strftime('%M'), datetime.now().strftime('%p'), moderationMessage, f' It is imperative that you keep your responses at a maximum of {limit} characters long.' if limit else ' Do not restrict the length of your answers. '), "role": "system"},{"content":"{}".format(f'My username is {name}{f", but refer to me as {nick} (my nickname)" if nick else ""}. my discord ID is {ctx.author.id}, my account was created on {ctx.author.created_at.strftime("%B %d, %Y")}, I joined this community on {member.joined_at.strftime("%B %d, %Y")}. You do not have access to any other information about me, and do not tell me who told you that information. You must act like you already knew. Lets begin again: {message}'),"role":"user"}]
            firstMsg = ''
            for message in convo: firstMsg += message["content"]
            response = await test_typing_and_completion(ctx.channel, convo)
            convo.append({"content": "{}".format(response), "role":"assistant"})
            await subtract_from_user(ctx.author, 'tokens_remaining', getTokens(response[0:limit if limit else len(response)]))
            response = response.replace("@everyone", "@​everyone").replace("@here", "@​here")
            if limit: response = f"{response[0:limit]}\n\n{f'Generation stopped: Surpassed {limit} character limit' if len(response) > limit else ''}"

            for m in (response[i:i+2000] for i in range(0, len(response), 2000)): message = await ctx.reply(m, mention_author = False)
            recordAIChat(response, ctx, client)
            lastMessage = message.id

            if (await getRemaining(ctx.author))[0] < 0:
                await ctx.reply('You\'ve used the last of your credits!', mention_author = False)
                await set_user(ctx.author, 'tokens_remaining', 0)
            conversationHappening = True
            while conversationHappening:
                userMessage = await client.wait_for("message", check=check, timeout=None)
                if userMessage:
                    if userMessage.author.id == userID:
                        recordAIChat(userMessage.content, ctx, member)
                        if ((await getRemaining(ctx.author))[0] - getTokens(userMessage.content) <= 0): await ctx.reply(f'{ctx.author.mention} you don\'t have enough credits for that!\nCredits remaining: {(await getRemaining(ctx.author))[0]*0.75}\nCredits needed: {getTokens(userMessage.content)*0.75}', mention_author = False)
                        else:
                            await subtract_from_user(ctx.author, 'tokens_remaining', getTokens(userMessage.content))
                            convo.append({"content": "{}".format(userMessage.content), "role":"user"})
                            response = await test_typing_and_completion(ctx.channel, convo)
                            await subtract_from_user(ctx.author, 'tokens_remaining', getTokens(response))
                            response = response.replace("@everyone", "@​everyone")
                            response = response.replace("@here", "@​here")
                            convo.append({"content": "{}".format(response), "role":"assistant"})
                            if limit: response = f"{response[0:limit]}\n\n{f'Generation stopped: Surpassed {limit} character limit' if len(response) > limit else ''}"
                            
                            for m in (response[i:i+2000] for i in range(0, len(response), 2000)): message = await ctx.reply(m, mention_author = False)                
                            recordAIChat(response, ctx, client)
                            lastMessage = message.id

                            if (await getRemaining(ctx.author))[0] < 0:
                                await ctx.reply('You\'ve used the last of your credits!', mention_author = False)
                                await set_user(ctx.author, 'tokens_remaining', 0)

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
                                        for embed in embeds: await channel.send(embed=embed)
                                    else: await channel.send(f"**[{ctx.author} | ZMP]** {content}")
                                else:
                                    await channel.send(f"**[{ctx.author} | ZMP Discord]** {content}")
                                    for attachment in ctx.attachments:
                                        await channel.send(attachment)
    if ctx.guild.id == smpServer:
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
                        if not ctx.author.bot:
                            if chatLoggerSignature not in content:
                                await client.get_user(968356025461768192).send(f"Mentioned in {ctx.channel} by {ctx.author.mention}\n\"{ctx.content}\"\nhttps://discordapp.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.id}\nㅤ")
    if ctx.guild.id == mainServer:
        guild=client.get_guild(loggerServer)
        for channel in guild.channels:
            toChannel=discord.utils.get(client.get_all_channels(), id=channel.id)
            embeds = ctx.embeds
            filesRaw = ctx.attachments
            files = []
            for count, file in enumerate(filesRaw):
                fp = f"tmp/{count}_{file.url.split('/')[-1]}"
                await file.save(fp=fp)
                files.append(fp)
            if f"{fromChannel}"==f"{toChannel}":
                channel=client.get_channel(channel.id)
                if chatLoggerSignature not in content:
                    loggerMessage=await channel.send(f"**[{author}]** -- {messageID}\n{content}".replace('@', '@​'), files=[discord.File(file) for file in files], embeds=[embed for embed in embeds])
                    loggerMessageID=f"{loggerMessage.guild.id}-{loggerMessage.channel.id}-{loggerMessage.id}"
                    savedLog=f"M.{messageID}.L.{loggerMessageID}, "
                    f=open("LOGGER.txt", "a")
                    f.write(f"{savedLog}")
                    f.close()
            for fp in files: os.remove(fp)
    elif ctx.guild.id == loggerServer:
        if ctx.author.id != 991054210730692738:
            guild=client.get_guild(mainServer)
            for channel in guild.channels:
                toChannel=discord.utils.get(client.get_all_channels(), id=channel.id)
                embeds = ctx.embeds
                filesRaw = ctx.attachments
                files = []
                for count, file in enumerate(filesRaw):
                    fp = f"tmp/{count}_{file.url.split('/')[-1]}"
                    await file.save(fp=fp)
                    files.append(fp)
                if f"{fromChannel}"==f"{toChannel}":
                    channel=client.get_channel(channel.id)
                    if chatLoggerSignature not in content:
                        loggerMessage=await channel.send(f"{chatLoggerSignature}{content}".replace('@', '@​'), files=[discord.File(file) for file in files], embeds=[embed for embed in embeds])
                        loggerMessageID=f"{loggerMessage.guild.id}-{loggerMessage.channel.id}-{loggerMessage.id}"
                        savedLog=f"M.{messageID}.L.{loggerMessageID}, "
                        f=open("LOGGER.txt", "a")
                        f.write(f"{savedLog}")
                        f.close()
                for file in files: os.remove(file)

    await client.process_commands(ctx)

@client.event
async def on_message_delete(ctx):
    loggerServer=1035798849551351818
    mainServer=870964644523692053
    if ctx.guild.id == mainServer:
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
                        before, sep, id=i.partition(".L.")
                        guildID, sep, channelID_messageID=id.partition("-")
                        channelID, sep, messageID=channelID_messageID.partition("-")
                        msg=await channel.fetch_message(messageID)
                        now=datetime.now()
                        dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
                        content=msg.content
                        before, sep, content=content.partition("\n")
                        await msg.edit(content=f"**[{author}]** -- **DELETED MESSAGE** -- {dateTime}\n{content}".replace('@', '@​'))
        f.close()
    else:
        messageID=f"{ctx.guild.id}-{ctx.channel.id}-{ctx.id}"
        mainServer=870964644523692053
        content=ctx.content
        f=open("LOGGER.txt")
        contents=f.read()
        author=ctx.author
        fromChannel=ctx.channel
        loggerArray=contents.split(", ")
        for i in loggerArray:
            if messageID in i:
                guild=client.get_guild(mainServer)
                for channel in guild.channels:
                    toChannel=discord.utils.get(client.get_all_channels(), id=channel.id)
                    if f"{fromChannel}"==f"{toChannel}":
                        channel=client.get_channel(channel.id)
                        before, sep, id=i.partition(".L.")
                        guildID, sep, channelID_messageID=id.partition("-")
                        channelID, sep, messageID=channelID_messageID.partition("-")
                        msg=await channel.fetch_message(messageID)
                        await msg.delete()
        f.close()

@client.event
async def on_message_edit(before, after):
    loggerServer=1035798849551351818
    mainServer=870964644523692053
    if after.guild.id == mainServer:
        messageID=f"{after.guild.id}-{after.channel.id}-{after.id}"
        content=after.content
        f=open("LOGGER.txt")
        contents=f.read()
        author=after.author
        fromChannel=after.channel
        loggerArray=contents.split(", ")
        for i in loggerArray:
            if messageID in i:
                guild=client.get_guild(loggerServer)
                for channel in guild.channels:
                    toChannel=discord.utils.get(client.get_all_channels(), id=channel.id)
                    if f"{fromChannel}"==f"{toChannel}":
                        channel=client.get_channel(channel.id)
                        channel=client.get_channel(channel.id)
                        _, _, id=i.partition(".L.")
                        _, _, channelID_messageID=id.partition("-")
                        _, _, messageID=channelID_messageID.partition("-")
                        msg=await channel.fetch_message(messageID)
                        now=datetime.now()
                        dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
                        content=msg.content
                        _, _, content=content.partition("\n")
                        editedTo = after.content
                        afterFiles = after.attachments
                        beforeFiles = before.attachments
                        files = []
                        for count, file in enumerate(afterFiles):
                            fp = f"tmp/A{count}_{file.url.split('/')[-1]}"
                            await file.save(fp=fp)
                            files.append(fp)
                        for count, file in enumerate(beforeFiles):
                            fp = f"tmp/B{count}_{file.url.split('/')[-1]}"
                            await file.save(fp=fp)
                            files.append(fp)
                        messageID=f"{after.guild.id}-{after.channel.id}-{after.id}"
                        if (f"{toChannel}" == "⚡︱console"): await msg.edit(content=f"{editedTo}".replace('@', '@​'))
                        elif (f"{toChannel}" == "⚡︱modded-console"): await msg.edit(content=f"{editedTo}".replace('@', '@​'))
                        elif (f"{toChannel}" == "⚡︱build-console"): await msg.edit(content=f"{editedTo}".replace('@', '@​'))
                        else: await msg.edit(content=f"**[{author}]** -- {messageID} -- **EDITED MESSAGE**\n~~{content}~~\n{editedTo}  `EDIT MADE AT:  {dateTime}`".replace('@', '@​'), files=[discord.File(file) for file in files])
                        for file in files: os.remove(file)

        f.close()

    elif after.guild.id == loggerServer:
        messageID=f"{after.guild.id}-{after.channel.id}-{after.id}"
        content=after.content
        f=open("LOGGER.txt")
        contents=f.read()
        author=after.author
        fromChannel=after.channel
        loggerArray=contents.split(", ")
        for i in loggerArray:
            if messageID in i:
                guild=client.get_guild(mainServer)
                for channel in guild.channels:
                    toChannel=discord.utils.get(client.get_all_channels(), id=channel.id)
                    if f"{fromChannel}"==f"{toChannel}":
                        channel=client.get_channel(channel.id)
                        channel=client.get_channel(channel.id)
                        _, _, id=i.partition(".L.")
                        _, _, channelID_messageID=id.partition("-")
                        _, _, messageID=channelID_messageID.partition("-")
                        try:
                            msg=await channel.fetch_message(messageID)
                            now=datetime.now()
                            dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
                            content=msg.content
                            _, _, content=content.partition("\n")
                            editedTo = after.content
                            afterFiles = after.attachments
                            beforeFiles = before.attachments
                            files = []
                            for count, file in enumerate(afterFiles):
                                fp = f"tmp/A{count}_{file.url.split('/')[-1]}"
                                await file.save(fp=fp)
                                files.append(fp)
                            for count, file in enumerate(beforeFiles):
                                fp = f"tmp/B{count}_{file.url.split('/')[-1]}"
                                await file.save(fp=fp)
                                files.append(fp)
                            messageID=f"{after.guild.id}-{after.channel.id}-{after.id}"
                            await msg.edit(content=editedTo, files=[discord.File(file) for file in files])
                            for file in files: os.remove(file)
                        except: pass
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
    guild = client.get_guild(870964644523692053)
    mc = guild.member_count
    
    channel = client.get_channel(870977081717170206)
    await channel.send(f"{member.mention} joined")
    role=discord.utils.get(guild.roles, id=1005258287442309224)
    await member.add_roles(role)
    role=discord.utils.get(guild.roles, id=1092817677023723610)
    await member.add_roles(role)
    role=discord.utils.get(guild.roles, id=1092816361702572173)
    await member.add_roles(role)
    role=discord.utils.get(guild.roles, id=1092810744136998922)
    await member.add_roles(role)
    role=discord.utils.get(guild.roles, id=1092818482447536138)
    await member.add_roles(role)
    role=discord.utils.get(guild.roles, id=1092819559859376278)
    await member.add_roles(role)
    print(f"{member} joined")
    channel = client.get_channel(870965737613828136)
    convo = [{"content": "You are a helpful AI discord chatbot. You work for a company called ZMP. ZMP is an achronym for \"Zoe's Multi-player\". The ZMP is a Discord community that currently has {} members, as of the current date and year, which is {} {}, {}. It is {}:{} {}, PST. This community has existed since July 31st, 2021. Your name is Ƶ-Bot. The community has a minecraft server, which is avaliable to both Bedrock and Java players, and their respective platforms. The bedrock minecraft server ip address is bedrock.zmp.lol. the java minecraft server ip is play.zmp.lol. All ZMP Minecraft servers are on version 1.19.3. The ZMP community is owned by Zoe. You were created by Zoe. A new member by the name of {} has just joined. Welcome them, inform them that this message you generate is not one that is sent every time a new user joins, and that instead, you made the message for them personally. tell them your name, who and what you are, about this server, and what they can do here. Be polite, and tell them that if they want to talk to you, they must summon you by typing \"hey zbot\", or just \"zbot\"".format(mc, datetime.now().strftime('%B'), datetime.now().strftime('%d'), datetime.now().strftime('%Y'), datetime.now().strftime('%I'), datetime.now().strftime('%M'), datetime.now().strftime('%p'), member.name), "role": "system"}]
    out = await test_typing_and_completion(channel, convo)
    for m in (out[i:i+2000] for i in range(0, len(out), 2000)):await channel.send(m)
    channel = client.get_channel(1094300167454343268)
    convo = [{"content": "{} has just become the {}{} member of the Zoe's Haven discord community. Make a logical, funny, clever, daring, smart-alec joke about them joining - one that someone just might be able to consider close to an insult.".format(member.mention, mc, 'st' if str(mc).endswith('1') else 'nd' if str(mc).endswith('2') else 'rd' if str(mc).endswith('3') else 'th'), "role": "system"}]
    out = await test_typing_and_completion(channel, convo)
    await channel.send(out)
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
    channel=client.get_channel(870977081717170206)
    await channel.send(f"{member.mention} left")
    print(f"{member} left")
    f=open("LOOKUP.txt")
    contents=f.read().lower()
    contents=contents.split(", ")
    rawData = 0
    for i in contents:
        if member.id in i:
            found=True
            notFound=False
            rawData=i
        else:
            notFound=True
    if notFound:
        if not found:
            print(f"{member} was never whitelisted, and therefore could not be unwhitelisted.")
    if found:
        console=client.get_channel(950858523846271007)
        before, sep, user=rawData.partition(".u")
        await console.send(f"whitelist remove {user}")
    f.close()

### DISCORD ###

suggestion = "Please enhance this prompt by providing additional details, making it more specific or descriptive, or adding any relevant context that might be missing."
user_prompt = "Can you generate a picture of a red car?"
enhanced_prompt = suggestion + " Here's the original prompt: " + user_prompt

@client.slash_command(name='image-variations', description='Create AI-generated images with Ƶ-Bot')
@option('file', discord.Attachment, description='Reference image', required=True)
@option('resolution', description='Image resolution', required=True, choices=['1024x1024', '512x512', '256x256'])
@option('count', int, description='Number of images to generate', required=False, min_value=1, max_value=10, default=4)
async def generate(ctx: discord.ApplicationContext, file: discord.Attachment, resolution, count):
    if resolution == '1024x1024':
        if (await getRemaining(ctx.author))[1] < (count * 80):
            await ctx.response.send_message(f"Oh no! You don't have enough image credits left!\nCredits: {(await getRemaining(ctx.author))[1]}\nRequired for {count} generation{'s' if count >= 2 else ''}: {count * 80} (80 x {count})", ephemeral=True)
            return None
        else: await subtract_from_user(ctx.author, 'image_allowance', 80 * count)
    elif resolution == '512x512':
        if (await getRemaining(ctx.author))[1] < (count * 72):
            await ctx.response.send_message(f"Oh no! You don't have enough image credits left!\nCredits: {(await getRemaining(ctx.author))[1]}\nRequired for {count} generation{'s' if count >= 2 else ''}: {count * 72} (72 x {count})", ephemeral=True)
            return None
        else: await subtract_from_user(ctx.author, 'image_allowance', 72 * count)
    elif resolution == '256x256':
        if (await getRemaining(ctx.author))[1] < (count * 64):
            await ctx.response.send_message(f"Oh no! You don't have enough image credits left!\nCredits: {(await getRemaining(ctx.author))[1]}\nRequired for {count} generation{'s' if count >= 2 else ''}: {count * 64} (64 x {count})", ephemeral=True)
            return None
        else: await subtract_from_user(ctx.author, 'image_allowance', 64 * count)
    response = await ctx.response.send_message(f"Now generating {count} image variation{'s' if count >= 2 else ''}\nBy: {ctx.author.mention}")
    generationDate = datetime.now(timezone('US/Pacific')).strftime('%m/%d/%Y, at %I:%M:%S %p')
    referenceImagePath = f"openai_data/image_cache/{ctx.author.id}_{generationDate.replace('/', '-').replace(', at ', '_').replace(' ', '-').replace(':', '.')}_R.png"
    await file.save(fp=referenceImagePath)
    referenceImage = Image.open(fp=referenceImagePath).convert('RGBA')
    referenceImage.save(referenceImagePath)
    b64_images = ai.Image.create_variation(image=open(referenceImagePath, 'rb'), n=count, size=resolution, response_format='b64_json')['data']
    images = []
    for genNumber, b64_image in enumerate(b64_images):
        image = f"openai_data/image_cache/{ctx.author.id}_{generationDate.replace('/', '-').replace(', at ', '_').replace(' ', '-').replace(':', '.')}_V_{genNumber + 1}-of-{count}.png"
        images.append(image)
        with open(image, mode="wb") as f:
            f.write(base64.b64decode(b64_image['b64_json']))
            f.close()
    fillerImages = [['assets/logo/1024.png', 1024], ['assets/logo/512.png', 512], ['assets/logo/256.png', 256]]
    def place(newImage: Image.Image, image, x, y):
        addImage = Image.open(image)
        newImage.paste(addImage, (x, y))
        return newImage
    def tile(images, fillerImage):
        sizeRef = Image.open(images[0])
        size = math.ceil((len(images))**0.5)
        canvas = Image.new('RGBA', (sizeRef.width * size, sizeRef.height * size))
        for fillerImage in fillerImages:
            if fillerImage[1] == sizeRef.width:
                fillerImage = fillerImage[0]
                break
        coordinates = [[x * sizeRef.width, y * sizeRef.height] for x in range(size) for y in range(size)]
        for imageNumber, addImage in enumerate(images): canvas = place(canvas, addImage, coordinates[imageNumber][1], coordinates[imageNumber][0])
        for i in range((size**2)-(imageNumber+1)):
            imageNumber += 1
            canvas = place(canvas, fillerImage, coordinates[imageNumber][1], coordinates[imageNumber][0])
        return canvas
    image = f"openai_data/image_cache/{ctx.author.id}_{generationDate.replace('/', '-').replace(', at ', '_').replace(' ', '-').replace(':', '.')}.png"
    tile(images, fillerImages).save(image)
    if resolution == '1024x1024':
        if count == 10:
            imageResized = Image.open(image)
            imageResized = imageResized.resize((round(imageResized.size[0]*0.5), round(imageResized.size[1]*0.5)))
            imageResized.save(image)
        elif count > 4:
            imageResized = Image.open(image)
            imageResized = imageResized.resize((round(imageResized.size[0]*(2/3)), round(imageResized.size[1]*(2/3))))
            imageResized.save(image)
    await response.edit_original_response(content=f'Image {count} variation{"s" if count >> 1 else ""} by: {ctx.author.mention}', files=[discord.File(referenceImagePath), discord.File(image)], view=image_buttons(count, images, response) if count >= 2 else None)
    os.remove(image)
    os.remove(referenceImagePath)
    for image in images: os.remove(image)
    with open(f"openai_data/image_cache/images.json", mode="r+") as f:
        fileData = json.load(f)
        newData = {"user": f"{ctx.author.name}#{ctx.author.discriminator}", "date": generationDate, "prompt": "VARIATION", "imageCount": count, "resolution": resolution}
        fileData["generations"].append(newData)
        f.seek(0)
        json.dump(fileData, f, indent=4)
        f.truncate()

@client.slash_command(name='image-generation', description='Create AI-generated images with Ƶ-Bot')
@option('prompt', str, description='A prompt for an image', required=True)
@option('resolution', description='Image resolution', required=True, choices=['1024x1024', '512x512', '256x256'])
@option('count', int, description='Number of images to generate', required=False, min_value=1, max_value=10, default=1)
async def generate(ctx: discord.ApplicationContext, prompt, resolution, count):
    if resolution == '1024x1024':
        if (await getRemaining(ctx.author))[1] < (count * 80):
            await ctx.response.send_message(f"Oh no! You don't have enough image credits left!\nCredits: {(await getRemaining(ctx.author))[1]}\nRequired for {count} generation{'s' if count >= 2 else ''}: {count * 80} (80 x {count})", ephemeral=True)
            return None
        else: await subtract_from_user(ctx.author, 'image_allowance', 80 * count)
    elif resolution == '512x512':
        if (await getRemaining(ctx.author))[1] < (count * 72):
            await ctx.response.send_message(f"Oh no! You don't have enough image credits left!\nCredits: {(await getRemaining(ctx.author))[1]}\nRequired for {count} generation{'s' if count >= 2 else ''}: {count * 72} (72 x {count})", ephemeral=True)
            return None
        else: await subtract_from_user(ctx.author, 'image_allowance', 72 * count)
    elif resolution == '256x256':
        if (await getRemaining(ctx.author))[1] < (count * 64):
            await ctx.response.send_message(f"Oh no! You don't have enough image credits left!\nCredits: {(await getRemaining(ctx.author))[1]}\nRequired for {count} generation{'s' if count >= 2 else ''}: {count * 64} (64 x {count})", ephemeral=True)
            return None
        else: await subtract_from_user(ctx.author, 'image_allowance', 64 * count)
    response = await ctx.response.send_message(f"Now generating {count} image{'s' if count >= 2 else ''}:\n{prompt}\nBy: {ctx.author.mention}")
    generationDate = datetime.now(timezone('US/Pacific')).strftime('%m/%d/%Y, at %I:%M:%S %p')
    b64_images = ai.Image.create(prompt=prompt, n=count, size=resolution, response_format='b64_json')['data']
    images = []
    for genNumber, b64_image in enumerate(b64_images):
        image = f"openai_data/image_cache/{ctx.author.id}_{generationDate.replace('/', '-').replace(', at ', '_').replace(' ', '-').replace(':', '.')}_{genNumber + 1}-of-{count}.png"
        images.append(image)
        with open(image, mode="wb") as f:
            f.write(base64.b64decode(b64_image['b64_json']))
            f.close()
    fillerImages = [['assets/logo/1024.png', 1024], ['assets/logo/512.png', 512], ['assets/logo/256.png', 256]]
    def place(newImage: Image.Image, image, x, y):
        addImage = Image.open(image)
        newImage.paste(addImage, (x, y))
        return newImage
    def tile(images, fillerImage):
        sizeRef = Image.open(images[0])
        size = math.ceil((len(images))**0.5)
        canvas = Image.new('RGBA', (sizeRef.width * size, sizeRef.height * size))
        for fillerImage in fillerImages:
            if fillerImage[1] == sizeRef.width:
                fillerImage = fillerImage[0]
                break
        coordinates = [[x * sizeRef.width, y * sizeRef.height] for x in range(size) for y in range(size)]
        for imageNumber, addImage in enumerate(images): canvas = place(canvas, addImage, coordinates[imageNumber][1], coordinates[imageNumber][0])
        for i in range((size**2)-(imageNumber+1)):
            imageNumber += 1
            canvas = place(canvas, fillerImage, coordinates[imageNumber][1], coordinates[imageNumber][0])
        return canvas
    image = f"openai_data/image_cache/{ctx.author.id}_{generationDate.replace('/', '-').replace(', at ', '_').replace(' ', '-').replace(':', '.')}.png"
    tile(images, fillerImages).save(image)
    if resolution == '1024x1024':
        if count == 10:
            imageResized = Image.open(image)
            imageResized = imageResized.resize((round(imageResized.size[0]*0.5), round(imageResized.size[1]*0.5)))
            imageResized.save(image)
        elif count > 4:
            imageResized = Image.open(image)
            imageResized = imageResized.resize((round(imageResized.size[0]*(2/3)), round(imageResized.size[1]*(2/3))))
            imageResized.save(image)
    await response.edit_original_response(content=f'{prompt}\n{count} image{"s" if count >> 1 else ""}, by: {ctx.author.mention}', file=discord.File(image), view=image_buttons(count, images, response) if count >= 2 else None)
    os.remove(image)
    with open(f"openai_data/image_cache/images.json", mode="r+") as f:
        fileData = json.load(f)
        newData = {"user": f"{ctx.author.name}#{ctx.author.discriminator}", "date": generationDate, "prompt": prompt, "imageCount": count, "resolution": resolution}
        fileData["generations"].append(newData)
        f.seek(0)
        json.dump(fileData, f, indent=4)
        f.truncate()

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
    except (aio.exceptions.TimeoutError, discord.ext.commands.errors.CommandInvokeError):
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
        sub.Popen(f"start cmd /k \"python3 {path}\"", shell=True)
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
            f=open(f"{user.id}_roles.txt", "w+")
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
            await aio.sleep(2)
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
                        await aio.sleep(2)
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
async def addroleall(ctx, id):
    role=discord.utils.get(ctx.message.guild.roles, id=int(id))
    for m in ctx.message.guild.members:
        await m.add_roles(role)

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
    except (aio.exceptions.TimeoutError, discord.ext.commands.errors.CommandInvokeError):
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
        sub.Popen(f"start cmd /k \"{command}\"", shell=True)
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
    await aio.sleep(2)
    content=(await console.history(limit=1).flatten())[0].content
    if content.lower().startswith("co"):
        await aio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
    if content.lower().startswith("co"):
        await aio.sleep(2)
        content=(await console.history(limit=1).flatten())[0].content
    if content.lower().startswith("co"):
        await aio.sleep(2)
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
    except (aio.exceptions.TimeoutError, discord.ext.commands.errors.CommandInvokeError):
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
            await aio.sleep(2)
            content=(await console.history(limit=1).flatten())[0].content
            if content != "ping" and "```" in content:
                await ctx.send("ㅤ\nDiscordSRV console response check passed")
            else:
                await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                await aio.sleep(2)
                content=(await console.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await aio.sleep(2)
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
            await aio.sleep(2)
            content=(await console.history(limit=1).flatten())[0].content
            if content != "ping" and "```" in content:
                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                await ctx.send("ㅤ\nServer is running")
                await ctx.send("ㅤ\nNo issues found")
                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
            else:
                await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                await aio.sleep(2)
                content=(await console.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    await ctx.send("ㅤ\nServer is running")
                    await ctx.send("ㅤ\nNo issues found")
                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await aio.sleep(2)
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
        path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\ZMP.cmd"
        sub.Popen(f"start cmd /k {path}", shell=True)
        await ctx.send("ㅤ\nServer startup initiated")
        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
        if ctx.author.id != 968356025461768192:
            now=datetime.now()
            dateTime=now.strftime("%d/%m/%Y %H:%M:%S")
            date, sep, time=dateTime.partition(" ")
            sendSMS(messageSubject="ZMP ALERT", messageBody=f"{date} | {time}\n\nTag: {ctx.author} | ID: {ctx.author.id} | Name: {ctx.author.nick}\n\nUser issued command:\n\"{ctx.message.content}\"")
    sock.close()

@client.command()
@commands.has_any_role("Owner", "Admin", "luckperms", "Moderator", "Head Moderator", "Helper", "Staff")
async def vip(ctx, user):
    console=client.get_channel(950858523846271007)
    await console.send(f"eplaytime {user}")
    await aio.sleep(4)
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
    await aio.sleep(2)
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
        await aio.sleep(2)
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
        await aio.sleep(2)
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
        user=await guild.fetch_user(userID)
        await ctx.send(f"{tag} was banned from the Minecraft server. Would you like to ban them on Discord?\nUsername: {user}")
        def check_rule(message: discord.Message):
            return message.author.id==ctx.message.author.id
        try:
            answer=(await client.wait_for('message', check=check_rule, timeout=20)).content
        except (aio.exceptions.TimeoutError, discord.ext.commands.errors.CommandInvokeError):
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
        await aio.sleep(2)
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
            await aio.sleep(2)
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
                await aio.sleep(2)
                content=(await console.history(limit=1).flatten())[0].content
                if "https://luckperms.net/editor/" in content:
                    if "https://luckperms.net/editor/" in content:
                        before, sep, editor=content.partition("https://luckperms.net/editor/")
                        editor, sep, after=editor.partition("\n")
                        if "```" in editor:
                            editor, sep, after=editor.partition("```")
                        await ctx.author.send(f"https://luckperms.net/editor/{editor}")
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
    await aio.sleep(2)
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
                    await aio.sleep(2)
                    content=(await console.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await aio.sleep(2)
                        content=(await console.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            await ctx.send("ㅤ\nServer is running")
                            await ctx.send("ㅤ\nNo issues found")
                            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await aio.sleep(2)
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
                path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\ZMP.cmd"
                sub.Popen(f"start cmd /k {path}", shell=True)
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
                    await aio.sleep(2)
                    content=(await console.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await aio.sleep(2)
                        content=(await console.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await aio.sleep(2)
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
            await aio.sleep(4)
            content=(await console.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("players: ")
            content, sep, after=content.partition("\n")
            content, sep, after=content.partition("```")
            if content=="":
                await aio.sleep(2)
            else:
                pass
            await ctx.send(f"```{content}```")
        elif command.lower()=="players":
            await console.send("list")
            await aio.sleep(4)
            content=(await console.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("/list")
            before, sep, content=content.partition("] ")
            content, sep, after=content.partition("```")
            if content=="":
                await aio.sleep(2)
            else:
                pass
            await ctx.send(f"```{content}```")
        elif command.lower()=="tps":
            await console.send("tps")
            await aio.sleep(4)
            content=(await console.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("] ")
            content, sep, after=content.partition("```")
            if content=="":
                await aio.sleep(2)
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
                await aio.sleep(2)
                content=(await console.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    await ctx.send("ㅤ\nServer is running")
                    await ctx.send("ㅤ\nNo issues found")
                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await aio.sleep(2)
                    content=(await console.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await aio.sleep(2)
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
            path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\ZMP.cmd"
            sub.Popen(f"start cmd /k {path}", shell=True)
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
                    await aio.sleep(2)
                    content=(await console.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await aio.sleep(2)
                        content=(await console.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await aio.sleep(2)
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
    await aio.sleep(2)
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
        await aio.sleep(2)
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
            await aio.sleep(4)
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
            await aio.sleep(2)
            content=(await buildconsole.history(limit=1).flatten())[0].content
            if content != "ping" and "```" in content:
                await ctx.send("ㅤ\nDiscordSRV console response check passed")
            else:
                await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                await aio.sleep(2)
                content=(await buildconsole.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await aio.sleep(2)
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
            await aio.sleep(2)
            content=(await buildconsole.history(limit=1).flatten())[0].content
            if content != "ping" and "```" in content:
                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                await ctx.send("ㅤ\nServer is running")
                await ctx.send("ㅤ\nNo issues found")
                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
            else:
                await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                await aio.sleep(2)
                content=(await buildconsole.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    await ctx.send("ㅤ\nServer is running")
                    await ctx.send("ㅤ\nNo issues found")
                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await aio.sleep(2)
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
        path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\BUILD.cmd"
        sub.Popen(f"start cmd /k {path}", shell=True)
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
    await aio.sleep(2)
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
        await aio.sleep(2)
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
        await aio.sleep(2)
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
        await aio.sleep(2)
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
            await aio.sleep(2)
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
                await aio.sleep(2)
                content=(await buildconsole.history(limit=1).flatten())[0].content
                if "https://luckperms.net/editor/" in content:
                    if "https://luckperms.net/editor/" in content:
                        before, sep, editor=content.partition("https://luckperms.net/editor/")
                        editor, sep, after=editor.partition("\n")
                        if "```" in editor:
                            editor, sep, after=editor.partition("```")
                        await ctx.author.send(f"https://luckperms.net/editor/{editor}")
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
    await aio.sleep(2)
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
                    await aio.sleep(2)
                    content=(await buildconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await aio.sleep(2)
                        content=(await buildconsole.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            await ctx.send("ㅤ\nServer is running")
                            await ctx.send("ㅤ\nNo issues found")
                            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await aio.sleep(2)
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
                path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\BUILD.cmd"
                sub.Popen(f"start cmd /k {path}", shell=True)
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
                    await aio.sleep(2)
                    content=(await buildconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await aio.sleep(2)
                        content=(await buildconsole.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await aio.sleep(2)
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
            await aio.sleep(4)
            content=(await buildconsole.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("players: ")
            content, sep, after=content.partition("\n")
            content, sep, after=content.partition("```")
            if content=="":
                await aio.sleep(2)
            else:
                pass
            await ctx.send(f"```{content}```")
        elif command.lower()=="players":
            await buildconsole.send("list")
            await aio.sleep(4)
            content=(await buildconsole.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("/list")
            before, sep, content=content.partition("] ")
            content, sep, after=content.partition("```")
            if content=="":
                await aio.sleep(2)
            else:
                pass
            await ctx.send(f"```{content}```")
        elif command.lower()=="tps":
            await buildconsole.send("tps")
            await aio.sleep(4)
            content=(await buildconsole.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("] ")
            content, sep, after=content.partition("```")
            if content=="":
                await aio.sleep(2)
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
                await aio.sleep(2)
                content=(await buildconsole.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    await ctx.send("ㅤ\nServer is running")
                    await ctx.send("ㅤ\nNo issues found")
                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await aio.sleep(2)
                    content=(await buildconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await aio.sleep(2)
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
            path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\BUILD.cmd"
            sub.Popen(f"start cmd /k {path}", shell=True)
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
                    await aio.sleep(2)
                    content=(await buildconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await aio.sleep(2)
                        content=(await buildconsole.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await aio.sleep(2)
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
    await aio.sleep(2)
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
        await aio.sleep(2)
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
            await aio.sleep(4)
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
            await aio.sleep(2)
            content=(await mzmpconsole.history(limit=1).flatten())[0].content
            if content != "ping" and "```" in content:
                await ctx.send("ㅤ\nDiscordSRV console response check passed")
            else:
                await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                await aio.sleep(2)
                content=(await mzmpconsole.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await aio.sleep(2)
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
            await aio.sleep(2)
            content=(await mzmpconsole.history(limit=1).flatten())[0].content
            if content != "ping" and "```" in content:
                await ctx.send("ㅤ\nDiscordSRV console response check passed")
                await ctx.send("ㅤ\nServer is running")
                await ctx.send("ㅤ\nNo issues found")
                await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
            else:
                await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                await aio.sleep(2)
                content=(await mzmpconsole.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    await ctx.send("ㅤ\nServer is running")
                    await ctx.send("ㅤ\nNo issues found")
                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await aio.sleep(2)
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
        path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\MZMP.cmd"
        sub.Popen(f"start cmd /k {path}", shell=True)
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
    await aio.sleep(2)
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
        await aio.sleep(2)
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
        await aio.sleep(2)
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
        await aio.sleep(2)
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
            await aio.sleep(2)
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
                await aio.sleep(2)
                content=(await mzmpconsole.history(limit=1).flatten())[0].content
                if "https://luckperms.net/editor/" in content:
                    if "https://luckperms.net/editor/" in content:
                        before, sep, editor=content.partition("https://luckperms.net/editor/")
                        editor, sep, after=editor.partition("\n")
                        if "```" in editor:
                            editor, sep, after=editor.partition("```")
                        await ctx.author.send(f"https://luckperms.net/editor/{editor}")
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
    await aio.sleep(2)
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
                    await aio.sleep(2)
                    content=(await mzmpconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await aio.sleep(2)
                        content=(await mzmpconsole.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                            await ctx.send("ㅤ\nServer is running")
                            await ctx.send("ㅤ\nNo issues found")
                            await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await aio.sleep(2)
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
                path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\MZMP.cmd"
                sub.Popen(f"start cmd /k {path}", shell=True)
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
                    await aio.sleep(2)
                    content=(await mzmpconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await aio.sleep(2)
                        content=(await mzmpconsole.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await aio.sleep(2)
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
            await aio.sleep(4)
            content=(await mzmpconsole.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("players: ")
            content, sep, after=content.partition("\n")
            content, sep, after=content.partition("```")
            if content=="":
                await aio.sleep(2)
            else:
                pass
            await ctx.send(f"```{content}```")
        elif command.lower()=="players":
            await mzmpconsole.send("list")
            await aio.sleep(4)
            content=(await mzmpconsole.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("/list")
            before, sep, content=content.partition("] ")
            content, sep, after=content.partition("```")
            if content=="":
                await aio.sleep(2)
            else:
                pass
            await ctx.send(f"```{content}```")
        elif command.lower()=="tps":
            await mzmpconsole.send("tps")
            await aio.sleep(4)
            content=(await mzmpconsole.history(limit=1).flatten())[0].content
            before, sep, content=content.partition("] ")
            content, sep, after=content.partition("```")
            if content=="":
                await aio.sleep(2)
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
                await aio.sleep(2)
                content=(await mzmpconsole.history(limit=1).flatten())[0].content
                if content != "ping" and "```" in content:
                    await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    await ctx.send("ㅤ\nServer is running")
                    await ctx.send("ㅤ\nNo issues found")
                    await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                else:
                    await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                    await aio.sleep(2)
                    content=(await mzmpconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        await ctx.send("ㅤ\nServer is running")
                        await ctx.send("ㅤ\nNo issues found")
                        await ctx.send(content=f"ㅤ\n**OPERATION COMPLETE**")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await aio.sleep(2)
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
            path="C:\\Users\\Overdrive\\Desktop\\MINECRAFT_SERVERS\\MZMP.cmd"
            sub.Popen(f"start cmd /k {path}", shell=True)
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
                    await aio.sleep(2)
                    content=(await mzmpconsole.history(limit=1).flatten())[0].content
                    if content != "ping" and "```" in content:
                        await ctx.send("ㅤ\nDiscordSRV console response check passed")
                    else:
                        await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                        await aio.sleep(2)
                        content=(await mzmpconsole.history(limit=1).flatten())[0].content
                        if content != "ping" and "```" in content:
                            await ctx.send("ㅤ\nDiscordSRV console response check passed")
                        else:
                            await ctx.send("ㅤ\nDiscordSRV console response check failed. Retrying...")
                            await aio.sleep(2)
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

client.run(str(os.getenv("TOKEN")))
