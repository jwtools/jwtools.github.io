# -*- coding: utf-8 -*-

import json
import os
import sys
import urllib

import pyxbmct
import routing
import xbmc
import xbmcaddon
from six.moves.urllib.parse import parse_qs
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory

from resources.lib import JWParser


class MediumWindow(pyxbmct.AddonFullWindow):

    def __init__(self, title=''):
        super(MediumWindow, self).__init__(title)
        self.setGeometry(self.getWidth(), self.getHeight(), 20, 10)
        # connect a key action (Backspace) to close window.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
        self.connect(pyxbmct.ACTION_MOUSE_LEFT_CLICK, self.close)
        button = pyxbmct.Button('Close')
        self.placeControl(button, 18, 4, rowspan=2, columnspan=2)

    def set_image(self, img):
        # img
        image = pyxbmct.Image(img, aspectRatio=2)
        self.placeControl(image, 0, 0, rowspan=18, columnspan=5)

    def set_text(self, text):
        textbox = pyxbmct.TextBox()
        self.placeControl(textbox, 0, 5, rowspan=18, columnspan=5)
        textbox.setText(text)
        textbox.autoScroll(5000, 5000, 1000)


ADDON = xbmcaddon.Addon()
plugin = routing.Plugin()
plugin_args = xbmcaddon.Addon(ADDON.getAddonInfo('id')).getSetting('args')
jw_parser = JWParser.JWParser()
language = xbmcaddon.Addon(ADDON.getAddonInfo('id')).getSetting('language')
locale = xbmcaddon.Addon(ADDON.getAddonInfo('id')).getSetting('locale')
video_quality = xbmcaddon.Addon(ADDON.getAddonInfo('id')).getSetting('quality')

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer
cacheDuration = int(xbmcaddon.Addon(ADDON.getAddonInfo('id')).getSetting('cache'))
cache = StorageServer.StorageServer(ADDON.getAddonInfo('name'),
                                    cacheDuration)  # (Your plugin name, Cache time in hours)


@plugin.route('/')
def index():
    global plugin_args
    plugin_args = sys.argv[2][1:]
    xbmcaddon.Addon(ADDON.getAddonInfo('id')).setSetting(id='args', value=plugin_args)
    args = parse_qs(plugin_args)
    content_type = args.get('content_type', [])
    if len(content_type) > 0 and 'audio' == content_type[0]:
        show_audio()
    else:
        show_video()


def show_audio():
    show_study_bible()
    show_bibles()
    show_magazines()
    show_audio_categories()
    endOfDirectory(plugin.handle)

def show_study_bible():
    bible = cache.cacheFunction(jw_parser.get_study_bible, locale)
    if isinstance(bible, JWParser.JWBible):
        li = ListItem(bible.title)
        li.setArt({'thumb': bible.img, 'poster': bible.img, 'fanart': bible.img})
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_study_bible_content), li, True)


@plugin.route('/nwtsty/')
def show_study_bible_content():
    bible = cache.cacheFunction(jw_parser.get_study_bible, locale)
    for book in bible.books:
        li = ListItem(book.name)
        li.setArt({'thumb': book.img, 'poster': book.img, 'fanart': book.img})
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_study_bible_book, book.num), li, True)
    endOfDirectory(plugin.handle)


@plugin.route('/nwtsty/media/<title>/<image>/<audio>/<text>')
def display_media(title, image, audio, text):
    window = MediumWindow(urllib.unquote_plus(title))
    window.set_image(urllib.unquote_plus(image))
    window.set_text(urllib.unquote_plus(text))
    if len(audio) > 1:
        li = ListItem(urllib.unquote_plus(title))
        li.setInfo('video', {'title': urllib.unquote_plus(title)})
        xbmc.Player().play(urllib.unquote_plus(audio), li)
    window.doModal()
    del window
    return


