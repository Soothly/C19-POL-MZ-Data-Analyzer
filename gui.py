import sys
from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QApplication,
    QComboBox,
    QLabel,
)
from PyQt5 import QtCore
from lib.territory import TerritoryCodes
from analyzer import analyze


class CovidDataPlotter(QWidget):
    def __init__(self):
        super().__init__()
        self.codes = TerritoryCodes()
        self.territory_types = {
            "province": self.codes.province_codes,
            "county": self.codes.county_codes,
        }
        self.initUI()

    def initUI(self):
        self.setWindowTitle("COVID-19 Data Plotter")
        self.setGeometry(QtCore.QRect(500, 500, 350, 70))
        self.okButton = QPushButton("Plot")
        self.okButton.clicked.connect(self.draw_plots)
        self.territory_types_dropdown = QComboBox()
        self.territory_types_dropdown.setMinimumWidth(120)
        self.territory_types_dropdown.addItems(self.territory_types.keys())
        self.territory_types_dropdown.currentTextChanged.connect(self.selection_change)
        self.territory_type = self.territory_types_dropdown.currentText()
        self.label = QLabel("Welcome!")

        self.territory_dropdown = QComboBox()
        self.territory_dropdown.addItems(self.codes.province_codes)
        self.territory_dropdown.setMinimumWidth(120)

        hbox = QHBoxLayout()
        hbox.addWidget(self.territory_types_dropdown, alignment=QtCore.Qt.AlignCenter)
        hbox.addStretch(1)
        hbox.addWidget(self.territory_dropdown, alignment=QtCore.Qt.AlignCenter)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)
        vbox.addLayout(hbox)
        vbox.addWidget(self.okButton)

        self.setLayout(vbox)
        self.show()

    def selection_change(self, text):
        selection_options = self.codes.get_codes_for_territory_type(text)
        self.territory_dropdown.clear()
        self.territory_dropdown.addItems(list(selection_options))

    def draw_plots(self):
        self.label.setText("Processing...")
        self.chosen_terrain = self.territory_dropdown.currentText()
        self.chosen_territory_type = self.territory_types_dropdown.currentText()
        analyze(self.chosen_territory_type, self.chosen_terrain)
        self.label.setText("Ready to go :)")


def main():
    app = QApplication(sys.argv)
    ex = CovidDataPlotter()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
