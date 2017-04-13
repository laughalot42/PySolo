import wx                               # GUI controls
import os
import winsound
import wx.lib.masked as masked
from filebrowsebutton_LL import FileBrowseButton, DirBrowseButton
from wx.lib.masked import NumCtrl

import configurator as cfg
import videoMonitor as VM
import pysolovideoGlobals as gbl


class maskMakerPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY, size=(640,480), name=gbl.mon_name)


        self.parent = parent
        cfg.cfg_dict_to_nicknames()       # set all nicknames for this monitor.  use these so changes will be saved on page change.
        cfg.mon_dict_to_nicknames()

        self.widgets()
        self.binders()
        self.sizers()

    def widgets(self):

        # TODO: get coordinate values by clicking the mouse
        # TODO: add PySolo single ROI drawing

    # ------------------------------------------------------------------------------------------------------------ Title
        self.title = wx.StaticText(self, -1, "\n %s" % gbl.mon_name)  # title
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.title.SetFont(font)

    # --------------------------------------------------------------------------------------- ROI Coordinates Input Grid
        self.row_labels = [wx.StaticText(self, -1, ' '),
                           wx.StaticText(self, -1, 'Number'),                        # row labels
                           wx.StaticText(self, -1, 'Top Left'),
                           wx.StaticText(self, -1, 'Span'),
                           wx.StaticText(self, -1, 'Gap'),
                           wx.StaticText(self, -1, 'Tilt')
                           ]
        self.X = []
        self.Y = []
        self.X.append(wx.StaticText(self, wx.ID_ANY, "Columns (X)"))                    # column header for columns
        self.Y.append(wx.StaticText(self, wx.ID_ANY, "Rows (Y)"))                      # column header for rows
        for cnt in range(0,5):
            self.X.append(NumCtrl(self, wx.ID_ANY, 0))
            self.Y.append(NumCtrl(self, wx.ID_ANY, 0))

    # -------------------------------------------------------------------------------------------- instructional diagram
        self.diagram = wx.Bitmap(os.path.join(gbl.exec_dir, 'maskmakerdiagram.bmp'), wx.BITMAP_TYPE_BMP)
        self.diagramctl = wx.StaticBitmap(self, -1, self.diagram)

    # ------------------------------------------------------------------------------------ mask generator & save buttons
        self.btnMaskGen = wx.Button(self, wx.ID_ANY, label="Generate Mask", size=(130,25))
        self.btnMaskGen.Enable(True)

        self.btnSaveMask = wx.Button(self, wx.ID_ANY, label="Save Mask", size=(130,25))
        self.btnSaveMask.Enable(True)

    # -------------------------------------------------------------------------------------------- video display options
        self.previewPanel = VM.monitorPanel(self, mon_ID=gbl.mon_ID, panelType='thumb', loop=True)

        self.previewPanel.PlayMonitor()                                    # start video

        self.previewSizeLabel = wx.StaticText(self, wx.ID_ANY, 'frame size =')           # ------ preview frame size
        self.previewSize = wx.TextCtrl (self, wx.ID_ANY, str(gbl.preview_size),
                                              style=wx.TE_PROCESS_ENTER, name='Viewer Size')

        self.previewFPSLabel = wx.StaticText(self, wx.ID_ANY, 'preview fps =')         # --------- preview video fps
        self.previewFPS = wx.TextCtrl (self, wx.ID_ANY, str(gbl.preview_fps),
                                              style=wx.TE_PROCESS_ENTER, name='Viewer FPS')

        self.lineThicknessLabel = wx.StaticText(self, wx.ID_ANY, 'ROI line thickness =')  # --------- preview ROI line thickness
        self.lineThickness = wx.TextCtrl(self, wx.ID_ANY, str(gbl.line_thickness),
                                              style=wx.TE_PROCESS_ENTER, name='ROI line thickness')

    # -------------------------------------------------------------------------------------------------------- source
        self.txt_source = wx.StaticText(self, wx.ID_ANY, "Source:  ")
        self.currentSource = wx.TextCtrl (self, wx.ID_ANY, gbl.source, style=wx.TE_READONLY)    # get current source

        # -------------------------------------------------------------------------------  Webcam selection combobox
