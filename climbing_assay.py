#!/usr/bin/env python

# coding: utf-8

# In[1]:

# Calculates various information for chargebacks

# input:  .csv file made in Excel containing journal of activites
#      date, col_time, chargeback category, comments
# output: report of date, chargeback category, total col_time
#
import wx
import os
import sys
import csv                      # handles txt files
import folderselectdialog
import xml.etree.ElementTree as ET


class mainFrame(wx.Frame):
    """
    Creates the main window of the application.
    """

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        kwds["size"] = (650,650)
        wx.Frame.__init__(self, *args, **kwds)


        # window for stdout ---------------------------------------------------------------------
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL | wx.VSCROLL | wx.EXPAND
        log = wx.TextCtrl(self, wx.ID_ANY, size=(600, 600),
                          pos=(40,40), style=style)

        # Add widgets to a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(log, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

        # redirect text here
        sys.stdout = log

        # collect and output data -----------------------------------------------------------------
        report = []

        folderlist = folderselectdialog.dirselectdlg(self, pos=(500,300))          # get list of folders

        savefile = self.savedialog(self)                                            # get output file name
        try: os.remove(savefile)                                                    # delete old one if it exists
        except: pass
        savehdl = open(savefile, 'wb')                                              # open output file
        writer = csv.writer(savehdl, dialect='excel')               # tab-delimited

        for folder in folderlist:
            report.append(self.folderReporter(folder))                              # get a report for each folder

        for experiment in report:                                                          # output reports to file
            for row in experiment:
                writer.writerows(row)


        savehdl.close()
        print('           ')
        print('     Data saved to: ', savefile)
        print('     done.')

    def folderReporter(self, folder):   #  ------------------------------------  collect data for each folder
        # each string needs to be in its own list so that the csv writer will be able to iterate properly

            if folder[0:4] == 'ches':                           # if this is a folder on a mapped drive
                folder = folder[23:25] + folder[26:]
            print folder
            cross_barcodes = []
            tubes = []
            datetime = folder[-15:]

            sr_file = os.path.join(folder, 'session_results.txt')        # open session_results.txt
            session_results = []
            try:
                filepointer = open(sr_file, 'r')
                session_results = list(csv.reader(filepointer, delimiter='\t'))  # read into list
            except:
                print(datetime, ' session_results.txt  not found. \]n')
                session_results = [' ','?','?','?','?','?','?','?','?','?']             # substitute list for missing session_results.txt file

#            for line in csvlist.splitlines():
#                session_results.append(tuple(line.split(",")))

            try:
                md_file = os.path.join(folder, 'metadata.xml')          # collect metadata for the session
                metatree = ET.parse(md_file)
                metaroot = metatree.getroot()
                for tubedata in metaroot.iter('session'):
                    cross_barcodes.append(tubedata._children[0].attrib['cross_barcode'])
                    tubes.append(tubedata.attrib['id'])
            except:
                print(datetime, 'metadata.xml not found.  \n')
                for tubedata in range(0,5):
                    cross_barcodes.append([' ','?','?','?','?','?','?'])           # substitute list for missing metadata.xml file
                    tubes = ['1', '2', '3' ,'4', '5', '6']

            report = [['Date/Time', 'Tube', 'Cross Barcode']]             # column headers
            report[0].extend(session_results[0])                           # session file column headers
            report[0] = [report[0]]                                     # prevent commas between each character in output
            for tube in tubes:                                          # combine metadata and session results
                row = [datetime, tube]
                row.extend([cross_barcodes[int(tube)-1]])   # 0-indexed list
                row.extend(session_results[int(tube)])      # row 0 is titles, so essentially 1-indexed
                print row
                report.append([row])

            try: filepointer.close()
            except: pass                            # close the file

            return report


    #   gets file path for output file -----------------------------------------------------------------------------
    def savedialog(self, parent):
        wildcard = "Text File (*.txt)|*.txt|" \
                   "All files (*.*)|*.*"                        # adding space in here will mess it up!

        dlg = wx.FileDialog(                                                # get output file path
            parent, message = "Save File.",
            defaultDir = os.getcwd(),
            defaultFile = "",
            wildcard = wildcard,
            style = wx.SAVE | wx.CHANGE_DIR | wx.OVERWRITE_PROMPT           #| wx.STAY_ON_TOP
            )

        if dlg.ShowModal() == wx.ID_OK:  # show the open-file window
            savefile = dlg.GetPath()
            print savefile
            try:
                os.remove(savefile)  # delete the file if it already exists
            except:
                pass
        else:
            savefile = os.path.join(os.getcwd(), 'report.txt')
            print('cannot save to designated file.  Used: ', savefile)
        dlg.Destroy()
        return savefile



# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%         Main Program

if __name__ == "__main__":
    app = wx.App()
    wx.InitAllImageHandlers()

    frame_1 = mainFrame(None, -1, "")  # Create the main window.
    app.SetTopWindow(frame_1)
    frame_1.Show()  # Show the main window
    app.MainLoop()                              # Begin user interactions.






