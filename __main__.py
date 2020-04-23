import sys
from PySide2 import QtWidgets

import test_ui
import fusion_mode_ui
import manager

def run():
    app = QtWidgets.QApplication(sys.argv)

    window1 = test_ui.TestWidget()
    test_manager1 = manager.Manager(window1)
    window1.show()

    window2 = fusion_mode_ui.TestWidget()
    test_manager2 = fusion_mode_ui.TestManager(window2)
    window2.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
