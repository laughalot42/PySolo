import wx
import cv2, cv2.cv
import os
import winsound
import configurator as cfg
import pysolovideoGlobals as gbl

# --------------------------------------------------------------------------------------------- for using a video camera
class realCam(object):                                  # don't use global variables for this object due to threading
    """
    realCam class will handle a webcam connected to the system
    """

    def __init__(self_realCam, mon_ID=gbl.mon_ID, size=(320,240), fps=1, devnum=0):

        self_realCam.mon_ID = mon_ID
        self_realCam.size = size  # (w,h)
        self_realCam.fps = fps
        self_realCam.devnum = 0             ####### devnum

        self_realCam.currentFrame = 0
        self_realCam.lastFrame = 0                      # cameras don't have a last frame
        self_realCam.isVirtualCam = False

        self_realCam.blackFrame = cv2.cv.CreateImage(self_realCam.size , cv2.cv.IPL_DEPTH_8U, 3)       # blank frame alternative
        cv2.cv.Zero(self_realCam.blackFrame)

        try:                                                                        # initialize the camera
            self_realCam.captureCam = cv2.cv.CaptureFromCAM(0)      # only one camera is supported
        except:
            self_realCam.captureCam = None                                      # capture failed
# TODO:           self_realCam.TopLevelParent.SetStatusText('Real Cam capture failed.')
            winsound.Beep(600,200)

        self_realCam.currentFrame += 1

        self_realCam.in_size = self_realCam.getsize()                           # frame size (w,h) from camera
        self_realCam.scale = (self_realCam.in_size != self_realCam.size)                # need to scale images?

    def getImage(self_realCam):  # capture and prepare the next frame
        """
        for live cameras
        """
        try:
            frame = cv2.cv.QueryFrame(self_realCam.captureCam)
        except:
            frame = self_realCam.blackFrame
            # TODO:           self_realCam.TopLevelParent.SetStatusText('Real Cam capture failed.')
            winsound.Beep(600, 200)

        self_realCam.currentFrame += 1

        if self_realCam.scale:  # rescale the image size
            newframe = cv2.cv.CreateImage(self_realCam.size, cv2.cv.IPL_DEPTH_8U, 3)

            if type(frame) != type(newframe):
                return newframe                             # WHY MISMATCH?

            cv2.cv.Resize(frame, newframe)
            frame = newframe

        return frame

    def getsize(self_realCam):
        """
        Return real size
        """
        x1 = cv2.cv.GetCaptureProperty(self_realCam.captureCam, cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
        y1 = cv2.cv.GetCaptureProperty(self_realCam.captureCam, cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
        return int(x1), int(y1)

    """
    def setsize(self_realCam, (x, y)):
        """"""
        Set size of the camera we are acquiring from
        """"""
        x = int(x); y = int(y)
        cv2.cv.SetCaptureProperty(self_realCam.captureCam, cv2.cv.CV_CAP_PROP_FRAME_WIDTH, x)
        cv2.cv.SetCaptureProperty(self_realCam.captureCam, cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, y)
    """

# ----------------------------------------------------------------------------------------------- for using a video file
class virtualCamMovie(object):
    """
    A Virtual cam to be used to pick images from a movie (avi, mov)
    """
    def __init__(self_vMovie, source, size, fps):

        self_vMovie.source = source
        self_vMovie.size = size
        self_vMovie.fps = fps

        self_vMovie.currentFrame = 0
        self_vMovie.step = 1
        self_vMovie.loop = True

        self_vMovie.blackFrame = cv2.cv.CreateImage(self_vMovie.size , cv2.cv.IPL_DEPTH_8U, 3)       # blank frame alternative
        cv2.cv.Zero(self_vMovie.blackFrame)

        try:
                self_vMovie.captureMovie = cv2.cv.CaptureFromFile(self_vMovie.source)
        except:
            self_vMovie.captureMovie = None                                       # capture failed
# TODO:            self_realCam.TopLevelParent.SetStatusText('Video capture failed.')
            winsound.Beep(600, 200)

        self_vMovie.lastFrame = cv2.cv.GetCaptureProperty(self_vMovie.captureMovie, cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        self_vMovie.in_size = self_vMovie.getsize()                         # frame size from video
        self_vMovie.scale = (self_vMovie.in_size != self_vMovie.size)

    def getsize(self_vMovie):
        #finding the input size
        w = cv2.cv.GetCaptureProperty(self_vMovie.captureMovie, cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
        h = cv2.cv.GetCaptureProperty(self_vMovie.captureMovie, cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
        return int(w), int(h)

    def getImage(self_vMovie):            # capture next frame from video file
        """
        for input from video file
        """
        if self_vMovie.currentFrame >= self_vMovie.lastFrame:               # close file and loop from beginning
            self_vMovie.currentFrame = 0
            self_vMovie.captureMovie = cv2.cv.CaptureFromFile(self_vMovie.source)           # restarts video

        try:
            frame = cv2.cv.QueryFrame(self_vMovie.captureMovie)

        except:
            frame = self_vMovie.blackFrame

        if frame is None:  frame = self_vMovie.blackFrame

        self_vMovie.currentFrame += self_vMovie.step

        if self_vMovie.currentFrame > self_vMovie.lastFrame and not self_vMovie.loop: return False

        if self_vMovie.scale:
            newsize = cv2.cv.CreateImage(self_vMovie.size, cv2.cv.IPL_DEPTH_8U, 3)
            cv2.cv.Resize(frame, newsize)
            frame = newsize

        return frame

# ------------------------------------------------------------------------------------ for using a sequence of 2D images
class virtualCamFrames(object):
    """
    A Virtual cam to be used to pick images from a folder rather than a webcam
    Images are handled through PIL
    """
    def __init__(self_vFrames, source, size, fps):

        self_vFrames.source = source
        self_vFrames.size = size
        self_vFrames.fps = fps

        self_vFrames.fileList = self_vFrames.__populateList__()
        self_vFrames.lastFrame = len(self_vFrames.fileList)

        self_vFrames.currentFrame = 0
        self_vFrames.loop = False

        fp = os.path.join(self_vFrames.source, self_vFrames.fileList[0])

        self_vFrames.in_size = cv2.cv.GetSize(cv2.cv.LoadImage(fp))

        self_vFrames.scale = (self_vFrames.in_size != self_vFrames.size)

    def __populateList__(self_vFrames):
        """
        Populate the file list
        """
        fileList = []
        fileListTmp = os.listdir(self_vFrames.source)

        for fileName in fileListTmp:
            if '.tif' in fileName or '.jpg' in fileName:
                fileList.append(fileName)

        fileList.sort()
        return fileList

    def getImage(self_vFrames):
        """
        for folder of 2D images
        """
        w = self_vFrames.size[0]
        h = self_vFrames.size[1]

        if self_vFrames.currentFrame >= self_vFrames.lastFrame:
            self_vFrames.currentFrame = 0                                       # loop to beginning

        fp = os.path.join(self_vFrames.source, self_vFrames.fileList[self_vFrames.currentFrame])

        self_vFrames.currentFrame += 1

        try:
            frame = cv2.cv.LoadImage(fp) #using cv to open the file

        except:
            print ( 'error with image %s' % fp )
            raise

        if self_vFrames.scale:
            newsize = cv2.cv.CreateMat(h, w, cv2.cv.CV_8UC3)                    # must be in order (h,w) or picture will look terrible
            cv2.cv.Resize(frame, newsize)

        return frame

# ------------------------------------------------------------------------------------------ generic video display panel
class monitorPanel(wx.Panel):                                       
    """
    One Panel to be used as thumbnail, or a preview panel
    Avoid gbl nicknames, except for cfg_dict and flags, in case this is called for a monitor that is not currently selected
    """
    def __init__( self_monPanel, parent, mon_ID=gbl.mon_ID, panelType='thumb'):

        name = 'Monitor%d' % mon_ID
        wx.Panel.__init__(self_monPanel, parent, id=wx.ID_ANY, name=name)

        self_monPanel.parent = parent
        self_monPanel.keepPlaying = False                           # flag to start and stop video playback
        self_monPanel.mon_ID = mon_ID         
        self_monPanel.source = gbl.cfg_dict[mon_ID]['source']
        self_monPanel.source_type = gbl.cfg_dict[mon_ID]['source_type']

        if self_monPanel.source[0:6] == 'Webcam':               # get the device number if the panel source is a webcam
            self_monPanel.devnum = 0


        self_monPanel.panelType = panelType
        if panelType == 'preview':
            self_monPanel.size = gbl.cfg_dict[0]['preview_size']
            self_monPanel.fps = gbl.cfg_dict[mon_ID]['preview_fps']
            gbl.showROIs = True
        elif panelType == 'thumb':
            self_monPanel.size = gbl.cfg_dict[0]['thumb_size']
            self_monPanel.fps = gbl.cfg_dict[0]['thumb_fps']
            gbl.showROIs = False
        else:
            self_monPanel.size = (320,240)
            self_monPanel.fps = 1
            gbl.showROIs = True
            print('Unexpected panel type in class monitorPanel')

#        self_monPanel.imageCount = 0                  # for tracking
#        self_monPanel.grabmovie = False

        self_monPanel.SetSize(self_monPanel.size)
        self_monPanel.step = 1

        self_monPanel.widgetMaker()
        self_monPanel.sizers()

        self_monPanel.SetMinSize(self_monPanel.GetSize())
        self_monPanel.SetBackgroundColour('#A9A9A9')
        self_monPanel.allowEditing = False

        # use the sourcetype to create the correct type of object for capture
        if gbl.cfg_dict[self_monPanel.mon_ID]['source_type'] == 0:
            self_monPanel.captureMovie = realCam(self_monPanel.source, self_monPanel.GetSize(), self_monPanel.fps, devnum=0)
        elif gbl.cfg_dict[self_monPanel.mon_ID]['source_type'] == 1:
            self_monPanel.captureMovie = virtualCamMovie(self_monPanel.source, self_monPanel.GetSize(), self_monPanel.fps)
        elif gbl.cfg_dict[self_monPanel.mon_ID]['source_type'] == 2:
            self_monPanel.captureMovie = virtualCamFrames(self_monPanel.source, self_monPanel.GetSize(), self_monPanel.fps)


        # ---------------------------------------------------------------------------------------  apply threading
#        if gbl.cfg_dict[mon_ID]['track']:
#            self_monPanel.monThread = acquireThread(self_monPanel)

        # ---------------------------------------------------------------------- create a timer that will play the video
        self_monPanel.playTimer = wx.Timer(self_monPanel, id=wx.ID_ANY)
        self_monPanel.isPlaying = False               # leave it up to other functions to start and stop the video

    # --------------------------------------------------------------------------------------------------- Widgets
    def widgetMaker(self_monPanel):
        self_monPanel.monDisplayNumber = self_monPanel.displayNumber()                    # monitor number

    def displayNumber(self_monPanel):        # ------------------------------- Display the monitor number in corner of thumbnail
        # TODO: play, pause, loop, slider control
        font1 = wx.Font(25, wx.SWISS, wx.NORMAL, wx.NORMAL)
        text1 = wx.StaticText(self_monPanel, wx.ID_ANY, ' %s' % self_monPanel.mon_ID)
        text1.SetFont(font1)
        return text1

    def sizers(self_monPanel):
        self_monPanel.numberSizer = wx.BoxSizer(wx.HORIZONTAL)
        self_monPanel.numberSizer.Add(self_monPanel.monDisplayNumber, 0, wx.ALIGN_LEFT | wx.ALIGN_TOP, 20)

        self_monPanel.SetSizer(self_monPanel.numberSizer)

    def PlayMonitor(self_monPanel):

        self_monPanel.interval = 1000/ self_monPanel.fps

        # each of the 3 video input classes has a "getImage" function
        self_monPanel.captureMovie.getImage()

        (w, h) = self_monPanel.GetSize()
        frame = cv2.cv.CreateMat(h, w, cv2.cv.CV_8UC3)
        self_monPanel.bmp = wx.BitmapFromBuffer(w, h, frame.tostring())

        self_monPanel.Bind(wx.EVT_PAINT, self_monPanel.onPaint)
        self_monPanel.Bind(wx.EVT_TIMER, self_monPanel.onNextFrame)

        self_monPanel.isPlaying = True
        self_monPanel.keepPlaying = True
        self_monPanel.Show()

        # Non-threaded panels (previewss) must start inside PlayMonitor
        # Threaded panels (Thumbnails) must start in the class where the threading was called
#        if self_monPanel.panelType == 'preview':
#            self_monPanel.playTimer.Start(self_monPanel.interval)



    def onPaint(self_monPanel, evt):

        if self_monPanel.bmp:
            dc = wx.BufferedPaintDC(evt.GetEventObject())
            dc.DrawBitmap(self_monPanel.bmp, 0, 0, True)

            if gbl.showROIs and gbl.ROIs:                               # add ROIs if requested and available
                dc.SetPen(wx.Pen('red'))
                for roi in gbl.ROIs:
                    dc.DrawLines(roi)

#        evt.Skip()

    def onNextFrame(self_monPanel, evt):
        if not self_monPanel.keepPlaying:
            self_monPanel.playTimer.Stop()

        frame = self_monPanel.captureMovie.getImage()
        self_monPanel.paintImg(frame)

    def paintImg(self_monPanel, img):
        w = self_monPanel.size[0]
        h = self_monPanel.size[1]
        if img:
            depth, channels = img.depth, img.nChannels
            datatype = cv2.cv.CV_MAKETYPE(depth, channels)

            frame = cv2.cv.CreateMat(h, w, datatype)                    # ------ *MUST* be (h,w) or image will look terrible
            cv2.cv.Resize(img, frame)

            cv2.cv.CvtColor(frame, frame, cv2.cv.CV_BGR2RGB)

            self_monPanel.bmp.CopyFromBuffer(frame.tostring())
            self_monPanel.Refresh()






# ------------------------------------------------------------------------------------------ Stand alone test code
#
class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, *args, **kwds)

        self.config = cfg.Configuration(self)
        thumbnailsize = gbl.cfg_dict[0]['size_thumb']
        thumb = monitorPanel(self, gbl.cfg_dict, 'thumb')

        print('done.')

if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "", (10,10), (600,400))           # Create the main window.    id, title, pos, size, style, name
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.

#
