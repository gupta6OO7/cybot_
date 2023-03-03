import discord
import random
from discord.ui import View
from discord import ui
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from typing import Optional
from discord.ext.commands import Bot
import psycopg2
import requests
import asyncio
from datetime import datetime
from discord.ext import tasks
import string


conn = psycopg2.connect(database="testdb", user="postgres", password="admin", host="localhost", port="5432")
cur = conn.cursor()
cur.execute('create table if not exists scoringyess ( UId text primary key, Score integer )')
conn.commit()
cur.execute('create table if not exists disc_cf_id (DiscID text primary key, Cf_ID text)')
conn.commit()
cur.execute('create table if not exists PROBLEMS (ContestID integer,Index text,Rating integer, Name text)')
conn.commit()
cur.execute(
    'create table if not exists Sololevelling ( userdisc text primary key, usercf text, contestid integer, index text)')
conn.commit()
cur.execute('create table if not exists duelchallenge(user1 text, user2 text, ContestID integer, index text)')
conn.commit()
intents = discord.Intents.default()
intents.message_content = True
tag_list = [
    'implementation',
    'math',
    'greedy',
    'dp',
    'data structures',
    'brute force',
    'constructive algorithms',
    'graphs',
    'sortings',
    'binary search',
    'dfs and similar',
    'trees',
    'strings',
    'number theory',
    'combinatorics',
    'geometry',
    'bitmasks',
    'two pointers',
    'dsu',
    'shortest paths',
    'probabilities',
    'divide and conquer',
    'hashing',
    'games',
    'flows',
    'interactive',
    'matrices',
    'string suffix structures',
    'fft',
    'graph matchings',
    'ternary search',
    'expression parsing',
    'meet-in-the-middle',
    '2-sat',
    'chinese remainder theorem',
    'schedules']
duelrating = None


class ButtonYesNo(View):
    user1 = None
    inter = None

    def __init__(self, Interaction: discord.Interaction, timeout: float, user: discord.Member) -> None:
        super().__init__(timeout=timeout)

        self.user1 = user
        self.inter = Interaction
        print(user)
        self.user = user

    @ui.button(emoji="✅", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):

        print(f"{interaction.user} {self.user1} ")
        global duelrating
        global taglisduel
        if interaction.user == self.user1:
            user1 = self.inter.user
            user2 = self.user1
            cur.execute('select Cf_id from disc_cf_id where DiscID =%s or DiscID = %s', ((str)(user1), (str)(user2),))
            conn.commit
            rows = cur.fetchall()
            handle1 = rows[0][0]
            handle2 = rows[1][0]
            user1doneporblems = get_user_problems(handle1)
            user2doneproblems = get_user_problems(handle2)
            alldoneproblems = user1doneporblems + user2doneproblems
            alldoneproblems = list(alldoneproblems)
            if duelrating is not None and (duelrating < 800 or duelrating > 3500 or duelrating % 100 != 0):
                await self.response.send_message("Rating dhang se daal")
            else:
                unsolvedprobs = get_user_unsolved_problems(alldoneproblems, duelrating, None)
                if not unsolvedprobs:
                    await self.inter.edit_original_response(f"Nahi hai bhai question Bank me", view=None)
                    return
                unsolgiven = random.choice(unsolvedprobs)
                linktobesold = "https://codeforces.com/contest/" + (str)(unsolgiven[0]) + "/problem/" + (str)(
                    unsolgiven[1])
                cur.execute('Insert into duelchallenge values(%s,%s,%s,%s)',
                            ((str)(self.inter.user), (str)(interaction.user), unsolgiven[0], unsolgiven[1],))
                conn.commit()
                desc = f"your time has come go solve [this]({linktobesold})"
                ti = "Here is your problem"
                embed = send_embed(ti, desc)
                await self.inter.edit_original_response(embed=embed, view=None)

        else:
            await interaction.response.send_message('Tere lie nahi tha bhai', ephemeral=True)
        pass

    @ui.button(emoji="⛔", style=discord.ButtonStyle.red)
    async def no(self, interaction, button):
        if interaction.user == self.user1:
            await self.inter.edit_original_response(
                embed=send_embed("Battle Declined", "Its not the first time you are rejected"), view=None)
        else:
            await interaction.response.send_message('Tere lie nahi tha bhai', ephemeral=True)
        pass


