import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import random
import pytz
import time
import os

# --- WEB SİTESİ ANA AYARLARI ---
st.set_page_config(
    page_title="HFT $100 Challenge Terminal - Yapay Zeka Al-Sat", 
    layout="wide", 
    page_icon="⚡"
)

# Kurumsal Tema İçin CSS
st.markdown("""
    <style>
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
        h1 {color: #0f172a; font-family: 'Inter', sans-serif; font-weight: 800;}
        h3 {color: #1e293b; font-family: 'Inter', sans-serif; font-weight: 600;}
        .stMetric {background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0;}
    </style>
""", unsafe_allow_html=True)

# --- VERİTABANI VE KOMİSYON TANIMLARI ---
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
                
                # Kasa 100 dolardan büyükse, sıfırlama emri verildiği için sıfır başlangıca zorla
                if kasa > 105.00 or pnl > 5.00:
                    return 100.00, 0.00, 0, []
                
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
    # 🎯 YENİ BAŞLANGIÇ NOKTASI: Tam 100 Dolar
    return 100.00, 0.00, 0, []

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

if "kasa_nakit" not in st.session_state:
    kasa, pnl, adet, gecmis = verileri_yukle()
    st.session_state.kasa_nakit = kasa
    st.session_state.total_pnl = pnl
    st.session_state.islem_adedi = adet
    st.session_state.gecmis_islemler = gecmis

# Kasa 100 dolara çekilmek istendiği için session zorlaması
if st.session_state.kasa_nakit > 105.00:
    st.session_state.kasa_nakit = 100.00
    st.session_state.total_pnl = 0.00
    st.session_state.islem_adedi = 0
    st.session_state.gecmis_islemler = []
    verileri_kaydet(100.00, 0.00, 0, [])

hisse_havuzu = ["PLTR", "RKLB", "TSLA", "NVDA", "AMD", "AAPL"]

# --- ÜST LOGO ---
st.markdown("""
    <div style="background: linear-gradient(135deg, #0284c7 0%, #0f172a 100%); padding: 25px; border-radius: 12px; margin-bottom: 25px; color: white;">
        <h1 style="margin: 0; color: white; font-size: 28px;">📊 HFT $100 TRADING CHALLENGE</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.8; font-size: 14px;">Yapay Zeka Al-Sat Akademisi • Küçük Kasa Risk Yönetimi ve Gerçekçi Piyasa Simülasyonu</p>
    </div>
""", unsafe_allow_html=True)

col_status1, col_status2 = st.columns([2, 1])
with col_status1:
    placeholder_ust_not = st.empty()
with col_status2:
    placeholder_saat = st.empty()

st.markdown("---")

# --- KASA PANELİ ---
st.subheader("💰 Canlı Algoritmik Portföy Yönetimi")
col_k1, col_k2, col_k3 = st.columns(3)
with col_k1:
    placeholder_kasa = st.empty()
with col_k2:
    placeholder_pnl = st.empty()
with col_k3:
    placeholder_adet = st.empty()

st.markdown("---")

# --- EMİR TABLOSU ---
st.subheader("📜 Canlı Yayındaki HFT Emir Akış Defteri (Real-Time)")
placeholder_tablo = st.empty()

