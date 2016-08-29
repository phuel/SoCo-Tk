#!/usr/bin/env python

import Tkinter as tk
import logging, traceback
logging.basicConfig(format='%(asctime)s %(levelname)10s: %(message)s', level = logging.ERROR)

import tkMessageBox
import base64
import platform, os

from appsettings import AppSettings
from playerviewmodel import PlayerViewModel 
from currenttrackview import CurrentTrackView
from queueview import QueueView
from images import Images
import keynames as kn

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
        self._queueView = None
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
            self._speakermenu.add_radiobutton(label=speaker.display_name, value=speaker[kn.uid], variable=self.__speakerId,
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
        self._queueView = QueueView(self._right)
        
        self._createButtons()
        self._createInfoWidgets()

        self.after(500, self.__checkForEvents)

    def __checkForEvents(self):
        speaker = self.__currentSpeaker
        if speaker:
            speaker.handleEvents()
        self.after(500, self.__checkForEvents)

    def __onPropertyChanged(self, propertyName, viewModel):
        if propertyName == kn.current_state:
            self.__showSpeakerAndState(viewModel)
            self._configurePlayOrPauseButton(viewModel[propertyName] != "PLAYING")
        elif propertyName == kn.volume:
            self._infoWidget[kn.volume].set(viewModel[propertyName])
        elif propertyName == kn.mute:
            self._infoWidget['muteVar'].set(viewModel[propertyName])
        elif propertyName == kn.can_play_or_pause:
            self._updateButton('Play', viewModel[propertyName])
        elif propertyName == kn.can_play:
            self._updateMenu('Play', viewModel[propertyName])
        elif propertyName == kn.can_pause:
            self._updateMenu('Pause', viewModel[propertyName])
        elif propertyName == kn.can_stop:
            self._updateButton('Stop', viewModel[propertyName])
            self._updateMenu('Stop', viewModel[propertyName])
        elif propertyName == kn.can_go_next:
            self._updateButton('Next', viewModel[propertyName])
            self._updateMenu('Next', viewModel[propertyName])
        elif propertyName == kn.can_go_previous:
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

        self._infoWidget[kn.volume] = tk.Scale(panel,
                                               from_ = 0,
                                               to = 100,
                                               tickinterval = 10,
                                               orient = tk.HORIZONTAL)
        
        self._infoWidget[kn.volume].grid(row=0, column=1, pady = 5, sticky='we')
        self._infoWidget[kn.volume].bind('<ButtonRelease-1>', self._volumeChanged)

        self._infoWidget['muteVar'] = tk.IntVar()
        self._infoWidget[kn.mute] = tk.Checkbutton(panel, image=Images.Get("appbar.sound.mute.png"),
                                                  indicatoron=False,
                                                  command=self.__mute,
                                                  variable=self._infoWidget['muteVar'])
        self._infoWidget[kn.mute].grid(row=0, column=2, padx = 5)

        panel.pack(side=tk.BOTTOM, fill=tk.X)

        ###################################
        # Current track
        ###################################
        self._currentTrackView = CurrentTrackView(self._left, settings)
        self._currentTrackView.pack(side=tk.TOP, fill=tk.BOTH)

    def __getSelectedSpeaker(self):
        return self.__currentSpeaker

    def __setSelectedSpeaker(self, speaker):
        if self.__currentSpeaker:
            self.__currentSpeaker.unscubscribe()
            self.__currentSpeaker.removeListener(self.__onPropertyChanged)
            self._currentTrackView.detachViewModel()
            self._queueView.detachViewModel()
        self._disableButtons()
        self.__currentSpeaker = speaker
        if speaker:
            speaker.addListener(self.__onPropertyChanged)
            speaker.subscribe()
            self._infoWidget[kn.volume].config(state = tk.ACTIVE)
            self._infoWidget[kn.mute].config(state = tk.ACTIVE)
            self._currentTrackView.attachViewModel(speaker.CurrentTrack)
            self._queueView.attachViewModel(speaker.Queue, speaker)
        else:
            self._infoWidget[kn.volume].config(state = tk.DISABLED)
            self._infoWidget[kn.volume].set(0)
            self._infoWidget[kn.mute].config(state = tk.DISABLED)
        self.__showSpeakerAndState(speaker)

    def __showSpeakerAndState(self, speaker):
        title = "SoCo"
        if speaker:
            title += " - " + speaker[kn.player_name]
            if speaker[kn.current_state]:
                title += " - " + speaker[kn.current_state]
        self.__parent.wm_title(title)

    def _volumeChanged(self, evt):
        speaker = self.__getSelectedSpeaker()
        if not speaker:
            logging.warning('No speaker selected')
            return
        
        volume = self._infoWidget[kn.volume].get()

        logging.debug('Changing volume to: %d', volume)
        speaker.setVolume(volume)

    def _selectSpeaker(self):
        speaker = None
        for s in self._speakers:
            if s[kn.uid] == self.__speakerId.get():
                speaker = s
        if speaker == self.__currentSpeaker:
            logging.info('Speaker already selected, skipping')
            return
        
        self.__setSelectedSpeaker(speaker)
                
        logging.debug('Zoneplayer: "%s"', speaker)

        logging.debug('Storing last_selected: %s' % speaker[kn.uid])
        settings.setConfig('last_selected', speaker[kn.uid])

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
        
        panel = tk.Frame(self._left)
        button_prev = tk.Button(panel,
                                command = self.__previous,
                                image = Images.Get("appbar.chevron.left.png"))
        button_prev.pack(side=tk.LEFT, fill=tk.X, expand=1, padx=2, pady=5)
        self._controlButtons['Previous'] = button_prev

        button_play = tk.Button(panel,
                                 command = self.__play,
                                 image = Images.Get("appbar.control.play.png"))
        button_play.pack(side=tk.LEFT, fill=tk.X, expand=1, padx=2, pady=5)
        self._controlButtons['Play'] = button_play

        button_stop = tk.Button(panel,
                                 command = self.__stop,
                                 image = Images.Get("appbar.control.stop.png"))
        button_stop.pack(side=tk.LEFT, fill=tk.X, expand=1, padx=2, pady=5)
        self._controlButtons['Stop'] = button_stop

        button_next = tk.Button(panel,
                                command = self.__next,
                                image = Images.Get("appbar.chevron.right.png"))
        button_next.pack(side=tk.LEFT, fill=tk.X, expand=1, padx=2, pady=5)
        self._controlButtons['Next'] = button_next
        panel.pack(side=tk.BOTTOM, fill=tk.X)

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
            if speaker[kn.uid] == selected_speaker_uid:
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
