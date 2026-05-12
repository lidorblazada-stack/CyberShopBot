import discord
from discord import ui, app_commands
from discord.ext import commands
import os

# --- הגדרות בסיסיות ---
TOKEN = os.getenv('DISCORD_TOKEN')
MY_USER_ID = 1130542850883469443

# IDs של הרולים (מעודכן לפי מה ששלחת)
ROLE_SUPPORTER = 1503819239310627068
ROLE_VIP = 1503817695466881255
ROLE_TICKET_STAFF = 1501316672345211041

# הגדרות חנות
SHOP_CONFIG = {
    "supporter": {"name": "Server-Supporter 🎗️", "price": 2000, "role_id": ROLE_SUPPORTER},
    "vip": {"name": "💎 VIP Member", "price": 5000, "role_id": ROLE_VIP},
    "staff": {"name": "Ticket-Staff 🛠️", "price": 15000, "role_id": ROLE_TICKET_STAFF}
}

user_balances = {}

class ShopView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="קנה Supporter 🎗️", style=discord.ButtonStyle.secondary, custom_id="buy_supp", row=0)
    async def buy_supp(self, i: discord.Interaction, b: ui.Button):
        await self.process_buy(i, "supporter")

    @ui.button(label="קנה VIP 💎", style=discord.ButtonStyle.primary, custom_id="buy_vip_btn", row=1)
    async def buy_vip_btn(self, i: discord.Interaction, b: ui.Button):
        await self.process_buy(i, "vip")

    @ui.button(label="קנה Ticket-Staff 🛠️", style=discord.ButtonStyle.danger, custom_id="buy_staff_btn", row=2)
    async def buy_staff_btn(self, i: discord.Interaction, b: ui.Button):
        await self.process_buy(i, "staff")

    @ui.button(label="בדיקת יתרה 💰", style=discord.ButtonStyle.success, custom_id="check_bal_btn", row=3)
    async def check_bal_btn(self, i: discord.Interaction, b: ui.Button):
        bal = user_balances.get(i.user.id, 0)
        await i.response.send_message(f"💰 היתרה שלך היא: `{bal}` מטבעות.", ephemeral=True)

    async def process_buy(self, i, key):
        item = SHOP_CONFIG[key]
        bal = user_balances.get(i.user.id, 0)
        
        if bal < item["price"]:
            return await i.response.send_message(f"❌ חסר לך `{item['price'] - bal}` מטבעות!", ephemeral=True)
        
        role = i.guild.get_role(item["role_id"])
        if not role:
            return await i.response.send_message("❌ הרול לא נמצא בשרת.", ephemeral=True)
        
        if role in i.user.roles:
            return await i.response.send_message("❌ כבר יש לך את הרול הזה!", ephemeral=True)

        user_balances[i.user.id] -= item["price"]
        await i.user.add_roles(role)
        await i.response.send_message(f"✅ תתחדש! קיבלת את הרול **{item['name']}**!", ephemeral=True)

class ShopBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        self.add_view(ShopView())
        await self.tree.sync()

bot = ShopBot()

# --- פקודות ניהול מטבעות (רק עבורך) ---

@bot.tree.command(name="add_money", description="הוסף מטבעות למשתמש")
async def add_money(i: discord.Interaction, member: discord.Member, amount: int):
    if i.user.id != MY_USER_ID: return await i.response.send_message("🚫 אין לך הרשאה!", ephemeral=True)
    user_balances[member.id] = user_balances.get(member.id, 0) + amount
    await i.response.send_message(f"✅ נוספו `{amount}` מטבעות ל-{member.mention}")

@bot.tree.command(name="remove_money", description="הורד מטבעות למשתמש")
async def remove_money(i: discord.Interaction, member: discord.Member, amount: int):
    if i.user.id != MY_USER_ID: return await i.response.send_message("🚫 אין לך הרשאה!", ephemeral=True)
    current = user_balances.get(member.id, 0)
    user_balances[member.id] = max(0, current - amount)
    await i.response.send_message(f"✅ הוסרו `{amount}` מטבעות מ-{member.mention}")

@bot.tree.command(name="set_money", description="קבע סכום כסף למשתמש")
async def set_money(i: discord.Interaction, member: discord.Member, amount: int):
    if i.user.id != MY_USER_ID: return await i.response.send_message("🚫 אין לך הרשאה!", ephemeral=True)
    user_balances[member.id] = amount
    await i.response.send_message(f"✅ היתרה של {member.mention} עודכנה ל-`{amount}`")

@bot.tree.command(name="balance_user", description="בדוק יתרה של מישהו אחר")
async def balance_user(i: discord.Interaction, member: discord.Member):
    bal = user_balances.get(member.id, 0)
    await i.response.send_message(f"💰 ל-{member.mention} יש `{bal}` מטבעות.")

# --- פקודת הקמת החנות ---

@bot.tree.command(name="setup_shop", description="הקמת חדר החנות המעוצב")
async def setup_shop(i: discord.Interaction):
    if i.user.id != MY_USER_ID: return await i.response.send_message("🚫 פקודה לאונר בלבד!", ephemeral=True)
    
    emb = discord.Embed(
        title="🏪 Cyber-Store | חנות הרולים הרשמית",
        description="כאן תוכלו לקנות רולים יוקרתיים וגישות לצוות השרת!",
        color=0x2b2d31
    )
    
    emb.add_field(name="🎗️ Server-Supporter", value="מחיר: `2,000` מטבעות\n*רול כבוד למשתתפים פעילים.*", inline=False)
    emb.add_field(name="💎 VIP Member", value="מחיר: `5,000` מטבעות\n*גישה לחדרים מיוחדים וצבע בולט.*", inline=False)
    emb.add_field(name="🛠️ Ticket-Staff", value="מחיר: `15,000` מטבעות\n**הרול החשוב ביותר!** מאפשר גישה למערכת הטיקטים.", inline=False)
    
    emb.set_footer(text="Developed by Nehoray 👑 | כל הודעה מזכה ב-10 מטבעות")
    
    await i.channel.send(embed=emb, view=ShopView())
    await i.response.send_message("החנות המעוצבת הוקמה!", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot: return
    user_balances[message.author.id] = user_balances.get(message.author.id, 0) + 10
    await bot.process_commands(message)

bot.run(TOKEN)
