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
st.set_page_config(page_title="Yapay Zeka HFT Dolar Avcısı & Komisyon Engine", layout="wide", page_icon="⚡")

# --- VERİTABANI MOTORU (SABİT DOSYA SİSTEMİ) ---
DB_FILE = "veri_gecmisi.csv"
KOMISYON_ORANI = 0.50 # İşlem başına kesilen sabit $0.50 aracı kurum ücreti

def verileri_yukle():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if not df.empty:
                kasa = float(df.iloc[0]['Kasa_Nakit'])
                pnl = float(df.iloc[0]['Total_Pnl'])
                adet = int(df.iloc[0]['Islem_Adedi'])
                
                gecmis = []
                for _, row in df.iterrows():
                    gecmis.append({
                        "Zaman": row['Zaman'], "Hisse": row['Hisse'], "Islem": row['Islem'],
                        "Adet": int(row['Adet']), "Alis": float(row['Alis']), "Satis": float(row['Satis']), 
                        "Pnl": float(row['Pnl']), "Komisyon": float(row['Komisyon']) if 'Komisyon' in df.columns else -0.50
                    })
                return kasa, pnl, adet, gecmis
        except:
            pass
    # Başlangıç değerleri
    return 5240.20, 345.10, 42, [
        {"Zaman": "07:28:12", "Hisse": "RKLB", "Islem": "⚡ MİKRO VURGUN", "Adet": 800, "Alis": 11.02, "Satis": 11.09, "Pnl": 55.50, "Komisyon": -0.50},
        {"Zaman": "07:29:45", "Hisse": "PLTR", "Islem": "⚡ MİKRO VURGUN", "Adet": 400, "Alis": 34.20, "Satis": 34.35, "Pnl": 59.50, "Komisyon": -0.50}
    ]

def verileri_kaydet(kasa, pnl, adet, gecmis):
    liste = []
    for isc in gecmis:
        liste.append({
            "Kasa_Nakit": kasa, "Total_Pnl": pnl, "Islem_Adedi": adet,
            "Zaman": isc["Zaman"], "Hisse": isc["Hisse"], "Islem": isc["Islem"],
            "Adet": isc["Adet"], "Alis": isc["Alis"], "Satis": isc["Satis"], "Pnl": isc["Pnl"], "Komisyon": isc["Komisyon"]
        })
    df = pd.DataFrame(liste)
    df.to_csv(DB_FILE, index=False)

# --- İLK AÇILIŞTA HAFIZAYI ÇEK ---
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
st.subheader("💰 Canlı Finansal Portföy Durumu (Komisyon Düşülmüş Net Veriler)")
col_k1, col_k2, col_k3 = st.columns(3)
with col_k1:
    placeholder_kasa = st.empty()
with col_k2:
    placeholder_pnl = st.empty()
with col_k3:
    placeholder_adet = st.empty()

st.markdown("---")

# Tablo Alanı
st.subheader("📜 Bot Anlık Real-Time Al-Sat Geçmişi (Net PNL Dağılımı)")
placeholder_tablo = st.empty()

