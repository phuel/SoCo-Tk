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
    def __init__(self, cache):
        self.__cache = cache

    def getImage(self, trackUri, imageUri):
        if Image is None:
            return None

        try:
            raw_data = None
            
            # Check for cached albumart
            if trackUri:
                raw_data = self.__cache.tryGetImage(trackUri)

            connectiom = None
            if raw_data is None:
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
