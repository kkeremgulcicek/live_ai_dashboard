import time
import requests
import yfinance as yf
import pandas as pd

# ==========================================
# 🔑 KEREM'İN TELEGRAM BOT BAĞLANTI BİLGİLERİ
# ==========================================
TELEGRAM_TOKEN = "8722465210:AAHP2gU71SNUEO_QtYYIwHLFbGxwdIlCA7w"
TELEGRAM_CHAT_ID = "7046446969"

def telegram_mesaj_gonder(mesaj):
    """Bulunan borsa fırsatlarını Kerem'in telefonuna ileten fonksiyon"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": mesaj, 
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("🚀 Sinyal Kerem'in telefonuna başarıyla fırlatıldı!")
        else:
            print(f"⚠️ Telegram API hatası: {response.text}")
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")

def rsi_hesapla(data, period=14):
    """Teknik analiz için RSI indikatörünü hesaplar"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def piyasayi_tara(hisse_listesi):
    print("\n🔄 Küresel borsalar ve indikatörler taranıyor...")
    
    for sembol in hisse_listesi:
        try:
            # yfinance ile en güncel saatlik verileri çekiyoruz
            ticker = yf.Ticker(sembol)
            df = ticker.history(period="1mo", interval="1h")
            
            if df.empty or len(df) < 15: 
                continue
            
            # RSI hesaplamasını ekliyoruz
            df['RSI'] = rsi_hesapla(df)
            
            son_rsi = df['RSI'].iloc[-1]
            anlik_fiyat = df['Close'].iloc[-1]
            
            print(f"🔍 {sembol} | Fiyat: ${anlik_fiyat:.2f} | RSI: {son_rsi:.2f}")
            
            # 🎯 STRATEJİ KURALI: RSI 30'un altındaysa o hisse aşırı ucuzlamıştır, alım fırsatıdır!
            if son_rsi < 30:
                mesaj = (
                    f"🚨 *KEREM FORCES - YENİ FIRSAT* 🚨\n\n"
                    f"📈 *Hisse:* #{sembol}\n"
                    f"💰 *Anlık Fiyat:* ${anlik_fiyat:.2f}\n"
                    f"📊 *RSI Değeri:* {son_rsi:.2f} (Aşırı Satım / Ucuz)\n\n"
                    f"💡 *Strateji Notu:* Hisse matematiksel olarak dipten dönüş sinyali veriyor. "
                    f"Alım yapmayı veya CALL opsiyonu açmayı değerlendirebilirsin.\n\n"
                    f"🤖 _Son karar senin, emri onaylıyor musun abim?_"
                )
                telegram_mesaj_gonder(mesaj)
                
        except Exception as e:
            print(f"⚠️ {sembol} taranırken teknik hata oluştu: {e}")

if __name__ == "__main__":
    # Kerem'in radarındaki ana hisseler
    takip_listesi = ["PLTR", "RKLB", "TSLA", "NVDA"]
    
    # Test amaçlı: Botun çalıştığını doğrulamak için hemen telefona bir açılış mesajı atalım
    telegram_mesaj_gonder("🔋 *Kerem Sinyal Botu Aktif!* Küresel piyasalar 7/24 takibe alındı. Fırsat yakaladığımda burayı canlandıracağım.")
    
    # Her 5 dakikada bir (300 saniye) borsayı tarayan sonsuz döngü
    while True:
        piyasayi_tara(takip_listesi)
        print("💤 Tarama tamamlandı. Yeni tarama için 5 dakika bekleniyor...")
        time.sleep(300)
