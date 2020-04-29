import sys
from PySide2.QtCore import Qt, Slot, QRect
from PySide2.QtGui import QPainter, QPixmap
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QGridLayout,
    QFileDialog,
    QSpinBox,
    QFormLayout,
)

import pictures


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        # pciture manager

        self.manager_img = pictures.Manager()
        self.layers = []

        self.btn_add_layer = QPushButton("Add layer")

        self.btn_remove_layer = QPushButton("Remove 1 layer")
        self.btn_clear = QPushButton("Clear All Layers")

        self.sbox_alpha = QSpinBox()
        self.sbox_alpha.setRange(0, 100)
        self.sbox_alpha.setValue(50)

        self.sbox_rgb = QSpinBox()
        self.sbox_rgb.setRange(0, 100)
        self.sbox_rgb.setValue(50)

        # connect buttons
        # Signals and Slots
        self.btn_add_layer.clicked.connect(self.add_layer)

        self.btn_remove_layer.clicked.connect(self.remove_layer)
        self.sbox_remove_index = QSpinBox()
        self.sbox_remove_index.setValue(0)
        self.sbox_remove_index.setRange(0, 100)
        self.sbox_remove_index.setSingleStep(1)

        self.lbl_index_remove = QLabel("index calque")

        self.btn_clear.clicked.connect(self.clear)

        self.pic_res = QLabel()

        # self.manager_img.pixmap_updated.connect(self.pic_res.setPixmap)
        self.connect_signals()

        
        # self.pic_1.setGeometry(QRect(10, 40, 500, 500))
        # self.pic_1.setGeometry(QRect(10, 540, 500, 500))
        # self.pic_1.setPixmap(pixmap)
        # self.pic_2.setPixmap(pixmap)
        # self.pic_res.setPixmap(pixmap)

        self.cbox_actions = QComboBox()
        self.cbox_definitions = QComboBox()
        self.setup_cbox()

        self.form_layout = QFormLayout()
        self.form_layout.addRow("alpha:", self.sbox_alpha)
        self.form_layout.addRow("rgb:", self.sbox_rgb)

        self.cbox_actions.currentIndexChanged.connect(self.update_blendmode)

        self.h_layout_add_layer = QHBoxLayout()
        self.h_layout_add_layer.addWidget(self.btn_add_layer)
        self.h_layout_add_layer.addWidget(self.cbox_actions)
        self.h_layout_add_layer.addWidget(self.cbox_definitions)
        self.h_layout_add_layer.addLayout(self.form_layout)

        self.h_layout_remove = QHBoxLayout()
        self.h_layout_remove.addWidget(self.btn_remove_layer)
        self.h_layout_remove.addWidget(self.lbl_index_remove)
        self.h_layout_remove.addWidget(self.sbox_remove_index)
        self.h_layout_remove.addWidget(self.btn_clear)

        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.pic_res)
        self.v_layout.addLayout(self.h_layout_add_layer)
        # self.v_layout.addLayout(self.form_layout)
        self.v_layout.addLayout(self.h_layout_remove)

        self.setLayout(self.v_layout)
    
    def connect_signals(self):
        self.manager_img.pixmap_updated.connect(self.pic_res.setPixmap)
        # self.cbox_actions.currentTextChanged.connect(self.set_overlay_blendmode)
        # self.cbox_definitions.connect(self.set_definition)

    def set_overlay_blendmode(self, blend_mode):
        self.manager_img.set_blend_mode(1, self.cbox_actions.currentText())

    def set_definition(self, str_def):
        self.manager_img.set_definition(self.cbox_definitions.currentText())

    def remove_layer(self):
        self.manager_img.remove_layer(self.sbox_remove_index.value())
        self.layers.remove(self.sbox_remove_index.value())

        # self.sbox_remove_index.setValue(self.sbox_remove_index.value() - 1)

    def clear(self):
        self.layers = []
        self.manager_img.clear()

    def update_blendmode(self):
        pass

    

    def setup_cbox(self):
        for action in pictures.BLEND_MODES:
            self.cbox_actions.addItem(action)
        for key, _ in pictures.DEFINITIONS.items():
            self.cbox_definitions.addItem(key)

    def add_layer(self):
        path_filename = QFileDialog.getOpenFileName(self, "Choose Image", "/home/",)

        # self.manager_img.set_definition(self.cbox_definitions.currentText())
        self.manager_img.add_layer(
            path_filename[0], blend_mode=self.cbox_actions.currentText()
        )

        pixmap = QPixmap(path_filename[0])
        self.pic_res.setPixmap(pixmap)

        self.layers.append(pixmap)
        # self.sbox_remove_index.setValue(self.sbox_remove_index.value() + 1)

    

        # self.view.fitInView(QRectF(0, 0, pixmap.width(), pixmap.height()), Qt.KeepAspectRatio)


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("Tutorial")

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)

        self.file_menu.addAction(exit_action)
        self.setCentralWidget(widget)

    @Slot()
    def exit_app(self, checked):
        QApplication.quit()


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    # QWidget
    widget = Widget()
    # QMainWindow using QWidget as central widget
    window = MainWindow(widget)
    window.resize(800, 600)
    window.show()

    # Execute application
    sys.exit(app.exec_())
