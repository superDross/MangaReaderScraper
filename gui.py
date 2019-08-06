from functools import partial

import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw

from converter import convert
from download import download_manga
from search import Search

# https://pythonspot.com/pyqt5-tabs/
# https://build-system.fman.io/pyqt5-tutorial
# https://www.riverbankcomputing.com/static/Docs/PyQt4/classes.html

# TODO:
# - turn download buttons into checkboxes with a single download button for all
# - select volume ranges
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
        # stops massive selection box appearing
        combo.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.setCellWidget(row_num, 1, combo)
        self.setItem(row_num, 2, qtw.QTableWidgetItem(_type))
        checkbox = qtw.QCheckBox()
        self.setCellWidget(row_num, 3, checkbox)
        download_button = qtw.QPushButton("Download")
        # connect state of row widgets to click function
        download_button.clicked.connect(
            partial(self.on_click, url, combo, checkbox)
        )
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
        self.search_layout = qtw.QHBoxLayout()
        self.table = ResultsTable()
        self.table_layout = qtw.QVBoxLayout()
        self._configure()

    def _text_label(self):
        """ Configures the text label."""
        self.search_layout.addWidget(self.text_label)

    def _search_line(self):
        """ Configures search box."""
        self.search_line.setMaximumSize(200, 25)
        self.search_line.returnPressed.connect(self.submit_button.click)
        self.search_layout.addWidget(self.search_line)

    def _submit_button(self):
        """ Configures search submission button."""
        self.submit_button.clicked.connect(self.on_click)
        self.submit_button.setMaximumSize(80, 25)
        self.search_layout.addWidget(self.submit_button)

    def _table_box(self):
        """ Configures the search result table."""
        self.table_layout.addWidget(self.table)

    def _configure(self):
        self._text_label()
        self._search_line()
        self._submit_button()
        self._table_box()
        # layouts have to be joined together
        self.table_layout.addLayout(self.search_layout)
        self.setLayout(self.table_layout)

    @qtc.pyqtSlot()
    def on_click(self):
        """ Used to submit query for search."""
        search = Search()
        search.search(self.search_line.text())
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
        self.setCentralWidget(TabsWidget(self, self.height, self.width))
        self.show()
