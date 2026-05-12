import discord
from discord import ui, app_commands
from discord.ext import commands
import os

# --- הגדרות IDs (השתמשתי במה ששלחת לי) ---
TOKEN = os.getenv('DISCORD_TOKEN')
MY_USER_ID = 1130542850883469443

# IDs של הרולים לחנות
ROLE_SUPPORTER = 1503819239310627068
ROLE_VIP = 1503817695466881255
ROLE_TICKET_STAFF = 1501316672345211041

# הגדרות פריטים (שם, מחיר, ID)
SHOP_ITEMS = {
    "supporter": {"name": "Server-Supporter 🎗️", "price": 2000, "role_id": ROLE_SUPPORTER},
    "vip": {"name": "💎 VIP", "price": 5000, "role_id": ROLE_VIP},
    "staff": {"name": "Ticket-Staff 🛠️", "price": 15000, "role_id": ROLE_TICKET_STAFF}
}

# מערכת יתרות (בזיכרון - נמחק בריסטארט)
user_balances = {}

# --- מחלקת הכפתורים של החנות ---
class ShopView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="קנה Supporter (2,000)", style=discord.ButtonStyle.secondary, custom_id="btn_supporter")
    async def buy_supporter(self, i: discord.Interaction, b: ui.Button):
        await self.handle_purchase(i, "supporter")

    @ui.button(label="קנה 💎 VIP (5,000)", style=discord.ButtonStyle.blurple, custom_id="btn_vip")
    async def buy_vip(self, i: discord.Interaction, b: ui.Button):
        await self.handle_purchase(i, "vip")

    @ui.button(label="קנה Ticket-Staff (15,000)", style=discord.ButtonStyle.danger, custom_id="btn_staff")
    async def buy_staff(self, i: discord.Interaction, b: ui.Button):
        await self.handle_purchase(i, "staff")

    @ui.button(label="בדיקת יתרה 💳", style=discord.ButtonStyle.success, custom_id="btn_balance")
    async def check_bal(self, i: discord.Interaction, b: ui.Button):
        bal = user_balances.get(i.user.id, 0)
        await i.response.send_message(f"💰 היתרה הנוכחית שלך: `{bal}` מטבעות.", ephemeral=True)

    async def handle_purchase(self, i, item_key):
        item = SHOP_ITEMS[item_key]
        user_id = i.user.id
        bal = user_balances.get(user_id, 0)

        if bal < item["price"]:
            return await i.response.send_message(f"❌ חסר לך `{item['price'] - bal}` מטבעות!", ephemeral=True)
        
        role = i.guild.get_role(item["role_id"])
        if not role:
            return await i.response.send_message("❌ הרול לא נמצא בשרת, דבר עם אונר.", ephemeral=True)
        
        if role in i.user.roles:
            return await i.response.send_message("❌ כבר קנית את הרול הזה!", ephemeral=True)

        # ביצוע הרכישה
        user_balances[user_id] -= item["price"]
        await i.user.add_roles(role)
        await i.response.send_message(f"✅ תתחדש! קנית את הרול **{item['name']}**!", ephemeral=True)

# --- הגדרות הבוט ---
class CyberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(ShopView()) # גורם לכפתורים לעבוד גם אחרי הפעלה מחדש
        await self.tree.sync()

bot = CyberBot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} | הבוט של נהוראי באוויר!")

# --- צבירת כסף מהודעות ---
@bot.event
async def on_message(msg):
    if msg.author.bot: return
    # נותן 10 מטבעות על כל הודעה
    user_balances[msg.author.id] = user_balances.get(msg.author.id, 0) + 10
    await bot.process_commands(msg)

# --- פקודות אונר ---

@bot.tree.command(name="setup_shop", description="אונר | הקמת חנות הרולים בחדר")
async def setup_shop(i: discord.Interaction):
    if i.user.id != MY_USER_ID:
        return await i.response.send_message("🚫 רק נהוראי יכול להקים את החנות!", ephemeral=True)

    emb = discord.Embed(
        title="🛒 Cyber-Market | חנות הרולים",
        description=(
            "ברוכים הבאים! כאן קונים רולים עם המטבעות שהרווחתם.\n\n"
            "**מחירון:**\n"
            "🎗️ **Server-Supporter:** `2,000` מטבעות\n"
            "💎 **VIP:** `5,000` מטבעות\n"
            "🛠️ **Ticket-Staff:** `15,000` מטבעות\n\n"
            "*כל הודעה שאתם כותבים בשרת שווה 10 מטבעות!*"
        ),
        color=0x2b2d31
    )
    emb.set_footer(text="Developed by Nehoray 👑")
    
    await i.channel.send(embed=emb, view=ShopView())
    await i.response.send_message("החנות הוקמה בהצלחה!", ephemeral=True)

@bot.tree.command(name="add_money", description="אונר | הבא כסף למשתמש")
async def add_money(i: discord.Interaction, member: discord.Member, amount: int):
    if i.user.id != MY_USER_ID: return
    user_balances[member.id] = user_balances.get(member.id, 0) + amount
    await i.response.send_message(f"💵 הבאת `{amount}` מטבעות ל-{member.mention}!")

bot.run(TOKEN)