def get_user_problems(handle):
    user_problems = []
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    response = requests.get(url)
    data = response.json()
    result = data['result']

    for x in result:
        if x['verdict'] is None:
            continue
        elif x['verdict'] == 'OK':
            user_problems.append([x['problem']['contestId'], x['problem']['index']])

    return user_problems


def get_user_unsolved_problems(user_problems, rating, tags):
    unsolved_user_problems = []
    if rating is None:
        cur.execute('SELECT ContestID, Index, Rating, Tags from PROBLEMS')
    else:
        cur.execute("SELECT ContestID, Index, Rating, Tags from PROBLEMS  where Rating = %s", ((str)(rating),))
    conn.commit()
    rows = cur.fetchall()

    for row in rows:
        bol = 1
        if tags:

            for tag in tags:
                i = 0
                while i < 35:
                    if tag_list[i] == tag:
                        break
                    i += 1
                if row[3][i] == 0:
                    bol = 0
                    break
            if bol == 0:
                continue
        for x in user_problems:
            if x[0] == row[0] and x[1] == row[1]:
                bol = 0
                break

        if bol == 1:
            unsolved_user_problems.append([row[0], row[1]])

    return unsolved_user_problems


bot = commands.Bot(command_prefix="!", intents=intents, )
choices_made = {}
bot_button_message_id = None
score_dict = {}


def send_embed(ti, desc):
    embed = discord.Embed(
        colour=discord.Colour.dark_teal(),
        description=desc,
        title=ti
    )
    return embed


@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"Slash commands synced and lenght is" + str(len(synced)) + "commnads")
    reminder.start()


def unixToHumanandUtkarsh(seconds):
    ans = ""
    extraTime = seconds % (24 * 60 * 60)
    hours = extraTime // 3600
    minutes = (extraTime % 3600) // 60
    minutes += 30
    if minutes >= 60:
        hours += 1
        minutes = minutes - 60
    hours += 5
    if hours >= 24:
        hours = hours - 24

    if hours < 10:
        ans += '0'
    ans += str(hours)
    ans += ":"
    if minutes < 10:
        ans += '0'
    ans += str(minutes)

    return ans


@tasks.loop(seconds=3600)
async def reminder():
    url = "https://codeforces.com/api/contest.list?"
    response = requests.get(url)
    data = response.json()
    result = data['result']
    ts = result[0]['startTimeSeconds']
    contest = result[0]['name']
    for r in result:
        if r['startTimeSeconds'] < ts and r['phase'] == "BEFORE":
            ts = r['startTimeSeconds']
            contest = r['name']
        if r['phase'] == "FINISHED":
            break
    time1 = unixToHumanandUtkarsh(ts)
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    t1 = time1.split(':')
    t2 = current_time.split(':')
    delay = int(t1[0]) * 60 + int(t1[1]) - int(t2[0]) * 60 - int(t2[1])
    channel = bot.get_channel(1056929299501953104)
    if 120 >= delay >= 0:
        desc = f"@everyone {contest} begins at {time1}"
        title = 'Contest Reminder'
        await channel.send(desc)


def asking_compilation_error(Interaction, handlename, random_key):
    handlemention = Interaction.user
    print(handlename)

    linktorecentsub = "https://codeforces.com/api/user.status?handle=" + handlename + "&from=1&count=1"

    embed = discord.Embed(
        colour=discord.Colour.dark_teal(),
        description=f"{Interaction.user.mention} Submit a compilation error to this problem 👉 [{random_key}]({handlesetproblems[random_key]})",
        title='Identify Yourself'
    )
    embed.set_image(
        url="https://i0.wp.com/greglawlegal.com/wp-content/uploads/2016/07/Do-You-Need-To-Identify-Yourself-To-Law-Enforcement-Utah.png")
    return embed


handlesetproblems = {"System Administrator": "https://codeforces.com/problemset/problem/245/A"
    , "Four Segments": "https://codeforces.com/problemset/problem/1468/E"
    , "DZY Loves Hash": "https://codeforces.com/problemset/problem/447/A"
    , "Display Size": "https://codeforces.com/problemset/problem/747/A"
    , "Palindromic Supersequence": "https://codeforces.com/problemset/problem/932/A"
    , "Johny Likes Numbers": "https://codeforces.com/problemset/problem/678/A"
    , "Sleuth": "https://codeforces.com/problemset/problem/49/A"
    , "Glory Addicts": "https://codeforces.com/problemset/problem/1738/A"
    , "A pile of stones": "https://codeforces.com/problemset/problem/1159/A"
    , "Triangular numbers": "https://codeforces.com/problemset/problem/47/A"
    , "The Doors": "https://codeforces.com/problemset/problem/1143/A"}


