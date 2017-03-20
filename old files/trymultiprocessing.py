from multiprocessing import Pool
import wx

class newprocess():
    def __init__(self,count):
        self.worker(count)


    def worker(self, count):
        """thread worker function"""
        for repeat in range(0,10):
            print 'Worker %d' % count

        return 'from worker'

 # ------------------------------------------------------------------------------------------ Stand alone test code

#
class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, *args, **kwds)

        pool = Pool(processes=4)  # start 4 worker processes
        for count in range(0,4):
            result = pool.apply_async(newprocess(count))



if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.

