from PySide2 import QtWidgets, QtCore, QtGui

import test_ui
import pictures


class TestManager(object):
    def __init__(self, window):

        self.window = window
        self.pic_manager = pictures.Manager()

        self.pic_manager.test_bg()
        pixmap = self.pic_manager.test_overlay()
        self.window.show_pixmap(pixmap)

        self.connect_signals()

    def connect_signals(self):
        # selon les tests
        self.window.fusion_box.currentTextChanged.connect(self.set_overlay_blendmode)

    def set_overlay_blendmode(self, blend_mode):
        self.pic_manager.set_blend_mode(1, blend_mode)
        pixmap = self.pic_manager.get_compositing()
        self.window.show_pixmap(pixmap)

class TestWidget(QtWidgets.QWidget):
    def __init__(self):
        super(TestWidget, self).__init__()

        self.setWindowTitle('Test')

        layout = QtWidgets.QVBoxLayout(self)
        self.pic_viewer = test_ui.PictureViewer()

        # pour l'instant je mets juste 4 boutons à pluger comme vous voule
        self.fusion_box = QtWidgets.QComboBox()

        layout.addWidget(self.pic_viewer)
        layout.addWidget(self.fusion_box)
        layout.addStretch(1)

        for blend_mode in pictures.BLEND_MODES:
            self.fusion_box.addItem(blend_mode)

    def show_pixmap(self, pixmap):
        if not pixmap:
            self.pic_viewer.setPixmap(None)
            return

        resized_pix = pixmap.scaled(self.pic_viewer.width(), self.pic_viewer.width(),
                                    QtCore.Qt.KeepAspectRatio,
                                    QtCore.Qt.SmoothTransformation)

        self.pic_viewer.setPixmap(resized_pix)


class FieldButton(QtWidgets.QWidget):

    clicked = QtCore.Signal()
    returnPressed = QtCore.Signal()

    def __init__(self, name):
        super(FieldButton, self).__init__()

        layout = QtWidgets.QHBoxLayout(self)

        self.field = QtWidgets.QLineEdit(placeholderText='enter text for {}'.format(name))
        self.button = QtWidgets.QPushButton(name)

        layout.addWidget(self.field)
        layout.addWidget(self.button)

        # propagate signals
        self.button.clicked.connect(self.clicked.emit)
        self.field.returnPressed.connect(self.returnPressed.emit)


class PictureViewer(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super(PictureViewer, self).__init__(*args, **kwargs)

    def paintEvent(self, event):
        if not self.pixmap():
            rect = event.rect()
            painter = QtGui.QPainter(self)
            painter.setPen(QtCore.Qt.white)
            painter.fillRect(rect, QtCore.Qt.black)
            painter.drawText(rect, QtCore.Qt.AlignCenter, 'No picture.')

        else:
            # paint as usual
            super(PictureViewer, self).paintEvent(event)


def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    window = TestWidget()
    test = TestManager(window)
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
