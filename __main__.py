import sys
from PySide2 import QtWidgets

import test_ui
import manager

def run():
    app = QtWidgets.QApplication(sys.argv)

    window = test_ui.TestWidget()
    browser = QtWidgets.QFileDialog()
    main_manager = manager.Manager(window, browser)
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
