#

#  Merlin Music Player E2
#
#  $Id$
#
#  Coded by Dr.Best (c) 2010 - 2018
#  Support: www.dreambox-tools.info
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
#  Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.

#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.

#
# merlin mp3 player
# for localized messages
from . import _
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ConfigList import ConfigListScreen
from Components.FileList import FileList
from Components.GUIComponent import GUIComponent
from Components.Label import Label
from Components.MerlinMusicPlayerWidget import MerlinMusicPlayerWidget, MerlinMusicPlayerRMS
from Components.MerlinPictureViewerWidget import MerlinPictureViewer
from Components.Pixmap import Pixmap, MultiPixmap
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.ServicePosition import ServicePositionGauge
from Components.Sources.StaticText import StaticText
from Components.SystemInfo import SystemInfo
from Components.VideoWindow import VideoWindow
from Components.VolumeControl import VolumeControl
from Components.config import config, ConfigSubsection, ConfigDirectory, ConfigYesNo, ConfigInteger, ConfigText, getConfigListEntry, configfile, NoSave, ConfigLocations, ConfigSelection
from Plugins.Plugin import PluginDescriptor
from Screens.ChannelSelection import SimpleChannelSelection
from Screens.ChoiceBox import ChoiceBox
from Screens.EpgSelection import EPGSelection
from Screens.EventView import EventViewEPGSelect
from Screens.InfoBarGenerics import InfoBarSeek, InfoBarNotifications
from Screens.InfoBarGenerics import NumberZap
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.VirtualKeyBoard import VirtualKeyBoard
from ServiceReference import ServiceReference
from Tools import Notifications
from Tools.BoundFunction import boundFunction
from Tools.Directories import fileExists, resolveFilename, SCOPE_CURRENT_SKIN
from Tools.HardwareInfo import HardwareInfo
from Tools.LoadPixmap import LoadPixmap
from datetime import timedelta as datetime_timedelta
from enigma import RT_VALIGN_CENTER, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, gFont, eListbox, ePoint, eListboxPythonMultiContent
from enigma import eEnv
from enigma import ePicLoad
from enigma import ePoint, eEPGCache
from enigma import ePythonMessagePump
from enigma import eServiceCenter, getBestPlayableServiceReference
from enigma import eServiceReference, eTimer, eActionMap, eEnv, eDVBVolumecontrol
from enigma import getDesktop
from enigma import iPlayableService, iServiceInformation
from json import loads as json_loads
from keyids import KEYIDS
from mutagen.aiff import AIFF
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4
from mutagen.flac import FLAC
from mutagen.id3 import ID3, USLT
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from os import path as os_path, mkdir as os_mkdir, listdir as os_listdir, walk as os_walk, access as os_access, W_OK as os_W_OK
from random import randint
from random import shuffle, randrange
from skin import TemplatedListFonts, componentSizes
from sqlite3 import dbapi2 as sqlite
from threading import Thread, Lock
from time import localtime, time
from time import time
from timer import TimerEntry
from twisted.internet import reactor, defer
from twisted.web import client
from twisted.web.client import HTTPClientFactory, downloadPage
from twisted.web.client import getPage
from urllib import quote
from xml.etree.cElementTree import fromstring as cet_fromstring
from merlin_musicplayer.emerlinmusicplayer import eMerlinMusicPlayer, eMerlinMusicPlayerRecorder, eMerlinVideoPlayer
# from merlin_musicplayer import _emerlinmusicplayer
import merlin_musicplayer._emerlinmusicplayer
import urlparse

ENIGMA_MERLINPLAYER_ID = 0x1019
START_MERLIN_PLAYER_SCREEN_TIMER_VALUE = 60000

config.plugins.merlinmusicplayer2 = ConfigSubsection()
config.plugins.merlinmusicplayer2.hardwaredecoder = ConfigYesNo(default=False)
config.plugins.merlinmusicplayer2.startlastsonglist = ConfigYesNo(default=True)
config.plugins.merlinmusicplayer2.lastsonglistindex = ConfigInteger(-1)
config.plugins.merlinmusicplayer2.databasepath = ConfigDirectory(default="/media/hdd/")
config.plugins.merlinmusicplayer2.usegoogleimage = ConfigYesNo(default=True)
config.plugins.merlinmusicplayer2.googleimagepath = ConfigDirectory(default="/media/hdd/")
config.plugins.merlinmusicplayer2.usescreensaver = ConfigYesNo(default=True)
config.plugins.merlinmusicplayer2.screensaverwait = ConfigInteger(1, limits=(1, 60))
config.plugins.merlinmusicplayer2.screensaverselection = ConfigSelection(choices=[("0", _("Default")), ("1", _("Sinus")), ("2", _("Waves")), ("3", _("Eclipse")), ("4", _("Balls")), ("5", _("Dots")), ("6", _("Random"))], default="6")
config.plugins.merlinmusicplayer2.idreamextendedpluginlist = ConfigYesNo(default=True)
config.plugins.merlinmusicplayer2.merlinmusicplayerextendedpluginlist = ConfigYesNo(default=True)
config.plugins.merlinmusicplayer2.defaultfilebrowserpath = ConfigDirectory(default="/media/hdd/")
config.plugins.merlinmusicplayer2.rememberlastfilebrowserpath = ConfigYesNo(default=True)
config.plugins.merlinmusicplayer2.idreammainmenu = ConfigYesNo(default=False)
config.plugins.merlinmusicplayer2.merlinmusicplayermainmenu = ConfigYesNo(default=False)
config.plugins.merlinmusicplayer2.dvbradiolastroot = ConfigText()
config.plugins.merlinmusicplayer2.dvbradiolastservice = ConfigText()
config.plugins.merlinmusicplayer2.usestandardradiobackground = ConfigYesNo(default=False)
config.plugins.merlinmusicplayer2.infobar_timeout = ConfigInteger(default=5, limits=(1, 99))
config.plugins.merlinmusicplayer2.gapless = ConfigYesNo(default=True)
config.plugins.merlinmusicplayer2.alsa = ConfigYesNo(default=True)
config.plugins.merlinmusicplayer2.last_movie_dir = ConfigDirectory(default="/media/hdd/")
config.plugins.merlinmusicplayer2.last_movie_filename = ConfigText()
config.plugins.merlinmusicplayer2.last_picture_dir = ConfigDirectory(default="")
config.plugins.merlinmusicplayer2.last_picture_filename = ConfigText()
config.plugins.merlinmusicplayer2.picture_duration = ConfigInteger(default=5, limits=(0, 999))
config.plugins.merlinmusicplayer2.kenburns = ConfigYesNo(default=True)
config.plugins.merlinmusicplayer2.picture_scale_to_screen = ConfigYesNo(default=False)
config.plugins.merlinmusicplayer2.transition_duration = ConfigInteger(default=1000, limits=(0, 5000))
config.plugins.merlinmusicplayer2.transition_default_duration = ConfigYesNo(default=True)
config.plugins.merlinmusicplayer2.transition_mode = ConfigSelection(
        [("0", _("Slice")), ("1", _("Swap")), ("2", _("Water drop")), ("3", _("Doorway")), ("4", _("Cube")), ("5", _("Squares")),
        ("6", _("Circle")), ("7", _("Ripple")), ("8", _("Angular")), ("9", _("Dreamy")), ("10", _("Fade")), ("11", _("Random"))], default="11")
config.plugins.merlinmusicplayer2.infobar_timeout_tv = ConfigYesNo(default=True)
config.plugins.merlinmusicplayer2.infobar_timeout_video = ConfigYesNo(default=True)
config.plugins.merlinmusicplayer2.infobar_timeout_picture = ConfigYesNo(default=True)

config.plugins.merlinmusicplayerrecorder = ConfigSubsection()
config.plugins.merlinmusicplayerrecorder.locations = ConfigLocations(default=["/hdd/musicrecorder"])
config.plugins.merlinmusicplayerrecorder.split_files = ConfigYesNo(default=True)
config.plugins.merlinmusicplayerrecorder.duration = ConfigInteger(default=120, limits=(10, 999))
config.plugins.merlinmusicplayerrecorder.lastLocation = ConfigText(default="/hdd/musicrecorder")


def isValidAudio(filename):
    return filename.lower().endswith((".mp3", ".flac", ".m4a", ".ogg", ".aif", ".aiff", ".wav", ".wma", ".au", ".mpc"))

def isValidPicture(filename):
    return filename.lower().endswith((".jpg", ".png", ".bmp", ".gif"))

def url_parse(url, defaultPort=None):
    parsed = urlparse.urlparse(url)
    scheme = parsed[0]
    path = urlparse.urlunparse(('', '') + parsed[2:])
    if defaultPort is None:
        if scheme == 'https':
            defaultPort = 443
        else:
            defaultPort = 80
    host, port = parsed[1], defaultPort
    if ':' in host:
        host, port = host.split(':')
        port = int(port)
    return scheme, host, port, path


class ThreadQueue:
    def __init__(self):
        self.__list = []
        self.__lock = Lock()

    def push(self, val):
        lock = self.__lock
        lock.acquire()
        self.__list.append(val)
        lock.release()

    def pop(self):
        lock = self.__lock
        lock.acquire()
        ret = self.__list.pop()
        lock.release()
        return ret


displayname = None
THREAD_WORKING = 1
THREAD_FINISHED = 2


class MerlinMusicPlayerBase:
    def __init__(self):
        self.skinName = []
        if HardwareInfo().get_device_name() in ("one", "two"):
            self.skinName.append("%s_AARCH64" % self.__class__.__name__)
        elif HardwareInfo().get_device_name() not in ("dm900", "dm920"):
            self.skinName.append("%s_MIPSEL" % self.__class__.__name__)
        else:
            self.skinName.append("%s_ARM" % self.__class__.__name__)
        self.skinName.append(self.__class__.__name__)


