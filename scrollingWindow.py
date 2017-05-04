#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Major revisions by Caitlin A Laughrey and Loretta E Laughrey in 2016-2017.
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



import wx
import threading
import configurator as cfg
import videoMonitor as VM
import track
import pysolovideoGlobals as gbl
# from wx.lib.newevent import NewCommandEvent
# ThumbnailClickedEvt, EVT_THUMBNAIL_CLICKED = wx.lib.newevent.NewCommandEvent()  # NOT USED - click on thumbnail goes unnoticed

# TODO:  make click on thumbnail change to monitor configuration page

""" ============================================================================================== Video playback thread
"""
class videoThread (threading.Thread):                       # threading speeds up video processing
    def __init__(self, monitorPanel, (name)):
        threading.Thread.__init__(self)
        self.monitorPanel = monitorPanel                            # the video panel to be played in the panel
        self.name = name

    def run(self):
        self.monitorPanel.PlayMonitor()                             # start playing the video
        print('pause')

""" ============================================================================================= Object tracking thread
"""
class trackingThread (threading.Thread):                    # Thread that processes the video input
    def __init__(self, trackedMonitor, (mon_ID)):
        threading.Thread.__init__(self)
        self.trackedMonitor = trackedMonitor                # the tracking object
        self.mon_ID = mon_ID
        self.name = gbl.cfg_dict[self.mon_ID]['mon_name']

    def run(self):
        self.trackedMonitor.startTrack()                    # starts tracking process


