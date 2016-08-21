import datetime

from viewmodelbase import ViewModelBase 

class CurrentTrackViewModel(ViewModelBase):
    def __init__(self):
        ViewModelBase.__init__(self)
        self.__startPos = datetime.timedelta()
        self.__startTime = None
        self.__lastUri = None
        self.__clear()

    def updateFromEvent(self, entry, baseUri):
        if not entry:
            self.__clear()
            return
        self['uri'] = entry.resources[0].uri
        self['title'] = entry.title
        self['album'] = entry.album
        self['artist'] = entry.creator
        albumArt = entry.album_art_uri
        if not albumArt.startswith("http"):
            albumArt = baseUri + albumArt
        self['album_art'] = albumArt
        self['duration'] = self.__parseTime(entry.resources[0].duration)
        trackChanged = self.__lastUri != self['uri']
        self.__lastUri = self['uri']
        return trackChanged

    def start(self, position):
        self.__startPos = self.__parseTime(position)
        self['position'] = self.__startPos
        self.__startTime = datetime.datetime.now()
    
    def updatePosition(self):
        now = datetime.datetime.now()
        diff = now - self.__startTime
        self['position'] = self.__startPos + diff

    def __clear(self):
        self['uri'] = ""
        self['title'] = ""
        self['album'] = ""
        self['artist'] = ""
        self['album_art'] = ""
        self['duration'] = ""
        self['position'] = 0

    def __parseTime(self, time):
        if not time:
            return datetime.timedelta()
        hour, minute, second = time.split(":")
        return datetime.timedelta(hours=int(hour), minutes=int(minute), seconds=int(second))
    
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