@plugin.route('/nwtsty/<book_num>')
def show_study_bible_book(book_num):
    bible = cache.cacheFunction(jw_parser.get_study_bible, locale)
    url = ""
    book_name = ""
    jwbook = JWParser.JWBibleBook()
    for book in bible.books:
        if str(book.num) == book_num:
            url = book.url
            book_name = book.name
            break
    book_content = cache.cacheFunction(jw_parser.get_study_bible_book, url, book_num, book_name, book.has_media,
                                       language)
    for chapter in book_content:
        for medium in chapter.media:
            li = ListItem(medium.title)
            li.setArt({'thumb': medium.image, 'poster': medium.image, 'fanart': medium.image})
            li.setInfo(type="Image", infoLabels={"Title": medium.title})
            if medium.medium_type == 'image':
                addDirectoryItem(plugin.handle, plugin.url_for(
                    display_media, urllib.quote_plus(medium.title), urllib.quote_plus(medium.image),
                    urllib.quote_plus(medium.audio), urllib.quote_plus(medium.text)), li, False)
            else:
                if medium.medium_type == 'video':
                    addDirectoryItem(plugin.handle, medium.get_url(video_quality).url, li, False)
        li = ListItem(chapter.title)
        li.setArt({'thumb': jwbook.img, 'poster': jwbook.img, 'fanart': jwbook.img})
        li.setInfo('video', {'title': chapter.book + " - " + chapter.title})
        addDirectoryItem(plugin.handle, chapter.url, li, False)
    endOfDirectory(plugin.handle)


def show_bibles():
    global bibles_list
    bibles_list = cache.cacheFunction(jw_parser.get_bibles_list, locale)
    for bible in bibles_list:
        li = ListItem(bible.title)
        li.setArt({'thumb': bible.img, 'poster': bible.img, 'fanart': bible.img})
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_bible_content, bibles_list.index(bible)), li, True)


def show_magazines():
    addDirectoryItem(plugin.handle, plugin.url_for(
        show_magazines_types), ListItem(jw_parser.get_magazine_title(locale)), True)


def show_audio_categories():
    audio_categories = cache.cacheFunction(jw_parser.get_categories, language, 'audio')
    for audio_category in audio_categories:
        image_url = ""
        if 'images' in audio_category:
            if 'sqr' in audio_category['images']:
                image_url = audio_category['images']['sqr']['lg']
            elif 'wss' in audio_category['images']:
                image_url = audio_category['images']['wss']['lg']
            elif 'pnr' in audio_category['images']:
                if 'lg' in  audio_category['images']['pnr']:
                    image_url = audio_category['images']['pnr']['lg']
                else:
                    image_url = audio_category['images']['pnr']['md']
        li =  ListItem(audio_category['name'])
        li.setArt({'thumb': image_url, 'poster': image_url, 'fanart': image_url})
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_category, audio_category['key']), li, True)


@plugin.route('/bible-book/<bible_id>/<book_nr>/')
def show_book_content(bible_id, book_nr):
    bibles_list = cache.cacheFunction(jw_parser.get_bibles_list, locale)
    bible_issue = bibles_list[int(bible_id)]
    book_content = cache.cacheFunction(jw_parser.get_bible_book_content, bible_issue.json['pub'], book_nr, language)
    for chapter in book_content:
        li = ListItem(chapter.title)
        li.setArt({'thumb': bible_issue.img, 'poster': bible_issue.img, 'fanart': bible_issue.img})
        li.setInfo('video', {'title': chapter.book + " - " + chapter.title})
        addDirectoryItem(plugin.handle, chapter.url, li, False)
    endOfDirectory(plugin.handle)


@plugin.route('/bible/<bible_id>')
def show_bible_content(bible_id):
    bibles_list = cache.cacheFunction(jw_parser.get_bibles_list, locale)
    bible_content = cache.cacheFunction(jw_parser.get_bible_content, json.dumps(bibles_list[int(bible_id)].json),
                                        language)
    for book in bible_content:
        li = ListItem(book.name)
        li.setArt({'thumb': bibles_list[int(bible_id)].img, 'poster': bibles_list[int(bible_id)].img, 'fanart': bibles_list[int(bible_id)].img})
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_book_content, bible_id, book.num), li, True)
    endOfDirectory(plugin.handle)


