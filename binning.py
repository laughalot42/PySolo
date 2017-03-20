import wx                               # GUI controls


class binningPanel(wx.Panel):                                 # temporary class
    """
    panel for creating a mask of ROIs
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY, name='binningPanel')

        mainSizer4 = wx.BoxSizer(wx.HORIZONTAL)
        tempText4 = wx.StaticText(self, wx.ID_ANY, "Binning Panel")
        mainSizer4.Add(tempText4)
        self.SetSizer(mainSizer4)

class SCAMPPanel(wx.Panel):                                     # temporary class
    """
    panel for creating a mask of ROIs
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY, name='SCAMPPanel')

        mainSizer5 = wx.BoxSizer(wx.HORIZONTAL)
        tempText5 = wx.StaticText(self, wx.ID_ANY, "SCAMP Panel")
        mainSizer5.Add(tempText5)
        self.SetSizer(mainSizer5)





# ------------------------------------------------------------------------------------------ Stand alone test code
#  insert other classes above and call them in mainFrame
#
class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, *args, **kwds)







        print('done.')

if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.

#