class PathToDatabase(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.__running = False
        self.__cancel = False
        self.__path = None
        self.__messages = ThreadQueue()
        self.__messagePump = ePythonMessagePump()

    def __getMessagePump(self):
        return self.__messagePump

    def __getMessageQueue(self):
        return self.__messages

    def __getRunning(self):
        return self.__running

    def Cancel(self):
        self.__cancel = True

    MessagePump = property(__getMessagePump)
    Message = property(__getMessageQueue)
    isRunning = property(__getRunning)

    def Start(self, path):
        if not self.__running:
            self.__path = path
            self.start()

    def run(self):
        mp = self.__messagePump
        self.__running = True
        self.__cancel = False
        if self.__path:
            connection = OpenDatabase()
            if connection is not None:
                connection.text_factory = str
                cursor = connection.cursor()
                counter = 0
                checkTime = 0
                for root, subFolders, files in os_walk(self.__path):
                    if self.__cancel:
                        break
                    for filename in files:
                        if self.__cancel:
                            break
                        cursor.execute('SELECT song_id FROM Songs WHERE filename = "%s";' % os_path.join(root, filename))
                        row = cursor.fetchone()
                        if row is None:
                            audio, isAudio, title, genre, artist, album, tracknr, track, date, length, bitrate = getID3Tags(root, filename)
                            if audio:
                                # 1. Artist
                                artistID = -1
                                cursor.execute('SELECT artist_id FROM Artists WHERE artist = "%s";' % (artist.replace('"', '""')))

                                row = cursor.fetchone()
                                if row is None:
                                    cursor.execute('INSERT INTO Artists (artist) VALUES("%s");' % (artist.replace('"', '""')))
                                    artistID = cursor.lastrowid
                                else:
                                    artistID = row[0]
                                # 2. Album
                                albumID = -1
                                cursor.execute('SELECT album_id FROM Album WHERE album_text="%s";' % (album.replace('"', '""')))
                                row = cursor.fetchone()
                                if row is None:
                                    cursor.execute('INSERT INTO Album (album_text) VALUES("%s");' % (album.replace('"', '""')))
                                    albumID = cursor.lastrowid
                                else:
                                    albumID = row[0]

                                # 3. Genre
                                genreID = -1
                                cursor.execute('SELECT genre_id FROM Genre WHERE genre_text="%s";' % (genre.replace('"', '""')))
                                row = cursor.fetchone()
                                if row is None:
                                    cursor.execute('INSERT INTO Genre (genre_text) VALUES("%s");' % (genre.replace('"', '""')))
                                    genreID = cursor.lastrowid
                                else:
                                    genreID = row[0]

                                # 4. Songs
                                try:
                                    cursor.execute("INSERT INTO Songs (filename,title,artist_id,album_id,genre_id,tracknumber, bitrate, length, track, date) VALUES(?,?,?,?,?,?,?,?,?,?);", (os_path.join(root, filename), title, artistID, albumID, genreID, tracknr, bitrate, length, track, date))
                                    self.__messages.push((THREAD_WORKING, _("%s\n added to database") % os_path.join(root, filename)))
                                    mp.send(0)
                                    counter += 1
                                except sqlite.IntegrityError:
                                    self.__messages.push((THREAD_WORKING, _("%s\n already exists in database!") % os_path.join(root, filename)))
                                    mp.send(0)
                                audio = None
                        elif time() - checkTime >= 0.1:  # update interval for gui
                            self.__messages.push((THREAD_WORKING, _("%s\n already exists in database!") % os_path.join(root, filename)))
                            mp.send(0)
                            checkTime = time()

                if not self.__cancel:
                    connection.commit()
                cursor.close()
                connection.close()
                if self.__cancel:
                    self.__messages.push((THREAD_FINISHED, _("Process aborted.\n 0 files added to database!\nPress OK to close.")))
                else:
                    self.__messages.push((THREAD_FINISHED, _("%d files added to database!\nPress OK to close." % counter)))
            else:
                self.__messages.push((THREAD_FINISHED, _("Error!\nCan not open database!\nCheck if save folder is correct and writeable!\nPress OK to close.")))
            mp.send(0)
            self.__running = False
            Thread.__init__(self)


pathToDatabase = PathToDatabase()


class myHTTPClientFactory(HTTPClientFactory):
    def __init__(self, url, method='GET', postdata=None, headers=None,
                 agent="SHOUTcast", timeout=0, cookies=None,
                 followRedirect=1, lastModified=None, etag=None):
        HTTPClientFactory.__init__(self, url, method=method, postdata=postdata,
                                   headers=headers, agent=agent, timeout=timeout, cookies=cookies, followRedirect=followRedirect)


def sendUrlCommand(url, contextFactory=None, timeout=60, *args, **kwargs):
    scheme, host, port, path = url_parse(url)
    factory = myHTTPClientFactory(url, *args, **kwargs)
    reactor.connectTCP(host, port, factory, timeout=timeout)
    return factory.deferred


class MethodArguments:
    def __init__(self, method=None, arguments=None):
        self.method = method
        self.arguments = arguments


class CacheList:
    def __init__(self, cache=True, index=0, listview=[], headertext="", methodarguments=None):
        self.cache = cache
        self.index = index
        self.listview = listview
        self.headertext = headertext
        self.methodarguments = methodarguments


class Item:
    def __init__(self, text="", mode=0, id=-1, navigator=False, artistID=0, albumID=0, title="", artist="", filename="", bitrate=None, length="", genre="", track="", date="", album="", playlistID=0, genreID=0, songID=0, join=True, PTS=None, isDVB=False):
        self.text = text
        self.mode = mode
        self.navigator = navigator
        self.artistID = artistID
        self.albumID = albumID
        self.title = title
        self.artist = artist
        self.filename = filename
        self.isDVB = isDVB
        if bitrate is not None:
            if join:
                self.bitrate = "%d Kbps" % bitrate
            else:
                self.bitrate = bitrate
        else:
            self.bitrate = ""
        self.length = repr(length)[2:-1]
        self.genre = genre
        if track is not None:
            self.track = "Track %s" % track
        else:
            self.track = ""
        if date is not None:
            if join:
                self.date = " (%s)" % date
            else:
                self.date = date
        else:
            self.date = ""
        self.album = album
        self.playlistID = playlistID
        self.genreID = genreID
        self.songID = songID
        self.PTS = PTS


def OpenDatabase():
    connectstring = os_path.join(config.plugins.merlinmusicplayer2.databasepath.value, "iDream.db")
    db_exists = False
    if os_path.exists(connectstring):
        db_exists = True
    try:
        connection = sqlite.connect(connectstring)
        if not os_access(connectstring, os_W_OK):
            print("[MerlinMusicPlayer] Error: database file needs to be writable, can not open %s for writing..." % connectstring)
            connection.close()
            return None
    except:
        print("[MerlinMusicPlayer] unable to open database file: %s" % connectstring)
        return None
    if not db_exists:
        connection.execute('CREATE TABLE IF NOT EXISTS Songs (song_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL UNIQUE, title TEXT, artist_id INTEGER, album_id INTEGER, genre_id INTEGER, tracknumber INTEGER, bitrate INTEGER, length TEXT, track TEXT, date TEXT, lyrics TEXT);')
        connection.execute('CREATE TABLE IF NOT EXISTS Artists (artist_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, artist TEXT NOT NULL UNIQUE);')
        connection.execute('CREATE TABLE IF NOT EXISTS Album (album_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, album_text TEXT NOT NULL UNIQUE);')
        connection.execute('CREATE TABLE IF NOT EXISTS Genre (genre_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, genre_text TEXT NOT NULL UNIQUE);')
        connection.execute('CREATE TABLE IF NOT EXISTS Playlists (playlist_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, playlist_text TEXT NOT NULL);')
        connection.execute('CREATE TABLE IF NOT EXISTS Playlist_Songs (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, playlist_id INTEGER NOT NULL, song_id INTEGER NOT NULL);')
        connection.execute('CREATE TABLE IF NOT EXISTS CurrentSongList (ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, song_id INTEGER, filename TEXT NOT NULL, title TEXT, artist TEXT, album TEXT, genre TEXT, bitrate TEXT, length TEXT, track TEXT, date TEXT, PTS INTEGER);')
    return connection


def getEncodedString(value):
    returnValue = ""
    try:
        returnValue = value.encode("utf-8", 'ignore')
    except UnicodeDecodeError:
        try:
            returnValue = value.encode("iso8859-1", 'ignore')
        except UnicodeDecodeError:
            try:
                returnValue = value.decode("cp1252").encode("utf-8")
            except UnicodeDecodeError:
                returnValue = "n/a"
    return returnValue


def getID3Tags(root, filename):
    audio = None
    isFlac = False
    isAudio = True
    title = ""
    genre = ""
    artist = ""
    album = ""
    tracknr = -1
    track = None
    date = None
    length = ""
    bitrate = None
    if filename.lower().endswith(".mp3"):
        try:
            audio = MP3(os_path.join(root, filename), ID3=EasyID3)
        except:
            audio = None
    elif filename.lower().endswith(".flac"):
        try:
            audio = FLAC(os_path.join(root, filename))
            isFlac = True
        except:
            audio = None
    elif filename.lower().endswith(".m4a"):
        try:
            audio = EasyMP4(os_path.join(root, filename))
        except:
            audio = None
    elif filename.lower().endswith(".ogg"):
        try:
            audio = OggVorbis(os_path.join(root, filename))
        except:
            audio = None
    elif filename.lower().endswith(".aif") or filename.lower().endswith(".aiff"):
        try:
            audio = AIFF(os_path.join(root, filename))
        except:
            audio = None
    else:
        isAudio = False
    if audio:
        title = getEncodedString(audio.get('title', [filename])[0])
        try:
            # list index out of range workaround
            genre = getEncodedString(audio.get('genre', ['n/a'])[0])
        except:
            genre = "n/a"
        artist = getEncodedString(audio.get('artist', ['n/a'])[0])
        album = getEncodedString(audio.get('album', ['n/a'])[0])
        try:
            tracknr = int(audio.get('tracknumber', ['-1'])[0].split("/")[0])
        except:
            tracknr = -1
        track = getEncodedString(audio.get('tracknumber', ['n/a'])[0])
        date = getEncodedString(audio.get('date', ['n/a'])[0])
        try:
            length = str(datetime_timedelta(seconds=int(audio.info.length))).encode("utf-8", 'ignore')
            length = repr(length)[2:-1]
        except:
            length = -1
        if not isFlac:
            bitrate = audio.info.bitrate / 1000
        else:
            bitrate = None
    else:
        if isAudio:
            title = os_path.splitext(os_path.basename(filename))[0]
            genre = "n/a"
            artist = "n/a"
            album = "n/a"
            tracknr = -1
            track = None
            date = None
            length = ""
            bitrate = None

    return audio, isAudio, title, genre, artist, album, tracknr, track, date, length, bitrate


class MerlinMusicPlayer2ScreenSaver(MerlinMusicPlayerBase, Screen):

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        if HardwareInfo().get_device_name() in ("dm900", "dm920", "one", "two"):
            if config.plugins.merlinmusicplayer2.screensaverselection.value != "0":
                self.skinName.insert(0, "%s_%s" % (self.__class__.__name__, config.plugins.merlinmusicplayer2.screensaverselection.value))

        self["display"] = Label()
        self.onClose.append(self.__onClose)
        self.session.nav.SleepTimer.on_state_change.append(self.sleepTimerEntryOnStateChange)
        self["cover"] = MerlinMusicPlayerWidget()
        self["visu"] = MerlinMusicPlayerWidget()
        self["visu2"] = MerlinMusicPlayerWidget()
        self["rms0"] = MerlinMusicPlayerRMS()
        self["rms1"] = MerlinMusicPlayerRMS()
        self["rms2"] = MerlinMusicPlayerRMS()
        self["rms3"] = MerlinMusicPlayerRMS()
        self["rms4"] = MerlinMusicPlayerRMS()

        self.autoActivationKeyPressedActionSlot = eActionMap.getInstance().bindAction('', -0x7FFFFFFF, self.autoActivationKeyPressed)

    def sleepTimerEntryOnStateChange(self, timer):
        if timer.state == TimerEntry.StateEnded:
            self.close()

    def autoActivationKeyPressed(self, key=None, flag=None):
        if key in (KEYIDS["KEY_VOLUMEDOWN"], KEYIDS["KEY_VOLUMEUP"]):
            return 0
        elif key == KEYIDS["KEY_STOP"]:
            if not flag and not self["cover"].visGLRandomPause():
                self.close()
            return 1
        elif key == KEYIDS["KEY_PLAY"]:
            if not flag and not self["cover"].visGLRandomStart():
                self.close()
            return 1
        elif key == KEYIDS["KEY_NEXTSONG"]:
            if not flag and not self["cover"].visGLRandomNext():
                self.close()
            return 1
        else:
            self.close()
            return 1

    def __onClose(self):
        self.session.nav.SleepTimer.on_state_change.remove(self.sleepTimerEntryOnStateChange)
        self.autoActivationKeyPressedActionSlot = None

    def updateDisplayText(self, text):
        self["display"].setText(text)

    def updateLCD(self, text, line):
        self.summaries.setText(text, line)

    def updateCover(self, filename=""):
        self["cover"].setCover(filename)
        self.summaries.updateCover(filename)

    def createSummary(self):
        return MerlinMusicPlayer2LCDScreen


class MerlinMusicPlayer2DVBRadioSelection(MerlinMusicPlayerBase, SimpleChannelSelection):

    IS_DIALOG = True

    def __init__(self, session, title):
        SimpleChannelSelection.__init__(self, session, title)
        MerlinMusicPlayerBase.__init__(self)
        self.skinName.append("SimpleChannelSelection")

        self["actions"] = ActionMap(["OkCancelActions", "TvRadioActions"],
        {
            "cancel": self.close,
            "ok": self.channelSelected,
            "keyRadio": self.setModeRadio,
        })

    def channelSelected(self):
        ref = self.getCurrentSelection()
        if (ref.flags & 7) == 7:
            self.enterPath(ref)
        elif not (ref.flags & eServiceReference.isMarker):
            ref = self.getCurrentSelection()
            serviceHandler = eServiceCenter.getInstance()
            services = []
            servicelist = eServiceCenter.getInstance().list(self.getRoot())
            currentIndex = 0
            index = 0
            if servicelist is not None:
                while True:
                    service = servicelist.getNext()
                    if not service.valid():
                        break
                    if service.flags & (eServiceReference.isDirectory | eServiceReference.isMarker):
                        continue

                    info = serviceHandler.info(service)
                    name = info and info.getName(service) or "."
                    services.append((service, name))
                    if ref == service:
                        currentIndex = index
                    index += 1
            config.plugins.merlinmusicplayer2.dvbradiolastservice.value = ref.toString()
            config.plugins.merlinmusicplayer2.dvbradiolastservice.save()
            path = ''
            for i in self.servicePath:
                path += i.toString()
                path += ';'
            if path:
                config.plugins.merlinmusicplayer2.dvbradiolastroot.value = path
                config.plugins.merlinmusicplayer2.dvbradiolastroot.save()
            self.close(ref, services, currentIndex)

    def layoutFinished(self):
        self.setRadioMode()
        tmp = [x for x in config.plugins.merlinmusicplayer2.dvbradiolastroot.value.split(';') if x != '']
        self.clearPath()
        cnt = 0
        for i in tmp:
            self.servicePathRadio.append(eServiceReference(i))
            cnt += 1
        if cnt:
            path = self.servicePathRadio.pop()
            self.enterPath(path)
        else:
            self.showFavourites()
        if config.plugins.merlinmusicplayer2.dvbradiolastservice.value:
            lastservice = eServiceReference(config.plugins.merlinmusicplayer2.dvbradiolastservice.value)
            self.setCurrentSelection(lastservice)


class MerlinRecorderLocationScreen(MerlinMusicPlayerBase, LocationBox):

    IS_DIALOG = True

    def __init__(self, session, text, dir, minFree=None):
        inhibitDirs = ["/bin", "/boot", "/dev", "/etc", "/lib", "/proc", "/sbin", "/sys", "/usr", "/var"]
        LocationBox.__init__(self, session, text=text, currDir=dir, bookmarks=config.plugins.merlinmusicplayerrecorder.locations, autoAdd=True, editDir=True, inhibitDirs=inhibitDirs, minFree=minFree)
        MerlinMusicPlayerBase.__init__(self)
        self.skinName.append("LocationBox")


class MerlinRecorderScreen(MerlinMusicPlayerBase, ConfigListScreen, Screen):

    IS_DIALOG = True

    def __init__(self, session, url="", record_path="", playlist_filename="", filename="", split_files=True, duration=3600, name=""):
        self.session = session
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("OK"))
        self.list = []
        self.url = url

        default = record_path
        tmp = config.plugins.merlinmusicplayerrecorder.locations.value
        if default not in tmp:
            tmp.append(default)
        config.plugins.merlinmusicplayerrecorder.split_files.value = split_files
        config.plugins.merlinmusicplayerrecorder.duration.value = duration
        self.record_path = ConfigSelection(default=default, choices=tmp)
        self.playlist_filename = NoSave(ConfigText(default=playlist_filename))
        self.filename = NoSave(ConfigText(default=filename))
        self.name = NoSave(ConfigText(default=name))
        self.list.append(getConfigListEntry(_("name"), self.name))
        self.record_config = getConfigListEntry(_("record path"), self.record_path)
        self.list.append(self.record_config)
        self.list.append(getConfigListEntry(_("playlist filename"), self.playlist_filename))
        self.list.append(getConfigListEntry(_("filename"), self.filename))
        self.list.append(getConfigListEntry(_("split files"), config.plugins.merlinmusicplayerrecorder.split_files))
        self.list.append(getConfigListEntry(_("record duration"), config.plugins.merlinmusicplayerrecorder.duration))
        ConfigListScreen.__init__(self, self.list, session)
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
        {
            "green": self.keySave,
            "cancel": self.keyClose,
            "ok": self.keySelect,
        }, -2)

    def keySave(self):
        for x in self["config"].list:
            x[1].save()
        config.plugins.merlinmusicplayerrecorder.lastLocation.value = self.record_path.value
        config.plugins.merlinmusicplayerrecorder.lastLocation.save()
        config.plugins.merlinmusicplayerrecorder.save()
        self.close(True, self.url,  self.record_path.value, self.playlist_filename.value,  self.filename.value,  config.plugins.merlinmusicplayerrecorder.split_files.value, config.plugins.merlinmusicplayerrecorder.duration.value, self.name.value)

    def keyClose(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close(False, None, None, None, None, None, None, None)

    def keySelect(self):
        cur = self["config"].getCurrent()
        if cur == self.record_config:
            self.chooseDestination()

    def pathSelected(self, res):
        if res is not None:
            if config.plugins.merlinmusicplayerrecorder.locations.value != self.record_path.choices:
                self.record_path.setChoices(config.plugins.merlinmusicplayerrecorder.locations.value, default=res)
            self.record_path.value = res

    def chooseDestination(self):
        self.session.openWithCallback(
            self.pathSelected,
            MerlinRecorderLocationScreen,
            _("Choose target folder"),
            self.record_path.value,
            minFree = 100  # Same requirement as in Screens.TimerEntry
        )


class MerlinRecorder(object):
    instance = None

    def __init__(self):
        assert not MerlinRecorder.instance, "only one MerlinRecorder instance is allowed!"
        MerlinRecorder.instance = self  # set instance
        self.merlinMusicPlayerRecorder = eMerlinMusicPlayerRecorder()
        self.merlinMusicPlayerRecorder_conn = self.merlinMusicPlayerRecorder.m_event.connect(self.gotMerlinMusicPlayerRecorderEvent)
        Notifications.notificationQueue.registerDomain("MerlinRecorder", _("merlin recorder"), Notifications.ICON_TIMER)
        self.stopPlugin = None

    def showRecordingScreen(self, url, record_path, playlist_filename, filename, split_files, duration, name):
        Notifications.AddNotificationWithCallback(
                self.showRecordingScreenCallback,
                MerlinRecorderScreen,
                url=url,
                record_path=record_path,
                playlist_filename=playlist_filename,
                filename=filename,
                split_files=split_files,
                duration=duration,
                name=name)

    def showRecordingScreenCallback(self, result, url, record_path, playlist_filename, filename, split_files, duration, name):
        if result:
            self.merlinMusicPlayerRecorder.start(url, record_path, playlist_filename, filename, split_files, duration, name)

    def startRecording(self, url, record_path, playlist_filename, filename, split_files, duration, name):
        if not self.merlinMusicPlayerRecorder.isRecording():
            self.showRecordingScreen(url, record_path, playlist_filename, filename, split_files, duration, name)
        else:
            choicelist = ((_("stop recording"), "stop"), (_("start new recording"), "start"), (_("do nothing"), "no"))

            Notifications.AddNotificationWithCallback(
                boundFunction(self.startRecordingCallback, url, record_path, playlist_filename, filename, split_files, duration, name),
                ChoiceBox,
                list=choicelist,
                title=_("There is already a recording in progress..."),
                titlebartext=_("Select an action"))

    def startRecordingCallback(self, url, record_path, playlist_filename, filename, split_files, duration, name, answer):
        if answer is None:
            return
        if answer[1] == "stop":
            self.merlinMusicPlayerRecorder.stop()
        elif answer[1] == "start":
            self.showRecordingScreen(url, record_path, playlist_filename, filename, split_files, duration, name)

    def gotMerlinMusicPlayerRecorderEvent(self, event):
        from Components.PluginComponent import plugins
        print("[gotMerlinMusicPlayerRecorderEvent] event = ", event)
        text = ""
        mtype = MessageBox.TYPE_INFO
        if event == eMerlinMusicPlayerRecorder.evRecordRunning:
            text = _("MerlinRecorder: Recording started....")
            if self.stopPlugin is None:
                for p in plugins.getPlugins(where=-10000):
                    plugins.removePlugin(p)
                    self.stopPlugin = p
                    self.stopPlugin.needsRestart = False
                    self.stopPlugin.weight = 0
                    self.stopPlugin.where = [PluginDescriptor.WHERE_EXTENSIONSMENU]
                    plugins.addPlugin(self.stopPlugin)
                    break
            else:
                plugins.addPlugin(self.stopPlugin)

        elif event == eMerlinMusicPlayerRecorder.evRecordStopped:
            text = _("MerlinRecorder: Recording stopped....")
            if self.stopPlugin:
                plugins.removePlugin(self.stopPlugin)

        elif event == eMerlinMusicPlayerRecorder.evRecordFailed:
            text = _("MerlinRecorder: Recording failed....")
            if self.stopPlugin:
                plugins.removePlugin(self.stopPlugin)
            mtype = MessageBox.TYPE_ERROR
        if text != "":
            Notifications.AddPopup(text=text, type=mtype, timeout=20, domain="MerlinRecorder")


class MerlinMusicPlayer2MovieFileList(MerlinMusicPlayerBase, Screen):

    def __init__(self, session, lastdir, matchingPattern, useRef, selectItem, itemEntry):
        self.session = session
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        self["list"] = FileList(lastdir, showDirectories=True, showFiles=True, matchingPattern=matchingPattern, useServiceRef=useRef)
        self.itemEntry = itemEntry
        self.useRef = useRef
        self["actions"] = ActionMap(["WizardActions", "DirectionActions"],
        {
            "ok": self.ok,
            "back": self.closing,
            "up": self.moveup,
            "down": self.movedown,
            "right": self.moveright,
            "left": self.moveleft,
        }, -1)
        self["headertext"] = Label()
        self.onShown.append(self.updateTarget)
        if selectItem and itemEntry:
            if useRef:
                self.onFirstExecBegin.append(self.select_last_file)
            else:
                self.onFirstExecBegin.append(self.select_last_picture)

    def select_last_picture(self):
        self.select_file(self.itemEntry)

    def select_last_file(self):
        self.select_file(eServiceReference(self.itemEntry))

    def select_file(self, select):
        i = 0
        for x in self["list"].list:
            p = x[0][0]
            if isinstance(p, eServiceReference) or (not self.useRef and isinstance(p, str)):
                if p == select:
                    self["list"].moveToIndex(i)
                    break
            i += 1

    def closing(self):
        if self.useRef:
            self.close(None)
        else:
            self.close(None, None)

    def ok(self):
        if self["list"].canDescent():
            self["list"].descent()
            self.updateTarget()
        else:
            if self.useRef:
                config.plugins.merlinmusicplayer2.last_movie_dir.value = self["list"].getCurrentDirectory()
                config.plugins.merlinmusicplayer2.last_movie_dir.save()
                self.close(self["list"].getServiceRef())
            else:
                self.close(self["list"].getCurrentDirectory(), self["list"].getFilename())

    def updateTarget(self):
        currFolder = self["list"].getCurrentDirectory()
        if currFolder is None:
            currFolder = _("Invalid Location")
        self["headertext"].setText(_("Filelist: %s") % currFolder)

    def moveright(self):
        self["list"].pageDown()

    def moveleft(self):
        self["list"].pageUp()

    def moveup(self):
        self["list"].up()

    def movedown(self):
        self["list"].down()


class MerlinMusicPlayer2Video(MerlinMusicPlayer2ScreenSaver):

    def __init__(self, session, playNext, playPrevious):
        self.session = session
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        self.onClose.append(self.__onClose)
        self["actions"] = ActionMap(["OkCancelActions", "InfobarActions", "DirectionActions"],
        {
            "cancel": self.close,
            "ok": self.showHide,
            "showMovies": self.showMovies,
            "right": playNext,
            "left": playPrevious,

        }, -1)
        self["infobar"] = Label()

        self.videoPlayer = eMerlinVideoPlayer()
        VolumeControl.instance.volctrl = self.videoPlayer
        self.initialized = False
        self["title"] = Label()
        self["next_title"] = Label()
        self["video"] = VideoWindow(decoder=0, fb_width=getDesktop(0).size().width(), fb_height=getDesktop(0).size().height())
        self["cover"] = MerlinMusicPlayerWidget()
        self["visu"] = MerlinMusicPlayerWidget()
        self["visu2"] = MerlinMusicPlayerWidget()
        self["rms0"] = MerlinMusicPlayerRMS()
        self["rms1"] = MerlinMusicPlayerRMS()
        self["rms2"] = MerlinMusicPlayerRMS()
        self["rms3"] = MerlinMusicPlayerRMS()
        self["rms4"] = MerlinMusicPlayerRMS()

        self.showHideTimer = eTimer()
        self.showHideTimer_conn = self.showHideTimer.timeout.connect(self.showHideTimerTimeout)
        self.session.nav.SleepTimer.on_state_change.append(self.sleepTimerEntryOnStateChange)

        self.onFirstExecBegin.append(self.initialize)
        if config.plugins.merlinmusicplayer2.last_movie_filename.value:
            self.movie_selected(eServiceReference(config.plugins.merlinmusicplayer2.last_movie_filename.value))
        else:
            self.onFirstExecBegin.append(self.showMovies)

    def initialize(self):
        self.idx = config.plugins.merlinmusicplayer2.infobar_timeout.value
        if self.idx:
            self.showHideTimer.start(self.idx * 1000)
            self.displayShown = True
        else:
            self.displayShown = False
            self.hide()
        self.initialized = True

    def showMovies(self):
        self.session.openWithCallback(self.movie_selected, MerlinMusicPlayer2MovieFileList, config.plugins.merlinmusicplayer2.last_movie_dir.value,  ".([tT][sS]|[mM][kK][vV]|[mM][pP]4|[mM][pP][gG]|[mM][pP][eE][gG]|[mM]2[tT][sS]|[aA][vV][iI]|[dD][iI][vV][xX]|[mM][oO][vV]|[wW][mM][vV]|[mM]4[vV]|[fF][lL][vV])$", True, True, config.plugins.merlinmusicplayer2.last_movie_filename.value)

    def movie_selected(self, ref):
        if ref:
            self.videoPlayer.play(ref)
            config.plugins.merlinmusicplayer2.last_movie_filename.value = ref.toString()
            config.plugins.merlinmusicplayer2.last_movie_filename.save()

    def sleepTimerEntryOnStateChange(self, timer):
        if timer.state == TimerEntry.StateEnded:
            self.close()

    def showHide(self):
        if self.displayShown:
            if self.showHideTimer.isActive():
                self.showHideTimer.stop()
            self.hide()
        else:
            self.show()
            if self.idx:
                self.showHideTimer.start(self.idx * 1000)
        self.displayShown = not self.displayShown

    def showHideTimerTimeout(self):
        self.showHide()

    def updateDisplayText(self, text):
        self["title"].setText(text)
        if not self.initialized:
            return
        if config.plugins.merlinmusicplayer2.infobar_timeout_video.value:
            if self.showHideTimer.isActive():
                self.showHideTimer.stop()
            self.displayShown = False
            self.showHide()

    def updateLCD(self, text, line):
        if line == 4:
            self["next_title"].setText(text)
        self.summaries.setText(text, line)

    def __onClose(self):
        VolumeControl.instance.volctrl = eDVBVolumecontrol.getInstance()
        self.session.nav.SleepTimer.on_state_change.remove(self.sleepTimerEntryOnStateChange)
        self.videoPlayer = None
        if self.showHideTimer.isActive():
            self.showHideTimer.stop()
        if config.plugins.merlinmusicplayer2.usestandardradiobackground.value:
            eMerlinMusicPlayer.getInstance().show_iFrame_Pic(config.misc.radiopic.value)
        else:
            eMerlinMusicPlayer.getInstance().show_iFrame_Pic(eEnv.resolve("${libdir}/enigma2/python/Plugins/Extensions/MerlinMusicPlayer2/images/background"))


class MerlinMusicPlayer2PicturesInfobar(MerlinMusicPlayer2ScreenSaver):

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        self["infobar"] = Label()
        self["title"] = Label()
        self["next_title"] = Label()
        self["cover"] = MerlinMusicPlayerWidget()
        self["visu"] = MerlinMusicPlayerWidget()
        self["visu2"] = MerlinMusicPlayerWidget()
        self["rms0"] = MerlinMusicPlayerRMS()
        self["rms1"] = MerlinMusicPlayerRMS()
        self["rms2"] = MerlinMusicPlayerRMS()
        self["rms3"] = MerlinMusicPlayerRMS()
        self["rms4"] = MerlinMusicPlayerRMS()

    def updateDisplayText(self, text):
        self["title"].setText(text)

    def updateLCD(self, text, line):
        if line == 4:
            self["next_title"].setText(text)


class MerlinMusicPlayer2Pictures(MerlinMusicPlayer2ScreenSaver):

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        self.onClose.append(self.__onClose)
        self["actions"] = ActionMap(["OkCancelActions", "InfobarActions", "DirectionActions", "MediaPlayerActions", "MediaPlayerSeekActions"],
        {
            "cancel": self.close,
            "ok": self.showHide,
            "showMovies": self.showPictures,
            "right": boundFunction(self.skipImage, 1),
            "left": boundFunction(self.skipImage, -1),
            "pause": self.pause,
            "seekBack": boundFunction(self.skipImage, -1),
            "seekFwd": boundFunction(self.skipImage, 1),

        }, -1)
        self["image"] = MerlinPictureViewer()
        self.screenInfobar = None
        self.showHideTimer = eTimer()
        self.showHideTimer_conn = self.showHideTimer.timeout.connect(self.showHideTimerTimeout)
        self.session.nav.SleepTimer.on_state_change.append(self.sleepTimerEntryOnStateChange)
        self.onFirstExecBegin.append(self.initializeInfobar)
        if config.plugins.merlinmusicplayer2.last_picture_dir.value:
            self.onFirstExecBegin.append(self.startRun)
        else:
            self.onFirstExecBegin.append(self.showPictures)
        self.initialized = False

    def initializeInfobar(self):
        self.screenInfobar = self.session.instantiateDialog(MerlinMusicPlayer2PicturesInfobar)
        self.idx = config.plugins.merlinmusicplayer2.infobar_timeout.value
        if self.idx:
            self.screenInfobar.show()
            self.showHideTimer.start(self.idx * 1000)
            self.displayShown = True
        else:
            self.displayShown = False
        self.initialized = True

    def startRun(self):
        self.pictures_selected(config.plugins.merlinmusicplayer2.last_picture_dir.value, config.plugins.merlinmusicplayer2.last_picture_filename.value)

    def showPictures(self):
        self.session.openWithCallback(self.pictures_selected, MerlinMusicPlayer2MovieFileList, config.plugins.merlinmusicplayer2.last_picture_dir.value, "\.([pP][nN][gG]|[jJ][pP][eE]?[gG]|[gG][iI][fF]|[bB][mM][pP]]{1,2})$", False, True, os_path.basename(self["image"].getCurrentFilename()))

    def pictures_selected(self, dirname, current_filename):
        list = []
        start_index = 0
        if dirname:
            files = os_listdir(dirname)
            files.sort()
            for filename in files:
                if isValidPicture(filename):
                    list.append(os_path.join(dirname, filename))
                    if filename == current_filename:
                        start_index = len(list) -1
        if list:
            config.plugins.merlinmusicplayer2.last_picture_dir.value = dirname
            config.plugins.merlinmusicplayer2.last_picture_dir.save()
            self["image"].setTransitionMode(int(config.plugins.merlinmusicplayer2.transition_mode.value))
            self["image"].scaleToScreen(1 if config.plugins.merlinmusicplayer2.picture_scale_to_screen.value else 0)
            self["image"].setTransitionDuration(-1 if config.plugins.merlinmusicplayer2.transition_default_duration.value else config.plugins.merlinmusicplayer2.transition_duration.value)
            self["image"].startSlideShow(list, start_index, config.plugins.merlinmusicplayer2.picture_duration.value * 1000, config.plugins.merlinmusicplayer2.kenburns.value)

    def sleepTimerEntryOnStateChange(self, timer):
        if timer.state == TimerEntry.StateEnded:
            self.close()

    def showHide(self):
        if self.displayShown:
            if self.showHideTimer.isActive():
                self.showHideTimer.stop()
            if self.screenInfobar:
                self.screenInfobar.hide()
        else:
            if self.screenInfobar:
                self.screenInfobar.show()
            if self.idx:
                self.showHideTimer.start(self.idx * 1000)
        self.displayShown = not self.displayShown

    def showHideTimerTimeout(self):
        self.showHide()

    def updateDisplayText(self, text):
        if self.screenInfobar:
            self.screenInfobar.updateDisplayText(text)
        if not self.initialized:
            return
        self.displayShown = False
        if config.plugins.merlinmusicplayer2.infobar_timeout_picture.value:
            self.showHide()

    def updateLCD(self, text, line):
        if self.screenInfobar:
            self.screenInfobar.updateLCD(text, line)
        self.summaries.setText(text, line)

    def updateCover(self, filename=""):
        if self.screenInfobar:
            self.screenInfobar.updateCover(filename)
        self.summaries.updateCover(filename)

    def __onClose(self):
        self.session.deleteDialog(self.screenInfobar)
        self.session.nav.SleepTimer.on_state_change.remove(self.sleepTimerEntryOnStateChange)
        if self.showHideTimer.isActive():
            self.showHideTimer.stop()
        config.plugins.merlinmusicplayer2.last_picture_filename.value = os_path.basename(self["image"].getCurrentFilename())
        config.plugins.merlinmusicplayer2.last_picture_filename.save()
        if config.plugins.merlinmusicplayer2.usestandardradiobackground.value:
            eMerlinMusicPlayer.getInstance().show_iFrame_Pic(config.misc.radiopic.value)
        else:
            eMerlinMusicPlayer.getInstance().show_iFrame_Pic(eEnv.resolve("${libdir}/enigma2/python/Plugins/Extensions/MerlinMusicPlayer2/images/background"))

    def pause(self):
        self["image"].setState()

    def skipImage(self, direction):
        self["image"].skipImage(direction)

    def createSummary(self):
        return MerlinMusicPlayer2PicturesLCDScreen


class MerlinMusicPlayer2TV(MerlinMusicPlayer2ScreenSaver):

    def __init__(self, session, currentService, servicelist):
        self.session = session
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        self.onClose.append(self.__onClose)
        self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ChannelSelectBaseActions", "ChannelSelectEPGActions"],
        {
            "cancel": self.close,
            "ok": self.showHide,
            "right": self.nextService,
            "left": self.prevService,
            "nextBouquet": self.nextBouquet,
            "prevBouquet": self.prevBouquet,
            "showEPGList": self.openEventView,

        }, -1)
        self["actions2"] = NumberActionMap(["NumberActions"],
        {
            "1": self.keyNumberGlobal,
            "2": self.keyNumberGlobal,
            "3": self.keyNumberGlobal,
            "4": self.keyNumberGlobal,
            "5": self.keyNumberGlobal,
            "6": self.keyNumberGlobal,
            "7": self.keyNumberGlobal,
            "8": self.keyNumberGlobal,
            "9": self.keyNumberGlobal,
        }, -1)
        self.epgcache = eEPGCache.getInstance()
        self.servicelist = servicelist
        self["infobar"] = Label()
        self["NowEPG"] = Label()
        self["NowTime"] = Label()
        self["NextEPG"] = Label()
        self["NextTime"] = Label()
        self["NowChannel"] = Label()

        self.videoPlayer = eMerlinVideoPlayer()
        VolumeControl.instance.volctrl = self.videoPlayer
        self.initialized = False

        self["display"] = Label()
        self["video"] = VideoWindow(decoder=0, fb_width=getDesktop(0).size().width(), fb_height=getDesktop(0).size().height())
        self["cover"] = MerlinMusicPlayerWidget()
        self["visu"] = MerlinMusicPlayerWidget()
        self["visu2"] = MerlinMusicPlayerWidget()
        self["rms0"] = MerlinMusicPlayerRMS()
        self["rms1"] = MerlinMusicPlayerRMS()
        self["rms2"] = MerlinMusicPlayerRMS()
        self["rms3"] = MerlinMusicPlayerRMS()
        self["rms4"] = MerlinMusicPlayerRMS()
        if self.servicelist is None:
            self.playService(currentService)
        else:
            current = ServiceReference(self.servicelist.getCurrentSelection())
            self.playService(current.ref)
        self.showHideTimer = eTimer()
        self.showHideTimer_conn = self.showHideTimer.timeout.connect(self.showHideTimerTimeout)
        self.session.nav.SleepTimer.on_state_change.append(self.sleepTimerEntryOnStateChange)
        self.updateTVInfos()
        self.onFirstExecBegin.append(self.initialize)

    def initialize(self):
        self.idx = config.plugins.merlinmusicplayer2.infobar_timeout.value
        if self.idx:
            self.showHideTimer.start(self.idx * 1000)
            self.displayShown = True
        else:
            self.displayShown = False
            self.hide()
        self.initialized = True

    def sleepTimerEntryOnStateChange(self, timer):
        if timer.state == TimerEntry.StateEnded:
            self.close()

    def showHide(self):
        if self.displayShown:
            if self.showHideTimer.isActive():
                self.showHideTimer.stop()
            self.hide()
        else:
            self.updateTVInfos()
            self.show()
            if self.idx:
                self.showHideTimer.start(self.idx * 1000)
        self.displayShown = not self.displayShown

    def showHideTimerTimeout(self):
        self.showHide()

    def updateDisplayText(self, text):
        self["display"].setText(text)
        if not self.initialized:
            return
        if config.plugins.merlinmusicplayer2.infobar_timeout_tv.value:
            if self.showHideTimer.isActive():
                self.showHideTimer.stop()
            self.displayShown = False
            self.showHide()

    def updateTVInfos(self):
        current = ServiceReference(self.servicelist.getCurrentSelection())
        self["NowChannel"].setText(current.getServiceName())
        nowepg, nowtimedisplay = self.getEPGNowNext(current.ref, 0)
        nextepg, nexttimedisplay = self.getEPGNowNext(current.ref, 1)
        self["NowEPG"].setText(nowepg)
        self["NextEPG"].setText(nextepg)
        self["NowTime"].setText(nowtimedisplay)
        self["NextTime"].setText(nexttimedisplay)

