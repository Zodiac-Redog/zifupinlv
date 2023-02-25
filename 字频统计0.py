import os
import PyPDF2
import docx
from collections import Counter
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import textract
from pdfminer.high_level import extract_text
import numpy as np
from multiprocessing import Pool, Manager
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(500, 500)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 20, 81, 21))
        self.label.setObjectName("label")
        self.lineEdit1 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit1.setGeometry(QtCore.QRect(110, 20, 261, 21))
        self.lineEdit1.setObjectName("lineEdit1")
        self.pushButton1 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton1.setGeometry(QtCore.QRect(380, 20, 91, 21))
        self.pushButton1.setObjectName("pushButton1")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 60, 81, 21))
        self.label_2.setObjectName("label_2")
        self.lineEdit2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit2.setGeometry(QtCore.QRect(110, 60, 261, 21))
        self.lineEdit2.setObjectName("lineEdit2")
        self.pushButton2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton2.setGeometry(QtCore.QRect(380, 60, 91, 21))
        self.pushButton2.setObjectName("pushButton2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(20, 100, 81, 21))
        self.label_3.setObjectName("label_3")
        self.lineEdit3 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit3.setGeometry(QtCore.QRect(110, 100, 261, 21))
        self.lineEdit3.setObjectName("lineEdit3")
        self.pushButton3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton3.setGeometry(QtCore.QRect(380, 100, 91, 21))
        self.pushButton3.setObjectName("pushButton3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(20, 140, 81, 21))
        self.label_4.setObjectName("label_4")
        self.lineEdit4 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit4.setGeometry(QtCore.QRect(110, 140, 261, 21))
        self.lineEdit4.setObjectName("lineEdit4")
        self.pushButton4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton4.setGeometry(QtCore.QRect(380, 140, 91, 21))
        self.pushButton4.setObjectName("pushButton4")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(20, 200, 451, 251))
        self.textBrowser.setObjectName("textBrowser")
        self.pushButton5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton5.setGeometry(QtCore.QRect(200, 170, 91, 21))
        self.pushButton5.setObjectName("pushButton5")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.file_paths = [None] * 4  # 用于存储用户选择的文件路径
        self.block_size = 1024 * 1024  # 每个文件块的大小，单位为字节
        self.total_chars = {}  # 用于存储每个文件的总字符数
        self.pushButton1.clicked.connect(self.get_file_path)
        self.pushButton2.clicked.connect(self.get_file_path)
        self.pushButton3.clicked.connect(self.get_file_path)
        self.pushButton4.clicked.connect(self.get_file_path)
        self.pushButton5.clicked.connect(self.compute_and_display_distance)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "文件1"))
        self.pushButton1.setText(_translate("MainWindow", "选择文件"))
        self.label_2.setText(_translate("MainWindow", "文件2"))
        self.pushButton2.setText(_translate("MainWindow", "选择文件"))
        self.label_3.setText(_translate("MainWindow", "文件3"))
        self.pushButton3.setText(_translate("MainWindow", "选择文件"))
        self.label_4.setText(_translate("MainWindow", "文件4"))
        self.pushButton4.setText(_translate("MainWindow", "选择文件"))
        self.pushButton5.setText(_translate("MainWindow", "计算距离"))
    def get_file_path(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName()
        button = self.sender()
        if button == self.pushButton1:
            self.lineEdit1.setText(file_path)
            self.file_paths[0] = file_path
        elif button == self.pushButton2:
            self.lineEdit2.setText(file_path)
            self.file_paths[1] = file_path
        elif button == self.pushButton3:
            self.lineEdit3.setText(file_path)
            self.file_paths[2] = file_path
        elif button == self.pushButton4:
            self.lineEdit4.setText(file_path)
            self.file_paths[3] = file_path
    def count_chars_pdf(self, file_path):
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfFileReader(f)
            total_chars = 0
            for page_num in range(pdf_reader.getNumPages()):
                page = pdf_reader.getPage(page_num)
                text = page.extractText()
                total_chars += len(text)
        return total_chars

    def count_chars_docx(self, file_path):
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return len(''.join(full_text))

    def count_chars_txt(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return len(text)

    def compute_distance(self, file_paths):
        # 计算每个文件的总字符数
        for file_path in file_paths:
            if file_path is not None:
                file_type = os.path.splitext(file_path)[-1].lower()
                if file_type == ".pdf":
                    total_chars = self.count_chars_pdf(file_path)
                elif file_type == ".doc" or file_type == ".docx":
                    total_chars = self.count_chars_docx(file_path)
                elif file_type == ".txt":
                    total_chars = self.count_chars_txt(file_path)
                else:
                    total_chars = 0
                self.total_chars[file_path] = total_chars

        # 分块读取和计算距离
        distances = []
        for i in range(len(file_paths)):
            if file_paths[i] is None:
                continue
            for j in range(i+1, len(file_paths)):
                if file_paths[j] is None:
                    continue
                distance = 0
                with open(file_paths[i], 'rb') as f1, open(file_paths[j], 'rb') as f2:
                    while True:
                        block1 = f1.read(self.block_size)
                        block2 = f2.read(self.block_size)
                        if not block1 or not block2:
                            break
                        freq1 = np.zeros((256,), dtype=int)
                        freq2 = np.zeros((256,), dtype=int)
                        np.add.at(freq1, np.frombuffer(block1, dtype=np.uint8), 1)
                        np.add.at(freq2, np.frombuffer(block2, dtype=np.uint8), 1)
                        freq1 /= self.total_chars[file_paths[i]]
                        freq2 /= self.total_chars[file_paths[j]]
                        diff = freq1 - freq2
                        distance += np.sum(diff**2)
                distances.append(distance)
        return distances
    def compute_and_display_distance(self):
        # 计算距离
        distances = self.compute_distance(self.file_paths)
        # 显示结果
        result = ""
        for i in range(len(self.file_paths)):
            if self.file_paths[i] is not None:
                result += f"{os.path.basename(self.file_paths[i])}: {distances[i]}\n"
        self.textBrowser.setText(result)
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
