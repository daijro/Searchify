from PyQt5 import QtCore, QtGui, QtWidgets
import os
import sys
import threading
from tkinter import messagebox
import tkinter as tk
import json

root = tk.Tk()
root.withdraw()

class Ui_MainWindow(object):
    def switchthemes(self):
        if self.comboBox.currentText() == 'Light Theme':
            app.setPalette(palette_light)
        elif self.comboBox.currentText() == 'Dark Theme':
            app.setPalette(palette)
        elif self.comboBox.currentText() == 'Black Theme':
            app.setPalette(palette_black)

    def savefile(self):
        data = {
            "searchQuizlet": self.checkBox.isChecked(),
            "searchBrainly": self.checkBox_2.isChecked(),
            "themeInput": self.comboBox.currentText(),
        }
        cdfolder = os.path.dirname(sys.argv[0])

        if os.path.exists(os.path.join(cdfolder, 'config.json')): os.remove(os.path.join(cdfolder, 'config.json'))
        with open(os.path.join(cdfolder, 'config.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def openfile(self):
        data = json.load(open(os.path.join(os.path.dirname(sys.argv[0]), 'config.json')))
        self.checkBox.setChecked(data['searchQuizlet'])
        self.checkBox_2.setChecked(data['searchBrainly'])
        self.comboBox.setCurrentText(data['themeInput'])
        self.switchthemes()

    def search(self):
        self.checkBox.setEnabled(False)
        self.checkBox_2.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.lineEdit.setEnabled(False)
        self.label_3.setText('Processing...')
        self.label_3.show()
        specific_websites = []
        if self.checkBox.isChecked(): specific_websites.append('quizlet.com')
        if self.checkBox_2.isChecked(): specific_websites.append('brainly.com')
        specific_websites = ','.join(specific_websites)
        text = self.lineEdit.text().strip().replace('\n', ' ').strip('"')
        output = os.popen(f'"{os.path.join(os.path.dirname(sys.argv[0]), "bin", "parse_sites", "parse_sites.py")}" "{text}" "{specific_websites}" "{os.path.join(os.path.dirname(sys.argv[0]), "bin", "parser_file", "parser_file.py")}"').read()
        #print(f'"{os.path.join(os.path.dirname(sys.argv[0]), "bin", "runner.py")}" "{text}" "{specific_websites}"')
        #print(json.dumps(json.loads(output), indent=4))
        print(output)
        #os.system('pause')
        self.data = json.loads(output)

    def search2(self):
        #print(self.data)
        self.treeWidget.clear()
        for i in self.data['output']:
            confident = i['confidence']
            answer = i['answer']
            question = i['question']
            link = i['link']

            if confident == 100.0:
                confident = 'Exact Match'
            else: confident = str(confident)+'%'

            answer = ' '.join(answer.split())
            if link.startswith('https://brainly.com'):
                confident = str(confident)+'\n(Brainly)'
                answer = answer.replace('Answer:', 'Answer: ').replace('Explanation:', '\nExplanation: ').replace('Thanks:', '\nThanks: ')
            elif link.startswith('https://quizlet.com'): confident = str(confident)+'\n(Quizlet)'

            item = QtWidgets.QTreeWidgetItem(self.treeWidget, [f'{confident}'])
            label = QtWidgets.QLabel(' '.join(question.split()))
            label.setWordWrap(True)
            label.setMargin(10)
            label.setFrameShape(QtWidgets.QFrame.StyledPanel)
            label.setFrameShadow(QtWidgets.QFrame.Plain)
            label.setLineWidth(1)
            label.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)

            label2 = QtWidgets.QLabel(answer)
            label2.setWordWrap(True)
            label2.setMargin(10)
            label2.setFrameShape(QtWidgets.QFrame.StyledPanel)
            label2.setFrameShadow(QtWidgets.QFrame.Plain)
            label2.setLineWidth(1)
            label2.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)

            label3 = QtWidgets.QLabel(' \n ')
            #label3.setWordWrap(True)
            label3.setMargin(10)
            label3.setFrameShape(QtWidgets.QFrame.StyledPanel)
            label3.setFrameShadow(QtWidgets.QFrame.Plain)
            label3.setLineWidth(1)
            label3.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)

            #self.treeWidget.addTopLevelItem(item)
            self.treeWidget.setItemWidget(item, 0, label3)
            #self.treeWidget.setItemWidget(item, 1, label4)
            self.treeWidget.setItemWidget(item, 1, label)
            self.treeWidget.setItemWidget(item, 2, label2)

        self.checkBox.setEnabled(True)
        self.checkBox_2.setEnabled(True)
        self.pushButton.setEnabled(True)
        self.lineEdit.setEnabled(True)
        if self.data['error'] == 'Success':
            datalen = len(self.data['output'])
            self.label_3.setText(f"{datalen} result{'s' if datalen != 1 else ''} from {self.data['search_engine']} ({round(self.data['total_elapsed_time'], 3)} seconds)")
            #self.label_3.hide()
        else:
            self.label_3.setText(self.data['error'])
            messagebox.showerror('Error', self.data['error'])

    def run_search1(self):
        if not self.checkBox.isChecked() and not self.checkBox_2.isChecked():
            messagebox.showerror('Search error', 'You have to have at least one search enabled.')
        elif self.lineEdit.text().strip() == '':
            messagebox.showerror('Input error', 'There is no input.')
        else:
            t = threading.Thread(target=self.search)
            t.daemon = True
            t.start()
            while t.is_alive():
                QtCore.QCoreApplication.processEvents()
            self.search2()

    def setconnections(self):
        MainWindow.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(sys.argv[0]), 'icons', 'icon.ico')))
        self.horizontalLayout_3.setContentsMargins(0, 10, 0, 10)
        #self.checkBox_3.toggled.connect(lambda x: self.treeWidget.setUniformRowHeights(x))
        self.treeWidget.setAutoScroll(False)
        self.treeWidget.setUniformRowHeights(False)
        if os.path.exists(os.path.join(os.path.dirname(sys.argv[0]), 'config.json')):
            self.openfile()

        self.checkBox.toggled.connect(self.savefile)
        self.checkBox_2.toggled.connect(self.savefile)
        self.comboBox.currentTextChanged.connect(self.savefile)

        self.treeWidget.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.pushButton.clicked.connect(lambda: self.run_search1())
        self.lineEdit.returnPressed.connect(lambda: self.run_search1())
        self.comboBox.currentTextChanged.connect(self.switchthemes)
        #self.treeWidget.sortByColumn(0, QtCore.Qt.DescendingOrder)
        #self.treeWidget.setColumnWidth(0, 50)
        self.treeWidget.setColumnWidth(0, 120)
        self.treeWidget.setColumnWidth(1, 350)


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1300, 700)
        MainWindow.setMinimumSize(QtCore.QSize(700, 300))
        font = QtGui.QFont()
        font.setFamily("Poppins Medium")
        font.setPointSize(11)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_2.addWidget(self.checkBox)
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_2.setChecked(True)
        self.checkBox_2.setObjectName("checkBox_2")
        self.horizontalLayout_2.addWidget(self.checkBox_2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        #self.checkBox_3 = QtWidgets.QCheckBox(self.centralwidget)
        #self.checkBox_3.setChecked(True)
        #self.checkBox_3.setObjectName("checkBox_3")
        #self.horizontalLayout_2.addWidget(self.checkBox_3)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout_2.addWidget(self.comboBox)
        self.gridLayout.addLayout(self.horizontalLayout_2, 5, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setMinimumSize(QtCore.QSize(0, 52))
        self.label.setMaximumSize(QtCore.QSize(16777215, 52))
        font = QtGui.QFont()
        font.setFamily("Poppins")
        font.setPointSize(28)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setMaximumSize(QtCore.QSize(50, 50))
        self.label_2.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(sys.argv[0]).replace('/', '\\'), 'icons\\search.png')))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Poppins Medium")
        font.setPointSize(11)
        self.treeWidget.setFont(font)
        self.treeWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.treeWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.treeWidget.setRootIsDecorated(False)
        self.treeWidget.setObjectName("treeWidget")
        self.verticalLayout.addWidget(self.treeWidget)
        self.gridLayout.addLayout(self.verticalLayout, 3, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Poppins")
        font.setPointSize(18)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit.setFont(font)
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setMinimumSize(QtCore.QSize(100, 50))
        font = QtGui.QFont()
        font.setFamily("Poppins Medium")
        font.setPointSize(14)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.label_3.hide()
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Searchify v1.1.3b"))
        self.checkBox.setText(_translate("MainWindow", "Search Quizlet"))
        self.checkBox_2.setText(_translate("MainWindow", "Search Brainly"))
        #self.checkBox_3.setText(_translate("MainWindow", "Uniform Heights"))
        self.comboBox.setItemText(0, _translate("MainWindow", "Light Theme"))
        self.comboBox.setItemText(1, _translate("MainWindow", "Dark Theme"))
        self.comboBox.setItemText(2, _translate("MainWindow", "Black Theme"))
        self.label.setText(_translate("MainWindow", "Searchify"))
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Confidence"))
        self.treeWidget.headerItem().setText(1, _translate("MainWindow", "Identified Question"))
        self.treeWidget.headerItem().setText(2, _translate("MainWindow", "Answer"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Enter your question..."))
        self.pushButton.setText(_translate("MainWindow", "Search"))
        self.label_3.setText(_translate("MainWindow", "Searching..."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    palette_light = QtGui.QPalette()
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(25,35,45))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(39, 49, 58))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(25,35,45))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(25,35,45))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.blue)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(20, 129, 216))
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)

    palette_black = QtGui.QPalette()
    palette_black.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
    palette_black.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette_black.setColor(QtGui.QPalette.Base, QtGui.QColor(10, 10, 10))
    palette_black.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(0, 0, 0))
    palette_black.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette_black.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette_black.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette_black.setColor(QtGui.QPalette.Button, QtGui.QColor(0, 0, 0))
    palette_black.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette_black.setColor(QtGui.QPalette.BrightText, QtCore.Qt.blue)
    palette_black.setColor(QtGui.QPalette.Highlight, QtGui.QColor(20, 129, 216))
    palette_black.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setStyle('Fusion')
    #app.setPalette(palette)

    QtGui.QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(sys.argv[0]).replace('/', '\\'), 'fonts\\Poppins Medium.ttf'))
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.setconnections()
    MainWindow.show()
    sys.exit(app.exec_())