# Source Code taken from Virtual(Pip)Zap :-)

    def getEPGNowNext(self, ref, modus):
        # get now || next event
        if self.epgcache is not None:
            event = self.epgcache.lookupEvent(['IBDCTSERNX', (ref.toString(), modus, -1)])
            if event:
                if event[0][4]:
                    t = localtime(event[0][1])
                    duration = event[0][2]
                    if modus == 0:
                        timedisplay = "+%d min" % (((event[0][1] + duration) - time()) / 60)
                    elif modus == 1:
                        timedisplay = "%d min" % (duration / 60)
                    return "%02d:%02d %s" % (t[3], t[4], event[0][4]), timedisplay
                else:
                    return "", ""
        return "", ""

    # switch with numbers
    def keyNumberGlobal(self, number):
        if self.servicelist is not None:
            self.session.openWithCallback(self.numberEntered, NumberZap, number)

    def numberEntered(self, retval):
        if retval > 0:
            self.zapToNumber(retval)

    def searchNumberHelper(self, serviceHandler, num, bouquet):
        servicelist = serviceHandler.list(bouquet)
        if servicelist is not None:
            while num:
                serviceIterator = servicelist.getNext()
                if not serviceIterator.valid():  # check end of list
                    break
                playable = not (serviceIterator.flags & (eServiceReference.isMarker | eServiceReference.isDirectory))
                if playable:
                    num -= 1
            if not num:  # found service with searched number ?
                return serviceIterator, 0
        return None, num

    def zapToNumber(self, number):
        bouquet = self.servicelist.bouquet_root
        service = None
        serviceHandler = eServiceCenter.getInstance()
        bouquetlist = serviceHandler.list(bouquet)
        if bouquetlist is not None:
            while number:
                bouquet = bouquetlist.getNext()
                if not bouquet.valid():  # check end of list
                    break
                if bouquet.flags & eServiceReference.isDirectory:
                    service, number = self.searchNumberHelper(serviceHandler, number, bouquet)
        if service is not None:
            if self.servicelist.getRoot() != bouquet:  # already in correct bouquet?
                self.servicelist.clearPath()
                if self.servicelist.bouquet_root != bouquet:
                    self.servicelist.enterPath(self.servicelist.bouquet_root)
                self.servicelist.enterPath(bouquet)
            self.servicelist.setCurrentSelection(service)  # select the service in servicelist
        # update infos, no matter if service is none or not
        current = ServiceReference(self.servicelist.getCurrentSelection())
        self.playService(current.ref)

    def nextService(self):
        if self.servicelist is not None:
            # get next service
            if self.servicelist.inBouquet():
                prev = self.servicelist.getCurrentSelection()
                if prev:
                    prev = prev.toString()
                    while True:
                        if config.usage.quickzap_bouquet_change.value and self.servicelist.atEnd():
                            self.servicelist.nextBouquet()
                        else:
                            self.servicelist.moveDown()
                        cur = self.servicelist.getCurrentSelection()
                        if not cur or (not (cur.flags & 64)) or cur.toString() == prev:
                            break
            else:
                self.servicelist.moveDown()
            if self.isPlayable():
                current = ServiceReference(self.servicelist.getCurrentSelection())
                self.playService(current.ref)
            else:
                self.nextService()

    def prevService(self):
        if self.servicelist is not None:
            # get previous service
            if self.servicelist.inBouquet():
                prev = self.servicelist.getCurrentSelection()
                if prev:
                    prev = prev.toString()
                    while True:
                        if config.usage.quickzap_bouquet_change.value:
                            if self.servicelist.atBegin():
                                self.servicelist.prevBouquet()
                        self.servicelist.moveUp()
                        cur = self.servicelist.getCurrentSelection()
                        if not cur or (not (cur.flags & 64)) or cur.toString() == prev:
                            break
            else:
                self.servicelist.moveUp()
            if self.isPlayable():
                current = ServiceReference(self.servicelist.getCurrentSelection())
                self.playService(current.ref)
            else:
                self.prevService()

    def isPlayable(self):
        # check if service is playable
        current = ServiceReference(self.servicelist.getCurrentSelection())
        return not (current.ref.flags & (eServiceReference.isMarker | eServiceReference.isDirectory))

    def nextBouquet(self):
        if self.servicelist is not None:
            # next bouquet with first service
            if config.usage.multibouquet.value:
                self.servicelist.nextBouquet()
                current = ServiceReference(self.servicelist.getCurrentSelection())
                self.playService(current.ref)

    def prevBouquet(self):
        if self.servicelist is not None:
            # previous bouquet with first service
            if config.usage.multibouquet.value:
                self.servicelist.prevBouquet()
                current = ServiceReference(self.servicelist.getCurrentSelection())
                self.playService(current.ref)

    def openSingleServiceEPG(self):
        if self.servicelist is not None:
            current = ServiceReference(self.servicelist.getCurrentSelection())
            self.session.open(EPGSelection, current.ref)

    def openEventView(self):
        if self.servicelist is not None:
            epglist = []
            self.epglist = epglist
            service = ServiceReference(self.servicelist.getCurrentSelection())
            ref = service.ref
            evt = self.epgcache.lookupEventTime(ref, -1)
            if evt:
                epglist.append(evt)
            evt = self.epgcache.lookupEventTime(ref, -1, 1)
            if evt:
                epglist.append(evt)
            if epglist:
                self.session.open(EventViewEPGSelect, epglist[0], service, self.eventViewCallback, self.openSingleServiceEPG, self.openMultiServiceEPG, self.openSimilarList)

    def eventViewCallback(self, setEvent, setService, val):
        epglist = self.epglist
        if len(epglist) > 1:
            tmp = epglist[0]
            epglist[0] = epglist[1]
            epglist[1] = tmp
            setEvent(epglist[0])

    def openMultiServiceEPG(self):
        # not supported
        pass

    def openSimilarList(self, eventid, refstr):
        self.session.open(EPGSelection, refstr, None, eventid)

    def playService(self, service):
        if service and (service.flags & eServiceReference.isGroup):
            ref = getBestPlayableServiceReference(service, eServiceReference())
        else:
            ref = service
        if ref is not None:
            if HardwareInfo().get_device_name() in ("one", "two") and ref.getPath() == "":
                ref = eServiceReference(ENIGMA_MERLINPLAYER_ID, 0, "http://127.0.0.1:8001/"+ref.toString())
            self.videoPlayer.play(ref)
            self.updateTVInfos()

    def __onClose(self):
        VolumeControl.instance.volctrl = eDVBVolumecontrol.getInstance()
        self.session.nav.SleepTimer.on_state_change.remove(self.sleepTimerEntryOnStateChange)
        self.videoPlayer = None
        if self.showHideTimer.isActive():
            self.showHideTimer.stop()
        if config.plugins.merlinmusicplayer2.usestandardradiobackground.value:
            eMerlinMusicPlayer.getInstance().show_iFrame_Pic(config.misc.radiopic.value)
        else:
            eMerlinMusicPlayer.getInstance().show_iFrame_Pic(eEnv.resolve("${libdir}/enigma2/python/Plugins/Extensions/MerlinMusicPlayer2/images/background"))


