#!/usr/bin/env python3
# coding: latin-1

from io import StringIO
from datetime import datetime
import sys, os, signal, logging
from urllib.error import HTTPError
from urllib.request import Request, urlopen


# ================ constants
PROJ = {'name'      : 'pyarxiver',
        'version'   : '1.00',
        'author'    : 'compy',
        'page'      : 'https://github.com/com-py/',
        'license'   : 'https://creativecommons.org/licenses/by-nc-sa/4.0/',
        'desc'      : 'Python Youtube Arxiver - record from any point of live streams'}

vid_fmts = {'144p': '256x144',     # video format dictionary
            '240p': '426x240',
            '360p': '640x360',
            '480p': '854x480',
            '720p': '1280x720',
            '1080p': '1920x1080'}
vidfmt = vid_fmts['720p']   # default resolution

retries = 2     # retries on http error
fragdir = 'fragsdir'
prefix = 'f720p.frag'
yellow = "\033[33m"
coloff = "\033[0m"

hdrs = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'}
ytube = 'https://www.youtube.com/watch?v='


# ================ define modules
"""    
    quit, highlight, terminate, download_data, get_m3u8, parser, get_seq, cal_time_back
"""

def quit(text):
    msg.error(highlight(text))
    sys.exit()


def highlight(text):    # highlight text with escape sequence
    return yellow + text + coloff


def terminate(signal, frame):       # Ctrl-C handler
    quit('total frags completed: {}'.format(count))
    

def download_data(url, header=False):     # download data as bytes
    retry, data, success = 0, b'', False
    
    try:
        req = Request(url, headers=hdrs if header else {})
    except:
        msg.info('unknown request: {}'.format(url))
        return b'', False
        
    while retry < retries:
        retry += 1
        try:
            data = urlopen(req, timeout=10).read()
        except HTTPError:       # session likely expired
            if retry < retries:
                msg.info('http error ... {}'.format(url[-10:]))
        else:           # successful
            success = True
            break
    
    return data, success


def get_m3u8(data):     # get m3u8 link
    beg = 'https'
    end = 'index.m3u8'
    url = ''
    
    with StringIO(data) as f:
        for eachline in f:
            line = eachline.strip()
            pos2 = line.find(end)
            if pos2 > 0:
                pos1 = line[:pos2].rfind(beg)
                url = line[pos1:pos2] + end
                break
    return url


def parser(data):   # parse master m3u8 for formats and urls
    mark1 = 'RESOLUTION='
    mark2 = 'index.m3u8'
    
    formats, resolution = [], ''
    with StringIO(data) as f:
        for eachline in f:
            line = eachline.strip()
            pos1 = line.find(mark1)
            pos2 = line.find(mark2)
            if pos1 > 0:
                k = pos1 + len(mark1)
                resolution = line[k: k + line[k:].find(',')]
            elif pos2 > 0:
                url = get_m3u8(line)
                formats.append((resolution, url))
    return formats


def get_seq(htmdata):   # get sequence number
    frag_dur = 5        # default, just in case
    curr_frag = 0
    beg, end = 'https', '/sq/'
    url, dur = '', '/dur/'
    
    with StringIO(htmdata) as file:
        for eachline in file:
            line = eachline.strip()
            pos2 = line.find(end)       # look for '/sq/'
            if pos2 > 0:
                pos1 = line.rfind(beg)  # look for url
                if pos1 >=0:
                    j = pos2 + len(end) # end of url
                    url = line[pos1: j]
                    k = j + line[j:].find('/')
                    curr_frag = line[j: k]
                    
                    pos1 = line[k:].find(dur)
                    if pos1 > 0:
                        durstr = line[k + pos1 + len(dur):][:5]
                        if durstr.replace('.','').isdigit():
                            frag_dur = round(float(durstr))
                    break

    return url, curr_frag, frag_dur
    
    
# calculate frag number from time back, timeback format=days:hrs:min
def cal_time_back(timeback, frag_dur):    
    valid = True
    seconds = 0
    factor = [60, 3600, 24*3600]    # secs in one min, hr, day
    maxval = [59, 23, 5]            # maximum values in each field
    
    items = timeback.split(':')
    items.reverse()                 # reverse order in case day is missing
    n = len(items)
    if n < 2:                       # no : separators
        valid = False
    else:
        for i in range(n):
            if items[i].isdigit() and int(items[i]) <= maxval[i]:
                seconds += factor[i] * int(items[i])
            else:
                valid = False
                break
        
    if valid:
        seconds = min(seconds, factor[2]*5) # max time back not to exceed 5 days
        time_back = datetime.fromtimestamp(datetime.now().timestamp() - seconds)
        return seconds//frag_dur, str(time_back)[:-7]     # strip decimal second
    else:
        return 0, None


