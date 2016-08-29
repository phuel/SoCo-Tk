from viewmodelbase import ViewModelBase
from queuetrackviewmodel import QueueTrackViewModel
import keynames as kn

class QueueViewModel(ViewModelBase):
    """ View model for the player queue. """
    def __init__(self):
        ViewModelBase.__init__(self)
        self.SelectAndPlay = None
        self[kn.entries] = []
        self[kn.current_track] = 0
    
    @property
    def length(self):
        """ Gets the number of tracks in the queue. """
        return len(self['entries'])
    
    def setEntries(self, queue):
        """ Sets the queue entries from the information from an event. """
        entries = []
        index = 1
        for entry in queue:
            entryVm = QueueTrackViewModel(index, entry)
            entryVm.SelectionCallback = self.__selectAndPlay
            entryVm[kn.selected] = index == self[kn.current_track]
            entries.append(entryVm)
            index += 1
        self['entries'] = entries

    def setCurrentTrack(self, index):
        """ Sets the current track in the queue. """
        if self[kn.current_track] == int(index):
            return False 
        self[kn.current_track] = int(index)
        for entry in self[kn.entries]:
            entry[kn.selected] = entry[kn.index] == self[kn.current_track]
        return True 
    
    def __selectAndPlay(self, index):
        """ Select a queue entry and play it. """
        self.setCurrentTrack(index)
        if self.SelectAndPlay:
            self.SelectAndPlay(index)
    
    def __clearEntries(self):
        """ Clears the content of the queue. """
        for entry in self[kn.entries]:
            entry.SelectionCallback = None
