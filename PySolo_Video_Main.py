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
from win32api import GetSystemMetrics
import wx.lib.inspection

import pysolovideoGlobals as gbl
import configurator as cfg
import cfgPanel
import maskPanel


# TODO: stop flickering when changing pages



""" ====================================================================================================== Main notebook
The main notebook containing all the panels for data displaying and analysis
"""
class mainNotebook(wx.Notebook):
    # ---------------------------------------------------------------------------------------------- initialize notebook
    def __init__(self, parent):

        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.NB_LEFT, name='NotebookNameStr')

        self.notebookPages = []                 # list to contain notebook page information

        self.notebookPages.append(cfgPanel.cfgPanel(self))          # ----- configuration page is element 0
        cfg.cfg_dict_to_nicknames()                                 # load configuration parameters into global nicknames
        self.AddPage(self.notebookPages[0], 'Configuration')

        for gbl.mon_ID in range(1, gbl.monitors+1):                 # monitor page numbers match monitor number
            cfg.mon_dict_to_nicknames()                             # load monitor configuration into global nicknames
            self.addMonitorPage()                                   # add monitor page to notebook

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onPageChanging)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,  self.onPageChanged)
        self.Layout()

        gbl.mon_ID = 0             # set mon_ID to zero which is configuration page

    # ---------------------------------------------------------------------------------------------------- add a monitor
    def addMonitorPage(self):
        # duplicates the last monitor to make a new one.  Only 9 monitors are allowed.
        self.notebookPages.append(maskPanel.monCfgPanel(self))       # make the monitor page
        self.AddPage(self.notebookPages[gbl.mon_ID], gbl.mon_name)      # add to notebook

    # ----------------------------------------------------------------------- event response: prepare to change the page
    def onPageChanging(self, event):
        self.onPrepToChangePage()

    # ---------------------------------------------------------------------------------- event response: page is changed
    def onPageChanged(self, event):
        page_num = event.GetSelection()
        self.onPrepNewPage(page_num)

    # -------------------------------------------------------------- change page by page number instead of an event call
    def onGoToPage(self, page_num):
        gbl.statbar.SetStatusText(' ')
        self.prepToChangePage()
        self.onPrepNewPage(page_num)

    # -------------------------------------------------------------------------------------- prepare to change the page
    def onPrepToChangePage(self):

        if self.notebookPages[gbl.mon_ID].shouldSaveCfg:                    # something changed. does user want to save?
            answer = self.TopLevelParent.config.Q_wantToSave()  # save config changes?
            if answer == wx.ID_CANCEL:  # leave things alone and go back
                return

            if answer == wx.ID_YES:  # save everything
                cfg.cfg_nicknames_to_dicts()  # save any changes made to the configuration
                cfg.mon_nicknames_to_dicts(gbl.mon_ID)  # save any changes made to the monitor
                self.Parent.config.cfgSaveAs(self)  # save to cfg file

            # if No, just keep going            # remove all thumbnails, timers, and threads

        if gbl.mon_ID == 0:  # ---------------------------------------------------------- leaving the configuration page
                self.notebookPages[0].scrolledThumbs.clearGrid()

        if gbl.mon_ID != 0:     # --------------------------------------------------------------- leaving a monitor page
            page_num = self.notebookPages[gbl.mon_ID].Q_shouldSaveMask(gbl.mon_ID)    # save mask?

            self.notebookPages[gbl.mon_ID].clearVideo()     # remove video and timer

    # ------------------------------------------------------------------------------ page has changed. update everything
    def onPrepNewPage(self, page_num):
        # ----------------------------------------------------------------- update nickname to the new page number
        gbl.mon_ID = page_num

        if page_num == 0:         # --------------------------------------------------- refresh configuration page
            cfg.cfg_dict_to_nicknames()                                 # load configuration page parameters
            self.notebookPages[0].fillTable()                           # update the configuration table
            self.notebookPages[0].scrolledThumbs.clearGrid              # destroy old thumbnails
            self.notebookPages[0].scrolledThumbs.refreshThumbGrid()     # restart the thumbnail windows
            self.notebookPages[0].scrolledThumbs.EnableScrolling(1, 1)  # restore scrollbars
            self.notebookPages[0].Layout()

        else:          # ----------------------------------------------------------------- refresh the monitor page
            if gbl.mon_ID != 0:
                cfg.mon_dict_to_nicknames()                             # update nicknames for the selected monitor

            self.notebookPages[gbl.mon_ID].previewPanel.parent.clearVideo()         # destroy old preview panel
            self.notebookPages[gbl.mon_ID].previewPanel.parent.refreshVideo()       # restart start video
            self.notebookPages[gbl.mon_ID].SetSizer(self.notebookPages[gbl.mon_ID].mainSizer)
            self.notebookPages[gbl.mon_ID].Layout()
            self.Layout()

    # ------------------------------------------------------------------------- update notebook after add/delete monitor
    def repaginate(self):
        # page 0 (config page) will not be affected except for thumbnails

        self.Unbind(wx.EVT_NOTEBOOK_PAGE_CHANGING)             # prevent changes from triggering events
        self.Unbind(wx.EVT_NOTEBOOK_PAGE_CHANGED)             # prevent changes from triggering events

        # -------------------------------------------------------------------- delete each page from notebook (except 0)
        for gbl.mon_ID in range(len(self.notebookPages)-1, 0, -1):
            self.notebookPages[gbl.mon_ID].clearVideo()      # stop & remove video, timer, and thread for monitor pages
            del self.notebookPages[gbl.mon_ID]               # remove page from list of pages
            self.DeletePage(gbl.mon_ID)                      # remove page from notebook object

        # --------------------------------------------------------- stop configuration page thumbnail and console timers
        self.notebookPages[0].scrolledThumbs.clearGrid()

        # -------------------------------------------------------------------------------------- recreate notebook pages
        cfg.cfg_dict_to_nicknames()                  # load configuration parameters into globals
        self.notebookPages[0].scrolledThumbs.thumbPanels = ['videoMonitors']  # initiate a new thumbnail list;

        # ----------------------------------------------------------------------------------- add back each monitor page
        for gbl.mon_ID in range(1, gbl.monitors+1):                         # pages are numbered by monitor number
            cfg.mon_dict_to_nicknames()                                     # load monitor configuration into globals
            gbl.mon_name = 'Monitor%d' % gbl.mon_ID                         # correct mon_name
            cfg.mon_nicknames_to_dicts(gbl.mon_ID)                          # save new mon_name
            self.addMonitorPage()                                           # add monitor page to notebook

        self.notebookPages[0].fillTable()                                   # update the configuration table
        self.notebookPages[0].scrolledThumbs.refreshThumbGrid()             # update the scrolled thumbs window

        gbl.mon_ID = 0          # ------------------------------------------------------------ go to configuration page
        self.SetSelection(gbl.mon_ID)

        self.notebookPages[0].scrolledThumbs.EnableScrolling(1, 1)
        self.notebookPages[0].Layout()

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onPageChanging)         # restore binding
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,  self.onPageChanged)          # restore binding

