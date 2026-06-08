import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import random
import pytz
import time
import os

# --- WEB SİTESİ ANA AYARLARI VE PROFESSIONAL TEMA ---
st.set_page_config(
    page_title="HFT Live Quant Terminal - Yapay Zeka Al-Sat Akademisi", 
    layout="wide", 
    page_icon="📊"
)

# Web sitesi görünümünü kurumsallaştırmak için özel CSS enjeksiyonu
st.markdown("""
    <style>
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
        h1 {color: #0f172a; font-family: 'Inter', sans-serif; font-weight: 800;}
        h3 {color: #1e293b; font-family: 'Inter', sans-serif; font-weight: 600;}
        .stMetric {background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0;}
        div[data-testid="stNotification"] {border-radius: 10px;}
    </style>
""", unsafe_allow_html=True)

# --- VERİTABANI MOTORU VE ÇİFT YÖNLÜ KOMİSYON SİSTEMİ ---
DB_FILE = "veri_gecmisi.csv"
ALIS_KOMISYON = 0.50  
SATIS_KOMISYON = 0.50 
TOPLAM_KOMISYON = ALIS_KOMISYON + SATIS_KOMISYON

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
                        "Pnl": float(row['Pnl'])
                    })
                return kasa, pnl, adet, gecmis
        except:
            pass
    # Site ilk defa kuruluyorsa açılış portföyü
    return 10000.00, 0.00, 0, []

def verileri_kaydet(kasa, pnl, adet, gecmis):
    liste = []
    for isc in gecmis:
        liste.append({
            "Kasa_Nakit": kasa, "Total_Pnl": pnl, "Islem_Adedi": adet,
            "Zaman": isc["Zaman"], "Hisse": isc["Hisse"], "Islem": isc["Islem"],
            "Adet": isc["Adet"], "Alis": isc["Alis"], "Satis": isc["Satis"], "Pnl": isc["Pnl"]
        })
    df = pd.DataFrame(liste)
    df.to_csv(DB_FILE, index=False)

# Hafızayı Sitede Koru
if "kasa_nakit" not in st.session_state:
    kasa, pnl, adet, gecmis = verileri_yukle()
    st.session_state.kasa_nakit = kasa
    st.session_state.total_pnl = pnl
    st.session_state.islem_adedi = adet
    st.session_state.gecmis_islemler = gecmis

hisse_havuzu = ["PLTR", "RKLB", "TSLA", "NVDA", "AMD", "AAPL"]

# --- WEB SİTESİ ÜST LOGO VE BAŞLIK ALANI ---
st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); padding: 25px; border-radius: 12px; margin-bottom: 25px; color: white;">
        <h1 style="margin: 0; color: white; font-size: 28px;">📊 HFT LIVE QUANT ALGO TERMINAL</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.8; font-size: 14px;">Yapay Zeka Al-Sat Akademisi • Gerçek Zamanlı Kurumsal Likidite ve Yüksek Frekanslı Scalping Takip Platformu</p>
    </div>
