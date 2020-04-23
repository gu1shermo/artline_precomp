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

BLEND_MODES = [
                  'over',
                  'multiply',
                  'screen',
                  'darker',
                  'lighter',
                  'add',
                  'subtract',
                  'difference',
                  'add (no clipping)',
                  'subtract (no clipping)'
              ]

from PySide2 import QtCore, QtGui
#from PySide2 import QtSvg

#------------------------------------------------------------------------------

def index_assert(func):
    def wrap(self, *args, **kwargs):
        index = args[0]

        if not self.layers or not len(self.layers) > index:
            raise Exception('No layer at index [{}].'.format(index))

        return func(self, *args, **kwargs)
    return wrap

#------------------------------------------------------------------------------

class Manager(QtCore.QObject):

    pixmap_updated = QtCore.Signal()

    def __init__(self):

        self.layers = []

    #--------------------------------------------------------------------------
    def test_bg(self):
        self.add_layer(BG_FILE)
        return self.get_compositing()
    #--------------------------------------------------------------------------
    def test_overlay(self):
        self.add_layer(TEST_DIFF, mask=TEST_ALPHA)
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

        bg_size = self.layers[0][0].size
        image = self.transparent_image(size=bg_size)

        for i, (layer, alpha, blend_mode) in enumerate(self.layers) or ():
            image = self.perform_operation(image, layer, alpha, blend_mode)

        return self.to_qpixmap(image)
    #--------------------------------------------------------------------------
    def perform_operation(self, base_image, overlay_image, alpha, blend_mode):
        assert blend_mode in BLEND_MODES, 'Unknown blend mode : {}'.format(blend_mode)

        base_size = base_image.size
        ol_width, ol_height = overlay_image.size
        offset = ((base_size[0] - ol_width)//2, (base_size[1] - ol_height)//2)

        if blend_mode == 'over':
            base_image.paste(overlay_image, offset, mask=alpha)
            return base_image

        else:
            work_image = self.transparent_image(size=base_size)
            work_image.paste(overlay_image, offset)
            work_image.putalpha(255)

            alpha_image = self.transparent_image(size=base_size)
            overlay_image.putalpha(alpha)
            alpha_image.paste(overlay_image, offset)
            alpha = alpha_image.split()[-1]

            if blend_mode == 'multiply':
                result = PIL.ImageChops.multiply(base_image, work_image)
            elif blend_mode == 'screen':
                result = PIL.ImageChops.screen(base_image, work_image)
            elif blend_mode == 'darker':
                result = PIL.ImageChops.darker(base_image, work_image)
            elif blend_mode == 'lighter':
                result = PIL.ImageChops.lighter(base_image, work_image)
            elif blend_mode == 'add':
                result = PIL.ImageChops.add(base_image, work_image)
            elif blend_mode == 'subtract':
                result = PIL.ImageChops.subtract(base_image, work_image)
            elif blend_mode == 'difference':
                result = PIL.ImageChops.difference(base_image, work_image)
            elif blend_mode == 'add (no clipping)':
                result = PIL.ImageChops.add_modulo(base_image, work_image)
            elif blend_mode == 'subtract (no clipping)':
                result = PIL.ImageChops.subtract_modulo(base_image, work_image)

            base_image.paste(result, (0, 0), mask=alpha)
            return base_image
    #--------------------------------------------------------------------------
    @index_assert
    def set_rgb(self, index, rgb_path):
        self.layers[index][0] = self.as_pil_image(rgb_path)
    #--------------------------------------------------------------------------
    @index_assert
    def get_rgb(self, index):
        return self.layers[index][0]
    #--------------------------------------------------------------------------
    @index_assert
    def set_alpha(self, index, alpha):
        # set alpha uniform value
        if isinstance(alpha, (int, float)):
            rgb_size = self.get_rgb(index).size
            white_image = PIL.Image.new('RGB', rgb_size, (alpha, alpha, alpha))
            self.layers[index][1] = white_image.split()[0]

        # set alpha from alpha image's red channel
        else:
            self.layers[index][1] = self.as_pil_image(alpha).split()[0]
    #--------------------------------------------------------------------------
    @index_assert
    def set_blend_mode(self, index, blend_mode):
        assert blend_mode in BLEND_MODES, 'Unknown blend mode : {}'.format(blend_mode)
        self.layers[index][2] = blend_mode
    #--------------------------------------------------------------------------
    @index_assert
    def remove_layer(self, index):
        self.layers.pop(index)
    #--------------------------------------------------------------------------
    def add_layer(self, path, mask=None, blend_mode='over'):
        if path.split('.')[-1] == 'exr':
            raise Exception('EXR not implemented yet!')

        image = self.as_pil_image(path)

        alpha = image.convert('RGBA').split()[-1] if not mask else \
                self.as_pil_image(mask).split()[0]

        self.layers.append([image, alpha, blend_mode])
    #--------------------------------------------------------------------------
    def as_pil_image(self, path):
        image = self.converted_tga(path) if path.split('.')[-1] == 'tga' else \
                self.converted_psd(path) if path.split('.')[-1] == 'psd' else \
                self.converted_svg(path) if path.split('.')[-1] == 'svg' else \
                PIL.Image.open(path)

        return image
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
    pic_manager.remove_layer(0)

if __name__ == '__main__':
    test()
