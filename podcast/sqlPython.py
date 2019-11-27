"""
Author: Chelsea Piccirilli
File: sqlPython.py
Professor: Dr. Mamo
Description: This houses 4 classes required for parsing strings, sql, and data.
Note: Some functions are being built with a future implimentation in mind. They are very "beta".
Use at your own risk
"""

import os
import shutil
from html.parser import HTMLParser
from podcast.connection import DbConnection
import datetime, sys, requests, sqlite3
from mutagen.mp3 import MP3

class MLStripper(HTMLParser):
    """
    Strips the html elements from the passed string.
    Makes it more uniform
    """
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

class sqlPython:

    def __init__(self, feed):
        self.feed = feed
        self.dbc = DbConnection()
        self.dbc.db_connection()
        self.rsshref = ""
        self.title = ""
        self.website = ""
        self.subtitle = ""

        dateadded = datetime.datetime.now()
        self.conv_date = dateadded.strftime("%m/%d/%Y, %H:%M:%S")

    def strip_tags(self, html):
        """Way to use the tag stripper class above"""
        s = MLStripper()
        s.feed(html)
        return s.get_data()

    def infoGrabber(self):
        """
        Fills out the info needed for the rssurl table
        :return:
        """
        try:
            if self.feed.feed:
                if self.feed.feed.title: self.title = self.feed.feed.title

                if self.feed.feed.links[0].href: self.website = self.feed.feed.links[0].href

                if self.feed.feed.links[1].href: self.rsshref = self.feed.feed.links[1].href

                if self.feed.feed.subtitle: self.subtitle = self.feed.feed.subtitle
            else:
                print("Invalid feed.")
                sys.exit(1)

        except Exception as e:
            print("An Error occured in SeriesRssInfo. ")
            print(str(e), str(e).__class__())

        print(self.title, self.website, self.rsshref, self.subtitle)

    def get_title(self):
        """
        returns title for functions in PyCast.py
        :return:
        """
        return self.title

    def info_update(self):
        """
        Inserts sql. Inserts into rssurl table if it doesn't
        exist already.
        :return:
        """
        self.infoGrabber()

        try:
            info = "INSERT INTO rssurl VALUES (?, ?, ?, ?, ?)"
            select = "SELECT * FROM rssurl where title= '"+self.title+"'"
            data = (self.title, self.website, self.rsshref, self.subtitle, self.conv_date)
            conn = sqlite3.connect("podcast\podcast.db")
            cur = conn.cursor()
            cur.execute(select)
            row = cur.fetchall()
            if not row:

                print(row)
                cur.execute(info, data)
                conn.commit()
            else:
                print("Series already exists.")
        except Exception as e:
            ex = str(e)
            print(ex, ex.__class__())

    def _info_update(self):
        """
        Mostly for batch loading series. Carbon copy of the one above only with
        different connect statement.
        :return:
        """
        self.infoGrabber()

        try:
            info = "INSERT INTO rssurl VALUES (?, ?, ?, ?, ?)"
            select = "SELECT * FROM rssurl where title= '"+self.title+"'"
            data = (self.title, self.website, self.rsshref, self.subtitle, self.conv_date)
            conn = sqlite3.connect("podcast.db")
            cur = conn.cursor()
            cur.execute(select)
            row = cur.fetchall()
            if not row:

                print(row)
                cur.execute(info, data)
                conn.commit()
            else:
                print("Series already exists.")
        except Exception as e:
            ex = str(e)
            print(ex, ex.__class__())


    def _parse_episodes_from_feed(self):
        """
        Takes the feed parser object and takes out the required information. Then kicks it to the database
        :return:
        """
        title = ()
        epurl = ()
        published = ()
        desc = ()
        storage = ()
        seriestitle = self.feed.feed.title

        parsed_list = []

        for en, f in enumerate(self.feed.entries): # gets out required information and sorts it into personal tuple.

             # checks if there. If so puts it in the tuple
            try:
                title += (f.title, )
            except IndexError as e:
                title +=("No title given", )

            try:
                 epurl += (f.links[1]["href"],)
                 url = f.links[1]["href"]
                 pie = url.split("/")[-1]
                 if ".mp3" in pie:
                    if pie.endswith(".mp3"):
                        pieces = pie
                    else:
                        parts = pie.split(".mp3")[0]
                        pieces = parts + ".mp3"

            except IndexError as e:
                epurl += ("No episode url present",)

            try:
                published += (f.published, )
            except IndexError as e:
                published +=("Publish date invalid", )

            try:
                z = self.strip_tags(f.content[0]["value"])
                desc += (z, )
            except IndexError as e:
                desc += ("Description unavailable", )

            storage += (self.ep_path(seriestitle, pieces),) # sticks the storage path into the proper tuple.
            #print(title[en], "|", epurl[en], "|", published[en], "|", desc[en], "|", self.ep_path(seriestitle, title[en]), "|", seriestitle)

        for i in range(0, len(title)):
            # required order title, epurl, published, description, storage, series title
            container = (title[i], epurl[i], published[i], desc[i], storage[i], seriestitle)
            parsed_list.append(container)
            if len(container) != 6:
                print("ERROR", title[i], epurl[i], published[i], desc[i], storage[i], seriestitle)
            #print("Parsed_episodes: container: {} List: {}\n".format(len(container), len(parsed_list)))

        gc = GetCalls()
        gc._insert_episodes(parsed_list)


    def ep_path(self, title, episodename):
        """
        Creates path for filename when data is created on local storage
        """
        home = os.path.expanduser("~")
        podcast_dir = os.path.join(home, "Music", "Podcasts", title)
        if not os.path.isdir(podcast_dir):
            os.makedirs(podcast_dir)

        pd_complete = os.path.join(podcast_dir, episodename)
        return pd_complete


    def parse_episodes_from_feed(self):
        """
        Takes the feed parser object and takes out the required information. Then kicks it to the database
        :return:
        """
        title = ()
        epurl = ()
        published = ()
        desc = ()
        storage = ()
        seriestitle = self.feed.feed.title

        parsed_list = []

        for en, f in enumerate(self.feed.entries): # gets out required information and sorts it into personal tuple.

             # checks if there. If so puts it in the tuple
            try:
                title += (f.title, )
            except IndexError as e:
                title +=("No title given", )

            try:
                 epurl += (f.links[1]["href"],)
                 url = f.links[1]["href"]
                 pie = url.split("/")[-1]
                 if ".mp3" in pie:
                    if pie.endswith(".mp3"):
                        pieces = pie
                    else:
                        parts = pie.split(".mp3")[0]
                        pieces = parts + ".mp3"

            except IndexError as e:
                epurl += ("No episode url present",)

            try:
                published += (f.published, )
            except IndexError as e:
                published +=("Publish date invalid", )

            try:
                z = self.strip_tags(f.content[0]["value"])
                desc += (z, )
            except IndexError as e:
                desc += ("Description unavailable", )

            storage += (self.ep_path(seriestitle, pieces),) # sticks the storage path into the proper tuple.
            #print(title[en], "|", epurl[en], "|", published[en], "|", desc[en], "|", self.ep_path(seriestitle, title[en]), "|", seriestitle)

        for i in range(0, len(title)):
            # required order title, epurl, published, description, storage, series title
            container = (title[i], epurl[i], published[i], desc[i], storage[i], seriestitle)
            parsed_list.append(container)
            if len(container) != 6:
                print("ERROR", title[i], epurl[i], published[i], desc[i], storage[i], seriestitle)
            #print("Parsed_episodes: container: {} List: {}\n".format(len(container), len(parsed_list)))

        gc = GetCalls()
        gc.insert_episodes(parsed_list)


