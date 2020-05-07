import PIL
import PIL.ImageQt
import PIL.TgaImagePlugin
#from psd_tools import PSDImage
# import OpenEXR

import os

ICONS_ROOT = os.path.dirname(__file__).replace('\\', '/') +'/icons/'
BG_FILE = ICONS_ROOT +'gotham_city.png'
TEST_FULL = ICONS_ROOT +'why_serious_with_alpha.png'
TEST_DIFF = ICONS_ROOT +'why_serious_diffuse.png'
TEST_ALPHA = ICONS_ROOT +'why_serious_alpha.png'
TGA_FILE = ICONS_ROOT +'ep01_sc01_compo.002.tga'

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

DEFINITIONS = {
                  '1:1': 1,
                  '1/2': 0.5,
                  '1/4': 0.25,
                  '1/8': 0.125
              }

from PySide2 import QtCore, QtGui
#from PySide2 import QtSvg

#------------------------------------------------------------------------------

def index_assert(func):
    """
    Simple decorator that raise error if index is not found into Manager.layers.
    """

    def wrap(self, *args, **kwargs):
        index = args[0]

        if not self.layers or not len(self.layers) > index:
            raise Exception('No layer at index [{}].'.format(index))

        return func(self, *args, **kwargs)
    return wrap

#------------------------------------------------------------------------------

