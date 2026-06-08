import os, time
from ib_insync import *
import pandas_ta as ta
import pandas as pd

IB_HOST = os.getenv("IB_HOST", "127.0.0.1")
IB_PORT = int(os.getenv("IB_PORT", 7497))

ib = IB()

def borsaya_baglan():
    try:
        ib.connect(IB_HOST, IB_PORT, clientId=1)
        print("✅ IB bağlantısı kuruldu.")
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")

def varlik_olustur(sembol):
    return Stock(sembol, 'SMART', 'USD')

def piyasayi_analiz_et(kontrat):
    [ticker] = ib.reqTickers(kontrat)
    fiyat = ticker.marketPrice()
    print(f"👀 {kontrat.symbol} canlı fiyat: {fiyat}")

    # Geçmiş veriyi çek
    bars = ib.reqHistoricalData(
        kontrat,
        endDateTime='',
        durationStr='1 D',
        barSizeSetting='5 mins',
        whatToShow='MIDPOINT',
        useRTH=True
    )
    df = util.df(bars)

    # RSI ve MACD hesapla
    df["RSI"] = ta.rsi(df["close"], length=14)
    macd = ta.macd(df["close"])
    df = pd.concat([df, macd], axis=1)

    rsi = df["RSI"].iloc[-1]
    macd_hist = df["MACDh_12_26_9"].iloc[-1]

    if rsi < 30 and macd_hist > 0:
        return "AL"
    elif rsi > 70 and macd_hist < 0:
        return "SAT"
    else:
        return "BEKLE"

def emir_gonder(kontrat, islem_turu="BUY", lot=10):
    emir = MarketOrder(islem_turu, lot)
    ticaret = ib.placeOrder(kontrat, emir)
    ib.sleep(1)
    print(f"📣 Emir Durumu: {ticaret.orderStatus.status}")

if __name__ == "__main__":
    borsaya_baglan()
    if ib.isConnected():
        izleme_listesi = [varlik_olustur("PLTR"), varlik_olustur("RKLB")]
        try:
            while True:
                for varlik in izleme_listesi:
                    sinyal = piyasayi_analiz_et(varlik)
                    if sinyal == "AL":
                        emir_gonder(varlik, "BUY", lot=5)
                    elif sinyal == "SAT":
                        emir_gonder(varlik, "SELL", lot=5)
                time.sleep(10)
        except KeyboardInterrupt:
            print("👋 Bot durduruldu.")
            ib.disconnect()
