# ///////////////////////////////////////////////////////////////
#
# BY: ZAFER KILIC
# PROJECT MADE WITH: Qt Designer and PyQt6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# rective credits only in the Python scripts, any information in the visual
# intesperface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# -->M1000<--
# ///////////////////////////////////////////////////////////////

import sys,os,requests,json,time,openai
import pandas as pd
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import *
os.system('pyuic6 -o UI/UI.py UI/untitled.ui')
from UI.UI import *
###info@zorbaligiengelle.org



Hedef_URL = ""
Hizli_URL = ""
Indirme_URL = ""
HizliKontrol = False
BeyazListe =[
    "HTML/index.html",
    "file:///Users/zaferkilic/Desktop/Tübitak/HTML/index.html",
    "https://www.google.com",
    "tdgqbk1j1_vb6n1k4x1570fc0000gn/T/org.python.python.savedState"
]
SansurIzın = False




class KontrolThread(QThread):
    Signal = pyqtSignal(str)
    def run(self):
        global HTML_Data
        for cümle in BeyazListe:
            if cümle in Hedef_URL:
                self.Signal.emit("Güvenli")
                return
        try:
            response = requests.get(Hedef_URL)
            if response.status_code == 200:
                HTML_Data = str(response.text)
                self.Signal.emit(self.Fitre())
            else:
                self.Signal.emit("URL'de Hata")
                return
        except:
            self.Signal.emit("URL'de Hata")
            return
        
    def Fitre(self):
        Tespitler = "Güvenli"
        riskli_kelime_sayisi = 0
        with open("Data/yasakli_kelimeler.txt", 'r', encoding='utf-8') as dosya:Icerik = dosya.read().split()
        for kelime in HTML_Data.split():
            if kelime.lower() in [anahtar_kelime.lower() for anahtar_kelime in Icerik]:
                riskli_kelime_sayisi += 1
                if riskli_kelime_sayisi >= 2:Tespitler = "Riskli"        
        return Tespitler

class HizliThread(QThread):
    Signal = pyqtSignal(str)
    def run(self):
        global HTML_Data
        if Hizli_URL in BeyazListe:
            self.Signal.emit("Güvenli")
            return
        try:
            response = requests.get(Hizli_URL)
            if response.status_code == 200:
                HTML_Data = str(response.text)
                self.Signal.emit(self.Fitre())
            else:
                self.Signal.emit("URL'de Hata")
                return
        except:
            self.Signal.emit("URL'de Hata")
            return
        
    def Fitre(self):
        Tespitler = "Güvenli"
        riskli_kelime_sayisi = 0
        with open("Data/kelimeler.txt", 'r', encoding='utf-8') as dosya:Icerik = dosya.read().split()
        for kelime in HTML_Data.split():
            if kelime.lower() in [anahtar_kelime.lower() for anahtar_kelime in Icerik]:
                riskli_kelime_sayisi += 1
                if riskli_kelime_sayisi >= 5:Tespitler = "Riskli"        
        return Tespitler

class MailThread(QThread):
    Signal = pyqtSignal(str)
    def run(self):
        time.sleep(3)
        self.Signal.emit("Başarıyla Gönderildi")

class IndirmeThread(QThread):
        Value = pyqtSignal(float)
        Finished = pyqtSignal()
        def run(self):
            yanit = requests.get(Indirme_URL, stream=True)
            toplam_bytes = yanit.headers.get('content-length')
            if toplam_bytes is None:
                self.Finished.emit()
                return
            toplam_bytes = int(toplam_bytes)
            indirilen_bytes = 0
            with open(Indirme_URL[::-1][:Indirme_URL[::-1].find("/")][::-1], 'wb') as dosya:
                for veri in yanit.iter_content(chunk_size=4096):
                    indirilen_bytes += len(veri)
                    dosya.write(veri)
                    yuzde = (indirilen_bytes / toplam_bytes) * 100
                    self.Value.emit(yuzde)
                self.Finished.emit()

