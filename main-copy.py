from telethon import TelegramClient, events
import asyncio
import re
from datetime import datetime, time
from PIL import Image, ImageDraw, ImageFont
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aiohttp import web
import os
import time as t
import pandas as pd

# --- Configuration ---
api_id = '28654273'
api_hash = '3594edc66acff32e0887c418bb46bb65'
bot_token = '8094367127:AAEjB-lKaTWI5kmVZ_Axe2UG56rINSezKVI'
target_channel = '@stockode_learning'
source_channels = ['fivepaisaofficial', 'stockexploderofficial', 'boomingbullscompany', 'stockodeofficial', 'legend_of_trading']
client = TelegramClient('multi_forward_bot', api_id, api_hash).start(bot_token=bot_token)

replace_map = {
    '5paisa': 'Stockode',
    'Sebi registered': 'CFA',
    'Booming Bulls Academy': 'stokcode',
    'our team': 'Team Analyst',
    'structure.it': 'webinar.stockode.com',
    'Join now: https://t.me/realdeepwinner': 'https://webinar.stockode.com',
    'navjotbrar': 'Rahulpreneur'
}
banned_keywords = ['gamble', 'high risk']
thumbnail_path = 'thumbnail.jpg'
thumbnail2_path = 'thumbnail2.jpg'
thumbnail3_path = 'thumbnail3.jpg'

#
bot_token = os.getenv("BOT_TOKEN")
if not bot_token:
    print("Error: BOT_TOKEN environment variable is not set.")
    exit(1)
# helper function web
async def handle(request):
    return web.Response(text="Bot is running")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server running on port {port}")


# Use your custom TradingView shared chart URLs (must be logged in)
nifty_chart_url = "https://www.tradingview.com/chart/?symbol=NSE:NIFTY&interval=15"  # Replace with your NIFTY chart
btc_chart_url = "https://www.tradingview.com/chart/?symbol=BINANCE:BTCUSDT&interval=60"    # Replace with your BTC chart

# --- Functions ---
def apply_replacements(text):
    for old, new in replace_map.items():
        text = re.sub(fr'\b{re.escape(old)}\b', new, text, flags=re.IGNORECASE)
    return text

def capture_chart(url, save_path, overlay_text):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    t.sleep(10)  # wait for the chart to load
    driver.save_screenshot(save_path)
    driver.quit()

    # Load captured screenshot
    image = Image.open(save_path).convert("RGBA")

    # Load watermark logo
    watermark = Image.open("watermark.png").convert("RGBA")  # Make sure watermark.png exists
    wm_width, wm_height = 200, 80  # Resize to desired size
    watermark = watermark.resize((wm_width, wm_height), Image.Resampling.LANCZOS)


    # Reduce watermark opacity
    alpha = watermark.split()[3]
    alpha = alpha.point(lambda p: p * 0.3)  # 0.3 = 30% opacity
    watermark.putalpha(alpha)
    # Position watermark at bottom right
    margin = 30
    x = (image.width - wm_width - margin) // 2
    y = (image.height - wm_height - margin) // 2

    # Paste watermark with transparency
    image.paste(watermark, (x, y), watermark)
    image.save(save_path)

# --- Chart Capture Task ---
async def capture_and_send_charts():
    await client.connect()
    while True:
        now = datetime.now()
        # Nifty chart every 30 min between 9:10 AM to 3:35 PM
        if now.time() >= time(9, 10) and now.time() <= time(15, 35):
            if now.minute % 30 == 10 or now.minute == 35:
                try:
                    capture_chart("https://www.tradingview.com/chart/?symbol=NSE:NIFTY&interval=15", "nifty.png", "Join Now: @stockode_learning")
                    await client.send_file(target_channel, file="nifty.png", caption="📈 NIFTY Chart Update - 15 Min Timeframe")
                except Exception as e:
                    print(f"Error sending Nifty chart: {e}")
                finally:
                    if os.path.exists("nifty.png"):
                        os.remove("nifty.png")

        # Bitcoin chart every 1 hour (24x7)
        if now.minute == 0:
            try:
                capture_chart("https://www.tradingview.com/chart/?symbol=BINANCE:BTCUSDT&interval=60", "btc.png", "Join Now: @stockode_learning")
                await client.send_file(target_channel, file="btc.png", caption="📊 Bitcoin Chart Update - 1 Hour Timeframe")
            except Exception as e:
                print(f"Error sending Bitcoin chart: {e}")
            finally:
                if os.path.exists("btc.png"):
                    os.remove("btc.png")    
        await asyncio.sleep(60)
    

def get_fno_gainers():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.nseindia.com/market-data/top-gainers-losers")
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table")))

        gainers_table = driver.find_element(By.XPATH, "//div[contains(@id, 'gainers')]//table")
        rows = gainers_table.find_elements(By.TAG_NAME, "tr")[1:]
        data = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 5:
                symbol = cols[0].text.strip()
                change_percent = cols[4].text.strip().replace('%', '')
                data.append({'symbol': symbol, 'pChange': change_percent})
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error scraping gainers: {e}")
        return pd.DataFrame()
    finally:
        driver.quit()

