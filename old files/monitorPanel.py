import wx                               # GUI controls
import cv2, cv
import os

from configurator import Configuration
from filebrowsebutton_LL import FileBrowseButton
import videoMonitor

class maskMakerPanel(wx.Panel):

    def __init__(self, parent, cfg_dict, mon_ID):
        wx.Panel.__init__(self, parent, wx.ID_ANY, size=(800,500), name='maskMakerPanel')

        self.parent = parent
        self.cfg_dict = cfg_dict
        self.mon_ID = mon_ID
        self.n_mons = self.cfg_dict[0]['monitors']  # monitor selection box
        self.maskfile = cfg_dict[self.mon_ID]['maskfile']
        self.fps_preview = self.cfg_dict[self.mon_ID]['fps_preview']

        self.ROIs = self.loadROIs(self.maskfile)                # get ROIs from maskfile and set flag to show them
        if self.ROIs != []: self.showROIs = True
        else: self.showROIs = False

        self.size = cfg_dict[0]['size_preview']

        self.widgets()
        self.binders()
        self.sizers()

    def widgets(self):

        # TODO: get coordinate values by clicking the mouse
        # TODO: add PySolo single ROI drawing

    # video display panel
        self.previewPanel = videoMonitor.monitorPanel(self, self.cfg_dict, self.mon_ID, self.size, self.ROIs, self.showROIs)
        self.previewPanel.Play(self.cfg_dict, self.mon_ID, self.fps_preview, self.ROIs, self.showROIs,)           # don't show mask until requested

    # Title
        self.title = wx.StaticText(self, -1, "\n Measurements: ")  # title
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.title.SetFont(font)

    # monitor selection combobox
        if self.n_mons < 1:
            self.n_mons = 1  # there must be at least one monitor
        self.monitorList = ['Monitor %s' % (int(m)) for m in range(1, self.n_mons + 1)]  # make list
        self.mon_choice = wx.ComboBox(self, wx.ID_ANY, choices=self.monitorList,
                                      style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)  # mon_ID is 1-indexed
        self.mon_choice.Selection = self.mon_ID - 1  # initial selection is monitor 1

    # Coordinates Input Grid
        self.row_labels = [wx.StaticText(self, -1, ' '),
                           wx.StaticText(self, -1, 'Number'),
                           wx.StaticText(self, -1, 'Top Left'),
                           wx.StaticText(self, -1, 'Span'),
                           wx.StaticText(self, -1, 'Gap'),
                           wx.StaticText(self, -1, 'Tilt')
                           ]                                                    # row labels
        self.X = []
        self.Y = []
        self.X.append(wx.StaticText(self, wx.ID_ANY, "Columns (X)"))                    # column header for columns
        self.Y.append(wx.StaticText(self, wx.ID_ANY, "Rows (Y)"))                      # column header for rows
        for cnt in range(0,5):
            self.X.append(wx.TextCtrl(self, wx.ID_ANY, value='0'))
            self.Y.append(wx.TextCtrl(self, wx.ID_ANY, value='0'))

    # instructional diagram
        self.diagram = wx.Bitmap('maskmakerdiagram.bmp', wx.BITMAP_TYPE_BMP)        # instructional diagram
        self.diagramctl = wx.StaticBitmap(self, wx.ID_ANY, self.diagram)

    # start automask & save buttons
        self.autobtn = wx.Button(self, wx.ID_ANY, label="Generate Mask")
        self.autobtn.Enable(True)
        self.savebtn = wx.Button(self, wx.ID_ANY, label="Save")
        self.savebtn.Enable(True)

    # mask file handling
        self.maskfile = self.cfg_dict[self.mon_ID]['maskfile']
        wildcard = 'PySolo Video mask file (*.msk)|*.msk|' \
                   'All files (*.*)|*.*'  # adding space in here will mess it up!
        self.pickMaskBrowser = FileBrowseButton(self, id=wx.ID_ANY,
                                                labelText='Select Mask File:', buttonText='Browse',
                                                toolTip='Type filename or click browse to choose mask file',
                                                dialogTitle='Choose a mask file',
                                                startDirectory=os.path.split(self.maskfile)[0],
                                                wildcard=wildcard, style=wx.ALL,
                                                changeCallback=self.onNewROIs,
                                                name='maskBrowseButton')

    def binders(self):
        self.Bind(wx.EVT_COMBOBOX, self.onChangeMonitor, self.mon_choice)
        self.Bind(wx.EVT_BUTTON, self.maskCalculator, self.autobtn)
        self.Bind(wx.EVT_BUTTON, self.onSaveMask, self.savebtn)

    def sizers(self):
        self.mainSizer     = wx.BoxSizer(wx.HORIZONTAL)
        self.leftSizer     = wx.BoxSizer(wx.VERTICAL)
        self.rightSizer    = wx.BoxSizer(wx.VERTICAL)
        self.controlSizer  = wx.BoxSizer(wx.HORIZONTAL)        # bottom left side, auto mask maker controls
        self.titleSizer    = wx.BoxSizer(wx.HORIZONTAL)
        self.coordinatesSizer = wx.BoxSizer(wx.VERTICAL)
        self.gen_saveSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tableSizer    = wx.FlexGridSizer(6, 3, 1, 5)      # coordinate entry table


    # coordinate entry table
        # --- Apply each row to the table
        for row in range(0, len(self.row_labels)):
            self.tableSizer.Add(self.row_labels[row],  0, wx.EXPAND, 5)                  # column headers
            self.tableSizer.Add(self.X[row],           0, wx.EXPAND, 5)                  # X column entries
            self.tableSizer.Add(self.Y[row],           0, wx.EXPAND, 5)                  # Y column entries

    # control panel
        self.titleSizer.Add(self.title,                0, wx.ALIGN_TOP | wx.EXPAND, 5)      # title
        self.titleSizer.Add(self.mon_choice,           0, wx.ALIGN_BOTTOM, 5)            # monitor selection combobox

        self.coordinatesSizer.Add(self.titleSizer,     0, wx.ALIGN_CENTER, 5)
        self.coordinatesSizer.AddSpacer(20)

        self.coordinatesSizer.Add(self.tableSizer,     2, wx.ALIGN_CENTER, 5)            # coordinate table

        self.gen_saveSizer.Add(self.autobtn,           1, wx.ALIGN_CENTER, 10)           # generate and save buttons
        self.gen_saveSizer.Add(self.savebtn,           1, wx.ALIGN_CENTER, 10)
        self.coordinatesSizer.Add(self.gen_saveSizer,  0, wx.ALIGN_RIGHT, 2)

        self.controlSizer.Add(self.diagramctl,         1, wx.ALIGN_CENTER | wx.ALIGN_TOP | wx.EXPAND, 5)  # instructional diagram
        self.controlSizer.Add(self.coordinatesSizer,   1, wx.ALIGN_CENTER | wx.EXPAND, 5)

        # video monitor  & automask controls                                           # left side
        self.leftSizer.Add(self.pickMaskBrowser,       0, wx.ALIGN_TOP | wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND, 2)
        self.leftSizer.Add(self.previewPanel,          0, wx.ALIGN_TOP | wx.ALIGN_CENTER_HORIZONTAL| wx.EXPAND, 2)
        self.leftSizer.Add(self.controlSizer,          0, wx.ALIGN_BOTTOM | wx.EXPAND, 2)

        # right side placeholder
        self.rightSizer.AddSpacer(800)

        self.mainSizer.Add(self.leftSizer,             1, wx.ALIGN_CENTER | wx.EXPAND, 2)
        self.mainSizer.Add(self.rightSizer,            1, wx.ALIGN_CENTER | wx.EXPAND, 2)

        self.SetSizerAndFit(self.mainSizer)
        self.Layout()

    def onChangeMonitor(self, event):  # ------------------------------------------------------    Changing Monitor
        # User has selected a monitor from the combobox

        self.mon_ID = event.Selection + 1  # mon_ID is 1-indexed but event is 0-indexed
        self.source = self.cfg_dict[self.mon_ID]['source']
        self.maskfile = self.cfg_dict[self.mon_ID]['maskfile']
        self.fps_preview = self.cfg_dict[self.mon_ID]['fps_preview']

        self.ROIs = self.loadROIs(self.maskfile)
        if self.ROIs != []: self.showROIs = True
        else: self.showROIs = False


        self.previewPanel.Play(self.cfg_dict, self.mon_ID, self.fps_preview, self.ROIs, self.showROIs)

    def onSaveMask(self, event):            # --------------------------------------------------------  Save mask file
        """
        Lets user select file and path where mask will be saved.
        """

        # set file types for find dialog
        wildcard = "PySolo Video config file (*.msk)|*.msk|" \
                   "All files (*.*)|*.*"  # adding space in here will mess it up!

        dlg = wx.FileDialog(self,
                            message="Save mask as file ...",
                            defaultDir=self.cfg_dict[self.mon_ID]['datafolder'],
                            wildcard=wildcard,
                            style=(wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        )

        if not(dlg.ShowModal() == wx.ID_OK):                     # show the file browser window
            return False

        else:
            self.filePathName = dlg.GetPath()               # get the path from the save dialog

            if os.path.isfile(self.filePathName):
                os.remove(self.filePathName)                # get rid of old file before appending data

            with open(self.filePathName, 'a') as maskfile:
                for roi in self.mask:
                    maskfile.write(roi)                          # write to file line by line

        dlg.Destroy()
        maskfile.close()
        return True

    def onNewROIs(self, event):                    # need function to provide arguments to loadROIs on event & Generate Mask button
        self.ROIs = self.loadROIs(self.pickMaskBrowser.GetValue())
        self.showROIs = True
        self.previewPanel.ROIs = self.ROIs
        self.previewPanel.showROIs = self.showROIs

    def maskCalculator(self, event):
        self.showROIs = True               # the only way to use this function is with the "Generate Mask" button
        self.mask = []                     # so user will expect to see the mask
        self.ROIs = []

        columns = int(self.X[1].GetValue())
        x1      = int(self.X[2].GetValue())                # top left x coordinate
        x_len   = float(self.X[3].GetValue())              # width of ROI
        x_sep   = float(self.X[4].GetValue())              # gap between ROIs (x-direction)
        x_tilt  = float(self.X[5].GetValue())              # x-distance between start of (first row, first column) and (second row, second column)

        rows    = int(self.Y[1].GetValue())
        y1      = int(self.Y[2].GetValue())                # top left y coordinate
        y_len   = float(self.Y[3].GetValue())              # width of ROI
        y_sep   = float(self.Y[4].GetValue())              # gap between ROIs (y-direction)
        y_tilt  = float(self.Y[5].GetValue())              # y-distance between start of (first row, first column) and (second row, second column)

        ROI = 1                     # counter; numbers the ROIs

        for row in range(0, rows):  # y-coordinates change through rows
            ax = int(x1 + row * x_tilt)                   # reset x-coordinate start of row
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
                if (col == 0 and row == 0):
                    self.mask.append(                               # for saving to mask file
                        '(lp1\n((I%d\nI%d\nt(I%d\nI%d\nt(I%d\nI%d\nt(I%d\nI%d\n' % (ax, ay, bx, by, cx, cy, dx, dy))
                else:
                    self.mask.append(
                        'ttp%d\na((I%d\nI%d\nt(I%d\nI%d\nt(I%d\nI%d\nt(I%d\nI%d\n' % (ROI, ax, ay, bx, by, cx, cy, dx, dy))

                self.ROIs.append([(ax, ay), (bx, by), (cx, cy), (dx, dy), (ax, ay)])     # for immediate use

                ax = int(bx + x_sep)                                   # prepare for next time
                bx = int(ax + x_len)
                cx = bx
                dx = ax
                ay = int(ay + y_tilt)
                by = ay
                cy = int(ay + y_len)
                dy = cy
                ROI = ROI + 1

        self.mask.append('ttp%d\na.(lp1\nI1\n' % (ROI + 1))
        self.mask.append('aI1\n' * (rows * columns - 1))
        self.mask.append('a.\n\n\n')

        self.showROIs = True
        self.previewPanel.ROIs = self.ROIs
        self.previewPanel.showROIs = self.showROIs
        self.previewPanel.Refresh()



# ------------------------------------------------------------------------------------------ Stand alone test code
#  insert other classes above and call them in mainFrame
#
class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, *args, **kwds)

        config = Configuration(self)
        whole = maskMakerPanel(self, config, mon_ID=1)




        print('done.')

if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.

#
