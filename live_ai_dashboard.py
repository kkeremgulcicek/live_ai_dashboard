import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import pytz

# Sayfa Ayarları
st.set_page_config(page_title="Yapay Zeka Al-Sat Akademisi Canlı Bot", layout="wide", page_icon="⚡")

# --- KESİNTİSİZ ARKA PLAN YENİLEME MOTORU (30 Saniyede Bir Sayfa Tetiklenir) ---
if "fragment_rerun" not in st.session_state:
    st.fragment(run_every=30)(lambda: None)()

# --- BOTUN HAFIZASI (SAYFA YENİLENSE DE SİLİNMEYEN CANLI KASA) ---
if "kasa_nakit" not in st.session_state:
    st.session_state.kasa_nakit = 2500.0
    st.session_state.total_pnl = 120.50
    st.session_state.islem_adedi = 14
    
    # Başlangıç geçmişi
    st.session_state.gecmis_islemler = [
        {"Zaman": "07:14:30", "Hisse": "TSLA", "Islem": "MİKRO KÂR (SATTI)", "Alis": 219.40, "Satis": 220.60, "Pnl": 24.0},
        {"Zaman": "07:18:05", "Hisse": "RKLB", "Islem": "MİKRO KÂR (SATTI)", "Alis": 10.92, "Satis": 11.01, "Pnl": 45.0},
        {"Zaman": "07:21:10", "Hisse": "PLTR", "Islem": "MİKRO KÂR (SATTI)", "Alis": 34.10, "Satis": 34.50, "Pnl": 40.0}
    ]

# --- SİTE HER YENİLENDİĞİNDE YENİ BİR İŞLEM YAP (HAFIZAYA EKLE) ---
# Bot her 30 saniyede bir tetiklendiğinde rastgele yeni bir al-sat yapar ve kasaya ekler!
tz_tr = pytz.timezone('Europe/Istanbul')
su_an_saat = datetime.now(tz_tr).strftime("%H:%M:%S")

hisse_havuzu = ["PLTR", "RKLB", "TSLA", "NVDA", "AMD", "AAPL", "COIN"]
secilen_hisse = random.choice(hisse_havuzu)

# Rastgele kâr veya ufak zarar simülasyonu (%75 ihtimal kâr, %25 ihtimal ufak zarar)
islem_turu = random.choices(["KAR", "ZARAR"], weights=[75, 25])[0]

if islem_turu == "KAR":
    kazanc = round(random.uniform(15.0, 65.0), 2)
    alis_fiyat = round(random.uniform(10.0, 200.0), 2)
    satis_fiyat = round(alis_fiyat * random.uniform(1.005, 1.02), 2)
    
    st.session_state.kasa_nakit += kazanc
    st.session_state.total_pnl += kazanc
    st.session_state.islem_adedi += 1
    
    # Yeni işlemi listenin en başına ekle
    st.session_state.gecmis_islemler.insert(0, {
        "Zaman": su_an_saat, "Hisse": secilen_hisse, "Islem": "⚡ MİKRO KÂR (SATTI)", 
        "Alis": alis_fiyat, "Satis": satis_fiyat, "Pnl": kazanc
    })
else:
    kayip = round(random.uniform(5.0, 20.0), 2)
    alis_fiyat = round(random.uniform(10.0, 200.0), 2)
    satis_fiyat = round(alis_fiyat * random.uniform(0.99, 0.995), 2)
    
    st.session_state.kasa_nakit -= kayip
    st.session_state.total_pnl -= kayip
    st.session_state.islem_adedi += 1
    
    st.session_state.gecmis_islemler.insert(0, {
        "Zaman": su_an_saat, "Hisse": secilen_hisse, "Islem": "🚨 ANLIK STOP (SATTI)", 
        "Alis": alis_fiyat, "Satis": satis_fiyat, "Pnl": -kayip
    })

# Listeyi maksimum 10 işlemde tut (ekran şişmesin)
if len(st.session_state.gecmis_islemler) > 10:
    st.session_state.gecmis_islemler.pop()

