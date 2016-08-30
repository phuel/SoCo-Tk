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
import keynames as kn

class PlayerViewModel(ViewModelBase):
    """ The view model for a zone player. 
        This class holds the current track and the queue and handles the events from the player. """

    def __init__(self, ip):
        """ Constructor.
            Argument: ip = the player's ip address. '"""
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
        self[kn.current_state] = None
        self[kn.uid] = self.__soco.uid
        self[kn.player_name] = self.__soco.player_name
        self[kn.volume] = self.__soco.volume
        self[kn.can_play] = False
        self[kn.can_pause] = False
        self[kn.can_play_or_pause] = False
        self[kn.can_stop] = False
        self[kn.can_go_next] = False
        self[kn.can_go_previous] = False

        self.CurrentTrack = CurrentTrackViewModel()
        self.Queue = QueueViewModel()
        self.Queue.SelectAndPlay = self.__selectAndPlay

    def __str__(self):
        """ Returns a string representation for this player. """
        name = self.__soco.speaker_info['zone_name']
        if name is None:
            name = 'Unnamed'
        return name

    def __del__(self):
        """ Destructor. """
        del self.__soco
    
    @staticmethod
    def get_speaker_ips():
        """ Returns a list of all player ip addresses. """
        return [s.ip_address for s in soco.discover()]

    @staticmethod
    def stopEventListener():
        """ Unsubscribes from all Sonos events. """
        event_listener.stop()

    @property
    def display_name(self):
        """ Returns the display name of this player. """
        return "%s (%s)" % (self.__soco.player_name, self.__soco.ip_address)

    def isValidSpeaker(self):
        """ Returns True if this instance does not represent a valid Sonos player. """
        return not self.__soco.speaker_info is None
    
    def setVolume(self, volume):
        """ Sets the volume of this player. """
        self.__soco.volume = volume

    def subscribe(self):
        """ Subscribe to the Sonos events. """
        self.__subscriptions.append((self.__soco.avTransport.subscribe(auto_renew=True), self.__avTransportEvent))
        self.__subscriptions.append((self.__soco.contentDirectory.subscribe(auto_renew=True), self.__contentDirectoryEvent))
        self.__subscriptions.append((self.__soco.renderingControl.subscribe(auto_renew=True), self.__renderingControlEvent))
    
    def unsubscribe(self):
        """ Unsubscribe from the Sonos events. """
        for subscription in self.__subscriptions:
            subscription[0].unsubscribe()
        self.__subscriptions = []

    def handleEvents(self):
        """ Function to update view model from the Sonos events.
            This function needs to be called in regular intervals. """
        for subscription in self.__subscriptions:
            while not subscription[0].events.empty():
                event = subscription[0].events.get()
                subscription[1](event)
        if self[kn.current_state] == "PLAYING":
            self.CurrentTrack.updatePosition()
                    
    def __avTransportEvent(self, event):
        """ Handler for transport events (changes of the current track). """
        self[kn.current_state] = event.variables['transport_state']
        self.__updateAllowedCommands()
        baseUri = "http://%s:1400" % self.__soco.ip_address        
        self.CurrentTrack.update(event.variables['current_track_meta_data'], baseUri)
        trackChanged = self.Queue.setCurrentTrack(event.variables[kn.current_track])
        if trackChanged or self[kn.current_state] == kn.PLAYING:
            track = self.__soco.get_current_track_info()
            self.CurrentTrack.start(track[kn.position])
        elif self[kn.current_state] == kn.STOPPED:
            self.CurrentTrack.start("0:0:0")

    def __contentDirectoryEvent(self, event):
        """ Handler for content directory events (changes of the queue). """
        queue = self.__soco.get_queue()
        self.Queue.setEntries(queue)
        self.__updateAllowedCommands()

    def __renderingControlEvent(self, event):
        """ Handler for redering control events (volume changes). """
        if hasattr(event, kn.volume):
            self[kn.volume] = event.volume['Master']
        if hasattr(event, kn.mute):
            self[kn.mute] = event.mute['Master']

    def __updateAllowedCommands(self):
        """ Update the state of the commands supported by this viwe model. """
        queueLen = self.Queue.length
        self[kn.can_play] = queueLen > 0 and self[kn.current_state] in ( kn.STOPPED, kn.PAUSED_PLAYBACK )
        self[kn.can_pause] = self[kn.current_state] == kn.PLAYING
        self[kn.can_stop] = self[kn.current_state] == kn.PLAYING
        self[kn.can_play_or_pause] = self[kn.can_play] or self[kn.can_pause]
        self[kn.can_go_next] = queueLen
        self[kn.can_go_previous] = queueLen
         
    def __selectAndPlay(self, index):
        """ Select and play a tray after a click in the queue view. """
        self.play_from_queue(index - 1) 
    
    def play(self):
        """ Play the current track. """
        self.__soco.play()

    def play_from_queue(self, index):
        """ Play the track with the specified index in the queue. """
        self.__soco.play_from_queue(index)

    def pause(self):
        """ Pause the current track. """
        self.__soco.pause()
    
    def stop(self):
        """ Stop the current track. """
        self.__soco.stop()

    def previous(self):
        """ Play the previous track. """
        self.__soco.previous()
    
    def next(self):
        """ Play the next track. """
        self.__soco.next()

    def mute(self):
        """" Mute the player. """
        self.__soco.mute = not self.__soco.mute