class MerlinMusicPlayer2Screen(MerlinMusicPlayerBase, Screen, InfoBarBase, InfoBarSeek, InfoBarNotifications):

    def __init__(self, session, songlist, index, idreammode, currentservice, servicelist):
        self.session = session
        Screen.__init__(self, session)
        InfoBarNotifications.__init__(self)
        InfoBarBase.__init__(self)
        MerlinMusicPlayerBase.__init__(self)
        self["actions"] = ActionMap(["WizardActions", "MediaPlayerActions", "EPGSelectActions", "MediaPlayerSeekActions", "ColorActions", "InfobarActions", "InfobarInstantRecord"],
        {
            "back": self.closePlayer,
            "pause": self.pauseEntry,
            "stop": self.stopEntry,
            "right": self.playNext,
            "left": self.playPrevious,
            "up": self.showPlaylist,
            "down": self.showPlaylist,
            "prevBouquet": self.shuffleList,
            "nextBouquet": self.repeatSong,
            "info": self.showLyrics,
            "yellow": self.pauseEntry,
            "green": self.play,
            "red": self.startScreenSaver,
            "input_date_time": self.menu_pressed,
            "ok": boundFunction(self.showMedia, 0),
            "showRadio": self.showRadio,
            "instantRecord": self.recordStream,
            "showTv": self.showInternetRadioFavorites,
            "showMovies": boundFunction(self.showMedia, 1),
            "subtitles": boundFunction(self.showMedia, 2),
        }, -1)

        self["PositionGauge"] = ServicePositionGauge(self.session.nav)
        self["repeat"] = MultiPixmap()
        self["shuffle"] = MultiPixmap()
        self["dvrStatus"] = MultiPixmap()
        self["title"] = Label()
        self["album"] = Label()
        self["artist"] = Label()
        self["genre"] = Label()
        self["track"] = Label()
        self["nextTitle"] = Label()
        self["buffering"] = Label()
        self["gapless"] = MultiPixmap()
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
            {
                iPlayableService.evUpdatedInfo: self.__evUpdatedInfo,
                iPlayableService.evUser+10: self.__evAudioDecodeError,
                iPlayableService.evUser+12: self.__evPluginError,
                iPlayableService.evUser+13: self.embeddedCoverArt,
                iPlayableService.evStart: self.__serviceStarted,
                iPlayableService.evStopped: self.__serviceStopped,
                iPlayableService.evBuffering: self.__buffering,
            })

        InfoBarSeek.__init__(self, actionmap="MediaPlayerSeekActions")
        self.onClose.append(self.__onClose)
        self.session.nav.stopService()
        self.serviceStarted = False
        self.songList = songlist
        self.origSongList = songlist[:]
        self.currentIndex = index
        self.shuffle = False
        self.repeat = False
        self.currentFilename = ""
        self.currentGoogleCoverFile = ""
        self.googleDownloadDir = os_path.join(config.plugins.merlinmusicplayer2.googleimagepath.value, "downloaded_covers/")
        if not os_path.exists(self.googleDownloadDir):
            try:
                os_mkdir(self.googleDownloadDir)
            except:
                self.googleDownloadDir = "/tmp/"

        self.init = 0
        self.onShown.append(self.__onShown)
        # for lcd
        self.currentTitle = ""
        self.nextTitle = ""
        self.screenSaverTimer = eTimer()
        self.screensaverTimer_conn = self.screenSaverTimer.timeout.connect(self.screenSaverTimerTimeout)
        self.screenSaverScreen = None
        self.onShownTimer = eTimer()
        self.onShownTimer_conn = self.onShownTimer.timeout.connect(self.onShownTimerTimeout)
        self.iDreamMode = idreammode
        self.currentService = currentservice
        self.serviceList = servicelist
        self.session.nav.SleepTimer.on_state_change.append(self.sleepTimerEntryOnStateChange)
        self.autoActivationKeyPressedActionSlot = eActionMap.getInstance().bindAction('', -0x7FFFFFFF, self.autoActivationKeyPressed)
        self.gotEmbeddedCoverArt = False
        eMerlinMusicPlayer.getInstance().setFunc(self.getNextFile)
        self.sTitle = self.sAlbum = self.sArtist = self.sGenre = self.sYear = self.sTrackNumber = self.sTrackCount = ""
        self["cover"] = MerlinMusicPlayerWidget()
        self["visu"] = MerlinMusicPlayerWidget()
        self["visu2"] = MerlinMusicPlayerWidget()
        self["rms0"] = MerlinMusicPlayerRMS()
        self["rms1"] = MerlinMusicPlayerRMS()
        self["rms2"] = MerlinMusicPlayerRMS()
        self["rms3"] = MerlinMusicPlayerRMS()
        self["rms4"] = MerlinMusicPlayerRMS()
        config.plugins.merlinmusicplayer2.gapless.addNotifier(self.gaplessConfigOnChange, initial_call=True)
        config.plugins.merlinmusicplayer2.alsa.addNotifier(self.alsaConfigOnChange, initial_call=True)

    def menu_pressed(self):
        self.screenSaverTimer.stop()
        options = [(_("Configuration"), self.config), ]
        options.extend(((_("Radio channels"), self.showRadio), ))
        options.extend(((_("InternetRadio channels"), self.showInternetRadioFavorites),))
        options.extend(((_("Watch TV"), boundFunction(self.showMedia, 0)),))
        options.extend(((_("Watch video"), boundFunction(self.showMedia, 1)),))
        options.extend(((_("Show pictures"), boundFunction(self.showMedia, 2)),))
        self.session.openWithCallback(self.menuCallback, ChoiceBox, list=options)

    def menuCallback(self, ret):
        ret and ret[1]()

    def alsaConfigOnChange(self, configElement=None):
        eMerlinMusicPlayer.getInstance().enableAlsa(config.plugins.merlinmusicplayer2.alsa.value)

    def gaplessConfigOnChange(self, configElement=None):
        eMerlinMusicPlayer.getInstance().enableGapless(config.plugins.merlinmusicplayer2.gapless.value)
        if config.plugins.merlinmusicplayer2.gapless.value:
            gapless = 1
        else:
            gapless = 0
        self["gapless"].setPixmapNum(gapless)

    def getNextFile(self, arg):
        self.gotEmbeddedCoverArt = False
        filename = ""
        nextfilename = ""
        if not self.repeat:
            if self.currentIndex +1 > len(self.songList) -1:
                self.currentIndex = 0
            else:
                self.currentIndex += 1
        if self.songList[self.currentIndex][0].PTS is None:
            filename = self.songList[self.currentIndex][0].filename
            self.currentFilename = filename
            self["nextTitle"].setText(self.getNextTitle())
        else:
            self.playCUETrack()

        return filename

    def autoActivationKeyPressed(self, key=None, flag=None):
        self.screenSaverTimer.stop()
        if self.screenSaverScreen is None:
            self.screenSaverTimer.start(config.plugins.merlinmusicplayer2.screensaverwait.value * 60000)
        return 0

    def sleepTimerEntryOnStateChange(self, timer):
        if timer.state == TimerEntry.StateEnded:
            self.closePlayer()

    def embeddedCoverArt(self):
        self.gotEmbeddedCoverArt = True
        self.setCovers("/tmp/.id3coverart")

    def setCovers(self, filename):
        self["cover"].setCover(filename)
        if self.screenSaverScreen:
            self.screenSaverScreen.updateCover(filename)
        else:
            self.summaries.updateCover(filename)

    def screenSaverTimerTimeout(self):
        if config.plugins.merlinmusicplayer2.usescreensaver.value:
            self.startScreenSaver()

    def startScreenSaver(self):
        self.screenSaverTimer.stop()
        if not self.screenSaverScreen and self.instance.isEnabled():
            self.screenSaverScreen = self.session.instantiateDialog(MerlinMusicPlayer2ScreenSaver)
            self.session.execDialog(self.screenSaverScreen)
            self.screenSaverScreen.updateLCD(self.currentTitle, 1)
            self.screenSaverScreen.updateLCD(self.nextTitle, 4)
            album = self["album"].getText()
            if album:
                text = "%s - %s" % (self["title"].getText(), album)
            else:
                text = self["title"].getText()
            self.screenSaverScreen.updateDisplayText(text)
            self.screenSaverScreen.updateCover(self["cover"].filename)

    def resetScreenSaverTimer(self):
        if config.plugins.merlinmusicplayer2.usescreensaver.value and config.plugins.merlinmusicplayer2.screensaverwait.value != 0:
            self.screenSaverTimer.stop()
            self.screenSaverTimer.start(config.plugins.merlinmusicplayer2.screensaverwait.value * 60000)

    def onShownTimerTimeout(self):
        self.playSong(self.songList[self.currentIndex][0].filename)

    def __onShown(self):
        if self.init == 0:
            self.init = 1
            self.setCovers("")
            self.onShownTimer.start(0, 1)
        else:
            self.summaries.updateCover(self["cover"].filename)
            self.summaries.setText(self.currentTitle, 1)
            self.summaries.setText(self.nextTitle, 4)
            if self.screenSaverScreen:
                self.session.deleteDialog(self.screenSaverScreen)
                self.screenSaverScreen = None
        self.resetScreenSaverTimer()

    def __onClose(self):
        self.session.nav.SleepTimer.on_state_change.remove(self.sleepTimerEntryOnStateChange)
        config.plugins.merlinmusicplayer2.gapless.removeNotifier(self.gaplessConfigOnChange)
        config.plugins.merlinmusicplayer2.alsa.removeNotifier(self.alsaConfigOnChange)
        self.seek = None
        eMerlinMusicPlayer.getInstance().setFunc(None)
        self.autoActivationKeyPressedActionSlot = None

    def config(self):
        self.screenSaverTimer.stop()
        self.session.openWithCallback(self.setupFinished, MerlinMusicPlayer2Setup, False)

    def showMedia(self, mode):
        if (mode in (0, 1) and config.plugins.merlinmusicplayer2.hardwaredecoder.value is False and config.plugins.merlinmusicplayer2.alsa.value is True) or mode == 2:
            self.screenSaverTimer.stop()
            if self.screenSaverScreen:
                self.session.deleteDialog(self.screenSaverScreen)
                self.screenSaverScreen = None
            if mode == 0:
                self.screenSaverScreen = self.session.instantiateDialog(MerlinMusicPlayer2TV, self.currentService, self.serviceList)
            elif mode == 1:
                self.screenSaverScreen = self.session.instantiateDialog(MerlinMusicPlayer2Video, self.playNext, self.playPrevious)
            elif mode == 2:
                self.screenSaverScreen = self.session.instantiateDialog(MerlinMusicPlayer2Pictures)
            self.session.execDialog(self.screenSaverScreen)
            self.screenSaverScreen.updateLCD(self.currentTitle, 1)
            self.screenSaverScreen.updateLCD(self.nextTitle, 4)
            album = self["album"].getText()
            if album:
                text = "%s - %s" % (self["title"].getText(), album)
            else:
                text = self["title"].getText()
            self.screenSaverScreen.updateDisplayText(text)
            self.screenSaverScreen.updateCover(self["cover"].filename)
        else:
            msg = ""
            if mode == 0:
                msg = _("Activate alsasink to watch TV!")
            elif mode == 1:
                msg = _("Activate alsasink to watch videos!")
            self.session.open(MessageBox, msg, type=MessageBox.TYPE_INFO, timeout=20)

    def setupFinished(self, result):
        if result:
            self.googleDownloadDir = os_path.join(config.plugins.merlinmusicplayer2.googleimagepath.value, "downloaded_covers/")
            if not os_path.exists(self.googleDownloadDir):
                try:
                    os_mkdir(self.googleDownloadDir)
                except:
                    self.googleDownloadDir = "/tmp/"
        self.resetScreenSaverTimer()

    def closePlayer(self):
        if config.plugins.merlinmusicplayer2.startlastsonglist.value:
            config.plugins.merlinmusicplayer2.lastsonglistindex.value = self.currentIndex
            config.plugins.merlinmusicplayer2.lastsonglistindex.save()
            try:  # so lame, but OperationalError: disk I/O error occurs too often
                connection = OpenDatabase()
                if connection is not None:
                    connection.text_factory = str
                    cursor = connection.cursor()
                    cursor.execute("Delete from CurrentSongList;")
                    for song in self.origSongList:
                        title = song[0].title
                        if song[0].isDVB:
                            title = os_path.splitext(os_path.basename(song[0].filename))[0]
                        elif song[0].filename.lower().startswith("http://"):
                            title = song[0].text
                        cursor.execute("INSERT INTO CurrentSongList(song_id, filename, title, artist, album,genre, bitrate, length, track, date, PTS) VALUES(?,?,?,?,?,?,?,?,?,?,?);", (song[0].songID, song[0].filename, title, song[0].artist, song[0].album, song[0].genre, song[0].bitrate, song[0].length, song[0].track, song[0].date, song[0].PTS))
                    connection.commit()
                    cursor.close()
                    connection.close()
            except:
                pass
        self.screenSaverTimer.stop()
        self.close()

    def showRadio(self):
        self.session.openWithCallback(
                self.finishedServiceSelection,
                MerlinMusicPlayer2DVBRadioSelection,
                _("Select radio service")
            )

    def finishedServiceSelection(self, *args):
        if args:
            sname = args[0].toString()
            cur = eServiceReference(sname)
            serviceHandler = eServiceCenter.getInstance()
            info = serviceHandler.info(cur)
            name = info and info.getName(cur) or "."
            services = args[1]
            self.songList = []
            self.origSongList = []
            for s in services:
                a = Item(text=s[1], filename="http://127.0.0.1:8001/" + s[0].toString(), isDVB=True)
                self.songList.append((a,))
                self.origSongList.append((a,))
            self.currentIndex = args[2]
            self.playSong("http://127.0.0.1:8001/"+sname, name)

    def showInternetRadioFavorites(self):
        try:
            from Plugins.Extensions.InternetRadio.InternetRadioFavoriteConfig import InternetRadioFavoriteConfig
            favorite = InternetRadioFavoriteConfig()
            favoriteList = favorite.favoriteConfig.Entries
        except:
            favoriteList = None

        if favoriteList:
            self.songList = []
            self.origSongList = []
            for item in favoriteList:
                if item.type.value == 0:
                    a = Item(text=item.name.value, filename=item.text.value)
                    self.songList.append((a,))
                    self.origSongList.append((a,))
            if self.songList:
                self.currentIndex = 0
                self.showPlaylist()

    def playSong(self, filename, name=""):
        self.serviceStarted = False
        self.session.nav.stopService()
        self.sTitle = self.sAlbum = self.sArtist = self.sGenre = self.sYear = self.sTrackNumber = self.sTrackCount = ""
        self.seek = None
        self.currentFilename = filename
        self.gotEmbeddedCoverArt = False
        # if not self.setFolderCover():
        #   self.setCovers("")
        if not (config.plugins.merlinmusicplayer2.hardwaredecoder.value and HardwareInfo().get_device_name() not in ("one", "two")):
            sref = eServiceReference(ENIGMA_MERLINPLAYER_ID, 0, self.currentFilename)
        else:
            sref = eServiceReference(4097, 0, self.currentFilename)
        if name:
            sref.setName(name)
        else:
            if self.songList[self.currentIndex][0].isDVB:
                sref.setName(self.songList[self.currentIndex][0].text)
        self.session.nav.playService(sref)
        if self.iDreamMode:
            self.updateMusicInformation(self.songList[self.currentIndex][0].artist, self.songList[self.currentIndex][0].title,
            self.songList[self.currentIndex][0].album, self.songList[self.currentIndex][0].genre, self.songList[self.currentIndex][0].date, self.songList[self.currentIndex][0].track.replace("Track", ""), clear=True)
        if self.songList[self.currentIndex][0].PTS is not None:
            service = self.session.nav.getCurrentService()
            if service:
                self.seek = service.seek()
            self.updateMusicInformationCUE()
            self.ptsTimer = eTimer()
            self.ptsTimer_conn = self.ptsTimer.timeout.connect(self.ptsTimerCallback)
            self.ptsTimer.start(1000)

        self["nextTitle"].setText(self.getNextTitle())

    def ptsTimerCallback(self):
        if self.seek:
            pts = self.seek.getPlayPosition()
            index = 0
            currentIndex = 0
            for songs in self.songList:
                if pts[1] > songs[0].PTS:
                    currentIndex = index
                else:
                    break
                index += 1
            if currentIndex != self.currentIndex:
                self.currentIndex = currentIndex
                self.updateMusicInformationCUE()
        self.ptsTimer.start(1000)

    def updateMusicInformationCUE(self):
        self.updateSingleMusicInformation("artist", self.songList[self.currentIndex][0].artist, True)
        self.updateSingleMusicInformation("title", self.songList[self.currentIndex][0].title, True)
        self.updateSingleMusicInformation("album", self.songList[self.currentIndex][0].album, True)
        self.updateSingleMusicInformation("track", self.songList[self.currentIndex][0].track.replace("Track", ""), True)
        self.summaries.setText(self.songList[self.currentIndex][0].title, 1)
        if self.screenSaverScreen:
            self.screenSaverScreen.updateLCD(self.songList[self.currentIndex][0].title, 1)
            if self.songList[self.currentIndex][0].album:
                self.screenSaverScreen.updateDisplayText("%s - %s" % (self.songList[self.currentIndex][0].title, self.songList[self.currentIndex][0].album))
            else:
                self.screenSaverScreen.updateDisplayText(self.songList[self.currentIndex][0].title)
        self.updateCover(self.songList[self.currentIndex][0].artist, self.songList[self.currentIndex][0].album)
        self.currentTitle = self.songList[self.currentIndex][0].title
        self["nextTitle"].setText(self.getNextTitle())

    def __buffering(self):
        currPlay = self.session.nav.getCurrentService()
        if currPlay is not None:
            streamed = currPlay.streamed()
            bufferInfo = streamed.getBufferCharge()
            percent = bufferInfo[0]
            text = ""
            if percent != 100 and percent != 0:  # 0 --> One Bug(?) FIXME
                text = "Buffering %d ..." % percent
            self["buffering"].setText(text)

    def __serviceStopped(self):
        self.serviceStarted = False

    def __serviceStarted(self):
        self.serviceStarted = True
        self["dvrStatus"].setPixmapNum(0)

    def __evUpdatedInfo(self):
        currPlay = self.session.nav.getCurrentService()
        if currPlay is not None:
            if not self.serviceStarted:
                return
            if currPlay.info().getInfoObject(iServiceInformation.sTagTrackGain) is None:
                return
            sTitle = currPlay.info().getInfoString(iServiceInformation.sTagTitle)
            sAlbum = currPlay.info().getInfoString(iServiceInformation.sTagAlbum)
            sArtist = currPlay.info().getInfoString(iServiceInformation.sTagArtist)
            sGenre = currPlay.info().getInfoString(iServiceInformation.sTagGenre)
            sYear = currPlay.info().getInfoString(iServiceInformation.sTagDate)
            sTrackNumber = currPlay.info().getInfo(iServiceInformation.sTagTrackNumber)
            sTrackCount = currPlay.info().getInfo(iServiceInformation.sTagTrackCount)

            if sTitle == self.sTitle and sAlbum == self.sAlbum and sArtist == self.sArtist and sGenre == self.sGenre and sYear == self.sYear and sTrackNumber == self.sTrackNumber and sTrackCount == self.sTrackCount:
                return

            self.sTitle = sTitle
            self.sAlbum = sAlbum
            self.sArtist = sArtist
            self.sGenre = sGenre
            self.sYear = sYear
            self.sTrackNumber = sTrackNumber
            self.sTrackCount = sTrackCount

            track = ""
            if sTrackNumber and sTrackCount:
                track = "%s/%s" % (sTrackNumber, sTrackCount)
            elif sTrackNumber:
                track = str(sTrackNumber)
            if sYear:
                sYear = "(%s)" % sYear

            if self.songList[self.currentIndex][0].PTS is None:
                self.updateMusicInformation(sArtist, sTitle, sAlbum, sGenre, sYear, track, clear=True)
            else:
                self.updateSingleMusicInformation("genre", sGenre, True)
        else:
            self.setCovers("")
            self.updateMusicInformation(clear=True)

    def updateMusicInformation(self, artist="", title="", album="", genre="", year="", track="", clear=False):
        if year and album:
            album_year = "%s %s" % (album, year)
        else:
            album_year = album

        if self.songList[self.currentIndex][0].filename.startswith("http://") and album_year == "":
            album_year = self.songList[self.currentIndex][0].text
        self.updateSingleMusicInformation("artist", artist, clear)
        self.updateSingleMusicInformation("title", title, clear)
        self.updateSingleMusicInformation("album", album_year, clear)
        self.updateSingleMusicInformation("genre", genre, clear)
        self.updateSingleMusicInformation("track", track, clear)
        self.currentTitle = title
        if not self.iDreamMode and self.songList[self.currentIndex][0].PTS is None:
            # for lyrics
            self.songList[self.currentIndex][0].title = title
            self.songList[self.currentIndex][0].artist = artist
        self.summaries.setText(title, 1)
        if self.screenSaverScreen:
            self.screenSaverScreen.updateLCD(title, 1)
            if album:
                self.screenSaverScreen.updateDisplayText("%s - %s" % (title, album))
            else:
                self.screenSaverScreen.updateDisplayText(title)

        if self.gotEmbeddedCoverArt is False:
            if not self.setFolderCover():
                self.updateCover(artist, album)

    def setFolderCover(self):
        path = os_path.dirname(os_path.abspath(self.currentFilename))
        if not path.endswith("/"):
            path = path + "/"
        coverFileNames = ["folder.png", "folder.jpg", "cover.jpg", "cover.png", "coverArt.jpg"]
        coverArtFileName = None
        for filename in coverFileNames:
            if fileExists(path + filename):
                coverArtFileName = path + filename
        if coverArtFileName is not None:
            self.gotEmbeddedCoverArt = True
            print("[MerlinMusicPlayer] using cover from directory")
            self.setCovers(coverArtFileName)
            return True
        return False

    def updateCover(self, artist, album):
        if self.gotEmbeddedCoverArt is False:
            if config.plugins.merlinmusicplayer2.usegoogleimage.value:
                self.getGoogleCover(artist, album)
            else:
                self.gotEmbeddedCoverArt = True
                self.setCovers("")
                self.currentGoogleCoverFile = ""

    def updateSingleMusicInformation(self, name, info, clear):
        if info != "" or clear:
            if self[name].getText() != info:
                self[name].setText(info)

    def getGoogleCover(self, artist, album):
        if (artist != "" and album != "") or ("://" in self.currentFilename and self.sTitle != ""):
            if (artist != "" and album != ""):
                file_name_string = self.googleDownloadDir + "%s_%s" % (self.format_filename(artist), self.format_filename(album))
            else:
                file_name_string = self.googleDownloadDir + self.format_filename(self.sTitle)
            if os_path.exists(file_name_string):
                print("[MerlinMusicPlayer] using cover from %s " % file_name_string)
                self.setCovers(file_name_string)
            else:
                print("[MerlinMusicPlayer] searching for cover at iTunes")
                if (artist != "" and album != ""):
                    searchstr = "%s+%s" % (quote(album), quote(artist))
                else:
                    searchstr = quote(self.sTitle)
                url = "http://itunes.apple.com/search?term=%s&limit=1&media=music" % (searchstr)
                if self.currentGoogleCoverFile != url:
                    self.setCovers("")
                    self.currentGoogleCoverFile = url
                    print url
                    getPage(url, timeout=4).addCallback(boundFunction(self.googleImageCallback, file_name_string)).addErrback(self.coverDownloadFailed)
        else:
            self.setCovers("")

    def googleImageCallback(self, filename, result):
        url = ""
        try:
            data = json_loads(result)
            url = data['results'][0]['artworkUrl100'].encode('utf-8')
            url = url.replace('100x100', '450x450').replace('https', 'http')
        except:
            pass
        if url:
            print("[MerlinMusicPlayer] downloading cover from %s " % url)
            downloadPage(url, filename).addCallback(boundFunction(self.coverDownloadFinished, filename)).addErrback(self.coverDownloadFailed)
        else:
            print('iTunes-images not found...')
            self.setCovers("")

    def format_filename(self, filename):
        f = "".join([c for c in filename if c.isalpha() or c.isdigit() or c == ' '])
        return f.replace(" ", "_")

    def coverDownloadFailed(self, result):
        print("[MerlinMusicPlayer] cover download failed: %s " % result)
        self.setCovers("")

    def coverDownloadFinished(self, filename, result):
        print("[MerlinMusicPlayer] cover download finished")
        self.setCovers(filename)

    def __evAudioDecodeError(self):
        self.updateSingleMusicInformation("artist", "", True)
        self.updateSingleMusicInformation("album", "", True)
        self.updateSingleMusicInformation("genre", "", True)
        self.updateSingleMusicInformation("track", "", True)
        self.updateSingleMusicInformation("title", self.currentFilename, True)
        currPlay = self.session.nav.getCurrentService()
        sAudioType = currPlay.info().getInfoString(iServiceInformation.sUser+10)
        print("[MerlinMusicPlayer] audio-codec %s can't be decoded by hardware" % (sAudioType))
        self.session.open(MessageBox, _("This Dreambox can't decode %s streams!") % sAudioType, type=MessageBox.TYPE_INFO, timeout=20)

    def __evPluginError(self):
        self.updateSingleMusicInformation("artist", "", True)
        self.updateSingleMusicInformation("album", "", True)
        self.updateSingleMusicInformation("genre", "", True)
        self.updateSingleMusicInformation("track", "", True)
        self.updateSingleMusicInformation("title", self.currentFilename, True)
        currPlay = self.session.nav.getCurrentService()
        message = currPlay.info().getInfoString(iServiceInformation.sUser+12)
        print("[MerlinMusicPlayer]", message)
        self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=20)

    def doEofInternal(self, playing):
        if playing:
            self.playNext()

    def checkSkipShowHideLock(self):
        self.updatedSeekState()

    def updatedSeekState(self):
        if self.seekstate == self.SEEK_STATE_PAUSE:
            self["dvrStatus"].setPixmapNum(1)
        elif self.seekstate == self.SEEK_STATE_PLAY:
            self["dvrStatus"].setPixmapNum(0)

    def pauseEntry(self):
        self.updatedSeekState()
        if self.seekstate == self.SEEK_STATE_PAUSE:
            self.unPauseService()
        else:
            self.pauseService()
        self.resetScreenSaverTimer()

    def play(self):
        # play the current song from beginning again
        if self.songList[self.currentIndex][0].PTS is None:
            self.playSong(self.songList[self.currentIndex][0].filename)
        else:
            if self.seek:
                self.seek.seekTo(self.songList[self.currentIndex][0].PTS)
                self.updatedSeekState()
        self.resetScreenSaverTimer()

    def unPauseService(self):
        if self.seekstate == self.SEEK_STATE_PAUSE:
            self.setSeekState(self.SEEK_STATE_PLAY)

    def stopEntry(self):
        self.seek = None
        self.session.nav.stopService()
        self.origSongList = []
        self.songList = []
        if config.plugins.merlinmusicplayer2.startlastsonglist.value:
            config.plugins.merlinmusicplayer2.lastsonglistindex.value = -1
            config.plugins.merlinmusicplayer2.lastsonglistindex.save()
            try:  # so lame, but OperationalError: disk I/O error occurs too often
                connection = OpenDatabase()
                if connection is not None:
                    connection.text_factory = str
                    cursor = connection.cursor()
                    cursor.execute("Delete from CurrentSongList;")
                    connection.commit()
                    cursor.close()
                    connection.close()
            except:
                pass
        self.resetScreenSaverTimer()
        self.close()

    def playNext(self):
        if not self.repeat:
            if self.currentIndex +1 > len(self.songList) -1:
                self.currentIndex = 0
            else:
                self.currentIndex += 1
        if self.songList[self.currentIndex][0].PTS is None:
            self.playSong(self.songList[self.currentIndex][0].filename)
        else:
            self.playCUETrack()
        if not self.screenSaverScreen:
            self.resetScreenSaverTimer()

    def playPrevious(self):
        if not self.repeat:
            if self.currentIndex - 1 < 0:
                self.currentIndex = len(self.songList) - 1
            else:
                self.currentIndex -= 1
        if self.songList[self.currentIndex][0].PTS is None:
            self.playSong(self.songList[self.currentIndex][0].filename)
        else:
            self.playCUETrack()
        self.resetScreenSaverTimer()

    def getNextTitle(self):
        if self.repeat:
            index = self.currentIndex
        else:
            if self.currentIndex + 1 > len(self.songList) -1:
                index = 0
            else:
                index = self.currentIndex + 1
        if self.iDreamMode or self.songList[index][0].PTS is not None:
            text = "%s - %s" % (self.songList[index][0].title, self.songList[index][0].artist)
        else:
            if self.songList[index][0].filename.lower().startswith("http://"):
                text = self.songList[index][0].text
            else:
                path, filename = os_path.split(self.songList[index][0].filename)
                audio, isAudio, title, genre, artist, album, tracknr, track, date, length, bitrate = getID3Tags(path, filename)
                if audio:
                    if artist:
                        text = "%s - %s" % (title, artist)
                    else:
                        text = title
                else:
                    text = title
                audio = None
        self.nextTitle = text
        self.summaries.setText(text, 4)
        if self.screenSaverScreen:
            self.screenSaverScreen.updateLCD(text, 4)
        return str(text)

    def shuffleList(self):
        if self.songList[self.currentIndex][0].PTS is None:  # not implemented for cue files yet
            self.shuffle = not self.shuffle
            if self.shuffle:
                self["shuffle"].setPixmapNum(1)
                shuffle(self.songList)
            else:
                self.songList = self.origSongList[:]
                self["shuffle"].setPixmapNum(0)
            index = 0
            for x in self.songList:
                if x[0].filename == self.currentFilename:
                    self.currentIndex = index
                    break
                index += 1
            self["nextTitle"].setText(self.getNextTitle())
        else:
            self.session.open(MessageBox, _("Shuffle is not available yet with cue-files!"), type=MessageBox.TYPE_INFO, timeout=20)
        self.resetScreenSaverTimer()

    def repeatSong(self):
        if self.songList[self.currentIndex][0].PTS is None:  # not implemented for cue files yet
            self.repeat = not self.repeat
            if self.repeat:
                self["repeat"].setPixmapNum(1)
            else:
                self["repeat"].setPixmapNum(0)
            self["nextTitle"].setText(self.getNextTitle())
        else:
            self.session.open(MessageBox, _("Repeat is not available yet with cue-files!"), type=MessageBox.TYPE_INFO, timeout=20)
        self.resetScreenSaverTimer()

    def showPlaylist(self):
        self.screenSaverTimer.stop()
        self.session.openWithCallback(self.showPlaylistCallback, MerlinMusicPlayer2SongList, self.songList, self.currentIndex, self.iDreamMode)

    def showPlaylistCallback(self, index):
        if index != -1:
            self.currentIndex = index
            if self.songList[self.currentIndex][0].PTS is None:
                self.playSong(self.songList[self.currentIndex][0].filename)
            else:
                self.playCUETrack()
        self.resetScreenSaverTimer()

    def playCUETrack(self):
        if self.ptsTimer.isActive():
            self.ptsTimer.stop()
        if self.seek:
            self.seek.seekTo(self.songList[self.currentIndex][0].PTS)
            self.updatedSeekState()
            self.updateMusicInformationCUE()
            self.ptsTimer.start(1000)

    def showLyrics(self):
        self.screenSaverTimer.stop()
        self.session.openWithCallback(self.resetScreenSaverTimer, MerlinMusicPlayer2Lyrics, self.songList[self.currentIndex][0])

    def recordStream(self):
        if self.currentFilename.startswith('http'):
            MerlinRecorder.instance.startRecording(self.currentFilename, config.plugins.merlinmusicplayerrecorder.lastLocation.value, self.songList[self.currentIndex][0].text.replace('\xc2\x86', '').replace('\xc2\x87', '') + "_playlist", self.songList[self.currentIndex][0].text.replace('\xc2\x86', '').replace('\xc2\x87', ''), config.plugins.merlinmusicplayerrecorder.split_files.value, config.plugins.merlinmusicplayerrecorder.duration.value, self.songList[self.currentIndex][0].text.replace('\xc2\x86', '').replace('\xc2\x87', ''))

    def createSummary(self):
        return MerlinMusicPlayer2LCDScreen