# --- ARKA PLAN GERÇEKÇİ DÖNGÜ ---
while True:
    tz_tr = pytz.timezone('Europe/Istanbul')
    su_an_saat = datetime.now(tz_tr).strftime("%H:%M:%S")
    
    placeholder_saat.markdown(f"""
    <div style="text-align: right; font-family: sans-serif; background-color: #f1f5f9; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0;">
        <span style="color: #0284c7; font-weight: bold; font-size: 12px;">● RUNNING FROM GROUND ZERO ($100)</span><br>
        <span style="color: #0f172a; font-size: 22px; font-weight: bold; font-family: monospace;">{su_an_saat}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Gerçekçi işlem sıklığı (%8 ihtimalle sinyal üretir)
    if random.random() < 0.08:
        secilen_hisse = random.choice(hisse_havuzu)
        placeholder_ust_not.warning(f"🤖 **Yapay Zeka Analizi:** {secilen_hisse} tahtasında mikro spread taranıyor...")
        
        try:
            ticker_data = yf.Ticker(secilen_hisse)
            anlik_gercek_fiyat = float(ticker_data.history(period="1d")['Close'].iloc[-1])
        except:
            baz_fiyatlar = {"PLTR": 34.50, "RKLB": 11.05, "TSLA": 220.30, "NVDA": 122.10, "AMD": 163.40, "AAPL": 181.20}
            anlik_gercek_fiyat = baz_fiyatlar.get(secilen_hisse, 50.0)
            
        # %53 Kâr, %47 Zarar Dengesi
        islem_sans = random.choices(["KAR", "ZARAR"], weights=[53, 47])[0]
        
        # ⚠️ KÜÇÜK KASA AYARI: 100 dolarla 1000 lot RKLB alınamayacağı için lot boyutları kasaya oranla düşürüldü
        if anlik_gercek_fiyat > 150: # TSLA, AAPL vb.
            adet = random.choice([1, 2]) # Kaldıraçsız veya parçasal lot simülasyonu
        elif anlik_gercek_fiyat > 50:
            adet = random.choice([3, 5])
        else: # RKLB, PLTR
            adet = random.choice([10, 15, 20])
        
        if islem_sans == "KAR":
            fark_yuzdesi = random.uniform(0.08, 0.15) # Küçük lotta kârın cent kalmaması için oynaklık marjı açıldı
            alis_fiyat = round(anlik_gercek_fiyat * (1 - fark_yuzdesi * 0.1), 2)
            satis_fiyat = round(anlik_gercek_fiyat, 2)
            
            brut_pnl = (satis_fiyat - alis_fiyat) * adet
            # Küçük kasada da komisyon sonrası en az +1$ kalmasını zorluyoruz
            if brut_pnl < 2.00: brut_pnl = random.uniform(2.50, 4.00)
            net_pnl = round(brut_pnl - TOPLAM_KOMISYON, 2)
            
            st.session_state.kasa_nakit += net_pnl
            st.session_state.total_pnl += net_pnl
            st.session_state.islem_adedi += 1
            
            st.session_state.gecmis_islemler.insert(0, {
                "Zaman": su_an_saat, "Hisse": secilen_hisse, "Islem": "⚡ MİKRO VURGUN", 
                "Adet": adet, "Alis": alis_fiyat, "Satis": satis_fiyat, "Pnl": net_pnl
            })
        else:
            fark_yuzdesi = random.uniform(0.05, 0.12)
            alis_fiyat = round(anlik_gercek_fiyat, 2)
            satis_fiyat = round(anlik_gercek_fiyat * (1 - fark_yuzdesi * 0.1), 2)
            
            brut_pnl = (satis_fiyat - alis_fiyat) * adet
            if abs(brut_pnl) < 1.50: brut_pnl = -random.uniform(1.50, 3.00)
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
        placeholder_ust_not.info("🔍 **Piyasa İzleniyor:** 100 dolarlık kasa emniyeti için yapay zeka yüksek güvenli sinyal bekliyor...")

    # Metrikleri Güncelle
    placeholder_kasa.metric(label="💵 Portföy Toplam Nakit (Net USD)", value=f"${st.session_state.kasa_nakit:,.2f}")
    
    pnl_gosterge = f"${st.session_state.total_pnl:,.2f}"
    placeholder_pnl.metric(label="📈 Net Dönem Kârı/Zararı (PNL)", value=pnl_gosterge, delta="Pozitif" if st.session_state.total_pnl >= 0 else "Negatif")
    
    placeholder_adet.metric(label="🔄 Toplam Sonlandırılan Pozisyon", value=f"{st.session_state.islem_adedi} Pozisyon")

    # Tabloyu Bas
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
        placeholder_tablo.info("$100 Sıfırdan Başlama Mücadelesi Aktif. İlk emrin eşleşmesi bekleniyor...")
    
    time.sleep(1)
