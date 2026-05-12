import discord
from discord import ui, app_commands
from discord.ext import commands
import os

# --- הגדרות בסיסיות ---
TOKEN = os.getenv('DISCORD_TOKEN')
MY_USER_ID = 1130542850883469443

# IDs של הרולים
ROLE_SUPPORTER = 1503819239310627068
ROLE_VIP = 1503817695466881255
ROLE_TICKET_STAFF = 1501316672345211041

# מערכת יתרות
user_balances = {}

class ShopView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # שורה ראשונה - זוג כפתורים
    @ui.button(label="קנה Supporter 🎗️", style=discord.ButtonStyle.secondary, custom_id="shop:supporter", row=0)
    async def buy_supp(self, i: discord.Interaction, b: ui.Button):
        await self.handle_purchase(i, 2000, ROLE_SUPPORTER)

    @ui.button(label="קנה VIP 💎", style=discord.ButtonStyle.primary, custom_id="shop:vip", row=0)
    async def buy_vip(self, i: discord.Interaction, b: ui.Button):
        await self.handle_purchase(i, 5000, ROLE_VIP)

    # שורה שנייה - זוג כפתורים
    @ui.button(label="קנה Ticket-Staff 🛠️", style=discord.ButtonStyle.danger, custom_id="shop:staff", row=1)
    async def buy_staff(self, i: discord.Interaction, b: ui.Button):
        await self.handle_purchase(i, 15000, ROLE_TICKET_STAFF)

    @ui.button(label="בדיקת יתרה 💳", style=discord.ButtonStyle.success, custom_id="shop:bal", row=1)
    async def check_bal(self, i: discord.Interaction, b: ui.Button):
        bal = user_balances.get(i.user.id, 0)
        await i.response.send_message(f"💰 היתרה הנוכחית שלך: `{bal}` מטבעות.", ephemeral=True)

    async def handle_purchase(self, i, price, role_id):
        bal = user_balances.get(i.user.id, 0)
        if bal < price:
            return await i.response.send_message(f"❌ חסר לך `{price - bal}` מטבעות!", ephemeral=True)
        
        role = i.guild.get_role(role_id)
        if not role:
            return await i.response.send_message("❌ תקלה: הרול לא נמצא בשרת.", ephemeral=True)
        
        if role in i.user.roles:
            return await i.response.send_message("❌ כבר יש לך את הרול הזה!", ephemeral=True)

        user_balances[i.user.id] = bal - price
        await i.user.add_roles(role)
        await i.response.send_message(f"✅ תתחדש! קיבלת את הרול **{role.name}**!", ephemeral=True)

class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(ShopView())
        await self.tree.sync()

bot = CyberBot()

@bot.event
async def on_message(msg):
    if msg.author.bot: return
    user_balances[msg.author.id] = user_balances.get(msg.author.id, 0) + 10
    await bot.process_commands(msg)

@bot.tree.command(name="add_money", description="הוסף כסף למשתמש")
async def add_money(i: discord.Interaction, member: discord.Member, amount: int):
    if i.user.id != MY_USER_ID: return
    user_balances[member.id] = user_balances.get(member.id, 0) + amount
    await i.response.send_message(f"💵 נוספו `{amount}` מטבעות ל-{member.mention}")

@bot.tree.command(name="setup_shop", description="הקמת חנות")
async def setup_shop(i: discord.Interaction):
    if i.user.id != MY_USER_ID: return
    
    emb = discord.Embed(title="═══ 💠 CYBER-STORE MARKET 💠 ═══", color=0x2b2d31)
    emb.description = "👋 **ברוכים הבאים לחנות!**\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
    
    emb.add_field(name="🎗️ | Server-Supporter", value="**Price:** 2,000 Coins\nרול כבוד למשתתפים פעילים.", inline=False)
    emb.add_field(name="💎 | VIP Member", value="**Price:** 5,000 Coins\nגישה לחדרי VIP וצבע בולט.", inline=False)
    emb.add_field(name="🛠️ | TICKET-STAFF", value="**Price:** 15,000 Coins\n**הגישה למערכת הטיקטים!**", inline=False)
    
    emb.set_footer(text="Developed by NL 👑")
    
    await i.channel.send(embed=emb, view=ShopView())
    await i.response.send_message("החנות באוויר במבנה זוגות! 🔥", ephemeral=True)

bot.run(TOKEN)
