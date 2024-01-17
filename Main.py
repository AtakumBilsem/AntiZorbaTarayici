# ///////////////////////////////////////////////////////////////
#
# BY: ATAKUM BİLSEM
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
# ///////////////////////////////////////////////////////////////

import sys,os,requests,json,time
from bs4 import BeautifulSoup
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import *
os.system('pyuic6 -o UI/UI.py UI/untitled.ui')
from UI.UI import *
    
from transformers import AutoTokenizer, TextClassificationPipeline, TFBertForSequenceClassification
from nltk.tokenize import word_tokenize
tokenizer = AutoTokenizer.from_pretrained("nanelimon/bert-base-turkish-bullying")
model = TFBertForSequenceClassification.from_pretrained("nanelimon/bert-base-turkish-bullying", from_pt=True)
pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer)


SEBEP = None
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

BULUNAN = []
YASAKLI = []

with open("Data/yasakli_kelimeler.txt", 'r') as dosya:
    for satir in dosya:
        YASAKLI.append(satir.strip())




class KontrolThread(QThread):
    Signal = pyqtSignal(str)
    def run(self):
        BULUNAN.clear()
        global HTML_Data
        for cümle in BeyazListe:
            if cümle in Hedef_URL:
                self.Signal.emit("Güvenli")
                return
        response = requests.get(Hedef_URL)
        if response.status_code == 200:
            HTML_Data = response.text
            self.Ayıkla()
            self.Signal.emit(self.Algoritma())
        else:
            self.Signal.emit("Hata")
            return
    def Ayıkla(self):
        try:
            soup = BeautifulSoup(HTML_Data, 'html.parser')
            for baslik in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                if not BULUNAN == BULUNAN:
                    BULUNAN.extend(baslik.get_text().split())
            for metin in soup.find_all('p'):
                if not BULUNAN == BULUNAN:
                    BULUNAN.extend(metin.get_text().split())
        except:
            pass
    def Algoritma(self):
        SEBEP = ""
        for KELIME in BULUNAN:
            if not KELIME in YASAKLI:
                result = pipe(KELIME)[0]
                if not result['label'] == "Nötr" and result['score'] >= 0.992:
                    if KELIME not in YASAKLI:
                        SEBEP = result['label']
                        YASAKLI.append(KELIME)
        if len(YASAKLI) >= 2:
            return 'Riskli'

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
class LoopThread(QThread):
    my_signal = pyqtSignal()
    def run(self):
        while True:
            self.my_signal.emit()
            self.msleep(1500)



class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.SHOWBOX = True
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Anti Zorbalık Web Tarayıcısı | Atakum Bilsem')
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
        self.ui.AramaAlan.editingFinished.connect(lambda: self.browser.setUrl(QUrl("https://www.google.com/search?q=" + self.ui.AramaAlan.text() if not self.ui.AramaAlan.text().startswith(('http://', 'https://')) else self.ui.AramaAlan.text())))
        self.ui.CB_Rapor.stateChanged.connect(lambda : self.ui.BTN_RaporGonder.setEnabled(not self.ui.BTN_RaporGonder.isEnabled()))
        self.browser.loadProgress.connect(self.YuklemeDurum)
        self.browser.loadFinished.connect(self.YuklemeSon)

        QShortcut(QKeySequence('Shift+J'), self).activated.connect(self.HizliKontrol)
        QShortcut(QKeySequence('Shift+P'), self).activated.connect(self.EkranGoruntusu)

        self.ui.BTN_Geri.clicked.connect(lambda: (self.browser.back(), self.ui.AramaAlan.clear()))
        self.ui.BTN_Ileri.clicked.connect(lambda: self.browser.forward())
        self.ui.BTN_Ana.clicked.connect(lambda: (self.browser.setUrl(QUrl("https://www.google.com.tr")),self.ui.AramaAlan.clear()))
        self.ui.BTN_Yenile.clicked.connect(lambda : self.browser.reload())
        self.ui.BTN_MesajKapat.clicked.connect(self.ui.MesajWidget.hide)
        self.ui.BTN_Rapor.clicked.connect(lambda : self.ui.RaporAlan.setVisible(not self.ui.RaporAlan.isVisible()))
        self.ui.BTN_Ayar.clicked.connect(lambda : self.ui.AyarAlan.setVisible(not self.ui.AyarAlan.isVisible()))
        self.ui.BTN_Engelle.clicked.connect(lambda: self.ui.BTN_Sansurle.setChecked(False))
        self.ui.BTN_Sansurle.clicked.connect(lambda: self.ui.BTN_Engelle.setChecked(False))
        self.browser.page().profile().downloadRequested.connect(self.DosyaIndirme)

        self.thread = JSThread()
        self.thread.my_signal.connect(self.JavaScriptYukle)
        self.thread.start()

        self.threads = LoopThread()
        self.threads.my_signal.connect(lambda: self.KontrolEt(Hedef="Loop"))
        self.threads.start()





    def KontrolEt(self, Hedef=None):
        global Hedef_URL
        self.SHOWBOX = True
        if not Hedef or Hedef == "Loop":
            self.SHOWBOX = False
            Hedef=self.browser.url().toString()
        
        Hedef_URL = Hedef
        self.ui.BTN_Kontrol.setIcon(QIcon("UI/Icons/loader.svg"))
        self.ui.BTN_Kontrol.setEnabled(False)
        thread = KontrolThread(self)
        thread.Signal.connect(self.KontrolSon)
        thread.start()
    def KontrolSon(self, Result):
        print(Result)
        if Result == "Riskli":
            self.ui.BTN_Kontrol.setIcon(QIcon("UI/Icons/KirmiziShield.svg"))
            if self.SHOWBOX == True:
                dialog = QMessageBox(parent=self, text=f"Bu Web Sayfası Zorbalık, Irkçılık vb. Sebepler Yüzünden Sansürlenmiştir.")
                ret = dialog.exec()  
                self.SHOWBOX= False
        elif Result == "Güvenli":self.ui.BTN_Kontrol.setIcon(QIcon("UI/Icons/yesilShield.svg"))
        else:self.ui.BTN_Kontrol.setIcon(QIcon("UI/Icons/uyari.svg"))
        self.ui.BTN_Kontrol.setEnabled(True)
        


    def JavaScriptYukle(self):
        for cümle in BeyazListe:
            if cümle in self.browser.url().toString():return
        try:
            def ScriptSon(banned_words):
                replace_script = ""
                for word in banned_words:replace_script += f"censoredText = censoredText.replace(new RegExp('{word}', 'gi'), '<span>SANSÜR</span>');\n"
                return replace_script
            script = f"""
                var elements = document.getElementsByTagName('*');
                for (var i = 0; i < elements.length; i++) {{
                    var element = elements[i];
                    for (var j = 0; j < element.childNodes.length; j++) {{
                        var node = element.childNodes[j];
                        if (node.nodeType === 3) {{
                            var text = node.nodeValue;
                            var censoredText = text;
                            {ScriptSon(YASAKLI)}
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
        except:
            pass



    

        
    


        
        
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
    def YuklemeSon(self):
        self.ui.progressBar.hide()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()