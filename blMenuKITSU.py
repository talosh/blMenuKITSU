import sys
from PyQt5.QtWidgets import QApplication, QWidget

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'My First Application'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(300, 300, 400, 200)  # position x, position y, width, height
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
