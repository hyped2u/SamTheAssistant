import ctypes  # Yönetici olarak çalıştırma fonksiyonu için
from AppOpener import run as app_open  # Uygulama açma fonksiyonu için
import pywhatkit
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import re
import sys
import os
import asyncio
import pyaudio
import json
import speech_recognition as sr
from groq import Groq
from google.genai import types
import edge_tts
import pygame
import qtawesome as qta
from vosk import Model, KaldiRecognizer

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                             QSystemTrayIcon, QMenu, QAction, QDesktopWidget, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint, QVariantAnimation
from PyQt5.QtGui import QIcon, QFont, QColor, QPainter, QLinearGradient

# --- AYARLAR VE GROQ API ANAHTARI ---
GROQ_API_KEY = "enteryourGROQapihere"

# Groq istemcisini başlat
client = Groq(api_key=GROQ_API_KEY)

pygame.mixer.init()

# --- YARDIMCI FONKSİYONLAR ---
def openadministrator(appName):
    """Windows Shell API kullanarak uygulamayı yönetici izni (UAC) ile başlatır."""
    try:
        # 'runas' parametresi Windows'a yönetici izni sormasını söyler
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", f"/c start {appName}", None, 1)
    except Exception as e:
        print(f"Yönetici olarak başlatılamadı: {e}")
        
def runapp(appName):
    """Verilen isme en yakın uygulamayı Windows'ta bulup açar."""
    try:
        # match_closest=True sayesinde "hesap" desen bile "Hesap Makinesi"ni bulur
        app_open(appName, match_closest=True, throw_error=False)
    except Exception as e:
        print(f"Uygulama açılamadı: {e}")
        
def playmusic(sarki_adi):
    """Verilen şarkı adını YouTube'da aratır ve otomatik oynatır."""
    try:
        # pywhatkit arka planda tarayıcıyı açıp videoyu bulur ve oynatır
        pywhatkit.playonyt(sarki_adi)
    except Exception as e:
        print(f"Müzik açılırken hata oluştu: {e}")

def goodnight():
    """Windows'u uyku moduna alır."""
    # Not: Eğer bilgisayar uyku yerine hazırda bekletmeye (hibernate) geçerse, 
    # cmd'yi yönetici olarak açıp 'powercfg -h off' yazman gerekebilir.
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def changebrightness(percent):
    """Ekran parlaklığını 0 ile 100 arasında ayarlar."""
    try:
        percent = int(percent)
        percent = max(0, min(100, percent)) # 0-100 arası sınırla
        sbc.set_brightness(percent)
    except:
        pass

def changevolume(percent):
    """Sistem sesini 0 ile 100 arasında ayarlar."""
    try:
        percent = int(percent)
        percent = max(0, min(100, percent))
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(percent / 100.0, None)
    except:
        pass

def speak(dosya_yolu):
    pygame.mixer.music.load(dosya_yolu)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()
    if os.path.exists(dosya_yolu):
        os.remove(dosya_yolu)

async def metni_sese_cevir(metin):
    ses_ayari = "tr-TR-EmelNeural" 
    communicate = edge_tts.Communicate(metin, ses_ayari)
    await communicate.save("cevap.mp3")
    speak("cevap.mp3")

