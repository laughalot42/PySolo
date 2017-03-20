import wx
from tryglobalini import cfg_dict
import tryglobalscript

class doit(object):
    def __init__(self):

        print('starting alphabet: %s' % cfg_dict[0]['alphabet'] )
        print('starting numbers: %d' % cfg_dict[1]['numbers'])

        newobject = tryglobalscript.anobject()
        cfg_dict[1]['numbers'] = 456

        print('ending alphabet: %s' % cfg_dict[0]['alphabet'] )
        print('ending numbers: %d' % cfg_dict[1]['numbers'])

 # ------------------------------------------------------------------------------------------ Stand alone test code

#  insert other classes above and call them in mainFrame
#
class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, *args, **kwds)
        doit()


        print('done.')

if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.

#
