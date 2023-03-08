import json
import sys
from wb_ui import Ui_Form
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QStandardItemModel, QStandardItem


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.model = QStandardItemModel()
        self.ui.cb_main_menu.setModel(self.ui.model)
        self.ui.cb_category.setModel(self.ui.model)

        with open('menu.json', 'r', encoding='utf-8') as file:
            dict_main_menu = json.load(file)

        for k, v in dict_main_menu.items():
            menu = QStandardItem(k)
            self.ui.model.appendRow(menu)
            for value in v:
                sub_category = QStandardItem(value[0])
                menu.appendRow(sub_category)

        self.ui.cb_main_menu.currentIndexChanged.connect(self.updateCombo)
        self.updateCombo(0)

    def updateCombo(self, index):
        indx = self.ui.model.index(index, 0, self.ui.cb_main_menu.rootModelIndex())
        self.ui.cb_category.setRootModelIndex(indx)
        self.ui.cb_category.setCurrentIndex(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MainWindow()
    # apply_stylesheet(form, theme='light_teal.xml')
    form.show()
    sys.exit(app.exec())
