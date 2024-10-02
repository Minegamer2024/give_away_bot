import discord
from discord.ext import commands
import random
from datetime import timedelta
from typing import Literal
import sqlite3
import asyncio
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
client = commands.Bot(command_prefix="!", intents=intents)
db = sqlite3.connect("role.db")
db_member = sqlite3.connect("member.db")
db.execute("create table if not exists give_role (role_id integer, id integer)")
db_member.execute("create table if not exists member_give (members_id integer, server_id  integer)")
cr = db.cursor()
cr_member = db_member.cursor()
@client.event
async def on_ready():
    await client.tree.sync()
    await client.change_presence(activity=discord.Game(name="Giveaways"))
    print(f"ready {client.user}")
@client.tree.command(name="role", description="لأضافة الرتبة التي سيسمح لها بأستخدام البوت")
async def role_member(interaction: discord.Interaction, الرتبة: discord.Role, الوظية:Literal["اضافة","ازالة"]):
    guild = interaction.guild
    user = interaction.user
    owner = guild.owner_id
    cr.execute(f"select role_id from give_role where id = {interaction.guild.id}")
    result = [row[0] for row in cr.fetchall()]
    try:
        if user.id == owner:
                if الوظية == "اضافة":
                    if الرتبة.id in result:
                        await interaction.response.send_message(f"رتبة {الرتبة.mention} موجودة بالفعل", ephemeral=True)
                    else:
                        cr.execute(f"insert into give_role(role_id, id) values({الرتبة.id}, {interaction.guild.id})")
                        await interaction.response.send_message("تم اضافة الرتبة لقاعدة البيانات", ephemeral=True)
                        db.commit()
                elif الوظية == "ازالة":
                    if الرتبة.id in result:
                        cr.execute(f"delete from give_role where role_id = {الرتبة.id}")
                        await interaction.response.send_message("تم ازالة الرتبة من قاعدة البيانات", ephemeral=True)
                        db.commit()
                    else:
                        await interaction.response.send_message(f"رتبة {الرتبة.mention} غير موجودة في قاعدة البيانات", ephemeral=True)
        else:
            await interaction.response.send_message("اسف لكن وحده مالك السيرفر يستطيع استخدام هذا الامر", ephemeral=True)
    except:
        if user.id == owner:
            await interaction.response.send_message("يوجد خطأ غريب يرجى التأكد من انك ادخلت كل شيئ بشكل صحيح", ephemeral=True)
        else:
            await interaction.response.send_message("اسف لكن انت لا تملك الصلاحية لأستخدام هذا الامر", ephemeral=True)
