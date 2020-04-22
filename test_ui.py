from PySide2 import QtWidgets, QtCore, QtGui


class TestWidget(QtWidgets.QWidget):
    def __init__(self):
        super(TestWidget, self).__init__()

        self.setWindowTitle('Test')

        layout = QtWidgets.QVBoxLayout(self)
        self.pic_viewer = PictureViewer()

        # pour l'instant je mets juste 4 boutons à pluger comme vous voule
        self.test1 = FieldButton('test 1')
        self.test2 = FieldButton('test 2')
        self.test3 = FieldButton('test 3')
        self.test4 = FieldButton('test 4')

        layout.addWidget(self.pic_viewer)

        for test in (self.test1, self.test2, self.test3, self.test4):
            layout.addWidget(test)

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
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