""" ========================================================================================================= Main Frame
"""
class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self.config = cfg.Configuration(self)        # let user select a configuration to load before starting

        gbl.statbar = wx.StatusBar(self, wx.ID_ANY)  # status bar
        self.SetStatusBar(gbl.statbar)
        gbl.statbar.SetStatusText('Status Bar')

        self.theNotebook = mainNotebook(self)        # build the notebook

        self.__set_properties("pySolo Video", 0.95)  # set title and frame/screen ratio
        self.__do_layout()

        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(self.theNotebook, 1, wx.EXPAND, 0)
        self.SetSizer(mainSizer)
        self.Layout()


        print('done.')

    # -------------------------------------------------------------------------------------------- Set window properties
    def __set_properties(self, window_title, size_ratio):
        """
        Set the title of the main window.
        Set the size of the main window relative to the size of the user's display.
        Center the window on the screen.


        Get screen_width & screen_height:   Screen resolution information
              Allows all object sizes to be sized relative to the display.
        """
        screen_width = GetSystemMetrics(0)  # get the screen resolution of this monitor
        screen_height = GetSystemMetrics(1)

        # begin wxGlade: mainFrame.__set_properties
        self.SetTitle(window_title)  # set window title
        self.SetSize((screen_width * size_ratio,
                      screen_height * size_ratio))  # set size of window
        self.Center()  # center the window

    # ------------------------------------------------------------------------------------ apply notebook to main window
    def __do_layout(self):

        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(self.theNotebook, 1, wx.EXPAND, 0)
        self.SetSizer(mainSizer)


""" ####################################################################################################### Main Program
"""
if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()

    frame_1 = mainFrame(None, -1, '')           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

#    wx.lib.inspection.InspectionTool().Show()   # starts a GUI inspection tool that helps evaluate structures in a window

    app.MainLoop()                              # Begin user interactions.


