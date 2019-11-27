import sqlite3 as lite


class DbConnection:
    """
    Connects to database for the initial call and creates - File & table.
    I was going to use it as a persistent db connection, but it caused too many problems
    Ended up doing open statements where needed instead.
    """
    def _init_(self):

        if __name__ == "__main__":
            self.database = "podcast.db"
        else:
            self.database = "podcast\podcast.db"

        self.conn = ""
        self.cur = ""

    def db_connection(self):
        try:
            self.conn = lite.connect(self.database)
            self.cur = self.conn.cursor()
            self.create_tables()
        except AttributeError as e:
            print(str(e))

    def create_tables(self):

        rss_urls = """Create Table if not exists rssurl (title text PRIMARY KEY, website text, rsshref text, subtitle text, dateadded text NOT NULL)"""
        eps_urls = """Create Table if not exists episodes(title text NOT NULL, epurl text, published text NOT NULL, description text, storage text, seriestitle text)"""
        try:
            if self.cur != None:
                self.cur.execute(rss_urls)
                self.cur.execute(eps_urls)
                self.conn.commit()
            else:
                print()

        except Exception as e:
            self.conn.close()

    def get_conn(self):
        return self.conn

    def get_cur(self):
        return self.cur

    def main(self):

        self.db_connection()
        #self.create_tables()
