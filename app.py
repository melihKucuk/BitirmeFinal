import streamlit as st
import requests
from io import BytesIO

st.title('Beslenme Sohbet Servisi')

backend_url = "http://localhost:8000"

# Speech-to-text input
st.header("Ses Yükle")
audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])
if audio_file is not None:
    audio_bytes = audio_file.read()
    files = {"file": (audio_file.name, audio_bytes, audio_file.type)}
    try:
        response = requests.post(f'{backend_url}/speech-to-text/', files=files)
        response.raise_for_status()  # Raise an exception for HTTP errors
        st.write("Text:", response.json()["text"])
    except requests.exceptions.HTTPError as errh:
        st.error(f"HTTP Hatası: {errh}")
        st.error(f"Hata Mesajı: {response.text}")
    except requests.exceptions.ConnectionError as errc:
        st.error(f"Bağlantı Hatası: {errc}")
    except requests.exceptions.Timeout as errt:
        st.error(f"Zaman Aşımı Hatası: {errt}")
    except requests.exceptions.RequestException as err:
        st.error(f"Bir hata oluştu: {err}")

# Text-to-speech input
st.header("Sesli Yanıt Al")
if st.button("Convert to Speech"):
    try:
        response = requests.get(f'{backend_url}/text-to-speech/')
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.status_code == 200:
            audio_data = BytesIO(response.content)
            st.audio(audio_data, format="audio/mpeg")
        else:
            st.error(f"Yanıt alınamadı, HTTP durum kodu: {response.status_code}")
    except requests.exceptions.RequestException as err:
        st.error(f"Bir hata oluştu: {err}")

# Beslenme Sohbet Formu
st.header("Beslenme Sohbeti")
with st.form(key='nutrition_form'):
    weight = st.text_input("Kilo (kg)")  # 'kilo' yerine 'weight'
    height = st.text_input("Boy (cm)")   # 'boy' yerine 'height'
    city = st.text_input("Şehir")        # 'sehir' yerine 'city'
    message = st.text_area("Mesajınız")  # 'mesaj' yerine 'message'
    submit_button = st.form_submit_button(label='Gönder')

if submit_button:
    if not (weight and height and city):
        st.error("Lütfen tüm zorunlu alanları doldurunuz.")
    else:
        data = {
            'weight': weight,
            'height': height,
            'city': city,
            'message': message
        }
        try:
            response = requests.post(f'{backend_url}/beslenme_sohbeti/', json=data)
            response.raise_for_status()  # Raise an exception for HTTP errors
            if response.status_code == 200:
                st.success("Beslenme Danışmanı: " + response.json()['response'])
            else:
                st.error(f"Yanıt alınamadı, HTTP durum kodu: {response.status_code}")
                if response.status_code == 422:
                    st.json(response.json())  # Hata detaylarını göster
        except requests.exceptions.RequestException as err:
            st.error(f"Bir hata oluştu: {err}")
