import urllib
import StringIO as sio
import logging, traceback

try:
    from PIL import Image, ImageTk
except:
    logging.error('Could not import PIL')
    logging.error(traceback.format_exc())
    ImageTk = None
    Image = None

class AlbumImageProvider(object):
    """ The class loading album art from a URI or from the cache. """
    
    def __init__(self, cache):
        """ Constructor """
        self.__cache = cache

    def getImage(self, trackUri, imageUri):
        """ Get an album art image.
            trackUri : The track URI used as a key in the cache.
            imageUri : The image URI. """
        if Image is None:
            return None

        try:
            raw_data = None
            connectiom = None
            
            # Check for cached albumart
            if trackUri:
                raw_data = self.__cache.tryGetImage(trackUri)

            if raw_data is None:
                if not imageUri:
                    return None
                logging.info('Could not find cached album art, loading from URL')
                connection = urllib.urlopen(imageUri)
                raw_data = connection.read()

            self.__cache.setImage(trackUri, raw_data)

            image = Image.open(sio.StringIO(raw_data))
            return image
        except:
            logging.error('Could not set album art, skipping...')
            logging.error(imageUri)
            logging.error(traceback.format_exc())
        finally:
            if connectiom: connectiom.close()