@bot.command()
async def ping(ctx):
    desc = f'@everyone'
    ti = 'hello'
    await ctx.send(f"@everyone")


def changearg(arg):
    if arg != 'meet-in-the-middle' and arg != '2-sat':
        arg = arg.replace('-', ' ')
    print(arg)
    return arg


@bot.tree.command(name="solo_arise", description="Gives you a problem from codeforces")
@app_commands.describe(tags='Enter upto 5 tags seprated by commas and then a space')
@app_commands.describe(rating='Enter the rating of problem you want to solve ')
async def solo_arise(Interaction: discord.Interaction, rating: int = None, tags: str = None):
    taglis = []
    if tags != None:
        taglis = tags.split(', ')
    cur.execute('select userdisc from sololevelling where userdisc=%s', ((str)(Interaction.user),))
    conn.commit()
    roww = cur.fetchall()
    if roww:
        desc = 'You are already in solo Complete you ongoing solo by using solo_complete command'
        ti = 'Already in solo'
        embed = send_embed(ti, desc)
        await Interaction.response.send_message(embed=embed)
        return
    cur.execute('select Cf_ID from disc_cf_id where DiscID=%s', ((str)(Interaction.user),))
    conn.commit()
    row = cur.fetchall()
    if row is None:
        desc = 'You have not identified your handle to do so use !handle identify <cf_id>'
        ti = 'Identification Pending'
        embed = send_embed(ti, desc)
        await Interaction.response.send_message(embed=embed)
        return
    else:
        user_probs = get_user_problems(row[0][0])
        if rating is not None and (rating < 800 or rating > 3500 or rating % 100 != 0):
            await Interaction.response.send_message("Rating dhang se daal")
        else:
            unsolvedprobs = get_user_unsolved_problems(user_probs, rating, taglis)
            if not unsolvedprobs:
                await Interaction.response.send_message(f"Nahi hai bhai question Bank me")
                return
            unsolgiven = random.choice(unsolvedprobs)
            linktobesold = "https://codeforces.com/contest/" + (str)(unsolgiven[0]) + "/problem/" + (str)(unsolgiven[1])
            cur.execute('insert into sololevelling values(%s,%s,%s,%s)',
                        ((str)(Interaction.user), row[0][0], unsolgiven[0], unsolgiven[1],))
            conn.commit()
            desc = f"your time has come go solve [this]({linktobesold})"
            ti = "Here is your problem"
            embed = send_embed(ti, desc)
            await Interaction.response.send_message(embed=embed)


@bot.tree.command(name="solo_end", description="Ends your ongoing solo")
async def solo_end(Interaction: discord.Interaction):
    user = (str)(Interaction.user)
    cur.execute('select * from sololevelling where userdisc=%s', (user,))
    conn.commit()
    rows = cur.fetchall()
    if not rows:
        desc = 'You are not in solo'
        ti = 'Go level up!'
        embed = send_embed(ti, desc)
        await Interaction.response.send_message(embed=embed)
        return
    url = f"https://codeforces.com/api/user.status?handle={rows[0][1]}&from=1&count=30"
    response = requests.get(url)
    data = response.json()
    result = data['result']
    bool = 0
    for res in result:
        if res['problem']['contestId'] == (str)(rows[0][2]) and res['problem']['index'] == rows[0][3]:
            if res['verdict'] == 'OK':
                bool = 1
                break
    if bool == 1:
        desc = 'You have levelled up '
        ti = 'Level Up!'
        embed = send_embed(ti, desc)
        await Interaction.response.send_message(embed=embed)
    else:
        desc = 'Ese kese package milega'
        ti = 'Gonna cry ?'
        embed = send_embed(ti, desc)
        await Interaction.response.send_message(embed=embed)

    cur.execute('Delete from sololevelling where userdisc=%s', (user,))
    conn.commit()