class MerlinMusicPlayer2ScreenInfobar(MerlinMusicPlayer2Screen):
    def __init__(self, session, songlist, index, idreammode, currentservice, servicelist):
        MerlinMusicPlayer2Screen.__init__(self, session, songlist, index, idreammode, currentservice, servicelist)
        self.skinName = []
        if HardwareInfo().get_device_name() not in ("dm900", "dm920"):
            self.skinName.append("MerlinMusicPlayer2Screen_MIPSEL")
        else:
            self.skinName.append("MerlinMusicPlayer2Screen_ARM")
        self.skinName.append("MerlinMusicPlayer2Screen")
        eMerlinMusicPlayer.getInstance().show_iFrame_Pic(eEnv.resolve("${libdir}/enigma2/python/Plugins/Extensions/MerlinMusicPlayer2/images/background"))

    def closePlayer(self):
        if self.screenSaverTimer.isActive():
            self.screenSaverTimer.stop()
        self.seek = None
        self.close()

    def stopEntry(self):
        self.closePlayer()


class MerlinMusicPlayer2Lyrics(MerlinMusicPlayerBase, Screen):

    IS_DIALOG = True

    def __init__(self, session, currentsong):
        self.session = session
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        self["headertext"] = Label(_("Merlin Music Player Lyrics"))
        self["resulttext"] = Label()
        self["actions"] = ActionMap(["WizardActions", "DirectionActions"],
        {
            "back": self.close,
            "upUp": self.pageUp,
            "leftUp": self.pageUp,
            "downUp": self.pageDown,
            "rightUp": self.pageDown,
        }, -1)
        self["lyric_text"] = ScrollLabel()
        self.currentSong = currentsong
        self.onLayoutFinish.append(self.startRun)

    def startRun(self):
        # get lyric-text from id3 tag
        try:
            audio = ID3(self.currentSong.filename)
        except:
            audio = None
        text = getEncodedString(self.getLyricsFromID3Tag(audio)).replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        self["lyric_text"].setText(text)

    def getLyricsFromID3Tag(self, tag):
        if tag:
            for frame in tag.values():
                if frame.FrameID == "USLT":
                    return frame.text
        url = "http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect?artist=%s&song=%s" % (quote(self.currentSong.artist), quote(self.currentSong.title))
        sendUrlCommand(url, None, 10).addCallback(self.gotLyrics).addErrback(self.urlError)
        return "No lyrics found in id3-tag, trying api.chartlyrics.com..."

    def urlError(self, error=None):
        if error is not None:
            self["resulttext"].setText(str(error.getErrorMessage()))
            self["lyric_text"].setText("")

    def gotLyrics(self, xmlstring):
        root = cet_fromstring(xmlstring)
        lyrictext = ""
        lyrictext = root.findtext("{http://api.chartlyrics.com/}Lyric").encode("utf-8", 'ignore')
        self["lyric_text"].setText(lyrictext)
        title = root.findtext("{http://api.chartlyrics.com/}LyricSong").encode("utf-8", 'ignore')
        artist = root.findtext("{http://api.chartlyrics.com/}LyricArtist").encode("utf-8", 'ignore')
        result = _("Response -> lyrics for: %s (%s)") % (title, artist)
        self["resulttext"].setText(result)
        if not lyrictext:
            self["resulttext"].setText(_("No lyrics found"))
            self["lyric_text"].setText("")

    def pageUp(self):
        self["lyric_text"].pageUp()

    def pageDown(self):
        self["lyric_text"].pageDown()


class MerlinMusicPlayer2SongList(MerlinMusicPlayerBase, Screen):

    IS_DIALOG = True

    def __init__(self, session, songlist, index, idreammode):
        self.session = session
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        self["headertext"] = Label(_("Merlin Music Player Songlist"))
        self["list"] = iDreamList()
        self["list"].connectSelChanged(self.lcdUpdate)
        self["actions"] = ActionMap(["WizardActions"],
        {
            "ok": self.ok,
            "back": self.closing,
        }, -1)
        self.songList = songlist
        self.index = index
        self.iDreamMode = idreammode
        self.onLayoutFinish.append(self.startRun)
        self.onShown.append(self.lcdUpdate)

    def startRun(self):
        if self.iDreamMode:
            self["list"].setMode(10)  # songlist
        self["list"].setList(self.songList)
        self["list"].moveToIndex(self.index)

    def ok(self):
        self.close(self["list"].getCurrentIndex())

    def closing(self):
        self.close(-1)

    def lcdUpdate(self):
        try:
            index = self["list"].getCurrentIndex()
            songlist = self["list"].getList()
            mode = self.iDreamMode or songlist[index][0].PTS
            if mode:
                self.summaries.setText(songlist[index][0].title, 1)
            else:
                self.summaries.setText(songlist[index][0].text, 1)
            count = self["list"].getItemCount()
            # voheriges
            index -= 1
            if index < 0:
                index = count
            if mode:
                self.summaries.setText(songlist[index][0].title, 3)
            else:
                self.summaries.setText(songlist[index][0].text, 3)
            # naechstes
            index = self["list"].getCurrentIndex() + 1
            if index > count:
                index = 0
            if mode:
                self.summaries.setText(songlist[index][0].title, 4)
            else:
                self.summaries.setText(songlist[index][0].text, 4)
        except:
            pass

    def createSummary(self):
        return MerlinMusicPlayerLCDScreenText


class iDreamAddToDatabaseScreen(MerlinMusicPlayerBase, Screen):

    IS_DIALOG = True

    def __init__(self, session, initDir):
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        self["actions"] = ActionMap(["WizardActions", "ColorActions"],
        {
            "back": self.cancel,
            "green": self.green,
            "red": self.cancel,
            "ok": self.green,

        }, -1)
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("Close"))
        self["output"] = Label()
        self.onClose.append(self.__onClose)
        self.pathToDatabase_mp_conn = pathToDatabase.MessagePump.recv_msg.connect(self.gotThreadMsg)
        if not pathToDatabase.isRunning and initDir:
            pathToDatabase.Start(initDir)

    def gotThreadMsg(self, msg):
        msg = pathToDatabase.Message.pop()
        self["output"].setText(msg[1])
        if msg[0] == THREAD_FINISHED:
            self["key_red"].setText("")

    def green(self):
        self.close()

    def cancel(self):
        if pathToDatabase.isRunning:
            pathToDatabase.Cancel()

    def __onClose(self):
        del self.pathToDatabase_mp_conn


