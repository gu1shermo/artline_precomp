import pictures


class Manager(object):
    def __init__(self, window):

        self.window = window
        self.pic_manager = pictures.Manager()

        self.connect_signals()

    def connect_signals(self):
        # selon les tests
        self.window.test1.clicked.connect(self.show_bg)
        self.window.test2.clicked.connect(self.add_layer_test)
        self.window.test3.clicked.connect(self.clear_test)
        self.pic_manager.pixmap_updated.connect(self.window.show_pixmap)

    def show_bg(self):
        pixmap = self.pic_manager.test_bg()

    def add_layer_test(self):
        pixmap = self.pic_manager.test_overlay()

    def clear_test(self):
        self.pic_manager.clear()
