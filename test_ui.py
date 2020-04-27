from PySide2 import QtWidgets, QtCore, QtGui

class FieldButton(QtWidgets.QWidget):

    clicked = QtCore.Signal()
    returnPressed = QtCore.Signal()
    deleted = QtCore.Signal(str)

    def __init__(self, name, parent=None):
        super(FieldButton, self).__init__()

        self.layout = QtWidgets.QHBoxLayout(self)

        self.field = QtWidgets.QLineEdit(placeholderText='enter text for {}'.format(name))
        self.showButton = QtWidgets.QPushButton(name)
        self.removeButton = QtWidgets.QPushButton("-")

        self.layout.addWidget(self.field)
        self.layout.addWidget(self.showButton)
        self.layout.addWidget(self.removeButton)

        # propagate signals
        self.showButton.clicked.connect(self.clicked.emit)
        self.removeButton.clicked.connect(self.removePicture)

    def removePicture(self):

        # Signal pour aussi delete l'image dans le pic_manager
        self.deleted.emit(self.field.text())
        self.deleteLater()


class TestWidget(QtWidgets.QWidget):
    added = QtCore.Signal(FieldButton)

    def __init__(self):
        super(TestWidget, self).__init__()

        self.setWindowTitle('Test')

        self.layout = QtWidgets.QVBoxLayout(self)
        self.pic_viewer = PictureViewer()

        # pour l'instant je mets juste 4 boutons à pluger comme vous voulez
        self.test1 = FieldButton('test 1')
        self.test2 = FieldButton('test 2')
        self.test3 = FieldButton('test 3')
        self.fileBrowser = FieldButton('Browse...')
        self.addFile = QtWidgets.QPushButton("+")

        self.addFile.clicked.connect(self.add_fieldButton)

        self.layout.addWidget(self.pic_viewer)

        for widget in (self.test1, self.test2, self.test3, self.fileBrowser, self.addFile):
            self.layout.addWidget(widget)


    def add_fieldButton(self):
        new_widget = FieldButton('Browse...')

        self.layout.addWidget(new_widget)
        self.layout.insertWidget(self.layout.count(), self.addFile)
        self.added.emit(new_widget)


    def show_pixmap(self, pixmap):
        if not pixmap:
            self.pic_viewer.setPixmap(None)
            return

        resized_pix = pixmap.scaled(self.pic_viewer.width(), self.pic_viewer.width(),
                                    QtCore.Qt.KeepAspectRatio,
                                    QtCore.Qt.SmoothTransformation)

        self.pic_viewer.setPixmap(resized_pix)




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