#        if len(gbl.webcams_inuse) >= gbl.webcams:                          # only one webcam implemented at this time
#            self.WebcamsList = ['No more webcams available.']
#        else:
#        self.WebcamsList = ['Webcam %s' % (int(w) + 1) for w in range(gbl.webcams)]
        self.WebcamsList = ['Webcam 1']

        # ------------------------------------------------------------------------------------------- source options
        self.sources = [(wx.ComboBox(self, wx.ID_ANY, choices=self.WebcamsList, name='Webcam',                # webcam
                                style= wx.EXPAND | wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)),
                        (FileBrowseButton(self, id=wx.ID_ANY,                                       # video file
                                name='File', buttonText='Browse',
                                toolTip='Type filename or click browse to choose video file',
                                dialogTitle='Choose a video file',
                                startDirectory=gbl.data_folder,
                                wildcard='*.*', style=wx.ALL, changeCallback=self.onChangeSource1)),
                        (DirBrowseButton(self, id=wx.ID_ANY, name='Folder',                     # folder of images
                                style=wx.DD_DIR_MUST_EXIST,
                                startDirectory=gbl.data_folder, changeCallback=self.onChangeSource2))
                        ]

        # --------------------------------------------------------------------------------  source type radio buttons
        self.rbs = [(wx.RadioButton(self, wx.ID_ANY, 'Camera', style=wx.RB_GROUP)),
                   (wx.RadioButton(self, wx.ID_ANY, 'File')),
                   (wx.RadioButton(self, wx.ID_ANY, 'Folder'))
                   ]

   # ------------------------------------------------------------------------------------------------- video attributes
        self.sourceFPSLabel = wx.StaticText(self, wx.ID_ANY, 'Speed (fps) =')           # ---------------- source fps
        self.sourceFPS = wx.TextCtrl (self, wx.ID_ANY, str(gbl.source_fps),
                                              style=wx.TE_PROCESS_ENTER, name='Source FPS')

        self.txt_date = wx.StaticText(self, wx.ID_ANY, "Date: ")                        # ---------------- start date
        self.start_date = wx.DatePickerCtrl(self, wx.ID_ANY, dt=gbl.start_datetime, style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY)

        self.txt_time = wx.StaticText(self, wx.ID_ANY, 'Time: (24-hr) ')                 # ---------------- start time
        self.btnSpin = wx.SpinButton(self, wx.ID_ANY, wx.DefaultPosition, (-1, 20), wx.SP_VERTICAL)
        starttime = gbl.wxdatetime2string(gbl.start_datetime)
        self.start_time = masked.TimeCtrl(self, wx.ID_ANY, value=starttime,
                                          name='time: \n24 hour control', fmt24hr=True,
                                          spinButton=self.btnSpin)

    # ------------------------------------------------------------------------------------------------ activate tracking
        self.trackBox = wx.CheckBox(self, wx.ID_ANY, 'Activate Tracking')
        self.trackBox.Enable(True)
        self.trackBox.SetValue(gbl.track)

    # ---------------------------------------------------------------------------------------- sleep deprivation monitor
        self.isSDMonitor = wx.CheckBox(self, wx.ID_ANY, 'Sleep Deprivation Monitor')
        self.isSDMonitor.Enable(True)
        self.isSDMonitor.SetValue(gbl.issdmonitor)

    # ---------------------------------------------------------------------------------------------------- tracking type
        self.trackChoice = [(wx.RadioButton(self, wx.ID_ANY, 'Activity as distance traveled', style=wx.RB_GROUP)),
                            (wx.RadioButton(self, wx.ID_ANY, 'Activity as midline crossings count')),
                            (wx.RadioButton(self, wx.ID_ANY, 'Only position of flies'))]

        for count in range(0, len(self.trackChoice)):
            self.trackChoice[count].Enable(True)
            if gbl.track_type == count:
                self.trackChoice[count].SetValue(True)
            else:
                self.trackChoice[count].SetValue(False)

     # ------------------------------------------------------------------------------------------------ mask file browser
        wildcard = 'PySolo Video mask file (*.msk)|*.msk|' \
                   'All files (*.*)|*.*'                # adding space in here will mess it up!

        if gbl.mask_file == None:
            gbl.mask_file = ''
        if os.path.isfile(gbl.mask_file):
            startDirectory = os.path.split(gbl.mask_file)[0]  # Default directory for file dialog startup
            initialValue = gbl.mask_file
        else:
            startDirectory = gbl.data_folder,  # Default directory for file dialog startup
            initialValue = "",

        self.pickMaskBrowser = FileBrowseButton(self,id =  wx.ID_ANY,
                                        labelText = 'Mask File:         ', buttonText = 'Browse',
                                        toolTip = 'Type filename or click browse to choose mask file',
                                        dialogTitle = 'Choose a mask file',
                                        startDirectory = startDirectory, initialValue=initialValue,
                                        wildcard = wildcard, style = wx.ALL,
                                        changeCallback = self.onMaskBrowse,
                                        name = 'maskBrowseButton')

    # -------------------------------------------------------------------------------------------- output folder browser
        self.pickOutputBrowser = DirBrowseButton(self,id =  wx.ID_ANY,
                                        style=wx.TAB_TRAVERSAL,
                                        labelText= 'Output Folder:  ',
                                        dialogTitle = 'Choose an output folder',
                                        startDirectory = gbl.data_folder,
                                        name = 'OutputBrowseButton')

        self.pickOutputBrowser.SetValue(gbl.data_folder)

    # ---------------------------------------------------------------------------------------  Save Configuration Button
        self.btnSaveCfg = wx.Button( self, wx.ID_ANY, label='Save Configuration', size=(130,25))
        if gbl.source != '':
            self.btnSaveCfg.Enable(True)                    # don't allow save if no source is selected
        else:
            self.btnSaveCfg.Enable(False)

    # ---------------------------------------------------------------------------------------  Delete Monitor Button
        self.monitors = gbl.monitors
        self.btnRemoveMonitor = wx.Button( self, wx.ID_ANY, label='Delete Monitor', size=(130,25))
        if gbl.monitors == 1:                        # don't allow last monitor to be deleted
            self.btnRemoveMonitor.Enable(False)
        else:
            self.btnRemoveMonitor.Enable(True)

    def binders(self):  # -------------------------------------------------------------------------------- Event Binders

        self.Bind(wx.EVT_RADIOBUTTON,       self.onChangeRb,            self.rbs[0])
        self.Bind(wx.EVT_RADIOBUTTON,       self.onChangeRb,            self.rbs[1])
        self.Bind(wx.EVT_RADIOBUTTON,       self.onChangeRb,            self.rbs[2])
        self.Bind(wx.EVT_COMBOBOX,          self.onChangeSource0,       self.sources[0])
        self.Bind(wx.EVT_TEXT,              self.onChangeSource1,       self.sources[1])
        self.Bind(wx.EVT_TEXT,              self.onChangeSource2,       self.sources[2])
        self.Bind(wx.EVT_BUTTON,            self.onSaveCfg,             self.btnSaveCfg)
        self.Bind(wx.EVT_BUTTON,            self.onRemoveMonitor,       self.btnRemoveMonitor)
        self.Bind(wx.EVT_TEXT_ENTER,        self.onChangePreviewSize,   self.previewSize)
        self.Bind(wx.EVT_TEXT_ENTER,        self.onChangePreviewFPS,    self.previewFPS)
        self.Bind(wx.EVT_TEXT_ENTER,        self.onChangeLineThickness, self.lineThickness)
        self.Bind(wx.EVT_BUTTON,            self.onMaskGen,             self.btnMaskGen)
        self.Bind(wx.EVT_BUTTON,            self.onMaskBrowse,          self.pickMaskBrowser)
        self.Bind(wx.EVT_BUTTON,            self.onSaveMask,            self.btnSaveMask)
        self.Bind(wx.EVT_RADIOBUTTON,       self.onChangeTrackType,     self.trackChoice[0])
        self.Bind(wx.EVT_RADIOBUTTON,       self.onChangeTrackType,     self.trackChoice[1])
        self.Bind(wx.EVT_RADIOBUTTON,       self.onChangeTrackType,     self.trackChoice[2])
        self.Bind(wx.EVT_TEXT,              self.onChangeOutput,        self.pickOutputBrowser)

    def sizers(self):
        self.mainSizer              = wx.BoxSizer(wx.HORIZONTAL)                                #   Main
        self.leftSizer              = wx.BoxSizer(wx.VERTICAL)                                  #   |   Left
        self.sb_selectsource        = wx.StaticBox(self, wx.ID_ANY, 'Select Source')            #   |   |   source selection text
        self.sbSizer_selectsource   = wx.StaticBoxSizer(self.sb_selectsource, wx.VERTICAL)      #   |   |   select box
        self.sourceGridSizer        = wx.FlexGridSizer(5, 2, 2, 2)                              #   |   |   |   |   grid of rbs & sources
        self.sb_maskNoutput         = wx.StaticBox(self, wx.ID_ANY, '')                         #   |   |   monitor selection text
        self.sbSizer_maskNoutput    = wx.StaticBoxSizer(self.sb_maskNoutput, wx.VERTICAL)       #   |   |   |   select box
        self.maskBrowserSizer       = wx.BoxSizer(wx.HORIZONTAL)                                #   |   |   |   |   mask browser
        self.outputDirSizer         = wx.BoxSizer(wx.HORIZONTAL)                                #   |   |   |   |   output dir browser
        self.leftMiddleSizer        = wx.BoxSizer(wx.HORIZONTAL)                                #   |   |   left middle
        self.sb_timeSettings        = wx.StaticBox(self, wx.ID_ANY, 'Time Settings')            #   |   |   |   time settings text
        self.sbSizer_timeSettings   = wx.StaticBoxSizer(self.sb_timeSettings, wx.VERTICAL)      #   |   |   |   time settings box
        self.dt_Sizer               = wx.FlexGridSizer(3, 2, 2, 2)                              #   |   |   |   |   |   datetimefps widgets
        self.sb_trackingParms       = wx.StaticBox(self, wx.ID_ANY, 'Tracking Parameters')      #   |   |   |   tracking parameters text
        self.sbSizer_trackingParms  = wx.StaticBoxSizer(self.sb_trackingParms, wx.VERTICAL)     #   |   |   tracking parameters box
        self.trackOptionsSizer      = wx.BoxSizer(wx.VERTICAL)                                  #   |   |   |   |   |   tracking options widgets
        self.calcbox_sizer          = wx.BoxSizer(wx.VERTICAL)                                  #   |   |   |   |   |   calculations widgets
        self.leftBottomSizer        = wx.BoxSizer(wx.HORIZONTAL)                                #   |   |   left bottom
        self.diagramSizer           = wx.BoxSizer(wx.HORIZONTAL)                                #   |   |   |   diagram
        self.tableSizer             = wx.FlexGridSizer(6, 3, 1, 5)                              #   |   |   |   table
        self.button_sizer           = wx.BoxSizer(wx.VERTICAL)                                  #   |   |   |   buttons column

        self.rightSizer             = wx.BoxSizer(wx.VERTICAL)                                  #   |   Right
        self.titleSizer             = wx.BoxSizer(wx.HORIZONTAL)                                #   |   |   Monitor title
        self.saveNdeleteSizer       = wx.BoxSizer(wx.HORIZONTAL)                                #   |   |   save and delete buttons
        self.videoSizer             = wx.BoxSizer(wx.HORIZONTAL)                                #   |   |   video panel
        self.settingsSizer          = wx.BoxSizer(wx.HORIZONTAL)                                #   |   |   preview settings


