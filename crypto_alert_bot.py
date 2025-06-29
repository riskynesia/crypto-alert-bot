from telegram.ext import ApplicationBuilder
import requests, asyncio
from datetime import datetime

TOKEN = '7441556247:AAG2qhJWkxKw8CfxRDNZ0yrpaivQggUUMxQ'
CHAT_ID = -1002823301318

harga_sebelumnya = {}
waktu_sebelumnya = {}

def get_all_coin_data_indodax():
    url = "https://indodax.com/api/ticker_all"
    return requests.get(url).json()['tickers']

async def monitor(app):
    await asyncio.sleep(3)
    while True:
        try:
            data = get_all_coin_data_indodax()
            for coin_key, info in data.items():
                if not coin_key.endswith('_idr'):
                    continue  # hanya coin dengan IDR pair

                try:
                    harga = float(info['last'])
                    vol_key = 'vol_' + coin_key.split('_')[0]
                    volume_koin = float(info.get(vol_key, 0))
                    volume_idr = harga * volume_koin

                    prev_harga = harga_sebelumnya.get(coin_key)
                    prev_waktu = waktu_sebelumnya.get(coin_key)

                    if prev_harga:
                        perubahan = ((harga - prev_harga) / prev_harga) * 100
                        arah = "🚀 Pump" if perubahan > 0 else "📉 Dump"
                        durasi = int((datetime.now() - prev_waktu).total_seconds() // 60)

                        if abs(perubahan) >= 5:
                            simbol = coin_key.upper().replace('_IDR', '')
                            msg = f"""
🔥 <b>{simbol}/IDR {arah.upper()} ALERT</b>

📈 <b>Perubahan:</b> {perubahan:+.2f}% dalam {durasi} menit
💰 <b>Harga Saat Ini:</b> Rp {harga:,.0f}
🔄 <b>Volume 24 Jam:</b> Rp {volume_idr / 1_000_000:.2f} Juta
🏦 <b>Sumber:</b> Indodax

📣 <i>Waspadai volatilitas! Lakukan riset sebelum trading.</i>
#CryptoAlert
"""
                            try:
                                await app.bot.send_message(
                                    chat_id=CHAT_ID,
                                    text=msg.strip(),
                                    parse_mode='HTML'
                                )
                            except Exception as e:
                                print(f"[SEND ERROR] {coin_key}: {e}")

                    harga_sebelumnya[coin_key] = harga
                    waktu_sebelumnya[coin_key] = datetime.now()

                except Exception as e:
                    print(f"[COIN ERROR] {coin_key}: {e}")
        except Exception as e:
            print(f"[LOOP ERROR] {e}")

        await asyncio.sleep(60)  # Cek tiap menit

# 🔄 Jalankan bot
app = ApplicationBuilder().token(TOKEN).build()
app.post_init = monitor

print("🚀 Bot sinyal semua coin Indodax aktif...")
app.run_polling()
