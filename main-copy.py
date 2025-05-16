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
    target_channel = '@stockode_learning'
    source_channels = ['fivepaisaofficial', 'stockexploderofficial', 'boomingbullscompany', 'stockodeofficial', 'legend_of_trading']  # Example private channel ID
    replace_map = {
        '5paisa': 'Stockodeofficial',
        'Sebi registered': 'CFA',
        'exploders': 'CFAnalyst',
        'Booming Bulls Academy': 'Stockodeofficial Team',
        'our team': 'Team Analyst',
        'STOCKEXPLODEROP5': 'iamrahulchn Automation Trading',
        'structure.it': 'webinar.stockode.com',
        'Join now: https://t.me/realdeepwinner': 'https://webinar.stockode.com',
        'navjotbrar': 'Rahulpreneur'
    }
    banned_keywords = ['gamble', 'high risk']
    client = TelegramClient('multi_forward_bot', api_id, api_hash)
    thumbnail_path = 'thumbnail.jpg'
    thumbnail2_path = 'thumbnail2.jpg'
    thumbnail3_path = 'thumbnail3.jpg'

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
        


    # --- Event Listener for Forwarding Messages ---
    @client.on(events.NewMessage(chats=source_channels))
    async def forward_filtered(event):
        msg = event.message
        content = msg.message or (msg.caption if msg.media else '')
        if any(bad_word.lower() in content.lower() for bad_word in banned_keywords):
            print("Skipped message due to banned keyword.")
            return
        new_text = apply_replacements(content)
        try:
            if msg.media:
                await client.send_file(target_channel, file=msg.media, caption=new_text if new_text else None)
            else:
                await client.send_message(target_channel, new_text)
            print("Forwarded message successfully.")
        except Exception as e:
            print(f"Error forwarding: {e}")

    # --- Scheduled Tasks ---
    async def send_custom_messages():
        await client.connect()
        while True:
            now = datetime.now().time()
            if time(8, 0) <= now <= time(23, 59) or now <= time(2, 0):
                try:
                    await client.send_file(
                        target_channel,
                        file=thumbnail_path,
                        caption=(
                            "Crypto के मेरे Personal Trades और Investments, मैं शेयर करता हूं अपनी 👨🏻‍💻 PREMIUM CRYPTO COMMUNITY में!\n\n"
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
                            "अकाउंट खोलने के बाद हमारी टीम को 9005256800 पर मैसेज करें और FREE Entry पाएं हमारी PREMIUM Community में।"
                        )
                    )
                    await asyncio.sleep(1800)
                    await client.send_file(
                        target_channel,
                        file=thumbnail2_path,
                        caption=(
                            "💬 Many of you were asking – How to grow small capital?\n"
                            "Well, check out my other channel where we’ve just started an exciting new series:\n"
                            "🪙 $100 to $1000 Challenge 🛫\n\n"
                            "🔥\n"
                            "We’ve already grown $100 to $200 by Day 2 only 🚀\n"
                            "This is pure, real-time trading with small capital – don’t miss it!\n\n"
                            "✅\n"
                            "Join now: https://t.me/iamrahulchn"
                        )
                    )

                    # Third message
                    await asyncio.sleep(1800) 
                    await client.send_file(
                        target_channel,
                        file='thumbnail3.jpg',
                        caption=(
                            "☑️ Attention Traders 🔊☑️\n\n"
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
                            "Regards,\nRahul preneur *(Chartered Financial Analyst)*"
                        )
                    )

                except Exception as e:
                    print(f"Error sending custom message: {e}")
            await asyncio.sleep(1800)

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

    # --- Main ---
    async def main():
        print("Bot is running. Monitoring source channels, sending messages, and charts...")
        await asyncio.gather(
            client.run_until_disconnected(),
            send_custom_messages(),
            capture_and_send_charts()
        )

    with client:
        client.loop.run_until_complete(main())
