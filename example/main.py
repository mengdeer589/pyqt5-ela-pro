import sys, os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QApplication

from mainwindow import MainWindow
from SplashScreen import SplashScreen

os.chdir(os.path.dirname(os.path.abspath(__file__)))


from PyQt5ElaWidgetTools import eApp

try:
    QT_VERSION_STR = "5.14.0"
except:
    QT_VERSION_STR = "6.8.3"

if QT_VERSION_STR < "6.0.0":
    QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    if QT_VERSION_STR >= "5.14.0":
        QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

app = QApplication(sys.argv)

splash = SplashScreen()
splash.create(app)
splash.showMessage("正在初始化...")

eApp.init()
splash.showMessage("正在加载主题...")

w = MainWindow()
splash.showMessage("正在启动窗口...")

splash.finish(w)
w.show()

app.exec()
