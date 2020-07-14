# -*- coding: utf-8 -*

import json
import xml.etree.ElementTree as ET
from datetime import datetime
import urllib3
import certifi
from six.moves import html_parser
from bs4 import BeautifulSoup
from six.moves.urllib.parse import urlparse, parse_qs, urljoin

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where())


class JWMedium:
    """Class to store a medium"""
    urls = []
    title = ""
    category = ""
    language = ""
    category = ""
    image = ""
    medium_type = ""
    audio = "-"
    text = " "

    def get_url(self, quality):
        the_url = self.urls[0]
        for url in self.urls:
            if (url.label == quality):
                the_url = url
        return the_url


class JWMagazineType:
    '''Class to store magazines'''
    mag_type = ''
    mag_title = ''

    def __repr__(self):
        return ''


class JWMediumURL:
    url = ""
    label = ""

    def __repr__(self):
        return ''


class JWSection:
    url = ""
    title = ""
    image = ""

    def __repr__(self):
        return ''


class JWMagazine:
    img = ""
    title = ""
    id = ""
    mag_type = ""
    sections = []

    def __repr__(self):
        return ''


class JWChapter:
    title = ""
    url = ""
    book = ""
    media = []
    data_url = ""
    num = ""

    def __repr__(self):
        return ''


class JWBibleBook:
    json = ""
    name = ""
    num = ""
    bible_type = ""
    url = ""
    img = "https://download-a.akamaihd.net/files/media_video/ad/nwtsv_univ.jpg"
    has_media = False

    def __repr__(self):
        return ''


class JWBible:
    json = ""
    locale = ""
    title = ""
    img = "https://download-a.akamaihd.net/files/media_video/ad/nwtsv_univ.jpg"
    books = []

    def __len__(self):
        return len(self.books)

    def __repr__(self):
        return ''


