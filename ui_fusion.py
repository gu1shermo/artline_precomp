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
)
from PySide2.QtCharts import QtCharts
import pictures


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        # pciture manager



        self.manager_img = pictures.Manager()

        self.btn_load_img_1 = QPushButton("Load img1")
        self.btn_load_img_2 = QPushButton("load img2")
        self.btn_run = QPushButton("Run")

        # connect buttons
        # Signals and Slots
        self.btn_load_img_1.clicked.connect(self.load_img_1)
        self.btn_load_img_2.clicked.connect(self.load_img_2)
        self.btn_run.clicked.connect(self.run_action)
        
        self.pic_1 = QLabel()
        self.pic_2 = QLabel()
        self.pic_res = QLabel()
        
        # self.pic_1.setGeometry(QRect(10, 40, 500, 500))
        # self.pic_1.setGeometry(QRect(10, 540, 500, 500))
        # self.pic_1.setPixmap(pixmap)
        # self.pic_2.setPixmap(pixmap)
        # self.pic_res.setPixmap(pixmap)

        self.cbox_actions = QComboBox()
        self.cbox_definitions = QComboBox()
        self.setup_cbox()

        self.cbox_actions.currentIndexChanged.connect(self.update_blendmode)

        self.path = QLineEdit()

        self.grid = QGridLayout()
        self.v_layout = QVBoxLayout()

        self.v_layout.addWidget(self.btn_load_img_1)
        self.v_layout.addWidget(self.btn_load_img_2)
        self.v_layout.addWidget(self.cbox_actions)
        self.v_layout.addWidget(self.cbox_definitions)
        self.v_layout.addWidget(self.path)
        self.v_layout.addWidget(self.btn_run)
        self.grid.addWidget(self.pic_1, 0, 0)
        self.grid.addWidget(self.pic_2, 0, 1)
        self.grid.addLayout(self.v_layout, 1, 0)
        self.grid.addWidget(self.pic_res, 1, 1)

        self.setLayout(self.grid)

    def update_blendmode(self):
        pass

    def run_action(self):
        all_items = [self.cbox_actions.itemText(i) for i in range(self.cbox_actions.count())]
        item_selected = self.cbox_actions.currentText()
        print(all_items)
        print(item_selected)
        self.manager_img.set_blend_mode(self.current_layer, item_selected)
        
        
        
        



    def setup_cbox(self):
        for action in pictures.BLEND_MODES:
            self.cbox_actions.addItem(action)
        for key, _ in pictures.DEFINITIONS.items():
            self.cbox_definitions.addItem(key)
        

    def load_img_1(self):
        path_filename = QFileDialog.getOpenFileName(self, "Choose Image", "/home/",)
        self.load_image(path_filename, self.pic_1)
        self.manager_img.add_layer(path_filename)

    def load_img_2(self):
        path_filename = QFileDialog.getOpenFileName(
            self,
            "Choose Image",
            "/home/",
            "Image Files (*.png *.jpg *.bmp *.tga *.jpeg)",
        )
        self.load_image(path_filename, self.pic_2)
        self.manager_img.add_layer(path_filename)

    def load_image(self, image_path, label):

        pixmap = QPixmap(image_path[0])
        label.setPixmap(pixmap)

        print(pixmap)

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
