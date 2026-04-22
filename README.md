🤖 SamTheAssistant: Y2K Estetikli Akıllı Masaüstü Asistanı
Sam, Windows işletim sistemi için geliştirilmiş, Groq Llama 3.3 modelinden güç alan, yüksek performanslı ve görsel olarak Cyberpunk/y2k estetiğine sahip bir sesli asistandır. Hem sisteminizi kontrol edebilir hem de sizinle zeki diyaloglar kurabilir.

✨ Öne Çıkan Özellikler
🎙️ Wake Word (Uyandırma Kelimesi): "Hey Sam" komutuyla anında tetiklenir (Vosk ile çevrimdışı dinleme).

🧠 Gelişmiş Yapay Zeka: Groq API üzerinden Llama-3.3-70b modeli ile hızlı ve mantıklı cevaplar.

🌌 Y2K / Cyberpunk Arayüz: Neon siyan (cyan) renkli, parlayan efektli ve animasyonlu modern bir GUI.

📂 Kalıcı Hafıza: Söylediğiniz önemli bilgileri unutmaz, hafiza.json dosyasına kaydeder ve sonraki sohbetlerde hatırlar.

⚙️ Sistem Kontrolü: * Parlaklık ve Ses seviyesini ayarlama.

Bilgisayarı uyku moduna alma.

YouTube üzerinden müzik açma.

🔊 Doğal Ses: edge-tts kullanarak insansı bir Türkçe ses tonuyla konuşur.

🛠️ Teknik Gereksinimler
Projenin çalışması için aşağıdaki ana bileşenlere ihtiyaç vardır:

Python 3.8+

Groq API Anahtarı (Ücretsiz alabilirsiniz)

Vosk Dil Modeli: Proje klasöründe model_en (veya kodda belirttiğiniz isimde) bir klasör bulunmalıdır.

🚀 Kurulum ve Çalıştırma
1. Depoyu Klonlayın
Bash
git clone https://github.com/hyped2u/SamTheAssistant.git
cd SamTheAssistant
2. Bağımlılıkları Yükleyin
Bash
pip install -r requirements.txt
Not: pyaudio kurulumunda sorun yaşarsanız Windows için .whl dosyası ile kurulum yapmanız gerekebilir.

3. API Anahtarını Yapılandırın
main.py dosyası içindeki GROQ_API_KEY değişkenine kendi anahtarınızı yapıştırın:

Python
GROQ_API_KEY = "SİZİN_GROQ_API_ANAHTARINIZ"
4. Vosk Modelini Ekleyin
Vosk Modelleri sayfasından uygun (küçük boyutlu bir model önerilir) modeli indirin, zipten çıkarın ve klasör adını model_en yaparak ana dizine koyun.

5. Başlatın
Bash
python main.py
🎨 Arayüz Detayları
Sam, ekranın altında şık bir bar olarak belirir.

Neon Glow: Siyan renkli dış çerçeve parlaması.

Shine Efekti: Arayüz üzerinde sürekli kayan beyaz bir yansıma efekti.

Sistem Tepsisi: Kapatmak için sağ alttaki waveform ikonuna sağ tıklayıp "Sam'i Kapat" demeniz yeterlidir.

📝 Yol Haritası (Roadmap)
[ ] Daha fazla sistem komutu (Dosya açma, ekran görüntüsü alma).

[ ] Farklı arayüz renk temaları (Kırmızı/Amber).

[ ] Tamamen çevrimdışı çalışabilen yerel bir LLM desteği.

🤝 Katkıda Bulunma
Bu proje geliştirilmeye açıktır. Forklayabilir, hata raporlayabilir veya yeni özellikler ekleyerek Pull Request gönderebilirsiniz.

⚠️ Önemli Hatırlatma
Groq API ücretsiz sürümünde dakikada belirli bir sorgu limiti vardır (yaklaşık 30). Çok hızlı üst üste komut göndermek bağlantı hatalarına yol açabilir.
