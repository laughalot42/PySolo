import wx, threading

class acquireThread(threading.Thread):
    def __init__(self, parent, count):
        super(acquireThread, self).__init__()
        self.t = threading.Thread(target=parent.worker(count))


 # ------------------------------------------------------------------------------------------ Stand alone test code

#
class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, *args, **kwds)

        self.keepgoing = True
        mythread = []
        for count in range(5):
            mythread.append(acquireThread(self, count))
            mythread[count].daemon = True
            mythread[count].t.start()

        self.keepgoing = False
        for count in range(5):
            mythread[count]._Thread__stop()

        print('done.')

    def worker(self, count):
        """thread worker function"""
        for repeat in range(0,10):
            print 'Worker %d' % count


if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.

#
