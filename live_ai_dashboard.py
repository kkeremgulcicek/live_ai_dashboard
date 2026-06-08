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
    page_title="Kantitatif Terminal", 
    layout="wide", 
    page_icon="📊"
)

# --- TRANSPARAN SİTE CSS ENJEKSİYONU ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 4.5rem !important; 
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        
        div[data-testid="stMetric"] {
            background-color: transparent !important; 
            border: 1px solid rgba(148, 163, 184, 0.15) !important; 
            border-radius: 8px !important;
            padding: 12px !important;
            box-shadow: none !important;
        }
        
        button, .stButton>button {
            background-color: transparent !important;
            color: #64748b !important;
            border: 1px solid rgba(148, 163, 184, 0.2) !important;
            border-radius: 6px !important;
            transition: all 0.3s ease;
        }
        button:hover {
            border-color: #0284c7 !important;
            color: #0284c7 !important;
        }

        div[data-testid="stNotification"] {
            background-color: transparent !important;
            border: 1px solid rgba(148, 163, 184, 0.15) !important;
            color: #475569 !important;
        }
        
        hr {margin-top: 1rem !important; margin-bottom: 1rem !important; opacity: 0.1;}
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
                
                if kasa > 120.00 or pnl > 20.00:
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

# --- GENİŞLETİLMİŞ KÜRESEL HAVUZLAR ---
bist_havuzu = ["THYAO", "EREGL", "TUPRS", "ASELS"]
us_havuzu = ["PLTR", "RKLB", "TSLA", "NVDA"]

# --- ÜST AKTİVİTE VE ZAMAN SATIRI ---
col_status1, col_status2 = st.columns([3, 1])
with col_status1:
    placeholder_ust_not = st.empty()
with col_status2:
    placeholder_saat = st.empty()

st.markdown("---")

# --- MİNİMAL KASA PANELİ ---
col_k1, col_k2, col_k3 = st.columns(3)
with col_k1:
    placeholder_kasa = st.empty()
with col_k2:
    placeholder_pnl = st.empty()
with col_k3:
    placeholder_adet = st.empty()

st.markdown("---")

# --- EMİR TABLO ALANI ---
placeholder_tablo = st.empty()

