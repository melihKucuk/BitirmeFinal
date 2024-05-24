from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from openai import OpenAI
from gtts import gTTS
import speech_recognition as sr
from io import BytesIO
from pydub import AudioSegment

from gtts import gTTS
from io import BytesIO
from fastapi.responses import StreamingResponse

AudioSegment.converter = r"C:\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"


api_key = "APİ KEYİ GİRİNİZ"
client = OpenAI(api_key=api_key)

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"]   # Allow all headers
)
# GPT-3 yanıtını saklamak için geçici değişken
gpt_response_cache = {}

# Serve static files from a specified directory
app.mount("/static", StaticFiles(directory="C:\\Users\\TULPAR\\Desktop\\MulakatPython\\fastapi-ai-example\\StaticFiles\\MulakatAppFrontEnd"), name="static")

class BeslenmeSohbetIstekModeli(BaseModel):
    
    city: str  # Changed 'şehir' to 'city'
    weight: str  # Changed 'kilo' to 'weight'
    height: str  # Changed 'boy' to 'height'
    message: str = None  # Changed 'mesaj' to 'message'

@app.post("/beslenme_sohbeti/")
async def beslenme_sohbeti_yaniti_al(request: BeslenmeSohbetIstekModeli):
    response = createBeslenmeSohbeti(request.weight, request.height, request.city, request.message)
    gpt_response_cache["last_response"] = response ########
    return {"response": response}

def createBeslenmeSohbeti(weight: str, height: str, city: str, message: str):
    prompt = f"""Kullanicilara saglikli besin önerileri sun. Bu öneriler Kullanicinin yasadigi sehire göre Yerel yiyecekler, beslenme aliskanlik ve kültürel
diyetler hakkinda bilgiler içersin. Height: {height}, Weight: {weight}, City: {city}, Question: {message}"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        frequency_penalty=0.2,
        presence_penalty=0.2,
        temperature=0.7,
    )
    return response.choices[0].message.content

@app.post("/speech-to-text/")
async def speech_to_text(file: UploadFile = File(...)):
    try:
        # Dosyayı oku
        audio_bytes = await file.read()
        audio_stream = BytesIO(audio_bytes)

        # Gerekirse sesi WAV formatına dönüştür
        sound = AudioSegment.from_file(audio_stream, format=file.filename.split('.')[-1])
        wav_stream = BytesIO()
        sound.export(wav_stream, format="wav")
        wav_stream.seek(0)  # Stream'i başa sar

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_stream) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language="tr-TR")
            except sr.UnknownValueError:
                raise HTTPException(status_code=400, detail="Sesi anlamadım")
            except sr.RequestError:
                raise HTTPException(status_code=500, detail="Ses tanıma servisi kullanılamıyor")

        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ses metnine dönüştürme başarısız: {str(e)}")

@app.get("/text-to-speech/")
async def text_to_speech():
    try:
        # Cache'deki son yanıtı al
        gpt_response = gpt_response_cache.get("last_response", "")
        if not gpt_response:
            raise HTTPException(status_code=404, detail="GPT-3 yanıtı bulunamadı.")
        
        # Ses dosyasını oluştur
        tts = gTTS(gpt_response, lang="tr")
        
        # Ses dosyasını belleğe yaz
        audio_io = BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        
        # Ses dosyasını döndür
        return StreamingResponse(audio_io, media_type="audio/mpeg", headers={"Content-Disposition": "inline; filename=speech.mp3"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
