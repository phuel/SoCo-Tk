from viewmodelbase import ViewModelBase

class QueueTrackViewModel(ViewModelBase):
    """ Viewmodel for a track in the queue. """
   
    def __init__(self, index, entry):
        ViewModelBase.__init__(self)
        self['index'] = index
        self['uri'] = entry.resources[0].uri
        self['title'] = entry.title
        self['album'] = entry.album
        self['artist'] = entry.creator
        self['album_art'] = entry.album_art_uri
        self['duration'] = entry.resources[0].duration
        self['selected'] = False
