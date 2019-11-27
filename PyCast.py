#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: Chelsea Piccirilli
Prof: Dr. Mamo
File: PyCast.py
Description: Front end of the limited functionality Podcast player PyCast.
Note: Some of the features I wanted to impliment eventually have code here and may be "beta"
stages of development. Impliment at your own risk.

"""

import sys, os
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QMainWindow, QAction, QApplication, QLabel, QVBoxLayout, QWidget, QSlider,
                             QHBoxLayout, QPushButton, QGridLayout, QTableWidgetItem, QTableWidget, QTabWidget,
                             QLineEdit, QCheckBox, QStatusBar, QFileDialog)

from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent
from podcast.sqlPython import sqlPython as sql
from podcast.sqlPython import *
import feedparser



class Player(QMainWindow):

    def __init__(self):
        super().__init__(None, Qt.WindowStaysOnTopHint)

        #main widget
        self.widg = QWidget()
        self.status = QStatusBar()
        self.status.showMessage("Welcome to PyCast!")

        #tabs
        self.tabs = QTabWidget()
        self.series_tab = QWidget()
        self.episode_tab=QWidget()
        self.playlist_tab = QWidget()
        self.playlist_table = QTableWidget()
        self.tableWidget = QTableWidget()
        self.eps = []
        self.series_list = []
        self.list_labels = []
        self.line = QLineEdit()
        self.play_list = []
        self.seriesLayout = self.series_layout()

        # media player
        self.media = QMediaPlayer()
        self.media_playlist = QMediaPlaylist()
        self.color = True
        self.track = QLabel("PyCast - Player built with Python and QtPy5")
        self.pause_btn = self.pause()
        self.skb15 = self.skip_15_back()
        self.skf15 = self.skip_15_forward()
        self.slider = self.track_slider()

        # menubar/options
        self.toggleColors()
        self.top_menu_bar()
        self.app_show()

    def get_color(self):
        return self.color

    """
    menu stuff starts here
    """
    def exit_menu_item(self):
        """
        Exits the application

        """
        icon = QIcon("static_images\index.png")
        exit_action = QAction(icon, "Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit PyCast")
        exit_action.triggered.connect(self.close)
        return exit_action

    def open_menu_item(self):

        open_act = QAction( "Open", self)
        open_act.setShortcut("Ctrl+O")
        open_act.setStatusTip("Open a file")
        open_act.triggered.connect(self.open_file)
        return open_act

    def top_menu_bar(self):
        """
        Creates the top menu.
        :return: void
        """
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        options_menu = menu.addMenu("Options")
        rss_menu = menu.addMenu("Rss/Atom")
        self.file_menu(file_menu)
        self.options_menu(options_menu)
        return menu

    def file_menu(self, menu):
        """
        file menu on the menu bar
        :return: void
        """
        exit = self.exit_menu_item()
        open = self.open_menu_item()
        menu.addAction(open)
        menu.addAction(exit)
        return menu

    def open_file(self):
        song = QFileDialog.getOpenFileName(self, "Open Song", "~", "Sound Files (*.mp3 *.ogg *.wav *.m4a)")
        s = song.split("\\")[-1]

        if song[0] != "":
            self.play_handler(song, "Song", s)
    def options_menu(self, menu):
        """
        Creates an options menu. Mostly for the dark theme.
        :param menu:
        :return:
        """
        dark = self.dark_theme()
        menu.addAction(dark)
        return menu



    def dark_theme(self):
        """
        Creates a dark theme toggle.
        :return:
        """
        dark_action = QAction("Switch Theme", self)
        dark_action.setShortcut("Ctrl+l")
        dark_action.setStatusTip("Switch Theme")
        dark_action.triggered.connect(self.toggleColors)
        return dark_action

    """
    menu stuff stops here
    """

    """
    Player stuff starts here
    """

    def set_track_name(self, series, ep):
        """
        sets track area
        :param name:
        :return:
        """
        name = "Episode: {} - Series: {}".format(series, ep)
        self.track = QLabel(name)

    def track_slider(self):
        """
        Creates a slider to track the music play back.
        :return:
        """
        slider = QSlider(Qt.Horizontal)
        slider.valueChanged[int].connect(self.media.position)
        return slider

    def skip_15_back(self):
        """
        allows you to skip back 15 seconds, button
        :return:
        """
        skipback15 = QPushButton()
        icon=QIcon("static_images\\icons8-rewind-24.png")
        skipback15.setIcon(icon)
        skipback15.clicked.connect(self.skipback_handle)

        return skipback15

    def skip_15_forward(self):
        """
        Allows you to skip forward 15 seconds, button
        :return:
        """
        skipfor15 = QPushButton()
        icon = QIcon("static_images\\icons8-fast-forward-24.png")
        skipfor15.setIcon(icon)
        skipfor15.clicked.connect(self.skipforward_handle)
        return skipfor15

    def play(self):
        """
        Signals the start of track playback, button
        :return:
        """
        play = QPushButton()
        icon = QIcon("static_images\\icons8-play-24.png")
        play.setIcon(icon)
        return play

    def pause(self):
        """
        Signals the pause of the track play back.
        :return:
        """
        pause = QPushButton()
        picon = QIcon("static_images\\icons8-pause-24.png")
        pause.setIcon(picon)
        pause.clicked.connect(self.pause_handle)

        return pause

    def skipforward_handle(self):
        """
        Handler for the skip forward button
        :return:
        """
        position = self.media.position()
        position += 15000
        self.media.setPosition(position)

    def skipback_handle(self):
        """
        Handler for the skip back button
        :return:
        """
        position = self.media.position()
        if position > 15000:
            position -= 15000
        else:
            position = 0

        self.media.setPosition(position)

    def pause_handle(self):
        """
        Handler for the pause button
        :return:
        """
        t = self.track.text()
        state = self.media.state()

        if state == self.media.PlayingState:
            self.media.pause()
            self.status_info("Paused - {}".format(t))

        if state == self.media.PausedState:
            self.status_info("Playing - {}".format(t))
            self.media.play()


    def toggleColors(self):
        """
        Settings for the dark theme and light theme.
         """
        app.setStyle("Fusion")
        palette = QPalette()
        if not self.color:
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(235, 101, 54))
            palette.setColor(QPalette.Highlight, QColor(235, 101, 54))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
            self.color = True

        elif self.color:
            palette.setColor(QPalette.Window, Qt.white)
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, QColor(240, 240, 240))
            palette.setColor(QPalette.AlternateBase, Qt.white)
            palette.setColor(QPalette.ToolTipBase, Qt.darkYellow)
            palette.setColor(QPalette.ToolTipText, Qt.black)
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, Qt.lightGray)
            palette.setColor(QPalette.ButtonText, Qt.black)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(66, 155, 248))
            palette.setColor(QPalette.Highlight, QColor(66, 155, 248))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
            self.color = False

    def h_box(self):
        """
        Packs buttons into a  horizontal box layout.
        :return:
        """

        play = self.play()


        h_layout = QHBoxLayout()
        h_layout.addWidget(self.skb15)
        #h_layout.addWidget(play)
        h_layout.addWidget(self.pause_btn)
        h_layout.addWidget(self.skf15)

        return h_layout

    def v_box(self):
        """
        Packs elements into a vertical box layout.
        :return:
        """

        # Set up widget objects here
        self.track.setAlignment(Qt.AlignLeft)
        buttons = self.h_box()
        self.vertical_tabs()

        # Packing into a vertical box begins here
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.track)
        #v_layout.addWidget(self.slider)
        v_layout.addLayout(buttons)
        v_layout.addWidget(self.tabs)
        v_layout.addWidget(self.status)
        self.widg.setLayout(v_layout)

    def play_handler(self, pod_ep, series, track):
        """
        Handler for the play button.
        :param pod_ep: local url str
        :param series: str
        :param track: str
        :return:
        """
        self.status_info("Playing - {}: {}".format(series, track))
        if pod_ep == "":
            print("ERROR! - play_handler")
        else:
            t = self.set_track_info(series, track)
            try:
                print("Playing....")
                print(pod_ep)
                self.media_playlist.clear()
                self.media.setVolume(100)
                self.media_playlist.addMedia(QMediaContent(QUrl.fromLocalFile(pod_ep)))
                self.media.setPlaylist(self.media_playlist)
                self.media.play()
                print("done")
            except Exception as e:
                ex = str(e)
                print(e, e.__class__())
            return

    def set_track_info(self, series, track):
        """
        sets the trac info above the buttons.
        :param series: str
        :param track: str
        :return:
        """
        t = "{}: {}".format(series, track)
        self.track.repaint()
        self.track.setText(t)


    """
    Player stuff ends here
    """

    """
    Browser stuff starts here
    """
    def series_layout(self):
        """
        layout for the series tab. Need to update to table to make dynamic
        :return:
        """
        series = GetCalls()
        s = series.get_series()
        #print(s)

        grid = QGridLayout()
        add = QPushButton("View Series")
        update = QPushButton("Update!")
        for i in s:
            self.series_list.append(i[0])
            self.list_labels.append(i[0])
            #print(i[0])


        for en, i in enumerate(self.series_list):
            self.series_list[en] = QCheckBox(i) #adds the check box to the list.
            grid.addWidget(self.series_list[en], en, 0) #adds to the grid widget while we are here.

        grid.addWidget(add)
        grid.addWidget(update)

        add.clicked.connect(self.check_box_handler)
        add.clicked.connect(self.add_rows)
        update.clicked.connect(self.update_handler)
        return grid

    def playlist(self):
        """
        Unimplimented
        Playlist QTableWidget
        :return:
        """
        headers = ("Series", "Episode", "Play", "Published", "Description")

        self.playlist_table.setColumnCount(len(headers))
        self.playlist_table.setHorizontalHeaderLabels(headers )


        # self.tableWidget.move(0,0)

        # self.tableWidget.doubleClicked.connect(self.on_click)
        return self.playlist_table


    def playlist_add_list(self, i: tuple):
        """
        adds line to the playlist list
        :param i:
        :return:
        """
        self.play_list.append(i)
        for line in self.play_list:
            print(line)

    def playlist_add_rows(self):
        """
        Playlist. Adds rows to the qtablewidget.
        Adds to the widget.
        :return:
        """
        ep = self.play_list
        self.playlist_table.setEditTriggers(QTableWidget.NoEditTriggers)
        plist = self.playlist_table
        row_pos = self.playlist_table.rowCount()
        self.playlist_table.insertRow(row_pos)

        for en, i in enumerate(ep):
            plist.setItem(en, 0, QTableWidgetItem(i[5]))
            plist.setItem(en, 1, QTableWidgetItem(i[0]))
            # Play Button Start
            play = QPushButton(plist)
            pIcon = QIcon("static_images\\icons8-play-24.png")
            play.setText("Play")
            play.setIcon(pIcon)
            plist.setCellWidget(en, 2, play)

            plist.setItem(en, 3, QTableWidget(i[2]))

            plist.setItem(en, 4, QTableWidget(i[3]))


    def add_rows(self):
        """
        Adds rows to the Episode QTable Widget.
        :return:
        """
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        for en, i in enumerate(self.eps):
            rowposition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowposition)

            try:
                pod_path = os.path.join(os.path.expanduser("~"), "Music", "Podcasts", i[5])
                dir = os.listdir(pod_path)
            except FileNotFoundError as e:
                print(str(e), str(e).__class__())

            filename = i[4].split("\\")[-1]

            #Download Button Start
            gc = GetCalls()
            download = QPushButton(self.tableWidget)
            dIcon = QIcon("static_images\\icons8-download-24.png")
            download.setIcon(dIcon)
            download.setText("Download")
            #download.clicked.connect(lambda *args, arg1 = self.eps[en][5], arg2=self.eps[en][0]: self.status_info(arg1, arg2))
            download.clicked.connect(lambda *args, arg1= self.eps[en][1], arg2=self.eps[en][4]: self.download_click_handle(arg1, arg2))
            self.tableWidget.setCellWidget(en, 0, download)

            #Play Button Start
            play = QPushButton(self.tableWidget)
            pIcon = QIcon("static_images\\icons8-play-24.png")
            play.setText("Play")
            play.setIcon(pIcon)
            play.clicked.connect(lambda *args, arg1=self.eps[en][4], arg2=self.eps[en][5], arg3=self.eps[en][0]: self.play_handler(arg1, arg2, arg3))
            self.tableWidget.setCellWidget(en, 3, play)

            # Playlist Button
            playlist = QPushButton(self.tableWidget)
            plIcon = QIcon("static_images\\icons8-fast-forward-24.png")
            playlist.setIcon(plIcon)
            playlist.clicked.connect(lambda *args, arg=i: self.playlist_add_list(arg))

            self.tableWidget.setCellWidget(en, 8, playlist)

            if filename not in dir:
                download.setDisabled(False)
                play.setDisabled(True)
                #playlist.setDisabled(True)

                #self.tableWidget.setItem(en, 3, QTableWidgetItem("X"))

            else:
                download.setDisabled(True)
                play.setDisabled(False)
                #playlist.setDisabled(False)
                #self.tableWidget.setItem(en, 0, QTableWidgetItem("X"))


            self.tableWidget.setItem(en, 1, QTableWidgetItem(i[5]))

            #self.ep = QTableWidgetItem(i[0])

            self.tableWidget.setItem(en, 2, QTableWidgetItem(i[0]))

            #self.tableWidget.setItem(en, 3, QTableWidgetItem("Play"))

            self.tableWidget.setItem(en, 4, QTableWidgetItem(i[2]))

            self.tableWidget.setItem(en, 5, QTableWidgetItem(i[3]))

            self.tableWidget.setItem(en, 6, QTableWidgetItem(i[4]))

            self.tableWidget.setItem(en, 7, QTableWidgetItem(i[1]))

    def download_click_handle(self, url, path):
        """
        Handler for the Download button on the episode Qtablewidget
        :param url: str
        :param path: str
        :return:
        """
        print(url, path)
        gc = GetCalls()
        # msg = QMessageBox.information("Downloading....", QMessageBox.Close)
        gc.download(path, url)

        self.status_info("Download Done!") #updates status bar

    def check_box_handler(self):
        """
        Handler to see what boxes are checked. If checked adds that series to the episode QTableWidget
        :return:
        """
        self.status_info("Populating Browser. One moment please.")
        sql_string = ""
        for sl, ll in zip(self.series_list, self.list_labels):
            if sl.checkState():
                sql_string = sql_string + "'{}', ".format(ll)

        s = sql_string.rstrip(', ')
        #print(s)

        series = GetCalls()
        eps= series.get_episodes(s)
        self.eps += eps
        self.status_info("All done! Thanks!")

    def update_handler(self):
        """
        Handler for the update button
        :return:
        """
        gc = GetCalls()
        rows = gc.get_series()
        for r in rows:
            parser = feedparser.parse(r[2])
            if not parser.bozo:
                s = sql(parser)
                s.parse_episodes_from_feed()
        self.status_info("Updating finished.")

    def sync_playlist(self):
        """
        Playlist sync button. Fills out rows upon clicking
        :return:
        """
        sy = QPushButton("Sync Playlist")
        sy.clicked.connect(self.playlist_add_rows)

        return sy

    def clear_playlist(self):
        """
        Playlist clear button
        :return:
        """
        pl = QPushButton("Clear Playlist")
        pl.clicked.connect(self.playlist_clear_handle)
        return pl

    def playlist_layout(self):
        """
        Layout for the playlist tab
        :return:
        """
        listtable = self.playlist()
        clear = self.clear_playlist()
        sy = self.sync_playlist()
        g = QGridLayout()
        g.addWidget(sy, 0, 0)
        g.addWidget(clear, 0, 1)
        v = QVBoxLayout()
        v.addWidget(listtable)
        v.addLayout(g)
        return v


    def vertical_tabs(self):
        """
        Where all the tab magic happens. Sets up layouts. Loads them into tab widget.
        :return:
        """
        self.tabs.addTab(self.series_tab, "Series")
        self.tabs.addTab(self.episode_tab, "Episodes")
        # self.tabs.addTab(self.playlist_tab, "Playlist") #add this when playlist is working.

        playlist = self.playlist_layout()
        #grid2 = self.series_layout
        self.series_tab.setLayout(self.seriesLayout)
        clear = self.clear_btn()
        grid = self.grid_box_buttons()
        h_box = self.browser_h_box()

        v_box = QVBoxLayout()
        v_box.addLayout(grid)
        v_box.addLayout(h_box)
        v_box.addWidget(clear)
        self.episode_tab.setLayout(v_box)
        self.playlist_tab.setLayout(playlist)

    def clear_btn(self):
        """Clear button for qtablewidget """
        clear = QPushButton("Clear")
        clear.clicked.connect(self.clear_handle)
        return clear

    def clear_handle(self):
        """
        Handler for Clear button of episode qtablewidget
        :return:
        """
        self.tableWidget.setRowCount(0)
        self.eps = []

    def playlist_clear_handle(self):
        """
        Playlist clear handler. Clears the playlist.
        :return:
        """
        self.playlist_table.setRowCount(0)

    def add_cast(self):
        """
        Add button for episodes tab
        :return:
        """
        add = QPushButton("Add")
        add.clicked.connect(self.add_cast_handler)
        return add

    def add_cast_handler(self):
        """
        Handler for the add button of the episodes tab
        :return:
        """
        try:
            feed_devourer = feedparser.parse(self.line.text())
            if not feed_devourer.bozo:
                s = sql(feed_devourer)
                s.info_update() #updates rssurl table with info.
                s.parse_episodes_from_feed() #gets episodes from feed
                title = "'"+s.get_title()+"'"
                g = GetCalls()
                a = g.get_episodes(title)
                print(type(a))
                self.eps += a
                self.add_rows()
            else:
                print("Check connection. Try again. Also could be a badly formed feed.")
            self.line.setText("")
        except Exception as e:
            print("add_cast")
            print(str(e))

        try:
            self.series_tab.repaint()

        except Exception as e:
            print(str(e))

    def sync_button(self):
        """
        Sync button for the episode tab
        :return:
        """
        sync = QPushButton("Sync")
        sync.clicked.connect(self.sync_handle)
        return sync

    def sync_handle(self):
        """
        Sync button handler. Does A LOT of things.
        Clears the episode qtablewidget, sees what checkboxes are ticked,
        adds those to the rows, prints a status bar message.
        :return:
        """
        self.status_info("Updating. Just a moment thanks.")
        self.clear_handle()
        self.check_box_handler()
        self.add_rows()
        self.status_info("Thanks! Enjoy!")


    def episodes(self):
        """
        This is where the episodes tablewidget is birthed.
        :return:
        """
        headers = ("Download", "Series", "Episode", "Play", "Published", "Description", "Location", "URL", "Playlist")
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers )
        return self.tableWidget

    def grid_box_buttons(self):
        """
        episode tab layouts and widgets are packed here. Just the add, text field, and sync buttons
        :return:
        """
        add = self.add_cast()
        sync = self.sync_button()

        grid = QGridLayout()
        grid.setColumnStretch(1,4)

        grid.addWidget(sync, 0, 0)
        grid.addWidget(self.line, 0, 1)
        grid.addWidget(add, 0, 2)

        return grid

    def browser_h_box(self):
        """
        Vertical layout. I know it says h_box. Changed as I had to add a few things later.
        :return:
        """
        h_box = QVBoxLayout()
        h_box.addWidget(self.episodes())
        return h_box

    """
    Browser stuff ends here
    """
    def status_info(self, info):
        """
        This updates the status bar message as needed by other functions.
        :param info:
        :return:
        """
        self.status.repaint()
        self.status.showMessage(info)

    def app_show(self):
        """
        Calls the vertical layout to do the packing, sets the widget that the vertical
        box is assigned to as the central widget, sets title and shows app.
        :return:
        """
        self.v_box()
        self.setCentralWidget(self.widg)
        #self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('PyCast')
        self.show()



if __name__ == "__main__":
    """
    Instantiates objects and allows to exit once closed
    """
    app = QApplication(sys.argv)
    ex = Player()
    sys.exit(app.exec_())