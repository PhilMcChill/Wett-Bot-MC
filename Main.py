import discord
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta
import json
import os
import asyncio
import sqlite3
import pytz
import random  # Neu für Zufallsauswahl
from flask import Flask
from threading import Thread

# Flask-Server für Uptime
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ist online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Discord Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

# Globale Variablen
valid_managers = []
bets = {}
season_races = 22
current_race = 1
betted_users = set()

# --------------------------
# NEUE FUNKTIONEN UND BEFEHLE
# --------------------------

@bot.command(name='race')
async def show_current_race(ctx):
    await ctx.send(f"🏎️ Heute ist Rennen **{current_race}** von **{season_races}**!")

@bot.command(name='reminder')
async def show_reminder(ctx):
    count = len(bets)
    await ctx.send(f"📢 Ich werde gezwungen zu berichten, dass das Wettbüro geöffnet ist. Es wurden heute bereits **{count}** Wetten abgegeben.")

def get_random_manager():
    return random.choice(valid_managers) if valid_managers else "kein Manager verfügbar"

@tasks.loop(time=[
    time(18, 30, tzinfo=pytz.timezone('Europe/Berlin')),  # 18:30 Uhr
    time(20, 0, tzinfo=pytz.timezone('Europe/Berlin')),   # 20:00 Uhr
    time(20, 30, tzinfo=pytz.timezone('Europe/Berlin'))   # 20:30 Uhr
])
async def race_reminders():
    channel = bot.get_channel(1338532421322281001)  # DEINE CHANNEL-ID
    if not channel:
        return

    random_manager = get_random_manager()
    current_time = datetime.now(pytz.timezone('Europe/Berlin')).time()

    if current_time.hour == 18 and current_time.minute == 30:
        msg = f"👋 Werte Mitglieder! Heute schon eure Wette abgegeben? Punkte wachsen nicht auf Bäumen! Ich denke **{random_manager}** könnte Glück bringen. Aber ich bin nur ein schlecht programmierter Bot! :)"
    
    elif current_time.hour == 20 and current_time.minute == 0:
        msg = f"🏁 Hallo! In fast einer Stunde startet das Rennen! Hätte ich Finger, würde ich auf **{random_manager}** tippen!"
    
    elif current_time.hour == 20 and current_time.minute == 30:
        msg = f"⏰ Letzter Aufruf! In 15 Minuten mach ich den Laden dicht! Unsicher? Setzt auf **{random_manager}!** :)"

    await channel.send(msg)

# --------------------------
# BESTEHENDER CODE (AKTUALISIERT)
# --------------------------

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user.name} ist online!')
    init_db()
    
    global current_race, valid_managers, bets, betted_users
    current_race = int(load_state('current_race', 1))
    valid_managers = load_state('valid_managers', '').split(',') if load_state('valid_managers') else []
    bets = load_bets()
    betted_users = load_betted_users()

    reminder_task.start()
    race_reminders.start()  # Starte die neuen Erinnerungen

# Hilfe-Befehl aktualisieren
@bot.command(name='hilfe')
async def help_command(ctx):
    help_message = """
    **🎉 Verfügbare Befehle 🎉**

    **Für alle Nutzer:**
    - `!bet [Manager]`: Setze eine Wette auf einen Manager.
    - `!points`: Zeige deine Punkte an.
    - `!scoreboard`: Zeige die Punkte-Tabelle an.
    - `!managers`: Liste alle Manager auf.
    - `!race`: Zeige aktuelles Rennen an.
    - `!hilfe`: Diese Hilfe-Nachricht.

    **Für Admins:**
    - `!setmanagers [Manager1 ...]`: Setze Manager-Liste.
    - `!setwinner [Manager]`: Trage Gewinner ein.
    - `!setrace [Nummer]`: Setze Rennnummer.
    - `!resetseason`: Saison zurücksetzen.
    - `!setpoints [Mitglied] [Punkte]`
    - `!betfor [Mitglied] [Manager]`
    - `!total`: Anzahl Wetten
    - `!list`: Alle Wetten anzeigen
    - `!reminder`: Wettestatus anzeigen
    """
    await ctx.send(help_message)

# ... (Alle anderen vorhandenen Funktionen bleiben UNVERÄNDERT)

# Flask-Server
keep_alive()

# Bot starten
bot.run(os.getenv("TOKEN"))
