# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-09-04
@Author      : jet
@Filename : views.py
@Software : pycharm

report views
"""
import os
import re
import stat
import mimetypes


from flask import (
    Blueprint,
    current_app,
    render_template,
    make_response,
    request,
    Response,
    send_file,
    flash,
    redirect,
    url_for
)
from flask_login import login_required

from http_server_tools.report.forms import ReportForm
from http_server_tools.report.prom_report import PerformanceReport

blueprint = Blueprint(
    "report",
    __name__,
    url_prefix="/tools",
    static_folder="../static")

ignored = ['.bzr', '$RECYCLE.BIN', '.DAV', '.DS_Store', '.git', '.hg',
           '.htaccess', '.htpasswd', '.Spotlight-V100', '.svn', '__MACOSX',
           'ehthumbs.db', 'robots.txt', 'Thumbs.db', 'thumbs.tps']

BASE_DIR = str(os.path.dirname(os.path.dirname(__file__)))
BASE_DIR = BASE_DIR.replace('\\', '/')

ROOT_FOLDER = BASE_DIR + "/report/report_files"
BACKUP_FOLDER = BASE_DIR + "/report/report_files/backup"
UPLOAD_FILE_NAME = ""
CURRENT_FOLDER = ""


@blueprint.route('/report/', methods=['GET', 'POST'])
@login_required
def report():
    # 进入报告生成工具界面后，先清理ROOT_FOLDER目录中文件
    del_files(ROOT_FOLDER)
    form = ReportForm(request.form)
    if request.method == "POST":
        query_url = "http://%s/api/v1/query?query=%s[%s]" % (
            form.data["hostname"], form.data["metricname"], form.data["queryperiod"])
        _res = PerformanceReport().gen_single_report(
            query_url, form.data["metricname"])
        if "OK" != _res:
            flash("Query faild! Response data: %s" % _res, 'warning')
            return render_template("tools/to_report.html", form=form)
        return redirect(url_for('report.report_download'))

    return render_template("tools/to_report.html", form=form)


@blueprint.route('/report/history', methods=['GET', 'POST'])
@login_required
def history():
    return report_download(ROOT_FOLDER)


@blueprint.route("/report/report_download", methods=["GET", "POST"])
@blueprint.route("/report/<path:p>", methods=["GET", "POST"])
@login_required
def report_download(p=ROOT_FOLDER):
    current_app.logger.info("in get! method=%s" % request.method)
    hide_dotfile = request.args.get(
        'hide-dotfile',
        request.cookies.get(
            'hide-dotfile',
            'no'))

    path = os.path.join(ROOT_FOLDER, p)
    if os.path.isdir(path):
        contents = []
        total = {'size': 0, 'dir': 0, 'file': 0}
        for filename in os.listdir(path):
            if filename in ignored:
                continue
            if hide_dotfile == 'yes' and filename[0] == '.':
                continue
            filepath = os.path.join(path, filename)
            stat_res = os.stat(filepath)
            info = {}
            info['name'] = filename
            info['mtime'] = stat_res.st_mtime
            ft = get_type(stat_res.st_mode)
            info['type'] = ft
            total[ft] += 1
            sz = stat_res.st_size
            info['size'] = sz
            total['size'] += sz
            contents.append(info)
        page = render_template(
            'tools/report_download.html',
            path=p,
            contents=contents,
            total=total,
            hide_dotfile=hide_dotfile)
        res = make_response(page, 200)
        res.set_cookie('hide-dotfile', hide_dotfile, max_age=16070400)
    elif os.path.isfile(path):
        if 'Range' in request.headers:
            start, end = get_range(request)
            res = partial_response(path, start, end)
        else:
            res = send_file(path)
            res.headers.add('Content-Disposition', 'attachment')
    else:
        res = make_response('Not found', 404)
    return res


def get_type(mode):
    if stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
        type = 'dir'
    else:
        type = 'file'
    return type


def get_range(request):
    range = request.headers.get('Range')
    m = re.match(r'bytes=(?P<start>\d+)-(?P<end>\d+)?', range)
    if m:
        start = m.group('start')
        end = m.group('end')
        start = int(start)
        if end is not None:
            end = int(end)
        return start, end
    else:
        return 0, None


def partial_response(path, start, end=None):
    file_size = os.path.getsize(path)

    if end is None:
        end = file_size - start - 1
    end = min(end, file_size - 1)
    length = end - start + 1

    with open(path, 'rb') as fd:
        fd.seek(start)
        bytes = fd.read(length)
    assert len(bytes) == length

    response = Response(
        bytes,
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True,
    )
    response.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(
            start, end, file_size,
        ),
    )
    response.headers.add(
        'Accept-Ranges', 'bytes'
    )
    return response

# 仅删除指定目录下所有文件，不涉及子目录


def del_files(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            pass
        else:
            os.remove(c_path)
