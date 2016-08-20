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

from trackviewmodel import CurrentTrackViewModel, QueueTrackViewModel

class Changes(object):
    State = 1
    Position = 2
    Track = 3
    Queue = 4

class PlayerViewModel(object):
    def __init__(self, ip):
        self.__soco = soco.SoCo(ip)
        
        try:
            self.__soco.get_speaker_info()
        except:
            logging.warn('Could not get info for speaker ' + ip)
        
        invalid_keys = [key for key, value in self.speaker_info.items() if value is None]
        for key in invalid_keys:
            del self.speaker_info[key]
        
        self.__ipAddress = ip
        self.__subscription = None
        self.CurrentState = None
        self.CurrentTrack = CurrentTrackViewModel()
        self.Queue = []

    def __str__(self):
        name = self.speaker_info['zone_name']
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
    def speaker_info(self):
        return self.__soco.speaker_info
    
    @property
    def uid(self):
        return self.__soco.uid
    
    @property
    def player_name(self): 
        return self.__soco.player_name

    @property
    def display_name(self): 
        return "%s (%s)" % (self.__soco.player_name, self.__soco.ip_address)

    @property
    def volume(self): 
        return self.__soco.volume

    def subscribe(self):
        self.__subscription = self.__soco.avTransport.subscribe()
    
    def unsubscribe(self):
        if self.__subscription:
            self.__subscription.unsubscribe()
            self.__subscription = None
    
    def handleEvents(self):
        changes = []
        if self.__subscription:
            while not self.__subscription.events.empty():
                event = self.__subscription.events.get()
                state = event.variables['transport_state']
                if state != self.CurrentState:
                    self.CurrentState = state
                    changes.append(Changes.State)
                if self.CurrentTrack.updateFromEvent(event.variables['current_track_meta_data']):
                    changes.append(Changes.Track)
        return changes
                    
    def refresh(self):
        track = self.__soco.get_current_track_info()
        self.CurrentTrack.update(track)
        return self.CurrentTrack

    def refreshQueue(self):
        queue = self.__soco.get_queue()
        self.Queue = [QueueTrackViewModel(entry) for entry in queue]
        return self.Queue

    def getCurrentTrackIndex(self):
        for index, item in enumerate(self.Queue):
            if item.Uri == self.CurrentTrack["uri"]:
                return index
        return -1

    def play(self):
        self.__soco.play()

    def play_from_queue(self, index):
        self.__soco.play_from_queue(index)

    def pause(self):
        self.__soco.pause()
    
    def previous(self):
        self.__soco.previous()
    
    def next(self):
        self.__soco.next()
