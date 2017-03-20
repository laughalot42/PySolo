#include <wx/grid.h>

"""  ********************************************************************************
-----------   ***   "prj" is used instead of "cfg"  *** ----------------------------
     ********************************************************************************
"""

import os
import subprocess
import threading

import wx
import wx.grid as gridlib

import videoMonitor
from configurator import Configuration
from filebrowsebutton_LL import FileBrowseButton



class progressTimer(wx.Timer):
    """
    triggers event periodically to process next frame in video
    """
    def __init__(vidMon):
        wx.Timer.__init__(vidMon)
        vidMon.timer = wx.Timer(vidMon, wx.ID_ANY)

class acquireThread(threading.Thread):
    """
    allows multiple processes to run at the same time so videos can run simultaneously
    """
    def __init__(prj, parent, mon_num, cfg_dict):
        threading.Thread.__init__(prj)

        prj.parent = parent
        prj.progressTimer = parent.progressTimer

        prj.mon_num = mon_num                                  # use to identify this thread

        prj.track = cfg_dict[mon_num]['track']                 # avoid changing everything to refer to the dictionary
        prj.dataFolder = cfg_dict[mon_num]['datafolder']
        prj.source = cfg_dict[mon_num]['source']
        prj.track_type = cfg_dict[mon_num]['tracktype']
        prj.mask_file = cfg_dict[mon_num]['maskfile']
        prj.outputFile = os.path.join(prj.dataFolder, 'Monitor%02d.txt' % (prj.mon_num +1))   # account for computer indexing diff from humans

        prj.mon = thumbnails.monitorPanel(parent, config, mon_num)
        prj.setTracking()

    def setTracking(prj):
        """
        Set the tracking parameters

        track       Boolean     Do we do tracking of flies?
        trackType   0           tracking using the virtual beam method
                    1 (Default) tracking calculating distance moved
        mask_file   text        the file used to load and store masks
        outputFile  text        the txt file where results will be saved
        """
        """
        if prj.mask_file:
            return maskPanel.maskMakerPanel.loadROIS(, prj.mask_file)
        """
        print('acquirePanel:  set tracking')

    def doTrack(prj):
        """
        """
        prj.mon.tracking = True
        prj.start()

    def start(prj):
        """
        """
        prj.mon.tracking = True
        prj.run()

    def run(prj, kbdint=False):
        """
        checks to see if program should keep going.
        """
        prj.keepGoing = True
        while prj.mon.tracking:
            prj.mon.GetImage()

    def halt(prj):

        """
        """
        prj.keepGoing = False
        prj.halt()

class acquireTable(wx.Panel):
    """
    displays table of configuration parameters
    """
    def __init__(prj, parent, cfg_dict, size=(800,200)):
        wx.Panel.__init__(prj, parent, size=size)

        prj.parent = parent
        prj.cfg_dict = cfg_dict
        prj.n_mons = cfg_dict[0]['monitors']

    # ------------------------------------------------------------------------------------------------- create the table
        prj.colLabels = ['Monitor', 'Track type', 'Track', 'Source', 'Mask', 'Output']

        prj.acqGrid = gridlib.Grid(prj)
        prj.acqGrid.CreateGrid(prj.n_mons, len(prj.colLabels))
        prj.acqGrid.SetRowLabelSize(0)                    # no need to show row numbers
        prj.acqGrid.EnableEditing(False)                  # user should not make changes here   TODO: change this and allow changes from Acquire?

        for colnum in range(0, len(prj.colLabels)):
            prj.acqGrid.SetColLabelValue(colnum, prj.colLabels[colnum])       # apply labels to columns

        prj.fillTable(prj.cfg_dict)                  # fill the table using config info

        prj.sizers()

    def sizers(prj):
        prj.tableSizer = wx.BoxSizer(wx.VERTICAL)
        prj.tableSizer.Add(prj.acqGrid,                 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 2)  # -- Cfg table

        prj.SetSizer(prj.tableSizer)

    def fillTable(prj, cfg_dict):      # ----------------------------------------- # use cfg dictionary to fill in table

        prj.cfg_dict = cfg_dict

        prj.progressTimer = progressTimer()            # timer that plays videos

        currentrows = prj.acqGrid.GetNumberRows()                    # clear the grid & resize to fit new configuration
        prj.acqGrid.AppendRows(cfg_dict[0]['monitors'], updateLabels=False)
        prj.acqGrid.DeleteRows(0, currentrows, updateLabels=False)                     # deletes old rows

        prj.monitors = ['no monitor 0']                                 # preload the 0 element to keep indexing straight

        for mon_num in range(1, prj.n_mons +1):                         # prep monitor list for tracking
            if prj.cfg_dict[mon_num]['track']:                                         # dictionary is 1-indexed
                prj.monitors.append(acquireThread(prj, mon_num, prj.cfg_dict))

