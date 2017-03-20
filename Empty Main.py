import wx

class myclass(wx.Panel):

    def __init__(self, parent):
        self.deleteBtn = wx.Button(parent, wx.ID_ANY, size=(100, 100), label='X')
        font_X = wx.Font(36, wx.SWISS, wx.NORMAL, wx.NORMAL



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


