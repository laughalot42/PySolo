import wx                               # GUI controls
import os
import winsound
import wx.lib.masked as masked
from filebrowsebutton_LL import FileBrowseButton, DirBrowseButton
import configurator as cfg
import videoMonitor
import pysolovideoGlobals as gbl


class maskMakerPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY, size=(640,480), name=gbl.mon_name)

        self.parent = parent
        gbl.ROIs = gbl.loadROIs(gbl.mask_file)
        gbl.showROIs = True

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
        self.X.append(wx.StaticText(self, -1, "Columns (X)"))                    # column header for columns
        self.Y.append(wx.StaticText(self, -1, "Rows (Y)"))                      # column header for rows
        for cnt in range(0,5):
            self.X.append(wx.TextCtrl(self, -1, ""))
            self.Y.append(wx.TextCtrl(self, -1, ""))

    # -------------------------------------------------------------------------------------------- instructional diagram
        self.diagram = wx.Bitmap(os.path.join(gbl.exec_dir, 'maskmakerdiagram.bmp'), wx.BITMAP_TYPE_BMP)
        self.diagramctl = wx.StaticBitmap(self, -1, self.diagram)

    # ------------------------------------------------------------------------------------ start automask & save buttons
        self.btnMaskGen = wx.Button(self, wx.ID_ANY, label="Generate Mask")
        self.btnMaskGen.Enable(True)

        self.btnSaveMask = wx.Button(self, wx.ID_ANY, label="Save Mask")
        self.btnSaveMask.Enable(True)

    # -------------------------------------------------------------------------------------------- video display options
        self.previewPanel = videoMonitor.monitorPanel(self, mon_ID=gbl.mon_ID, panelType='thumb')       # video panel

        self.previewPanel.PlayMonitor()                                    # start video

        self.previewSizeLabel = wx.StaticText(self, wx.ID_ANY, 'frame size =')           # ------ preview frame size
        self.previewSize = wx.TextCtrl (self, wx.ID_ANY, str(gbl.preview_size),
                                              style=wx.TE_PROCESS_ENTER, name='Viewer Size')

        self.previewFPSLabel = wx.StaticText(self, wx.ID_ANY, 'preview fps =')         # --------- preview video fps
        self.previewFPS = wx.TextCtrl (self, wx.ID_ANY, str(gbl.preview_fps),
                                              style=wx.TE_PROCESS_ENTER, name='Viewer FPS')

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

        self.txt_time = wx.StaticText(self, wx.ID_ANY, 'Time: (24-hr)')                 # ---------------- start time
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

    # ---------------------------------------------------------------------------------------------------- tracking type
        self.trackChoice = [(wx.RadioButton(self, wx.ID_ANY, 'Activity as distance traveled', style=wx.RB_GROUP)),
                            (wx.RadioButton(self, wx.ID_ANY, 'Activity as midline crossings count')),
                            (wx.RadioButton(self, wx.ID_ANY, 'Only position of flies'))]

        for count in range(0, len(self.trackChoice)):
            self.trackChoice[count].Enable(True)
            if gbl.track_type == count: self.trackChoice[count].SetValue(True)
            else: self.trackChoice[count].SetValue(False)

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
                                        labelText = 'Mask File:      ', buttonText = 'Browse',
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
        self.btnSaveCfg = wx.Button( self, wx.ID_ANY, label='Save Configuration', size=(-1,25))
        if gbl.source != '': self.btnSaveCfg.Enable(True)      # don't allow save if no source was selected
        else: self.btnSaveCfg.Enable(False)

    # ---------------------------------------------------------------------------------------  Delete Monitor Button
        self.btnRemoveMonitor = wx.Button( self, wx.ID_ANY, label='Delete Monitor', size=(-1,25))
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
        self.Bind(wx.EVT_TEXT_ENTER,        self.onPreviewFPSnSize,     self.previewSize)
        self.Bind(wx.EVT_TEXT_ENTER,        self.onPreviewFPSnSize,     self.previewFPS)
        self.Bind(wx.EVT_BUTTON,            self.onMaskGen,             self.btnMaskGen)
        self.Bind(wx.EVT_BUTTON,            self.onMaskBrowse,          self.pickMaskBrowser)
        self.Bind(wx.EVT_BUTTON,            self.onSaveMask,            self.btnSaveMask)
        self.Bind(wx.EVT_RADIOBUTTON,       self.onChangeTrackType,     self.trackChoice[0])
        self.Bind(wx.EVT_RADIOBUTTON,       self.onChangeTrackType,     self.trackChoice[1])
        self.Bind(wx.EVT_RADIOBUTTON,       self.onChangeTrackType,     self.trackChoice[2])

    def sizers(self):
        self.mainSizer     = wx.BoxSizer(wx.HORIZONTAL)                             #   Main
        self.leftSizer     = wx.BoxSizer(wx.VERTICAL)                               #   |   Left
        self.sb_selectmonitor = wx.StaticBox(self, wx.ID_ANY, 'Select Monitor')     #   |   |   monitor selection text
        self.sbSizer_selectmonitor = wx.StaticBoxSizer(self.sb_selectmonitor, wx.VERTICAL)# |   |   select box
        self.sourceGridSizer = wx.FlexGridSizer(5, 2, 2, 2)                         #   |   |   |   |   grid of rbs & sources
        self.leftMiddleSizer = wx.BoxSizer(wx.VERTICAL)                             #   |   |   left middle
        self.maskBrowserSizer = wx.BoxSizer(wx.HORIZONTAL)                          #   |   |   |   mask browser
        self.outputDirSizer = wx.BoxSizer(wx.HORIZONTAL)                            #   |   |   |   output dir browser
        self.leftParamSizer = wx.BoxSizer(wx.HORIZONTAL)                            #   |   |   left parameters
        self.sb_timeSettings = wx.StaticBox(self, wx.ID_ANY, 'Time Settings')       #   |   |   |   time settings text
        self.sbSizer_timeSettings = wx.StaticBoxSizer(self.sb_timeSettings, wx.VERTICAL)#   |   |   |   time settings box
        self.dt_Sizer = wx.FlexGridSizer(3, 2, 2, 2)                                #   |   |   |   |   |   datetimefps widgets
        self.sb_trackingParms = wx.StaticBox(self, wx.ID_ANY, 'Tracking Parameters')#   |   |   |   tracking parameters text
        self.sbSizer_trackingParms = wx.StaticBoxSizer(self.sb_trackingParms, wx.VERTICAL)# |   |   |   tracking parameters box
        self.trackOptionsSizer = wx.BoxSizer(wx.VERTICAL)                           #   |   |   |   |   |   tracking options widgets
        self.calcbox_sizer = wx.BoxSizer(wx.VERTICAL)                               #   |   |   |   |   |   |   calculations widgets
        self.leftBottomSizer = wx.BoxSizer(wx.HORIZONTAL)                           #   |   |   left bottom

        self.rightSizer    = wx.BoxSizer(wx.VERTICAL)                               #   |   Right
        self.titleSizer    = wx.BoxSizer(wx.HORIZONTAL)                             #   |   |   Monitor title
        self.settingsSizer = wx.BoxSizer(wx.HORIZONTAL)                             #   |   |   preview settings
        self.videoSizer    = wx.BoxSizer(wx.HORIZONTAL)                             #   |   |   video panel
        self.settingsSizer = wx.BoxSizer(wx.HORIZONTAL)                             #   |   |   video panel settings
        self.rightBottomSizer = wx.BoxSizer(wx.HORIZONTAL)                          #   |   |   right bottom
        self.maskGenSizer  = wx.BoxSizer(wx.VERTICAL)                               #   |   |   |   mask maker controls
        self.tableSizer    = wx.FlexGridSizer(6, 3, 1, 5)                           #   |   |   |   |   table
        self.gen_saveSizer = wx.BoxSizer(wx.HORIZONTAL)                             #   |   |   |   |   save & gen buttons
        self.diagramSizer  = wx.BoxSizer(wx.HORIZONTAL)                             #   |   |   |   diagram

    # -------------------------------------------------------------------------------------------- add widgets to sizers

        self.sourceGridSizer.Add(self.txt_source,                       0, wx.ALL | wx.LEFT,     5)      # ------ source grid
        self.sourceGridSizer.Add(self.currentSource,                    1, wx.ALL | wx.EXPAND,   5)


        for count in range(0, len(self.rbs)):
            self.sourceGridSizer.Add(self.rbs[count],                   0, wx.ALL | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
            self.sourceGridSizer.Add(self.sources[count],               1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL,   5)

        self.sbSizer_selectmonitor.Add(self.sourceGridSizer,            0, wx.ALL | wx.EXPAND,   5)
        self.leftSizer.Add(self.sbSizer_selectmonitor,                  0, wx.ALL | wx.EXPAND,   5)

        self.leftMiddleSizer.Add(self.pickMaskBrowser,                  1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND, 5)
        self.leftMiddleSizer.Add(self.pickOutputBrowser,                1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND, 5)
        self.leftSizer.Add(self.leftMiddleSizer,                        0, wx.ALL | wx.EXPAND,   5)

        # ------------------------------------------------------------------------------- Video Start Date and Time
        # fill datetime grid
        self.dt_Sizer.Add(self.txt_date,                                0, wx.ALL, 5)
        self.dt_Sizer.Add(self.start_date,                              0, wx.ALL, 5)
        self.dt_Sizer.Add(self.txt_time,                                0, wx.ALL, 5)
        self.addWidgets(self.dt_Sizer, [self.start_time, self.btnSpin])
        self.dt_Sizer.Add(self.sourceFPSLabel,                          0, wx.ALL, 5)
        self.dt_Sizer.Add(self.sourceFPS,                               0, wx.ALL, 5)

        # fill video start date and time box
        self.sbSizer_timeSettings.Add(self.dt_Sizer,                    0, wx.ALL, 5)

        # ------------------------------------------------------------------------------------- Tracking Parameters
        # fill tracking parameters box
        self.trackOptionsSizer.Add(self.trackBox,                       0, wx.ALL | wx.ALIGN_LEFT, 5)
        self.trackOptionsSizer.Add(self.isSDMonitor,                    0, wx.ALL | wx.ALIGN_LEFT, 5)

        # fill calculation type box
        for count in range(0, len(self.trackChoice)):
            self.calcbox_sizer.Add(self.trackChoice[count],             0, wx.ALL | wx.ALIGN_LEFT, 5)
        self.trackOptionsSizer.Add(self.calcbox_sizer,                  0, wx.ALL | wx.ALIGN_LEFT, 5)

        self.sbSizer_trackingParms.Add(self.trackOptionsSizer,          0, wx.ALL, 5)

        self.leftParamSizer.Add(self.sbSizer_timeSettings,              0, wx.ALL | wx.ALIGN_TOP, 5)
        self.leftParamSizer.Add(self.sbSizer_trackingParms,             0, wx.ALL | wx.ALIGN_TOP, 5)

        self.leftBottomSizer.Add(self.btnSaveCfg,                       1, wx.ALL | wx.ALIGN_CENTER, 5)
        self.leftBottomSizer.Add(self.btnRemoveMonitor,                 1, wx.ALL | wx.ALIGN_CENTER, 5)

        self.leftSizer.Add(self.leftParamSizer,                         0, wx.ALL | wx.ALIGN_CENTER | wx.EXPAND, 5)
        self.leftSizer.Add(self.leftBottomSizer,                        0, wx.ALL | wx.ALIGN_CENTER | wx.EXPAND, 5)

        # ------------------------------------------------------------------------------------- Video Preview Panel
        self.rightSizer.Add(self.title,                     0, wx.ALL | wx.ALIGN_CENTER, 1)

        #                                      this sizer saves the spot in rightSizer in case video is changed later
        self.videoSizer.Add(self.previewPanel,              1, wx.ALL | wx.ALIGN_TOP, 5)
        self.rightSizer.Add(self.videoSizer,                1, wx.ALL | wx.ALIGN_CENTER, 5)

        self.settingsSizer.AddSpacer(5)
        self.settingsSizer.Add(self.previewSizeLabel,       0, wx.ALL | wx.EXPAND, 5)
        self.settingsSizer.Add(self.previewSize,            0, wx.ALL | wx.EXPAND, 5)
        self.settingsSizer.AddSpacer(5)
        self.settingsSizer.Add(self.previewFPSLabel,        0, wx.ALL | wx.EXPAND, 5)
        self.settingsSizer.Add(self.previewFPS,             0, wx.ALL | wx.EXPAND, 5)
        self.settingsSizer.AddSpacer(5)

        self.rightSizer.Add(self.settingsSizer,             0, wx.ALL, 5)

    # --------------------------------------------------------------------------------- mask coordinate entry table
        # --- Apply each row to the table
        for row in range(0, len(self.row_labels)):
            self.tableSizer.Add(self.row_labels[row],  0, wx.ALL | wx.EXPAND, 5)                  # column headers
            self.tableSizer.Add(self.X[row],           0, wx.ALL | wx.EXPAND, 5)                  # X column entries
            self.tableSizer.Add(self.Y[row],           0, wx.ALL | wx.EXPAND, 5)                  # Y column entries

        self.gen_saveSizer.Add(self.btnMaskGen,           1, wx.ALL | wx.ALIGN_CENTER, 10)           # generate and save buttons
        self.gen_saveSizer.Add(self.btnSaveMask,          1, wx.ALL | wx.ALIGN_CENTER, 10)

        self.maskGenSizer.Add(self.tableSizer,         0, wx.ALL | wx.ALIGN_CENTER, 2)
        self.maskGenSizer.Add(self.gen_saveSizer,      0, wx.ALL | wx.ALIGN_CENTER, 2)

    # ------------------------------------------------------------------------------------------------------ diagram

        self.diagramSizer.Add(self.diagramctl,         0, wx.ALL | wx.ALIGN_CENTER, 2)

        self.rightBottomSizer.Add(self.maskGenSizer,   0, wx.ALL | wx.ALIGN_CENTER, 2)
        self.rightBottomSizer.Add(self.diagramSizer,   0, wx.ALL | wx.ALIGN_CENTER, 2)

        self.rightSizer.Add(self.rightBottomSizer,     0, wx.ALL, 5)

   # ------------------------------------------------------------------------------------------- left & right sides
        self.mainSizer.Add(self.leftSizer,            0, wx.ALL | wx.ALIGN_LEFT, 2)
        self.mainSizer.Add(self.rightSizer,           0, wx.ALL | wx.ALIGN_RIGHT, 2)

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

        # -------------------------------------------------------------------------- stop & remove current video monitor
        if len(gbl.thumbPanels) > 2:                # always keep at least one monitor
            self.parent.notebookPages[0].scrolledThumbs.clearThumbGrid()        # remove thumbnails from config page
            gbl.cfg_dict.pop(old_mon)                           # delete from dictionary; renumbers list automatically
            self.parent.notebookPages.__delitem__(old_mon)      # delete notebook page from page list


        if gbl.source[0:6] == 'Webcam':                  # if needed change global copy of number of webcams
            gbl.webcams -= 1  # change number of webcams
#            gbl.webcams_inuse.remove(gbl.mon_name)       # remove name from webcam list

        # ------------------------------------------------------------------------ reset higher numbered monitors' names
        for mon_count in range(old_mon, gbl.monitors):
            gbl.cfg_dict[mon_count]['mon_name'] = 'Monitor%d' % mon_count  # change monitor names
#            if gbl.cfg_dict[mon_count]['source'][0:6] == 'Webcam':
#                gbl.cfg_dict[mon_count]['source'][0:6] = 'Webcam %d' % mon_count    # rename webcam    ->  only 1 webcam currently supported

        gbl.monitors -= 1  # ------------------------------------------------------ Change global settings
        gbl.mon_ID = old_mon - 1

        cfg.cfg_nicknames_to_dicts()       # -------------------------------------------------- update config dictionary

        cfg.mon_dict_to_nicknames()         # ------------------------------------------------- get new monitor settings

        self.parent.repaginate()
#        self.parent.DeletePage(old_mon)                                     # triggers page change event

    def onSaveCfg(self, event):
        r = self.TopLevelParent.config.cfgSaveAs(self)
        if r:                                                               # TODO: progress indicator of some sort?
            self.TopLevelParent.SetStatusText('Configuration saved.')
        else:
            self.TopLevelParent.SetStatusText('Configuration not saved.')
        winsound.Beep(600, 200)

    def refreshVideo(self):

        cfg.mon_nicknames_to_dicts()                                                    # save any new monitor settings

    # ------------------------------------------------------------------------------------------- kill old monitor panel  TODO: Update mask & settings
        self.previewPanel.keepPlaying = False
        self.previewPanel.Hide()
        self.previewPanel.Destroy()
        self.videoSizer.Clear()

        self.previewPanel = videoMonitor.monitorPanel(self, mon_ID=gbl.mon_ID, panelType='preview')   # make new monitor panel
        self.previewPanel.PlayMonitor()
        self.videoSizer.Add(self.previewPanel, 1, wx.ALL | wx.ALIGN_CENTER, 5)
        self.previewPanel.playTimer.Start(1000 / float(self.previewFPS.GetValue()))
        self.SetSizer(self.mainSizer)
        self.Layout()

    def onChangeTrackType(self, event):
        gbl.track_type = event.Selection

    def onChangeRb(self, event):
        gbl.source_type = event.EventObject.Label

        if self.sources[gbl.source_type].GetValue() != '':
            gbl.source = self.sources[gbl.source_type].GetValue()
            self.currentSource.SetValue(gbl.source)

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

    def onPreviewFPSnSize(self, event):
        gbl.preview_fps = gbl.correctType(self.previewFPS.GetValue(), 'fps_preview')
        gbl.preview_size = gbl.correctType(self.previewSize.GetValue(), 'size_preview')
        cfg.mon_nicknames_to_dicts()                        # save change to dictionary

        self.refreshVideo()                                 # close and restart video playback

    # --------------------------------------------------------------------------------------------------------- ROI handlers
    def onMaskBrowse(self, event):             # ----------------------------------------------------------- select a mask file
        gbl.mask_file = self.pickMaskBrowser.GetValue()
        cfg.mon_nicknames_to_dicts()                        # save change to dictionary

        gbl.ROIs = gbl.loadROIs(gbl.mask_file)
        gbl.showROIs = True

    def onMaskGen(self, event):
        gbl.showROIs = True                       # the only way to use this function is with the "Generate Mask" button
                                                        #  so user will expect to see the mask

        self.mask = []  # holds rows for output to a mask file
        gbl.ROIs = []  # holds tuples for drawing ROIs

        columns = int(self.X[1].GetValue())
        x1 = int(self.X[2].GetValue())  # top left x coordinate
        x_len = float(self.X[3].GetValue())  # width of ROI
        x_sep = float(self.X[4].GetValue())  # gap between ROIs (x-direction)
        x_tilt = float(self.X[
                           5].GetValue())  # x-distance between start of (first row, first column) and (second row, second column)

        rows = int(self.Y[1].GetValue())
        y1 = int(self.Y[2].GetValue())  # top left y coordinate
        y_len = float(self.Y[3].GetValue())  # width of ROI
        y_sep = float(self.Y[4].GetValue())  # gap between ROIs (y-direction)
        y_tilt = float(self.Y[
                           5].GetValue())  # y-distance between start of (first row, first column) and (second row, second column)

        ROI = 1  # counter; numbers the ROIs

        for row in range(0, rows):  # y-coordinates change through rows
            ax = int(x1 + row * x_tilt)  # reset x-coordinate start of row
            bx = int(ax + x_len)
            cx = int(bx)
            dx = int(ax)
            if row == 0:
                ay = y1
            else:
                ay = int(y1 + row * (y_len + y_sep))  # move down in y
            by = ay
            cy = int(ay + y_len)
            dy = cy
            for col in range(0, columns):  # x-coordinates change through columns

                # ------------------------------------------------------------------------ create the mask coordinates
                if col == 0 and row == 0:
                    self.mask.append(  # for saving to mask file
                        '(lp1\n((I%d\nI%d\nt(I%d\nI%d\nt(I%d\nI%d\nt(I%d\nI%d\n' % (ax, ay, bx, by, cx, cy, dx, dy))
                else:
                    self.mask.append(
                        'ttp%d\na((I%d\nI%d\nt(I%d\nI%d\nt(I%d\nI%d\nt(I%d\nI%d\n' % (
                        ROI, ax, ay, bx, by, cx, cy, dx, dy))

                gbl.ROIs.append([(ax, ay), (bx, by), (cx, cy), (dx, dy), (ax, ay)])  # for immediate use

                ax = int(bx + x_sep)  # prepare for next time
                bx = int(ax + x_len)
                cx = bx
                dx = ax
                ay = int(ay + y_tilt)
                by = ay
                cy = int(ay + y_len)
                dy = cy
                ROI += 1

        self.mask.append('ttp%d\na.(lp1\nI1\n' % (ROI + 1))
        self.mask.append('aI1\n' * (rows * columns - 1))
        self.mask.append('a.\n\n\n')

        gbl.showROIs = True

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

        return True
    
    def onClearMask(self, event):
        gbl.ROIs = []
        gbl.showROIs = False

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
