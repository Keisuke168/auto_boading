# coding:utf-8
import ui
import io
import dialogs
import photos
import clipboard
from PIL import Image
from PIL import ImageOps
from objc_util import *
import camera_scanner
import platform
import tempfile
import datetime
import os

from Pythonista_Silent_camera import muon

CIImage = ObjCClass('CIImage')
UIImage = ObjCClass('UIImage')


class BansyoCam():
    def __init__(self):
        cam = muon.camera(format='CIImage', save_to_album=False,
                          return_Image=True, auto_close=True)
        cam.launch()

        self.ci_img = cam.getData()
        corners = camera_scanner.find_corners(self.ci_img)
        self.out_img = camera_scanner.apply_perspective(corners, self.ci_img)

        uiImg = UIImage.imageWithCIImage_scale_orientation_(
            self.out_img, 1.0, 3)
        data = ObjCInstance(c.UIImageJPEGRepresentation(uiImg.ptr, 0.8))
        today = datetime.datetime.now().strftime("%Y%m%d-%H%M")
        temp_path = os.path.join(
            tempfile.gettempdir(), '{0}.{1}'.format(today, 'jpg'))
        data.writeToFile_atomically_(temp_path, True)

        self.img = Image.open(temp_path)
        #all_assets = photos.get_assets()
        #last_asset = all_assets[-1]
        #self.img = last_asset.get_image()
        self.img = self.img.convert("L")
        self.img = ImageOps.invert(self.img)
        self.miniimg = self.img.copy()
        self.miniimg = self.miniimg.resize(
            (round(self.img.width*0.2), round(self.img.height*0.2)))

    def monolize(self, i):
        self.imgmono = self.img.point(lambda x: 0 if x < i else x)
        self.imgmono = self.imgmono.point(lambda x: 255 if x >= i else x)

    def Fastmonolize(self, i):
        self.miniimgmono = self.miniimg.point(lambda x: 0 if x < i else x)
        self.miniimgmono = self.miniimgmono.point(
            lambda x: 255 if x >= i else x)

    def transpalent(self):
        temp = self.imgmono.copy()
        temp = ImageOps.invert(temp)
        self.imgmono.putalpha(temp)

    def copy(self):
        clipboard.set_image(self.imgmono)

    def saveImg(self):
        pass

    def getImg(self):
        return self.pil2ui(self.imgmono)

    def getminiImg(self):
        return self.pil2ui(self.miniimgmono)

    def pil2ui(self, imgIn):
        with io.BytesIO() as bIO:
            imgIn.save(bIO, 'PNG')
            imgOut = ui.Image.from_data(bIO.getvalue())
        del bIO
        return imgOut


class myview(ui.View):
    def __init__(self):
        self.background_color = 'white'
        self.height = ui.get_screen_size()[1]
        self.width = ui.get_screen_size()[0]

        if 'iPad' in platform.machine():  # overwrite
            self.height = ui.get_screen_size()[1]/1.3
            self.width = ui.get_screen_size()[0]/1.5

        self.min = 80
        self.max = 130
        self.i = (self.min+self.max)/2

        self.bbimg = BansyoCam()
        self.bbimg.monolize(self.i)
        self.bbimg.Fastmonolize(self.i)

        self.imageView = ui.ImageView()
        self.imageView.width = self.width
        self.imageView.center = (self.width * 0.5, self.height * 0.3)
        self.imageView.flex = 'WHB'
        self.imageView.image = self.bbimg.getImg()
        self.imageView.content_mode = ui.CONTENT_SCALE_ASPECT_FILL

        self.sliderView = ui.Slider()
        self.sliderView.width = self.width*0.8
        self.sliderView.center = (self.width * 0.5, self.height * 0.75)
        self.sliderView.flex = 'WT'
        self.sliderView.value = 0.5
        self.sliderView.action = self.sliderAction

        self.button = ui.Button(title='Complete')
        self.button.flex = 'WT'
        self.button.width = self.width*0.2
        self.button.center = (self.width * 0.5, self.height * 0.65)
        self.button.action = self.button_tapped

        self.textfield1 = ui.TextField()
        self.textfield1.width = self.width * 0.15
        self.textfield1.height = 36
        self.textfield1.center = (self.width*0.1, self.height*0.05)
        self.textfield1.text = str(self.min)
        self.textfield1.keyboard_type = ui.KEYBOARD_NUMBERS
        self.textfield1.action = self.textfield1_edit

        self.textfield2 = ui.TextField()
        self.textfield2.width = self.width * 0.15
        self.textfield2.height = 36
        self.textfield2.center = (self.width*0.9, self.height*0.05)
        self.textfield2.text = str(self.max)
        self.textfield2.keyboard_type = ui.KEYBOARD_NUMBERS
        self.textfield2.action = self.textfield2_edit

        self.label = ui.Label()
        self.label.width = self.width*0.2
        self.label.height = 36
        self.label.center = (self.width*0.57, self.height*0.05)
        self.label.text = str(self.i)

        if 'iPad' in platform.machine():  # overwrite
            self.imageView.center = (self.width * 0.5, self.height * 0.42)
            self.sliderView.center = (self.width * 0.5, self.height * 0.75)
            self.button.center = (self.width * 0.5, self.height * 0.87)
            self.textfield1.center = (self.width*0.1, self.height*0.70)
            self.textfield2.center = (self.width*0.9, self.height*0.70)

        self.add_subview(self.imageView)
        self.add_subview(self.sliderView)
        self.add_subview(self.button)
        # self.add_subview(self.button2)
        self.add_subview(self.textfield1)
        self.add_subview(self.textfield2)
        self.add_subview(self.label)

    def sliderAction(self, sender):
        self.i = sender.value * (self.max - self.min) + self.min
        self.bbimg.Fastmonolize(self.i)
        # print(self.i)
        self.draw()

    def button_tapped(self, sender):
        self.bbimg.monolize(self.i)
        self.bbimg.transpalent()
        self.bbimg.copy()
        ok = ui.Button(title='OK')

        dialogs.alert('Copied!', '', 'OK', hide_cancel_button=True)
        self.close()

    def change_value(self):
        if self.i >= self.max:
            self.sliderView.value = 1.0
        elif self.i <= self.min:
            self.sliderView.value = 0.0
        else:
            self.sliderView.value = (self.i - self.min)/(self.max - self.min)

    def textfield1_edit(self, sender):
        self.min = int(self.textfield1.text)
        self.change_value()

    def textfield2_edit(self, sender):
        self.max = int(self.textfield2.text)
        self.change_value()

    def draw(self):
        self.imageView.image = self.bbimg.getminiImg()
        self.label.text = str(self.i)

# self.imageView.image.resizable_image(10,10,240,200)


v = myview()
v.present('sheet')
