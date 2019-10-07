# coding:utf-8
import ui
import io
import photos
import clipboard
from PIL import Image
from PIL import ImageOps


class BBCam():
    def __init__(self):
        self.img = photos.capture_image()
        #all_assets = photos.get_assets()
        #last_asset = all_assets[-1]
        #self.img = last_asset.get_image()
        self.img = self.img.convert("L")
        self.img = ImageOps.invert(self.img)

    def monolize(self, i):
        self.imgmono = self.img.point(lambda x: 0 if x < i else x)
        self.imgmono = self.imgmono.point(lambda x: 255 if x >= i else x)

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

    def pil2ui(self, imgIn):
        with io.BytesIO() as bIO:
            imgIn.save(bIO, 'PNG')
            imgOut = ui.Image.from_data(bIO.getvalue())
        del bIO
        return imgOut


class myview(ui.View):
    def __init__(self):
        self.background_color = 'white'
        self.height = ui.get_screen_size()[1]/2
        self.width = ui.get_screen_size()[0]/2

        self.i = 150

        self.bbimg = BBCam()
        self.bbimg.monolize(self.i)

        self.imageView = ui.ImageView()
        self.imageView.width = self.width
        self.imageView.center = (self.width * 0.5, self.height * 0.3)
        self.imageView.flex = 'WHB'
        self.imageView.image = self.bbimg.getImg()
        self.imageView.content_mode = ui.CONTENT_SCALE_ASPECT_FILL

        # self.imageView.width=self.width*0.9

        self.sliderView = ui.Slider()
        self.sliderView.width = self.width*0.8
        self.sliderView.center = (self.width * 0.5, self.height * 0.8)
        self.sliderView.flex = 'WT'
        self.sliderView.value = 0.5
        self.sliderView.continuous = False
        self.sliderView.action = self.sliderAction

        self.button = ui.Button(title='Complete')
        self.button.width = self.width*0.2
        self.button.center = (self.width * 0.5, self.height * 0.85)
        self.button.action = self.button_tapped

        self.add_subview(self.imageView)
        self.add_subview(self.sliderView)
        self.add_subview(self.button)

    def sliderAction(self, sender):
        self.i = sender.value * 40 + 130
        self.bbimg.monolize(self.i)
        print(self.i)
        self.draw()

    def button_tapped(self, sender):
        self.bbimg.transpalent()
        self.bbimg.copy()
        self.close()

    def draw(self):
        self.imageView.image = self.bbimg.getImg()


v = myview()
v.present('sheet')