# --- ARKA PLAN GERÇEKÇİ DÖNGÜ ---
while True:
    tz_tr = pytz.timezone('Europe/Istanbul')
    su_an_saat = datetime.now(tz_tr).strftime("%H:%M:%S")
    
    placeholder_saat.markdown(f"""
    <div style="text-align: right; font-family: monospace; color: #64748b; font-size: 16px; font-weight: bold; padding-top: 5px;">
        [SİSTEM_SAATİ: {su_an_saat}]
    </div>
    """, unsafe_allow_html=True)
    
    if random.random() < 0.10: # Tarama hızı pürüzsüz akış için optimize edildi
        
        # 🎯 PAZAR VE VARLIK TÜRÜ SEÇİMİ (Eşit Dağılım)
        # %35 TR Hisse, %35 ABD Hisse, %30 Opsiyon Fırsatı
        pazar_secimi = random.choices(["BIST", "US_EQUITY", "OPSIYON"], weights=[35, 35, 30])[0]
        
        if pazar_secimi == "BIST":
            secilen_hisse = random.choice(bist_havuzu)
            anlik_gercek_fiyat = random.uniform(50.0, 300.0) # BIST simüle baz fiyat
            strateji_adi = "⚡ BIST AL (LONG)"
        elif pazar_secimi == "US_EQUITY":
            secilen_hisse = random.choice(us_havuzu)
            try:
                ticker_data = yf.Ticker(secilen_hisse)
                anlik_gercek_fiyat = float(ticker_data.history(period="1d")['Close'].iloc[-1])
            except:
                baz_fiyatlar = {"PLTR": 34.50, "RKLB": 11.05, "TSLA": 220.30, "NVDA": 122.10}
                anlik_gercek_fiyat = baz_fiyatlar.get(secilen_hisse, 50.0)
            strateji_adi = "⚡ US AL (LONG)"
        else: # OPSIYON
            secilen_hisse = random.choice(us_havuzu)
            anlik_gercek_fiyat = random.uniform(5.0, 25.0) # Opsiyon prim baz fiyatı
            strateji_adi = f"📦 {random.choice(['CALL (ALIM)', 'PUT (SATIM)'])}"
            
        # Gerçekçi Borsa Kuralları (%48 Başarı, %40 Stop, %12 İptaller/Hatalar)
        islem_sans = random.choices(
            ["KAR", "ZARAR", "REJECTED", "TIMEOUT", "SLIPPAGE_CANCEL"], 
            weights=[48, 40, 4, 4, 4]
        )[0]
        
        # 100 Dolarlık Kasa İçin Hacim Limitlemesi (Lot Kontrolü)
        if anlik_gercek_fiyat > 150:
            adet = random.choice([1, 2])
        elif anlik_gercek_fiyat > 50:
            adet = random.choice([3, 5])
        else:
            adet = random.choice([10, 15, 20])
            
        if islem_sans == "KAR":
            fark_yuzdesi = random.uniform(0.08, 0.15)
            alis_fiyat = round(anlik_gercek_fiyat * (1 - fark_yuzdesi * 0.1), 2)
            satis_fiyat = round(anlik_gercek_fiyat, 2)
            
            brut_pnl = (satis_fiyat - alis_fiyat) * adet
            if brut_pnl < 2.00: brut_pnl = random.uniform(2.50, 4.00)
            
            # Opsiyonlarda kaldıraç çarpanı
            if pazar_secimi == "OPSIYON":
                brut_pnl = brut_pnl * random.uniform(1.2, 1.5)
                
            net_pnl = round(brut_pnl - TOPLAM_KOMISYON, 2)
            
            st.session_state.kasa_nakit += net_pnl
            st.session_state.total_pnl += net_pnl
            st.session_state.islem_adedi += 1
            
            placeholder_ust_not.warning(f"🔍 Fırsat: {secilen_hisse} {strateji_adi} pozisyonu başarıyla kapatıldı.")
            
            st.session_state.gecmis_islemler.insert(0, {
                "Zaman": su_an_saat, "Hisse": secilen_hisse, "Islem": strateji_adi, 
                "Adet": adet, "Alis": alis_fiyat, "Satis": satis_fiyat, "Pnl": net_pnl
            })
            
        elif islem_sans == "ZARAR":
            fark_yuzdesi = random.uniform(0.05, 0.12)
            alis_fiyat = round(anlik_gercek_fiyat, 2)
            satis_fiyat = round(anlik_gercek_fiyat * (1 - fark_yuzdesi * 0.1), 2)
            
            brut_pnl = (satis_fiyat - alis_fiyat) * adet
            if abs(brut_pnl) < 1.50: brut_pnl = -random.uniform(1.50, 3.00)
            
            if pazar_secimi == "OPSIYON":
                brut_pnl = brut_pnl * random.uniform(1.1, 1.4)
                
            net_pnl = round(brut_pnl - TOPLAM_KOMISYON, 2)
            
            st.session_state.kasa_nakit += net_pnl
            st.session_state.total_pnl += net_pnl
            st.session_state.islem_adedi += 1
            
            risk_etiketi = "🚨 BIST STOP" if pazar_secimi == "BIST" else ("🚨 US STOP" if pazar_secimi == "US_EQUITY" else "🚨 OPS_STOP")
            placeholder_ust_not.warning(f"🔍 Risk: {secilen_hisse} piyasası döndü, {risk_etiketi} tetiklendi.")
            
            st.session_state.gecmis_islemler.insert(0, {
                "Zaman": su_an_saat, "Hisse": secilen_hisse, "Islem": risk_etiketi, 
                "Adet": adet, "Alis": alis_fiyat, "Satis": satis_fiyat, "Pnl": net_pnl
            })
            
        # Hata ve İptal Durumları (Kurallara Bağlı)
        elif islem_sans == "REJECTED":
            placeholder_ust_not.error(f"🚨 Emir Reddedildi: {secilen_hisse} pazar limit engeline takıldı.")
            st.session_state.gecmis_islemler.insert(0, {
                "Zaman": su_an_saat, "Hisse": secilen_hisse, "Islem": "🚨 REDDEDİLDİ", 
                "Adet": 0, "Alis": 0.0, "Satis": 0.0, "Pnl": 0.0
            })
            
        elif islem_sans == "TIMEOUT":
            placeholder_ust_not.error(f"⚠️ Zaman Aşımı: {secilen_hisse} emir defterinde alıcı bulunamadı.")
            st.session_state.gecmis_islemler.insert(0, {
                "Zaman": su_an_saat, "Hisse": secilen_hisse, "Islem": "⚠️ ZAMANAŞIMI", 
                "Adet": 0, "Alis": 0.0, "Satis": 0.0, "Pnl": 0.0
            })
            
        elif islem_sans == "SLIPPAGE_CANCEL":
            placeholder_ust_not.error(f"❌ Fiyat Kayması: {secilen_hisse} ani derinlik kaybı, işlem iptal edildi.")
            st.session_state.gecmis_islemler.insert(0, {
                "Zaman": su_an_saat, "Hisse": secilen_hisse, "Islem": "❌ KAYMA_İPTAL", 
                "Adet": 0, "Alis": 0.0, "Satis": 0.0, "Pnl": 0.0
            })
            
        if len(st.session_state.gecmis_islemler) > 15:
            st.session_state.gecmis_islemler.pop()
            
        verileri_kaydet(st.session_state.kasa_nakit, st.session_state.total_pnl, st.session_state.islem_adedi, st.session_state.gecmis_islemler)
    else:
        placeholder_ust_not.info("⚙️ Beklemede: Algoritma küresel pazarları (BIST, US, Opsiyon) çapraz tarıyor...")

    # Metrikler
    placeholder_kasa.metric(label="TOPLAM BAKİYE (USD)", value=f"${st.session_state.kasa_nakit:,.2f}")
    placeholder_pnl.metric(label="NET KÂR / ZARAR (PNL)", value=f"${st.session_state.total_pnl:,.2f}", delta="▲" if st.session_state.total_pnl >= 0 else "▼")
    placeholder_adet.metric(label="TOPLAM POZİSYON", value=f"{st.session_state.islem_adedi} İşlem")

    # Tablo Güncelleme
    tablo_listesi = []
    for isc in st.session_state.gecmis_islemler:
        kom_goster = f"-${ALIS_KOMISYON:.2f}" if isc["Adet"] > 0 else "$0.00"
        pnl_yazi = "$0.00"
        if isc["Pnl"] > 0:
            pnl_yazi = f"+${isc['Pnl']:,.2f}"
        elif isc["Pnl"] < 0:
            pnl_yazi = f"-${abs(isc['Pnl']):,.2f}"

        tablo_listesi.append({
            "SAAT": isc["Zaman"],
            "ENSTRÜMAN": isc["Hisse"],
            "İŞLEM TÜRÜ": isc["Islem"],
            "HACİM": f"{isc['Adet']} Lot" if isc["Adet"] > 0 else "0 Lot",
            "GİRİŞ FİYATI": f"${isc['Alis']:.2f}" if isc["Alis"] > 0 else "$0.00",
            "KOMİSYON (ALIM)": kom_goster,
            "ÇIKIS FİYATI": f"${isc['Satis']:.2f}" if isc["Satis"] > 0 else "$0.00",
            "KOMİSYON (SATIM)": kom_goster,
            "NET SONUÇ": pnl_yazi
        })
    
    if tablo_listesi:
        placeholder_tablo.dataframe(pd.DataFrame(tablo_listesi), use_container_width=True)
    else:
        placeholder_tablo.info("Küresel finansal ağlardan emir akışı bekleniyor...")
    
    time.sleep(1)
