import os
import PyPDF2
import docx
import textract
from collections import Counter
from PyQt5 import QtCore, QtGui, QtWidgets
from multiprocessing import Pool, Manager
import sys

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # 设置主窗口对象
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(500, 500)

        # 创建中心窗口
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 创建各种控件
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
        self.textBrowser.setGeometry(QtCore.QRect(20, 190, 451, 271))
        self.textBrowser.setObjectName("textBrowser")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(20, 470, 91, 21))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(380, 470, 91, 21))
        self.pushButton_2.setObjectName("pushButton_2")


        # 设置控件的默认值
        self.label.setText("文件1：")
        self.label_2.setText("文件2：")
        self.label_3.setText("文件3：")
        self.label_4.setText("文件4：")
        self.pushButton1.setText("选择文件")
        self.pushButton2.setText("选择文件")
       
    def load_file1(self):
        """
        加载文件1的按钮点击事件。
        """
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(None, "选择文件", "", "PDF Files (*.pdf);;Word Files (*.docx);;Text Files (*.txt)")
        self.lineEdit1.setText(filepath)

    def load_file2(self):
        """
        加载文件2的按钮点击事件。
        """
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(None, "选择文件", "", "PDF Files (*.pdf);;Word Files (*.docx);;Text Files (*.txt)")
        self.lineEdit2.setText(filepath)

    def load_file3(self):
        """
        加载文件3的按钮点击事件。
        """
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(None, "选择文件", "", "PDF Files (*.pdf);;Word Files (*.docx);;Text Files (*.txt)")
        self.lineEdit3.setText(filepath)

    def load_file4(self):
        """
        加载文件4的按钮点击事件。
        """
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(None, "选择文件", "", "PDF Files (*.pdf);;Word Files (*.docx);;Text Files (*.txt)")
        self.lineEdit4.setText(filepath)

    def compute_and_display_distance(self):
        """
        计算并显示文件之间的距离。
        """
        # 获取所有文件的路径
        filepath1 = self.lineEdit1.text()
        filepath2 = self.lineEdit2.text()
        filepath3 = self.lineEdit3.text()
        filepath4 = self.lineEdit4.text()

        # 检查文件是否已经选择
        if not filepath1 or not filepath2:
            QtWidgets.QMessageBox.warning(None, "警告", "请至少选择两个文件。")
            return

        # 使用多进程加载文件并计算距离
        pool = Pool()
        manager = Manager()
        distances = manager.list()

        # 读取文件1的内容并计算其它所有文件与其的距离
        if filepath1:
            charset = "utf-8"
            if os.path.splitext(filepath1)[1].lower() == ".docx":
                charset = "gbk"
            process1 = pool.apply_async(self.load_text, (filepath1, charset))
            if filepath2:
                process2 = pool.apply_async(self.compute_distance, (process1.get(), self.load_text(filepath2, charset)))
                distances.append(process2)
            if filepath3:
                process3 = pool.apply_async(self.compute_distance, (process1.get(), self.load_text(filepath3, charset)))
                distances.append(process3)
            if filepath4:
                process4 = pool.apply_async(self.compute_distance, (process1.get(), self.load_text(filepath4, charset)))
                distances.append(process4)

        # 读取文件2的内容并计算其它所有文件与其的距离
        if filepath2:
            charset = "utf-8"
            if os.path.splitext(filepath2)[1].lower() == ".docx":
                charset = "gbk"
            process2 = pool.apply_async(self.load_text, (filepath2, charset))
            if filepath3:
                process3 = pool.apply_async(self.compute_distance, (process2.get(), self.load_text(filepath3, charset)))
                distances.append(process3)
            if filepath4:
                process4 = pool.apply_async(self.compute_distance, (process2.get(), self.load_text(filepath4, charset)))
                distances.append(process4)

        # 读取文件3的内容并计算其与文件4的距离
        if filepath3 and filepath4:
            charset = "utf-8"
            if os.path.splitext(filepath3)[1].lower() == ".docx" or os.path.splitext(filepath4)[1].lower() == ".docx":
                charset = "gbk"
            process3 = pool.apply_async(self.load_text, (filepath3, charset))
            process4 = pool.apply_async(self.load_text, (filepath4, charset))
            process5 = pool.apply_async(self.compute_distance, (process3.get(), process4.get()))
            distances.append(process5)

        # 等待所有进程执行完毕并获取结果
        pool.close()
        pool.join()
        # 在文本浏览器中显示计算结果
        if len(distances) == 2:
            text1 = os.path.basename(filepath1)
            text2 = os.path.basename(filepath2)
            result = "文件1（{}）和文件2（{}）之间的距离为：{:.6f}\n".format(text1, text2, distances[0].get())
            self.textBrowser.setText(result)
        elif len(distances) == 3:
            text1 = os.path.basename(filepath1)
            text2 = os.path.basename(filepath2)
            text3 = os.path.basename(filepath3)
            result = "文件1（{}）和文件2（{}）之间的距离为：{:.6f}\n".format(text1, text2, distances[0].get())
            result += "文件1（{}）和文件3（{}）之间的距离为：{:.6f}\n".format(text1, text3, distances[1].get())
            result += "文件2（{}）和文件3（{}）之间的距离为：{:.6f}\n".format(text2, text3, distances[2].get())
            self.textBrowser.setText(result)
        elif len(distances) == 4:
            text1 = os.path.basename(filepath1)
            text2 = os.path.basename(filepath2)
            text3 = os.path.basename(filepath3)
            text4 = os.path.basename(filepath4)
            result = "文件1（{}）和文件2（{}）之间的距离为：{:.6f}\n".format(text1, text2, distances[0].get())
            result += "文件1（{}）和文件3（{}）之间的距离为：{:.6f}\n".format(text1, text3, distances[1].get())
            result += "文件1（{}）和文件4（{}）之间的距离为：{:.6f}\n".format(text1, text4, distances[2].get())
            result += "文件2（{}）和文件3（{}）之间的距离为：{:.6f}\n".format(text2, text3, distances[3].get())
            result += "文件2（{}）和文件4（{}）之间的距离为：{:.6f}\n".format(text2, text4, distances[4].get())
            result += "文件3（{}）和文件4（{}）之间的距离为：{:.6f}\n".format(text3, text4, distances[5].get())
            self.textBrowser.setText(result)
if __name__ == '__main__':
    # 创建应用程序对象
    app = QtWidgets.QApplication(sys.argv)

    # 创建窗口对象
    MainWindow = QtWidgets.QMainWindow()

    # 创建主窗口UI对象
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    # 显示窗口
    MainWindow.show()

    # 进入应用程序主循环
    sys.exit(app.exec_())