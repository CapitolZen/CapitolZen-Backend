from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class JSONEditorWidget(forms.Widget):
    """
    Adds https://github.com/josdejong/jsoneditor to any json 
    field in the admin area.
    """
    template_name = 'widgets/jsoneditor.html'

    def render(self, name, value, attrs=None, renderer=None):
        context = {
            'data': value,
            'name': name
        }

        return mark_safe(render_to_string(self.template_name, context))
