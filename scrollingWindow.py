
import wx
import threading
import configurator as cfg
import videoMonitor as VM
import track
import pysolovideoGlobals as gbl
from wx.lib.newevent import NewCommandEvent
ThumbnailClickedEvt, EVT_THUMBNAIL_CLICKED = wx.lib.newevent.NewCommandEvent()

class RedirectText(object):
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self, string):
        wx.CallAfter(self.out.WriteText, string)

class consolePanel(wx.TextCtrl):   # ------------------------------------------------ redirect sysout to scrolled textctrl
    def __init__(self, parent, size=(200,200)):                             # parent is the cfgPanel
        self.mon_ID = gbl.mon_ID                            # keep track of which monitor this console is for
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_AUTO_SCROLL | wx.HSCROLL | wx.VSCROLL | wx.EXPAND
        wx.TextCtrl.__init__(self, parent, wx.ID_ANY, size=size, style=style, name=gbl.mon_name)

    def flush(self):            # imitates a file-like object to avoid "no attribute 'flush'" error
        pass


# ------------------------------------------------------------------------- creates a thread that plays a videoMonitor
class videoThread (threading.Thread):                       # threading speeds up video processing
    def __init__(self, monitorPanel, name):
        threading.Thread.__init__(self)
        self.monitorPanel = monitorPanel                            # the video panel to be played in the panel
        self.name = name

    def start(self):
        self.monitorPanel.PlayMonitor()                        # start playing the video

class trackingThread (threading.Thread):        #----------------------- creates a Thread that processes the video input
    def __init__(self, trackedMonitor, consolePanel, mon_ID):
        threading.Thread.__init__(self)
        self.trackedMonitor = trackedMonitor                # the tracking object
        self.console = consolePanel                         # the output console
        self.mon_ID = mon_ID
        self.name = gbl.cfg_dict[self.mon_ID]['mon_name']

    def run(self):
        self.trackedMonitor.startTrack()


class scrollingWindow(wx.ScrolledWindow):     # ---------------------- contails a list of thumbnails in a scrolled window
    def __init__(self, parent):
        """
        Thumbs may be videoMonitor panels or console panels.  They are contained in the self.thumbPanels list
        and are mutually exclusive.
        """
        # -------------------------------------------------------------------------------------- Set up scrolling window
        self.parent = parent
#        self.numberOfThreads = 0
#        self.numberOfTimers = 0
        wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY, size=(-1, 300))
        self.SetScrollbars(1, 1, 1, 1)
        self.SetScrollRate(10, 10)
        self.thumbGridSizer = wx.GridSizer(3, 3, 5, 5)

        self.thumbPanels = ['']
        self.refreshThumbGrid()            # --------------------- put thumbnails in gridsizer and display in scrolled window

    def clearThumbGrid(self):
        if len(self.thumbPanels) > 1:        # don't remove the 0th element
            maxcount = len(self.thumbPanels) -1
            for mon_count in range(maxcount, 0, -1):     # destroy old previewPanel objects or they will keep playing
                                                            # reverse order avoids issues with list renumbering
                self.thumbPanels[mon_count].monitorPanel.keepPlaying = False        # stop playing video
                self.thumbPanels[mon_count].monitorPanel.playTimer.Stop()
                self.thumbPanels[mon_count].monitorPanel.Hide()
                self.thumbPanels[mon_count].monitorPanel.Destroy()
                del self.thumbPanels[mon_count]                    # delete the objects from the list.



        self.thumbGridSizer.Clear()                          # clear out gridsizer

    def refreshThumbGrid(self):  # -------------------------------------- Make array of thumbnails to populate the grid

        self.clearThumbGrid()
        # --------------------------------------------- go through each monitor configuration and make a thumbnail panel
        for gbl.mon_ID in range(1, gbl.monitors + 1):
            cfg.mon_dict_to_nicknames()  # load monitor parameters to globals

            # create thread with thumbnail panel and add to grid
            self.thumbPanels.append(videoThread(VM.monitorPanel(self, mon_ID=gbl.mon_ID, panelType='thumb', loop=True),
                                               gbl.mon_name))

            interval = self.thumbPanels[gbl.mon_ID].monitorPanel.interval
            self.thumbPanels[gbl.mon_ID].start()
            self.thumbPanels[gbl.mon_ID].monitorPanel.playTimer.Start(interval)
            self.thumbGridSizer.Add(self.thumbPanels[gbl.mon_ID].monitorPanel, 1, wx.ALIGN_CENTER_HORIZONTAL, 5)

        gbl.mon_ID = 0                          # this function is only called from the config panel (mon_ID = 0)
        self.SetSizer(self.thumbGridSizer)
        self.Layout()

    def refreshConsoleGrid(self):  # ------------------------------------- Make array of thumbnails to populate the grid

        self.clearThumbGrid()
        # --------------------------------------------- go through each monitor configuration and make a thumbnail panel
        for gbl.mon_ID in range(1, gbl.monitors + 1):
            cfg.mon_dict_to_nicknames()  # load monitor parameters to globals

            # create thread with tracked monitor and scroll panel and add to grid
            self.thumbPanels.append(trackingThread(track.trackedMonitor(self, gbl.mon_ID),            # create tracked object
                                    consolePanel(self, size=gbl.thumb_size), gbl.mon_ID))

            self.thumbGridSizer.Add(self.thumbPanels[gbl.mon_ID].console, 1, wx.ALIGN_CENTER_HORIZONTAL, 5) # add console to scrolled window
            self.thumbPanels[gbl.mon_ID].trackedMonitor.startTrack()                            # start tracking

        gbl.mon_ID = 0  # this function is only called from the config panel (mon_ID = 0)
        self.SetSizer(self.thumbGridSizer)
        self.Layout()


# ------------------------------------------------------------------------------------------ Stand alone test code

#  insert other classes above and call them in mainFrame
#
class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, *args, **kwds)

        startit = myclass(self)

        print('done.')

if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.