def askai(metin):
    try:
        mevcut_hafiza = hafiza_yukle()
        hafiza_metni = "\n".join([f"- {bilgi}" for bilgi in mevcut_hafiza])
        
        sistem_talimati = f"""Sen kısa, öz ve zeki bir bilgisayar asistanısın. Adın Sem. Türkçe konuş.
Kullanıcı hakkında bildiğin bilgiler:
{hafiza_metni}

GÖREVLER VE GİZLİ ETİKETLER (ÇOK ÖNEMLİ):
Senden bazı sistem işlemlerini yapman veya bilgi kaydetmen istenirse, cevabının sonuna gizli etiketler eklemelisin.
1. Bilgi Kaydetme: Eğer kullanıcı bir şeyi hatırlamanı isterse sona [KAYDET: bilgi] ekle.
2. Bilgisayarı Uyutma: Kullanıcı bilgisayarı uyku moduna almanı veya kapatmanı isterse sona [ISLEM:UYKU] ekle.
3. Ekran Parlaklığı: Kullanıcı ekran parlaklığını değiştirmek isterse sona [ISLEM:PARLAKLIK:YUZDE] ekle.
4. Ses percentsi: Kullanıcı sesi açmak/kısmak isterse sona [ISLEM:SES:YUZDE] ekle.
5. Müzik Açma: Kullanıcı belirli bir şarkı veya müzik açmanı isterse sona [ISLEM:MUZIK:şarkı_adı] ekle. (Örn: "Şarkıyı başlatıyorum. [ISLEM:MUZIK:Duman Belki Alışman Lazım]")

Lütfen cevaplarını her zaman çok kısa tut (maksimum 1-2 cümle) ve sadece gereken yerde bu etiketleri kullan.
"""

        # YENİ: Groq API Çağrısı
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Groq üzerindeki en yetenekli ve zeki model
            messages=[
                {"role": "system", "content": sistem_talimati},
                {"role": "user", "content": metin}
            ],
            temperature=0.7,   # Yaratıcılık/Rastgelelik percentsi
            max_tokens=150,    # Asistanın çok uzun cevaplar verip sesi ve API'yi yormaması için sınır
        )
        
        cevap_metni = response.choices[0].message.content

        # 1. Kaydetme Etiketi Kontrolü
        match_kaydet = re.search(r"\[KAYDET:(.*?)\]", cevap_metni)
        if match_kaydet:
            hafiza_kaydet(match_kaydet.group(1).strip())

        # 2. İşlem Etiketleri Kontrolü ve Tetiklenmesi
        if "[ISLEM:UYKU]" in cevap_metni:
            goodnight()
            
        match_parlaklik = re.search(r"\[ISLEM:PARLAKLIK:(\d+)\]", cevap_metni)
        if match_parlaklik:
            changebrightness(match_parlaklik.group(1))
            
        match_ses = re.search(r"\[ISLEM:SES:(\d+)\]", cevap_metni)
        if match_ses:
            changevolume(match_ses.group(1))

        # YENİ EKLENEN KISIM: Müzik Tetikleyicisi
        match_muzik = re.search(r"\[ISLEM:MUZIK:(.*?)\]", cevap_metni)
        if match_muzik:
            sarki_adi = match_muzik.group(1).strip()
            playmusic(sarki_adi)
            
        
            

        # Etiketleri metinden temizle ki asistan bunları okumasın
        cevap_metni = re.sub(r"\[KAYDET:.*?\]", "", cevap_metni)
        cevap_metni = re.sub(r"\[ISLEM:.*?\]", "", cevap_metni)

        return cevap_metni.strip()
    except Exception as e:
        print(f"\n[!] GROQ API HATASI: {e}\n")
        return "Sanırım bağlantımda bir sorun var."
       

