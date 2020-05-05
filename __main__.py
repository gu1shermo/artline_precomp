import sys
from PySide2 import QtWidgets
import ui_fusion



def run():
        # Qt Application
    app = QtWidgets.QApplication(sys.argv)
    # QWidget
    widget = ui_fusion.Widget()
    # QMainWindow using QWidget as central widget
    window = ui_fusion.MainWindow(widget)
    window.resize(800, 600)
    window.show()

    # Execute application
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
