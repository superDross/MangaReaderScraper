import sys
from functools import partial

import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw

from converter import convert
from download import download_manga
from search import Search

# https://pythonspot.com/pyqt5-tabs/
# https://build-system.fman.io/pyqt5-tutorial

# TODO:
# - free movement instead of gridbox layout
# - complete the other tabs
# - progress bar
# - move to thread so doesn't block gui interaction


class ResultsTable(qtw.QTableWidget):
    """ Search results in a tabeled format. """

    def __init__(self):
        super().__init__()
        self.results = None
        self.msg = qtw.QMessageBox()

    def _configure_headers(self):
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Title", "Chapter", "Type", "CBZ", ""])
        header = self.horizontalHeader()
        header.setDefaultAlignment(qtc.Qt.AlignCenter)
        header.setSectionResizeMode(0, qtw.QHeaderView.Stretch)
        header.setSectionResizeMode(3, qtw.QHeaderView.ResizeToContents)
        self.verticalHeader().setVisible(False)

    @staticmethod
    def create_combo_widget(num):
        """ Creates a combobox with selection from 0 to parsed num."""
        combobox = qtw.QComboBox()
        combobox.addItem("all")
        for i in range(1, int(num) + 1):
            combobox.addItem(str(i))
        return combobox

    def _add_row(self, row_num, name, url, chapters, _type):
        """ Search result row with chapter selection and download button."""
        self.setItem(row_num, 0, qtw.QTableWidgetItem(name))
        combo = self.create_combo_widget(chapters)
        self.setCellWidget(row_num, 1, combo)
        self.setItem(row_num, 2, qtw.QTableWidgetItem(_type))
        checkbox = qtw.QCheckBox()
        self.setCellWidget(row_num, 3, checkbox)
        download_button = qtw.QPushButton("Download")
        # connect state of row widgets to click function
        download_button.clicked.connect(partial(self.on_click, url, combo, checkbox))
        self.setCellWidget(row_num, 4, download_button)

    def _add_rows(self):
        """ Transforms the search results into rows."""
        row_num = 0
        for result in self.results.items():
            name, url, chapters, _type = list(result[1].values())
            self._add_row(row_num, name, url, chapters, _type)
            row_num += 1

    def construct(self, results):
        """ Creates the tabel."""
        self.results = results
        self.setRowCount(len(results.keys()))
        self._configure_headers()
        self._add_rows()

    def _completion_msg(self):
        self.msg.setIcon(qtw.QMessageBox.Information)
        self.msg.setText("Download Complete!")
        self.msg.setWindowTitle("message")
        self.msg.show()

    @qtc.pyqtSlot()
    def on_click(self, url, combo, checkbox):
        """ Downloads the selected manga."""
        checked = checkbox.isChecked()
        print(checked)
        volume = combo.currentText() if combo.currentText() != "all" else None
        download_manga(url, volume)
        convert(url, volume, checked)
        self._completion_msg()


class SearchTab(qtw.QWidget):
    """ Tab allowing user to search and select mangas."""

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
        """ Configures the text label."""
        self.layout.addWidget(self.text_label, 0, 0)

    def _search_line(self):
        """ Configures search box."""
        self.search_line.setMaximumSize(200, 25)
        self.search_line.returnPressed.connect(self.submit_button.click)
        self.layout.addWidget(self.search_line, 1, 0)

    def _submit_button(self):
        """ Configures search submission button."""
        self.submit_button.clicked.connect(self.on_click)
        self.submit_button.setMaximumSize(80, 25)
        self.layout.addWidget(self.submit_button, 1, 1)

    def _table_box(self):
        """ Configures the search result table."""
        self.layout.addWidget(self.table, 2, 0)

    def _configure(self):
        self._text_label()
        self._search_line()
        self._submit_button()
        self._table_box()
        self.setLayout(self.layout)

    @qtc.pyqtSlot()
    def on_click(self):
        """ Used to submit query for search."""
        self.user_input = self.search_line.text()
        search = Search()
        search.search(self.user_input)
        self.table.construct(search.results)
        self.search_line.clear()


class SelectionTab(qtw.QWidget):
    """ Tab allowing the user to download a known manga & volume."""

    def __init__(self):
        super().__init__()
        self.name = "Selection"


class HelpTab(qtw.QWidget):
    """ Tab showing application instructions."""

    def __init__(self):
        super().__init__()
        self.name = "Help"


class TabsWidget(qtw.QWidget):
    """ All tabs in the main window."""

    def __init__(self, parent, height, width):
        super().__init__(parent)
        self.layout = qtw.QVBoxLayout(self)
        self.tabs = qtw.QTabWidget()
        self.tab1 = SearchTab()
        self.tab2 = SelectionTab()
        self.tab3 = HelpTab()
        self._configure(width, height)

    def _configure(self, width, height):
        self.tabs.resize(width, height)
        self.tabs.addTab(self.tab1, self.tab1.name)
        # self.tabs.addTab(self.tab2, self.tab2.name)
        # self.tabs.addTab(self.tab3, self.tab3.name)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


class AppGui(qtw.QMainWindow):
    """ Primary GUI window."""

    def __init__(self):
        super().__init__()
        self.title = "MangaReaderScraper"
        self.left = 480
        self.top = 480
        self.width = 756
        self.height = 591
        self._configure()

    def _configure(self):
        self.setWindowTitle(self.title)
        # set initial position on desktop
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.statusBar().showMessage("In progress")
        self.setCentralWidget(TabsWidget(self, self.height, self.width))
        self.show()
