import os
import time
from ib_insync import *
# Gerekli kütüphaneyi yüklemek için: pip install ib_insync

# --- 1. GÜVENLİK VE BAĞLANTI AYARLARI ---
# Gerçek hayatta API anahtarları asla koda yazılmaz, bilgisayarın sistem ortamından çekilir.
IB_HOST = os.getenv("IB_HOST", "127.0.0.1")  # TWS veya Gateway bağlantı adresi
IB_PORT = int(os.getenv("IB_PORT", 7497))    # 7497 = TWS Paper (Sanal) Hesap Portu

ib = IB()

def borsaya_baglan():
    try:
        print(f"🔄 Interactive Brokers API bağlantısı kuruluyor... ({IB_HOST}:{IB_PORT})")
        ib.connect(IB_HOST, IB_PORT, clientId=1)
        print("✅ Bağlantı Başarılı! Canlı piyasa emir havuzu aktif.")
    except Exception as e:
        print(f"❌ Bağlantı Hatası! Lütfen TWS veya IB Gateway programının açık olduğundan emin olun. Hata: {e}")

# --- 2. VARLIK TANIMLAMALARI (HİSSE & OPSİYON) ---
def varlik_olustur(sembol, tur="HISSE", vade="", kullanım_fiyati=0, opsiyon_turu="C"):
    if tur == "HISSE":
        # ABD Borsası (NYSE/NASDAQ) için Palantir, Rocket Lab vb.
        return Stock(sembol, 'SMART', 'USD')
    elif tur == "OPSIYON":
        # Örn: PLTR 2026-06-19 vadeli, 35 Strike, CALL Opsiyonu
        return Option(sembol, vade, kullanım_fiyati, opsiyon_turu, 'SMART', 'USD')

# --- 3. GERÇEK YAPAY ZEKA / STRATEJİ MOTORU ---
def piyasayi_analiz_et(hisse_kontrati):
    """
    Şu anki Streamlit kodundaki rastgele %48 ihtimal yerine, 
    buraya gerçek teknik analiz algoritmaları yazılır.
    """
    # Anlık emir defterini ve canlı fiyatı çekiyoruz (Gecikmesiz)
    [ticker] = ib.reqTickers(hisse_kontrati)
    canli_fiyat = ticker.marketPrice()
    
    print(f"👀 Anlık İzleniyor -> {hisse_kontrati.symbol}: ${canli_fiyat}")
    
    # BASİT BİR STRATEJİ ÖRNEĞİ:
    # Gerçek hayatta buraya RSI < 30 ise AL, MACD kesiştiyse SAT gibi matematiksel modeller gelir.
    # Şimdilik sanal hesapta işlem dönebilmesi için bir sinyal simüle edelim:
    import random
    return random.choice(["AL", "SAT", "BEKLE"])

# --- 4. ARACI KURUMA GERÇEK EMİR GÖNDERME KÖPRÜSÜ ---
def emir_gonder(kontrat, islem_turu="BUY", lot_adedi=10):
    """
    Bu fonksiyon çağrıldığı an aracı kurum üzerinden borsaya emir iletilir.
    islem_turu: 'BUY' (Alım) veya 'SELL' (Satım)
    """
    # Piyasa Fiyatından Emir Tipi (Market Order)
    emir = MarketOrder(islem_turu, lot_adedi)
    
    # Emri borsaya fırlat
    ticaret = ib.placeOrder(kontrat, emir)
    
    # Emir durumunu takip et (Gerçek zamanlı)
    ib.sleep(0.5) 
    print(f"📣 Emir Durumu: {ticaret.orderStatus.status}")
    
    if ticaret.orderStatus.status == 'Filled':
        print(f"✅ İŞLEM GERÇEKLEŞTİ: {islem_turu} {lot_adedi} Lot {kontrat.symbol}")
        # Burada oluşan kâr/zarar ve komisyon verilerini CSV dosyana (veri_gecmisi.csv) 
        # yazarak Streamlit paneline anında gönderebilirsin!
    elif ticaret.orderStatus.status in ['Rejected', 'Cancelled']:
        print(f"❌ İPTAL/RED: Emir borsa kuralları veya fiyat kayması nedeniyle gerçekleşmedi.")

# --- MAIN DÖNGÜ (7/24 TARAMA) ---
if __name__ == "__main__":
    borsaya_baglan()
    
    if ib.isConnected():
        # Takip etmek istediğimiz gerçek enstrümanları listeliyoruz
        izleme_listesi = [
            varlik_olustur("PLTR", "HISSE"),
            varlik_olustur("RKLB", "HISSE"),
            # Sadece hisse değil, opsiyon kontratı da ekleyebiliriz:
            # varlik_olustur("PLTR", "OPSIYON", vade="20260619", kullanım_fiyati=35, opsiyon_turu="C")
        ]
        
        try:
            while True:
                for varlik in izleme_listesi:
                    sinyal = piyasayi_analiz_et(varlik)
                    
                    if sinyal == "AL":
                        emir_gonder(varlik, "BUY", lot_adedi=5)
                    elif sinyal == "SAT":
                        emir_gonder(varlik, "SELL", lot_adedi=5)
                        
                    ib.sleep(2) # Borsayı yormamak için 2 saniye bekle
                
                print("--- Tarama Döngüsü Tamamlandı, Yeniden Başlıyor ---")
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("👋 Bot kullanıcı tarafından durduruldu. Bağlantılar kesiliyor.")
            ib.disconnect()
