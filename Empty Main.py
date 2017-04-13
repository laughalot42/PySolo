import wx
import configurator
import cv2
import numpy as np



drawing = False # true if mouse is pressed
ix,iy = -1,-1

# mouse callback function
def draw_rect(event,x,y,flags,param):
    global ix,iy,drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            cv2.line(img,(ix,iy),(ix,y),(0,255,0),1)
            cv2.line(img,(ix,iy),(x,iy),(0,255,0),1)


    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(img,(ix,iy),(x,y),(0,255,0),1)



# ------------------------------------------------------------------------------------------ Stand alone test code

#  insert other classes above and call them in mainFrame
#
class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, *args, **kwds)
        global img
#        self.config = configurator.Configuration(self)
        img = np.zeros((512, 512, 3), np.uint8)
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', draw_rect)

        while (1):
            cv2.imshow('image', img)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('m'):
                mode = not mode
            elif k == 27:
                break

        cv2.destroyAllWindows()

        print('done.')

if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.


