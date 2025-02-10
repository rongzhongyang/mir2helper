# -*- coding: utf-8 -*-
import MainWindow
import sys
from PyQt6 import QtWidgets

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myMainWind = MainWindow.CMyMainWindow()
    myMainWind.show()
    sys.exit(app.exec())
