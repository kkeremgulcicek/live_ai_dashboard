import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import random
import pytz
import time
import os

# Sayfa Ayarları
st.set_page_config(page_title="Yapay Zeka HFT Ölümsüz Hafıza Terminali", layout="wide", page_icon="⚡")

# --- VERİTABANI MOTORU (SABİT DOSYA SİSTEMİ) ---
# Sayfa yenilense bile verilerin kaybolmaması için diske yazma/okuma fonksiyonları
DB_FILE = "veri_gecmisi.csv"

def verileri_yukle():
    """Diskteki dosyadan kayıtlı kasa ve işlemleri geri yükler"""
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # Eğer dosya boş değilse son durumu çek
            if not df.empty:
                kasa = float(df.iloc[0]['Kasa_Nakit'])
                pnl = float(df.iloc[0]['Total_Pnl'])
                adet = int(df.iloc[0]['Islem_Adedi'])
                
                # Tablo geçmişini listeye geri çevir
                gecmis = []
                for _, row in df.iterrows():
                    gecmis.append({
                        "Zaman": row['Zaman'], "Hisse": row['Hisse'], "Islem": row['Islem'],
                        "Adet": int(row['Adet']), "Alis": float(row['Alis']), "Satis": float(row['Satis']), "Pnl": float(row['Pnl'])
                    })
                return kasa, pnl, adet, gecmis
        except:
            pass
    # Dosya yoksa veya hata varsa başlangıç değerleri
    return 5240.20, 345.10, 42, [
        {"Zaman": "07:28:12", "Hisse": "RKLB", "Islem": "⚡ SCALP (SATTI)", "Adet": 500, "Alis": 11.02, "Satis": 11.09, "Pnl": 35.00},
        {"Zaman": "07:29:45", "Hisse": "PLTR", "Islem": "⚡ SCALP (SATTI)", "Adet": 200, "Alis": 34.20, "Satis": 34.35, "Pnl": 30.00}
    ]

def verileri_kaydet(kasa, pnl, adet, gecmis):
    """Her yeni işlemde kasayı ve tüm tabloyu diske kalıcı olarak yazar"""
    liste = []
    for isc in gecmis:
        liste.append({
            "Kasa_Nakit": kasa, "Total_Pnl": pnl, "Islem_Adedi": adet,
            "Zaman": isc["Zaman"], "Hisse": isc["Hisse"], "Islem": isc["Islem"],
            "Adet": isc["Adet"], "Alis": isc["Alis"], "Satis": isc["Satis"], "Pnl": isc["Pnl"]
        })
    df = pd.DataFrame(liste)
    df.to_csv(DB_FILE, index=False)

# --- İLK AÇILIŞTA HAFIZAYI VERİTABANINDAN ÇEK ---
if "kasa_nakit" not in st.session_state:
    kasa, pnl, adet, gecmis = verileri_yukle()
    st.session_state.kasa_nakit = kasa
    st.session_state.total_pnl = pnl
    st.session_state.islem_adedi = adet
    st.session_state.gecmis_islemler = gecmis

hisse_havuzu = ["PLTR", "RKLB", "TSLA", "NVDA", "AMD", "AAPL"]

# --- ARAYÜZ TASARIMI ---
st.title("⚡ Yapay Zeka HFT Real-Time Ölümsüz Terminal")

col_status1, col_status2 = st.columns([2, 1])
with col_status1:
    placeholder_ust_not = st.empty()
with col_status2:
    placeholder_saat = st.empty()

st.markdown("---")

# Kasa Göstergeleri
st.subheader("💰 Canlı Finansal Portföy Durumu (Sayfa Yenilense de Sıfırlanmaz 💾)")
col_k1, col_k2, col_k3 = st.columns(3)
with col_k1:
    placeholder_kasa = st.empty()
with col_k2:
    placeholder_pnl = st.empty()
with col_k3:
    placeholder_adet = st.empty()

st.markdown("---")

# Tablo Alanı
st.subheader("📜 Bot Anlık Real-Time Al-Sat Geçmişi")
placeholder_tablo = st.empty()

