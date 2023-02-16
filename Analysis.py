from atexit import register, unregister, _run_exitfuncs
from os import walk, mkdir

from tqdm import tqdm

from msgs import _setup, chmkdir


# noinspection PyBroadException
class Analysis(object):
    """
    Takes a .csv file and runs analysis on it based on the header found in the file.
    """

    def __init__(self, file):
        """Initiates the class"""
        (self.ids,
         self.authors,
         self.servers,
         self.channels,
         self.content_length,
         self.content) = ([], [], [], [], [], [])
        # this makes the 6 lists needed for the different rows that (might) be present
        (self.most_server,
         self.most_channel,
         self.most_author,
         self.most_content,
         self.most_content_length,
         self.average_length) = (None,) * 6
        # this passes the inspection where all attributes have to be defined in __init__
        self.logger = _setup("Analysis_%s" % file.split('App\\')[-1].replace("\\", "_"), "Logs", False, False)
        # The methods debug, info, warning, error, critical, and exception are assigned to the class instead of
        # having to be called through self.logger.x
        self.exc = self.exception = self.logger.exception  # most used
        self.debug = self.logger.debug
        self.info = self.logger.info
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical
        self.full_dir = file
        (self.folder_path,
         self.report) = ('', '')
        for i in self.full_dir.split("\\")[:-1]:
            self.folder_path += i + '\\'
        self.f = open(file, 'r', encoding="utf-8")

        @register
        def close_file():
            """
            This function is registered to an atexit function. It closes the file on exit.
            """
            self.f.close()

        self.close_file = close_file
        self.header = self.f.readlines(1)[0][:-1]
        self.parts = self.header.split(",")
        self._parts = self.parts
        self.parts.remove("ID")
        self.logger.info("Header: %s", self.header)

    def author_append_lists(self, row):
        if row[-1] == '\n':
            row = row[:-1]
        a, b, c, d, e = row.split(",")
        try:
            if int(d) != 0:
                self.ids.append(a)
                self.servers.append(b)
                self.channels.append(c)
                self.content_length.append(int(d))
                self.content.append(e)
        except ValueError:
            self.logger.exception("Value %s is not a valid integer", d)
        except Exception:
            self.logger.exception()

    def author_all(self):
        if self.header == "ID,Server,Channel,Content Length,Content":
            for i in tqdm(self.f.readlines()):
                self.author_append_lists(i)

    def server_all(self):
        if self.header == "ID,Author,Channel,Content Length,Content":
            for i in tqdm(self.f.readlines()):
                self.server_append_lists(i)

    def author_channel_all(self):
        if self.header == "ID,Author,Content Length,Content":
            for i in tqdm(self.f.readlines()):
                self.author_channel_append_lists(i)

    def channel_all(self):
        if self.header == "ID,Content Length,Content":
            for i in tqdm(self.f.readlines()):
                self.only_channel_append_lists(i)

    @staticmethod
    def check_biggest_count(d: dict):
        """Checks a dictionary for the item with the biggest number value"""
        big = ("null", 0)
        for a, b in d.items():
            if b > big[1]:
                big = (a, b)
        return big

    def count_and_check_entries_in_list(self, l):
        d = {}
        for i in set(l):
            d[i] = 0
        for i in tqdm(l):
            if i != '0':
                d[i] += 1
        return self.check_biggest_count(d)

    def check_list(self, l):
        if len(l) > 0:
            return self.count_and_check_entries_in_list(l)
        else:
            return None

    def check_without_empty_entries(self, l):
        nl = [i for i in l if i != '']
        return self.check_list(nl)

    def stats(self):
        self.most_server = self.check_list(self.servers)
        self.most_channel = self.check_list(self.channels)
        self.most_author = self.check_list(self.authors)
        self.most_content_length = self.check_list(self.content_length)
        self.most_content = self.check_without_empty_entries(self.content)

    def average_content_length(self):
        try:
            self.average_length = round(sum(self.content_length) / len(self.content_length), 0)
        except ZeroDivisionError:
            self.logger.exception("Content-Length: %s, Sum: %s, Len: %s",
                                  str(self.content_length), sum(self.content_length), len(self.content_length))

    def format_into_report(self):
        if self.most_server is not None:
            try:
                self.report += 'Favorite Server: %s with %d counts\n' % self.most_server
            except Exception:
                self.logger.exception("Error! self.most_server = %s, self.report = %s",
                                      str(self.most_server), self.report)
        if self.most_author is not None:
            try:
                self.report += 'Most Active Person: %s with %d counts\n' % self.most_author
            except Exception:
                self.logger.exception("Error! self.most_author = %s, self.report = %s",
                                      str(self.most_author), self.report)
        if self.most_channel is not None:
            try:
                self.report += 'Most Used Channel: %s with %d counts\n' % self.most_channel
            except Exception:
                self.logger.exception("Error! self.most_channel = %s, self.report = %s",
                                      str(self.most_channel), self.report)
        if self.most_content_length is not None:
            try:
                self.report += 'Favorite Message Length: %s with %d counts\n' % self.most_content_length
            except Exception:
                self.logger.exception("Error! self.most_content_length = %s, self.report = %s",
                                      str(self.most_content_length), self.report)
        if self.most_content is not None:
            try:
                self.report += 'Favorite Message: %s with %d counts\n' % self.most_content
            except Exception:
                self.logger.exception("Error! self.most_content = %s, self.report = %s",
                                      str(self.most_content), self.report)
        if self.average_length is None:
            try:
                self.average_content_length()
            except Exception:
                self.logger.exception("Content Length could not be calculated, average_length = %s",
                                      str(self.average_length))
        try:
            self.report += 'Average Content Length: %d characters\n' % self.average_length
        except Exception:
            self.logger.exception("Content Length could not be added, average_length = %s", str(self.average_length))

    def server_append_lists(self, row):
        if row[-1] == '\n':
            row = row[:-1]
        a, b, c, d, e = row.split(",")
        try:
            if int(d) != 0:
                self.ids.append(a)
                self.authors.append(b)
                self.channels.append(c)
                self.content_length.append(int(d))
                self.content.append(e)
        except ValueError:
            self.logger.exception("Value %s is not a valid integer", d)
        except Exception:
            self.logger.exception()

    def author_channel_append_lists(self, row):
        if row[-1] == '\n':
            row = row[:-1]
        a, b, c, d = row.split(",")
        try:
            if int(c) != 0:
                self.ids.append(a)
                self.authors.append(b)
                self.content_length.append(int(c))
                self.content.append(d)
        except ValueError:
            self.logger.exception("Value %s is not a valid integer", c)
        except Exception:
            self.logger.exception()

    def only_channel_append_lists(self, row):
        if row[-1] == '\n':
            row = row[:-1]
        a, b, c = row.split(",")
        try:
            if int(b) != 0:
                self.ids.append(a)
                self.content_length.append(int(b))
                self.content.append(c)
        except ValueError:
            self.logger.exception("Value %s is not a valid integer", b)
        except Exception:
            self.logger.exception()

    def run_all_analysis(self):
        self.author_all()
        self.server_all()
        self.author_channel_all()
        self.channel_all()
        self.all_all()

    def run_all_all(self):
        self.run_all_analysis()
        self.stats()
        self.average_content_length()
        self.format_into_report()
        self.save_to_new_file()
        self.close_file()
        unregister(self.close_file)

    def save_to_new_file(self):
        chmkdir(self.folder_path.replace("App", "Reports\\App"), self.logger)
        with open(self.full_dir.replace("App", "Reports\\App").replace('csv', 'txt'), 'w', encoding='utf-8') as file:
            file.write(self.report)

    def all_all(self):
        if self.header == "ID,Author,Server,Channel,Content Length,Content":
            for a, i in tqdm(enumerate(self.f.readlines())):
                self.all_append_lists(i, a)

    def all_append_lists(self, row, rnum):
        if row[-1] == '\n':
            row = row[:-1]
        try:
            a, b, c, d, e, f = row.split(",")
        except Exception:
            self.logger.exception("Row: %s, Split Row: %s, R#: %d", row, row.split("\n"), rnum)
        try:
            if int(e) != 0:
                self.ids.append(a)
                self.authors.append(b)
                self.servers.append(c)
                self.channels.append(d)
                self.content_length.append(int(e))
                self.content.append(f)
        except ValueError:
            self.logger.exception("Value %s is not a valid integer", e)
        except Exception:
            self.logger.exception("")


def main():
    for a, b, c in tqdm(list(walk("App"))):
        for i in tqdm(c):
            path = a + '\\' + i
            if '.csv' in path:
                try:
                    Analysis(path).run_all_all()
                except OSError:
                    _run_exitfuncs()
                    Analysis(path).run_all_all()


if __name__ == '__main__':
    try:
        mkdir("Logs")
    except FileExistsError:
        pass
    main()