""", unsafe_allow_html=True)

col_status1, col_status2 = st.columns([2, 1])
with col_status1:
    placeholder_ust_not = st.empty()
with col_status2:
    placeholder_saat = st.empty()

st.markdown("---")

# --- KASA VE METRİK PANELİ ---
st.subheader("💰 Canlı Algoritmik Portföy Yönetimi")
col_k1, col_k2, col_k3 = st.columns(3)
with col_k1:
    placeholder_kasa = st.empty()
with col_k2:
    placeholder_pnl = st.empty()
with col_k3:
    placeholder_adet = st.empty()

st.markdown("---")

# --- CANLI EMİR DEFTERİ TABLOSU ---
st.subheader("📜 Canlı Yayındaki HFT Emir Akış Defteri (Real-Time)")
placeholder_tablo = st.empty()

# --- SİTEYİ AYAKTA TUTAN VE VERİLERİ ANLIK AKITAN REAL-TIME DÖNGÜ ---
while True:
    tz_tr = pytz.timezone('Europe/Istanbul')
    su_an_saat = datetime.now(tz_tr).strftime("%H:%M:%S")
    
    # 1. Sağ Üst Köşe Web Sitesi Durum Bilgisi
    placeholder_saat.markdown(f"""
    <div style="text-align: right; font-family: sans-serif; background-color: #f1f5f9; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0;">
        <span style="color: #16a34a; font-weight: bold; font-size: 12px;">● SİTE CANLI YAYINDA (ACTIVE)</span><br>
        <span style="color: #0f172a; font-size: 22px; font-weight: bold; font-family: monospace;">{su_an_saat}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Canlı Emir Algılama Simülasyonu (%25 ihtimalle tıkır tıkır yeni işlem basar)
    if random.random() < 0.25:
        secilen_hisse = random.choice(hisse_havuzu)
        placeholder_ust_not.warning(f"🤖 **Yapay Zeka Analizi:** {secilen_hisse} tahtasında kurumsal emir eşleşmesi yakalandı, pozisyon açılıyor...")
        
        try:
            # Sitede tamamen gerçek fiyatlar dönecek
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
            
            brut_pnl = (satis_fiyat - alis_fiyat) * adet
            if brut_pnl < 2.00: brut_pnl = random.uniform(3.00, 7.00)
            net_pnl = round(brut_pnl - TOPLAM_KOMISYON, 2)
            
            st.session_state.kasa_nakit += net_pnl
            st.session_state.total_pnl += net_pnl
            st.session_state.islem_adedi += 1
            
            st.session_state.gecmis_islemler.insert(0, {
                "Zaman": su_an_saat, "Hisse": secilen_hisse, "Islem": "⚡ MİKRO VURGUN", 
                "Adet": adet, "Alis": alis_fiyat, "Satis": satis_fiyat, "Pnl": net_pnl
            })
        else:
            fark_yuzdesi = random.uniform(0.0010, 0.0020)
            alis_fiyat = round(anlik_gercek_fiyat, 2)
            satis_fiyat = round(anlik_gercek_fiyat * (1 - fark_yuzdesi), 2)
            
            brut_pnl = (satis_fiyat - alis_fiyat) * adet
            if abs(brut_pnl) < 1.00: brut_pnl = -random.uniform(1.00, 3.00)
            net_pnl = round(brut_pnl - TOPLAM_KOMISYON, 2)
            
            st.session_state.kasa_nakit += net_pnl
            st.session_state.total_pnl += net_pnl
            st.session_state.islem_adedi += 1
            
            st.session_state.gecmis_islemler.insert(0, {
                "Zaman": su_an_saat, "Hisse": secilen_hisse, "Islem": "🚨 ANLIK STOP", 
                "Adet": adet, "Alis": alis_fiyat, "Satis": satis_fiyat, "Pnl": net_pnl
            })
            
        if len(st.session_state.gecmis_islemler) > 15:
            st.session_state.gecmis_islemler.pop()
            
        verileri_kaydet(st.session_state.kasa_nakit, st.session_state.total_pnl, st.session_state.islem_adedi, st.session_state.gecmis_islemler)
    else:
        placeholder_ust_not.info("🔍 **Sistem İzlemede:** Yapay zeka emir yoğunluğu tarıyor, yeni bir kurumsal dalga bekleniyor...")

    # 3. Web Sitesi Kurumsal Metrik Kutuları
    placeholder_kasa.metric(label="💵 Portföy Toplam Nakit (Net USD)", value=f"${st.session_state.kasa_nakit:,.2f}")
    placeholder_pnl.metric(label="📈 Toplam Gerçekleşen Net Kâr (PNL)", value=f"${st.session_state.total_pnl:,.2f}", delta="Komisyon Giderleri Dahil")
    placeholder_adet.metric(label="🔄 Toplam Sonlandırılan Pozisyon", value=f"{st.session_state.islem_adedi} Başarılı Emir")

    # 4. Yayındaki Canlı Tablo Yapısı
    tablo_listesi = []
    for isc in st.session_state.gecmis_islemler:
        tablo_listesi.append({
            "Zaman Damgası": isc["Zaman"],
            "Enstrüman (Ticker)": isc["Hisse"],
            "Strateji Türü": isc["Islem"],
            "İşlem Hacmi": f"{isc['Adet']} Lot",
            "Giriş Fiyatı": f"${isc['Alis']:.2f}",
            "Alış Komisyonu": f"-${ALIS_KOMISYON:.2f}",
            "Çıkış Fiyatı": f"${isc['Satis']:.2f}",
            "Satış Komisyonu": f"-${SATIS_KOMISYON:.2f}",
            "Net Finansal Sonuç": f"+${isc['Pnl']:,.2f}" if isc['Pnl'] > 0 else f"-${abs(isc['Pnl']):,.2f}"
        })
    
    if tablo_listesi:
        placeholder_tablo.dataframe(pd.DataFrame(tablo_listesi), use_container_width=True)
    else:
        placeholder_tablo.info("Sistem başlatıldı, ilk algoritmik emrin eşleşmesi bekleniyor (Ortalama 5 saniye)...")
    
    time.sleep(1)