# --- ARKA PLAN REAL-TIME AKIŞ DÖNGÜSÜ ---
while True:
    tz_tr = pytz.timezone('Europe/Istanbul')
    su_an_saat = datetime.now(tz_tr).strftime("%H:%M:%S")
    
    # 1. Saati Güncelle
    placeholder_saat.markdown(f"""
    <div style="text-align: right; font-family: sans-serif;">
        <span style="color: #22c55e; font-weight: bold; font-size: 13px;">🟢 ÖLÜMSÜZ VERİ TABANI AKTİF</span><br>
        <span style="color: #1e3a8a; font-size: 20px; font-weight: bold;">{su_an_saat}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. İşlem Simülasyonu (%25 ihtimalle tetiklenir)
    if random.random() < 0.25:
        secilen_hisse = random.choice(hisse_havuzu)
        placeholder_ust_not.warning(f"🤖 Bot şu an **{secilen_hisse}** tahtasında mikro spread tarıyor...")
        
        try:
            ticker_data = yf.Ticker(secilen_hisse)
            anlik_gercek_fiyat = float(ticker_data.history(period="1d")['Close'].iloc[-1])
        except:
            baz_fiyatlar = {"PLTR": 34.50, "RKLB": 11.05, "TSLA": 220.30, "NVDA": 122.10, "AMD": 163.40, "AAPL": 181.20}
            anlik_gercek_fiyat = baz_fiyatlar.get(secilen_hisse, 50.0)
            
        islem_sans = random.choices(["KAR", "ZARAR"], weights=[85, 15])[0]
        
        if anlik_gercek_fiyat > 150:
            adet = random.choice([10, 20, 50])
        elif anlik_gercek_fiyat > 50:
            adet = random.choice([50, 100, 150])
        else:
            adet = random.choice([200, 400, 500, 1000])
        
        if islem_sans == "KAR":
            alis_fiyat = round(anlik_gercek_fiyat * random.uniform(0.998, 0.999), 2)
            satis_fiyat = round(anlik_gercek_fiyat, 2)
            net_pnl = round((satis_fiyat - alis_fiyat) * adet, 2)
            
            st.session_state.kasa_nakit += net_pnl
            st.session_state.total_pnl += net_pnl
            st.session_state.islem_adedi += 1
            
            st.session_state.gecmis_islemler.insert(0, {
                "Zaman": su_an_saat, "Hisse": secilen_hisse, "Islem": "⚡ SCALP (SATTI)", 
                "Adet": adet, "Alis": alis_fiyat, "Satis": satis_fiyat, "Pnl": net_pnl
            })
        else:
            alis_fiyat = round(anlik_gercek_fiyat, 2)
            satis_fiyat = round(anlik_gercek_fiyat * random.uniform(0.996, 0.997), 2)
            net_pnl = round((satis_fiyat - alis_fiyat) * adet, 2)
            
            st.session_state.kasa_nakit += net_pnl
            st.session_state.total_pnl += net_pnl
            st.session_state.islem_adedi += 1
            
            st.session_state.gecmis_islemler.insert(0, {
                "Zaman": su_an_saat, "Hisse": secilen_hisse, "Islem": "🚨 STOP (SATTI)", 
                "Adet": adet, "Alis": alis_fiyat, "Satis": satis_fiyat, "Pnl": net_pnl
            })
            
        if len(st.session_state.gecmis_islemler) > 15:
            st.session_state.gecmis_islemler.pop()
            
        # KRİTİK ADIM: Yeni işlem bittiği an diske kaydet (F5'e karşı koruma kalkanı)
        verileri_kaydet(st.session_state.kasa_nakit, st.session_state.total_pnl, st.session_state.islem_adedi, st.session_state.gecmis_islemler)
    else:
        placeholder_ust_not.info(f"🔍 Yapay zeka likidite havuzlarını tarıyor, emir eşleşmesi bekleniyor...")

    # 3. Metrikleri Güncelle
    placeholder_kasa.metric(label="💵 Mevcut Kullanılabilir Nakit", value=f"${st.session_state.kasa_nakit:,.2f}")
    placeholder_pnl.metric(label="📈 Net Gerçekleşen Toplam PNL", value=f"${st.session_state.total_pnl:,.2f}", delta="Hafıza Kilitli 💾")
    placeholder_adet.metric(label="🔄 Toplam Atılan HFT Emri", value=f"{st.session_state.islem_adedi} İşlem")

    # 4. Tabloyu Ekrana Bas
    tablo_listesi = []
    for isc in st.session_state.gecmis_islemler:
        tablo_listesi.append({
            "Eşleşme Zamanı": isc["Zaman"],
            "Hisse Kodu": isc["Hisse"],
            "İşlem Türü": isc["Islem"],
            "İşlem Adedi (Lot)": f"{isc['Adet']} Adet",
            "Alış Fiyatı ($)": isc["Alis"],
            "Satış Fiyatı ($)": isc["Satis"],
            "Net Kâr/Zarar ($)": f"+${isc['Pnl']:,.2f}" if isc['Pnl'] > 0 else f"-${abs(isc['Pnl']):,.2f}"
        })
    
    placeholder_tablo.dataframe(pd.DataFrame(tablo_listesi), use_container_width=True)
    
    time.sleep(1)