# --- ARAYÜZ TASARIMI (SADECE EN ÖNEMLİLER) ---
st.title("⚡ Yapay Zeka HFT Canlı Scalping Terminali")

# SAAT VE GERİ SAYIM BAR BAR ALANI
col_status1, col_status2 = st.columns([2, 1])
with col_status1:
    st.info(f"🤖 Bot şu an **{secilen_hisse}** tahtasında milisaniyelik emir derinliğini inceliyor...")
with col_status2:
    st.components.v1.html("""
    <div style="background-color: transparent; padding: 4px 0px; font-family: sans-serif; height: 75px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="color: #1e40af; font-weight: bold; font-size: 13px;">🟢 SCALPER: AKTİF</span>
            <span id="clock" style="color: #1e3a8a; font-size: 16px; font-weight: bold;">00:00:00</span>
        </div>
        <div style="font-size: 12px; color: #475569; font-weight: 500; margin-bottom: 4px;">
            🔄 Bir Sonraki Yapay Zeka Emrine Kalan Süre: <span id="countdown" style="color: #dc2626; font-weight: bold;">30</span> saniye
        </div>
        <div style="width: 100%; background-color: #e2e8f0; border-radius: 4px; height: 6px;">
            <div id="bar" style="width: 100%; background-color: #22c55e; height: 6px; border-radius: 4px; transition: width 1s linear;"></div>
        </div>
    </div>
    <script>
        var timeLeft = 30;
        function updateClockAndCounter() {
            var now = new Date();
            var options = { timeZone: 'Europe/Istanbul', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
            var timeString = now.toLocaleTimeString('tr-TR', options);
            document.getElementById('clock').innerHTML = timeString;
            
            document.getElementById('countdown').innerHTML = timeLeft;
            var barWidth = (timeLeft / 30) * 100;
            document.getElementById('bar').style.width = barWidth + '%';
            
            if (timeLeft > 0) {
                timeLeft--;
            }
        }
        setInterval(updateClockAndCounter, 1000);
        updateClockAndCounter();
    </script>
    """, height=85)

st.markdown("---")

# 💰 YAŞAYAN VE DEĞİŞEN CANLI KASA PANELİ
st.subheader("💰 Canlı Finansal Portföy Durumu")
col_k1, col_k2, col_k3 = st.columns(3)
with col_k1:
    st.metric(label="💵 Mevcut Kullanılabilir Nakit", value=f"${st.session_state.kasa_nakit:,.2f}")
with col_k2:
    pnl_renk = "normal" if st.session_state.total_pnl >= 0 else "inverse"
    st.metric(label="📈 Net Gerçekleşen Toplam PNL", value=f"${st.session_state.total_pnl:,.2f}", delta="Canlı Artıyor")
with col_k3:
    st.metric(label="🔄 Toplam Atılan Scalp Emri", value=f"{st.session_state.islem_adedi} İşlem")

st.markdown("---")

# 📜 SÜREKLİ YENİLENEN İŞLEM DEFTERİ
st.subheader("📜 Bot Anlık Al-Sat Geçmişi (Saniye Saniye Canlı Eklenen Kayıtlar)")

# Hafızadaki verileri tabloya döküyoruz
tablo_listesi = []
for isc in st.session_state.gecmis_islemler:
    tablo_listesi.append({
        "Eşleşme Zamanı": isc["Zaman"],
        "Hisse Kodu": isc["Hisse"],
        "İşlem Türü": isc["Islem"],
        "Alış Fiyatı ($)": isc["Alis"],
        "Satış Fiyatı ($)": isc["Satis"],
        "Net Kâr/Zarar ($)": f"+${isc['Pnl']}" if isc['Pnl'] > 0 else f"-${abs(isc['Pnl'])}"
    })

df_canli_gecmis = pd.DataFrame(tablo_listesi)
st.dataframe(df_canli_gecmis, use_container_width=True)
