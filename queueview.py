import Tkinter as tk
import logging
from verticalscrolledframe import VerticalScrolledFrame
from queuetrackview import QueueTrackView
import keynames as kn

class QueueView(VerticalScrolledFrame):
    """ The view for the player queue. """

    def __init__(self, parent):
        """ Constructor. """
        VerticalScrolledFrame.__init__(self, parent)
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.__viewModel = None
        self.__speaker = None
        self.__tracks = []

    def attachViewModel(self, viewModel, speaker):
        """ Attach the view model and the Sonos player to this view. """
        self.__viewModel = viewModel
        self.__speaker = speaker
        self.__viewModel.addListener(self.__onPropertyChanged)
        self.__showQueue(self.__viewModel[kn.entries])

    def detachViewModel(self):
        """ Detach the view model from this view. """
        if self.__viewModel:
            self.__viewModel.removeListener(self.__onPropertyChanged)
        self.__viewModel = None
        self.__speaker = None

    def __onPropertyChanged(self, propertyName, viewModel):
        """ Updates the view after changes in the view model. """
        if propertyName == kn.entries:
            self.__showQueue(viewModel[propertyName])

    def __showQueue(self, queue):
        """ Show the queue content. """
        self.__clear()

        logging.debug('Inserting items (%d) to listbox', len(queue))
        for item in queue:
            trackView = QueueTrackView(self.interior, item)
            self.__tracks.append(trackView)

    def __clear(self):
        """ Clear the view. """
        logging.debug('Deleting old items')
        for track in self.__tracks:
            track.destroy()