class iDream(MerlinMusicPlayerBase, Screen):

    def __init__(self, session, servicelist):
        self.session = session
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        self["list"] = iDreamList()
        self["list"].connectSelChanged(self.lcdUpdate)
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions", "EPGSelectActions"],
        {
            "ok": self.ok,
            "back": self.closing,
            "red": self.red_pressed,
            "green": self.green_pressed,
            "yellow": self.yellow_pressed,
            "blue": self.blue_pressed,
            "input_date_time": self.menu_pressed,
            "info": self.info_pressed,
        }, -1)

        self["actions2"] = NumberActionMap(["InputActions"],
        {
            "0": self.keyNumber_pressed,
        }, -1)

        self.onLayoutFinish.append(self.startRun)
        self.onShown.append(self.lcdUpdate)
        self.onClose.append(self.__onClose)

        self.serviceList = servicelist
        self.currentService = self.session.nav.getCurrentlyPlayingServiceReference()
        self.session.nav.stopService()

        self.mode = 0
        self.mainMenuList = []
        self.cacheList = []
        self.LastMethod = None
        self.player = None

        self["key_red"] = StaticText("")
        self["key_green"] = StaticText("")
        self["key_yellow"] = StaticText("")
        self["key_blue"] = StaticText("")
        self["headertext"] = Label(_("iDream Main Menu"))

        self.startMerlinPlayerScreenTimer = eTimer()
        self.startMerlinPlayerScreenTimer_conn = self.startMerlinPlayerScreenTimer.timeout.connect(self.info_pressed)
        self.autoActivationKeyPressedActionSlot = eActionMap.getInstance().bindAction('', -0x7FFFFFFF, self.autoActivationKeyPressed)

        self.session.nav.SleepTimer.on_state_change.append(self.sleepTimerEntryOnStateChange)

        if config.plugins.merlinmusicplayer2.usestandardradiobackground.value:
            eMerlinMusicPlayer.getInstance().show_iFrame_Pic(config.misc.radiopic.value)
        else:
            eMerlinMusicPlayer.getInstance().show_iFrame_Pic(eEnv.resolve("${libdir}/enigma2/python/Plugins/Extensions/MerlinMusicPlayer2/images/background"))

    def sleepTimerEntryOnStateChange(self, timer):
        if timer.state == TimerEntry.StateEnded:
            self.close()

    def autoActivationKeyPressed(self, key=None, flag=None):
        self.startMerlinPlayerScreenTimer.stop()
        if self.instance.isVisible() and self.isEnabled():
            self.startMerlinPlayerScreenTimer.start(START_MERLIN_PLAYER_SCREEN_TIMER_VALUE)
        return 0

    def getPlayList(self):
        connection = OpenDatabase()
        if connection is not None:
            connection.text_factory = str
            cursor = connection.cursor()
            playList = []
            cursor.execute("select playlist_id,playlist_text from playlists order by playlist_text;")
            for row in cursor:
                playList.append((row[1], row[0]))
            cursor.close()
            connection.close()
            return playList
        else:
            return None

    def sqlCommand(self, sqlSatement):
        connection = OpenDatabase()
        if connection is not None:
            cursor = connection.cursor()
            cursor.execute(sqlSatement)
            cursor.close()
            connection.commit()
            connection.close()

    def clearCache(self):
        for items in self.cacheList:
            items.cache = False
            items.listview = []
            items.headertext = ""

    def getCurrentSelection(self):
        sel = None
        try:
            sel = self["list"].l.getCurrentSelection()[0]
        except:
            pass
        return sel

    def addListToPlaylistConfirmed(self, methodName, answer):
        if answer:
            playList = self.getPlayList()
            if len(playList):
                self.session.openWithCallback(methodName, ChoiceBox, list=playList)
            else:
                self.session.openWithCallback(self.createPlaylistConfirmed, MessageBox, _("There are no playlists defined.\nDo you want to create a new playlist?"))

    def menu_pressed(self):
        self.startMerlinPlayerScreenTimer.stop()
        options = [(_("Configuration"), self.config), (_("Search in iDream database"), self.searchInIDreamDatabase), ]
        options.extend(((_("Scan path for music files and add them to database"), self.scanDir), ))
        if self.mode != 1:
            options.extend(((_("Create new playlist"), self.createPlaylist),))
        if self["list"].getDisplaySongMode():
            if self.mode == 2:
                options.extend(((_("Delete song from current playlist"), self.deleteSongFromPlaylist),))
            else:
                options.extend(((_("Add selected song to a playlist"), self.addSongToPlaylist),))
                if self.mode == 18:
                    options.extend(((_("Add all songs from selected album to a playlist"), self.addAlbumToPlaylist),))
                elif self.mode == 19:
                    options.extend(((_("Add all songs from selected artist to a playlist"), self.addArtistToPlaylist),))
                options.extend(((_("Delete song from database"), self.deleteSongFromDatabase),))
            options.extend(((_("Clear current songlist and play selected entry"), self.stopPlayingAndAppendFileToSongList),))
            options.extend(((_("Append file to current playing songlist"), self.appendFileToSongList),))
            if self.player is not None and self.player.songList:
                options.extend(((_("Insert file to current playing songlist and play next"), self.insertFileToSongList),))
        else:
            if self.mode == 1:
                options.extend(((_("Delete selected playlist"), self.deletePlaylist),))
            elif self.mode == 4:
                options.extend(((_("Add all songs from selected artist to a playlist"), self.addArtistToPlaylist),))
            elif self.mode == 5 or self.mode == 7:
                options.extend(((_("Add all songs from selected album to a playlist"), self.addAlbumToPlaylist),))
            elif self.mode == 13:
                options.extend(((_("Add all songs from selected genre to a playlist"), self.addGenreToPlaylist),))
        self.session.openWithCallback(self.menuCallback, ChoiceBox, list=options)

    def menuCallback(self, ret):
        ret and ret[1]()

    def scanDir(self):
        self.session.openWithCallback(self.pathSelected, SelectPath2, "/media/")

    def pathSelected(self, res):
        if res is not None:
            self.session.openWithCallback(self.filesAdded, iDreamAddToDatabaseScreen, res)

    def filesAdded(self):
        if pathToDatabase.isRunning:
            self.close()
        else:
            self.red_pressed()

    def addGenreToPlaylist(self):
        self.session.openWithCallback(boundFunction(self.addListToPlaylistConfirmed, self.addGenreToPlaylistConfirmedCallback), MessageBox, _("Do you really want to add all songs from that genre to a playlist?"))

    def addGenreToPlaylistConfirmedCallback(self, ret):
        if ret:
            sel = self.getCurrentSelection()
            if sel:
                self.sqlCommand("INSERT INTO Playlist_Songs (playlist_id,song_id) select %d, song_id from songs where genre_id=%d order by album_id,tracknumber,title, filename;" % (ret[1], sel.genreID))
                self.clearCache()

    def addArtistToPlaylist(self):
        self.session.openWithCallback(boundFunction(self.addListToPlaylistConfirmed, self.addArtistToPlaylistConfirmedCallback), MessageBox, _("Do you really want to add all songs from that artist to a playlist?"))

    def addArtistToPlaylistConfirmedCallback(self, ret):
        if ret:
            sel = self.getCurrentSelection()
            if sel:
                self.sqlCommand("INSERT INTO Playlist_Songs (playlist_id,song_id) select %d, song_id from songs where artist_id=%d order by album_id,tracknumber,title, filename;" % (ret[1], sel.artistID))
                self.clearCache()

    def addAlbumToPlaylist(self):
        self.session.openWithCallback(boundFunction(self.addListToPlaylistConfirmed, self.addAlbumToPlaylistConfirmedCallback), MessageBox, _("Do you really want to add all songs from that album to a playlist?"))

    def addAlbumToPlaylistConfirmedCallback(self, ret):
        if ret:
            sel = self.getCurrentSelection()
            if sel:
                self.sqlCommand("INSERT INTO Playlist_Songs (playlist_id,song_id) select %d, song_id from songs where album_id=%d order by tracknumber,title, filename;" % (ret[1], sel.albumID))
                self.clearCache()

    def deletePlaylist(self):
        self.session.openWithCallback(self.deletePlaylistConfirmed, MessageBox, _("Do you really want to delete the current playlist?"))

    def deletePlaylistConfirmed(self, answer):
        if answer:
            sel = self.getCurrentSelection()
            if sel:
                self.sqlCommand("delete from playlist_songs where playlist_id = %d" % (sel.playlistID))
                self.sqlCommand("delete from playlists where playlist_id = %d" % (sel.playlistID))
                self["list"].removeItem(self["list"].getCurrentIndex())
                self.clearCache()

    def deleteSongFromPlaylist(self):
        self.session.openWithCallback(self.deleteSongFromPlaylistConfirmed, MessageBox, _("Do you really want to delete that song the current playlist?"))

    def deleteSongFromPlaylistConfirmed(self, answer):
        if answer:
            sel = self.getCurrentSelection()
            if sel:
                self.sqlCommand("delete from playlist_songs where song_id = %d" % (sel.songID))
                self["list"].removeItem(self["list"].getCurrentIndex())
                self.clearCache()

    def deleteSongFromDatabase(self):
        self.session.openWithCallback(self.deleteSongFromDatabaseConfirmed, MessageBox, _("Do you really want to delete that song from the database?"))

    def deleteSongFromDatabaseConfirmed(self, answer):
        if answer:
            sel = self.getCurrentSelection()
            if sel:
                self.sqlCommand("delete from playlist_songs where song_id = %d" % (sel.songID))
                self.sqlCommand("delete from songs where song_id = %d" % (sel.songID))
                self["list"].removeItem(self["list"].getCurrentIndex())
                self.clearCache()

    def addSongToPlaylist(self):
        playList = self.getPlayList()
        if len(playList):
            self.session.openWithCallback(self.addSongToPlaylistCallback, ChoiceBox, list=playList)
        else:
            self.session.openWithCallback(self.createPlaylistConfirmed, MessageBox, _("There are no playlists defined.\nDo you want to create a new playlist?"))

    def createPlaylistConfirmed(self, val):
        if val:
            self.createPlaylist()

    def addSongToPlaylistCallback(self, ret):
        if ret:
            sel = self.getCurrentSelection()
            if sel:
                self.sqlCommand("INSERT INTO Playlist_Songs (playlist_id,song_id) VALUES(%d,%d);" % (ret[1], sel.songID))
                self.clearCache()

    def createPlaylist(self):
        self.session.openWithCallback(self.createPlaylistFinished, VirtualKeyBoard, title=_("Enter name for playlist"))

    def createPlaylistFinished(self, text=None):
        if text:
            self.sqlCommand('INSERT INTO Playlists (playlist_text) VALUES("%s");' % (text))
            self.clearCache()
            self.menu_pressed()

    def searchInIDreamDatabase(self):
        options = [(_("search for title"), 1),
            (_("search for artist"), 2),
            (_("search for album"), 3),
            (_("search in all of them"), 4), ]
        self.session.openWithCallback(self.enterSearchText, ChoiceBox, list=options)

    def enterSearchText(self, ret):
        if ret:
            self.session.openWithCallback(boundFunction(self.enterSearchTextFinished, ret[1]), VirtualKeyBoard, title=_("Enter search-text"))

    def enterSearchTextFinished(self, searchType, searchText=None):
        if searchText:
            search = "%" + searchText + "%"
            if searchType == 1:
                sql_where = "where title like '%s'" % search
                text = _('Search results for "%s" in all titles') % searchText
            elif searchType == 2:
                sql_where = "where artists.artist like '%s'" % search
                text = _('Search results for "%s" in all artists') % searchText
            elif searchType == 3:
                sql_where = "where album_text like '%s'" % search
                text = _('Search results for "%s" in all albums') % searchText
            else:
                sql_where = "where (title like '%s' or artists.artist like '%s' or album_text like '%s')" % (search, search, search)
                text = _('Search results for "%s" in title, artist or album') % searchText
            self.setButtons(red=True, yellow=True, blue=True)
            oldmode = self.mode
            self.mode = 20
            self["list"].setMode(self.mode)
            self.buildSearchSongList(sql_where, text, oldmode, True)

    def keyNumber_pressed(self, number):
        if number == 0 and self.mode != 0:
            self["list"].moveToIndex(0)
            self.ok()

    def ok(self):
        sel = self.getCurrentSelection()
        if sel is None:
            return
        if sel.mode == 99:
            self.green_pressed()
        else:
            self.mode = sel.mode
            self["list"].setMode(self.mode)
            if sel.navigator and len(self.cacheList) > 0:
                cache = self.cacheList.pop()
            else:
                cache = CacheList(cache=False, index=-1)
            if sel.navigator:
                self["headertext"].setText(cache.headertext)
                if cache.cache:
                    self["list"].setList(cache.listview)
                    self.LastMethod = MethodArguments(method=cache.methodarguments.method, arguments=cache.methodarguments.arguments)
                else:
                    cache.methodarguments.method(**cache.methodarguments.arguments)
                self["list"].moveToIndex(cache.index)
            if self.mode == 0:
                self.setButtons()
                if not sel.navigator:
                    self.buildMainMenuList()
            elif self.mode == 1:
                self.setButtons(red=True)
                if not sel.navigator:
                    self.buildPlaylistList(addToCache=True)
            elif self.mode == 2:
                self.setButtons(red=True, green=True, yellow=True, blue=True)
                if not sel.navigator:
                    self.buildPlaylistSongList(playlistID=sel.playlistID, addToCache=True)
            elif self.mode == 4:
                self.setButtons(red=True)
                if not sel.navigator:
                    self.buildArtistList(addToCache=True)
            elif self.mode == 5:
                self.setButtons(red=True)
                if not sel.navigator:
                    self.buildArtistAlbumList(sel.artistID, addToCache=True)
            elif self.mode == 6:
                self.setButtons(red=True, green=True, yellow=True)
                if not sel.navigator:
                    self.buildAlbumSongList(albumID=sel.albumID, mode=5, addToCache=True)
            elif self.mode == 7:
                self.setButtons(red=True)
                if not sel.navigator:
                    self.buildAlbumList(addToCache=True)
            elif self.mode == 8:
                self.setButtons(red=True, green=True, yellow=True)
                if not sel.navigator:
                    self.buildAlbumSongList(albumID=sel.albumID, mode=7, addToCache=True)
            elif self.mode == 10:
                self.setButtons(red=True, green=True, yellow=True, blue=True)
                if not sel.navigator:
                    self.buildSongList(addToCache=True)
            elif self.mode == 13:
                self.setButtons(red=True)
                if not sel.navigator:
                    self.buildGenreList(addToCache=True)
            elif self.mode == 14:
                self.setButtons(red=True, green=True, yellow=True, blue=True)
                if not sel.navigator:
                    self.buildGenreSongList(genreID=sel.genreID, addToCache=True)
            elif self.mode == 18 or self.mode == 19:
                if self.mode == 18:
                    self.setButtons(red=True, green=True, yellow=True)
                if self.mode == 19:
                    self.setButtons(red=True, green=True, blue=True)
                if not sel.navigator:
                    self.red_pressed()  # back to main menu --> normally that can not be happened
            elif self.mode == 20:
                self.setButtons(red=True, green=True, yellow=True, blue=True)
                if not sel.navigator:
                    self.red_pressed()  # back to main menu --> normally that can not be happened

    def buildPlaylistList(self, addToCache):
        if addToCache:
            self.cacheList.append(CacheList(index=self["list"].getCurrentIndex(), listview=self["list"].getList(), headertext=self["headertext"].getText(), methodarguments=self.LastMethod))
        arguments = {}
        arguments["addToCache"] = False
        self.LastMethod = MethodArguments(method=self.buildPlaylistList, arguments=arguments)
        self["headertext"].setText(_("Playlists"))
        connection = OpenDatabase()
        if connection is not None:
            connection.text_factory = str
            cursor = connection.cursor()
            playlistList = []
            playlistList.append((Item(text=_("[back]"), mode=0, navigator=True),))
            cursor.execute("select playlists.playlist_id, playlist_text, count(Playlist_Songs.playlist_id) from playlists left outer join Playlist_Songs on playlists.playlist_id = Playlist_Songs.playlist_id group by playlists.playlist_id order by playlists.playlist_text;")
            for row in cursor:
                playlistList.append((Item(text="%s (%d)" % (row[1], row[2]), mode=2, playlistID=row[0]),))
            cursor.close()
            connection.close()
            self["list"].setList(playlistList)
            if len(playlistList) > 1:
                self["list"].moveToIndex(1)

    def buildPlaylistSongList(self, playlistID, addToCache):
        if addToCache:
            self.cacheList.append(CacheList(index=self["list"].getCurrentIndex(), listview=self["list"].getList(), headertext=self["headertext"].getText(), methodarguments=self.LastMethod))
        arguments = {}
        arguments["playlistID"] = playlistID
        arguments["addToCache"] = False
        self.LastMethod = MethodArguments(method=self.buildPlaylistSongList, arguments=arguments)
        connection = OpenDatabase()
        if connection is not None:
            connection.text_factory = str
            cursor = connection.cursor()
            playlistSongList = []
            playlistSongList.append((Item(text=_("[back]"), mode=1, navigator=True),))
            cursor.execute("select songs.song_id, title, artists.artist, filename, songs.artist_id, bitrate, length, genre_text, track, date, album_text, songs.Album_id from songs inner join artists on songs.artist_id = artists.artist_id inner join Album on songs.Album_id = Album.Album_id inner join genre on songs.genre_id = genre.genre_id inner join playlist_songs on songs.song_id = playlist_songs.song_id where playlist_songs.playlist_id =  %d order by playlist_songs.id;" % (playlistID))
            for row in cursor:
                playlistSongList.append((Item(mode=99, songID=row[0], title=row[1], artist=row[2], filename=row[3], artistID=row[4], bitrate=row[5], length=row[6], genre=row[7], track=row[8], date=row[9], album=row[10], albumID=row[11], playlistID=playlistID),))
            cursor.execute("SELECT playlist_text from playlists where playlist_id = %d;" % playlistID)
            row = cursor.fetchone()
            self["headertext"].setText(_("Playlist (%s) -> Song List") % row[0])
            cursor.close()
            connection.close()
            self["list"].setList(playlistSongList)
            if len(playlistSongList) > 1:
                self["list"].moveToIndex(1)

    def buildGenreList(self, addToCache):
        if addToCache:
            self.cacheList.append(CacheList(index=self["list"].getCurrentIndex(), listview=self["list"].getList(), headertext=self["headertext"].getText(), methodarguments=self.LastMethod))
        arguments = {}
        arguments["addToCache"] = False
        self.LastMethod = MethodArguments(method=self.buildGenreList, arguments=arguments)
        self["headertext"].setText(_("Genre List"))
        connection = OpenDatabase()
        if connection is not None:
            connection.text_factory = str
            cursor = connection.cursor()
            genreList = []
            genreList.append((Item(text=_("[back]"), mode=0, navigator=True),))
            cursor.execute("select Genre.genre_id,Genre.Genre_text, count(*) from songs inner join Genre on songs.genre_id = Genre.Genre_id group by songs.Genre_id order by Genre.Genre_text;")
            for row in cursor:
                genreList.append((Item(text="%s (%d)" % (row[1], row[2]), mode=14, genreID=row[0]),))
            cursor.close()
            connection.close()
            self["list"].setList(genreList)
            if len(genreList) > 1:
                self["list"].moveToIndex(1)

    def buildGenreSongList(self, genreID, addToCache):
        if addToCache:
            self.cacheList.append(CacheList(index=self["list"].getCurrentIndex(), listview=self["list"].getList(), headertext=self["headertext"].getText(), methodarguments=self.LastMethod))
        arguments = {}
        arguments["genreID"] = genreID
        arguments["addToCache"] = False
        self.LastMethod = MethodArguments(method=self.buildGenreSongList, arguments=arguments)
        connection = OpenDatabase()
        if connection is not None:
            connection.text_factory = str
            cursor = connection.cursor()
            genreSongList = []
            genreSongList.append((Item(text=_("[back]"), mode=13, navigator=True),))
            cursor.execute("select song_id, title, artists.artist, filename, songs.artist_id, bitrate, length, genre_text, track, date, album_text, songs.Album_id from songs inner join artists on songs.artist_id = artists.artist_id inner join Album on songs.Album_id = Album.Album_id inner join genre on songs.genre_id = genre.genre_id where songs.genre_id = %d order by title, filename;" % (genreID))
            for row in cursor:
                genreSongList.append((Item(mode=99, songID=row[0], title=row[1], artist=row[2], filename=row[3], artistID=row[4], bitrate=row[5], length=row[6], genre=row[7], track=row[8], date=row[9], album=row[10], albumID=row[11], genreID=genreID),))
            cursor.execute("SELECT genre_text from genre where genre_ID = %d;" % genreID)
            row = cursor.fetchone()
            self["headertext"].setText(_("Genre (%s) -> Song List") % row[0])
            cursor.close()
            connection.close()
            self["list"].setList(genreSongList)
            if len(genreSongList) > 1:
                self["list"].moveToIndex(1)

    def setButtons(self, red=False, green=False, yellow=False, blue=False):
        if red:
            self["key_red"].setText(_("Main Menu"))
        else:
            self["key_red"].setText("")
        if green:
            self["key_green"].setText(_("Play"))
        else:
            self["key_green"].setText("")
        if yellow:
            self["key_yellow"].setText(_("All Artists"))
        else:
            self["key_yellow"].setText("")
        if blue:
            self["key_blue"].setText(_("Show Album"))
        else:
            self["key_blue"].setText("")

    def info_pressed(self):
        self.startMerlinPlayerScreenTimer.stop()
        if self.player is not None:
            if self.player.songList:
                self.session.execDialog(self.player)

    def green_pressed(self):
        try:
            sel = self["list"].l.getCurrentSelection()[0]
        except:
            sel = None
        if sel is None:
            return
        if sel.songID != 0:
            if self.player is not None:
                self.session.deleteDialog(self.player)
                self.player = None
            self.startMerlinPlayerScreenTimer.stop()
            self.player = self.session.instantiateDialog(MerlinMusicPlayer2Screen, self["list"].getList()[1:], self["list"].getCurrentIndex() -1, True, self.currentService, self.serviceList)
            self.session.execDialog(self.player)

    def red_pressed(self):
        self.cacheList = []
        self.setButtons()
        self.mode = 0
        self["list"].setMode(self.mode)
        self.buildMainMenuList()

    def yellow_pressed(self):
        try:
            sel = self["list"].l.getCurrentSelection()[0]
        except:
            return
        if sel.artistID != 0:
            oldmode = self.mode
            self.mode = 19
            self.setButtons(red=True, green=True, blue=True)
            self["list"].setMode(self.mode)
            self.buildArtistSongList(artistID=sel.artistID, mode=oldmode, addToCache=True)

    def blue_pressed(self):
        try:
            sel = self["list"].l.getCurrentSelection()[0]
        except:
            return
        if sel.albumID != 0:
            self.setButtons(red=True, green=True, yellow=True)
            oldmode = self.mode
            self.mode = 18
            self["list"].setMode(self.mode)
            self.buildAlbumSongList(albumID=sel.albumID, mode=oldmode, addToCache=True)

    def buildSongList(self, addToCache):
        if addToCache:
            self.cacheList.append(CacheList(index=self["list"].getCurrentIndex(), listview=self["list"].getList(), headertext=self["headertext"].getText(), methodarguments=self.LastMethod))
        arguments = {}
        arguments["addToCache"] = False
        self.LastMethod = MethodArguments(method=self.buildSongList,  arguments=arguments)
        self["headertext"].setText(_("All Songs"))
        connection = OpenDatabase()
        if connection is not None:
            connection.text_factory = str
            cursor = connection.cursor()
            SongList = []
            SongList.append((Item(text=_("[back]"), mode=0, navigator=True),))
            cursor.execute("select song_id, title, artists.artist, filename, songs.artist_id, bitrate, length, genre_text, track, date, album_text, songs.Album_id from songs inner join artists on songs.artist_id = artists.artist_id inner join Album on songs.Album_id = Album.Album_id inner join genre on songs.genre_id = genre.genre_id order by title, filename;")
            for row in cursor:
                SongList.append((Item(mode=99, songID=row[0], title=row[1], artist=row[2], filename=row[3], artistID=row[4], bitrate=row[5], length=row[6], genre=row[7], track=row[8], date=row[9], album=row[10], albumID=row[11]),))
            cursor.close()
            connection.close()
            self["list"].setList(SongList)
            if len(SongList) > 1:
                self["list"].moveToIndex(1)

    def buildSearchSongList(self, sql_where, headerText, mode, addToCache):
        if addToCache:
            self.cacheList.append(CacheList(index=self["list"].getCurrentIndex(), listview=self["list"].getList(), headertext=self["headertext"].getText(), methodarguments=self.LastMethod))
        arguments = {}
        arguments["sql_where"] = sql_where
        arguments["headerText"] = headerText
        arguments["mode"] = mode
        arguments["addToCache"] = False
        self.LastMethod = MethodArguments(method=self.buildSearchSongList, arguments=arguments)
        self["headertext"].setText(headerText)
        connection = OpenDatabase()
        if connection is not None:
            connection.text_factory = str
            cursor = connection.cursor()
            SongList = []
            SongList.append((Item(text=_("[back]"), mode=mode, navigator=True),))
            cursor.execute("select song_id, title, artists.artist, filename, songs.artist_id, bitrate, length, genre_text, track, date, album_text, songs.Album_id from songs inner join artists on songs.artist_id = artists.artist_id inner join Album on songs.Album_id = Album.Album_id inner join genre on songs.genre_id = genre.genre_id %s order by title, filename;" % sql_where)
            for row in cursor:
                SongList.append((Item(mode=99, songID=row[0], title=row[1], artist=row[2], filename=row[3], artistID=row[4], bitrate=row[5], length=row[6], genre=row[7], track=row[8], date=row[9], album=row[10], albumID=row[11]),))
            cursor.close()
            connection.close()
            self["list"].setList(SongList)
            if len(SongList) > 1:
                self["list"].moveToIndex(1)


    def buildArtistSongList(self, artistID, mode, addToCache):
        if addToCache:
            self.cacheList.append(CacheList(index=self["list"].getCurrentIndex(), listview=self["list"].getList(), headertext=self["headertext"].getText(), methodarguments=self.LastMethod))
        arguments = {}
        arguments["artistID"] = artistID
        arguments["mode"] = mode
        arguments["addToCache"] = False
        self.LastMethod = MethodArguments(method=self.buildArtistSongList, arguments=arguments)
        connection = OpenDatabase()
        if connection is not None:
            connection.text_factory = str
            cursor = connection.cursor()
            artistSongList = []
            artistSongList.append((Item(text=_("[back]"), mode=mode, navigator=True),))
            cursor.execute("select song_id, title, artists.artist, filename, bitrate, length, genre_text, track, date, album_text, songs.Album_id from songs inner join artists on songs.artist_id = artists.artist_id inner join Album on songs.Album_id = Album.Album_id inner join genre on songs.genre_id = genre.genre_id where songs.artist_id = %d order by Album.album_text, tracknumber, filename;" % (artistID))
            for row in cursor:
                artistSongList.append((Item(mode=99, songID=row[0], title=row[1], artist=row[2], filename=row[3], bitrate=row[4], length=row[5], genre=row[6], track=row[7], date=row[8], album=row[9], albumID=row[10], artistID=artistID),))
            cursor.execute("SELECT artist from artists where artist_ID = %d;" % artistID)
            row = cursor.fetchone()
            self["headertext"].setText(_("Artist (%s) -> Song List") % row[0])
            cursor.close()
            connection.close()
            self["list"].setList(artistSongList)
            if len(artistSongList) > 1:
                self["list"].moveToIndex(1)

    def buildAlbumSongList(self, albumID, mode, addToCache):
        if addToCache:
            self.cacheList.append(CacheList(index=self["list"].getCurrentIndex(), listview=self["list"].getList(), headertext=self["headertext"].getText(), methodarguments=self.LastMethod))
        arguments = {}
        arguments["albumID"] = albumID
        arguments["mode"] = mode
        arguments["addToCache"] = False
        self.LastMethod = MethodArguments(method=self.buildAlbumSongList, arguments=arguments)
        connection = OpenDatabase()
        if connection is not None:
            connection.text_factory = str
            cursor = connection.cursor()
            albumSongList = []
            albumSongList.append((Item(text=_("[back]"), mode=mode, navigator=True),))
            cursor.execute("select song_id, title, artists.artist, filename, songs.artist_id, bitrate, length, genre_text, track, date, album_text from songs inner join artists on songs.artist_id = artists.artist_id inner join Album on songs.Album_id = Album.Album_id inner join genre on songs.genre_id = genre.genre_id where songs.album_id = %d order by tracknumber, filename;" % (albumID))
            for row in cursor:
                albumSongList.append((Item(mode=99, songID=row[0], title=row[1], artist=row[2], filename=row[3], artistID=row[4], bitrate=row[5], length=row[6], genre=row[7], track=row[8], date=row[9], album=row[10], albumID=albumID),))
            cursor.execute("SELECT album_text from album where album_ID = %d;" % albumID)
            row = cursor.fetchone()
            self["headertext"].setText(_("Album (%s) -> Song List") % row[0])
            cursor.close()
            connection.close()
            self["list"].setList(albumSongList)
            if len(albumSongList) > 1:
                self["list"].moveToIndex(1)

    def buildMainMenuList(self, addToCache=True):
        arguments = {}
        arguments["addToCache"] = True
        self.LastMethod = MethodArguments(method=self.buildMainMenuList, arguments=arguments)
        self["headertext"].setText(_("iDream Main Menu"))
        mainMenuList = []
        connection = OpenDatabase()
        if connection is not None:
            connection.text_factory = str
            cursor = connection.cursor()
            # 1. Playlists
            cursor.execute("SELECT COUNT (*) FROM playlists;")
            row = cursor.fetchone()
            mainMenuList.append((Item(text=_("Playlists (%d)") % row[0], mode=1),))
            # 2. Artists
            cursor.execute("SELECT COUNT (*) FROM artists;")
            row = cursor.fetchone()
            mainMenuList.append((Item(text=_("Artists (%d)") % row[0], mode=4),))
            # 3. Albums
            cursor.execute("SELECT COUNT (DISTINCT album_text) FROM album;")
            row = cursor.fetchone()
            mainMenuList.append((Item(text=_("Albums (%d)") % row[0], mode=7),))
            # 4. Songs
            cursor.execute("SELECT COUNT (*) FROM songs;")
            row = cursor.fetchone()
            mainMenuList.append((Item(text=_("Songs (%d)") % row[0], mode=10),))
            # 5. Genres
            cursor.execute("SELECT COUNT (*) FROM genre;")
            row = cursor.fetchone()
            mainMenuList.append((Item(text=_("Genres (%d)") % row[0], mode=13),))
            cursor.close()
            connection.close()
            self["list"].setList(mainMenuList)
            self["list"].moveToIndex(0)

    def buildArtistList(self, addToCache):
        if addToCache:
            self.cacheList.append(CacheList(index=self["list"].getCurrentIndex(), listview=self["list"].getList(), headertext=self["headertext"].getText(), methodarguments=self.LastMethod))
        arguments = {}
        arguments["addToCache"] = False
        self.LastMethod = MethodArguments(method=self.buildArtistList, arguments=arguments)
        self["headertext"].setText(_("Artists List"))
        connection = OpenDatabase()
        if connection is not None:
            connection.text_factory = str
            cursor = connection.cursor()
            artistList = []
            artistList.append((Item(text=_("[back]"), mode=0, navigator=True),))
            cursor.execute("SELECT artists.artist_id,artists.artist, count (distinct album.album_text) FROM songs INNER JOIN artists ON songs.artist_id = artists.artist_id inner join album on songs.album_id =  album.album_id GROUP BY songs.artist_id ORDER BY artists.artist;")
            for row in cursor:
                artistList.append((Item(text="%s (%d)" % (row[1], row[2]), mode=5, artistID=row[0]),))
            cursor.close()
            connection.close()
            self["list"].setList(artistList)

    def buildArtistAlbumList(self, ArtistID, addToCache):
        if addToCache:
            self.cacheList.append(CacheList(index=self["list"].getCurrentIndex(), listview=self["list"].getList(), headertext=self["headertext"].getText(), methodarguments=self.LastMethod))
        arguments = {}
        arguments["ArtistID"] = ArtistID
        arguments["addToCache"] = False
        self.LastMethod = MethodArguments(method=self.buildArtistAlbumList, arguments=arguments)
        connection = OpenDatabase()
        if connection is not None:
            connection.text_factory = str
            cursor = connection.cursor()
            albumArtistList = []
            albumArtistList.append((Item(text=_("[back]"), mode=4, navigator=True),))
            cursor.execute("select Album.Album_id,Album.Album_text from songs inner join Album on songs.Album_id = Album.Album_id where songs.artist_id = %d group by songs.Album_id order by Album.Album_text;" % ArtistID)
            for row in cursor:
                cursor2 = connection.cursor()
                cursor2.execute("select count(song_id) from songs where album_id = %d;" % row[0])
                row2 = cursor2.fetchone()
                albumArtistList.append((Item(text="%s (%d)" % (row[1], row2[0]), mode=6, albumID=row[0], artistID=ArtistID),))
                cursor2.close()
            cursor.execute("SELECT artist from artists where artist_ID = %d;" % ArtistID)
            row = cursor.fetchone()
            self["headertext"].setText(_("Artist (%s) -> Album List") % row[0])
            cursor.close()
            connection.close()
            self["list"].setList(albumArtistList)
            if len(albumArtistList) > 1:
                self["list"].moveToIndex(1)

    def buildAlbumList(self, addToCache):
        if addToCache:
            self.cacheList.append(CacheList(index=self["list"].getCurrentIndex(), listview=self["list"].getList(), headertext=self["headertext"].getText(), methodarguments=self.LastMethod))
        arguments = {}
        arguments["addToCache"] = False
        self.LastMethod = MethodArguments(method=self.buildAlbumList, arguments=arguments)
        self["headertext"].setText(_("Albums List"))
        connection = OpenDatabase()
        if connection is not None:
            connection.text_factory = str
            cursor = connection.cursor()
            albumList = []
            albumList.append((Item(text=_("[back]"), mode=0, navigator=True),))
            cursor.execute("select Album.Album_id,Album.Album_text, count(*) from songs inner join Album on songs.Album_id = Album.Album_id group by songs.Album_id order by Album.Album_text;")
            for row in cursor:
                albumList.append((Item(text="%s (%d)" % (row[1], row[2]), mode=8, albumID=row[0]),))
            cursor.close()
            connection.close()
            self["list"].setList(albumList)
            if len(albumList) > 1:
                self["list"].moveToIndex(1)

    def startRun(self):
        if pathToDatabase.isRunning:
            self.showScanner = eTimer()
            self.showScanner_conn = self.showScanner.timeout.connect(self.showScannerCallback)
            self.showScanner.start(0, 1)
        else:
            if config.plugins.merlinmusicplayer2.startlastsonglist.value:
                self.startPlayerTimer = eTimer()
                self.startPlayerTimer_conn = self.startPlayerTimer.timeout.connect(self.startPlayerTimerCallback)
                self.startPlayerTimer.start(0, 1)
            self.mode = 0
            self["list"].setMode(self.mode)
            self.buildMainMenuList()

    def showScannerCallback(self):
        self.session.openWithCallback(self.filesAdded, iDreamAddToDatabaseScreen, None)

    def startPlayerTimerCallback(self):
        connection = OpenDatabase()
        if connection is not None:
            connection.text_factory = str
            cursor = connection.cursor()
            iDreamMode = False
            SongList = []
            cursor.execute("select song_id, filename, title, artist, album, genre, bitrate, length,  track, date, PTS from CurrentSongList;")
            for row in cursor:
                SongList.append((Item(songID=row[0], text=os_path.basename(row[1]), filename=row[1], title=row[2], artist=row[3], album=row[4], genre=row[5],  bitrate=row[6], length=row[7], track=row[8], date=row[9], PTS=row[10], join=False),))
                if row[0] != 0:
                    iDreamMode = True
            cursor.close()
            connection.close()
            if self.player is not None:
                self.session.deleteDialog(self.player)
                self.player = None
            self.startMerlinPlayerScreenTimer.stop()
            count = len(SongList)
            if count:
                # just to be sure, check the index , it's critical
                index = config.plugins.merlinmusicplayer2.lastsonglistindex.value
                if index >= count:
                    index = 0
                self.player = self.session.instantiateDialog(MerlinMusicPlayer2Screen, SongList, index, iDreamMode, self.currentService, self.serviceList)
                self.session.execDialog(self.player)

    def config(self):
        self.startMerlinPlayerScreenTimer.stop()
        self.session.openWithCallback(self.setupFinished, MerlinMusicPlayer2Setup, True)

    def setupFinished(self, result):
        if result:
            self.red_pressed()

    def stopPlayingAndAppendFileToSongList(self):
        self.startMerlinPlayerScreenTimer.stop()
        if self.player is not None:
            self.session.deleteDialog(self.player)
            self.player = None
        self.appendFileToSongList()
        self.startMerlinPlayerScreenTimer.start(START_MERLIN_PLAYER_SCREEN_TIMER_VALUE)

    def appendFileToSongList(self):
        SongList = []
        playerAvailable = self.player is not None and self.player.songList
        sel = self.getCurrentSelection()
        if sel:
            if playerAvailable:
                self.player.songList.append((sel,))
                self.player.origSongList.append((sel,))
            else:
                SongList.append((sel,))
            if not playerAvailable:
                if self.player is not None:
                    self.session.deleteDialog(self.player)
                    self.player = None
                self.player = self.session.instantiateDialog(MerlinMusicPlayer2Screen, SongList, 0, True, self.currentService, self.serviceList)
                self.player.playSong(self.player.songList[self.player.currentIndex][0].filename)
                self.player.init = 1
            else:
                self.player["nextTitle"].setText(self.player.getNextTitle())
                self.session.open(MessageBox, _("%s\nappended to songlist") % sel.title, type=MessageBox.TYPE_INFO, timeout=3)

    def insertFileToSongList(self):
        sel = self.getCurrentSelection()
        if sel:
            if self.player is not None and self.player.songList:
                index = self.player.currentIndex
                self.player.songList.insert(index+1, (sel, ))
                self.player.origSongList.insert(index+1, (sel,))
                self.player["nextTitle"].setText(self.player.getNextTitle())
                self.session.open(MessageBox, _("%s\ninserted and will be played as next song") % sel.title, type=MessageBox.TYPE_INFO, timeout=3)
            else:
                self.appendFileToSongList()

    def Error(self, error=None):
        if error is not None:
            self["list"].hide()
            self["statustext"].setText(str(error.getErrorMessage()))

    def closing(self):
        self.close()

    def __onClose(self):
        self.session.nav.SleepTimer.on_state_change.remove(self.sleepTimerEntryOnStateChange)
        self.autoActivationKeyPressedActionSlot = None
        self.startMerlinPlayerScreenTimer.stop()
        if self.player is not None:
            self.player.closePlayer()
            self.session.deleteDialog(self.player)
            self.player = None
            self.session.nav.stopService()
        if self.serviceList is None:
            self.session.nav.playService(self.currentService)
        else:
            current = ServiceReference(self.serviceList.getCurrentSelection())
            self.session.nav.playService(current.ref)

    def lcdUpdate(self):
        self.startMerlinPlayerScreenTimer.start(START_MERLIN_PLAYER_SCREEN_TIMER_VALUE)
        try:
            count = self["list"].getItemCount()
            index = self["list"].getCurrentIndex()
            iDreamList = self["list"].getList()
            self.summaries.setText(iDreamList[index][0].title or iDreamList[index][0].text, 1)
            # voheriges
            index -= 1
            if index < 0:
                index = count
            self.summaries.setText(iDreamList[index][0].title or iDreamList[index][0].text, 3)
            # naechstes
            index = self["list"].getCurrentIndex() + 1
            if index > count:
                index = 0
            self.summaries.setText(iDreamList[index][0].title or iDreamList[index][0].text, 4)
        except:
            pass

    def createSummary(self):
        return MerlinMusicPlayerLCDScreenText


