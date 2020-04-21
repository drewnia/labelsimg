import sys

import cv2 as cv
import numpy as np


class App():
    BLUE = [255, 0, 0]  # rectangle color
    RED = [0, 0, 255]  # PR BG
    GREEN = [0, 255, 0]  # PR FG
    BLACK = [0, 0, 0]  # sure BG
    WHITE = [255, 255, 255]  # sure FG

    DRAW_BG = {'color': BLACK, 'val': 0}
    DRAW_FG = {'color': WHITE, 'val': 1}
    DRAW_PR_BG = {'color': RED, 'val': 2}
    DRAW_PR_FG = {'color': GREEN, 'val': 3}

    # setting up flags
    rect = (0, 0, 1, 1)
    drawing = False  # flag for drawing curvesqa
    rectangle = False  # flag for drawing rect
    rect_over = False  # flag to check if rect drawn
    rect_or_mask = 100  # flag for selecting rect or mask mode
    value = DRAW_FG  # drawing initialized to FG
    thickness = 3  # brush thickness

    classes = {'Kritiy_Vagon': 40, 'Poluvagon': 70, 'Transporter': 100, 'Tsisterna': 130, 'Lokomotiv': 160,
               'Hopper': 190, 'Else': 220}
    counter = 0

    def onmouse(self, event, x, y, flags, param):
        if not self.rect_over:
            # Draw Rectangle
            if event == cv.EVENT_LBUTTONDOWN:
                self.rectangle = True
                self.ix, self.iy = x, y

            elif event == cv.EVENT_MOUSEMOVE:
                if self.rectangle == True:
                    self.img = self.img2.copy()
                    cv.rectangle(self.img, (self.ix, self.iy), (x, y), self.BLUE, 2)
                    self.rect = (min(self.ix, x), min(self.iy, y), abs(self.ix - x), abs(self.iy - y))
                    self.rect_or_mask = 0

            elif event == cv.EVENT_LBUTTONUP:
                self.rectangle = False
                self.rect_over = True
                cv.rectangle(self.img, (self.ix, self.iy), (x, y), self.BLUE, 2)
                self.rect = (min(self.ix, x), min(self.iy, y), abs(self.ix - x), abs(self.iy - y))
                self.rect_or_mask = 0
                print(" Now press the key 'n' a few times until no further change \n")

        # draw touchup curves
        else:
            if event == cv.EVENT_LBUTTONDOWN or event == cv.EVENT_RBUTTONDOWN:
                if event == cv.EVENT_LBUTTONDOWN:
                    self.value = self.DRAW_FG
                else:
                    self.value = self.DRAW_BG

                self.drawing = True
                cv.circle(self.img, (x, y), self.thickness, self.value['color'], -1)
                cv.circle(self.mask, (x, y), self.thickness, self.value['val'], -1)

            elif event == cv.EVENT_MOUSEMOVE:
                if self.drawing:
                    cv.circle(self.img, (x, y), self.thickness, self.value['color'], -1)
                    cv.circle(self.mask, (x, y), self.thickness, self.value['val'], -1)

            elif event == cv.EVENT_LBUTTONUP or event == cv.EVENT_RBUTTONUP:
                if self.drawing:
                    if event == cv.EVENT_LBUTTONUP:
                        self.value = self.DRAW_FG
                    else:
                        self.value = self.DRAW_BG
                    self.drawing = False
                    cv.circle(self.img, (x, y), self.thickness, self.value['color'], -1)
                    cv.circle(self.mask, (x, y), self.thickness, self.value['val'], -1)

    def run(self):
        # Loading images
        if len(sys.argv) == 2:
            filename = sys.argv[1]  # for drawing purposes
        else:
            print("No input image given, so loading default image, im.jpg \n")
            print("Correct Usage: python grabcut.py <filename> \n")
            filename = 'im.jpg'

        self.img = cv.imread(cv.samples.findFile(filename))
        self.orig_img = self.img
        self.img = cv.resize(self.img, (1200, 700))
        self.img2 = self.img.copy()  # a copy of original image
        self.mask = np.zeros(self.img.shape[:2], dtype=np.uint8)  # mask initialized to PR_BG
        self.output = np.zeros(self.img.shape, np.uint8)  # output image to be shown

        # input and output windows
        cv.namedWindow('output')
        cv.namedWindow('input')
        cv.setMouseCallback('input', self.onmouse)
        # cv.moveWindow('input', self.img.shape[0], self.img.shape[1]-60)

        print(" Instructions: \n")
        print(" Draw a rectangle around the object using left mouse button \n")

        while (1):

            cv.imshow('output', self.output)
            cv.imshow('input', self.img)
            k = cv.waitKey(1)

            # key bindings
            if k == 27:  # esc to exit
                break
            # elif k == ord('0'):  # BG drawing
            #     print(" mark background regions with left mouse button \n")
            #     self.value = self.DRAW_BG
            # elif k == ord('1'):  # FG drawing
            #     print(" mark foreground regions with left mouse button \n")
            #     self.value = self.DRAW_FG
            # elif k == ord('2'):  # PR_BG drawing
            #     self.value = self.DRAW_PR_BG
            # elif k == ord('3'):  # PR_FG drawing
            #     self.value = self.DRAW_PR_FG
            elif k == ord('s'):  # save image
                # print("Choose Class: v, p, t, c, l, h or e")
                #
                # nk = input()
                # if nk == 'v':
                #     klass = 'Kritiy_Vagon'
                # elif nk == 'p':
                #     klass = 'Poluvagon'
                # elif nk == 't':
                #     klass = 'Transporter'
                # elif nk == 'c':
                #     klass = 'Tsisterna'
                # elif nk == 'l':
                #     klass = 'Lokomotiv'
                # elif nk == 'h':
                #     klass = 'Hopper'
                # elif nk == 'e':
                klass = 'Else'


                bar = np.zeros((self.img.shape[0], 0, 3), np.uint8)
                res = np.hstack((bar, self.output))
                gray = cv.cvtColor(res, cv.COLOR_BGR2GRAY)
                gray = cv.resize(gray, (self.orig_img.shape[1], self.orig_img.shape[0]))
                _, gray = cv.threshold(gray, 0, 255, cv.THRESH_BINARY)
                contours, _ = cv.findContours(gray, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

                # save contours
                with open("Contours_{}_{}_{}.txt".format(filename, klass, self.counter), "a") as file:
                    # file.write(filename + "\n")
                    for i in range(len(contours)):
                        for j in range(len(contours[i])):
                            np.savetxt(file, contours[i][j], fmt="%1d", delimiter=" ")
                # set brightness by class name
                if klass in self.classes:
                    gray[gray == 255] = self.classes[klass]
                else:
                    gray[gray == 255] = 255
                cv.imwrite('{}_{}_{}.png'.format(filename, klass, self.counter), gray)
                self.counter += 1
                print(" Result saved as image \n")
            elif k == ord('r'):  # reset everything
                print("resetting \n")
                self.rect = (0, 0, 1, 1)
                self.drawing = False
                self.rectangle = False
                self.rect_or_mask = 100
                self.rect_over = False
                self.value = self.DRAW_FG
                self.img = self.img2.copy()
                self.mask = np.zeros(self.img.shape[:2], dtype=np.uint8)  # mask initialized to PR_BG
                self.output = np.zeros(self.img.shape, np.uint8)  # output image to be shown
            elif k == ord('n'):  # segment the image
                print(""" For finer touchups, mark foreground and background by left and right click
                and again press 'n' \n""")
                try:
                    bgdmodel = np.zeros((1, 65), np.float64)
                    fgdmodel = np.zeros((1, 65), np.float64)
                    if (self.rect_or_mask == 0):  # grabcut with rect
                        cv.grabCut(self.img2, self.mask, self.rect, bgdmodel, fgdmodel, 1, cv.GC_INIT_WITH_RECT)
                        self.rect_or_mask = 1
                    elif (self.rect_or_mask == 1):  # grabcut with mask
                        cv.grabCut(self.img2, self.mask, self.rect, bgdmodel, fgdmodel, 1, cv.GC_INIT_WITH_MASK)
                except:
                    import traceback
                    traceback.print_exc()

            mask2 = np.where((self.mask == 1) + (self.mask == 3), 255, 0).astype('uint8')
            self.output = cv.bitwise_and(self.img2, self.img2, mask=mask2)

        print('Done')


if __name__ == '__main__':
    print(__doc__)
    App().run()
    cv.destroyAllWindows()