# --- Event Listener ---
@client.on(events.NewMessage(chats=source_channels))
async def forward_filtered(event):
    msg = event.message
    content = msg.message or (msg.caption if msg.media else '')
    if any(bad.lower() in content.lower() for bad in banned_keywords):
        print("Blocked message due to banned keyword.")
        return
    new_text = apply_replacements(content)
    try:
        if msg.media:
            await client.send_file(target_channel, file=msg.media, caption=new_text or None)
        else:
            await client.send_message(target_channel, new_text)
    except Exception as e:
        print(f"Forwarding error: {e}")

# --- Scheduled Tasks ---
async def send_custom_messages():
    while True:
        now = datetime.now().time()
        if time(8, 0) <= now <= time(23, 59) or now <= time(2, 0):
            try:
                await client.send_file(target_channel, file=thumbnail_path, caption="Crypto के मेरे Personal Trades और Investments, मैं शेयर करता हूं अपनी 👨🏻‍💻 PREMIUM CRYPTO COMMUNITY में!\n\n"
                        "जुड़ने के लिए मेरे लिंक से DELTA Exchange में अकाउंट खोलें👇\n"
                        "🔗 https://www.delta.exchange/?code=Stockode\n"
                        "Referral Code: HEOWYV\n\n"
                        "🔥 Features:\n"
                        "• सिर्फ 5 मिनट में अकाउंट बनाएं\n"
                        "• 100x तक Leverage\n"
                        "• Instant Deposit & Withdrawal\n"
                        "• सबसे कम Brokerage\n"
                        "• FIU Registered Platform\n"
                        "• 10% Brokerage Discount\n\n"
                        "अकाउंट खोलने के बाद हमारी टीम को 9005256800 पर मैसेज करें और FREE Entry पाएं हमारी PREMIUM Community में।")
                await asyncio.sleep(3600)
                await client.send_file(target_channel, file=thumbnail2_path, caption="💬 Many of you were asking – How to grow small capital?\n"
                        "Well, check out my other channel where we’ve just started an exciting new series:\n"
                        "🪙 $100 to $1000 Challenge 🛫\n\n"
                        "🔥\n"
                        "We’ve already grown $100 to $200 by Day 2 only 🚀\n"
                        "This is pure, real-time trading with small capital – don’t miss it!\n\n"
                        "✅\n"
                        "Join now: https://t.me/iamrahulchn")
                await asyncio.sleep(3600)
                await client.send_file(target_channel, file=thumbnail3_path, caption="☑️ Attention Traders 🔊☑️\n\n"
                        "1. Always Follow Money Management – It protects your capital.\n"
                        "2. Divide Your Capital Wisely.\n" 
                        "3. Avoid Excessive Margin –.\n"
                        "4. Respect Your Stop Loss – It safeguards your capital from significant losses.\n"
                        "5. Don’t Overtrade – Overtrading negatively impacts your psychology and decision-making.\n"
                        "6. Manage Your Risk Properly – For instance, if your capital is ₹1,00,000, your risk per trade should ideally be limited to ₹2,000 (2%).\n"
                        "- Terms & Conditions: https://stockode.com/terms\n"
                        "- Investor Charter: https://stockode.com\n\n"
                        "⚠️ Disclaimer: *Investments in the securities market are subject to market risks. Read all related documents carefully before investing.*\n\n"
                        "Wishing you a successful trading journey!\n\n"
                        "Regards,\nRahul preneur *(Chartered Financial Analyst)*")
            except Exception as e:
                print(f"Custom message error: {e}")
        await asyncio.sleep(3600)

async def capture_and_send_charts():
    while True:
        now = datetime.now()
        try:
            if time(9, 10) <= now.time() <= time(15, 35) and (now.minute % 30 == 10 or now.minute == 35):
                capture_chart(nifty_chart_url, "nifty.png", "Join Now: @stockode_learning")
                await client.send_file(target_channel, file="nifty.png", caption="📈 NIFTY Chart Update - 15 Min TF")
                os.remove("nifty.png")
            if now.minute == 0:
                capture_chart(btc_chart_url, "btc.png", "Join Now: @stockode_learning")
                await client.send_file(target_channel, file="btc.png", caption="📈 Bitcoin Chart Update - 1 Hour TF")
                os.remove("btc.png")
        except Exception as e:
            print(f"Chart capture error: {e}")
        await asyncio.sleep(60)

async def fetch_gainers_periodically():
    while True:
        try:
            gainers = get_fno_gainers()
            if not gainers.empty:
                msg = "🔥 Today's Top F&O Gainers:\n\n" + '\n'.join(
                    f"{row['symbol']}: {row['pChange']}%" for _, row in gainers.iterrows())
                await client.send_message(target_channel, msg)
        except Exception as e:
            print(f"Gainers fetch error: {e}")
        await asyncio.sleep(3600)

# --- Main Runner ---
async def main():
    print("Bot is running...")

    # Start the web server task
    web_task = asyncio.create_task(start_web_server())

    # Run your other bot tasks concurrently
    await asyncio.gather(
        web_task,
        client.run_until_disconnected(),
        send_custom_messages(),
        capture_and_send_charts(),
        fetch_gainers_periodically()
    )


with client:
    client.loop.run_until_complete(main())
