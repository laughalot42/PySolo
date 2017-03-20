#!/usr/bin/python

import wx
import time
import videoMonitor as mon
import pysolovideoGlobals as gbl
import configurator as cfg
import threading


class myThread (threading.Thread):
    def __init__(self, parent, monPanel, name):
        threading.Thread.__init__(self)
        self.monPanel = monPanel
        self.name = name

    def run(self):
        print "Starting " + self.name

        self.monPanel.PlayMonitor()

        print "Exiting " + self.name

#------------------------------------------------------------------------------
def print_time(threadName, delay, counter):
    while counter:
        if exitFlag:
            threadName.exit()
        time.sleep(delay)
        print "%s: %s" % (threadName, time.ctime(time.time()))
        counter -= 1

#-------------------------------------------------------------------------------
#
class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, *args, **kwds)


        self.config = cfg.Configuration(self)                   # let user select a configuration to load before starting
        self.config.cfg_to_dicts()


        # Create new threads
        self.mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        monThread = ['']
        for mon_ID in range(1, gbl.cfg_dict[0]['monitors']+1):
            monThread.append(myThread(self, mon.monitorPanel(self, mon_ID=mon_ID, panelType='thumb'),
                                    gbl.cfg_dict[mon_ID]['mon_name']))

            self.mainsizer.Add(monThread[mon_ID].monPanel)
            monThread[mon_ID].start()                                   # Start new Thread
            monThread[mon_ID].monPanel.playTimer.Start(1/1000)                   # start timer

        self.SetSizer(self.mainsizer)
        self.Layout()

        print "Exiting Main Thread"

# -----------------------------------------------------------------------------------------------------
if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.