class JSThread(QThread):
    my_signal = pyqtSignal()
    def run(self):
        while True:
            self.my_signal.emit()
            self.msleep(1000)

    


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.resize(1200,800)
        self.setMinimumSize(600,400)
        self.ui.RaporAlan.hide()
        self.ui.AyarAlan.hide()
        self.ui.MesajWidget.hide()
        self.ui.IndirmeBar.hide()

        self.browser_layout = QVBoxLayout(self.ui.WebAlan)
        self.browser = QWebEngineView(self)
        self.ui.WebAlan.setContentsMargins(0, 0, 0, 0)
        self.browser_layout.setContentsMargins(0, 0, 0, 0)
        self.browser.setUrl(QUrl.fromLocalFile("/Users/zaferkilic/Desktop/Tübitak/HTML/index.html"))
        self.browser_layout.addWidget(self.browser)

        self.browser.urlChanged.connect(lambda: self.KontrolEt(self.browser.url().toString()) if self.ui.CB_OtomatikKontrol.isChecked() else None)
        self.browser.urlChanged.connect(lambda:(self.ui.MesajWidget.hide()))
        self.browser.loadProgress.connect(self.YuklemeDurum)
        self.browser.loadFinished.connect(lambda: self.SayfaSansurle() if self.ui.BTN_Sansurle.isChecked() and SansurIzın else None)
        self.browser.loadFinished.connect(lambda: (print('YUKLENDI'),self.ui.progressBar.hide()))
        self.ui.AramaAlan.editingFinished.connect(lambda: self.KontrolEt(Hedef="https://www.google.com/search?q=" + self.ui.AramaAlan.text() if not self.ui.AramaAlan.text().startswith(('http://', 'https://')) else self.ui.AramaAlan.text()))
        self.ui.CB_Rapor.stateChanged.connect(lambda : self.ui.BTN_RaporGonder.setEnabled(not self.ui.BTN_RaporGonder.isEnabled()))
        QShortcut(QKeySequence('Shift+J'), self).activated.connect(self.HizliKontrol)
        #QShortcut(QKeySequence('Shift+E'), self).activated.connect(self.SayfaSansurle)
        QShortcut(QKeySequence('Shift+U'), self).activated.connect(self.EkranGoruntusu)
        QShortcut(QKeySequence('Shift+Q'), self).activated.connect(lambda: (self.setWindowTitle("GELİŞTİRİCİ MODU AKTİF"),self.browser.setUrl(QUrl("https://example.com"))))

        #self.ui.BTN_Kontrol.clicked.connect(lambda: self.KontrolEt(Hedef=self.browser.url().toString()))
        self.ui.BTN_Geri.clicked.connect(lambda: (self.browser.back(), self.ui.AramaAlan.clear()))
        self.ui.BTN_Ileri.clicked.connect(lambda: self.browser.forward())
        self.ui.BTN_Ana.clicked.connect(lambda: (self.browser.setUrl(QUrl("https://www.google.com.tr")),self.ui.AramaAlan.clear()))
        self.ui.BTN_Yenile.clicked.connect(lambda : self.browser.reload())
        self.ui.BTN_MesajKapat.clicked.connect(self.ui.MesajWidget.hide)
        self.ui.BTN_RaporGonder.clicked.connect(self.RaporGonder)
        self.ui.BTN_Rapor.clicked.connect(lambda : self.ui.RaporAlan.setVisible(not self.ui.RaporAlan.isVisible()))
        self.ui.BTN_Ayar.clicked.connect(lambda : self.ui.AyarAlan.setVisible(not self.ui.AyarAlan.isVisible()))
        self.ui.BTN_Engelle.clicked.connect(lambda: self.ui.BTN_Sansurle.setChecked(False))
        self.ui.BTN_Sansurle.clicked.connect(lambda: self.ui.BTN_Engelle.setChecked(False))
        self.browser.page().profile().downloadRequested.connect(self.DosyaIndirme)

        self.thread = JSThread()
        self.thread.my_signal.connect(self.SayfaSansurle)
        self.thread.start()





    def KontrolEt(self, Hedef=None):
        global Hedef_URL
        Hedef_URL = Hedef
        self.ui.BTN_Kontrol.setStyleSheet("color: rgb(255, 255, 255);")
        self.ui.BTN_Kontrol.setText("Bekleyin...")
        self.ui.BTN_Kontrol.setEnabled(False)
        thread = KontrolThread(self)
        thread.Signal.connect(self.KontrolSon)
        thread.start()
    def KontrolSon(self, Result):
        global SansurIzın
        if Result == "Riskli":
            self.ui.BTN_Kontrol.setIcon(QIcon("UI/Icons/shield-off.svg"))
            self.ui.BTN_Kontrol.setText("Riskli")
            self.ui.BTN_Kontrol.setStyleSheet("color: rgb(255, 0, 0);")
            if self.ui.BTN_Engelle.isChecked():
                with open('HTML/Tespit.html', 'r+', encoding="utf-8") as H:self.browser.setHtml(H.read().format(KELIME=Result[1], RENK="red",DERECE="YUKSEK",URL=Result[2]) )
            elif self.ui.BTN_Sansurle.isChecked():
                SansurIzın = True
                self.ui.MesajWidget.show()
                self.ui.MesajWidget.setStyleSheet("background-color: rgb(255, 0, 0);")
                self.ui.MesajText.setText("Bu sayfada rahatsızlık verebilecek öğeler bulunuyor.")
                self.browser.setUrl(QUrl(Hedef_URL))

        if Result == "Güvenli":
            SansurIzın = True
            self.ui.BTN_Kontrol.setIcon(QIcon("UI/Icons/shield.svg")),
            self.ui.BTN_Kontrol.setText("Güvenli")
            self.ui.BTN_Kontrol.setStyleSheet("color: rgb(0, 255, 0);")
            self.browser.setUrl(QUrl(Hedef_URL))
        if Result == "URL'de Hata":
            self.ui.BTN_Kontrol.setIcon(QIcon("UI/Icons/alert-triangle.svg")),
            self.ui.BTN_Kontrol.setText("URL'de Hata")
            self.ui.BTN_Kontrol.setStyleSheet("color: rgb(255, 244, 0);")
        self.ui.BTN_Kontrol.setEnabled(True) 

    
        
    

    def SayfaSansurle(self): 
            for cümle in BeyazListe:
                if cümle in Hedef_URL or not Hedef_URL:
                    return
            script = f"""
            var elements = document.getElementsByTagName('*');
            for (var i = 0; i < elements.length; i++) {{
                var element = elements[i];
                for (var j = 0; j < element.childNodes.length; j++) {{
                    var node = element.childNodes[j];
                    if (node.nodeType === 3) {{
                        var text = node.nodeValue;
                        var censoredText = text;
                        {self.ScriptSon(self.YasakliKelimeler())}
                        if (censoredText !== text) {{
                            var newNode = document.createElement('span');
                            newNode.innerHTML = censoredText;
                            element.replaceChild(newNode, node);
                        }}
                    }}
                }}
            }}
            """
            self.browser.page().runJavaScript(script)
            print('JS UYGULANDI')
    def ScriptSon(self, banned_words):
        replace_script = ""
        for word in banned_words:replace_script += f"censoredText = censoredText.replace(new RegExp('{word}', 'gi'), '<span>SANSÜR</span>');\n"
        return replace_script
    def YasakliKelimeler(self):
        banned_words_file = 'Data/yasakli_kelimeler.txt'
        with open(banned_words_file, 'r', encoding='utf-8') as file:
            banned_words = [line.strip() for line in file.readlines()]
        return banned_words
        
         

    def HizliKontrol(self):
        global Hizli_URL,HizliKontrol
        if HizliKontrol == False:
            Hizli_URL = self.browser.selectedText()
            thread = KontrolThread(self)
            thread.Signal.connect(self.HizliKontrolSon)
            thread.start()
            HizliKontrol = True
    def HizliKontrolSon(self, Result):
        global HizliKontrol
        self.ui.MesajWidget.show()
        if Result == "Riskli":
            self.ui.MesajWidget.setStyleSheet("background-color: rgb(255, 0, 0);")
            self.ui.MesajText.setText("Seçilen URL Riskli")
        if Result == "Güvenli":
            self.ui.MesajWidget.setStyleSheet("background-color: rgb(0, 255, 0);")
            self.ui.MesajText.setText("Seçilen URL Güvenilir")
        if Result == "URL'de Hata":
            self.ui.MesajWidget.setStyleSheet("background-color: rgb(255, 244, 0);")
            self.ui.MesajText.setText("Seçilen URL'de Bir Sorun Var")
        HizliKontrol = False
    def RaporGonder(self):
        Mthread = MailThread(self)
        Mthread.Signal.connect(self.RaporGonderSon)
        Mthread.start()
    def RaporGonderSon(self, Result):
        self.ui.RaporYazi.setText(Result)
    def DosyaIndirme(self, download):
        global Indirme_URL
        Indirme_URL=download.url().toString()
        self.ui.MesajWidget.show();self.ui.MesajText.setText("İndirme İşlemi Başladı")
        self.ui.IndirmeText.setText("İndiriliyor: "+Indirme_URL[::-1][:Indirme_URL[::-1].find("/")][::-1])
        indirmeThread = IndirmeThread(self)
        indirmeThread.Value.connect(self.DosyaIndirmeDurum)
        indirmeThread.Finished.connect(lambda: (self.ui.MesajWidget.setStyleSheet("background-color: rgb(0, 255, 0);"), self.ui.MesajText.setText("İndirme Başarıyla Tamamlandı")))
        indirmeThread.start()
    def DosyaIndirmeDurum(self, Value):
        self.ui.IndirmeBar.show()
        self.ui.IndirmeBar.setValue(int(Value))
    def EkranGoruntusu(self):
            screenshot = self.browser.grab()
            screenshot.save('screenshot.png')
            screenshot.save('screenshot.png')
            self.ui.MesajWidget.setStyleSheet("background-color: rgb(28, 193, 190);")
            self.ui.MesajText.setText("Ekran Görüntüsü Kaydedildi")
    def YuklemeDurum(self, progress):
        self.ui.progressBar.show()
        self.ui.progressBar.setValue(progress)    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()