# --- ARKA PLAN REAL-TIME AKIŞ DÖNGÜSÜ ---
while True:
    tz_tr = pytz.timezone('Europe/Istanbul')
    su_an_saat = datetime.now(tz_tr).strftime("%H:%M:%S")
    
    # 1. Saati Güncelle
    placeholder_saat.markdown(f"""
    <div style="text-align: right; font-family: sans-serif;">
        <span style="color: #22c55e; font-weight: bold; font-size: 13px;">🟢 COMMISSION ENGINE ACTIVE</span><br>
        <span style="color: #1e3a8a; font-size: 20px; font-weight: bold;">{su_an_saat}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. İşlem Simülasyonu (%25 ihtimal)
    if random.random() < 0.25:
        secilen_hisse = random.choice(hisse_havuzu)
        placeholder_ust_not.warning(f"🤖 Bot şu an **{secilen_hisse}** tahtasında komisyon hesaplamalı HFT emri gönderiyor...")
        
        try:
            ticker_data = yf.Ticker(secilen_hisse)
            anlik_gercek_fiyat = float(ticker_data.history(period="1d")['Close'].iloc[-1])
        except:
            baz_fiyatlar = {"PLTR": 34.50, "RKLB": 11.05, "TSLA": 220.30, "NVDA": 122.10, "AMD": 163.40, "AAPL": 181.20}
            anlik_gercek_fiyat = baz_fiyatlar.get(secilen_hisse, 50.0)
            
        islem_sans = random.choices(["KAR", "ZARAR"], weights=[85, 15])[0]
        
        if anlik_gercek_fiyat > 150:
            adet = random.choice([30, 50, 100])
        elif anlik_gercek_fiyat > 50:
            adet = random.choice([100, 150, 200])
        else:
            adet = random.choice([400, 600, 1000])
        
        if islem_sans == "KAR":
            fark_yuzdesi = random.uniform(0.0015, 0.0040)
            alis_fiyat = round(anlik_gercek_fiyat * (1 - fark_yuzdesi), 2)
            satis_fiyat = round(anlik_gercek_fiyat, 2)
            
            # Brüt Kârı hesapla ve KOMİSYONU DÜŞ (-$0.50)
            brut_pnl = (satis_fiyat - alis_fiyat) * adet
            if brut_pnl < 1.50: brut_pnl = random.uniform(2.00, 5.00)
            net_pnl = round(brut_pnl - KOMISYON_ORANI, 2)
            
            st.session_state.kasa_nakit += net_pnl
            st.session_state.total_pnl += net_pnl
            st.session_state.islem_adedi += 1
            
            st.session_state.gecmis_islemler.insert(0, {
                "Zaman": su_an_saat, "Hisse": secilen_hisse, "Islem": "⚡ MİKRO VURGUN", 
                "Adet": adet, "Alis": alis_fiyat, "Satis": satis_fiyat, "Pnl": net_pnl, "Komisyon": -KOMISYON_ORANI
            })
        else:
            fark_yuzdesi = random.uniform(0.0010, 0.0020)
            alis_fiyat = round(anlik_gercek_fiyat, 2)
            satis_fiyat = round(anlik_gercek_fiyat * (1 - fark_yuzdesi), 2)
            
            # Brüt Zararın üzerine BİR DE KOMİSYON YÜKÜ ekle (-$0.50)
            brut_pnl = (satis_fiyat - alis_fiyat) * adet
            if abs(brut_pnl) < 1.00: brut_pnl = -random.uniform(1.00, 2.00)
            net_pnl = round(brut_pnl - KOMISYON_ORANI, 2) # Zarar daha da büyüdü
            
            st.session_state.kasa_nakit += net_pnl
            st.session_state.total_pnl += net_pnl
            st.session_state.islem_adedi += 1
            
            st.session_state.gecmis_islemler.insert(0, {
                "Zaman": su_an_saat, "Hisse": secilen_hisse, "Islem": "🚨 ANLIK STOP", 
                "Adet": adet, "Alis": alis_fiyat, "Satis": satis_fiyat, "Pnl": net_pnl, "Komisyon": -KOMISYON_ORANI
            })
            
        if len(st.session_state.gecmis_islemler) > 15:
            st.session_state.gecmis_islemler.pop()
            
        verileri_kaydet(st.session_state.kasa_nakit, st.session_state.total_pnl, st.session_state.islem_adedi, st.session_state.gecmis_islemler)
    else:
        placeholder_ust_not.info(f"🔍 Yapay zeka likidite havuzlarını tarıyor, emir eşleşmesi bekleniyor...")

    # 3. Metrikleri Güncelle
    placeholder_kasa.metric(label="💵 Mevcut Kullanılabilir Nakit (Net)", value=f"${st.session_state.kasa_nakit:,.2f}")
    placeholder_pnl.metric(label="📈 Net Gerçekleşen Toplam PNL", value=f"${st.session_state.total_pnl:,.2f}", delta="Komisyonlar Düşüldü")
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
            "Kesilen Komisyon ($)": f"-${abs(isc['Komisyon']):.2f}", # İSTEDİĞİN EKSİ KOMİSYON SÜTUNU
            "Net Kâr/Zarar ($)": f"+${isc['Pnl']:,.2f}" if isc['Pnl'] > 0 else f"-${abs(isc['Pnl']):,.2f}"
        })
    
    placeholder_tablo.dataframe(pd.DataFrame(tablo_listesi), use_container_width=True)
    
    time.sleep(1)
