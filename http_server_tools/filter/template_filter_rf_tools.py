import humanize
from datetime import datetime

icontypes = {'fa-music': 'm4a,mp3,oga,ogg,webma,wav', 'fa-archive': '7z,zip,rar,gz,tar',
             'fa-picture-o': 'gif,ico,jpe,jpeg,jpg,png,svg,webp', 'fa-file-text': 'pdf',
             'fa-film': '3g2,3gp,3gp2,3gpp,mov,qt',
             'fa-code': 'atom,plist,bat,bash,c,cmd,coffee,css,hml,js,json,java,less,markdown,md,php,pl,py,rb,rss,sass,scpt,swift,scss,sh,xml,yml',
             'fa-file-text-o': 'txt', 'fa-film': 'mp4,m4v,ogv,webm', 'fa-globe': 'htm,html,mhtm,mhtml,xhtm,xhtml'}

datatypes = {'audio': 'm4a,mp3,oga,ogg,webma,wav', 'archive': '7z,zip,rar,gz,tar',
             'image': 'gif,ico,jpe,jpeg,jpg,png,svg,webp', 'pdf': 'pdf',
             'quicktime': '3g2,3gp,3gp2,3gpp,mov,qt',
             'source': 'atom,bat,bash,c,cmd,coffee,css,hml,js,json,java,less,markdown,md,php,pl,py,rb,rss,sass,scpt,swift,scss,sh,xml,yml,plist',
             'text': 'txt', 'video': 'mp4,m4v,ogv,webm',
             'website': 'htm,html,mhtm,mhtml,xhtm,xhtml'}


def size_fmt(size):
    return humanize.naturalsize(size)


def time_desc(timestamp):
    mdate = datetime.fromtimestamp(timestamp)
    str = mdate.strftime('%Y-%m-%d %H:%M:%S')
    return str


def time_humanize(timestamp):
    # 将当前时间转换为UTC标准时间
    # mdate = datetime.utcfromtimestamp(timestamp)
    # 转换当前时间
    mdate = datetime.fromtimestamp(timestamp)
    return humanize.naturaltime(mdate)


def icon_fmt(filename):
    i = 'fa-file-o'
    for icon, exts in icontypes.items():
        if filename.split('.')[-1] in exts:
            i = icon
    return i

def data_fmt(filename):
    t = 'unknown'
    for type, exts in datatypes.items():
        if filename.split('.')[-1] in exts:
            t = type
    return t