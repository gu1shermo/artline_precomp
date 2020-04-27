import pictures
from os.path import expanduser
from PySide2 import QtCore
from test_ui import FieldButton


class Manager(object):
    def __init__(self, window, browser):

        self.window = window
        self.browser = browser
        self.pic_manager = pictures.Manager()

        self.connect_signals()

    def connect_signals(self):
        # selon les tests
        self.window.test1.clicked.connect(self.show_bg)
        self.window.test2.clicked.connect(self.add_layer_test)
        self.window.test3.clicked.connect(self.clear_test)
        self.window.fileBrowser.clicked.connect(self.browseFiles)
        self.window.fileBrowser.deleted.connect(self.del_layer)
        self.window.added.connect(self.added_layer_widget)

    def show_bg(self):
        pixmap = self.pic_manager.test_bg()
        self.window.show_pixmap(pixmap)

    def add_layer_test(self):
        pixmap = self.pic_manager.test_overlay()
        self.window.show_pixmap(pixmap)

    def clear_test(self):
        self.window.show_pixmap(None)

    def browseFiles(self):
        fileName = self.browser.getOpenFileName(
            caption = "Open Image",
            dir = expanduser('~/Pictures'),
            filter = "Image Files (*.png *.jpg *.bmp)"
        )
        self.window.fileBrowser.field.setText (fileName[0])
        self.pic_manager.add_layer(self.window.fileBrowser.field.text())

    @QtCore.Slot(FieldButton)
    def added_layer_widget(self, widget):
        # Connexion des signaux du FieldButton aux slots correspondants
        widget.clicked.connect(self.browseFiles)
        widget.deleted.connect(self.del_layer)

    @QtCore.Slot(str)
    def del_layer(self, field):
        print ("Deleted layer : {}".format(field))

        # TO DO : Enlever le layer avec l'image correspondante.
        # :field est un path absolu