class GetCalls:
    """
    These are calls that don't require a feed to parse.
    """
    def __init__(self):
        pass

    def get_series(self):
        """
        Returns all lines from podcast.db
        :return:
        """
        try:
            sql = "Select * FROM rssurl"
            conn = sqlite3.connect("podcast\podcast.db")
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            print(rows)
            return rows
        except Exception as e:
            print()
            ex = str(e)
            print(ex, ex.__class__())

    def get_specific_series(self, series):
        """
        Calls to db to return specific rows of rssurl.
        :param series:
        :return:
        """

        try:
            sql = "Select * FROM rssurl Where title in ("+ series +")" # "'option', 'option'"
            conn = sqlite3.connect("podcast\podcast.db")
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            print(rows)
            return rows
        except Exception as e:
            ex = str(e)
            print(ex, ex.__class__())

    def get_specific_episode(self, title):
        """
        SQL to return specific episodes
        :param title:
        :return:
        """
        try:
            sql = "SELECT * FROM episodes ORDER BY datetime(published) WHERE title in (" + title + ")"  # "'option', 'option'"
            conn = sqlite3.connect("podcast\podcast.db")
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            print(rows)
            return rows
        except Exception as e:
            ex = str(e)
            print(ex, ex.__class__())

    def insert_episodes(self, data: list):
        """
        Inserts episodes into db. Needs a list previously parsed.
        :param data:
        :return:
        """
        try:
            insert = []
            select = "Select * FROM episodes"
            sql = "INSERT INTO episodes VALUES(?, ?, ?, ?, ?, ?)"
            conn = sqlite3.connect("podcast\podcast.db")
            cur = conn.cursor()
            cur.execute(select)
            rows = cur.fetchall()
            for d in data:
                if d not in rows:
                    insert.append(d)
            if insert:
                cur.executemany(sql, insert)  # check this to makes sure it's correct
                conn.commit()

                print("Insert Successful: insert_episodes")
                for i in insert:
                    print(i)
            else:
                print("No rows")

        except Exception as e:
            print("Insert failed: insert_episodes")
            a = str(e)
            print(a, a.__class__())

    def _insert_episodes(self, data: list):
        """
        Same as above but with diferent database connection call.
        :param data:
        :return:
        """
        try:
            insert = []
            select = "Select * FROM episodes"
            sql = "INSERT INTO episodes VALUES(?, ?, ?, ?, ?, ?)"
            conn = sqlite3.connect("podcast.db")
            cur = conn.cursor()
            cur.execute(select)
            rows = cur.fetchall()
            for d in data:
                if d not in rows:
                    insert.append(d)
            if insert:
                cur.executemany(sql, insert)  # check this to makes sure it's correct
                conn.commit()

                print("Insert Successful: insert_episodes")
                for i in insert:
                    print(i)
            else:
                print("No rows")

        except Exception as e:
            print("Insert failed: insert_episodes")
            a = str(e)
            print(a, a.__class__())

    def get_episodes(self, series):
        """
        Recalls episodes from specific series using an "in" statement in the sql
        :param series:
        :return:
        """

        try:
            sql = "Select * FROM episodes where seriestitle in (" + series + ")"
            conn = sqlite3.connect("podcast\podcast.db")
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            if rows:
                for i in rows:
                    print(i)
            else:
                print("get_episodes: No rows")
            return rows
        except Exception as e:
            ex = str(e)
            print("get_episodes FAILED:", ex, ex.__class__())

    def download_ep(self, stor_location, url):
        """
        This was going to be a super complex download call. Ended up not working
        Meh.
        """

        self.download()



    def download(self, stor, url):
        """
        The actual download call.
        :param stor:
        :param url:
        :return:
        """
        sess = requests.get(url)
        print("Downloading!")
        with open(stor, "wb") as fn:
            for chunk in sess.iter_content(chunk_size=1024):

                if chunk:
                    fn.write(chunk)
        return

    def read_podcasts(self):
        """
        Used for bulk insert of rss feeds. I got tired of having to delete and reinsert them
        This made things easier.
        :return:
        """
        with open("scratch.txt", "rt") as scr:
            data = scr.readlines()
            for d in data:
                d = d.strip()
                fp = feedparser.parse(d)

                sql = sqlPython(fp)
                sql._info_update()
                sql._parse_episodes_from_feed()


class UpdateMp3:
    """
    I was trying to create custom id3 tags and strip away the old ones
    This wasn't exactly Successful and probably a waste of time.
    """

    def __init__(self, filepath):
        self.fp = filepath

    def id3_strip(self):
        m = MP3(self.fp)
        try:
            m.delete()
            m.save()
            print("ID3 tags deleted.")
            return
        except Exception as e:
            print(str(e))



if __name__ == "__main__":
    import feedparser

    s = sqlPython(feedparser.parse("http://feeds.wnyc.org/radiolab"))
    s.infoGrabber()

# gc = GetCalls()
# gc.get_specific_series("This American Life")