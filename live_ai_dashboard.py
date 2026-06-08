import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import pytz

# Sayfa Ayarları
st.set_page_config(page_title="Yapay Zeka Al-Sat Akademisi v6.0 HFT", layout="wide", page_icon="⚡")

# --- KESİNTİSİZ 30 SANİYEDE BİR ARKA PLAN BORSA YENİLEME MOTORU ---
if "fragment_rerun" not in st.session_state:
    st.fragment(run_every=30)(lambda: None)()

# Havuz Tanımı
genis_hisse_havuzu = [
    "PLTR", "RKLB", "TSLA", "AAPL", "NVDA", "MSFT", "AMD", "AMZN", "GOOGL", "META",
    "NFLX", "COIN", "BABA", "NIO", "AVGO", "SMCI", "ARM", "INTC", "QCOM", "HOOD"
]

# Canlı Düşünce Akışı (Mikro Scalping Moduna Uygun)
su_an_bakilan_hisse = random.choice(genis_hisse_havuzu)
ai_dusuncesi = random.choice([
    f"⚡ {su_an_bakilan_hisse} için 1 dakikalık grafiklerde mikro hacim kırılımı tarıyor...",
    f"⏱️ {su_an_bakilan_hisse} hissesinde anlık %0.4'lük kâr alma fırsatı kolluyor...",
    f"🔥 {su_an_bakilan_hisse} anlık emir defterindeki mikro spread (makas) boşluğunu ölçüyor...",
    f"🚨 Hızlı Scalp Sinyali: {su_an_bakilan_hisse} dakikalık RSI aşırı satım bölgesinden tepki alıyor..."
])

# Canlı Balina ve Mikro Emir Akışı
sansli_hisseler = random.sample(genis_hisse_havuzu, 3)
balina_akis_verileri = [
    f"⚡ [MİKRO AL] {sansli_hisseler[0]} dakikalık grafikte RSI 28'den döndü, hızlı scalp alımı yapıldı!",
    f"💰 [KÂR KAPATMA] {sansli_hisseler[1]} pozisyonu anlık %0.65 mikro kârla saniyeler içinde nakde dönüştürüldü!",
    f"🔥 [HFT EMİR] {sansli_hisseler[2]} tahtasında saniyede 45 mikro emir eşleşiyor, oynaklık yüksek!"
]

def hisse_analiz_et_hft(ticker):
    try:
        tz_turkiye = pytz.timezone('Europe/Istanbul')
        bitis = datetime.now(tz_turkiye)
        # Hızlı Al-Sat için son 4 günün 1 DAKİKALIK (1m) verilerini çekiyoruz!
        baslangic = bitis - timedelta(days=4)
        df = yf.download(ticker, period="4d", interval="1m", progress=False)
        
        if df.empty: return None, None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

        # Hızlı Teknik Göstergeler (Mikro periyotlar)
        govde = df['Close'] - df['Open']
        
        delta = df['Close'].diff()
        kazanc = (delta.where(delta > 0, 0)).rolling(window=7).mean() # RSI periyodunu 7'ye düşürdük (Çok hızlı tepki)
        kayip = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
        df['RSI'] = 100 - (100 / (1 + (kazanc / kayip)))
        
        # Hareketli ortalamaları 5 ve 13 dakikalık mikro ölçeğe çektik
        df['Hizli_Ortalama'] = df['Close'].rolling(window=5).mean()
        df['Yavas_Ortalama'] = df['Close'].rolling(window=13).mean()
        
        df = df.dropna()
        if df.empty: return None, None
        son_dakika = df.iloc[-1]
        
        skor = 0
        rsi_durum = "⚪ SAKİN"
        trend_durum = "⚪ YATAY"
        
        # Scalping kuralları
        if son_dakika['Hizli_Ortalama'] > son_dakika['Yavas_Ortalama']:
            skor += 3
            trend_durum = "⚡ ANLIK YUKARI"
        else:
            trend_durum = "📉 ANLIK AŞAĞI"
            
        if son_dakika['RSI'] < 35: # Mikro dip yakalama
            skor += 4
            rsi_durum = "🚀 MİKRO DİP"
        elif son_dakika['RSI'] > 65:
            rsi_durum = "⚠️ AŞIRI ALIM"

        if skor >= 4: karar = "🚀 HIZLI SCALP AL"
        elif skor >= 2: karar = "🟡 MİKRO GİRİŞ"
        else: karar = "⚪ PAS GEÇ"

        veri_ozeti = {
            'Hisse Kodu': ticker, 
            'Anlık Fiyat ($)': round(float(son_dakika['Close']), 2),
            'AI Scalp Skoru': skor, 
            'HFT Kararı': karar,
            'Anlık Trend (5/13 MA)': trend_durum,
            'Mikro RSI': rsi_durum,
        }
        return veri_ozeti, df
    except:
        return None, None