class iDreamList(GUIComponent, object):
    SKIN_COMPONENT_KEY = "MerliniDreamList"
    SKIN_COMPONENT_LINE_SPACING = "lineSpacing"
    SKIN_COMPONENT_LISTBIG_HEIGHT = "listbigHeight"
    SKIN_COMPONENT_TEXT_HEIGHT = "textHeight"
    SKIN_COMPONENT_TEXT_WIDTH = "textWidth"
    SKIN_COMPONENT_TEXT2_WIDTH = "text2Width"

    def buildEntry(self, item):
        width = self.l.getItemSize().width()
        sizes = componentSizes[iDreamList.SKIN_COMPONENT_KEY]
        lineSpacing = sizes.get(iDreamList.SKIN_COMPONENT_LINE_SPACING, 5)
        textHeight = sizes.get(iDreamList.SKIN_COMPONENT_TEXT_HEIGHT, 22)
        textWidth = sizes.get(iDreamList.SKIN_COMPONENT_TEXT_WIDTH, 100)
        text2Width = sizes.get(iDreamList.SKIN_COMPONENT_TEXT_WIDTH, 200)
        res = [None]
        if self.displaySongMode:
            if item.navigator:
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 0, 0, width, textHeight, 0, RT_HALIGN_CENTER|RT_VALIGN_CENTER, "%s" % item.text))
            else:
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 0, 0, width - textWidth, textHeight, 0, RT_HALIGN_LEFT|RT_VALIGN_CENTER, "%s - %s" % (item.title, item.artist)))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, width - textWidth, 2, textWidth, textHeight, 1, RT_HALIGN_RIGHT|RT_VALIGN_CENTER, "%s" % item.track))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 0, textHeight+lineSpacing, width -text2Width, textHeight, 1, RT_HALIGN_LEFT|RT_VALIGN_CENTER, "%s%s" % (item.album, item.date)))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, width - text2Width, textHeight+lineSpacing, text2Width, textHeight, 1, RT_HALIGN_RIGHT|RT_VALIGN_CENTER, "%s" % item.length))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 0, textHeight+textHeight, width -text2Width, textHeight, 1, RT_HALIGN_LEFT|RT_VALIGN_CENTER, "%s" % item.genre))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, width - text2Width, textHeight+textHeight, text2Width, textHeight, 1, RT_HALIGN_RIGHT|RT_VALIGN_CENTER, "%s" % item.bitrate))
        else:
            if item.navigator:
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 0, 0, width, textHeight, 0, RT_HALIGN_CENTER|RT_VALIGN_CENTER, "%s" % item.text))
            else:
                if item.PTS is None:
                    res.append((eListboxPythonMultiContent.TYPE_TEXT, 0, 0, width, textHeight, 0, RT_HALIGN_LEFT|RT_VALIGN_CENTER, "%s" % item.text))
                else:
                    res.append((eListboxPythonMultiContent.TYPE_TEXT, 0, 0, width, textHeight, 0, RT_HALIGN_LEFT|RT_VALIGN_CENTER, "%s" % item.title))
        return res

    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setBuildFunc(self.buildEntry)
        tlf = TemplatedListFonts()
        self.l.setFont(0, gFont(tlf.face(tlf.MEDIUM), tlf.size(tlf.MEDIUM)))
        self.l.setFont(1, gFont(tlf.face(tlf.SMALLER), tlf.size(tlf.SMALLER)))
        self.onSelectionChanged = []
        self.mode = 0
        self.displaySongMode = False
        self.list = []
        self.itemCount = 0

    def connectSelChanged(self, fnc):
        if fnc not in self.onSelectionChanged:
            self.onSelectionChanged.append(fnc)

    def disconnectSelChanged(self, fnc):
        if fnc in self.onSelectionChanged:
            self.onSelectionChanged.remove(fnc)

    def selectionChanged(self):
        for x in self.onSelectionChanged:
            x()

    def getCurrent(self):
        cur = self.l.getCurrentSelection()
        return cur and cur[0]

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        self.selectionChanged_conn = instance.selectionChanged.connect(self.selectionChanged)

    def preWidgetRemove(self, instance):
        instance.setContent(None)
        self.selectionChanged_conn = None

    def moveToIndex(self, index):
        self.instance.moveSelectionTo(index)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    currentIndex = property(getCurrentIndex, moveToIndex)
    currentSelection = property(getCurrent)

    def setList(self, list):
        self.list = list
        self.l.setList(list)
        self.itemCount = len(self.list) - 1

    def getItemCount(self):
        return self.itemCount

    def getList(self):
        return self.list

    def removeItem(self, index):
        del self.list[index]
        self.l.entryRemoved(index)

    def getDisplaySongMode(self):
        return self.displaySongMode

    def setMode(self, mode):
        self.mode = mode
        if mode == 2 or mode == 6 or mode == 8 or mode == 10 or mode == 18 or mode == 19 or mode == 14 or mode == 20:
            self.displaySongMode = True
            sizes = componentSizes[iDreamList.SKIN_COMPONENT_KEY]
            listbigHeight = sizes.get(iDreamList.SKIN_COMPONENT_LISTBIG_HEIGHT, 68)
            self.l.setItemHeight(listbigHeight)
        else:
            self.displaySongMode = False
            self.l.setItemHeight(componentSizes.itemHeight(self.SKIN_COMPONENT_KEY, 22))


class SelectPath2(MerlinMusicPlayerBase, Screen):

    IS_DIALOG = True

    def __init__(self, session, initDir):
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        inhibitDirs = ["/bin", "/boot", "/dev", "/lib", "/proc", "/sbin", "/sys", "/usr", "/var"]
        inhibitMounts = []
        self["filelist"] = FileList(initDir, showDirectories=True, showFiles=False, inhibitMounts=inhibitMounts, inhibitDirs=inhibitDirs)
        self["target"] = Label()
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions", "EPGSelectActions"],
        {
            "back": self.cancel,
            "left": self.left,
            "right": self.right,
            "up": self.up,
            "down": self.down,
            "ok": self.ok,
            "green": self.green,
            "red": self.cancel

        }, -1)
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("OK"))

    def cancel(self):
        self.close(None)

    def green(self):
        self.close(self["filelist"].getSelection()[0])

    def up(self):
        self["filelist"].up()
        self.updateTarget()

    def down(self):
        self["filelist"].down()
        self.updateTarget()

    def left(self):
        self["filelist"].pageUp()
        self.updateTarget()

    def right(self):
        self["filelist"].pageDown()
        self.updateTarget()

    def ok(self):
        if self["filelist"].canDescent():
            self["filelist"].descent()
            self.updateTarget()

    def updateTarget(self):
        currFolder = self["filelist"].getSelection()[0]
        if currFolder is not None:
            self["target"].setText(currFolder)
        else:
            self["target"].setText(_("Invalid Location"))


class MerlinMusicPlayer2LCDScreen(MerlinMusicPlayerBase, Screen):

    def __init__(self, session, parent):
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        self["PositionGauge"] = ServicePositionGauge(session.nav)
        self["cover"] = MerlinMusicPlayerWidget()
        self["visu"] = MerlinMusicPlayerWidget()
        self["rms0"] = MerlinMusicPlayerRMS()
        self["rms1"] = MerlinMusicPlayerRMS()
        self["rms2"] = MerlinMusicPlayerRMS()
        self["rms3"] = MerlinMusicPlayerRMS()
        self["text1"] = Label()
        self["text4"] = Label()

    def setText(self, text, line):
        if line == 1:
            self["text1"].setText(text)
        elif line == 4:
            self["text4"].setText(text)

    def updateCover(self, filename):
        self["cover"].setCover(filename)


class MerlinMusicPlayer2PicturesLCDScreen(MerlinMusicPlayer2LCDScreen):

    def __init__(self, session, parent):
        MerlinMusicPlayer2LCDScreen.__init__(self, session, parent)


class MerlinMusicPlayerLCDScreenText(MerlinMusicPlayerBase, Screen):

    def __init__(self, session, parent):
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        self["text1"] = Label()
        self["text3"] = Label()
        self["text4"] = Label()

    def setText(self, text, line):
        textleer = "    "
        text = text + textleer*10
        if line == 1:
            self["text1"].setText(text)
        elif line == 3:
            self["text3"].setText(text)
        elif line == 4:
            self["text4"].setText(text)


