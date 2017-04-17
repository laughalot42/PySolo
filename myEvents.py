import wx
import configurator
import cv2
import numpy as np

import msvcrt

def keychecker():
    while True:
        if msvcrt.kbhit():
            print "Key pressed: %s" % msvcrt.getch()


# ------------------------------------------------------------------------------------------ Stand alone test code

#  insert other classes above and call them in mainFrame
#
class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, *args, **kwds)

        keychecker()

        print('done.')

if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.


