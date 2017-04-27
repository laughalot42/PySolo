import pysolovideoGlobals
import cv, wx
import winsound
import threading


class acquireThread(threading.Thread):

    def __init__(selfacqthread, parent):
        """
        """
        selfacqthread.parent = parent
        selfacqthread.keepGoing = False
        threading.Thread.__init__(selfacqthread)

    def doTrack(selfacqthread, keepGoing):
        """
        checks to see if tracking should continue
        """
        while keepGoing:
            print('going going going')

    def halt(selfacqthread):
        """
        """
        selfacqthread.keepGoing = False
        selfacqthread.halt()

class captureRealCam(wx.Panel):
    def __init__(self_RealCam, parent, fps, size, options=None, devnum=0):
        wx.Panel.__init__(self_RealCam, parent, id=wx.ID_ANY, size=size)
        self_RealCam.fps = fps
        self_RealCam.interval = 1000 / self_RealCam.fps
        self_RealCam.size = size
        self_RealCam.devnum = devnum
        self_RealCam.isVirtualCam = False
        self_RealCam.keepGoing = False

        self_RealCam.__initCamera()
        self_RealCam.in_size = self_RealCam.getsize()  # frame size from camera
        self_RealCam.scale = (self_RealCam.in_size != self_RealCam.size)

        self_RealCam.playTimer = wx.Timer(self_RealCam, id=wx.ID_ANY)

    def __initCamera(self_RealCam):
        try:
            self_RealCam.captureCam = cv.CaptureFromCAM(self_RealCam.devnum)  # self_RealCam.devnum) #$$$$$
            self_RealCam.setsize(self_RealCam.in_size)
        except:
            return False
        return True

    def getsize(self_RealCam):
        """
        Return real size
        """
        x1 = cv.GetCaptureProperty(self_RealCam.captureCam, cv.CV_CAP_PROP_FRAME_WIDTH)
        y1 = cv.GetCaptureProperty(self_RealCam.captureCam, cv.CV_CAP_PROP_FRAME_HEIGHT)
        return (int(x1), int(y1))


    def setsize(self_RealCam, (x, y)):
        """
        Set size of the camera we are acquiring from
        """
        x = int(x)
        y = int(y)
        cv.SetCaptureProperty(self_RealCam.captureCam, cv.CV_CAP_PROP_FRAME_WIDTH, x)
        cv.SetCaptureProperty(self_RealCam.captureCam, cv.CV_CAP_PROP_FRAME_HEIGHT, y)

    def getCamImage(self_RealCam):
        self_RealCam.__initCamera()

        frame = cv.QueryFrame(cv.CaptureFromCAM(self_RealCam.devnum))

        return frame

    def onPaint(self_RealCam, evt):

        if self_RealCam.bmp:
            dc = wx.BufferedPaintDC(self_RealCam)
            dc.DrawBitmap(self_RealCam.bmp, 0, 0, True)

#            if gbl.showROIs:                               # add ROIs if requested and available
#                dc.SetPen(wx.Pen('red'))
#                for roi in gbl.ROIs:
#                    dc.DrawLines(roi)

        evt.Skip()



    def onNextFrame(self_RealCam, evt):
        img = self_RealCam.getCamImage()
        self_RealCam.paintImg(img)

    def paintImg(self_RealCam, img):
        """
        """
        if img:
            depth, channels = img.depth, img.nChannels
            datatype = cv.CV_MAKETYPE(depth, channels)

            frame = cv.CreateMat(self_RealCam.size[1], self_RealCam.size[0], datatype)
#            cv.Resize(img, frame)

            cv.CvtColor(frame, frame, cv.CV_BGR2RGB)

            self_RealCam.bmp.CopyFromBuffer(frame.tostring())
            self_RealCam.Refresh()


    def PlayMonitor(self_RealCam):

        frame = cv.CreateMat(self_RealCam.size[1], self_RealCam.size[0], cv.CV_8UC3)
        self_RealCam.bmp = wx.BitmapFromBuffer(self_RealCam.size[0], self_RealCam.size[1], frame.tostring())

        self_RealCam.playTimer = wx.Timer(self_RealCam, id=wx.ID_ANY)            # playtimer was created in init
        self_RealCam.Bind(wx.EVT_PAINT, self_RealCam.onPaint)
        self_RealCam.Bind(wx.EVT_TIMER, self_RealCam.onNextFrame)

        self_RealCam.isPlaying = True

        self_RealCam.playTimer.Start(self_RealCam.interval)







            # ------------------------------------------------------------------------------------------ Stand alone test code

#  insert other classes above and call them in mainFrame
#
class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, *args, **kwds)

        mymovie = captureRealCam(self, 1, (400,400), options=None, devnum=0)
        mymovie.keepGoing = True
        captureRealCam.PlayMonitor(mymovie)



        print('done.')

if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.

#
