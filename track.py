#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       pvg_acquire.py
#
#       Copyright 2011 Giorgio Gilestro <giorgio@gilest.ro>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

__author__ = "Giorgio Gilestro <giorgio@gilest.ro>"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2011/08/16 21:57:19 $"
__copyright__ = "Copyright (c) 2011 Giorgio Gilestro"
__license__ = "Python"

#       Revisions by Caitlin Laughrey and Loretta E Laughrey in 2016.


import threading
import wx
import sys
import pysolovideoGlobals as gbl
import configurator as cfg
import videoMonitor

# -------------------------------------------------------------------------------- redirect sysout to scrolled textctrl
class acquireConsole(wx.Panel):
    def __init__(self, parent):                             # parent is the cfgPanel
        wx.Panel.__init__(self, parent, wx.ID_ANY, size=(200,200))
        self.mon_ID = gbl.mon_ID                            # keep track of which monitor this console is for

        # ------------------------------------------------------ a textctrl box will accept print statement output
        size = gbl.thumb_size
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL | wx.VSCROLL | wx.EXPAND
        self.log = wx.TextCtrl(self, wx.ID_ANY, size=size, style=style)

        parent.scrolledThumbs.thumbGridSizer.Add(self.log, 1, wx.ALL | wx.EXPAND, 5)
        parent.scrolledThumbs.SetSizer(parent.scrolledThumbs.thumbGridSizer)

    def startLogging(self):
        sys.stdout = self.log  # redirect text here
        print('Log for ', gbl.mon_name)

class trackingThread (threading.Thread):
    def __init__(self, trackedMonitor, mon_ID):
        threading.Thread.__init__(self)
        self.trackedMonitor = trackedMonitor
        self.mon_ID = mon_ID
        self.name = gbl.cfg_dict[self.mon_ID]['mon_name']

    def run(self):
        print "Tracking " + self.name
        self.trackedMonitor.startTrack()
        print "Exiting " + self.name

class trackedMonitor(object):
    def __init__(self, parent):
        self.parent = parent                            # parent is cfgPanel
        self.mon_ID = gbl.mon_ID                        # preserve this monitor's attributes with this object
        self.source_type = gbl.source_type
        self.source = gbl.source
        self.source_fps = gbl.source_fps
        self.issdmonitor = gbl.issdmonitor
        self.start_datetime = gbl.start_datetime
        self.track_type = gbl.track_type
        self.mask_file = gbl.mask_file
        self.data_folder = gbl.data_folder
        self.console = acquireConsole(self.parent)  # create a progress reporting console & start

        self.playTimer = wx.Timer(self.parent, id=wx.ID_ANY)


    def startTrack(self):        # -------------------------------------------------------------------------------------- begin tracking
        self.console.startLogging()
        print('START TRACKING NOW', self.mon_ID)

    def onNextFrame(self, evt):
        print('next frame ', str(evt))
        """
        if not self.keepPlaying:
            self.playTimer.Stop()

        frame = self.captureMovie.getImage()
        self.paintImg(frame)
        """

class tracker(object):
    def __init__(self, parent):
        self.parent = parent                                # parent is configuration panel
        self.mon_ID = gbl.mon_ID

        self.consoles = ['consoles']
        self.trackedMonitors = ['tracker']
        for mon_count in range(1, gbl.monitors +1):
            if gbl.cfg_dict[mon_count]['track']:
                gbl.mon_ID = mon_count
                cfg.cfg_dict_to_nicknames()                         # load this monitor's configuration to nicknames

                self.trackedMonitors.append(trackingThread(trackedMonitor(parent), gbl.mon_ID))  # create and thread monitor for tracking
                self.trackedMonitors[-1].trackedMonitor.playTimer.Start(1000 / gbl.thumb_fps)



# ------------------------------------------------------------------------------------------ Stand alone test code
#  insert other classes above and call them in mainFrame
#
class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, None, id=wx.ID_ANY, size=(1000,200))


        print('done.')

if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.

#