@plugin.route('/magazines')
def show_magazines_types():
    magazines_types = cache.cacheFunction(jw_parser.get_magazines_categories, language)
    for mag_type in magazines_types:
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_magazine_by_type, mag_type.mag_type), ListItem(mag_type.mag_title), True)
    endOfDirectory(plugin.handle)


@plugin.route('/magazines/<magazine_type>')
def show_magazine_by_type(magazine_type):
    magazines_list = jw_parser.get_magazines_by_type(locale, language, magazine_type)
    for mag in magazines_list:
        li = ListItem(mag.title)
        li.setArt({'thumb': mag.img, 'poster': mag.img, 'fanart': mag.img})
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_magazine_content, mag.mag_type, mag.id), li, True)
    endOfDirectory(plugin.handle)


@plugin.route('/magazines/<magazine_type>/<magazine_id>')
def show_magazine_content(magazine_type, magazine_id):
    magazine_content = cache.cacheFunction(jw_parser.get_magazine_content, magazine_type, magazine_id, language)
    for entry in magazine_content:
        li = ListItem(entry.title)
        li.setArt({'thumb': entry.image, 'poster': entry.image, 'fanart': entry.image})
        li.setInfo('music', {'title': entry.title})
        addDirectoryItem(plugin.handle, entry.url, li, False)
    endOfDirectory(plugin.handle)


def show_video():
    videos_categories = cache.cacheFunction(jw_parser.get_categories, language, 'video')
    for video_category in videos_categories:
        image_url = ""
        if 'images' in video_category:
            if 'sqr' in video_category['images']:
                image_url = video_category['images']['sqr']['lg']
            elif 'wss' in video_category['images']:
                image_url = video_category['images']['wss']['lg']
            elif 'pnr' in video_category['images']:
                if 'lg' in  video_category['images']['pnr']:
                    image_url = video_category['images']['pnr']['lg']
                else:
                    image_url = video_category['images']['pnr']['md']
        li = ListItem(video_category['name'])
        li.setArt({'thumb': image_url, 'poster': image_url, 'fanart': image_url})
        addDirectoryItem(plugin.handle, plugin.url_for(
            show_category, video_category['key']), li, True)
    endOfDirectory(plugin.handle)


@plugin.route('/category/<category_id>')
def show_category(category_id):
    list_media = cache.cacheFunction(jw_parser.get_media_by_category, language, category_id)
    for medium in list_media:
        li = ListItem(medium.title)
        li.setArt({'thumb': medium.image, 'poster': medium.image, 'fanart': medium.image})
        li.setInfo('video', {'title': medium.title})
        addDirectoryItem(
            plugin.handle, medium.get_url(video_quality).url, li, False)
    endOfDirectory(plugin.handle)


@plugin.route('/languages')
def show_languages():
    languages = cache.cacheFunction(jw_parser.get_languages)
    images_path = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('path')), 'resources', 'images')
    for lang in languages:
        li = ListItem(lang["name"] + " (" + lang["vernacular"] + ")")
        li.setArt({'thumb': images_path + '/1608752-512.png', 'poster': images_path + '/1608752-512.png', 'fanart':  images_path + '/1608752-512.png'})
        addDirectoryItem(
            plugin.handle, plugin.url_for(
                set_language, lang['code'], lang['locale'], lang['name']), li)
    endOfDirectory(plugin.handle)


@plugin.route('/language/<language_id>/<language_locale>/<language_name>')
def set_language(language_id, language_locale, language_name):
    xbmcaddon.Addon(ADDON.getAddonInfo('id')).setSetting(id='language', value=language_id)
    xbmcaddon.Addon(ADDON.getAddonInfo('id')).setSetting(id='locale', value=language_locale)
    global language, locale
    language = language_id
    locale = language_locale
    url = plugin.url_for(index) + "?" + xbmcaddon.Addon(ADDON.getAddonInfo('id')).getSetting('args')
    xbmc.executebuiltin('Container.Refresh(%s)' % url)


def run():
    plugin.run()