@bot.tree.command(name='handle_identify', description='Identify Your handles and get started')
@app_commands.describe(handle_name="Enter the handle name")
async def handle_identify(Interaction: discord.Interaction, handle_name: str):
    CFID = handle_name
    cur.execute('select * from disc_cf_id where DiscID=%s', ((str)(Interaction.user),))
    conn.commit()
    rows = cur.fetchall()
    if rows:
        ti = 'Already Identified'
        desc = 'The handle is already registered to database to change it to different account use handle_change'
        embed = send_embed(ti, desc)
        await Interaction.response.send_message(embed=embed)
        return
    linktouser = "https://codeforces.com/api/user.info?handles=" + CFID
    response = requests.get(linktouser)
    if response.status_code == 200:
        random_key = random.choice(list(handlesetproblems.keys()))
        embed = asking_compilation_error(Interaction, CFID, random_key)
        await Interaction.response.send_message(embed=embed)
        await asyncio.sleep(60)
        linktorecentsub = "https://codeforces.com/api/user.status?handle=" + CFID + "&from=1&count=1"
        response = requests.get(linktorecentsub)
        if response.status_code == 200:
            data = response.json()
            final_data = data['result'][0]
            if final_data['problem']['name'] == random_key:
                if final_data['verdict'] == 'COMPILATION_ERROR':
                    try:
                        user = (str)(Interaction.user)
                        userid = (str)(CFID)
                        cur.execute('INSERT INTO disc_cf_id VALUES(%s,%s)', (user, userid,))
                    except Exception as error:
                        desc = f"{Interaction.user.mention} handle has been registerd with {userid} and stop spamming!!! )"
                        ti = 'Identification Already successfull'
                        embed = send_embed(ti, desc)
                        await Interaction.edit_original_response(embed=embed)
                        conn.commit()
                        return
                    conn.commit()
                    desc = f"{Interaction.user.mention} handle has been registerd with {userid}"
                    ti = 'Identification Successfull'
                    embed = send_embed(ti, desc)
                    await Interaction.edit_original_response(embed=embed)
                else:
                    desc = 'Please only submit compilation error'
                    ti = 'Submission Error'
                    embed = send_embed(ti, desc)
                    await Interaction.edit_original_response(embed=embed)
            else:
                desc = 'You are too slow Try completing in 60 seconds'
                ti = 'Timed Out'
                embed = send_embed(ti, desc)
                await Interaction.edit_original_response(embed=embed)
        else:
            desc = 'please try again later there might be issues with API'
            ti = 'API ERROR'
            embed = embed
            Interaction.edit_original_response(embed=embed)
    else:
        desc = f'{CFID} mentioned does not exist'
        ti = 'Identification Unsuccessfull'
        embed = send_embed(ti, desc)
        await Interaction.response.send_message(embed=embed)


@bot.tree.command(name='handle_change', description='Updates your Codeforces handle ')
@app_commands.describe(handle_name="Enter the handle name")
async def handle_identify(Interaction: discord.Interaction, handle_name: str):
    CFID = handle_name
    cur.execute('select * from disc_cf_id where DiscID=%s', ((str)(Interaction.user),))
    conn.commit()
    rows = cur.fetchall()
    if rows:
        if rows[0][1] == CFID:
            desc = 'Handle is already set to this account'
            ti = 'Same as Old'
            await Interaction.response.send_message(embed=send_embed(ti, desc))
            return
        linktouser = "https://codeforces.com/api/user.info?handles=" + CFID
        response = requests.get(linktouser)
        if response.status_code == 200:
            random_key = random.choice(list(handlesetproblems.keys()))
            embed = asking_compilation_error(Interaction, CFID, random_key)
            await Interaction.response.send_message(embed=embed)
            await asyncio.sleep(60)
            linktorecentsub = "https://codeforces.com/api/user.status?handle=" + CFID + "&from=1&count=1"
            response = requests.get(linktorecentsub)
            if response.status_code == 200:
                data = response.json()
                final_data = data['result'][0]
                if final_data['problem']['name'] == random_key:
                    if final_data['verdict'] == 'COMPILATION_ERROR':
                        user = (str)(Interaction.user)
                        userid = (str)(CFID)
                        cur.execute('Update disc_cf_id set Cf_ID=%s where DiscID =%s', (userid, (str)(user),))
                        conn.commit()
                        desc = f"{Interaction.user.mention} handle has changed to {userid}"
                        ti = 'Updation Successfull'
                        embed = send_embed(ti, desc)
                        await Interaction.edit_original_response(embed=embed)
                    else:
                        desc = 'Please only submit compilation error'
                        ti = 'Submission Error'
                        embed = send_embed(ti, desc)
                        await Interaction.edit_original_response(embed=embed)
                else:
                    desc = 'You are too slow Try completing in 60 seconds'
                    ti = 'Timed Out'
                    embed = send_embed(ti, desc)
                    await Interaction.edit_original_response(embed=embed)
            else:
                desc = 'please try again later there might be issues with API'
                ti = 'API ERROR'
                embed = embed
                Interaction.edit_original_response(embed=embed)
        else:
            desc = 'No User exist with the given codeforces id provided'
            ti = 'No CF handle found'
            await Interaction.response.send_message(embed=send_embed(ti, desc))
    else:
        desc = 'Looks like you have not identified yours CF handle yet'
        ti = 'Updation Unsuccesfull'
        await Interaction.response.send_message(embed=send_embed(ti, desc))