# ------------------------------------------------------------------------------------------------------------LEFT SIDE
    # -------------------------------------------------------------------------------------------- select source box

        self.sourceGridSizer.Add(self.txt_source,                       0, wx.ALL | wx.LEFT,     5)
        self.sourceGridSizer.Add(self.currentSource,                    1, wx.ALL | wx.EXPAND,   5)

        for count in range(0, len(self.rbs)):
            self.sourceGridSizer.Add(self.rbs[count],                   0, wx.ALL | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
            self.sourceGridSizer.Add(self.sources[count],               1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)

        self.sbSizer_selectsource.Add(self.sourceGridSizer,             1, wx.ALL | wx.EXPAND,   5)

        # -------------------------------------------------------------------------- mask browser, output folder browser
        self.sbSizer_maskNoutput.Add(self.pickMaskBrowser,              1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND, 5)
        self.sbSizer_maskNoutput.Add(self.pickOutputBrowser,            1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND, 5)

        # --------------------------------------------------------------------------------- time, tracking, buttons row
        # --------------------------------------------- date / time / fps grid
        self.dt_Sizer.Add(self.txt_date,                                0, wx.ALL, 5)
        self.dt_Sizer.Add(self.start_date,                              0, wx.ALL, 5)

        self.dt_Sizer.Add(self.txt_time,                                0, wx.ALL, 5)
        self.addWidgets(self.dt_Sizer, [self.start_time, self.btnSpin])

        self.dt_Sizer.Add(self.sourceFPSLabel,                          0, wx.ALL, 5)
        self.dt_Sizer.Add(self.sourceFPS,                               0, wx.ALL, 5)

        # fill video start date and time box
        self.sbSizer_timeSettings.Add(self.dt_Sizer,                    0, wx.ALL, 5)

        # ------------------------------------------------- tracking options
        self.trackOptionsSizer.Add(self.trackBox,                       0, wx.ALL | wx.ALIGN_LEFT, 5)
        self.trackOptionsSizer.Add(self.isSDMonitor,                    0, wx.ALL | wx.ALIGN_LEFT, 5)

        for count in range(0, len(self.trackChoice)):
            self.calcbox_sizer.Add(self.trackChoice[count],             0, wx.ALL | wx.ALIGN_LEFT, 5)
        self.trackOptionsSizer.Add(self.calcbox_sizer,                  0, wx.ALL | wx.ALIGN_LEFT, 5)

        # fill tracking box
        self.sbSizer_trackingParms.Add(self.trackOptionsSizer,          0, wx.ALL, 5)


        # fill middle row
        self.leftMiddleSizer.Add(self.sbSizer_timeSettings,             2, wx.ALL | wx.EXPAND, 5)
        self.leftMiddleSizer.Add(self.sbSizer_trackingParms,            2, wx.ALL | wx.EXPAND, 5)

        # ---------------------------------------------------------------------------------------------- mask generator
        self.diagramSizer.Add(self.diagramctl,                          0, wx.ALL | wx.ALIGN_CENTER, 2)

        # -------------------------------------------------------------------- Apply each row to the table
        for row in range(0, len(self.row_labels)):
            self.tableSizer.Add(self.row_labels[row],                   1, wx.ALL | wx.EXPAND, 5)  # column headers
            self.tableSizer.Add(self.X[row],                            1, wx.ALL | wx.EXPAND, 5)  # X column entries
            self.tableSizer.Add(self.Y[row],                            1, wx.ALL | wx.EXPAND, 5)  # Y column entries

        # -------------------------------------------------------------------------------------- button column
        self.button_sizer.Add(self.btnMaskGen,                          1, wx.ALL, 5)
        self.button_sizer.Add(self.btnSaveMask,                         1, wx.ALL, 5)

        # fill left bottom
        self.leftBottomSizer.Add(self.diagramSizer,                     0, wx.ALL | wx.ALIGN_CENTER, 2)
        self.leftBottomSizer.Add(self.tableSizer,                       0, wx.ALL | wx.ALIGN_CENTER, 2)
        self.leftBottomSizer.Add(self.button_sizer,                     1, wx.ALL | wx.ALIGN_BOTTOM, 5)

        self.leftSizer.Add(self.sbSizer_selectsource,                   1, wx.ALL | wx.EXPAND,   5)
        self.leftSizer.Add(self.sbSizer_maskNoutput,                    1, wx.ALL | wx.EXPAND,   5)
        self.leftSizer.Add(self.leftMiddleSizer,                        1, wx.ALL | wx.EXPAND,   5)
        self.leftSizer.Add(self.leftBottomSizer,                        1, wx.ALL | wx.EXPAND,   5)


        # ------------------------------------------------------------------------------ Right Side  Video Preview Panel

        self.saveNdeleteSizer.Add(self.btnSaveCfg,                      1, wx.ALL, 5)
        self.saveNdeleteSizer.Add(self.btnRemoveMonitor,                1, wx.ALL, 5)

        #                                      this sizer saves the spot in rightSizer in case video is changed later
        self.videoSizer.Add(self.previewPanel,                          1, wx.ALL | wx.ALIGN_TOP, 5)

        self.settingsSizer.AddSpacer(5)
        self.settingsSizer.Add(self.previewSizeLabel,                   0, wx.ALL | wx.EXPAND, 5)
        self.settingsSizer.Add(self.previewSize,                        0, wx.ALL | wx.EXPAND, 5)
        self.settingsSizer.AddSpacer(5)
        self.settingsSizer.Add(self.previewFPSLabel,                    0, wx.ALL | wx.EXPAND, 5)
        self.settingsSizer.Add(self.previewFPS,                         0, wx.ALL | wx.EXPAND, 5)
        self.settingsSizer.AddSpacer(5)
        self.settingsSizer.Add(self.lineThicknessLabel,                 0, wx.ALL | wx.EXPAND, 5)
        self.settingsSizer.Add(self.lineThickness,                      0, wx.ALL | wx.EXPAND, 5)
        self.settingsSizer.AddSpacer(5)

        self.rightSizer.Add(self.title,                                 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 1)
        self.rightSizer.Add(self.videoSizer,                            1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.rightSizer.Add(self.settingsSizer,                         0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.rightSizer.Add(self.saveNdeleteSizer,                      0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM, 5)

   # ------------------------------------------------------------------------------------------- left & right sides
        self.mainSizer.Add(self.leftSizer,                              1, wx.ALL | wx.ALIGN_LEFT, 2)
        self.mainSizer.Add(self.rightSizer,                             1, wx.ALL | wx.ALIGN_RIGHT, 2)

        self.SetSizer(self.mainSizer)
        self.Layout()

    def addWidgets(self, mainSizer ,widgets):       # ---------------------------------------  used for datetime widgets

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        for widget in widgets:
            if isinstance(widget, wx.StaticText):
                sizer.Add(widget,                           0, wx.ALL | wx.CENTER, 1),
            else:
                sizer.Add(widget,                           0, wx.ALL, 1)
        mainSizer.Add(sizer)

    def onRemoveMonitor(self, event):  # ------------------------------------------------------   Remove current monitor

        if gbl.monitors < 1:                                                    # don't remove the last monitor
            self.TopLevelParent.SetStatusText('Cannot remove last monitor.')
            winsound.Beep(600, 200)
            return False

        old_mon = gbl.mon_ID                          # keep track of monitor to be removed

        gbl.cfg_dict.pop(old_mon)                         # delete monitor from dictionary; renumbers list automatically

        if gbl.source[0:6] == 'Webcam':                  # if needed change global copy of number of webcams
            gbl.webcams -= 1  # change number of webcams
#            gbl.webcams_inuse.remove(gbl.mon_name)       # remove name from webcam list

        # ------------------------------------------------------------------------ reset higher numbered monitors' names
        for mon_count in range(old_mon, gbl.monitors):
            gbl.cfg_dict[mon_count]['mon_name'] = 'Monitor%d' % (mon_count)  # change monitor names
#            if gbl.cfg_dict[mon_count]['source'][0:6] == 'Webcam':
#                gbl.cfg_dict[mon_count]['source'][0:6] = 'Webcam%d' % mon_count    # rename webcam    ->  only 1 webcam currently supported

        gbl.monitors -= 1  # ------------------------------------------------------ Change global settings
        if old_mon > gbl.monitors:          # change current monitor number only if last monitor was deleted
            gbl.mon_ID = old_mon - 1

        cfg.cfg_nicknames_to_dicts()       # -------------------------- update config dictionary to change # of monitors
        cfg.mon_dict_to_nicknames()         # ------------------------------------------------- get new monitor settings

        self.parent.repaginate()            # this will delete the notebook pages and recreate the notebook

    def onSaveCfg(self, event):
        cfg.cfg_nicknames_to_dicts()  # -------------------------------------------------- update config dictionary
        r = self.TopLevelParent.config.cfgSaveAs(self)
        if r:                                                               # TODO: progress indicator of some sort?
            self.TopLevelParent.SetStatusText('Configuration saved.')
        else:
            self.TopLevelParent.SetStatusText('Configuration not saved.')
        winsound.Beep(600, 200)

    def clearVideo(self):
        cfg.mon_nicknames_to_dicts()  # save any new monitor settings

        # -------------------------------------------------------------------------------------- kill old monitor panel  TODO: Update mask & settings
        self.previewPanel.keepPlaying = False
        self.previewPanel.playTimer.Stop()
        self.previewPanel.Hide()
        self.previewPanel.Destroy()
        self.videoSizer.Clear()

    def refreshVideo(self):

        self.clearVideo()
        self.previewPanel = VM.monitorPanel(self, mon_ID=gbl.mon_ID, panelType='preview', loop=True)        # make new monitor panel

        self.previewPanel.PlayMonitor()
        self.videoSizer.Add(self.previewPanel, 1, wx.ALL | wx.ALIGN_CENTER, 5)
        self.previewPanel.playTimer.Start(1000 / float(self.previewFPS.GetValue()))
        self.videoSizer.SetMinSize(self.previewPanel.size)
        self.SetSizer(self.mainSizer)
        self.Layout()

    def onChangeTrackType(self, event):
        gbl.track_type = event.Selection
        cfg.mon_nicknames_to_dicts()                                                    # save any new monitor settings

    def onChangeRb(self, event):
        gbl.source_type = event.EventObject.Label

        if self.sources[gbl.source_type].GetValue() != '':
            gbl.source = self.sources[gbl.source_type].GetValue()
            self.currentSource.SetValue(gbl.source)

        cfg.mon_nicknames_to_dicts()                                                    # save any new monitor settings
        self.refreshVideo()

    def onChangeSource0(self, event):                   # TODO: get calling object from event & combine the three onChangeSource functions
        if gbl.cfg_dict[gbl.mon_ID]['source_type'] == 0:                    # if it was a webcam, remove from list
#            gbl.webcams_inuse.remove('Monitor%d' % gbl.mon_ID)                 # only one webcam implemented at this time
            gbl.webcams -= 1

        gbl.source_type = 0
        self.rbs[0].SetValue(True)

        gbl.source = self.sources[gbl.source_type].GetValue()
        self.currentSource.SetValue(gbl.source)
#        gbl.webcams_inuse.append(gbl.mon_name)              # add this monitor to webcam list (only one webcam implemented at this time)
        gbl.webcams += 1

        cfg.mon_nicknames_to_dicts()                        # save changes to dictionary
        self.refreshVideo()                                 # change video playback

    def onChangeSource1(self, event):
        if gbl.cfg_dict[gbl.mon_ID]['source_type'] == 0:                    # if it was a webcam, remove from list
#            gbl.webcams_inuse.remove('Monitor%d' % gbl.mon_ID)                 # only one webcam implemented at this time
            gbl.webcams -= 1
        gbl.source_type = 1
        self.rbs[1].SetValue(True)

        gbl.source = event.EventObject.GetValue()                           # change source information
        self.currentSource.SetValue(gbl.source)

        cfg.mon_nicknames_to_dicts()                                        # save change to dictionary
        self.refreshVideo()

    def onChangeSource2(self, event):
        if gbl.cfg_dict[gbl.mon_ID]['source_type'] == 0:                   # if it was a webcam, remove from list
#            gbl.webcams_inuse.remove('Monitor%d' % gbl.mon_ID)               # only one webcam implemented at this time
            gbl.webcams -= 1

        gbl.source_type = 2
        self.rbs[2].SetValue(True)

        gbl.source = event.EventObject.GetValue()                           # change source information
        self.currentSource.SetValue(gbl.source)

        cfg.mon_nicknames_to_dicts()                                        # save changes to dictionary
        self.refreshVideo()

    def onChangePreviewSize(self, event):
        gbl.preview_size = gbl.correctType(self.previewSize.GetValue(), 'preview_size')
        cfg.mon_nicknames_to_dicts()                        # save change to dictionary
        self.refreshVideo()                                 # close and restart video playback

    def onChangePreviewFPS(self, event):
        gbl.preview_fps = gbl.correctType(self.previewFPS.GetValue(), 'preview_fps')
        cfg.mon_nicknames_to_dicts()                        # save change to dictionary
        self.refreshVideo()                                 # close and restart video playback

    def onChangeLineThickness(self, event):
        gbl.line_thickness = gbl.correctType(self.lineThickness.GetValue(), 'line_thickness')
        cfg.mon_nicknames_to_dicts()                        # save change to dictionary
        self.refreshVideo()                                 # close and restart video playback

    def onChangeOutput(self, event):   # --------------------------------------------------------- change output folder
        gbl.data_folder = self.pickOutputBrowser.GetValue()
        cfg.mon_nicknames_to_dicts()                        # save change to dictionary

    def onMaskBrowse(self, event):      # ------------------------------------------------------ change mask file & ROIs
        gbl.mask_file = self.pickMaskBrowser.GetValue()
        cfg.mon_nicknames_to_dicts()                        # save change to dictionary
        gbl.genmaskflag = False                             # ROIs need to be read from the mask file
        self.refreshVideo()

    def onMaskGen(self, event):
        gbl.genmaskflag = True                              # ROIs need to be read from gbl.ROIs
        self.mask = []  # holds rows for output to a mask file
        gbl.ROIs = []  # holds tuples for drawing ROIs

        mask_dict = {}
        mask_keys = ['columns', 'x1', 'x_len', 'x_sep', 'x_tilt', 'rows', 'y1', 'y_len', 'y_sep', 'y_tilt']

        for count in range(0,5):
            mask_dict[mask_keys[count]] = int(self.X[count+1].GetValue())               # x column

        for count in range(5,10):
            mask_dict[mask_keys[count]] = int(self.Y[count-4].GetValue())               # y column

        ROI = 1  # counter; numbers the ROIs

        for row in range(0, int(mask_dict['rows'])):  # y-coordinates change through rows
            ax = mask_dict['x1'] + row * mask_dict['x_tilt']  # reset x-coordinate start of row
            bx = ax + mask_dict['x_len']
            cx = bx
            dx = ax
            if row == 0:
                ay = mask_dict['y1']
            else:
                ay = mask_dict['y1'] + row * (mask_dict['y_len'] + mask_dict['y_sep'])  # move down in y
            by = ay
            cy = ay + mask_dict['y_len']
            dy = cy
            for col in range(0, mask_dict['columns']):  # x-coordinates change through columns

                # ------------------------------------------------------------------------ create the mask coordinates
                if col == 0 and row == 0:
                    self.mask.append(  # for saving to mask file
                        '(lp1\n((I%d\nI%d\nt(I%d\nI%d\nt(I%d\nI%d\nt(I%d\nI%d\n' % (ax, ay, bx, by, cx, cy, dx, dy))
                else:
                    self.mask.append(
                        'ttp%d\na((I%d\nI%d\nt(I%d\nI%d\nt(I%d\nI%d\nt(I%d\nI%d\n' % (
                        ROI, ax, ay, bx, by, cx, cy, dx, dy))

                gbl.ROIs.append([(ax, ay), (bx, by), (cx, cy), (dx, dy), (ax, ay)])  # for immediate use

                ax = bx + mask_dict['x_sep']  # prepare for next time
                bx = ax + mask_dict['x_len']
                cx = bx
                dx = ax
                ay = ay + mask_dict['y_tilt']
                by = ay
                cy = ay + mask_dict['y_len']
                dy = cy
                ROI += 1

        self.mask.append('ttp%d\na.(lp1\nI1\n' % (ROI + 1))
        self.mask.append('aI1\n' * mask_dict['rows'] * (mask_dict['columns'] -1))
        self.mask.append('a.\n\n\n')

        cfg.mon_nicknames_to_dicts()
        self.refreshVideo()

    def onSaveMask(self, event):            # ---------------------------------------------------  Save new mask to file
        """
        Lets user select file and path where mask will be saved.
        """
        # set file types for find dialog
        wildcard = "PySolo Video config file (*.msk)|*.msk|" \
                   "All files (*.*)|*.*"  # adding space in here will mess it up!

        dlg = wx.FileDialog(self,
                            message="Save mask as file ...",
                            defaultDir=gbl.data_folder,
                            wildcard=wildcard,
                            style=(wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                            )

        if not(dlg.ShowModal() == wx.ID_OK):                     # show the file browser window
            return False

        else:
            gbl.mask_file = dlg.GetPath()                   # get the path from the save dialog

            if os.path.isfile(gbl.mask_file):
                os.remove(gbl.mask_file)                    # get rid of old file before appending data

            with open(gbl.mask_file, 'a') as mask_file:
                for roi in self.mask:
                    mask_file.write(roi)                          # write to file line by line

        dlg.Destroy()
        mask_file.close()

        self.pickMaskBrowser.SetValue(gbl.mask_file)                # update the mask browser textctrl box

        cfg.mon_nicknames_to_dicts()                                # update the dictionary
        self.refreshVideo()

        return True
    
    def onClearMask(self, event):
        gbl.ROIs = []
        cfg.mon_nicknames_to_dicts()
        self.refreshVideo()


###################################################################################### old mask making functions

    def addROI(self, coords, n_flies=1):
        """
        Add the coords for a new ROI and the number of flies we want to track in that area
        selection       (pt1, pt2, pt3, pt4)    A four point selection
        n_flies         1    (Default)      Number of flies to be tracked in that area
        """
        self.arena.addROI(coords, n_flies)

    def getROI(self, n):
        """
        Returns the coordinates of the nth crop area
        """
        return self.arena.getROI(n)

    def delROI(self, n):
        """
        removes the nth crop area from the list
        if n -1, remove all
        """
        self.arena.delROI(n)

    def resizeROIS(self, origSize, newSize):
        """
        Resize the mask to new size so that it would properly fit
        resized images
        """
        return self.arena.resizeROIS(origSize, newSize)

    def isPointInROI(self, pt):
        """
        Check if a given point falls whithin one of the ROI
        Returns the ROI number or else returns -1
        """
        return self.arena.isPointInROI(pt)

    def calibrate(self, pt1, pt2, cm=1):
        """
        Relays to arena calibrate
        """
        return self.arena.calibrate(pt1, pt2, cm)


# ------------------------------------------------------------------------------------------ Stand alone test code
#  insert other classes above and call them in mainFrame
#
class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, *args, **kwds)

        config = cfg.Configuration(self)
        whole = maskMakerPanel(self)




        print('done.')

if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.

#