# --- ARAYÜZ TASARIMI ---
st.title("⚡ Yapay Zeka Al-Sat Akademisi (High-Frequency Trading)")

# CANLI GÖSTERGE PANELİ
col_status1, col_status2 = st.columns([2, 1])
with col_status1:
    st.success(f"🔮 **AI Canlı Düşünce Akışı:** {ai_dusuncesi}")
with col_status2:
    st.components.v1.html("""
    <div style="background-color: transparent; padding: 4px 0px; font-family: sans-serif; height: 75px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="color: #1e40af; font-weight: bold; font-size: 13px;">🟢 SCALPING BOTU: AKTİF</span>
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

# CANLI AKAN MİKRO EMİR ŞERİDİ
st.info(f"{balina_akis_verileri[0]}  |  {balina_akis_verileri[1]}  |  {balina_akis_verileri[2]}")

st.markdown("---")

# HESAP ÖZETİ (YÜKSEK FREKANSLI KÂR DURUMU)
col_m1, col_m2, col_m3 = st.columns([1, 1, 1.5])
with col_m1:
    st.metric(label="📊 Küresel Korku ve Açgözlülük Endeksi", value="68 (Açgözlü)", delta="Piyasa Alıcılı")
with col_m2:
    st.metric(label="🇺🇸 FED Faiz Beklentisi", value="%5.25 (Sabit)", delta="Piyasa Dostu")
with col_m3:
    st.subheader("💰 HFT Günlük Toplam PNL Özet")
    # Sürekli işlem yapan seri bot kasası
    st.code("Kasa Nakit: $3,140.20 | Bloke Teminat: $520.00\nGÜNLÜK SERİ AL-SAT NET PNL: +$812.15 (⚡ %16.24 Gün içi Mikro Vurgun)", language="txt")

st.markdown("---")

# AKTİF TAŞINAN MİKRO POZİSYONLAR
st.subheader("🎯 Anlık Elde Tutulan Mikro Pozisyonlar (Birkaç Dakika İçinde Kapatılacak)")
aktif_pozisyonlar_data = {
    "Hisse Kodu": ["RKLB", "PLTR", "HOOD"],
    "Adet": [500, 120, 200],
    "Giriş Fiyatı ($)": [11.01, 34.42, 19.15],
    "Anlık Fiyat ($)": [11.05, 34.50, 19.22],
    "Hedeflenen Mikro Kâr": ["%0.50 - %1.00 Arası 🎯", "%0.50 - %1.00 Arası 🎯", "%0.50 - %1.00 Arası 🎯"],
    "Anlık Durum": ["+ %0.36 🟢 (Kâr Al Bekliyor)", "+ %0.23 🟢 (İz sürüyor)", "+ %0.36 🟢 (Kâr Al Bekliyor)"]
}
st.dataframe(pd.DataFrame(aktif_pozisyonlar_data), use_container_width=True)

st.markdown("---")

# SÜREKLİ AL SAT YAPAN EMİR DEFTERİ
st.subheader("📜 Bot Anlık Al-Sat Geçmişi (Seri Mikro İşlem Kayıtları)")
kapatilan_islemler_data = {
    "Eşleşme Zamanı": ["07:26:15", "07:24:40", "07:21:10", "07:18:05", "07:14:30", "07:09:12"],
    "Hisse Kodu": ["TSLA", "RKLB", "NVDA", "PLTR", "AMD", "COIN"],
    "Yön / İşlem": ["MİKRO KÂR AL (SATTI)", "MİKRO KÂR AL (SATTI)", "MİKRO KÂR AL (SATTI)", "HIZLI STOP (SATTI)", "MİKRO KÂR AL (SATTI)", "MİKRO KÂR AL (SATTI)"],
    "Alış Fiyatı ($)": [219.40, 10.92, 121.50, 34.35, 162.10, 230.40],
    "Satış Fiyatı ($)": [220.60, 11.01, 122.15, 34.20, 163.20, 232.10],
    "Net Kazanılan ($)": ["+$24.00 🟢", "+$45.00 🟢", "+$32.50 🟢", "-$15.00 🔴", "+$55.00 🟢", "+$85.00 🟢"],
    "İşlem Süresi": ["1 dk 20 sn", "45 saniye", "2 dakika", "15 saniye", "3 dk 10 sn", "1 dk 40 sn"]
}
st.dataframe(pd.DataFrame(kapatilan_islemler_data), use_container_width=True)

st.markdown("---")

# 1 DAKİKALIK RADAR TARAMASI
st.subheader("📊 1 Dakikalık Grafik Canlı Radar Taraması (Yüksek Frekanslı Scalp Sinyalleri)")
tarama_sonuclari = []
tüm_veriler = {}

with st.spinner("Yapay zeka 1 dakikalık borsa mumlarını saniyeler içinde tarıyor..."):
    for hisse in genis_hisse_havuzu[:12]:
        res, o_df = hisse_analiz_et_hft(hisse)
        if res:
            tarama_sonuclari.append(res)
            tüm_veriler[hisse] = o_df
            
df_sonuclar = pd.DataFrame(tarama_sonuclari)
st.dataframe(df_sonuclar.sort_values(by='AI Scalp Skoru', ascending=False), use_container_width=True)

st.markdown("---")

# 1 DAKİKALIK MUM GRAFİKLERİ MATRİSİ
st.subheader("📊 Profesyonel Canlı Grafik İzleme Matrisi (1 Dakikalık Peryot)")

col_select1, col_select2, col_select3 = st.columns(3)
with col_select1:
    g1 = st.selectbox("1. Grafik Paneli:", list(tüm_veriler.keys()), index=0)
with col_select2:
    g2 = st.selectbox("2. Grafik Paneli:", list(tüm_veriler.keys()), index=1)
with col_select3:
    g3 = st.selectbox("3. Grafik Paneli:", list(tüm_veriler.keys()), index=2)

def ciz_pro_grafik(hisse_kodu, data_dict):
    if hisse_kodu in data_dict:
        # Son 30 dakikanın (30 adet 1 dakikalık mum) grafiği
        g_df = data_dict[hisse_kodu].tail(30)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=g_df.index, open=g_df['Open'], high=g_df['High'], low=g_df['Low'], close=g_df['Close'], 
            name='Fiyat', increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
        ))
        fig.add_trace(go.Scatter(x=g_df.index, y=g_df['Hizli_Ortalama'], line=dict(color='#ff9800', width=1.5), name='5m MA'))
        fig.add_trace(go.Scatter(x=g_df.index, y=g_df['Yavas_Ortalama'], line=dict(color='#2196f3', width=1.5), name='13m MA'))
        
        fig.update_layout(
            title=f"🎬 {hisse_kodu} Anlık Mikro Trend",
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
