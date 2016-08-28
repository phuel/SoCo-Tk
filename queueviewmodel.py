from viewmodelbase import ViewModelBase
from queuetrackviewmodel import QueueTrackViewModel

class QueueViewModel(ViewModelBase):
    def __init__(self):
        ViewModelBase.__init__(self)
        self['entries'] = []
        self._currentTrack = 0
    
    @property
    def length(self):
        return len(self['entries'])
    
    def setEntries(self, queue):
        entries = []
        index = 1
        for entry in queue:
            entryVm = QueueTrackViewModel(index, entry)
            entryVm['selected'] = index == self._currentTrack
            entries.append(entryVm)
            index += 1
        self['entries'] = entries

    def setSelectedEntry(self, index):
        if self._currentTrack == int(index):
            return False 
        self._currentTrack = int(index)
        for entry in self['entries']:
            entry['selected'] = entry['index'] == self._currentTrack
        return True 