def hafiza_yukle():
    """Kayıtlı bilgileri json dosyasından okur."""
    if os.path.exists("hafiza.json"):
        with open("hafiza.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def hafiza_kaydet(yeni_bilgi):
    """Yeni öğrenilen bir bilgiyi json dosyasına kalıcı olarak yazar."""
    hafiza = hafiza_yukle()
    if yeni_bilgi not in hafiza:
        hafiza.append(yeni_bilgi)
        with open("hafiza.json", "w", encoding="utf-8") as f:
            json.dump(hafiza, f, ensure_ascii=False, indent=4)


# --- ARKA PLAN DİNLEME İŞ PARÇACIĞI (THREAD) ---
class AsistanDinleyici(QThread):
    arayuzu_goster = pyqtSignal()
    arayuzu_gizle = pyqtSignal()
    metin_guncelle = pyqtSignal(str)

    def run(self):
        if not os.path.exists("model_en"):
            self.metin_guncelle.emit("HATA: 'model_en' klasörü bulunamadı!")
            return
            
        vosk_model = Model("model_en")
        recognizer = KaldiRecognizer(vosk_model, 16000, '["hey", "sam", "[unk]"]')

        pa = pyaudio.PyAudio()
        audio_stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        audio_stream.start_stream()

        while True:
            data = audio_stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                sonuc = json.loads(recognizer.Result())
                metin = sonuc.get("text", "")
                
                if "hey sam" in metin:
                    audio_stream.stop_stream() 
                    self.arayuzu_goster.emit()
                    self.metin_guncelle.emit("Sam: Seni dinliyorum...")
                    
                    r = sr.Recognizer()
                    with sr.Microphone() as source:
                        try:
                            audio = r.listen(source, timeout=4, phrase_time_limit=8)
                            self.metin_guncelle.emit("Sam: Düşünüyorum...")
                            
                            komut = r.recognize_google(audio, language="tr-TR")
                            
                            if komut:
                                self.metin_guncelle.emit(f"Sen: {komut}")
                                
                                cevap = askai(komut)
                                self.metin_guncelle.emit(f"Sam: {cevap}")
                                asyncio.run(metni_sese_cevir(cevap))
                            
                        except sr.UnknownValueError:
                            self.metin_guncelle.emit("Sam: Ne dediğini anlayamadım.")
                            asyncio.run(metni_sese_cevir("Üzgünüm, anlayamadım."))
                        except sr.RequestError:
                            self.metin_guncelle.emit("Sam: İnternet bağlantısı sorunu.")
                        except Exception as e:
                            print(e)
                    
                    self.arayuzu_gizle.emit()
                    audio_stream.start_stream()

# --- GÖRSEL ARAYÜZ (GUI) - y2k Estetiği & Animasyonlu Version ---

class YansimaEfekti(QWidget):
    def __init__(self, parent, genislik, yukseklik):
        super().__init__(parent)
        self.resize(genislik, yukseklik)
        self.setAttribute(Qt.WA_TransparentForMouseEvents) # Tıklamaları engelle
        self.offset = -150.0

        # Rengi fiziksel olarak değil, matematiksel olarak kaydırıyoruz
        self.animasyon = QVariantAnimation(self)
        self.animasyon.setDuration(2500)
        self.animasyon.setStartValue(-150.0)
        self.animasyon.setEndValue(float(genislik))
        self.animasyon.valueChanged.connect(self.animasyon_guncelle)
        self.animasyon.setLoopCount(-1)
        self.animasyon.start()

    def animasyon_guncelle(self, val):
        self.offset = val
        self.update() # Değer değiştikçe ekranı yeniden çiz

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Gradient'i offset değerine göre sürekli kaydırıyoruz
        grad = QLinearGradient(self.offset, 0, self.offset + 150, 0)
        grad.setColorAt(0.0, QColor(0, 255, 255, 0))
        grad.setColorAt(0.5, QColor(0, 255, 255, 60)) # Parlak Siyan (Cyan)
        grad.setColorAt(1.0, QColor(0, 255, 255, 0))

        painter.setBrush(grad)
        painter.setPen(Qt.NoPen)
        # 25 değeri ana çerçevendeki border-radius ile aynı olmalı
        painter.drawRoundedRect(self.rect(), 25, 25)

class SamAsistanArayuz(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.dinleyici_baslat()

    def initUI(self):
        # 1. TEMEL PENCERE AYARLARI
        # Çerçeveyi kaldır, her zaman üstte tut, araç penceresi yap (görev çubuğunda çıkmaz)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        # Saydam arka plan
        self.setAttribute(Qt.WA_TranslucentBackground) 

        # 2. KONUMLANDIRMA (Animasyon için hazırlık)
        ekran = QDesktopWidget().screenGeometry()
        self.genislik = 800
        self.yukseklik = 120 
        self.final_x = (ekran.width() - self.genislik) // 2
        self.final_y = ekran.height() - self.yukseklik - 80 # Görev çubuğunun biraz üstü
        
        # Pencereyi ekranın altından başlat (Animasyonla yukarı kaydıracağız)
        self.setGeometry(self.final_x, ekran.height(), self.genislik, self.yukseklik)

        # 3. y2k/CYBERPUNK STİLİ (CSS)
        self.ana_cerceve = QFrame(self)
        self.ana_cerceve.setStyleSheet("""
            QFrame {
                background-color: rgba(10, 10, 20, 240); /* Derin siyah/mavi y2k arka planı */
                border-radius: 25px; /* Daha bulbous, y2k tarzı köşeler */
                border: 3px solid #00FFFF; /* Parlak Siyan (Neon Blue) Border */
            }
        """)
        
        # 4. NEON GLOW EFEKTİ (y2k Estetiği)
        glow_efekti = QGraphicsDropShadowEffect(self)
        glow_efekti.setBlurRadius(20) # Parlama yarıçapı
        glow_efekti.setColor(QColor(0, 255, 255, 200)) # Siyan renkli, parlak
        glow_efekti.setOffset(0, 0) # Parlama her yöne eşit
        self.ana_cerceve.setGraphicsEffect(glow_efekti)

        # 5. ETİKET VE YAZI AYARLARI
        self.etiket = QLabel("Sam Hazır...", self.ana_cerceve)
        self.etiket.setFont(QFont("Segoe UI", 16, QFont.Bold)) # Biraz daha büyük, y2k neon hissi için kalın
        self.etiket.setAlignment(Qt.AlignCenter)
        self.etiket.setWordWrap(True) 
        # Yazı rengini de Parlak Siyan yapıyoruz
        self.etiket.setStyleSheet("color: #00FFFF; background-color: transparent; border: none;")
        
        # --- YENİ YANSIMA (SHINE) EFEKTİ ---
        self.yansima_efekti = YansimaEfekti(self.ana_cerceve, self.genislik, self.yukseklik)
        self.yansima_efekti.lower() # Yansımayı arka planın hemen üstüne, yazının altına al
        self.etiket.raise_()        # Yazıyı en üste çıkar
        # ----------------------------------

        # 6. DÜZEN VE YERLEŞİM
        cerceve_layout = QVBoxLayout(self.ana_cerceve)
        cerceve_layout.addWidget(self.etiket)
        
        ana_layout = QVBoxLayout(self)
        ana_layout.addWidget(self.ana_cerceve)
        ana_layout.setContentsMargins(0, 0, 0, 0) # Ana pencereyle çerçeve arasındaki boşluğu sıfırla
        self.setLayout(ana_layout)

        # 7. SİSTEM TEPSİSİ (SYSTEM TRAY)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(qta.icon('mdi.waveform', color='#00BFFF'))
        
        tepsi_menusu = QMenu()
        cikis_aksiyonu = QAction("Sam'i Kapat", self)
        cikis_aksiyonu.triggered.connect(self.kapat)
        tepsi_menusu.addAction(cikis_aksiyonu)
        
        self.tray_icon.setContextMenu(tepsi_menusu)
        self.tray_icon.show()

        # 8. ANİMASYON AYARLARI (Canlılık için)
        # Pencerenin 'geometry' (konum ve boyut) özelliğini animasyonlaştıracağız
        self.animasyon = QPropertyAnimation(self, b"pos")
        self.animasyon.setDuration(400) # Yarım saniyeden kısa, seri ve canlı bir animasyon
        self.animasyon.setEasingCurve(QEasingCurve.OutCirc) # y2k tarzı, OutCirc (Hızlanan) bir akış

    def dinleyici_baslat(self):
        # Arka plan iş parçacığını (Vosk dinleyicisi) kur ve bağla
        self.thread = AsistanDinleyici()
        self.thread.arayuzu_goster.connect(self.goster)
        self.thread.arayuzu_gizle.connect(self.gizle)
        self.thread.metin_guncelle.connect(self.metin_yaz)
        self.thread.start()

    def goster(self):
        """Sam uyandığında arayüzü gösterir ve animasyonu başlatır."""
        self.show()
        # Animasyonun start (ekran altı) ve end (final) konumlarını belirleyip başlat
        self.animasyon.setStartValue(QPoint(self.final_x, QDesktopWidget().screenGeometry().height()))
        self.animasyon.setEndValue(QPoint(self.final_x, self.final_y))
        self.animasyon.start()

    def gizle(self):
        """İşlem bittiğinde arayüzü gizle."""
        self.hide()

    def metin_yaz(self, metin):
        self.etiket.setText(metin)

    def kapat(self):
        self.tray_icon.hide()
        sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) 
    
    asistan = SamAsistanArayuz()
    asistan.hide() 
    
    sys.exit(app.exec_())