@client.tree.command(name="giveaway", description="لبدء جيف اوي")
async def giveaway(interaction: discord.Interaction, الجائزة: str, الوصف: str, المدة: int, نوع_المدة: Literal["ثواني", "دقائق", "ساعات", "ايام"], عدد_الفائزين: int):
    cr.execute(f"select role_id from give_role where id = {interaction.guild.id}")
    members_check = cr_member.fetchall()
    if members_check == None:
        pass
    else:
        cr_member.execute(f"delete from member_give where server_id = {interaction.guild.id}")
    db_member.commit()
    owner_ids = interaction.guild.owner_id
    result = cr.fetchall()
    user = interaction.user
    for row in result:
        roless = interaction.guild.get_role(row[0])
    try:
        if roless in interaction.user.roles:
            if عدد_الفائزين >= 1:
                avatar = user.avatar.url
                member = []
                button = discord.ui.Button(label="🎉 انضمام", style=discord.ButtonStyle.primary)
                remove = discord.ui.Button(label="خروج", style=discord.ButtonStyle.red)
                embed = discord.Embed(
                    title=الوصف,
                    color=discord.Colour.gold()
                )
                embed.set_author(
                    name=الجائزة,
                    icon_url=avatar
                )
                embed.add_field(
                    name="الفائزين",
                    value="لا يوجد اي فائز حتى الان",
                    inline=False
                )
                embed.add_field(
                    name="المستضيف",
                    value=user.mention,
                    inline=False
                )
                embed.add_field(
                    name="عدد الفائزين",
                    value=عدد_الفائزين,
                    inline=False
                )
                embed.add_field(
                    name="عدد المشاركين",
                    value=len(member),
                    inline=False
                    )
                embed.add_field(
                    name="المدة",
                    value=f"{المدة} {نوع_المدة}"
                )
                embed.set_thumbnail(
                    url=interaction.guild.icon
                )
                view = discord.ui.View()
                view.add_item(button)
                view.add_item(remove)
                async def button_callback(interaction: discord.Interaction):
                    if interaction.user not in member:
                        member.append(interaction.user)
                        embed.set_field_at(3, name="عدد المشاركين", value=len(member), inline=False)
                        await interaction.response.edit_message(embed=embed, view=view)
                        await interaction.followup.send(f"لقد انضممت للجيف اوي يا {interaction.user.mention}", ephemeral=True)
                        cr_member.execute(f"insert into member_give(members_id, server_id) values({interaction.user.id}, {interaction.guild.id})")
                        db_member.commit()
                    else:
                        await interaction.response.send_message(f"لقد انضممت للجيف اوي بالفعل يا {interaction.user.mention}", ephemeral=True)
                async def remove_callback(interaction: discord.Interaction):
                    if interaction.user in member:
                        member.remove(interaction.user)
                        embed.set_field_at(3, name="عدد المشاركين", value=len(member), inline=False)
                        await interaction.response.edit_message(embed=embed, view=view)
                        await interaction.followup.send("لقد خرجت من الجيف اوي", ephemeral=True)
                        cr_member.execute(f"delete from member_give where server_id = {interaction.guild.id}")
                        db_member.commit()
                    else:
                        await interaction.response.send_message("انت خارج الجيف اوي بالفعل", ephemeral=True)
                button.callback = button_callback
                remove.callback = remove_callback
                await interaction.response.send_message(embed=embed, view=view)
                if نوع_المدة == "ثواني":
                    times = timedelta(seconds=المدة)
                elif نوع_المدة == "دقائق":
                    times = timedelta(minutes=المدة)
                elif نوع_المدة == "ساعات":
                    times = timedelta(hours=المدة)
                elif نوع_المدة == "ايام":
                    times = timedelta(days=المدة)
                await asyncio.sleep(times.total_seconds())
                if len(member) > 0:
                    if عدد_الفائزين >= len(member):
                        winner = random.sample(member, k=len(member))
                        embed.set_field_at(2, name="عدد الفائزين", value=len(member), inline=False)
                    else:
                        winner = random.sample(member, k=عدد_الفائزين)
                    winner_mention = " ".join([w.mention for w in winner])
                    embed.set_field_at(0, name="الفائزين", value=winner_mention, inline=False)
                    message = await interaction.followup.send(f"لقد فاز {winner_mention} ب {الجائزة}")
                    await message.add_reaction("🎉")
                else:
                    embed.set_field_at(0, name="الفائزون", value="لا يوجد اي فائز", inline=False)
                    await interaction.followup.send("لا يوجد فائز")
                button.disabled = True
                remove.disabled = True
                await interaction.edit_original_response(embed=embed, view=view)
            else:
                await interaction.response.send_message("لا يمكنك استخدام عدد اقل من 1 في عدد الفائزين", ephemeral=True)
        else:
            if user.id == owner_ids:
                await interaction.response.send_message("يجب عليك اضافة الرتبة التي اضفتها في قاعدة البيانات لنفسك حتى تتمكن من تشغيل البوت", ephemeral=True)
            else:
                await interaction.response.send_message("اسف لكن انت لا تملك الصلاحية لأستخدام هذا الامر", ephemeral=True)
    except:
        if interaction.user.id == owner_ids:
            await interaction.response.send_message("يوجد خطأ ما تأكد انك ادخلت الرتبة التي سوف تستخدم البوت وانك ادخلت كل شيئ بشكل صحيح", ephemeral=True)
        else:
            await interaction.response.send_message("اسف لكن انت لا تملك الصلاحية لأستخدام هذا الامر", ephemeral=True)
@client.tree.command(name="member", description="لمعرفة الاعضاء المشاركين في اخر جيف اوي")
async def member_join(interaction: discord.Interaction):
    owner = interaction.guild.owner_id
    try:
        cr.execute(f"select role_id from give_role where id = {interaction.guild.id}")
        for rows in cr.fetchall():
            role = interaction.guild.get_role(rows[0])
        if role in interaction.user.roles:
            cr_member.execute(f"select members_id from member_give where server_id = {interaction.guild.id}")
            members = [row[0] for row in cr_member.fetchall()]
            count_embed = discord.Embed(
                title="الاعضاء الماشركين في اخر جيف اوي",
                color= discord.Colour.green()
            )
            if len(members) >  0:
                for key, count_member in enumerate(members):
                    member = interaction.guild.get_member(count_member)
                    count_embed.add_field(
                        name=f"المشارك رقم {key + 1}",
                        value=member.mention,
                        inline=False
                    )
            else:
                count_embed.add_field(
                    name=f"المشاركين",
                    value="لا يوجد اي مشارك",
                    inline=False
                )
            await interaction.response.send_message(embed=count_embed, ephemeral=True)
        else:
            await interaction.response.send_message("اسف لكن انت لا تملك الصلاحية لأستخدام هذا الامر", ephemeral=True)
    except:
        if interaction.user.id == owner:
            await interaction.response.send_message("يوجد خطأ يرجى التأكد من اضافة الرتبة التي سوف تستخدم البوت", ephemeral=True)
        elif role in interaction.user.roles:
            await interaction.response.send_message("اسف لكن لا يمكنك استخدام هذا الامر الان", ephemeral=True)
        else:
            await interaction.response.send_message("اسف لكن انت لا تملك الصلاحية لأستخدام هذا الامر", ephemeral=True)       
client.run("your_bot_token")