# ================ config loggger console output
msg = logging.getLogger(PROJ['name'])
logging.basicConfig(level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y.%m.%d %H:%M:%S')
os.system("color")  # enable color output

msg.info(PROJ['name'] + ' (v' + PROJ['version'] + ') - ' + PROJ['desc'])
msg.info(PROJ['page'] + PROJ['name'] + '\n')


# ================ process arguments    
n = len(sys.argv)
if n <2 or n > 4:   # too few or too many args
    why = 'no video link' if n<2 else 'too many parameters'
    quit(why + '\nUsage: ' + sys.argv[0] +
         ' video-link [time-back ([day:]hr:min)]' + ' [resolution (480p or 854x480 ...)]\n'+
         'e.g. download vid-id from now at 720p(default): ' +
         sys.argv[0] + ' ' + ytube + 'vid-id\n' +
         'or download vid-id from 2hr.30min ago at 1080p: ' +
         sys.argv[0] + ' ' + ytube + 'vid-id 2:30 1080p')

vidurl, time_para = '', ''
for arg in sys.argv[1:]:
    if vidurl == '':
        vidurl = arg
        msg.info('video link: {}'.format(vidurl))
    elif arg[-1] == 'p' or arg.find('x') > 0:       # format like 720p, 854x480
        try:
            vidfmt = vid_fmts[arg]      # match standard ones
        except:
            vidfmt = arg    # non-standard

        msg.info('chosen resolution={}'.format(vidfmt))
        prefix = 'f' + arg + '.frag'
    else:                   # store as time back
        if time_para == '':
            time_para = arg
        else:
            msg.info('unknown parameter ignored - {}'.format(arg))


# ================ get response and top level m3u8 link
response, success = download_data(vidurl, True)

if success:
    url = get_m3u8(response.decode("utf-8"))    # get master m3u8 url
    if len(url) == 0:
        quit('No stream info found, check if video link is a LIVE stream.')
else:
    quit('No data read, check if video link is valid'.format(vidurl))


# ================ get all m3u8 formats
data, success = download_data(url, True)

formats = parser(data.decode("utf-8"))

allfmt = ''
fmturl = ''
for fmt in formats:             # select format and actual url
    allfmt += ' ' + fmt[0]
    if vidfmt == fmt[0]:
        fmturl = fmt[1]

msg.info('available formats: {}'.format(allfmt))
if len(fmturl) == 0:    # no standard 
    quit('No standard video format found, choose an available one above')


# ================ get actual video frags link
data, success = download_data(fmturl, True)    
base, curr_frag, frag_dur = get_seq(data.decode("utf-8"))

if (len(base) == 0):
    quit('no stream base url found')

# ================ calc time back if present in args
frag_back = 0
if time_para != '':
    frag_back, timeback = cal_time_back(time_para, frag_dur)
    
if frag_back > 0:
    msg.info('time back to {}, frags back={}, at {} sec/fragment'.format(timeback,
              frag_back, frag_dur))
elif time_para == '':
    msg.info('no time back, start at current time')
else:
    msg.info('invalid time back para ignored - {}, start at current time'.format(time_para))
            
frag = max(int(curr_frag)-frag_back, 0)   # adjust time back

# ================ create new frag dir if necessary
n, newdir = 0, fragdir
while os.path.exists(newdir):       # existing dir must be empty
    if os.path.isdir(newdir) and len(os.listdir(newdir)) == 0:  # ok
        break
    n += 1
    newdir = fragdir + repr(n)
    
if not os.path.exists(newdir):      # must have 'write' permission
    os.makedirs(newdir)

msg.info('downloading resolution {}, to folder {}'.format(vidfmt, newdir))
msg.info('Ctrl-C to stop downloading')

# ================ start downloading
size = 0
count = 0
counter = 60//frag_dur          # update every 60 secs of video
signal.signal(signal.SIGINT, terminate)     # register Ctrl-C handler

while True:
    url = base + repr(frag)
    vidname = prefix + repr(frag) + '.ts'
    vidpath = os.path.join(newdir, vidname)
    
    vdata, success = download_data(url)
    
    if success:
        with open(vidpath, 'wb') as file:
            file.write(vdata)
        
        size += len(vdata)
        count += 1
        if count % counter == 0:    # update status
            vidlen = frag_dur*count
            hr, mn = vidlen//3600, (vidlen%3600)//60
            print('frags done: {}, size: {} (mb), time (hr:min) = {}:{}'.format(count, size//1000000, hr, ('0'+repr(mn))[-2:]), end='\r')
    else:
        terminate(count, count)     # filler args
        
    frag += 1