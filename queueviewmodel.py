from viewmodelbase import ViewModelBase
from queuetrackviewmodel import QueueTrackViewModel

class QueueViewModel(ViewModelBase):
    def __init__(self):
        ViewModelBase.__init__(self)
        self.SelectAndPlay = None
        self['entries'] = []
        self['current_track'] = 0
    
    @property
    def length(self):
        return len(self['entries'])
    
    def setEntries(self, queue):
        entries = []
        index = 1
        for entry in queue:
            entryVm = QueueTrackViewModel(index, entry)
            entryVm.SelectionCallback = self.__selectAndPlay
            entryVm['selected'] = index == self['current_track']
            entries.append(entryVm)
            index += 1
        self['entries'] = entries

    def setCurrentTrack(self, index):
        if self['current_track'] == int(index):
            return False 
        self['current_track'] = int(index)
        for entry in self['entries']:
            entry['selected'] = entry['index'] == self['current_track']
        return True 
    
    def __selectAndPlay(self, index):
        self.setCurrentTrack(index)
        if self.SelectAndPlay:
            self.SelectAndPlay(index)
    
    def __clearEntries(self):
        for entry in self['entries']:
            entry.SelectionCallback = None
