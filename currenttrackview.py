import logging, traceback
import Tkinter as tk

from albumimageprovider import AlbumImageProvider
from progressmeter import Meter
import keynames as kn

try:
    from PIL import Image, ImageTk
except:
    logging.error('Could not import PIL')
    logging.error(traceback.format_exc())
    ImageTk = None
    Image = None

class CurrentTrackView(tk.Frame):
    """ The view displaying the current track. """
    
    def __init__(self, parent, settings):
        """ Constructor """
        tk.Frame.__init__(self, parent)

        self.columnconfigure(1, weight = 1)

        self.__images = AlbumImageProvider(settings)

        self.empty_info = '-'
        self.__parent = parent
        self._labels = {}
        self.__image = None
        infoIndex = 0

        labelGridSettings = {
            'column' : 1,
            'padx' : 5,
            'pady' : 5,
            'sticky' : 'we'
        }

        ###################################
        # Title
        ###################################
        label = tk.Label(self, text = 'Title:')
        label.grid(row = infoIndex, column = 0, sticky = 'w')
        
        self._labels[kn.title] = tk.Label(self, anchor = 'w')
        self._labels[kn.title].grid(labelGridSettings, row = infoIndex)
        infoIndex += 1

        ###################################
        # Artist
        ###################################
        label = tk.Label(self, text = 'Artist:')
        label.grid(row = infoIndex, column = 0, sticky = 'w')
        
        self._labels[kn.artist] = tk.Label(self, anchor = 'w')
        self._labels[kn.artist].grid(labelGridSettings, row = infoIndex)
        infoIndex += 1

        ###################################
        # Album
        ###################################
        label = tk.Label(self, text = 'Album:')
        label.grid(row = infoIndex, column = 0, sticky = 'w')
        
        self._labels[kn.album] = tk.Label(self, anchor = 'w')
        self._labels[kn.album].grid(labelGridSettings, row = infoIndex)
        infoIndex += 1

        ###################################
        # Album art
        ###################################
        self._album_art = tk.Label(self,
                                   image = tk.PhotoImage(),
                                   width = 150,
                                   height = 150)
        
        self._album_art.grid(row = infoIndex,
                             column = 0,
                             columnspan = 2,
                             padx = 5,
                             pady = 5)
        infoIndex += 1

        ###################################
        # Position
        ###################################
        label = tk.Label(self, text = 'Position:')
        label.grid(row = infoIndex,
                   column = 0,
                   sticky = 'w')
        
        self._labels[kn.position] = Meter(self, fillcolor='darkgray', bg='lightgray', relief="sunken", bd=1, height=14, text="")
        self._labels[kn.position].grid(labelGridSettings, row = infoIndex)
 
    def clearImage(self):
        """ Clear the displayed image. """
        self.__showAlbumArt(None)
        
    def attachViewModel(self, viewModel):
        """ Attach the event listener to the view model. """
        self.__viewModel = viewModel
        self.__viewModel.addListener(self.__onPropertyChanged)
    
    def detachViewModel(self):
        """ REmove the event listener from the view model. """
        if self.__viewModel:
            self.__viewModel.removeListener(self.__onPropertyChanged)
            self.__viewModel = None
        for label in self.__labels:
            label.configure(text = self.empty_info)
        self.clearImage()

    def __onPropertyChanged(self, propertyName, viewModel):
        """ Update the view after changes in the view model. """
        if propertyName == kn.position:
            if viewModel[kn.duration] and viewModel[kn.position]:
                showHours = viewModel[kn.duration].seconds > 3600
                position = "%s / %s" % (self.__formatDuration(viewModel[kn.position], showHours),
                                        self.__formatDuration(viewModel[kn.duration], showHours))
                progress = viewModel[kn.position].total_seconds() / viewModel[kn.duration].total_seconds()
                self._labels[propertyName].set(value=progress, text=position)
            else:
                self._labels[propertyName].set(value=0, text="")
        elif propertyName in self._labels:
            value = viewModel[propertyName]
            self._labels[propertyName].configure(text=value)
        elif propertyName == kn.album_art:
            image = self.__images.getImage(viewModel[kn.uri], viewModel[kn.album_art])
            self.__showAlbumArt(image)
    
    def __formatDuration(self, time, showHours):
        """ Format a duration or position.
            If showHours is True the format is 'H:MM:SS', otherwise 'M:SS'. """
        hours, remainder = divmod(time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60) 
        if showHours:
            return "%d:%02d:%02d" % (hours, minutes, seconds)
        return "%d:%02d" % (minutes, seconds)

    def __showAlbumArt(self, image):
        """ SHow the specified imagee as album art. """
        if image is None:
            self._album_art.config(image = None)
            self.__image = None
            return

        widgetConfig = self._album_art.config()
        thumbSize = (int(widgetConfig['width'][4]),
                     int(widgetConfig['height'][4]))

        logging.debug('Resizing album art to: %s', thumbSize)
        image.thumbnail(thumbSize, Image.ANTIALIAS)
        self.__image = ImageTk.PhotoImage(image = image)
        self._album_art.configure(image = self.__image)
