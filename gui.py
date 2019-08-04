import os
import sys
from functools import partial

import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QIcon, QTextCursor

import download
from config import JPG_DIR
from search import Search

# https://pythonspot.com/pyqt5-tabs/
# https://build-system.fman.io/pyqt5-tutorial


def download_manga(manga, volume):
    downloader = download.DownloadManga(manga)
    if not os.path.exists(JPG_DIR):
        os.makedirs(JPG_DIR)
    if volume.isdigit() or isinstance(volume, int):
        downloader.download_volume(volume)
    elif isinstance(volume, str):
        downloader.download_volumes(volume)
    else:
        downloader.download_all_volumes()


class ResultsTable(qtw.QTableWidget):
    def __init__(self):
        super().__init__()
        self.results = None

    def _set_headers(self):
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Title", "Chapter", "Type", ""])
        self.horizontalHeader().setSectionResizeMode(0, qtw.QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)

    @staticmethod
    def create_combo_widget(num):
        combobox = qtw.QComboBox()
        combobox.addItem("all")
        for i in range(1, int(num) + 1):
            combobox.addItem(str(i))
        return combobox

    def _add_row(self, row_num, name, url, chapters, _type):
        self.setItem(row_num, 0, qtw.QTableWidgetItem(name))
        combo = self.create_combo_widget(chapters)
        self.setCellWidget(row_num, 1, combo)
        self.setItem(row_num, 2, qtw.QTableWidgetItem(_type))
        download_button = qtw.QPushButton("Download")
        download_button.clicked.connect(partial(self.on_click, url, combo))
        self.setCellWidget(row_num, 3, download_button)

    def _add_rows(self):
        row_num = 0
        for result in self.results.items():
            name, url, chapters, _type = list(result[1].values())
            self._add_row(row_num, name, url, chapters, _type)
            row_num += 1

    def construct(self, results):
        self.results = results
        self.setRowCount(len(results.keys()))
        self._set_headers()
        self._add_rows()

    @qtc.pyqtSlot()
    def on_click(self, url, combo):
        volume = combo.currentText() if combo.currentText() != "any" else None
        print(f"selected {url} volume {volume}")
        download_manga(url, volume)


class SearchTab(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.name = "Search"
        self.text_label = qtw.QLabel("Search for a Manga:")
        self.search_line = qtw.QLineEdit(self)
        self.submit_button = qtw.QPushButton("Submit")
        self.table = ResultsTable()
        self.layout = qtw.QGridLayout(self)
        self.layout.setSpacing(10)
        self.user_input = None
        self._configure()

    def _text_label(self):
        self.layout.addWidget(self.text_label, 0, 0)

    def _search_line(self):
        self.search_line.setMaximumSize(200, 25)
        self.search_line.resize(20, 20)
        self.search_line.move(15, 1)
        self.layout.addWidget(self.search_line, 1, 0)

    def _submit_button(self):
        self.submit_button.clicked.connect(self.on_click)
        self.submit_button.setMaximumSize(80, 25)
        self.layout.addWidget(self.submit_button, 1, 1)

    def _table_box(self):
        self.layout.addWidget(self.table, 2, 0)

    def _configure(self):
        self._text_label()
        self._search_line()
        self._submit_button()
        self._table_box()
        self.setLayout(self.layout)

    @qtc.pyqtSlot()
    def on_click(self):
        print(self.search_line.text())
        self.user_input = self.search_line.text()
        search = Search()
        search.search(self.user_input)
        self.table.construct(search.results)
        self.search_line.clear()


class SelectionTab(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.name = "Selection"


class TableWidget(qtw.QWidget):
    def __init__(self, parent, height, width):
        super().__init__(parent)
        self.layout = qtw.QVBoxLayout(self)
        self.tabs = qtw.QTabWidget()
        self.tab1 = SearchTab()
        self.tab2 = SelectionTab()
        self._configure(width, height)

    def _configure(self, width, height):
        self.tabs.resize(width, height)
        self.tabs.addTab(self.tab1, self.tab1.name)
        self.tabs.addTab(self.tab2, self.tab2.name)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


class App(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "MangaReaderScraper"
        self.left = 480
        self.top = 480
        self.width = 656
        self.height = 591
        self._configure()

    def _configure(self):
        self.setWindowTitle(self.title)
        # set initial position on desktop
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.statusBar().showMessage("In progress")
        self.setCentralWidget(TableWidget(self, self.height, self.width))
        self.show()


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
