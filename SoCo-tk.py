#!/usr/bin/env python

import Tkinter as tk
import logging, traceback
logging.basicConfig(format='%(asctime)s %(levelname)10s: %(message)s', level = logging.ERROR)

import tkMessageBox
import base64
import platform, os

from appsettings import AppSettings
from playerviewmodel import PlayerViewModel 
from albumimageprovider import AlbumImageProvider
from progressmeter import Meter
from images import Images

try:
    from PIL import Image, ImageTk
except:
    logging.error('Could not import PIL')
    logging.error(traceback.format_exc())
    ImageTk = None
    Image = None

USER_DATA = None

if platform.system() == 'Windows':
    USER_DATA = os.path.join(os.getenv('APPDATA'), 'SoCo-Tk')
elif platform.system() == 'Linux':
    USER_DATA = '%(sep)shome%(sep)s%(name)s%(sep)s.config%(sep)sSoCo-Tk%(sep)s' % {
    'sep' : os.sep,
    'name': os.environ['LOGNAME']
    }    
##elif platform.system() == 'Mac':
##    pass

settings = AppSettings(USER_DATA)

class CurrentTrackView(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.columnconfigure(1, weight = 1)

        self.__images = AlbumImageProvider(settings)

        self.empty_info = '-'
        self.__parent = parent
        self._labels = {}
        self.__image = None
        infoIndex = 0

        ###################################
        # Title
        ###################################
        label = tk.Label(self, text = 'Title:')
        label.grid(row = infoIndex,
                   column = 0,
                   sticky = 'w')
        
        self._labels['title'] = tk.Label(self,
                                         anchor = 'w')
        
        self._labels['title'].grid(row = infoIndex,
                                   column = 1,
                                   padx = 5,
                                   pady = 5,
                                   sticky = 'we')
        infoIndex += 1

        ###################################
        # Artist
        ###################################
        label = tk.Label(self, text = 'Artist:')
        label.grid(row = infoIndex,
                   column = 0,
                   sticky = 'w')
        
        self._labels['artist'] = tk.Label(self,
                                          anchor = 'w')
        
        self._labels['artist'].grid(row = infoIndex,
                                    column = 1,
                                    padx = 5,
                                    sticky = 'we')
        infoIndex += 1

        ###################################
        # Album
        ###################################
        label = tk.Label(self, text = 'Album:')
        label.grid(row = infoIndex,
                   column = 0,
                   sticky = 'w')
        
        self._labels['album'] = tk.Label(self,
                                         anchor = 'w')
        
        self._labels['album'].grid(row = infoIndex,
                                   column = 1,
                                   padx = 5,
                                   pady = 5,
                                   sticky = 'we')
        infoIndex += 1

        ###################################
        # Album art
        ###################################
        self._album_art = tk.Label(self,
                                   image = tk.PhotoImage(),
                                   width = 150,
                                   height = 150)
        
        self._album_art.grid(row = infoIndex,
                             column = 0,
                             columnspan = 2,
                             padx = 5,
                             pady = 5)
        infoIndex += 1

        ###################################
        # Position
        ###################################
        label = tk.Label(self, text = 'Position:')
        label.grid(row = infoIndex,
                   column = 0,
                   sticky = 'w')
        
        self._labels['position'] = Meter(self, fillcolor='darkgray', bg='lightgray', relief="sunken", bd=1, height=14, text="")
        self._labels['position'].grid(row = infoIndex,
                                      column = 1,
                                      padx = 5,
                                      pady = 5,
                                      sticky = 'we')
 
    def clearImage(self):
        self.__showAlbumArt(None)
        
    def attachViewModel(self, viewModel):
        self.__viewModel = viewModel
        self.__viewModel.addListener(self.__onPropertyChanged)
    
    def detachViewModel(self):
        if self.__viewModel:
            self.__viewModel.removeListener(self.__onPropertyChanged)
            self.__viewModel = None
        for label in self.__labels:
            label.configure(text = self.empty_info)
        self.clearImage()

    def __onPropertyChanged(self, propertyName, viewModel):
        if propertyName == 'position':
            if viewModel['duration'] and viewModel['position']:
                showHours = viewModel['duration'].seconds > 3600
                position = self.__formatDuration(viewModel['position'], showHours) + " / " + self.__formatDuration(viewModel['duration'], showHours)
                self._labels[propertyName].set(value=viewModel['position'].total_seconds() / viewModel['duration'].total_seconds(), text=position)
            else:
                self._labels[propertyName].set(value=0, text="")
        elif propertyName in self._labels:
            value = viewModel[propertyName]
            self._labels[propertyName].configure(text=value)
        elif propertyName == 'album_art':
            image = self.__images.getImage(viewModel['uri'], viewModel['album_art'])
            self.__showAlbumArt(image)
    
    def __formatDuration(self, time, showHours):
        hours, remainder = divmod(time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60) 
        if showHours:
            return "%d:%02d:%02d" % (hours, minutes, seconds)
        return "%d:%02d" % (minutes, seconds)

    def __showAlbumArt(self, image):
        if image is None:
            self._album_art.config(image = None)
            self.__image = None
            return

        widgetConfig = self._album_art.config()
        thumbSize = (int(widgetConfig['width'][4]),
                     int(widgetConfig['height'][4]))

        logging.debug('Resizing album art to: %s', thumbSize)
        image.thumbnail(thumbSize, Image.ANTIALIAS)
        self.__image = ImageTk.PhotoImage(image = image)
        self._album_art.configure(image = self.__image)
        
class SonosList(tk.PanedWindow):

    def __init__(self, parent):
        self.__parent = parent
        tk.PanedWindow.__init__(self, parent, sashrelief = tk.RAISED)

        self.__parent.protocol('WM_DELETE_WINDOW', self._cleanExit)
        
        parent.rowconfigure(0, weight = 1)
        parent.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)

        self.grid(row = 0,
                  column = 0,
                  ipadx = 5,
                  ipady = 5,
                  sticky = 'news')

        self._controlButtons = {}
        self._infoWidget = {}
        self._currentTrackView = None

        self.__lastSelected = None
        self.__currentSpeaker = None
        self.__subscription = None
        self.__currentState = None
        self.__speakers = []
        self.__speakerId = tk.StringVar()

        self._createWidgets()
        self._createMenu()

        self._loadSettings()

    def destroy(self):
        try:
            PlayerViewModel.stopEventListener()

            for speaker in self.__speakers:
                del speaker
            self.__speakers = []
            self.__currentSpeaker = None

            settings.close()
        except:
            logging.error('Error while destroying')
            logging.error(traceback.format_exc())
        
    def __del__(self):
        self.destroy()

    def scanSpeakers(self):
        ips = PlayerViewModel.get_speaker_ips()

        speakers = []
        for ip in ips:
            speaker = PlayerViewModel(ip)
            if not speaker.isValidSpeaker():
                logging.warning('Speaker %s does not have any info (probably a bridge), skipping...', ip)
                continue

            speakers.append(speaker)

        logging.debug('Found %d speaker(s)', len(speakers))
        if len(speakers) > 1:
            logging.debug('Sorting speakers based on name')
            speakers = sorted(speakers,
                              cmp = lambda a,b: cmp(str(a), str(b)))

        self.__addSpeakers(speakers)
        return speakers

    def __addSpeakers(self, speakers):
        logging.debug('Deleting all items from list')
        
        self._speakermenu.delete(0, len(speakers))
        self._speakers = []

        if not speakers:
            logging.debug('No speakers to add, returning')
            return
        
        logging.debug('Inserting new items (%d)', len(speakers))
        for speaker in speakers:
            self._speakers.append(speaker)
            self._speakermenu.add_radiobutton(label=speaker.display_name, value=speaker['uid'], variable=self.__speakerId,
                                              command=self._selectSpeaker)
        
    def _createWidgets(self):
        logging.debug('Creating widgets')
                          
        # Left frame
        self._left = tk.Frame(self)
        self.add(self._left)

        # Right frame
        self._right = tk.Frame(self)
        self.add(self._right)

        # Create queue list
        panel = tk.Frame(self._right)
        scrollbar = tk.Scrollbar(panel)
        self._queuebox = tk.Listbox(panel, selectmode = tk.EXTENDED)

        scrollbar.config(command = self._queuebox.yview)
        self._queuebox.config(yscrollcommand = scrollbar.set)
        self._queuebox.bind('<Double-Button-1>', self._playSelectedQueueItem)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._queuebox.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        panel.pack(side=tk.TOP, fill=tk.BOTH, padx=5, pady=5, expand=1)        

        self._createButtons()
                          
        self._createInfoWidgets()

        self.after(500, self.__checkForEvents)

    def __checkForEvents(self):
        speaker = self.__currentSpeaker
        if speaker:
            speaker.handleEvents()
        self.after(500, self.__checkForEvents)

    def __onPropertyChanged(self, propertyName, viewModel):
        if propertyName == 'CurrentState':
            self.__showSpeakerAndState(viewModel)
            self._configurePlayOrPauseButton(viewModel[propertyName] != "PLAYING")
        elif propertyName == 'Queue':
            self._showQueue(viewModel[propertyName])
        elif propertyName == 'volume':
            self._infoWidget['volume'].set(viewModel[propertyName])
        elif propertyName == 'mute':
            self._infoWidget['muteVar'].set(viewModel[propertyName])
        elif propertyName == 'CanPlayOrPause':
            self._updateButton('Play', viewModel[propertyName])
        elif propertyName == 'CanPlay':
            self._updateMenu('Play', viewModel[propertyName])
        elif propertyName == 'CanPause':
            self._updateMenu('Pause', viewModel[propertyName])
        elif propertyName == 'CanStop':
            self._updateButton('Stop', viewModel[propertyName])
            self._updateMenu('Stop', viewModel[propertyName])
        elif propertyName == 'CanGoNext':
            self._updateButton('Next', viewModel[propertyName])
            self._updateMenu('Next', viewModel[propertyName])
        elif propertyName == 'CanGoPrevious':
            self._updateButton('Previous', viewModel[propertyName])
            self._updateMenu('Previous', viewModel[propertyName])

    def _createInfoWidgets(self):
        ###################################
        # Volume
        ###################################
        
        panel = tk.Frame(self._left)
        panel.columnconfigure(1, weight=1)

        label = tk.Label(panel, text = 'Volume:')
        label.grid(row = 0, column = 0, sticky = 'w', padx = 5)

        self._infoWidget['volume'] = tk.Scale(panel,
                                              from_ = 0,
                                              to = 100,
                                              tickinterval = 10,
                                              orient = tk.HORIZONTAL)
        
        self._infoWidget['volume'].grid(row=0, column=1, pady = 5, sticky='we')
        self._infoWidget['volume'].bind('<ButtonRelease-1>', self._volumeChanged)

        self._infoWidget['muteVar'] = tk.IntVar()
        self._infoWidget['mute'] = tk.Checkbutton(panel, image=Images.Get("appbar.sound.mute.png"),
                                                  indicatoron=False,
                                                  command=self.__mute,
                                                  variable=self._infoWidget['muteVar'])
        self._infoWidget['mute'].grid(row=0, column=2, padx = 5)

        panel.pack(side=tk.BOTTOM, fill=tk.X)

        ###################################
        # Current track
        ###################################
        self._currentTrackView = CurrentTrackView(self._left)
        self._currentTrackView.pack(side=tk.TOP, fill=tk.BOTH)

    def __getSelectedSpeaker(self):
        return self.__currentSpeaker

    def __setSelectedSpeaker(self, speaker):
        if self.__currentSpeaker:
            self.__currentSpeaker.unscubscribe()
            self.__currentSpeaker.removeListener(self.__onPropertyChanged)
            self._currentTrackView.detachViewModel()
        self._disableButtons()
        self.__currentSpeaker = speaker
        if speaker:
            speaker.addListener(self.__onPropertyChanged)
            speaker.subscribe()
            self._infoWidget['volume'].config(state = tk.ACTIVE)
            self._infoWidget['mute'].config(state = tk.ACTIVE)
            self._currentTrackView.attachViewModel(speaker.CurrentTrack)
        else:
            self._infoWidget['volume'].config(state = tk.DISABLED)
            self._infoWidget['volume'].set(0)
            self._infoWidget['mute'].config(state = tk.DISABLED)
        self.__showSpeakerAndState(speaker)

    def __showSpeakerAndState(self, speaker):
        title = "SoCo"
        if speaker:
            title += " - " + speaker['player_name']
            if speaker['CurrentState']:
                title += " - " + speaker['CurrentState']
        self.__parent.wm_title(title)

    def __getSelectedQueueItem(self):
        widget = self._queuebox

        selection = widget.curselection()
        if not selection:
            return None, None

        index = int(selection[0])

        speaker = self.__getSelectedSpeaker()
        assert len(speaker['Queue']) > index
        track = speaker['Queue'][index]
        return track, index
        
    def _volumeChanged(self, evt):
        speaker = self.__getSelectedSpeaker()
        if not speaker:
            logging.warning('No speaker selected')
            return
        
        volume = self._infoWidget['volume'].get()

        logging.debug('Changing volume to: %d', volume)
        speaker.setVolume(volume)

    def _selectSpeaker(self):
        speaker = None
        for s in self._speakers:
            if s['uid'] == self.__speakerId.get():
                speaker = s
        if speaker == self.__currentSpeaker:
            logging.info('Speaker already selected, skipping')
            return
        
        self.__setSelectedSpeaker(speaker)
                
        logging.debug('Zoneplayer: "%s"', speaker)

        logging.debug('Storing last_selected: %s' % speaker['uid'])
        settings.setConfig('last_selected', speaker['uid'])

    def _showQueue(self, queue):
        logging.debug('Deleting old items')
        self._queuebox.delete(0, tk.END)

        logging.debug('Inserting items (%d) to listbox', len(queue))
        for item in queue:
            self._queuebox.insert(tk.END, item.display_name)

        index = self.__getSelectedSpeaker().getCurrentTrackIndex()
        if index >= 0:
            self._queuebox.selection_clear(0, tk.END)
            self._queuebox.selection_anchor(index)
            self._queuebox.selection_set(index)

    def _disableButtons(self):
        newState = tk.DISABLED
        for (key,button) in self._controlButtons.items():
            button.config(state = newState)
            self._playbackmenu.entryconfigure(key, state=newState)
        self._playbackmenu.entryconfigure('Pause', state=newState)

    def _updateButton(self, key, enabled):
        newState = tk.ACTIVE if enabled else tk.DISABLED
        self._controlButtons[key].configure(state=newState)
    
    def _updateMenu(self, key, enabled):
        newState = tk.ACTIVE if enabled else tk.DISABLED
        self._playbackmenu.entryconfigure(key, state=newState)

    def _configurePlayOrPauseButton(self, play):
        if play:
            self._controlButtons['Play'].configure(image = Images.Get("appbar.control.play.png"), command=self.__play)
        else:
            self._controlButtons['Play'].configure(image = Images.Get("appbar.control.pause.png"), command=self.__pause)
        
    def _createButtons(self):
        logging.debug('Creating buttons')
        buttonWidth = 32
        
        panel = tk.Frame(self._left)
        button_prev = tk.Button(panel,
                                width = buttonWidth,
                                command = self.__previous,
                                image = Images.Get("appbar.chevron.left.png"))
        button_prev.pack(side=tk.LEFT, padx = 5, pady = 5)
        self._controlButtons['Previous'] = button_prev

        button_play = tk.Button(panel,
                                 width = buttonWidth,
                                 command = self.__play,
                                 image = Images.Get("appbar.control.play.png"))
        button_play.pack(side=tk.LEFT, padx = 5, pady = 5)
        self._controlButtons['Play'] = button_play

        button_stop = tk.Button(panel,
                                 width = buttonWidth,
                                 command = self.__stop,
                                 image = Images.Get("appbar.control.stop.png"))
        button_stop.pack(side=tk.LEFT, padx = 5, pady = 5)
        self._controlButtons['Stop'] = button_stop

        button_next = tk.Button(panel,
                                width = buttonWidth,
                                command = self.__next,
                                image = Images.Get("appbar.chevron.right.png"))
        button_next.pack(side=tk.LEFT, padx = 5, pady = 5)
        self._controlButtons['Next'] = button_next
        panel.pack(side=tk.BOTTOM)

    def _createMenu(self):
        logging.debug('Creating menu')
        self._menubar = tk.Menu(self)
        self.__parent.config(menu = self._menubar)
        
        # File menu
        self._filemenu = tk.Menu(self._menubar, tearoff=0)
        self._menubar.add_cascade(label="File", menu=self._filemenu)

        self._filemenu.add_command(label="Scan for speakers", command=self.scanSpeakers)
        self._filemenu.add_command(label="Exit", command=self._cleanExit)

        self._speakermenu = tk.Menu(self._menubar, tearoff=0)
        self._menubar.add_cascade(label="Speaker", menu=self._speakermenu)
        
        # Playback menu
        self._playbackmenu = tk.Menu(self._menubar, tearoff=0)
        self._menubar.add_cascade(label="Playback", menu=self._playbackmenu)

        self._playbackmenu.add_command(label = "Play",     command = self.__play)
        self._playbackmenu.add_command(label = "Pause",    command = self.__pause)
        self._playbackmenu.add_command(label = "Stop",     command = self.__stop)
        self._playbackmenu.add_command(label = "Previous", command = self.__previous)
        self._playbackmenu.add_command(label = "Next",     command = self.__next)

    def _playSelectedQueueItem(self, evt):
        try:
            track, track_index = self.__getSelectedQueueItem()
            speaker = self.__getSelectedSpeaker()

            if speaker is None or\
               track_index is None:
                logging.warning('Could not get track or speaker (%s, %s)', track_index, speaker)
                return
            
            speaker.play_from_queue(track_index)
        except:
            logging.error('Could not play queue item')
            logging.error(traceback.format_exc())
            tkMessageBox.showerror(title = 'Queue...',
                                   message = 'Error playing queue item, please check error log for description')
        

    def __previous(self):
        speaker = self.__getSelectedSpeaker()
        if not speaker:
            raise SystemError('No speaker selected, this should not happen')
        speaker.previous()
        
    def __next(self):
        speaker = self.__getSelectedSpeaker()
        if not speaker:
            raise SystemError('No speaker selected, this should not happen')
        speaker.next()

    def __pause(self):
        speaker = self.__getSelectedSpeaker()
        if not speaker:
            raise SystemError('No speaker selected, this should not happen')
        speaker.pause()

    def __play(self):
        speaker = self.__getSelectedSpeaker()
        if not speaker:
            raise SystemError('No speaker selected, this should not happen')
        speaker.play()

    def __stop(self):
        speaker = self.__getSelectedSpeaker()
        if not speaker:
            raise SystemError('No speaker selected, this should not happen')
        speaker.stop()

    def __mute(self):
        speaker = self.__getSelectedSpeaker()
        if not speaker:
            raise SystemError('No speaker selected, this should not happen')
        speaker.mute()

    def _loadSettings(self):
        # Load window geometry
        geometry = settings.getConfig('window_geometry')
        if geometry:
            try:
                logging.info('Found geometry "%s", applying', geometry)
                self.__parent.geometry(geometry)
            except:
                logging.error('Could not set window geometry')
                logging.error(traceback.format_exc())

        # Load sash_coordinates
        self.update_idletasks()
        sashes = settings.getConfig('sash_coordinates')
        if sashes:
            for sash_info in sashes.split(','):
                if len(sash_info) < 1: continue
                try:
                    logging.debug('Setting sash: "%s"' % sash_info)
                    index, x, y = map(int, sash_info.split(':'))
                    self.sash_place(index, x, y)
                except:
                    logging.error('Could not set sash: "%s"' % sash_info)
                    logging.error(traceback.format_exc())

        # Scan speakers
        speakers = self.scanSpeakers()

        # Load last selected speaker
        selected_speaker_uid = settings.getConfig('last_selected')
        self.__speakerId.set(selected_speaker_uid)
        logging.debug('Last selected speaker: %s', selected_speaker_uid)

        for speaker in speakers:
            if speaker['uid'] == selected_speaker_uid:
                self.__setSelectedSpeaker(speaker)

    def _cleanExit(self):
        try:
            geometry = self.__parent.geometry()
            if geometry:
                logging.debug('Storing geometry: "%s"', geometry)
                settings.setConfig('window_geometry', geometry)

            listOfPanes = self.panes()
            sashes = []
            for index in range(len(listOfPanes) - 1):
                x, y = self.sash_coord(index)
                sashes.append(':'.join((str(index),
                                        str(x),
                                        str(y))))

            finalSashValue = ','.join(sashes)
            logging.debug('Storing sashes: "%s"', finalSashValue)
            settings.setConfig('sash_coordinates', finalSashValue)
                
        except:
            logging.error('Error making clean exit')
            logging.error(traceback.format_exc())
        finally:
            self.destroy()
            self.__parent.quit()

def main(root):
    logging.debug('Main')
    sonosList = SonosList(root)
    sonosList.mainloop()
    sonosList.destroy()

if __name__ == '__main__':
    logging.info('Using data dir: "%s"', USER_DATA)
    
    root = tk.Tk()
    try:
        root.wm_title('SoCo')
        root.minsize(800,400)
        main(root)
    except:
        logging.error(traceback.format_exc())
    finally:
        root.quit()
        root.destroy()
