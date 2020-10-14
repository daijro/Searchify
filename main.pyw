from PyQt5 import QtCore, QtGui, QtWidgets
import os
import sys
import requests
from pyperclip import copy, paste
import threading
import json
from tkinter import messagebox
import tkinter as tk
import webbrowser

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
        self.savefile()

    def search(self):
        self.singleSearchProcessing.setHidden(True)
        self.singleSearchQuizletCheckbox.setEnabled(False)
        self.singleSearchBrainlyCheckbox.setEnabled(False)
        self.singleSearchButton.setEnabled(False)
        self.singleSearchLineEdit.setEnabled(False)
        self.singleSearchProcessing.setText('Processing...')
        self.singleSearchProcessing.show()
        specific_websites = []
        if self.singleSearchQuizletCheckbox.isChecked(): specific_websites.append('quizlet.com')
        if self.singleSearchBrainlyCheckbox.isChecked(): specific_websites.append('brainly.com')
        specific_websites = ','.join(specific_websites)
        text = self.singleSearchLineEdit.text().strip().replace('\n', ' ').strip('"')
        output = os.popen(f'"{os.path.join(os.path.dirname(sys.argv[0]), "bin", "parse_sites", "parse_sites.py")}" "{text}" "{specific_websites}" "{os.path.join(os.path.dirname(sys.argv[0]), "bin", "parser_file", "parser_file.py")}"').read()
        #print(f'"{os.path.join(os.path.dirname(sys.argv[0]), "bin", "runner.py")}" "{text}" "{specific_websites}"')
        #print(json.dumps(json.loads(output), indent=4))
        print(output)
        #os.system('pause')
        self.data = json.loads(output)

    def search2(self):
        #print(self.data)
        self.singleSearchTreeWidget.clear()
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

            item = QtWidgets.QTreeWidgetItem(self.singleSearchTreeWidget, [f''])
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

            label3 = QtWidgets.QLabel(confident)
            #label3.setWordWrap(True)
            label3.setMargin(10)
            label3.setFrameShape(QtWidgets.QFrame.StyledPanel)
            label3.setFrameShadow(QtWidgets.QFrame.Plain)
            label3.setLineWidth(1)
            label3.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)

            #self.singleSearchTreeWidget.addTopLevelItem(item)
            self.singleSearchTreeWidget.setItemWidget(item, 0, label3)
            #self.singleSearchTreeWidget.setItemWidget(item, 1, label4)
            self.singleSearchTreeWidget.setItemWidget(item, 1, label)
            self.singleSearchTreeWidget.setItemWidget(item, 2, label2)

        self.singleSearchQuizletCheckbox.setEnabled(True)
        self.singleSearchBrainlyCheckbox.setEnabled(True)
        self.singleSearchButton.setEnabled(True)
        self.singleSearchLineEdit.setEnabled(True)
        if self.data['error'] == 'Success':
            datalen = len(self.data['output'])
            self.singleSearchProcessing.setText(f"{datalen} result{'s' if datalen != 1 else ''} from {self.data['search_engine']} ({round(self.data['total_elapsed_time'], 3)} seconds)")
            #self.singleSearchProcessing.hide()
        else:
            self.singleSearchProcessing.setText(self.data['error'])
            messagebox.showerror('Error', self.data['error'])

    def run_search1(self):
        if not self.singleSearchQuizletCheckbox.isChecked() and not self.singleSearchBrainlyCheckbox.isChecked():
            messagebox.showerror('Search error', 'You have to have at least one search enabled.')
        elif self.singleSearchLineEdit.text().strip() == '':
            messagebox.showerror('Input error', 'There is no input.')
        else:
            t = threading.Thread(target=self.search)
            t.daemon = True
            t.start()
            while t.is_alive():
                QtCore.QCoreApplication.processEvents()
            self.search2()

    def getsingleselectedrow(self):
        i = None
        if self.data != []:
            rows = self.singleSearchTreeWidget.selectionModel().selectedRows()
            for r in rows:
                i = self.data['output'][r.row()]
                answer = ' '.join(self.data['output'][r.row()]['answer'].split())
                link = self.data['output'][r.row()]['link']
                if link.startswith('https://brainly.com'):
                    answer = answer.replace('Answer:', 'Answer: ').replace('Explanation:', '\nExplanation: ').replace('Thanks:', '\nThanks: ').strip()
                i.update({'answer': answer})
        return i

    def singlecopyitem(self):
        item = self.getsingleselectedrow()
        if item == None:
            messagebox.showerror('Error', 'Please select an item before copying it.')
        else:
            copy(item['answer'])

    def singleopenitem(self):
        item = self.getsingleselectedrow()
        if item == None:
            messagebox.showerror('Error', 'Please select an item before oepning it.')
        else:
            webbrowser.open(item['link'])

    def singleedittext(self):
        item = self.getsingleselectedrow()
        if item == None:
            messagebox.showerror('Error', 'Please select an item before editing it.')
        else:
            self.editTextInput.setPlainText(item['answer'])
            self.stackedWidget.setCurrentIndex(2)
            self.tabSwitcherList.setCurrentRow(2)
            QtCore.QCoreApplication.processEvents()
            self.paraphraser()

    def checkforupdate(self):
        try:
            data = requests.get('https://raw.githubusercontent.com/daijro/Searchify/main/current_version.json').content
            latestVersion = json.loads(data)['currentVersion']
            if self.currentVersion != latestVersion:
                if messagebox.askyesno('Update Avaliable', f'Update v{latestVersion} is avaliable to download. Would you like to go to the download page instead?'):
                    webbrowser.open('https://github.com/daijro/Searchify/blob/main/README.md#searchify')
                    sys.exit()
        except requests.exceptions.ConnectionError:
            if messagebox.askretrycancel('Connection Error', 'Could not connect to internet. Please try again later.'):
                self.checkforupdate()
            else:
                sys.exit()

    def pasteText(self):
        self.singleSearchLineEdit.setText(' '.join(paste().split()))
        if self.searchwhenpastingCheckbox.isChecked():
            self.run_search1()

    def savefile(self):
        data = {
            "searchQuizlet": self.singleSearchQuizletCheckbox.isChecked(),
            "searchBrainly": self.singleSearchBrainlyCheckbox.isChecked(),
            "searchWhenPasting": self.searchwhenpastingCheckbox.isChecked(),
            "checkForUpdates": self.checkforupdatesCheckbox.isChecked(),
            "themeInput": self.comboBox.currentText(),
        }
        cdfolder = os.path.dirname(sys.argv[0])

        if os.path.exists(os.path.join(cdfolder, 'config.json')): os.remove(os.path.join(cdfolder, 'config.json'))
        with open(os.path.join(cdfolder, 'config.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def openfile(self):
        data = json.load(open(os.path.join(os.path.dirname(sys.argv[0]), 'config.json')))
        self.singleSearchQuizletCheckbox.setChecked(data['searchQuizlet'])
        self.singleSearchBrainlyCheckbox.setChecked(data['searchBrainly'])
        self.searchwhenpastingCheckbox.setChecked(data['searchWhenPasting'])
        self.checkforupdatesCheckbox.setChecked(data['checkForUpdates'])
        self.comboBox.setCurrentText(data['themeInput'])
        self.switchthemes()

    def setconnections(self):
        MainWindow.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(sys.argv[0]), 'icons', 'icon.ico')))
        self.comboBox.setCurrentIndex(1)
        self.currentVersion = '1.2.0'
        self.data = []
        cdfolder = os.path.dirname(sys.argv[0])
        if os.path.exists(os.path.join(cdfolder, 'config.json')): self.openfile()
        else: self.savefile()
        if self.checkforupdatesCheckbox.isChecked(): self.checkforupdate()
        self.pushButton_2.clicked.connect(lambda: webbrowser.open('https://github.com/daijro/Searchify'))
        self.singlePasteButton.clicked.connect(self.pasteText)
        self.settingsButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.pushButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        self.singleSearchQuizletCheckbox.toggled.connect(self.savefile)
        self.singleSearchBrainlyCheckbox.toggled.connect(self.savefile)
        self.searchwhenpastingCheckbox.toggled.connect(self.savefile)
        self.checkforupdatesCheckbox.toggled.connect(self.savefile)

        #self.slowTypingCheckbox.toggled.connect(self.starthotkeythread)
        #self.quicksearchCheckbox.toggled.connect(self.starthotkeythread)


        self.singleSearchCopyButton.clicked.connect(self.singlecopyitem)
        self.singleSearchOpenLinkButton.clicked.connect(self.singleopenitem)

        self.singleSearchTreeWidget.setAutoScroll(False)
        self.singleSearchTreeWidget.setUniformRowHeights(False)
        self.singleSearchTreeWidget.setColumnWidth(0, 120)
        self.singleSearchTreeWidget.setColumnWidth(1, 350)
        self.singleSearchTreeWidget.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        self.stackedWidget.setCurrentIndex(0)
        self.singleSearchButton.clicked.connect(lambda: self.run_search1())
        self.singleSearchLineEdit.returnPressed.connect(lambda: self.run_search1())
        self.comboBox.currentIndexChanged.connect(self.switchthemes)
        self.singleSearchProcessing.hide()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1270, 713)
        MainWindow.setMinimumSize(QtCore.QSize(776, 353))
        font = QtGui.QFont()
        font.setFamily("Poppins Medium")
        font.setPointSize(11)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.stackedWidgetPage1 = QtWidgets.QWidget()
        self.stackedWidgetPage1.setObjectName("stackedWidgetPage1")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.stackedWidgetPage1)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.singleSearchOutputLayout = QtWidgets.QVBoxLayout()
        self.singleSearchOutputLayout.setObjectName("singleSearchOutputLayout")
        self.singleSearchTreeWidget = QtWidgets.QTreeWidget(self.stackedWidgetPage1)
        font = QtGui.QFont()
        font.setFamily("Poppins Medium")
        font.setPointSize(11)
        self.singleSearchTreeWidget.setFont(font)
        self.singleSearchTreeWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.singleSearchTreeWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.singleSearchTreeWidget.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.singleSearchTreeWidget.setRootIsDecorated(False)
        self.singleSearchTreeWidget.setUniformRowHeights(False)
        self.singleSearchTreeWidget.setObjectName("singleSearchTreeWidget")
        self.singleSearchOutputLayout.addWidget(self.singleSearchTreeWidget)
        self.singleSearchOptions = QtWidgets.QHBoxLayout()
        self.singleSearchOptions.setObjectName("singleSearchOptions")
        self.settingsButton = QtWidgets.QPushButton(self.stackedWidgetPage1)
        self.settingsButton.setMinimumSize(QtCore.QSize(40, 0))
        self.settingsButton.setMaximumSize(QtCore.QSize(40, 16777215))
        font = QtGui.QFont()
        font.setFamily("Segoe MDL2 Assets")
        font.setPointSize(22)
        self.settingsButton.setFont(font)
        self.settingsButton.setCheckable(False)
        self.settingsButton.setFlat(True)
        self.settingsButton.setObjectName("settingsButton")
        self.singleSearchOptions.addWidget(self.settingsButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.singleSearchOptions.addItem(spacerItem)
        self.singleSearchCopyButton = QtWidgets.QPushButton(self.stackedWidgetPage1)
        self.singleSearchCopyButton.setObjectName("singleSearchCopyButton")
        self.singleSearchOptions.addWidget(self.singleSearchCopyButton)
        self.singleSearchOpenLinkButton = QtWidgets.QPushButton(self.stackedWidgetPage1)
        self.singleSearchOpenLinkButton.setObjectName("singleSearchOpenLinkButton")
        self.singleSearchOptions.addWidget(self.singleSearchOpenLinkButton)
        self.singleSearchOutputLayout.addLayout(self.singleSearchOptions)
        self.gridLayout_2.addLayout(self.singleSearchOutputLayout, 3, 0, 1, 1)
        self.singleSearchInputLayout = QtWidgets.QHBoxLayout()
        self.singleSearchInputLayout.setObjectName("singleSearchInputLayout")
        self.singleSearchLineEdit = QtWidgets.QLineEdit(self.stackedWidgetPage1)
        font = QtGui.QFont()
        font.setFamily("Poppins")
        font.setPointSize(18)
        font.setBold(False)
        font.setWeight(50)
        self.singleSearchLineEdit.setFont(font)
        self.singleSearchLineEdit.setClearButtonEnabled(True)
        self.singleSearchLineEdit.setObjectName("singleSearchLineEdit")
        self.singleSearchInputLayout.addWidget(self.singleSearchLineEdit)
        self.singlePasteButton = QtWidgets.QPushButton(self.stackedWidgetPage1)
        self.singlePasteButton.setMinimumSize(QtCore.QSize(50, 50))
        self.singlePasteButton.setMaximumSize(QtCore.QSize(50, 16777215))
        font = QtGui.QFont()
        font.setFamily("Segoe MDL2 Assets")
        font.setPointSize(22)
        self.singlePasteButton.setFont(font)
        self.singlePasteButton.setFlat(False)
        self.singlePasteButton.setObjectName("singlePasteButton")
        self.singleSearchInputLayout.addWidget(self.singlePasteButton)
        self.singleSearchButton = QtWidgets.QPushButton(self.stackedWidgetPage1)
        self.singleSearchButton.setMinimumSize(QtCore.QSize(100, 50))
        font = QtGui.QFont()
        font.setFamily("Poppins Medium")
        font.setPointSize(14)
        self.singleSearchButton.setFont(font)
        self.singleSearchButton.setObjectName("singleSearchButton")
        self.singleSearchInputLayout.addWidget(self.singleSearchButton)
        self.gridLayout_2.addLayout(self.singleSearchInputLayout, 1, 0, 1, 1)
        self.singleSearchProcessing = QtWidgets.QLabel(self.stackedWidgetPage1)
        self.singleSearchProcessing.setObjectName("singleSearchProcessing")
        self.gridLayout_2.addWidget(self.singleSearchProcessing, 2, 0, 1, 1)
        self.titleLayout_2 = QtWidgets.QHBoxLayout()
        self.titleLayout_2.setContentsMargins(-1, 10, -1, 10)
        self.titleLayout_2.setObjectName("titleLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.titleLayout_2.addItem(spacerItem1)
        self.titleLabel_2 = QtWidgets.QLabel(self.stackedWidgetPage1)
        self.titleLabel_2.setMinimumSize(QtCore.QSize(0, 52))
        self.titleLabel_2.setMaximumSize(QtCore.QSize(16777215, 52))
        font = QtGui.QFont()
        font.setFamily("Poppins")
        font.setPointSize(28)
        font.setBold(True)
        font.setWeight(75)
        self.titleLabel_2.setFont(font)
        self.titleLabel_2.setObjectName("titleLabel_2")
        self.titleLayout_2.addWidget(self.titleLabel_2)
        self.titleIcon_2 = QtWidgets.QLabel(self.stackedWidgetPage1)
        self.titleIcon_2.setMaximumSize(QtCore.QSize(50, 50))
        self.titleIcon_2.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(sys.argv[0]).replace('/', '\\'), 'icons\\search.png')))
        self.titleIcon_2.setScaledContents(True)
        self.titleIcon_2.setObjectName("titleIcon_2")
        self.titleLayout_2.addWidget(self.titleIcon_2)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.titleLayout_2.addItem(spacerItem2)
        self.gridLayout_2.addLayout(self.titleLayout_2, 0, 0, 1, 1)
        self.stackedWidget.addWidget(self.stackedWidgetPage1)
        self.stackedWidgetPage2 = QtWidgets.QWidget()
        self.stackedWidgetPage2.setObjectName("stackedWidgetPage2")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.stackedWidgetPage2)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.pushButton = QtWidgets.QPushButton(self.stackedWidgetPage2)
        self.pushButton.setMinimumSize(QtCore.QSize(40, 0))
        self.pushButton.setMaximumSize(QtCore.QSize(40, 16777215))
        font = QtGui.QFont()
        font.setFamily("Segoe MDL2 Assets")
        font.setPointSize(22)
        self.pushButton.setFont(font)
        self.pushButton.setFlat(True)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_7.addWidget(self.pushButton, 3, 0, 1, 1)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.groupBox_2 = QtWidgets.QGroupBox(self.stackedWidgetPage2)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.license = QtWidgets.QTextBrowser(self.groupBox_2)
        self.license.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.license.setObjectName("license")
        self.gridLayout_3.addWidget(self.license, 1, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.groupBox_2)
        self.label_14.setObjectName("label_14")
        self.gridLayout_3.addWidget(self.label_14, 0, 0, 1, 1)
        self.gridLayout_5.addWidget(self.groupBox_2, 0, 0, 1, 1)
        self.horizontalLayout_14.addLayout(self.gridLayout_5)
        self.groupBox = QtWidgets.QGroupBox(self.stackedWidgetPage2)
        self.groupBox.setMaximumSize(QtCore.QSize(300, 16777215))
        self.groupBox.setAutoFillBackground(False)
        self.groupBox.setFlat(False)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.singleSearchQuizletCheckbox = QtWidgets.QCheckBox(self.groupBox)
        self.singleSearchQuizletCheckbox.setChecked(True)
        self.singleSearchQuizletCheckbox.setObjectName("singleSearchQuizletCheckbox")
        self.gridLayout_4.addWidget(self.singleSearchQuizletCheckbox, 2, 0, 1, 1)
        self.singleSearchBrainlyCheckbox = QtWidgets.QCheckBox(self.groupBox)
        self.singleSearchBrainlyCheckbox.setChecked(True)
        self.singleSearchBrainlyCheckbox.setObjectName("singleSearchBrainlyCheckbox")
        self.gridLayout_4.addWidget(self.singleSearchBrainlyCheckbox, 3, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout_4.addWidget(self.comboBox, 0, 0, 1, 1)
        self.searchwhenpastingCheckbox = QtWidgets.QCheckBox(self.groupBox)
        self.searchwhenpastingCheckbox.setChecked(False)
        self.searchwhenpastingCheckbox.setObjectName("searchwhenpastingCheckbox")
        self.gridLayout_4.addWidget(self.searchwhenpastingCheckbox, 1, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem3, 4, 0, 1, 1)
        self.checkforupdatesCheckbox = QtWidgets.QCheckBox(self.groupBox)
        self.checkforupdatesCheckbox.setChecked(True)
        self.checkforupdatesCheckbox.setObjectName("checkforupdatesCheckbox")
        self.gridLayout_4.addWidget(self.checkforupdatesCheckbox, 5, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_4.addWidget(self.pushButton_2, 6, 0, 1, 1)
        self.horizontalLayout_14.addWidget(self.groupBox)
        self.gridLayout_7.addLayout(self.horizontalLayout_14, 2, 0, 1, 1)
        self.titleLayout = QtWidgets.QHBoxLayout()
        self.titleLayout.setContentsMargins(-1, 10, -1, 10)
        self.titleLayout.setObjectName("titleLayout")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.titleLayout.addItem(spacerItem4)
        self.titleLabel = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.titleLabel.setMinimumSize(QtCore.QSize(0, 52))
        self.titleLabel.setMaximumSize(QtCore.QSize(16777215, 52))
        font = QtGui.QFont()
        font.setFamily("Poppins")
        font.setPointSize(28)
        font.setBold(True)
        font.setWeight(75)
        self.titleLabel.setFont(font)
        self.titleLabel.setObjectName("titleLabel")
        self.titleLayout.addWidget(self.titleLabel)
        self.titleIcon = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.titleIcon.setMaximumSize(QtCore.QSize(50, 50))
        self.titleIcon.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(sys.argv[0]).replace('/', '\\'), 'icons\\search.png')))
        self.titleIcon.setScaledContents(True)
        self.titleIcon.setObjectName("titleIcon")
        self.titleLayout.addWidget(self.titleIcon)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.titleLayout.addItem(spacerItem5)
        self.gridLayout_7.addLayout(self.titleLayout, 0, 0, 1, 1)
        self.stackedWidget.addWidget(self.stackedWidgetPage2)
        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Searchify v1.2.0 (Beta)"))
        self.singleSearchTreeWidget.setSortingEnabled(False)
        self.singleSearchTreeWidget.headerItem().setText(0, _translate("MainWindow", "Confidence"))
        self.singleSearchTreeWidget.headerItem().setText(1, _translate("MainWindow", "Identified Question"))
        self.singleSearchTreeWidget.headerItem().setText(2, _translate("MainWindow", "Answer"))
        self.settingsButton.setText(_translate("MainWindow", ""))
        self.singleSearchCopyButton.setToolTip(_translate("MainWindow", "Copy selected text"))
        self.singleSearchCopyButton.setText(_translate("MainWindow", "Copy"))
        self.singleSearchOpenLinkButton.setToolTip(_translate("MainWindow", "Open selected item in browser"))
        self.singleSearchOpenLinkButton.setText(_translate("MainWindow", "Open"))
        self.singleSearchLineEdit.setPlaceholderText(_translate("MainWindow", "Enter your question..."))
        self.singlePasteButton.setToolTip(_translate("MainWindow", "Paste text"))
        self.singlePasteButton.setText(_translate("MainWindow", ""))
        self.singleSearchButton.setText(_translate("MainWindow", "Search"))
        self.singleSearchProcessing.setText(_translate("MainWindow", "Processing..."))
        self.titleLabel_2.setText(_translate("MainWindow", "Searchify"))
        self.pushButton.setText(_translate("MainWindow", ""))
        self.groupBox_2.setTitle(_translate("MainWindow", "About"))
        self.license.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Poppins Medium\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Courier New\';\">Copyright 2020 u/daijro</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Courier New\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Courier New\';\">Licensed under the Apache License, Version 2.0 (the &quot;License&quot;);</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Courier New\';\">you may not use this file except in compliance with the License.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Courier New\';\">You may obtain a copy of the License at</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Courier New\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Courier New\';\">http://www.apache.org/licenses/LICENSE-2.0</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Courier New\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Courier New\';\">Unless required by applicable law or agreed to in writing, software</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Courier New\';\">distributed under the License is distributed on an &quot;AS IS&quot; BASIS,</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Courier New\';\">WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Courier New\';\">See the License for the specific language governing permissions and</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Courier New\';\">limitations under the License.</span></p></body></html>"))
        self.label_14.setText(_translate("MainWindow", "Version: v1.2.0 (Beta)"))
        self.groupBox.setTitle(_translate("MainWindow", "Settings"))
        self.singleSearchQuizletCheckbox.setText(_translate("MainWindow", "Search Quizlet"))
        self.singleSearchBrainlyCheckbox.setText(_translate("MainWindow", "Search Brainly (unstable)"))
        self.comboBox.setItemText(0, _translate("MainWindow", "Light Theme"))
        self.comboBox.setItemText(1, _translate("MainWindow", "Dark Theme"))
        self.comboBox.setItemText(2, _translate("MainWindow", "Black Theme"))
        self.searchwhenpastingCheckbox.setToolTip(_translate("MainWindow", "When the paste button is clicked, automatically search."))
        self.searchwhenpastingCheckbox.setText(_translate("MainWindow", "Search when Pasting"))
        self.checkforupdatesCheckbox.setText(_translate("MainWindow", "Check for updates"))
        self.pushButton_2.setText(_translate("MainWindow", "Open GitHub"))
        self.titleLabel.setText(_translate("MainWindow", "Searchify"))


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
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)

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
    palette_black.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)
    app.setStyle('Fusion')
    app.setPalette(palette)

    QtGui.QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(sys.argv[0]).replace('/', '\\'), 'fonts\\Poppins Medium.ttf'))
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.setconnections()
    MainWindow.show()
    sys.exit(app.exec_())
