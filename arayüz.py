import streamlit as st
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Gezi Rehberi | Travel Guide", page_icon="🌍", layout="wide")

STRAPI_URL = "https://gezi-rehberne-d.onrender.com"

# --- YARDIMCI FONKSİYONLAR ---

@st.cache_data(ttl=5)
def verileri_getir(dil_kodu):
    """Seçilen dile göre tüm Place verilerini Strapi'den çeker."""
    try:
        url = f"{STRAPI_URL}/api/places"
        
        params = {
            "populate": "*",
            "locale": dil_kodu
        }
            
        cevap = requests.get(url, params=params)
        
        if cevap.status_code == 200:
            return cevap.json().get('data', [])
        return None
    except Exception as e:
        return None


# --- SOL MENÜ (SIDEBAR) KONTROLLERİ ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2060/2060284.png", width=100)
st.sidebar.title("Ayarlar / Settings")

dil_secimi = st.sidebar.radio("Dil / Language", ["Türkçe", "English"])
dil_kodu = "en" if dil_secimi == "English" else "tr"

st.sidebar.divider()

ui = {
    "baslik": "🌍 Yapay Zeka Destekli Gezi Rehberi" if dil_kodu == "tr" else "🌍 AI Powered Travel Guide",
    "alt_baslik": "*Otonom olarak üretilmiş içerikler galerisi*" if dil_kodu == "tr" else "*Gallery of autonomously generated content*",
    "filtre_mekan": "🏛️ Mekan Filtresi" if dil_kodu == "tr" else "🏛️ Place Filter",
    "tum_mekanlar": "Tüm Mekanlar" if dil_kodu == "tr" else "All Places",
    "puan": "Puan" if dil_kodu == "tr" else "Rating",
    "detay_buton": "Detayları Gör" if dil_kodu == "tr" else "View Details",
    "hata": "🚨 Veriler çekilemedi! Strapi sunucusu çalışmıyor olabilir." if dil_kodu == "tr" else "🚨 Data could not be fetched! Strapi server might be down.",
    "bos": "Seçilen filtrede mekan bulunmuyor." if dil_kodu == "tr" else "No places found in this filter."
}


# --- VERİLERİ ÖNDEN ÇEKİYORUZ ---
# Mekan listesini oluşturabilmek için önce tüm veriyi alıyoruz
mekanlar = verileri_getir(dil_kodu)
if mekanlar is None:
    mekanlar_listesi = []
else:
    mekanlar_listesi = mekanlar

# Strapi'deki mevcut mekanların isimlerini dinamik olarak listeliyoruz (Kolezyum, Çin Seddi vb.)
mevcut_mekan_isimleri = []
for m in mekanlar_listesi:
    veri = m.get('attributes', m)
    ad_temp = veri.get('ad', '')
    if ad_temp and isinstance(ad_temp, str):
        mevcut_mekan_isimleri.append(ad_temp.strip())
mevcut_mekan_isimleri = sorted(list(set(mevcut_mekan_isimleri)))

# Sadece Mekan Filtresi Aktif
secilen_mekan = st.sidebar.selectbox(ui["filtre_mekan"], [ui["tum_mekanlar"]] + mevcut_mekan_isimleri)

# Eğer spesifik bir mekan seçildiyse (Örn: Kolezyum), listeyi sadece o mekan kalacak şekilde daraltıyoruz
if secilen_mekan != ui["tum_mekanlar"]:
    mekanlar_listesi = [
        m for m in mekanlar_listesi 
        if m.get('attributes', m).get('ad', '').strip() == secilen_mekan
    ]


# --- ANA EKRAN ---
st.title(ui["baslik"])
st.markdown(ui["alt_baslik"])
st.divider()

if mekanlar is None:
    st.error(ui["hata"])
elif len(mekanlar_listesi) == 0:
    st.warning(ui["bos"])
else:
    kolonlar = st.columns(3)
    
    for index, mekan in enumerate(mekanlar_listesi):
        veri = mekan.get('attributes', mekan)
        
        ad = veri.get('ad', '...')
        aciklama = veri.get('Aciklama', '...')
        puan = veri.get('Puan', 0)
        
        resim_url = "https://via.placeholder.com/400x200?text=Gorsel+Yok"
        kapak_resmi = veri.get('KapakResmi')
        
        if kapak_resmi:
            if isinstance(kapak_resmi, dict) and 'url' in kapak_resmi:
                resim_url = STRAPI_URL + kapak_resmi['url']
            elif isinstance(kapak_resmi, dict) and 'data' in kapak_resmi and kapak_resmi['data']:
                resim_url = STRAPI_URL + kapak_resmi['data']['attributes']['url']

        with kolonlar[index % 3]:
            with st.container(border=True): 
                st.image(resim_url, use_container_width=True)
                st.subheader(ad)
                st.caption(f"⭐ **{ui['puan']}:** {puan} / 5")
                
                if aciklama:
                    kisa_aciklama = aciklama[:150] + "..." if len(aciklama) > 150 else aciklama
                    st.write(kisa_aciklama)
                
                st.button(ui["detay_buton"], key=f"btn_{mekan.get('id', index)}")
