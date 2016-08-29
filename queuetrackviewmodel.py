from viewmodelbase import ViewModelBase
import keynames as kn

class QueueTrackViewModel(ViewModelBase):
    """ Viewmodel for a track in the queue. """
   
    def __init__(self, index, entry):
        """ Constructor """
        ViewModelBase.__init__(self)
        self.SelectionCallback = None
        self[kn.index] = index
        self[kn.uri] = entry.resources[0].uri
        self[kn.title] = entry.title
        self[kn.album] = entry.album
        self[kn.artist] = entry.creator
        self[kn.album_art] = entry.album_art_uri
        self[kn.duration] = entry.resources[0].duration
        self[kn.selected] = False
    
    def selectAndPlay(self):
        """ Select and play this track. """
        if self.SelectionCallback:
            self.SelectionCallback(self[kn.index])