class JWParser:
    """Class to load content from JW TV"""

    languages = []
    categories = []
    es_file_name = 'es_mp3'

    def get_magazine_title(self, locale):
        url = "https://www.jw.org/en/publications/magazines/"
        res = "The Watchtower and Awake! Magazines"
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data, "html.parser")
        link = soup.find(hreflang=locale)
        if None != link:
            res = link.get('title')
        return res

    def get_languages(self):
        if len(self.languages) == 0:
            response = http.request('GET', "https://data.jw-api.org/mediator/v1/languages/E/web?clientType=tvjworg")
            lang_list = json.loads(response.data)
            self.languages = lang_list["languages"]
        return self.languages

    def get_media(self, language, category):
        videos = []
        if "media" in category["category"]:
            for media in category["category"]["media"]:
                my_medium = JWMedium()
                my_medium.language = language
                my_medium.category = category["category"]["name"]
                my_medium.title = media["title"].encode("utf-8")
                my_medium.medium_type = media["type"]
                if 'sqr' in media['images']:
                    my_medium.image = media['images']['sqr']['lg']
                elif 'cvr' in media['images']:
                    if 'lg' in media['images']['cvr']:
                        my_medium.image = media['images']['cvr']['lg']
                    else:
                         my_medium.image = media['images']['cvr']['md']
                elif 'pnr' in media['images']:
                    if 'lg' in media['images']['pnr']:
                        my_medium.image = media['images']['pnr']['lg']
                    else:
                         my_medium.image = media['images']['pnr']['md']
                urls = []
                for medium in media["files"]:
                    an_url = JWMediumURL()
                    if medium["label"] is None:
                        an_url.label = ""
                    else:
                        an_url.label = medium["label"]
                    an_url.url = medium["progressiveDownloadURL"]
                    urls.append(an_url)
                my_medium.urls = urls
                videos.append(my_medium)
        return videos

    def get_media_by_category(self, language, category):
        response = http.request('GET',
                                "http://data.jw-api.org/mediator/v1/categories/" + language + "/" + category + "?detailed=1&clientType=tvjworg")
        json_videos_list = json.loads(response.data.decode('utf-8'))
        videos = []
        if json_videos_list["category"]["type"] == "container":
            for subcategory in json_videos_list["category"]["subcategories"]:
                videos_list = self.get_media_by_category(language, subcategory["key"])
                for video in videos_list:
                    videos.append(video)
        else:
            for video in self.get_media(language, json_videos_list):
                videos.append(video)
        return videos

    def get_subcategories(self, language, category):
        categories = []
        response = http.request('GET',
                                "http://data.jw-api.org/mediator/v1/categories/" + language + "/" + category + "?detailed=1&clientType=tvjworg")
        categories_list = json.loads(response.data)
        for category_entry in categories_list["category"]["subcategories"]:
            categories.append(category_entry)
        return categories

    def get_categories(self, language, plugin_type):
        if len(self.categories) == 0:
            categories = []
            response = http.request('GET',
                                    "http://data.jw-api.org/mediator/v1/categories/" + language + "?detailed=1&clientType=tvjworg")
            categories_list = json.loads(response.data)
            for category in categories_list["categories"]:
                if category['key'] != 'Streaming':
                    if category['key'] == 'Audio' and plugin_type == 'audio':
                        if category['type'] == 'container':
                            for subcategory in self.get_subcategories(language, category['key']):
                                categories.append(subcategory)
                        else:
                            categories.append(category)
                    else:
                        if category['key'] != 'Audio' and plugin_type == 'video':
                            if category['type'] == 'container':
                                for subcategory in self.get_subcategories(language, category['key']):
                                    categories.append(subcategory)
                            else:
                                categories.append(category)
                self.categories = categories
        return self.categories

    def get_magazines_categories(self, language):
        rss_url = "https://apps.jw.org/E_RSSMEDIAMAG?rln=" + language + "&rfm=mp3&rmn="
        magazine_types = {'w', 'wp', 'g'}
        mag_category = []
        for mag_type in magazine_types:
            url = rss_url + mag_type
            response = http.request('GET', url)
            tree = ET.fromstring(response.data)
            channel = tree.find('channel')
            magazine = JWMagazineType()
            magazine.mag_type = mag_type
            magazine.mag_title = channel.find('title').text
            mag_category.append(magazine)
        return mag_category

    def get_magazine_content(self, magazine_type, magazine_id, language):
        mag_json = self.get_json_for_magazine(magazine_id, magazine_type, language)
        entries = []
        for entry in mag_json['files'][language]['MP3'][1:]:
            mag_entry = JWSection()
            mag_entry.title = entry['title']
            mag_entry.image = mag_json['pubImage']['url']
            mag_entry.url = entry['file']['url']
            entries.append(mag_entry)
        return entries

    @staticmethod
    def get_image_for_magazine(html_content):
        img_url = ""
        cvr_wrapper = html_content.find("div", class_="cvr-wrapper")
        img_url = cvr_wrapper.find("span")["data-img-size-lg"]
        return img_url

    @staticmethod
    def get_url_for_magazine(html_content):
        url = ""
        url_link = html_content.find("a", class_="jsDownload")
        url = url_link["data-jsonurl"]
        return url

    @staticmethod
    def get_id_for_magazine(html_content):
        url = ""
        url_link = html_content.find("a", class_="jsDownload")
        url = url_link["data-jsonurl"]
        parsed_url = urlparse(url)
        args = parse_qs(parsed_url.query)
        issue_nr = args['issue'][0]
        return issue_nr

    @staticmethod
    def get_title_for_magazine(html_content):
        title = ""
        e_subject = html_content.find("div", class_="emailSubject")
        title = e_subject.text
        return title

    @staticmethod
    def get_json_for_magazine(magazine_id, magazine_type, language):
        url = "https://apps.jw.org/GETPUBMEDIALINKS?issue=" + magazine_id + "&output=json&pub=" + magazine_type + "&fileformat=MP3&alllangs=0&langwritten=" + language
        response = http.request('GET', url)
        content = response.data
        return json.loads(content)

    def get_magazines_by_type(self, locale, language, magazine_type):
        magazines_list = []
        url = "https://www.jw.org/en/library/magazines/?contentLanguageFilter=" + locale + "&pubFilter=" + magazine_type + "&yearFilter="
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data, "html.parser")
        magazines = soup.find_all("div", class_="PublicationIssue")
        for mag in magazines:
            if mag.find('div', class_='audioFormat') and mag.find(class_='cvr-wrapper'):
                magazine = JWMagazine()
                magazine.mag_type = magazine_type
                magazine.id = JWParser.get_id_for_magazine(mag)
                mag_json = JWParser.get_json_for_magazine(magazine.id, magazine_type, language)
                magazine.img = mag_json['pubImage']['url']
                magazine.title = JWParser.get_title_for_magazine(mag).strip()
                magazines_list.append(magazine)
        return magazines_list

    @staticmethod
    def get_bible_content(bible_json, bible_language):
        bible_content = []
        b_json = json.loads(bible_json)
        for book in b_json['files'][bible_language]['MP3']:
            bible_book = JWBibleBook()
            parser = html_parser.HTMLParser()
            bible_book.name = parser.unescape(book['title'])
            bible_book.num = book['booknum']
            bible_book.bible_type = b_json['pub']
            bible_content.append(bible_book)
        return bible_content

    def get_bible_book_content(self, bible_type, bible_book_num, language):
        content = []
        url = "https://pubmedia.jw-api.org/GETPUBMEDIALINKS?booknum=" + bible_book_num + "&output=json&pub=" + bible_type + "&fileformat=MP3%2CAAC&alllangs=0&langwritten=" + language + "&txtCMSLang=" + language
        response = http.request('GET', url)
        book_content = json.loads(response.data)
        for chap in book_content['files'][language]['MP3'][1:]:
            chapter = JWChapter()
            chapter.url = chap['file']['url']
            chapter.title = chap['title']
            chapter.num = chap['track']
            chapter.book = book_content['pubName']
            content.append(chapter)
        return content

    def get_bibles_list(self, locale):
        bibles_list = []
        url = "https://www.jw.org/en/library/bible/?contentLanguageFilter=" + locale
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data, "html.parser")
        bible_issues = soup.find_all("div", class_="BiblePublication")
        parser = html_parser.HTMLParser()
        for bible in bible_issues:
            if bible.find("div", class_="audioFormat"):
                a_json_url = bible.find("div", class_="audioFormat").find("a")
                json_url = a_json_url["data-jsonurl"]
                bible_issue = JWBible()
                response = http.request('GET', json_url)
                bible_issue.json = json.loads(response.data)
                bible_issue.locale = locale
                bible_issue.title = parser.unescape(bible_issue.json['pubName'])
                img_url = bible.find("div", class_="cvr-wrapper").find('span')['data-img-size-lg']
                bible_issue.img = img_url
                bibles_list.append(bible_issue)
        return bibles_list

    def get_study_bible(self, locale):
        url = 'https://www.jw.org/finder?locale=' + locale + '&prefer=lang&docid=1001070103&srcid=langpicker'
        bible = JWBible()
        bible.locale = locale
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data, "html.parser")
        if soup.find('article', attrs={'data-bible-pub': 'nwtsty'}):
            bible.title = soup.find('main', class_='readingPane').find('h1').text.strip()
            json_url = soup.find('div', attrs={'id': 'pageConfig'})['data-bible_multimedia_api_nwtsty']
            response = http.request('GET', urljoin(url, json_url))
            bible.json = json.loads(response.data)
            for book_id in bible.json['editionData']['books'].keys():
                book = bible.json['editionData']['books'][book_id]
                if book['hasAudio']:
                    bible_book = JWBibleBook()
                    bible_book.name = book['standardName']
                    bible_book.num = book_id
                    bible_book.url = urljoin(url, book['url'])
                    bible_book.img = book['images'][0]['sizes']['lg']
                    bible_book.has_media = book['hasMultimedia']
                    bible.books.append(bible_book)

                def get_key(item):
                    return item.num

                bible.books = sorted(bible.books, key=get_key)
        return bible

    def get_study_bible_book(self, url, book_num, book_name, has_media, language):
        response = http.request('GET', url)
        book_content = self.get_bible_book_content('nwt', book_num, language)
        chapters = []
        soup = BeautifulSoup(response.data, "html.parser")
        media_url = urljoin(url, soup.find(id='pageConfig')['data-bible_multimedia_api_nwtsty'])
        media_content = {}
        if has_media:
            media_content = self.get_bible_study_book_media(media_url, book_num, language)
        for chap in book_content:
            chapter = JWChapter()
            chapter.title = chap.title
            chapter.url = chap.url
            chapter.book = book_name
            key = '{:03}'.format(chap.num)
            if key in media_content:
                chapter.media = media_content[key]
            chapters.append(chapter)
        return chapters

    def get_bible_study_book_media(self, url, book_num, language):
        response = http.request('GET', url + book_num)
        data = json.loads(response.data)
        media_list = {}
        for medium in data['ranges'][book_num + "000000-" + book_num + "999999"]['multimedia']:
            jw_medium = JWMedium()
            jw_medium.title = medium['label'].strip().encode("utf-8")
            jw_medium.medium_type = medium['type']
            jw_medium.image = medium['thumbnail']['zoom']
            if medium['type'] == 'image':
                jw_medium.audio = self.get_audio_for_doc(medium['docID'], language)
                jw_medium.image = medium['resource']['sizes']['lg']
                soup = BeautifulSoup(medium['caption'].strip().encode('utf-8'), "html.parser")
                jw_medium.text = soup.get_text().encode('utf-8')
            else:
                if medium['type'] == 'video':
                    jw_medium.urls = self.get_videos_from_json(medium['resource']['src'][0], language)
            for entries in medium['source'].split(','):
                for entry in entries.split('-'):
                    if entry[:2] == book_num:
                        chapter = entry[2:-3]
                        media_for_chapter = []
                        if chapter in media_list:
                            media_for_chapter = media_list[chapter]
                        media_for_chapter.append(jw_medium)
                        tmp_dict = {chapter: media_for_chapter}
                        media_list.update(tmp_dict)
        return media_list

    def get_videos_from_json(self, url, language):
        response = http.request('GET', url)
        data = json.loads(response.data)
        urls = []
        for medium in data["files"][language]["MP4"]:
            an_url = JWMediumURL()
            if medium["label"] is None:
                an_url.label = ""
            else:
                an_url.label = medium['label']
                an_url.url = medium['file']['url']
            urls.append(an_url)
        return urls

    def get_audio_for_doc(self, doc_id, language):
        url = 'https://apps.jw.org/GETPUBMEDIALINKS?langwritten=' + language + '&txtCMSLang=' + language + '&fileformat=MP3&docid=' + doc_id
        file_url = '-'
        response = http.request('GET', url)
        if response.status == 200:
            data = json.loads(response.data)
            for medium in data['files'][language]['MP3']:
                file_url = medium['file']['url']
        return file_url

    def __init__(self):
        self.languages = self.get_languages()

    def init_daily_scriptures(self):
        url = 'https://wol.jw.org/en/wol/h/r1/lp-e'
        response = http.request('GET', url)
        return response.data

    def get_es_json(self, locale, init_content):
        currentDay = datetime.now().day
        currentMonth = datetime.now().month
        currentYear = datetime.now().year
        url = 'https://wol.jw.org/wol/dt/'
        content = {}
        soup = BeautifulSoup(init_content, "html.parser")
        link = soup.find(hreflang=locale)
        if link is not None:
            res = link.get('href')
            res_split = res.rsplit('/', 2)
            url = url + res_split[1] + '/' + res_split[2] + '/' + str(currentYear) + "/" + str(
                currentMonth) + "/" + str(currentDay)
            response = http.request('GET', url)
            content = json.loads(response.data)['items'][0]
            soup = BeautifulSoup(content['content'], "html.parser")
            text_day = soup.header.text
            tts_text = text_day
            text_bible_full = soup.header.next_sibling.next_sibling
            ref_bible_tmp = 'https://wol.jw.org' + text_bible_full.a['href']
            text_bible = text_bible_full.find('em').text
            script_ref_json = http.request('GET', ref_bible_tmp)
            json_ref = json.loads(script_ref_json.data)
            list_ref = json_ref['items'][0]['title'].split(':')
            ref_bible = ''
            for item in list_ref:
                ref_bible = ref_bible + " " + item
            tts_text = text_bible
            text_comm = soup.findAll("div", {"class": "bodyTxt"})[0]
            for anchor in text_comm.findAll("a"):
                anchor.decompose()
            tts_text = text_day + '.\n' + '..., ..., ...' + text_bible + '.\n' + '..., ..., ...' + ref_bible + '.\n' + '..., ..., ...' + text_comm.text
            tts = gtts.gTTS(text=tts_text, lang=locale)
            file_name = "special://temp/" + self.es_file_name + "_" + locale + ".mp3"
            tts.save(file_name)
        return content


def main():
    my_jw_parser = JWParser()

    bbl = my_jw_parser.get_study_bible("fr")

    for book in bbl.books:
        print(book.url)
        content = my_jw_parser.get_bible_book_content("nwt", book.num, "F")
        for chap in content:
            print(chap.num)


if __name__ == '__main__':
    main()