""" =================================================================================== Scrolling window of video panels
"""
class scrollingWindow(wx.ScrolledWindow):     # --------------------- contails a list of thumbnails in a scrolled window
    """
    Object is a scrolling window with either video preview panels or output consoles for tracking.
    """
    # ------------------------------------------------------------------------------------- initialize a scrolled window
    def __init__(self, parent):
        """
        Thumbs may be videoMonitor panels or console panels.  They are contained in the self.thumbPanels list
        and are mutually exclusive.
        """
        # --------------------------------------------------------------------------- Set up scrolling window
        self.parent = parent
        self.thumbType = 'thumb'                 # always starts with video playback thumbnails

        wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY, size=(-1, 300))
        self.SetScrollbars(1, 1, 1, 1)
        self.SetScrollRate(10, 10)

        self.thumbGridSizer = wx.GridSizer(3, 3, 5, 5)              # will contain the panels

        self.thumbPanels = ['thumb panels']
        self.refreshThumbGrid()       # --------------------- put thumbnails in gridsizer and display in scrolled window
                                           # setsizer is done in calling program (cfgPanel)

    def clearGrid(self):
        if self.thumbType == 'thumb':
            self.clearThumbGrid()
        elif  self.thumbType == 'console':
            self.clearConsoleGrid()

    def refreshGrid(self):
        if self.thumbType == 'thumb':
            self.refreshThumbGrid()
        elif  self.thumbType == 'console':
            self.refreshConsoleGrid()

    # --------------------------------------------------------------------- remove all video panels from scrolled window
    def clearThumbGrid(self):
        """ 
        threads must be stopped and panels must be destroyed or they will keep running in the background and cause
        display problems
        """
        if len(self.thumbPanels) > 1:  # don't remove the 0th element, which is just a descriptor that allows 1-indexing
            for gbl.mon_ID in range(len(self.thumbPanels) -1, 0, -1):
                                                            # reverse order avoids issues with list renumbering
                self.thumbPanels[gbl.mon_ID]._Thread__stop()
                self.thumbPanels[gbl.mon_ID].monitorPanel.keepPlaying = False        # stop playing video
                self.thumbPanels[gbl.mon_ID].monitorPanel.playTimer.Stop()           # stop the timer
                self.thumbPanels[gbl.mon_ID].monitorPanel.Hide()                     # remove the panel from display
                self.thumbPanels[gbl.mon_ID].monitorPanel.Destroy()         # prevents doubled up images & flickering
                del self.thumbPanels[gbl.mon_ID]                                    # delete the panel from the list.

        self.thumbGridSizer.Clear()                                         # clear out gridsizer

    # ---------------------------------------------------------- Make list of thumbnails to populate the scrolled window
    def refreshThumbGrid(self):
        oldMonID = gbl.mon_ID

        self.clearGrid()                                # clear current grid contents
        self.thumbType = 'thumb'                        # set grid content type

        # --------------------------------------------- go through each monitor configuration and make a thumbnail panel
        for gbl.mon_ID in range(1, gbl.monitors + 1):
            cfg.mon_dict_to_nicknames()

            # create thread with thumbnail panel and add to grid
            self.thumbPanels.append(videoThread(VM.monitorPanel(self, mon_ID=gbl.mon_ID, panelType='thumb',
                                                                loop=True, ROIs=[]), (gbl.mon_name)))

            interval = self.thumbPanels[gbl.mon_ID].monitorPanel.interval
            self.thumbPanels[gbl.mon_ID].start()

            if not self.thumbPanels[gbl.mon_ID].monitorPanel.playTimer.IsRunning():
                self.thumbPanels[gbl.mon_ID].monitorPanel.playTimer.Start(interval)

            self.thumbGridSizer.Add(self.thumbPanels[gbl.mon_ID].monitorPanel, 1, wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.SetSizerAndFit(self.thumbGridSizer)
        self.Parent.Layout()                            # rearranges thumbnails into grid
                                                        # must use Parent to get display numbers in the right place

        gbl.mon_ID = oldMonID                           # go back to same page we came from
        if gbl.mon_ID != 0:
            cfg.mon_dict_to_nicknames()                 # restore nicknames to current monitor values

    # ------------------------------------------------------------------- remove all console panels from scrolled window
    def clearConsoleGrid(self):
        # don't remove the 0th element which is there to allow 1-indexing
        if len(self.thumbPanels) > 1:
            maxcount = len(self.thumbPanels) -1
            for mon_count in range(maxcount, 0, -1):     # destroy old previewPanel objects or they will keep playing
                                                             # reverse order avoids issues with list renumbering
                self.thumbPanels[mon_count]._Thread__stop()
                self.trkdConsList[mon_count].Hide()
                self.trkdConsList[mon_count].Destroy()          # prevents doubled up panels and flickering
                del self.thumbPanels[mon_count]                 # delete the objects from the list.
                del self.trkdConsList[mon_count]                # delete the objects from the list.
                del self.trkdMonsList[mon_count]                # delete the objects from the list.

        self.thumbGridSizer.Clear()                             # clear out gridsizer

    # -------------------------------------------------- Make list of textctrl objects for consoles to populate the grid
    def refreshConsoleGrid(self):
        oldMon_ID = gbl.mon_ID

        self.clearGrid()                                    # clear current grid contents
        self.thumbType = 'console'                            # set grid content type

        # --------------------------------------------- go through each monitor configuration and make a thumbnail panel
        self.trkdMonsList = ['tracked monitors']
        self.trkdConsList = ['consoles']
        for gbl.mon_ID in range(1, gbl.monitors + 1):
            cfg.mon_dict_to_nicknames()  # load monitor parameters to globals

            # create thread with tracked monitor and scroll panel and add to grid
            self.trkdMonsList.append(trackingThread(track.trackedMonitor(self, gbl.mon_ID, gbl.video_on), (gbl.mon_ID)))
            self.trkdConsList.append(self.trkdMonsList[gbl.mon_ID].trackedMonitor.console)
            self.thumbGridSizer.Add(self.trkdConsList[gbl.mon_ID], 1, wx.ALIGN_CENTER_HORIZONTAL, 5) # add console to scrolled window

        self.SetSizerAndFit(self.thumbGridSizer)
        self.Parent.Layout()

        gbl.mon_ID = oldMon_ID              # go back to the page we came from
        if gbl.mon_ID != 0:
            cfg.mon_dict_to_nicknames()

    def ignoreEvent(self, event):
        event.skip()
# ------------------------------------------------------------------------------------------ Stand alone test code

class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, *args, **kwds)

        whatsit = scrollingWindow(self)

        print('done.')

if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.


