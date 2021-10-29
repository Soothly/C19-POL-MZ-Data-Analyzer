import sys
from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QApplication,
    QComboBox,
)
from lib.territory import TerritoryCodes
from analyzer import analyze


class CovidDataPlotter(QWidget):
    def __init__(self):
        super().__init__()
        self.codes = TerritoryCodes()
        self.territory_types = {
            "wojewodztwo": self.codes.province_codes,
            "powiat": self.codes.county_codes,
        }
        self.territory_types_list = list(self.territory_types)
        self.initUI()

    def initUI(self):

        self.okButton = QPushButton("Plot")
        self.okButton.clicked.connect(self.draw_plots)
        self.territory_types_dropdown = QComboBox()
        self.territory_types_dropdown.addItems(self.territory_types.keys())
        self.territory_types_dropdown.currentTextChanged.connect(self.selection_change)
        self.territory_type = self.territory_types_dropdown.currentText()

        self.territory_dropdown = QComboBox()
        self.territory_dropdown.addItems(self.codes.province_codes)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.territory_types_dropdown)
        hbox.addWidget(self.territory_dropdown)
        hbox.addWidget(self.okButton)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setGeometry(150, 150, 150, 150)
        self.setWindowTitle("COVID-19 Data Plotter")
        self.show()

    def selection_change(self, text):
        selection_options = self.codes.get_codes_for_territory_type(text)
        self.territory_dropdown.clear()
        self.territory_dropdown.addItems(list(selection_options))

    def draw_plots(self):
        self.chosen_terrain = self.territory_dropdown.currentText()
        self.chosen_territory_type = self.territory_types_dropdown.currentText()
        analyze(self.chosen_territory_type, self.chosen_terrain)


def main():
    app = QApplication(sys.argv)
    ex = CovidDataPlotter()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