class Manager(QtCore.QObject):
    """
    Pictures reading and operations handler.
    """

    pixmap_updated = QtCore.Signal(object)

    def __init__(self):
        super(Manager, self).__init__()

        self.layers = []
        self.buffer = Buffer()
        self.definition = 1

    #--------------------------------------------------------------------------
    #------------------------------ TEST FUNCTIONS ----------------------------
    def show_test_files(self):
        self.test_bg()
        self.test_overlay()
    #--------------------------------------------------------------------------
    def test_bg(self):
        self.add_layer(BG_FILE)
    #--------------------------------------------------------------------------
    def test_overlay(self):
        self.add_layer(TEST_DIFF, mask=TEST_ALPHA)
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    def uniform(self, size=(1920, 1080), mode='RGBA', rgba=(0, 0, 0, 0)):
        """
        Create uniform PIL image. By default, values will be set on 0, so a default
        RGB image will be full black, and a default RGBA one will be full-transparent.
        """

        value = rgba[0]  if mode == 'L' and isinstance(rgba, (tuple, list)) else \
                rgba[:3] if mode == 'RGB' else \
                rgba

        return PIL.Image.new(mode, size, value)
    #--------------------------------------------------------------------------
    def process_image(self):
        """ Get compositing from self.layers and emit result into pixmap_updated signal. """
        pixmap = self.get_compositing()
        self.pixmap_updated.emit(pixmap)
    #--------------------------------------------------------------------------
    def get_compositing(self):
        """
        Get composed layers as QtGui.QPixmap instance.
        """

        if not self.layers:
            return None

        bg_size = self.layers[0][0].size
        # apply display definition value
        bg_size = self.multiplied_size(bg_size, self.definition)
        # create background as uniform image that will receive all the layers
        image = self.uniform(size=bg_size)

        for i, (layer, alpha, blend_mode) in enumerate(self.layers) or ():
            if i == 0:
                blend_mode = 'over'     # no blend operation for first layer
            image = self.perform_operation(image, layer, alpha, blend_mode)

        return self.to_qpixmap(image)
    #--------------------------------------------------------------------------
    def multiplied_size(self, size, factor):
        return int(size[0] * factor), int(size[1] * factor)
    #--------------------------------------------------------------------------
    def center_offset(self, image, base_image):
        """ Get offset value for paste <image> to be centered on <base_image>. """

        return ((base_image.size[0] - image.size[0])//2,
                (base_image.size[1] - image.size[1])//2)
    #--------------------------------------------------------------------------
    def centered_paste(self, pasted_image, base_image, **kwargs):
        """ Return the result of centered <pasted_image> over <base_image>. """

        # make sure mask is dimensionned on <pasted_image> if set into kwargs
        if kwargs and 'mask' in kwargs:
            kwargs['mask'] = self.cropped(kwargs['mask'], pasted_image.size)

        base_image.paste(
                            pasted_image,
                            self.center_offset(pasted_image, base_image),
                            **kwargs
                        )

        return base_image
    #--------------------------------------------------------------------------
    def cropped(self, image, target_size):
        """ Set <image> dimensions to <target_size>. If <image> was too small,
        borders will be added, with default values from self.uniform(). """

        if image.size == target_size:
            return image

        default_image = self.uniform(size=target_size, mode=image.mode)
        return self.centered_paste(image, default_image)
    #--------------------------------------------------------------------------
    def conform_to_definition(self, image):
        """ Return resized image (no operation on <image> performed, self.layers
        remains intact) with display definition factor. """

        if self.definition == 1:
            return image

        new_size = self.multiplied_size(image.size, self.definition)
        resized_image = image.resize(new_size, PIL.Image.ANTIALIAS)

        return resized_image
    #--------------------------------------------------------------------------
    def perform_operation(self, base_image, overlay_image, alpha, blend_mode):
        """ Append <overlay_image> on <base_image> with <alpha> as mask,
        depending on <blend_mode>. """

        assert blend_mode in BLEND_MODES, 'Unknown blend mode : {}'.format(blend_mode)

        overlay_image  = self.conform_to_definition(overlay_image)
        alpha          = self.conform_to_definition(alpha)

        if blend_mode == 'over':
            return self.centered_paste(overlay_image, base_image, mask=alpha)

        else:
            # create a full-opacity work image for PIL operation (result will
            # then be pasted on the <base_image> with <alpha> as mask)
            work_image = self.cropped(overlay_image, base_image.size)
            work_image.putalpha(255)

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

            # make sure mask has the same diemnsions as the result image
            mask = self.cropped(alpha, base_image.size)

            # paste result on <base_image>
            base_image.paste(result, (0, 0), mask=mask)

            return base_image
    #--------------------------------------------------------------------------
    @index_assert
    def set_rgb(self, index, rgb_path):
        """ Set RGB map for layer at specified index. """

        self.layers[index][0] = self.as_pil_image(rgb_path)
        self.process_image()
    #--------------------------------------------------------------------------
    @index_assert
    def get_rgb(self, index):
        """ Get RGB map from layer at specified index. """

        return self.layers[index][0]
    #--------------------------------------------------------------------------
    @index_assert
    def set_alpha(self, index, alpha):
        """ Set alpha map for layer at specified index. """

        # set alpha uniform value
        if isinstance(alpha, (int, float)):
            rgb_size = self.get_rgb(index).size
            self.layers[index][1] = self.uniform(size=rgb_size, mode='L', rgba=255)

        # set alpha from alpha image's red channel
        else:
            self.layers[index][1] = self.as_pil_image(alpha).split()[0]

        self.process_image()
    #--------------------------------------------------------------------------
    @index_assert
    def set_blend_mode(self, index, blend_mode):
        """ Set blend mode for layer at specified index (ignored in display for
        the first layer). """

        assert blend_mode in BLEND_MODES, 'Unknown blend mode : {}'.format(blend_mode)

        self.layers[index][2] = blend_mode

        if index > 0:
            self.process_image()
    #--------------------------------------------------------------------------
    @index_assert
    def remove_layer(self, index):
        self.layers.pop(index)
        self.process_image()
    #--------------------------------------------------------------------------
    def clear(self):
        self.layers = []
        self.process_image()
    #--------------------------------------------------------------------------
    def set_definition(self, str_def):
        """ Set display definition. """

        assert str_def in DEFINITIONS, 'Unknown definition : {}'.format(str_def)

        self.definition = DEFINITIONS[str_def]
        self.process_image()
    #--------------------------------------------------------------------------
    def add_layer(self, path, mask=None, blend_mode='over'):
        """ Add new layer to compositing. """

        if path.split('.')[-1] == 'exr':
            raise Exception('EXR not implemented yet!')

        image = self.as_pil_image(path)
        alpha = image.convert('RGBA').split()[-1] if not mask else \
                self.as_pil_image(mask).split()[0]

        self.layers.append([image, alpha, blend_mode])

        self.process_image()
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

        w = renderer.defaultSize().width()
        h = renderer.defaultSize().height()

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

class Buffer(object):
    """
    In case we need to store image calculations that would take long to perform?
    For instance, OpenExr files may take a while to be calculated, so sequence
    reading may be hard to achieve without a buffer system...
    """

    def __init__(self):

        self.buffered_images = {}       # model : {<path> : <PIL.image instance>}

    #--------------------------------------------------------------------------
    def get(self, path):
        if path in self.buffered_images:
            return self.buffered_images[path]
    #--------------------------------------------------------------------------
    def add(self, path, image):
        self.buffered_images[path] = image
    #--------------------------------------------------------------------------
    def clear(self):
        self.buffered_images = {}

#------------------------------------------------------------------------------

def test():
    pic_manager = Manager()
    pic_manager.remove_layer(0)

if __name__ == '__main__':
    test()
