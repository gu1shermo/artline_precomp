from PySide2 import QtWidgets, QtCore, QtGui

import test_ui
import pictures


class TestManager(object):
    def __init__(self, window):

        self.window = window
        self.pic_manager = pictures.Manager()

        self.connect_signals()
        self.pic_manager.show_test_files()

    def connect_signals(self):
        self.pic_manager.pixmap_updated.connect(self.window.show_pixmap)
        self.window.fusion_box.currentTextChanged.connect(self.set_overlay_blendmode)
        self.window.definition_box.currentTextChanged.connect(self.set_definition)

    def set_overlay_blendmode(self, blend_mode):
        self.pic_manager.set_blend_mode(1, blend_mode)

    def set_definition(self, str_def):
        self.pic_manager.set_definition(str_def)


class TestWidget(QtWidgets.QWidget):
    def __init__(self):
        super(TestWidget, self).__init__()

        self.setWindowTitle('Test')

        layout = QtWidgets.QVBoxLayout(self)

        self.pic_viewer = test_ui.PictureViewer()
        self.fusion_box = QtWidgets.QComboBox()
        self.definition_box = QtWidgets.QComboBox()

        for blend_mode in pictures.BLEND_MODES:
            self.fusion_box.addItem(blend_mode)
        for definition in pictures.DEFINITIONS:
            self.definition_box.addItem(definition)

        layout.addWidget(self.pic_viewer)
        layout.addWidget(self.fusion_box)
        layout.addWidget(self.definition_box)
        layout.addStretch(1)

    def show_pixmap(self, pixmap):
        if not pixmap:
            self.pic_viewer.setPixmap(None)
            return

        # resize to fit label width, keeping pixmap ratio
        resized_pix = pixmap.scaled(self.pic_viewer.width(),
                                    self.pic_viewer.width(),
                                    QtCore.Qt.KeepAspectRatio,
                                    QtCore.Qt.SmoothTransformation)

        self.pic_viewer.setPixmap(resized_pix)


def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    window = TestWidget()
    test = TestManager(window)
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