#        for mon_num in range(1, prj.n_mons +1):

        # columns are: 'Monitor', 'Track type', 'Track', 'Source', 'Mask', 'Output'

            # monitor name
            prj.acqGrid.SetCellValue(mon_num - 1, 0, 'Monitor %d' % mon_num)   # row numbers are 0-indexed
            prj.acqGrid.SetCellAlignment(mon_num-1, 0,  wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

            # track type
            tracktype = cfg_dict[mon_num]['tracktype']
            if tracktype == 0: tracktype = 'Distance'
            elif tracktype == 1: tracktype = 'Virtual BM'
            elif tracktype == 2: tracktype = 'Position'
            prj.acqGrid.SetCellValue(mon_num - 1, 1, tracktype)
            prj.acqGrid.SetCellAlignment(mon_num-1, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

            # track
            track = cfg_dict[mon_num]['track']
            prj.acqGrid.SetCellValue(mon_num - 1, 2, str(track))
            prj.acqGrid.SetCellAlignment(mon_num-1, 2, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

            sourcefile = os.path.split(cfg_dict[mon_num]['source'])[1]
            prj.acqGrid.SetCellValue(mon_num - 1, 3, sourcefile)

            maskfile = os.path.split(cfg_dict[mon_num]['maskfile'])[1]
            prj.acqGrid.SetCellValue(mon_num - 1, 4, maskfile)

            # output file name
            outfile = os.path.join(cfg_dict[mon_num]['datafolder'], ('Monitor%d.txt' % mon_num))
            prj.acqGrid.SetCellValue(mon_num - 1, 5, outfile)

        prj.acqGrid.AutoSize()                     # cell size based on contents

        prj.Layout()

    def onChangeCfgFile(prj, newfile):       # ------------------------------------------------  new config file selected

        config = Configuration(prj, newfile)
        prj.cfg_dict = config.cfg_dict

        prj.fillTable(prj.cfg_dict)                             # put new configuration into the table


class projectPage(wx.Panel):
    """
    configuration summary and controls for processing
    """
    def __init__(prj, parent, cfg_dict, size=(800, 200)):
        wx.Panel.__init__(prj, parent, size=size)

        prj.cfg_dict = cfg_dict

        prj.makeWidgets()
        prj.sizers()

    def makeWidgets(prj):  # --------------------------------------------------------------------- create the buttons
        prj.cfgTable = acquireTable(prj, prj.cfg_dict)

        prj.pickConfigFile = FileBrowseButton(prj, id=wx.ID_ANY,
                                              labelText='Configuration', buttonText='Browse',
                                              dialogTitle='Choose a configuration file',
                                              startDirectory=prj.cfg_dict[0]['cfgfolder'],
                                              wildfire='*.*', style=wx.ALL,
                                              changeCallback=prj.onBrowse, name='cfgBrowseButton')

        prj.btnStart = wx.Button(prj, wx.ID_ANY, label='Start Acquisition')
        prj.Bind(wx.EVT_BUTTON, prj.onStart, prj.btnStart)
        prj.btnStart.Enable(True)

        prj.btnStop = wx.Button(prj, wx.ID_ANY, label='Stop')
        prj.Bind(wx.EVT_BUTTON, prj.onStop, prj.btnStop)
        prj.btnStop.Enable(False)

        prj.btnDAMFS = wx.Button(prj, wx.ID_ANY, label='DAMFileScan110X')
        prj.Bind(wx.EVT_BUTTON, prj.onDAMFileScan110X, prj.btnDAMFS)


    def sizers(prj):
        prj.btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        prj.DAMFS_Sizer = wx.BoxSizer(wx.HORIZONTAL)

        prj.btnSizer.Add(prj.btnStart,          0, wx.ALL, 2)  # ---------------------------- Start & Stop btns
        prj.btnSizer.Add(prj.btnStop,           0, wx.ALL, 2)

        prj.btnSizer.Add(prj.btnDamFileScan,    0, wx.ALL, 2)
        prj.btnSizer.Add(prj.SCAMP,             0, wx.ALL, 2)

        prj.acqSizer.Add(prj.pickConfigFile,   0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 2)  # ---- Config File Browser
        prj.acqSizer.AddSpacer(20)


    def showPanel(prj):        # ----------------------------------------------------------------------------------- sizers
        prj.acqSizer = wx.BoxSizer(wx.VERTICAL)
        prj.acqSizer.AddSpacer(20)
        prj.acqSizer.Add(prj.btnSizer,         0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 2)
        prj.acqSizer.AddSpacer(20)

        prj.SetSizer(prj.acqSizer)

    def onBrowse(prj, event):
        config = Configuration(prj.pickConfigFile)                  # get new dictionary
        prj.cfg_dict = config.cfg_dict

        prj.cfgTable.fillTable(prj.cfg_dict)                        # update config Table

    def onStart(prj, event):
        for mon_num in range(1, prj.n_mons +1):
            prj.cfgTable.monitors[mon_num].start()

    def onDAMFileScan110X(prj, event):
        cmd = os.path.join(os.getcwd(), 'DAMFileScan110X', 'DAMFileScan110.exe')
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        process.wait()

        def onStart(prj, event=None):
            prj.acquiring = True
            #        prj.btnStop.Enable(True)
            #        prj.btnStart.Enable(False)                # TODO: enable commands don't work until program returns to MainLoop
            #        prj.btnStop.Refresh()
            #        prj.Refresh()
            #        event.Skip()

            for mon_num in range(1, prj.n_mons + 1):
                if cfg_dict[mon_num]['track']:
                    prj.monitors[mon_num - 1].doTrack()  # monitors is 0-indexed

                    #        prj.parent.sb.SetStatusText('Tracking %s Monitors' % (str(int(c))))

        """
        def onStop(prj, event):
            prj.acquiring = False
            prj.btnStop.Enable(False)
            prj.btnStart.Enable(True)
            for mon_num in range(1, prj.n_mons+1):
                prj.monitors[mon_num].halt()
        """




    def globalToDict(prj):             # save the global configuration settings
        print('save global settings to dictionary')
    def globalToObj(prj):
        print('save global settings to configObj')


# ------------------------------------------------------------------------------------------ Stand alone test code
#  insert other classes above and call them in mainFrame
#
class mainFrame(wx.Frame):

    def __init__(prj, *args, **kwds):

        wx.Frame.__init__(prj, None, id=wx.ID_ANY, size=(1000,200))

        config = Configuration(prj, 'C:\Users\Lori\PyCharmProjects\pysolo_modular\Data\pysolo_config.cfg')
        frame_acq = projectPage(prj, config)  # Create the main window.
        app.SetTopWindow(frame_acq)

        print('done.')

if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.

#

