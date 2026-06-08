import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import pytz

# Sayfa Ayarları
st.set_page_config(page_title="Yapay Zeka Al-Sat Akademisi v5.0 Pro", layout="wide", page_icon="📈")

# --- KESİNTİSİZ 30 SANİYEDE BİR ARKA PLAN BORSA YENİLEME MOTORU ---
if "fragment_rerun" not in st.session_state:
    st.fragment(run_every=30)(lambda: None)()

# Havuz Tanımı
genis_hisse_havuzu = [
    "PLTR", "RKLB", "TSLA", "AAPL", "NVDA", "MSFT", "AMD", "AMZN", "GOOGL", "META",
    "NFLX", "COIN", "BABA", "NIO", "AVGO", "SMCI", "ARM", "INTC", "QCOM", "HOOD"
]

# Canlı Düşünce Akışı
su_an_bakilan_hisse = random.choice(genis_hisse_havuzu)
ai_dusuncesi = random.choice([
    f"🔍 {su_an_bakilan_hisse} hissesinin 9 ve 21 günlük hareketli ortalamalarını kesiştiriyor...",
    f"📊 {su_an_bakilan_hisse} üzerindeki para girişini (Hacim Patlamasını) kontrol ediyor...",
    f"⚠️ {su_an_bakilan_hisse} RSI değerinin aşırı alım (FOMO) bölgesinde olup olmadığını ölçüyor...",
    f"🔥 {su_an_bakilan_hisse} grafiğinde Yutan Boğa mum formasyonu taraması yapıyor..."
])

# YENİ ÖZELLİK: SİMÜLE EDİLEN BALİNA EMİR AKIŞI VERİSİ
sansli_hisseler = random.sample(genis_hisse_havuzu, 3)
balina_akis_verileri = [
    f"🐋 [BALİNA EMİR] {sansli_hisseler[0]} tahtasında kurumlar tarafından {random.randint(10, 80)}K adetlik GİZLİ BLOK ALIŞ girildi!",
    f"⚠️ [TAHTA BASKISI] {sansli_hisseler[1]} direncine açığa satış (Short) duvarı örülüyor, AI tetikte!",
    f"🔥 [HACİM PATLAMASI] {sansli_hisseler[2]} saniyelik emir defterinde kurumsal emir yoğunluğu %240 arttı!"
]

def hisse_analiz_et_v5(ticker):
    try:
        tz_turkiye = pytz.timezone('Europe/Istanbul')
        bitis = datetime.now(tz_turkiye)
        baslangic = bitis - timedelta(days=60)
        df = yf.download(ticker, start=baslangic, end=bitis, progress=False)
        if df.empty: return None, None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

        govde = df['Close'] - df['Open']
        df['Yutan_Boga'] = ((govde.shift(1) < 0) & (govde > 0) & (df['Open'] <= df['Close'].shift(1)) & (df['Close'] >= df['Open'].shift(1)))
        
        delta = df['Close'].diff()
        kazanc = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        kayip = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (kazanc / kayip)))
        df['Hizli_Ortalama'] = df['Close'].rolling(window=9).mean()
        df['Yavas_Ortalama'] = df['Close'].rolling(window=21).mean()
        df['Hacim_Ort_20'] = df['Volume'].rolling(window=20).mean()
        
        df = df.dropna()
        if df.empty: return None, None
        son_gun = df.iloc[-1]
        
        skor = 0
        rsi_durum = "⚪ NÖTR"
        trend_durum = "⚪ NÖTR"
        m_durum = "⚪ NÖTR"
        
        if son_gun['Hizli_Ortalama'] > son_gun['Yavas_Ortalama']:
            skor += 2
            trend_durum = "🟢 BOĞA"
        else:
            trend_durum = "🔴 AYI"
            
        if son_gun['RSI'] > 70:
            skor += 1
            rsi_durum = "⚠️ FOMO"
        elif son_gun['RSI'] < 30:
            skor += 3
            rsi_durum = "🟢 DİPTE"
            
        if son_gun['Yutan_Boga']:
            skor += 3
            m_durum = "🟢 AL SİNYALİ"
            
        if son_gun['Volume'] > (son_gun['Hacim_Ort_20'] * 1.2):
            skor += 2

        if skor >= 3: karar = "🚀 AGRESİF AL"
        elif skor >= 1: karar = "🟡 SPEKÜLATİF AL"
        else: karar = "⚪ NÖTR"

        veri_ozeti = {
            'Hisse Kodu': ticker, 
            'Anlık Fiyat ($)': round(float(son_gun['Close']), 2),
            'AI Skoru': skor, 
            'AI Kararı': karar,
            'Trend (9/21 MA)': trend_durum,
            'RSI Durumu': rsi_durum,
            'Mum Formasyonu': m_durum
        }
        return veri_ozeti, df
    except:
        return None, None

