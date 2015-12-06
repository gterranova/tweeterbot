# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.template import Context
from django.template.loader import get_template
from django import template

from django.conf import settings
#from django_select2.forms import Select2Widget, Select2MultipleWidget
#from html_field.forms.widgets import HTMLWidget

register = template.Library()

@register.filter
def bootstrap(element):
    markup_classes = {'label': '', 'value': '', 'single_value': ''}
    return render(element, markup_classes).encode('utf-8')


@register.filter
def bootstrap_inline(element):
    markup_classes = {'label': 'sr-only', 'value': '', 'single_value': ''}
    return render(element, markup_classes)


@register.filter
def bootstrap_horizontal(element, label_cols='col-sm-2 col-lg-2'):

    markup_classes = {'label': label_cols, 'value': '', 'single_value': ''}
    BOOTSTRAP_COLUMN_COUNT = getattr(settings, 'BOOTSTRAP_COLUMN_COUNT', 2)

    for cl in label_cols.split(' '):
        splitted_class = cl.split('-')

        try:
            value_nb_cols = int(splitted_class[-1])
        except ValueError:
            value_nb_cols = BOOTSTRAP_COLUMN_COUNT

        if value_nb_cols >= BOOTSTRAP_COLUMN_COUNT:
            splitted_class[-1] = '%d' % BOOTSTRAP_COLUMN_COUNT
        else:
            offset_class = cl.split('-')
            offset_class[-1] = 'offset-%d' % value_nb_cols
            splitted_class[-1] = '%d' % (BOOTSTRAP_COLUMN_COUNT - value_nb_cols)
            markup_classes['single_value'] += ' ' + '-'.join(offset_class)
            markup_classes['single_value'] += ' ' + '-'.join(splitted_class)

        markup_classes['value'] += ' ' + '-'.join(splitted_class)

    return render(element, markup_classes)

@register.filter
def add_input_classes(field):
    if not is_checkbox(field) and not is_multiple_checkbox(field) \
       and not is_radio(field) and not is_file(field):
        field_classes = field.field.widget.attrs.get('class', '')
        if 'form-control' not in field_classes:
            field_classes += ' form-control'
        field.field.widget.attrs['class'] = field_classes


def render(element, markup_classes):
    element_type = element.__class__.__name__.lower()
    if element_type == 'boundfield':
        add_input_classes(element)
        template = get_template("bootstrapform/field.html")
        context = {'field': element, 'classes': markup_classes, 'form': element.form}
    else:
        has_management = getattr(element, 'management_form', None)
        if 0: #if has_management:
            for form in element.forms:
                for field in form.visible_fields():
                    add_input_classes(field)

            template = get_template("bootstrapform/formset.html")
            context = Context({'formset': element, 'classes': markup_classes})
        if 1: #else:
            for field in element.visible_fields():
                add_input_classes(field)

            template = get_template("bootstrapform/form.html")
            context = {'form': element, 'classes': markup_classes}

    return template.render(context)


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxInput)


@register.filter
def is_multiple_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxSelectMultiple)


@register.filter
def is_radio(field):
    return isinstance(field.field.widget, forms.RadioSelect)


@register.filter
def is_file(field):
    return isinstance(field.field.widget, forms.FileInput)

#@register.filter
#def is_multiple_select2(field):
#    return isinstance(field.field.widget, Select2MultipleWidget)

#@register.filter
#def is_select2(field):
#    return isinstance(field.field.widget, Select2Widget)    

#@register.filter
#def is_html(field):
#    return isinstance(field.field.widget, HTMLWidget)        
