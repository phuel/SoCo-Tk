import logging, traceback
import os
import sqlite3 as sql
import contextlib as clib

class AppSettings(object):
    """ Wrapper class for the application setting database. """
    
    def __init__(self, path):
        """ Constructor
            Creates the database in the specified path if not already existing. """
        self.__dbPath = os.path.join(path, 'SoCo-Tk.sqlite')
        self._connection = None

        createStructure = False
        if not os.path.exists(self.__dbPath):
            logging.info('Database "%s" not found, creating', self.__dbPath)
            createStructure = True

            directory = os.path.dirname(self.__dbPath)
            if not os.path.exists(directory):
                logging.info('Creating directory structure')
                os.makedirs(directory)

        logging.info('Connecting: %s', self.__dbPath)
        self._connection = sql.connect(self.__dbPath)
        self._connection.row_factory = sql.Row

        if createStructure:
            self._createSettingsDB()

    def setConfig(self, settingName, value):
        """ Store a configuration value. """
        assert settingName is not None

        __sql = 'INSERT OR REPLACE INTO config (name, value) VALUES (?, ?)'

        self._connection.execute(__sql, (settingName, value)).close()
        self._connection.commit()
        
    def getConfig(self, settingName):
        """ Get a settings value from the database. """
        assert settingName is not None

        __sql = 'SELECT value FROM config WHERE name = ? LIMIT 1'

        with clib.closing(self._connection.execute(__sql, (settingName, ))) as cur:
            row = cur.fetchone()

            if not row:
                return None
            
            return row['value']

    def close(self):
        """ Close the database. """
        if self._connection:
            logging.info('Closing database connection')
            self._connection.close()
            self._connection = None

    def tryGetImage(self, track_uri):
        """ Try to get an album art image from the database.
            track_uri : The track uri used as a key in the cache. """
        raw_data = None
        try:
            __sql = '''
                SELECT image FROM images AS i
                WHERE
                    i.uri = ?
                LIMIT 1
            '''
            with clib.closing(self._connection.execute(__sql, (track_uri,))) as cur:
                row = cur.fetchone()
                if row:
                    logging.debug('Found album art for uri: "%s"', track_uri)
                    raw_data = str(row['image'])
        except:
            logging.warning('Could not load album art from database')
            logging.error(traceback.format_exc())
        return raw_data

    def setImage(self, track_uri, raw_data):
        """ Store an image in the database
            track_uri : The track uri used as a key in the cache. 
            raw_data  : The image data. """
        try:
            __sql = '''
                INSERT OR REPLACE INTO images (
                    uri,
                    image
                ) VALUES (?, ?)
            '''
            logging.info('Storing album art for uri: "%s"', track_uri)
            self._connection.execute(__sql, (track_uri,
                                             buffer(raw_data))).close()

            self._connection.commit()
        except:
            logging.error('Could not store album art')
            logging.error(traceback.format_exc())
    
    def _createSettingsDB(self):
        """ Create the settings database. """
        logging.debug('Creating tables')
        self._connection.executescript('''
            CREATE TABLE IF NOT EXISTS config(
                config_id   INTEGER,
                name        TEXT UNIQUE,
                value       TEXT,
                PRIMARY KEY(config_id)
            );
                
            CREATE TABLE IF NOT EXISTS images(
                image_id        INTEGER,
                uri             TEXT UNIQUE,
                image           BLOB,
                PRIMARY KEY(image_id)
            );
        ''').close()

        logging.debug('Creating index')
        self._connection.execute('''
            CREATE INDEX IF NOT EXISTS idx_image_uri ON images(uri)
        ''').close()

        self._connection.execute('''
            CREATE INDEX IF NOT EXISTS idx_config_name ON config(name)
        ''').close()