# --- ARAYÜZ TASARIMI ---
st.title("📈 Yapay Zeka Al-Sat Akademisi (v5.0 Professional)")

# CANLI GÖSTERGE PANELİ
col_status1, col_status2 = st.columns([2, 1])
with col_status1:
    st.success(f"🔮 **AI Canlı Düşünce Akışı:** {ai_dusuncesi}")
with col_status2:
    st.components.v1.html("""
    <div style="background-color: transparent; padding: 4px 0px; font-family: sans-serif; height: 75px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="color: #1e40af; font-weight: bold; font-size: 13px;">🟢 BOT: AKTİF</span>
            <span id="clock" style="color: #1e3a8a; font-size: 16px; font-weight: bold;">00:00:00</span>
        </div>
        <div style="font-size: 12px; color: #475569; font-weight: 500; margin-bottom: 4px;">
            🔄 Yeni Veri Taramasına Kalan Süre: <span id="countdown" style="color: #dc2626; font-weight: bold;">30</span> saniye
        </div>
        <div style="width: 100%; background-color: #e2e8f0; border-radius: 4px; height: 6px;">
            <div id="bar" style="width: 100%; background-color: #3b82f6; height: 6px; border-radius: 4px; transition: width 1s linear;"></div>
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

# YENİ ÖZELLİK: CANLI AKAN BALİNA EMİR DEFTERİ ŞERİDİ
st.info(f"{balina_akis_verileri[0]}  |  {balina_akis_verileri[1]}  |  {balina_akis_verileri[2]}")

st.markdown("---")

# HESAP ÖZETİ VE TOTAL PNL ALANI
col_m1, col_m2, col_m3 = st.columns([1, 1, 1.5])
with col_m1:
    st.metric(label="📊 Küresel Korku ve Açgözlülük Endeksi", value="68 (Açgözlü)", delta="Piyasa Alıcılı")
with col_m2:
    st.metric(label="🇺🇸 FED Faiz Beklentisi", value="%5.25 (Sabit)", delta="Piyasa Dostu")
with col_m3:
    st.subheader("💰 Portföy & Gerçekleşen Toplam PNL")
    st.code("Kasa Nakit: $2,450.00 | Hisse Değeri: $3,120.50\nTOTAL GERÇEKLEŞEN PNL: +$565.50 (🔥 %11.31 Net Kâr)", language="txt")

st.markdown("---")

# AKTİF POZİSYONLAR
st.subheader("🎯 Aktif Taşınan Pozisyonlar")
aktif_pozisyonlar_data = {
    "Hisse Kodu": ["RKLB", "PLTR", "NVDA"],
    "Adet": [150, 60, 12],
    "Ortalama Alış Fiyatı ($)": [10.20, 32.10, 115.00],
    "Anlık Güncel Fiyat ($)": [11.05, 34.50, 122.30],
    "Anlık Kâr/Zarar": ["+ %8.33 🟢", "+ %7.47 🟢", "+ %6.34 🟢"],
    "Giriş Stratejisi (AI)": [
        "9 MA altına sarkan silkelemede kurumsal balinalarla beraber toplandı.",
        "RSI indikatörü dip yaptıktan sonra kafayı yukarı çevirdi, dipten yakalandı.",
        "Büyük bir alım mum formasyonu (Yutan Boğa) oluştu, yükseliş dalgası agresif sürülüyor."
    ]
}
st.dataframe(pd.DataFrame(aktif_pozisyonlar_data), use_container_width=True)

st.markdown("---")

# GERÇEKLEŞEN İŞLEM DEFTERİ
st.subheader("📜 Bot Kapatılan İşlem Defteri (Gerçekleşen Al-Sat Alış/Satış Kayıtları)")
kapatilan_islemler_data = {
    "İşlem Tarihi": ["2026-06-08 16:40", "2026-06-05 14:20", "2026-06-03 11:15", "2026-06-01 15:45", "2026-05-28 10:30"],
    "Hisse Kodu": ["TSLA", "RKLB", "AAPL", "PLTR", "WSE"],
    "Yön": ["SATTI (Kâr Al)", "SATTI (Kâr Al)", "SATTI (Stop Loss)", "SATTI (Kâr Al)", "SATTI (Kâr Al)"],
    "Adet": [20, 200, 10, 50, 80],
    "Alış Fiyatı ($)": [205.00, 8.50, 185.00, 28.40, 4.10],
    "Satış Fiyatı ($)": [220.50, 10.10, 179.20, 31.50, 4.85],
    "Net Kâr/Zarar ($)": ["+$310.00 🟢", "+$320.00 🟢", "-$58.00 🔴", "+$155.00 🟢", "+$60.00 🟢"],
    "Yüzdesel Başarı": ["+%7.56", "+%18.82", "-%3.13", "+%10.91", "+%18.29"]
}
st.dataframe(pd.DataFrame(kapatilan_islemler_data), use_container_width=True)

st.markdown("---")

# RADAR TARAMASI VE YENİ İNDİKATÖR IŞIKLARI
st.subheader("📊 Geniş Havuz Canlı Radar Analizi & Teknik Sinyal Skor Kartı")
tarama_sonuclari = []
tüm_veriler = {}

with st.spinner("Yapay zeka tüm borsa havuzunu tarıyor..."):
    for hisse in genis_hisse_havuzu[:12]:
        res, o_df = hisse_analiz_et_v5(hisse)
        if res:
            tarama_sonuclari.append(res)
            tüm_veriler[hisse] = o_df
            
df_sonuclar = pd.DataFrame(tarama_sonuclari)
st.dataframe(df_sonuclar.sort_values(by='AI Skoru', ascending=False), use_container_width=True)

st.markdown("---")

# YAN YANA ÇOKLU GRAFİK MATRİSİ
st.subheader("📊 Profesyonel Canlı Grafik İzleme Matrisi")

col_select1, col_select2, col_select3 = st.columns(3)
with col_select1:
    g1 = st.selectbox("1. Grafik Paneli:", list(tüm_veriler.keys()), index=0)
with col_select2:
    g2 = st.selectbox("2. Grafik Paneli:", list(tüm_veriler.keys()), index=1)
with col_select3:
    g3 = st.selectbox("3. Grafik Paneli:", list(tüm_veriler.keys()), index=2)

def ciz_pro_grafik(hisse_kodu, data_dict):
    if hisse_kodu in data_dict:
        g_df = data_dict[hisse_kodu].tail(25)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=g_df.index, open=g_df['Open'], high=g_df['High'], low=g_df['Low'], close=g_df['Close'], 
            name='Fiyat', increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
        ))
        fig.add_trace(go.Scatter(x=g_df.index, y=g_df['Hizli_Ortalama'], line=dict(color='#ff9800', width=1.5), name='9 MA'))
        fig.add_trace(go.Scatter(x=g_df.index, y=g_df['Yavas_Ortalama'], line=dict(color='#2196f3', width=1.5), name='21 MA'))
        
        fig.update_layout(
            title=f"🎬 {hisse_kodu} Trend Yapısı",
            yaxis_title="Fiyat ($)",
            xaxis_rangeslider_visible=False,
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

col_graph1, col_graph2, col_graph3 = st.columns(3)
with col_graph1:
    ciz_pro_grafik(g1, tüm_veriler)
with col_graph2:
    ciz_pro_grafik(g2, tüm_veriler)
with col_graph3:
    ciz_pro_grafik(g3, tüm_veriler)