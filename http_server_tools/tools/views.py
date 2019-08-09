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
# from http_server_tools.utils import flash_errors
from http_server_tools.generate.generate_to_rf import GenerateRF

import os
import re
import json
import shutil
import time
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

BASE_DIR = str(os.path.dirname(os.path.dirname(__file__)))
BASE_DIR = BASE_DIR.replace('\\', '/')

ROOT_FOLDER = BASE_DIR + "/generate/files"
BACKUP_FOLDER = BASE_DIR + "/generate/files/backup"
UPLOAD_FILE_NAME = ""
CURRENT_FOLDER = ""


@blueprint.route('/cards', methods=['GET', 'POST'])
@login_required
def cards():
    return render_template("tools/tools.html")


@blueprint.route("/download", methods=["GET", "POST"])
@blueprint.route("/<path:p>", methods=["GET", "POST"])
@login_required
def tools_download(p=ROOT_FOLDER):
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
    path = os.path.join(ROOT_FOLDER, p)
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


# 删除指定目录下所有文件，子果有子目录，则递归删除所有子目录下文件
def del_folder_files(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_folder_files(c_path)
        else:
            os.remove(c_path)


# 仅删除指定目录下所有文件，不涉及子目录
def del_files(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            pass
        else:
            os.remove(c_path)


@blueprint.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    # 进入上传文件界面，清理UPLOAD_FOLDER目录
    del_files(ROOT_FOLDER)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'warning')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file', 'warning')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            global UPLOAD_FILE_NAME
            UPLOAD_FILE_NAME = secure_filename(file.filename)
            # UPLOAD_FOLDER = './upload_dir/'
            # CreateNewDir()
            # global UPLOAD_FOLDER
            file.save(os.path.join(ROOT_FOLDER, UPLOAD_FILE_NAME))
            flash('Upload file %s SUCCESS !!!' % UPLOAD_FILE_NAME, 'success')
            return redirect(url_for('tools.uploaded_file',
                                    filename=UPLOAD_FILE_NAME))
        else:
            flash('Only support zip/rar/json file upload!!!', 'warning')
    return render_template("tools/upload.html")


@blueprint.route('/uploaded', methods=['GET', 'POST'])
@login_required
def uploaded_file():
    # return redirect(url_for('tools.tools_download'))
    return render_template("tools/to_rf_main.html")


@blueprint.route('/history', methods=['GET', 'POST'])
@login_required
def history():
    return tools_download(ROOT_FOLDER)


@blueprint.route('/generate', methods=['GET', 'POST'])
@login_required
def to_rf_main():
    _template_folder = BASE_DIR + "/generate/generate_template"
    _upload_file_names = []
    if "" == UPLOAD_FILE_NAME:
        flash('Pls upload file!!!', 'warning')
        return render_template("tools/upload.html")
    elif "json" == UPLOAD_FILE_NAME[-4:]:
        # 将postman导出的json文件转换成RF关键字
        current_app.logger.info(
            "in to_rf_main! UPLOAD_FILE_NAME=%s" %
            UPLOAD_FILE_NAME)
        # 已上传的postman脚本导出文件路径
        pcj = ROOT_FOLDER + "/" + UPLOAD_FILE_NAME
        # 生成RF关键字脚本存放目录
        rfp = ROOT_FOLDER
        # 生成rf关键字文件的模板文件
        tfdn_kw = _template_folder + "/rf_template_kw.txt"
        # 生成rf关键字模板文件中的settings模板
        tfdn_settings = _template_folder + "/rf_template_kw_settings.txt"
        grf = GenerateRF()
        rf_file = grf.generate_rf_kw_from_postman(
            pcj, tfdn_kw, tfdn_settings, rfp)
        _mlist = rf_file.split('/')
        rf_file_name = _mlist[len(_mlist) - 1]
        _upload_file_names.append(rf_file_name)
        shutil.copy(
            rf_file,
            "%s/%s.%s.bak" %
            (BACKUP_FOLDER,
             rf_file_name,
             time.strftime(
                 '%Y%m%d%H%M%S',
                 time.localtime(
                     time.time()))))

        # 将postman导出的json文件转换成与生成RF关键字相匹配的测试用例脚本
        # 生成RF测试用例脚本文件的模板文件
        tfdn_case = _template_folder + "/template_testcase.txt"
        # 生成RF测试用例脚本文件模板文件中，变量定义的模板
        tfdn_var = _template_folder + "/template_testcase_variables.txt"
        rf_case_file = grf.generate_rf_case_from_postman(
            pcj, tfdn_case, tfdn_settings, tfdn_var, rfp)
        _mlist = rf_case_file.split('/')
        rf_case_file_name = _mlist[len(_mlist) - 1]
        _upload_file_names.append(rf_case_file_name)
        shutil.copy(
            rf_file,
            "%s/%s.%s.bak" %
            (BACKUP_FOLDER,
             rf_case_file_name,
             time.strftime(
                 '%Y%m%d%H%M%S',
                 time.localtime(
                     time.time()))))

    # 显示出已生成文件名称
    flash('Generate file %s successfully!!!' %
          ','.join(_upload_file_names), 'info')
    # 转到上传、下载文件目录
    # return tools_download(UPLOAD_FOLDER)
    return redirect(url_for('tools.tools_download'))
