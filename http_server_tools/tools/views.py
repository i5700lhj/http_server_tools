# -*- coding: utf-8 -*-
"""User views."""
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

import os
import re
import json
import stat
import mimetypes
from werkzeug import secure_filename

ignored = ['.bzr', '$RECYCLE.BIN', '.DAV', '.DS_Store', '.git', '.hg',
           '.htaccess', '.htpasswd', '.Spotlight-V100', '.svn', '__MACOSX',
           'ehthumbs.db', 'robots.txt', 'Thumbs.db', 'thumbs.tps']


ALLOWED_EXTENSIONS = set(['zip', 'rar', 'json'])


blueprint = Blueprint(
    "tools",
    __name__,
    url_prefix="/tools",
    static_folder="../static")

root = r"C:\Users\xl\Documents\http_server_tools\http_server_tools\tmp"
UPLOAD_FOLDER = r"C:\Users\xl\Documents\http_server_tools\http_server_tools\tmp"


@blueprint.route("/download", methods=["GET", "POST"])
@blueprint.route("/<path:p>", methods=["GET", "POST"])
@login_required
def tools_download(p=''):
    current_app.logger.info("in get! method=%s" % request.method)
    hide_dotfile = request.args.get(
        'hide-dotfile',
        request.cookies.get(
            'hide-dotfile',
            'no'))

    path = os.path.join(root, p)
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
            'tools/download.html',
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


def post(p=''):
    current_app.logger.info("in post!")
    path = os.path.join(root, p)
    info = {}
    if os.path.isdir(path):
        files = request.files.getlist('files[]')
        for file in files:
            try:
                filename = secure_filename(file.filename)
                file.save(os.path.join(path, filename))
            except Exception as e:
                info['status'] = 'error'
                info['msg'] = str(e)
            else:
                info['status'] = 'success'
                info['msg'] = 'File Saved'
    else:
        info['status'] = 'error'
        info['msg'] = 'Invalid Operation'
    res = make_response(json.JSONEncoder().encode(info), 200)
    res.headers.add('Content-type', 'application/json')
    return res


def get_type(mode):
    if stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
        type = 'dir'
    else:
        type = 'file'
    return type


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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@blueprint.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # UPLOAD_FOLDER = './upload_dir/'
            # CreateNewDir()
            global UPLOAD_FOLDER
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return redirect(url_for('tools.uploaded_file',
                                    filename=filename))
    return render_template("tools/upload.html")


@blueprint.route('/uploaded', methods=['GET', 'POST'])
@login_required
def uploaded_file():
    return redirect(url_for('tools.tools_download'))