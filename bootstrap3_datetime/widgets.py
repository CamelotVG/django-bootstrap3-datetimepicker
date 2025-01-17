# -*- coding: utf-8 -*-
import json

from django.forms.utils import flatatt
from django.forms.widgets import DateTimeInput
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_text


class DateTimePicker(DateTimeInput):
    # http://momentjs.com/docs/#/parsing/string-format/
    # http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
    format_map = (
        ('DDD', r'%j'),
        ('DD', r'%d'),
        ('MMMM', r'%B'),
        ('MMM', r'%b'),
        ('MM', r'%m'),
        ('YYYY', r'%Y'),
        ('YY', r'%y'),
        ('HH', r'%H'),
        ('hh', r'%I'),
        ('mm', r'%M'),
        ('ss', r'%S'),
        ('a', r'%p'),
        ('ZZ', r'%z'),
    )

    @classmethod
    def conv_datetime_format_py2js(cls, format):
        for js, py in cls.format_map:
            format = format.replace(py, js)
        return format

    @classmethod
    def conv_datetime_format_js2py(cls, format):
        for js, py in cls.format_map:
            format = format.replace(js, py)
        return format

    html_template = """
    <div%(div_attrs)s>
      <input%(input_attrs)s/>
      <span class="input-group-addon">
        <span%(icon_attrs)s></span>
      </span>
    </div>"""

    js_template = """
    <script>
      $(function(){
        $("#%(picker_id)s:has(input:not([readonly],[disabled]))").datetimepicker(%(options)s);
      });
    </script>"""

    def __init__(self, attrs=None, format=None, options=None, div_attrs=None, icon_attrs=None):
        if not icon_attrs:
            icon_attrs = {'class': 'glyphicon glyphicon-calendar'}
        if not div_attrs:
            div_attrs = {'class': 'input-group date'}
        if format is None and options and options.get('format'):
            format = self.conv_datetime_format_js2py(options.get('format'))
        super(DateTimePicker, self).__init__(attrs, format)
        if 'class' not in self.attrs:
            self.attrs['class'] = 'form-control'
        self.div_attrs = div_attrs and div_attrs.copy() or {}
        self.icon_attrs = icon_attrs and icon_attrs.copy() or {}
        self.picker_id = self.div_attrs.get('id') or None
        if options == False:  # datetimepicker will not be initalized when options is False
            self.options = False
        else:
            self.options = options and options.copy() or {}
            if format and not self.options.get('format') and not self.attrs.get('date-format'):
                self.options['format'] = self.conv_datetime_format_py2js(format)

    def render(self, name, value, attrs=None, *args, **kwargs):
        if value is None:
            value = ''

        extra_attrs = dict(
            type=self.input_type,
            name=name
        )
        input_attrs = self.build_attrs(attrs, extra_attrs)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            input_attrs['value'] = force_text(self._format_value(value))
        input_attrs = {key: conditional_escape(val) for key, val in input_attrs.items()}
        if not self.picker_id:
             self.picker_id = (input_attrs.get('id', '') +
                               '_pickers').replace(' ', '_')
        self.div_attrs['id'] = self.picker_id
        picker_id = conditional_escape(self.picker_id)
        div_attrs = {key: conditional_escape(val) for key, val in self.div_attrs.items()}
        icon_attrs = {key: conditional_escape(val) for key, val in self.icon_attrs.items()}
        html = self.html_template % dict(div_attrs=flatatt(div_attrs),
                                         input_attrs=flatatt(input_attrs),
                                         icon_attrs=flatatt(icon_attrs))
        if self.options:
            js = self.js_template % dict(picker_id=picker_id, options=json.dumps(self.options or {}))
        else:
            js = ''
        return mark_safe(force_text(html + js))
