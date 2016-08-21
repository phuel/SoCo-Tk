from viewmodelbase import ViewModelBase 

class CurrentTrackViewModel(ViewModelBase):
    def __init__(self):
        ViewModelBase.__init__(self)

    def updateFromEvent(self, entry, baseUri):
        if not entry:
            self.__clear()
            return
        self["uri"] = entry.resources[0].uri
        self["title"] = entry.title
        self["album"] = entry.album
        self["artist"] = entry.creator
        albumArt = entry.album_art_uri
        if not albumArt.startswith("http"):
            albumArt = baseUri + albumArt
        self["album_art"] = albumArt
        self["duration"] = entry.resources[0].duration
        
    def __clear(self):
        self["uri"] = ""
        self["title"] = ""
        self["album"] = ""
        self["artist"] = ""
        self["album_art"] = ""
        self["duration"] = ""

    def __getTrackProperty(self, track, item):
        return track[item] if item in track else ""
    
class QueueTrackViewModel(object):
    labelQueue = '%(artist)s - %(title)s'
    
    def __init__(self, entry):
        self.Uri = entry.resources[0].uri
        self.Title = entry.title
        self.Album = entry.album
        self.Artist = entry.creator
        self.AlbumArt = entry.album_art_uri
        self.Duration = entry.resources[0].duration

    @property
    def display_name(self):
        text = self.labelQueue % { 'artist' : self.Artist, 'title' : self.Title }
        if self.Duration:
            text += " (%s)" % self.Duration
        return text
