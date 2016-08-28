import logging

try:
    import soco
except:
    logging.warning('Could not import soco, trying from local file')
    try:
        import sys
        sys.path.append('./SoCo')
        import soco
    except:
        logging.error('Could not find SoCo library')
        soco = None
        exit()

from soco.events import event_listener

from viewmodelbase import ViewModelBase
from currenttrackviewmodel import CurrentTrackViewModel
from queueviewmodel import QueueViewModel

class PlayerViewModel(ViewModelBase):
    def __init__(self, ip):
        ViewModelBase.__init__(self)
        self.__soco = soco.SoCo(ip)
        
        try:
            self.__soco.get_speaker_info()
        except:
            logging.warn('Could not get info for speaker ' + ip)
        
        invalid_keys = [key for key, value in self.__soco.speaker_info.items() if value is None]
        for key in invalid_keys:
            del self.__soco.speaker_info[key]
        
        self.__ipAddress = ip
        self.__subscriptions = []
        self['CurrentState'] = None
        self['uid'] = self.__soco.uid
        self['player_name'] = self.__soco.player_name
        self['volume'] = self.__soco.volume
        self['CanPlay'] = False
        self['CanPause'] = False
        self['CanGoNext'] = False
        self['CanGoPrevious'] = False

        self.CurrentTrack = CurrentTrackViewModel()
        self.Queue = QueueViewModel()
        self.Queue.SelectAndPlay = self.__selectAndPlay

    def __str__(self):
        name = self.__soco.speaker_info['zone_name']
        if name is None:
            name = 'Unnamed'
        return name

    def __del__(self):
        del self.__soco
    
    @staticmethod
    def get_speaker_ips():
        return [s.ip_address for s in soco.discover()]

    @staticmethod
    def stopEventListener():
        event_listener.stop()

    @property
    def display_name(self): 
        return "%s (%s)" % (self.__soco.player_name, self.__soco.ip_address)

    def isValidSpeaker(self):
        return not self.__soco.speaker_info is None
    
    def setVolume(self, volume): 
        self.__soco.volume = volume

    def subscribe(self):
        self.__subscriptions.append((self.__soco.avTransport.subscribe(auto_renew=True), self.__avTransportEvent))
        self.__subscriptions.append((self.__soco.contentDirectory.subscribe(auto_renew=True), self.__contentDirectoryEvent))
        self.__subscriptions.append((self.__soco.renderingControl.subscribe(auto_renew=True), self.__renderingControlEvent))
    
    def unsubscribe(self):
        for subscription in self.__subscriptions:
            subscription[0].unsubscribe()
        self.__subscriptions = []

    def handleEvents(self):
        for subscription in self.__subscriptions:
            while not subscription[0].events.empty():
                event = subscription[0].events.get()
                subscription[1](event)
        if self['CurrentState'] == "PLAYING":
            self.CurrentTrack.updatePosition()
                    
    def __avTransportEvent(self, event):
        self['CurrentState'] = event.variables['transport_state']
        self.__updateAllowedCommands()
        baseUri = "http://%s:1400" % self.__soco.ip_address        
        self.CurrentTrack.updateFromEvent(event.variables['current_track_meta_data'], baseUri)
        trackChanged = self.Queue.setCurrentTrack(event.variables['current_track'])
        if trackChanged or self['CurrentState'] == "PLAYING":
            track = self.__soco.get_current_track_info()
            self.CurrentTrack.start(track['position'])
        elif self['CurrentState'] == "STOPPED":
            self.CurrentTrack.start("0:0:0")

    def __contentDirectoryEvent(self, event):
        queue = self.__soco.get_queue()
        self.Queue.setEntries(queue)
        self.__updateAllowedCommands()

    def __renderingControlEvent(self, event):
        if hasattr(event, 'volume'):
            self['volume'] = event.volume['Master']
        if hasattr(event, 'mute'):
            self['mute'] = event.mute['Master']

    def getCurrentTrackIndex(self):
        for index, item in enumerate(self.Queue['entries']):
            if item['uri'] == self.CurrentTrack['uri']:
                return index
        return -1

    def __updateAllowedCommands(self):
        queueLen = self.Queue.length
        self['CanPlay'] = queueLen > 0 and self['CurrentState'] in ( "STOPPED", "PAUSED_PLAYBACK" )
        self['CanPause'] = self['CurrentState'] == "PLAYING"
        self['CanStop'] = self['CurrentState'] == "PLAYING"
        self['CanPlayOrPause'] = self['CanPlay'] or self['CanPause']
        self['CanGoNext'] = queueLen
        self['CanGoPrevious'] = queueLen
         
    def __selectAndPlay(self, index):
        self.play_from_queue(index - 1) 
    
    def playOrPause(self):
        if self['CanPlay']:
            self.play()
        elif self['CanPause']:
            self.pause()

    def play(self):
        self.__soco.play()

    def play_from_queue(self, index):
        self.__soco.play_from_queue(index)

    def pause(self):
        self.__soco.pause()
    
    def stop(self):
        self.__soco.stop()

    def previous(self):
        self.__soco.previous()
    
    def next(self):
        self.__soco.next()

    def mute(self):
        self.__soco.mute = not self.__soco.mute