class MerlinMusicPlayer2Setup(MerlinMusicPlayerBase, Screen, ConfigListScreen):

    IS_DIALOG = True

    def __init__(self, session, databasePath):
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("OK"))

        self.list = []
        if HardwareInfo().get_device_name() not in ("one", "two"):
            self.list.append(getConfigListEntry(_("Use standard DMM music decoder (without visualizations)"), config.plugins.merlinmusicplayer2.hardwaredecoder))
            self.list.append(getConfigListEntry(_("Gapless playback (only when not using standard DMM decoder)"), config.plugins.merlinmusicplayer2.gapless))
            self.list.append(getConfigListEntry(_("Use alsasink (only when not using standard DMM decoder)"), config.plugins.merlinmusicplayer2.alsa))
        else:
            self.list.append(getConfigListEntry(_("Gapless playback"), config.plugins.merlinmusicplayer2.gapless))
        self.list.append(getConfigListEntry(_("Play last used songlist after starting"), config.plugins.merlinmusicplayer2.startlastsonglist))
        if databasePath:
            self.database = getConfigListEntry(_("iDream database path"), config.plugins.merlinmusicplayer2.databasepath)
            self.list.append(self.database)
        else:
            self.database = None
        self.list.append(getConfigListEntry(_("Use iTunes-images for cover art"), config.plugins.merlinmusicplayer2.usegoogleimage))
        self.googleimage = getConfigListEntry(_("iTunes-images path"), config.plugins.merlinmusicplayer2.googleimagepath)
        self.list.append(self.googleimage)
        self.list.append(getConfigListEntry(_("Activate screensaver"), config.plugins.merlinmusicplayer2.usescreensaver))
        self.list.append(getConfigListEntry(_("Wait for screensaver (in min)"), config.plugins.merlinmusicplayer2.screensaverwait))
        if HardwareInfo().get_device_name() in ("dm900", "dm920", "one", "two"):
            self.list.append(getConfigListEntry(_("Select screensaver view"), config.plugins.merlinmusicplayer2.screensaverselection))
        self.list.append(getConfigListEntry(_("Remember last path of filebrowser"), config.plugins.merlinmusicplayer2.rememberlastfilebrowserpath))
        self.defaultFileBrowserPath = getConfigListEntry(_("Filebrowser startup path"), config.plugins.merlinmusicplayer2.defaultfilebrowserpath)
        self.list.append(self.defaultFileBrowserPath)
        self.list.append(getConfigListEntry(_("Infobar timeout in seconds (for TV, video and pictures screens)"), config.plugins.merlinmusicplayer2.infobar_timeout))
        if HardwareInfo().get_device_name() not in ("one", "two"):
            self.list.append(getConfigListEntry(_("Show infobar on song-event change in tv screen"), config.plugins.merlinmusicplayer2.infobar_timeout_tv))
            self.list.append(getConfigListEntry(_("Show infobar on song-event change in video screen"), config.plugins.merlinmusicplayer2.infobar_timeout_video))
        self.list.append(getConfigListEntry(_("Show infobar on song-event change in picture screen"), config.plugins.merlinmusicplayer2.infobar_timeout_picture))
        self.list.append(getConfigListEntry(_("Display duration for pictures in seconds"), config.plugins.merlinmusicplayer2.picture_duration))
        self.list.append(getConfigListEntry(_("Activate Ken Burns effect for picure slideshow"), config.plugins.merlinmusicplayer2.kenburns))
        self.list.append(getConfigListEntry(_("Transition mode"), config.plugins.merlinmusicplayer2.transition_mode))
        self.list.append(getConfigListEntry(_("Enable default transition time for modes"), config.plugins.merlinmusicplayer2.transition_default_duration))
        self.list.append(getConfigListEntry(_("Transition time in milliseconds (if default is disabled)"), config.plugins.merlinmusicplayer2.transition_duration))
        self.list.append(getConfigListEntry(_("Scale to screen"), config.plugins.merlinmusicplayer2.picture_scale_to_screen))
        self.list.append(getConfigListEntry(_("Show radio background picture"), config.plugins.merlinmusicplayer2.usestandardradiobackground))
        self.list.append(getConfigListEntry(_("Show iDream in extended-pluginlist"), config.plugins.merlinmusicplayer2.idreamextendedpluginlist))
        self.list.append(getConfigListEntry(_("Show Merlin Music Player in extended-pluginlist"), config.plugins.merlinmusicplayer2.merlinmusicplayerextendedpluginlist))
        self.list.append(getConfigListEntry(_("Show iDream in mainmenu"), config.plugins.merlinmusicplayer2.idreammainmenu))
        self.list.append(getConfigListEntry(_("Show Merlin Music Player in mainmenu"), config.plugins.merlinmusicplayer2.merlinmusicplayermainmenu))
        ConfigListScreen.__init__(self, self.list, session)
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
        {
            "green": self.keySave,
            "cancel": self.keyClose,
            "ok": self.keySelect,
        }, -2)

    def keySelect(self):
        cur = self["config"].getCurrent()
        if cur == self.database:
            self.session.openWithCallback(self.pathSelectedDatabase, SelectPath2, config.plugins.merlinmusicplayer2.databasepath.value)
        elif cur == self.defaultFileBrowserPath:
            self.session.openWithCallback(self.pathSelectedFilebrowser, SelectPath2, config.plugins.merlinmusicplayer2.defaultfilebrowserpath.value)
        elif cur == self.googleimage:
            self.session.openWithCallback(self.pathSelectedGoogleImage, SelectPath2, config.plugins.merlinmusicplayer2.googleimagepath.value)

    def pathSelectedGoogleImage(self, res):
        if res is not None:
            config.plugins.merlinmusicplayer2.googleimagepath.value = res

    def pathSelectedDatabase(self, res):
        if res is not None:
            config.plugins.merlinmusicplayer2.databasepath.value = res

    def pathSelectedFilebrowser(self, res):
        if res is not None:
            config.plugins.merlinmusicplayer2.defaultfilebrowserpath.value = res

    def keySave(self):
        for x in self["config"].list:
            x[1].save()
        configfile.save()
        self.close(True)

    def keyClose(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close(False)


class MerlinMusicPlayer2FileList(MerlinMusicPlayerBase, Screen):

    def __init__(self, session, servicelist):
        self.session = session
        Screen.__init__(self, session)
        MerlinMusicPlayerBase.__init__(self)
        self["list"] = FileList(config.plugins.merlinmusicplayer2.defaultfilebrowserpath.value, showDirectories=True, showFiles=True, matchingPattern=".([aA][aA][cC]|[mM][pP]3|[mM][pP]2|[mM][pP]1|[mM]4[aA]|[fF][lL][aA][cC]|[oO][gG][gG]|[aA][iI][fF]|[aA][iI][fF][fF]|[wW][aA][vV]|[wW][mM][aA]|[aA][uU]|[mM][pP][cC]|[mM]3[uU]|[pP][lL][sS]|[cC][uU][eE])$", useServiceRef=False)
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions", "EPGSelectActions", "InfobarActions"],
        {
            "ok": self.ok,
            "back": self.closing,
            "input_date_time": self.menu_pressed,
            "info": self.info_pressed,
            "green": self.green_pressed,
            "up": self.moveup,
            "down": self.movedown,
            "right": self.moveright,
            "left": self.moveleft,
            "blue": self.appendFileToSongList,
            "yellow": self.insertFileToSongList,
            "red": self.stopPlayingAndAppendFileToSongList,
            "showRadio": self.showRadio,
            "showTv": self.showInternetRadioFavorites,
        }, -1)
        self.serviceList = servicelist
        self["headertext"] = Label()
        self.player = None
        self.onClose.append(self.__onClose)
        self.onLayoutFinish.append(self.startRun)
        self.onShown.append(self.updateTarget)
        self.currentService = self.session.nav.getCurrentlyPlayingServiceReference()
        self.session.nav.stopService()

        self.startMerlinPlayerScreenTimer = eTimer()
        self.startMerlinPlayerScreenTimer_conn = self.startMerlinPlayerScreenTimer.timeout.connect(self.info_pressed)

        self.closeTimer = eTimer()
        self.closeTimer_conn = self.closeTimer.timeout.connect(self.closeTimerTimeout)

        self.session.nav.SleepTimer.on_state_change.append(self.sleepTimerEntryOnStateChange)

        self.autoActivationKeyPressedActionSlot = eActionMap.getInstance().bindAction('', -0x7FFFFFFF, self.autoActivationKeyPressed)

        if config.plugins.merlinmusicplayer2.usestandardradiobackground.value:
            eMerlinMusicPlayer.getInstance().show_iFrame_Pic(config.misc.radiopic.value)
        else:
            eMerlinMusicPlayer.getInstance().show_iFrame_Pic(eEnv.resolve("${libdir}/enigma2/python/Plugins/Extensions/MerlinMusicPlayer2/images/background"))

    def sleepTimerEntryOnStateChange(self, timer):
        if timer.state == TimerEntry.StateEnded:
            self.close()

    def autoActivationKeyPressed(self, key=None, flag=None):
        self.startMerlinPlayerScreenTimer.stop()
        if self.instance.isVisible() and self.isEnabled():
            self.startMerlinPlayerScreenTimer.start(START_MERLIN_PLAYER_SCREEN_TIMER_VALUE)
        return 0

    def startRun(self):
        if config.plugins.merlinmusicplayer2.startlastsonglist.value:
            self.startPlayerTimer = eTimer()
            self.startPlayerTimer_conn = self.startPlayerTimer.timeout.connect(self.startPlayerTimerCallback)
            self.startPlayerTimer.start(0, 1)

    def startPlayerTimerCallback(self):
        try:  # so lame, but OperationalError: disk I/O error occurs too often
            connection = OpenDatabase()
            if connection is not None:
                connection.text_factory = str
                cursor = connection.cursor()
                iDreamMode = False
                SongList = []
                serviceHandler = eServiceCenter.getInstance()
                cursor.execute("select song_id, filename, title, artist, album, genre, bitrate, length,  track, date, PTS from CurrentSongList;")
                for row in cursor:
                    isDVB = False
                    if row[1].startswith("http://"):
                        text = row[2]
                        ref = eServiceReference(text)
                        if ref.valid():
                            info = serviceHandler.info(ref)
                            text = info and info.getName(ref) or "."
                            isDVB = True
                    else:
                        text = os_path.basename(row[1])
                    SongList.append((Item(songID=row[0], text=text, filename=row[1], title=row[2], artist=row[3], album=row[4], genre=row[5],  bitrate=row[6], length=row[7], track=row[8], date=row[9], PTS=row[10], isDVB=isDVB, join=False),))
                    if row[0] != 0:
                        iDreamMode = True
                cursor.close()
                connection.close()
                if self.player is not None:
                    self.session.deleteDialog(self.player)
                    self.player = None
                self.startMerlinPlayerScreenTimer.stop()
                count = len(SongList)
                if count:
                    # just to be sure, check the index , it's critical
                    index = config.plugins.merlinmusicplayer2.lastsonglistindex.value
                    if index >= count:
                        index = 0
                    self.player = self.session.instantiateDialog(MerlinMusicPlayer2Screen, SongList, index, iDreamMode, self.currentService, self.serviceList)
                    self.session.execDialog(self.player)
        except:
            self.session.open(MessageBox, _("Something went wrong while accessing the database."), type=MessageBox.TYPE_INFO, timeout=20)

    def readCUE(self, filename):
        SongList = []
        displayname = None
        try:
            cuefile = open(filename, "r")
        except IOError:
            return None
        import re
        performer_re = re.compile(r"""PERFORMER "(?P<performer>.*?)"(?:=\r\n|\r|\n|$)""")
        title_re = re.compile(r"""TITLE "(?P<title>.*?)"(?:=\r\n|\r|\n|$)""")
        filename_re = re.compile(r"""FILE "(?P<filename>.+?)".*(?:=\r\n|\r|\n|$)""", re.DOTALL)
        track_re = re.compile(r"""TRACK (?P<track_number>[^ ]+?)(?:[ ]+.*?)(?:=\r\n|\r|\n|$)""")
        index_re = re.compile(r"""INDEX (?P<index_nr>[^ ]+?)[ ]+(?P<track_index>[^ ]+?)(?:=\r\n|\r|\n|$)""")
        msts_re = re.compile("""^(?P<mins>[0-9]{1,}):(?P<secs>[0-9]{2}):(?P<ms>[0-9]{2})$""")
        songfilename = ""
        album = ""
        performer = ""
        title = ""
        pts = 0
        state = 0  # header
        for line in cuefile.readlines():
            entry = line.strip()
            m = filename_re.search(entry)
            if m:
                if m.group('filename')[0] == "/":
                    songfilename = m.group('filename')
                else:
                    songfilename = os_path.join(os_path.dirname(filename), m.group('filename'))
            m = title_re.search(entry)
            if m:
                if state == 0:
                    album = getEncodedString(m.group('title'))
                else:
                    title = getEncodedString(m.group('title'))
            m = performer_re.search(entry)
            if m:
                performer = getEncodedString(m.group('performer'))
            m = track_re.search(entry)
            if m:
                state = 1  # tracks
            m = index_re.search(entry)
            if m:
                if int(m.group('index_nr')) == 1:
                    m1 = msts_re.search(m.group('track_index'))
                    if m1:
                        pts = (int(m1.group('mins')) * 60 + int(m1.group('secs'))) * 90000
                        SongList.append((Item(text=title, filename=songfilename, title=title, artist=performer, album=album, join=False, PTS=pts),))
        cuefile.close()
        return SongList

    def readM3U(self, filename):
        SongList = []
        displayname = None
        try:
            m3ufile = open(filename, "r")
        except IOError:
            return None
        for line in m3ufile.readlines():
            entry = line.strip()
            if entry != "":
                if entry.startswith("#EXTINF:"):
                    extinf = entry.split(',', 1)
                    if len(extinf) > 1:
                        displayname = extinf[1]
                elif entry.startswith("http"):
                    isDVB = False
                    if displayname:
                        text = displayname
                        displayname = None
                    else:
                        text = entry
                    t = os_path.splitext(os_path.basename(entry))[0]
                    ref = eServiceReference(t)
                    if ref.valid():
                        if text == entry:
                            info = serviceHandler.info(ref)
                            text = info and info.getName(ref) or "."
                        isDVB = True
                    SongList.append((Item(text=text, filename=entry, isDVB=isDVB),))
                elif entry[0] != "#":
                    if entry[0] == "/":
                        songfilename = entry
                    else:
                        songfilename = os_path.join(os_path.dirname(filename), entry)
                    if displayname:
                        text = displayname
                        displayname = None
                    else:
                        text = entry
                    SongList.append((Item(text=text, filename=songfilename),))
        m3ufile.close()
        return SongList

    def readPLS(self, filename):
        SongList = []
        displayname = None
        try:
            plsfile = open(filename, "r")
        except IOError:
            return None
        entry = plsfile.readline().strip()
        if entry == "[playlist]":
            while True:
                entry = plsfile.readline().strip()
                if entry == "":
                    break
                if entry[0:4] == "File":
                    pos = entry.find('=') + 1
                    newentry = entry[pos:]
                    SongList.append((Item(text=newentry, filename=newentry),))
        else:
            SongList = self.readM3U(filename)
        plsfile.close()
        return SongList

    def green_pressed(self):
        SongList = []
        count = 0
        for root, subFolders, files in os_walk(self["list"].getCurrentDirectory()):
            files.sort()
            for filename in files:
                if isValidAudio(filename):
                    SongList.append((Item(text=filename, filename=os_path.join(root, filename)),))
        if self.player is not None:
            self.session.deleteDialog(self.player)
            self.player = None
        self.startMerlinPlayerScreenTimer.stop()
        count = len(SongList)
        if count:
            self.player = self.session.instantiateDialog(MerlinMusicPlayer2Screen, SongList, 0, False, self.currentService, self.serviceList)
            self.session.execDialog(self.player)
        else:
            self.session.open(MessageBox, _("No music files found!"), type=MessageBox.TYPE_INFO, timeout=20)

    def ok(self):
        if self["list"].canDescent():
            self["list"].descent()
            self.updateTarget()
        else:
            SongList = []
            foundIndex = 0
            count = 0
            index = 0
            currentFilename = self["list"].getFilename()
            if currentFilename.lower().endswith(".m3u"):
                SongList = self.readM3U(os_path.join(self["list"].getCurrentDirectory(), currentFilename))
            elif currentFilename.lower().endswith(".pls"):
                SongList = self.readPLS(os_path.join(self["list"].getCurrentDirectory(), currentFilename))
            elif currentFilename.lower().endswith(".cue"):
                SongList = self.readCUE(os_path.join(self["list"].getCurrentDirectory(), currentFilename))
            else:
                files = os_listdir(self["list"].getCurrentDirectory())
                files.sort()
                for filename in files:
                    if isValidAudio(filename):
                        SongList.append((Item(text=filename, filename=os_path.join(self["list"].getCurrentDirectory(), filename)),))
                        if self["list"].getFilename() == filename:
                            foundIndex = index
                        index += 1
            if self.player is not None:
                self.session.deleteDialog(self.player)
                self.player = None
            self.startMerlinPlayerScreenTimer.stop()
            count = len(SongList)
            if count:
                self.player = self.session.instantiateDialog(MerlinMusicPlayer2Screen, SongList, foundIndex, False, self.currentService, self.serviceList)
                self.session.execDialog(self.player)
            else:
                self.session.open(MessageBox, _("No music files found!"), type=MessageBox.TYPE_INFO, timeout=20)

    def config(self):
        self.startMerlinPlayerScreenTimer.stop()
        self.session.openWithCallback(self.merlinMusicPlayerSetupCallback, MerlinMusicPlayer2Setup, True)

    def merlinMusicPlayerSetupCallback(self, result):
        if result:
            if self.player is not None:
                self.player.closePlayer()
                self.session.deleteDialog(self.player)
                self.player = None
            self.startPlayerTimerCallback()

    def menu_pressed(self):
        self.startMerlinPlayerScreenTimer.stop()
        options = [(_("Configuration"), self.config), ]
        if not self["list"].canDescent():
            filename = self["list"].getFilename()
            if isValidAudio(filename):
                options.extend(((_("Clear current songlist and play selected entry"), self.stopPlayingAndAppendFileToSongList),))
                options.extend(((_("Append file to current songlist"), self.appendFileToSongList),))
                if self.player is not None and self.player.songList:
                    options.extend(((_("Insert file to current songlist and play next"), self.insertFileToSongList),))
        self.session.openWithCallback(self.menuCallback, ChoiceBox, list=options)

    def menuCallback(self, ret):
        ret and ret[1]()

    def stopPlayingAndAppendFileToSongList(self):
        self.startMerlinPlayerScreenTimer.stop()
        if self.player is not None:
            self.session.deleteDialog(self.player)
            self.player = None
        self.appendFileToSongList()
        self.startMerlinPlayerScreenTimer.start(START_MERLIN_PLAYER_SCREEN_TIMER_VALUE)

    def appendFileToSongList(self):
        playerAvailable = self.player is not None and self.player.songList
        filename = self["list"].getFilename()
        if isValidAudio(filename):
            SongList = []
            a = Item(text=filename, filename=os_path.join(self["list"].getCurrentDirectory(), filename))
            if playerAvailable:
                self.player.songList.append((a,))
                self.player.origSongList.append((a,))
            else:
                SongList.append((a,))
            if not playerAvailable:
                if self.player is not None:
                    self.session.deleteDialog(self.player)
                    self.player = None
                self.player = self.session.instantiateDialog(MerlinMusicPlayer2Screen, SongList, 0, False, self.currentService, self.serviceList)
                self.player.playSong(self.player.songList[self.player.currentIndex][0].filename)
                self.player.init = 1
            else:
                self.player["nextTitle"].setText(self.player.getNextTitle())
                self.session.open(MessageBox, _("%s\nappended to songlist") % a.text, type=MessageBox.TYPE_INFO, timeout=3)

    def insertFileToSongList(self):
        if self.player is not None and self.player.songList:
            index = self.player.currentIndex
            filename = self["list"].getFilename()
            if isValidAudio(filename):
                a = Item(text=filename, filename=os_path.join(self["list"].getCurrentDirectory(), filename))
                self.player.songList.insert(index + 1, (a,))
                self.player.origSongList.insert(index + 1, (a,))
                self.player["nextTitle"].setText(self.player.getNextTitle())
                self.session.open(MessageBox, _("%s\ninserted and will be played as next song") % a.text, type=MessageBox.TYPE_INFO, timeout=3)
        else:
            self.appendFileToSongList()

    def info_pressed(self):
        self.startMerlinPlayerScreenTimer.stop()
        if self.player is not None:
            if self.player.songList:
                self.session.execDialog(self.player)

    def moveright(self):
        self["list"].pageDown()
        self.lcdupdate()

    def moveleft(self):
        self["list"].pageUp()
        self.lcdupdate()

    def moveup(self):
        self["list"].up()
        self.lcdupdate()

    def movedown(self):
        self["list"].down()
        self.lcdupdate()

    def updateTarget(self):
        currFolder = self["list"].getCurrentDirectory()
        if currFolder is None:
            currFolder = _("Invalid Location")
        self["headertext"].setText(_("Filelist: %s") % currFolder)
        self.lcdupdate()

    def lcdupdate(self):
        self.startMerlinPlayerScreenTimer.start(START_MERLIN_PLAYER_SCREEN_TIMER_VALUE)
        index = self["list"].getSelectionIndex()
        sel = self["list"].list[index]
        text = sel[1][7]
        if sel[0][1] is True:
            text = "/" + text
        self.summaries.setText(text, 1)
        # voheriges
        index -= 1
        if index < 0:
            index = len(self["list"].list) - 1
        sel = self["list"].list[index]
        text = sel[1][7]
        if sel[0][1] is True:
            text = "/" + text
        self.summaries.setText(text, 3)
        # naechstes
        index = self["list"].getSelectionIndex() + 1
        if index > (len(self["list"].list) - 1):
            index = 0
        sel = self["list"].list[index]
        text = sel[1][7]
        if sel[0][1] is True:
            text = "/" + text
        self.summaries.setText(text, 4)

    def closing(self):
        c = self.session.nav.getCurrentlyPlayingServiceReference()
        if c is not None:
            if "http%3a//127.0.0.1%3a8001" in c.toString():
                self.session.nav.stopService()
                self.closeTimer.start(300)
                return
        self.session.nav.stopService()
        self.close()

    def closeTimerTimeout(self):
        self.close()

    def __onClose(self):
        self.autoActivationKeyPressedActionSlot = None
        self.session.nav.SleepTimer.on_state_change.remove(self.sleepTimerEntryOnStateChange)
        self.startMerlinPlayerScreenTimer.stop()
        if self.player is not None:
            self.player.closePlayer()
            self.session.deleteDialog(self.player)
            self.player = None
        if self.serviceList is None:
            self.session.nav.playService(self.currentService)
        else:
            current = ServiceReference(self.serviceList.getCurrentSelection())
            self.session.nav.playService(current.ref)
        if config.plugins.merlinmusicplayer2.rememberlastfilebrowserpath.value:
            try:
                config.plugins.merlinmusicplayer2.defaultfilebrowserpath.value = self["list"].getCurrentDirectory()
                config.plugins.merlinmusicplayer2.defaultfilebrowserpath.save()
            except:
                pass

    def showRadio(self):
        self.session.openWithCallback(
                self.finishedServiceSelection,
                MerlinMusicPlayer2DVBRadioSelection,
                _("Select radio service")
            )

    def finishedServiceSelection(self, *args):
        if args:
            sname = args[0].toString()
            cur = eServiceReference(sname)
            serviceHandler = eServiceCenter.getInstance()
            info = serviceHandler.info(cur)
            name = info and info.getName(cur) or "."
            services = args[1]
            songList = []
            for s in services:
                a = Item(text=s[1], filename="http://127.0.0.1:8001/" + s[0].toString(), isDVB=True)
                songList.append((a,))

            currentIndex = args[2]

            if self.player is not None:
                self.session.deleteDialog(self.player)
                self.player = None
            self.startMerlinPlayerScreenTimer.stop()
            count = len(songList)
            if count:
                self.player = self.session.instantiateDialog(MerlinMusicPlayer2Screen, songList, currentIndex, False, self.currentService, self.serviceList)
                self.session.execDialog(self.player)
            else:
                self.session.open(MessageBox, _("No music files found!"), type=MessageBox.TYPE_INFO, timeout=20)

    def showInternetRadioFavorites(self):
        try:
            from Plugins.Extensions.InternetRadio.InternetRadioFavoriteConfig import InternetRadioFavoriteConfig
            favorite = InternetRadioFavoriteConfig()
            favoriteList = favorite.favoriteConfig.Entries
        except:
            favoriteList = None
        songList = []
        if favoriteList:
            for item in favoriteList:
                if item.type.value == 0:
                    a = Item(text=item.name.value, filename=item.text.value)
                    songList.append((a,))

            if self.player is not None:
                self.session.deleteDialog(self.player)
                self.player = None
            self.startMerlinPlayerScreenTimer.stop()
            count = len(songList)
            if count:
                self.player = self.session.instantiateDialog(MerlinMusicPlayer2Screen, songList, 0, False, self.currentService, self.serviceList)
                self.session.execDialog(self.player)
            else:
                self.session.open(MessageBox, _("No music files found!"), type=MessageBox.TYPE_INFO, timeout=20)

    def createSummary(self):
        return MerlinMusicPlayerLCDScreenText


def stop_recording(session, **kwargs):
    choicelist = ((_("stop recording"), "stop"), (_("do nothing"), "no"))
    Notifications.AddNotificationWithCallback(
        boundFunction(MerlinRecorder.instance.startRecordingCallback, None, None, None, None, None, None, None),
        ChoiceBox,
        list=choicelist,
        title=_("Stop Merlin Music Player 2 streaming recording?"),
        titlebartext=_("Select an action"))


def main(session, **kwargs):
    if kwargs.has_key("servicelist"):
        servicelist = kwargs["servicelist"]
    else:
        from Screens.InfoBar import InfoBar
        servicelist = InfoBar.instance.servicelist
    session.open(iDream, servicelist)


def merlinmusicplayerfilelist(session, **kwargs):
    if kwargs.has_key("servicelist"):
        servicelist = kwargs["servicelist"]
    else:
        from Screens.InfoBar import InfoBar
        servicelist = InfoBar.instance.servicelist
    session.open(MerlinMusicPlayer2FileList, servicelist)


def menu_merlinmusicplayerfilelist(menuid, **kwargs):
    if menuid == "mainmenu":
        return [(_("Merlin Music Player 2"), merlinmusicplayerfilelist, "merlin_music_player", 46)]
    return []


def menu_idream(menuid, **kwargs):
    if menuid == "mainmenu":
        return [(_("iDream"), main, "idream", 47)]
    return []


def session_start(reason, **kwargs):
    if reason == 0:
        from skin import loadSkin, loadSingleSkinData, dom_skins
        from enigma import getDesktop
        from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN
        skindir = "Extensions/MerlinMusicPlayer2/skins/"
        desktopSize = getDesktop(0).size().height()
        skinFile = resolveFilename(SCOPE_CURRENT_PLUGIN, skindir + "skin_%d.xml" % desktopSize)
        loadSkin(skinFile, "")
        path, dom_skin = dom_skins[-1:][0]
        loadSingleSkinData(getDesktop(0), dom_skin, path)
        skinFileDisplay = resolveFilename(SCOPE_CURRENT_PLUGIN, skindir + "skin_display.xml")
        loadSkin(skinFileDisplay, "")
        path, dom_skin = dom_skins[-1:][0]
        loadSingleSkinData(getDesktop(0), dom_skin, path)


def recorder_stop(reason, **kwargs):
    if reason == 0:
        MerlinRecorder()
    elif reason == 1:
        MerlinRecorder.instance.merlinMusicPlayerRecorder = None


def Plugins(**kwargs):
    list = [PluginDescriptor(name="Merlin iDream 2", description=_("Dreambox Music Database"), where=[PluginDescriptor.WHERE_PLUGINMENU], icon="iDream.png", fnc=main)]
    list.append(PluginDescriptor(name="Merlin Music Player 2", description=_("Merlin Music Player"), where=[PluginDescriptor.WHERE_PLUGINMENU], icon="MerlinMusicPlayer.png", fnc=merlinmusicplayerfilelist))
    if config.plugins.merlinmusicplayer2.idreamextendedpluginlist.value:
        list.append(PluginDescriptor(name="iDream 2", description=_("Dreambox Music Database"), where=[PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=main))
    if config.plugins.merlinmusicplayer2.merlinmusicplayerextendedpluginlist.value:
        list.append(PluginDescriptor(name="Merlin Music Player 2", description=_("Merlin Music Player"), where=[PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=merlinmusicplayerfilelist))
    if config.plugins.merlinmusicplayer2.merlinmusicplayermainmenu.value:
        list.append(PluginDescriptor(name="Merlin Music Player 2", description=_("Merlin Music Player"), where=[PluginDescriptor.WHERE_MENU], fnc=menu_merlinmusicplayerfilelist))
    if config.plugins.merlinmusicplayer2.idreammainmenu.value:
        list.append(PluginDescriptor(name="iDream 2", description=_("iDream"), where=[PluginDescriptor.WHERE_MENU], fnc=menu_idream))
    list.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=session_start))
    list.append(PluginDescriptor(where=PluginDescriptor.WHERE_AUTOSTART, fnc=recorder_stop))
    list.append(PluginDescriptor(name="Merlin Music Player 2: stop stream-recording", description=_("Merlin Music Player 2 -> stop stream-recording"), where=[-10000], fnc=stop_recording))
    return list
