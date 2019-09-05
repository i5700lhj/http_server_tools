# -*- coding: utf-8 -*-
"""
!/usr/bin/python3
@CreateDate   : 2019-09-04
@Author      : jet
@Filename : views.py
@Software : pycharm

report forms.
"""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from flask_login import current_user



class ReportForm(FlaskForm):
    """Report form."""

    hostname = StringField(
        "Host name", validators=[DataRequired(), Length(min=13, max=22)]
    )
    podname = StringField(
        "Pod name", validators=[DataRequired()]
    )
    metricname = StringField(
        "Metric name", validators=[DataRequired()]
    )
    queryperiod = StringField(
        "Query period", validators=[DataRequired()]
    )



    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(ReportForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(ReportForm, self).validate()
        if not initial_validation:
            return False
        return True

