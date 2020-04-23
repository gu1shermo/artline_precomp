import PIL
import PIL.ImageQt              # is needed for .exe version to find it
import PIL.TgaImagePlugin       # is needed for .exe version to find it
from psd_tools import PSDImage
# import OpenEXR

import os

ICONS_ROOT = os.path.dirname(__file__).replace('\\', '/') +'/icons/'
BG_FILE = ICONS_ROOT +'gotham_city.png'
TEST_FULL = ICONS_ROOT +'why_serious_with_alpha.png'
TEST_DIFF = ICONS_ROOT +'why_serious_diffuse.png'
TEST_ALPHA = ICONS_ROOT +'why_serious_alpha.png'
TGA_ICON = ICONS_ROOT +'ep01_sc01_compo.002.tga'

from PySide2 import QtCore, QtGui, QtSvg

#------------------------------------------------------------------------------

class Manager(object):

    def __init__(self):

        self.layers = []

    #--------------------------------------------------------------------------
    def test_bg(self):
        self.add_layer(BG_FILE)
        return self.get_compositing()
    #--------------------------------------------------------------------------
    def test_overlay(self):
        self.add_layer(TEST_FULL)
        return self.get_compositing()

    #--------------------------------------------------------------------------
    def transparent_image(self, size=(1920, 1080)):
        return PIL.Image.new('RGBA', size, (0, 0, 0, 0))
    #--------------------------------------------------------------------------
    def get_compositing(self):
        """
        Get composed layers as QtGui.QPixmap instance.
        """

        if not self.layers:
            return None

        # take base layer's size for compositing
        bg_size = self.layers[0].size
        image = self.transparent_image(size=bg_size)

        for layer in self.layers or ():
            # get offset for layer centering
            layer_w, layer_h = layer.size
            offset = ((bg_size[0] - layer_w)//2, (bg_size[1] - layer_h)//2)

            # for now, just get the alpha from layer
            alpha = layer.convert('RGBA').split()[-1]

            image.paste(layer, offset, mask=alpha)

        return self.to_qpixmap(image)
    #--------------------------------------------------------------------------
    def add_layer(self, path):
        if path.split('.')[-1] == 'exr':
            raise Exception('EXR not implemented yet!')

        image = self.converted_tga(path) if path.split('.')[-1] == 'tga' else \
                self.converted_psd(path) if path.split('.')[-1] == 'psd' else \
                self.converted_svg(path) if path.split('.')[-1] == 'svg' else \
                PIL.Image.open(path)

        self.layers.append(image)
    #--------------------------------------------------------------------------
    def converted_tga(self, path):
        pil_image = PIL.Image.open(path).convert('RGB')
        return pil_image
    #--------------------------------------------------------------------------
    def converted_psd(self, path):
        psd = PSDImage.open(path)
        pil_image = psd.topil().convert('RGB')
        return pil_image
    #--------------------------------------------------------------------------
    def converted_svg(self, path):
        renderer = QtSvg.QSvgRenderer(path)

        width = renderer.defaultSize().width()
        height = renderer.defaultSize().height()

        # create empty QIcon with svg file's dimensions
        image = QtGui.QImage(w, h, QtGui.QImage.Format_ARGB32)
        image.fill(QtCore.Qt.transparent)
        # paint svg content
        painter = QtGui.QPainter(image)
        renderer.render(painter)
        painter.end()

        return image
    #--------------------------------------------------------------------------
    def to_qpixmap(self, pil_image):
        qt_image = PIL.ImageQt.ImageQt(pil_image)
        return QtGui.QPixmap.fromImage(qt_image)
#------------------------------------------------------------------------------

def test():
    pic_manager = Manager()
    print (pic_manager.converted_tga(TGA_ICON))

if __name__ == '__main__':
    test()