@bot.tree.command(name='duel_end', description='Ends the duel  you are currently in')
@app_commands.describe(handle_name="Mention the discord ID of user you want to battle")
async def handle_identify(Interaction: discord.Interaction, handle_name: discord.Member, rating: int = None):
    user = Interaction.user
    cur.execute()


@bot.tree.command(name='duel_challenge', description='Challenge other user for a 1v1 battle')
@app_commands.describe(handle_name="Mention the discord ID of user you want to battle")
async def handle_identify(Interaction: discord.Interaction, handle_name: discord.Member, rating: int = None):
    cur.execute("select Cf_ID from disc_cf_id where DiscID=%s", ((str)(Interaction.user),))
    conn.commit()
    global duelrating
    duelrating = rating
    row = cur.fetchall()
    if not row:
        await Interaction.response.send_message(embed=send_embed("Handle not identified",
                                                                 f"Looks like {Interaction.user.mention} has not identified handle"))
        return
    cur.execute("Select Cf_ID from disc_cf_id where DiscID=%s", ((str)(handle_name),))
    conn.commit()
    rows = cur.fetchall()
    if not rows:
        await Interaction.response.send_message(
            embed=send_embed("Handle not identified", f"Looks like {handle_name.mention} has not identified handle"))
        return
    if duelrating is not None and (duelrating < 800 or duelrating > 3500 or duelrating % 100 != 0):
        await Interaction.response.send_message("Rating dhang se daal")
        return
    cur.execute('select * from duelchallenge where user1=%s or user2=%s or user2=%s or user1 =%s',
                ((str)(Interaction.user), (str)(handle_name), (str)(Interaction.user), (str)(handle_name),))
    conn.commit()
    rowsy = cur.fetchall()
    if rowsy:
        # user1= row[0][0]
        # user2=row[1][1]
        # user3=row[0][1]
        # user4=row[1][0]

        await Interaction.response.send_message(
            embed=send_embed("Cant be done", "One of the user is already in a duel "))
        return
    desc = f"{handle_name.mention} you are being challenged by {Interaction.user.mention}"
    ti = f"Lets Battle it out"
    await  Interaction.response.send_message(embed=send_embed(ti, desc), view=ButtonYesNo(Interaction, 30, handle_name))


@bot.command(name="duel")
async def _command(ctx, member: discord.Member, rating):
    channel = ctx.channel
    react = ["✅", "⛔"]

    mes = await channel.send('Are you ready?')
    for tmp in react:
        await mes.add_reaction(tmp)

    def check(reaction, user):
        return user == member and str(reaction.emoji) in react

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await channel.send('Gonna cry?')
    else:
        i = react.index(str(reaction))
        if i == 1:
            await ctx.send("It is not the first time you have been rejected.")
        else:
            await ctx.send("Here we go!")


@bot.command(name="contest")
async def _command(ctx):
    channel = ctx.channel
    react = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

    mes = await channel.send('Div?')
    for tmp in react:
        await mes.add_reaction(tmp)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in react

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=10.0, check=check)
    except asyncio.TimeoutError:
        await channel.send('Kaanp kahe rahi ho?')
    else:
        i = react.index(str(reaction))
        if i == 0:
            await channel.send('Div 2 dede chup chaap!')
        else:
            rating = \
                [[[800, 900], [800, 800], [800, 800]],
                 [[1100, 1200], [900, 1000], [800, 900]],
                 [[1300, 1500], [1200, 1300], [900, 1100]],
                 [[1600, 1800], [1400, 1600], [1200, 1300]],
                 [[1900, 2100], [1700, 1800], [1400, 1600]]]
            i -= 1
            for problem in rating:
                await channel.send(str(problem[i]) + '\n')


TOKEN = 'MTA1MDg0NTEx1DQsW_NUUiPson7aKV8rAdll5NDk08'

bot.run(TOKEN)