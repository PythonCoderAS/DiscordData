import logging  # the logging commands
import logging.handlers  # used for logging
import os
from datetime import datetime

import aiofiles
import aiohttp
import discord
import halo
from colorlog import ColoredFormatter  # used for logging

from login import email, password


def _setup(name='PokestarBot', dir=None, append=True, _stream=True):
    if dir is not None:
        os.chdir(dir)
    log_format = "[%(log_color)s%(asctime)s%(reset)s] {%(log_color)s%(pathname)s:%(lineno)d%(reset)s} | " \
                 "%(log_color)s%(levelname)s%(reset)s : %(log_color)s%(message)s%(reset)s"  # idk
    file_format = "[%(asctime)s] {%(pathname)s:%(lineno)d}|%(levelname)s : %(message)s"  # same as log_format but
    # doesn't have the coloring
    formatter = ColoredFormatter(log_format)
    stream = logging.StreamHandler()
    stream.setLevel(logging.INFO)
    stream.setFormatter(formatter)
    log = logging.getLogger(name)

    log.setLevel(logging.DEBUG)
    if _stream:
        log.addHandler(stream)

    fn = r'%s_app.log' % name
    if not append:
        if os.path.isfile(fn):
            while os.path.isfile(fn):
                fn = '_' + fn
    fh = logging.FileHandler(fn, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(fmt=file_format))
    log.addHandler(fh)

    if dir is not None:
        os.chdir("..")
    return log

if __name__ == '__main__':
    logger = _setup()
    os.chdir("App")
    cs = aiohttp.ClientSession()
    


def multmkdir(dir, logger):
    parts = dir.split('\\')
    s = ''
    for i in parts:
        s += i + '\\'
        try:
            os.mkdir(s)
            logger.info("Folder %s created", s)
        except FileExistsError:
            pass


def chmkdir(name, lgr=None):
    try:
        if lgr is None:
            lgr = logger
        multmkdir(name, lgr)
    except FileExistsError:
        pass


if __name__ == '__main__':
    # chmkdir("Servers")
    # chmkdir("Authors")
    chmkdir("Attachments")


def check_if_exists(filename, heading, text):
    try:
        with open(filename, 'x', encoding='utf-8') as file:
            heading = heading if heading[-1] == '\n' else heading + '\n'
            file.write(heading)
            logger.info("File %s created with heading %s", filename, heading.replace("\n", ""))
    except FileExistsError:
        pass
    finally:
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(text)
            #logger.info("%s had %s written to it",filename,text)


client = discord.Client()


def return_csv_form(*args):
    s = ""
    for i in args:
        s += str(i).replace(",", "_").replace('\n', "NL") + ','
    s = s[:-1]
    s += '\n'
    return s


async def format_msg(m):
    _id = m.id
    s = m.server
    server = s.name if s is not None else 'DM'
    channel = m.channel.name
    author = m.author.name
    content = m.content
    content_length = len(content)
    """
    server_dir = "Servers\\%s" % server
    server_dir = server_dir.replace("/", "_").replace(",", "_").replace(":", "_")
    server_all = server_dir + '\\all.csv'
    channel_dir = server_dir + '\\%s.csv' % channel
    author_dir = "Authors\\%s" % author
    author_dir = author_dir.replace("/", "_").replace(".", "_").replace("|", "_")
    author_all = author_dir + '\\all.csv'
    author_server_dir = author_dir + '\\' + server_dir
    author_server_all = author_server_dir + '\\all.csv'
    author_server_channel = author_dir + '\\' + channel_dir
    """
    with open("all_all.csv", "a", encoding='utf-8') as a:
        a.write(return_csv_form(_id, author, server, channel, content_length, content))
    # """
    attachments = 'Attachments\\' + server
    attachments = attachments.replace("/", "_").replace(",", "_").replace(":", "_")
    chmkdir(attachments)
    for a, i in enumerate(m.attachments):
        async with cs.get(i['url']) as f:
            file = await aiofiles.open(attachments + '\\' + str(_id) + '_' + str(a) + '.png', mode='wb')
            await file.write(await f.read())
    # """
    """
    chmkdir(server_dir)
    check_if_exists(server_all, "ID,Author,Channel,Content Length,Content",
                    return_csv_form(_id, author, channel, content_length, content))
    check_if_exists(channel_dir, "ID,Author,Content Length,Content",
                    return_csv_form(_id, author, content_length, content))
    chmkdir(author_dir)
    check_if_exists(author_all, "ID,Server,Channel,Content Length,Content",
                    return_csv_form(_id, server, channel, content_length, content))
    chmkdir(author_server_dir)
    check_if_exists(author_server_all, "ID,Channel,Content Length,Content",
                    return_csv_form(_id, channel, content_length, content))
    check_if_exists(author_server_channel, "ID,Content Length,Content", return_csv_form(_id, content_length, content))
    """


@client.event
async def on_ready():
    print("Ready!")


# noinspection PyGlobalUndefined,PyBroadException
@client.event
async def on_message(message):
    if (datetime.now() - now).seconds < 600:
        try:
            await format_msg(message)
            # logger.info(count)
            # count += 1
        except Exception:
            logger.exception("Message with id %s could not formatted", message.id)
    else:
        logger.warning("10 minutes have passed, exiting")
        os._exit(0)


if __name__ == '__main__':
    now = datetime.now()
    h = halo.Halo()
    h.start()
    client.run(email, password)
