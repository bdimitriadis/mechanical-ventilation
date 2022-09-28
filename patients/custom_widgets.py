'''
Created on Nov 2, 2018

@author: b.dimitriadis
'''

from django import forms


class ListTextWidget(forms.TextInput):
    """ A widget combining both TextInput and dropdown (select)
    """

    def __init__(self, field_model, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self.field_model = field_model
        self._name = name
        self._list = field_model.objects.all()
        self.attrs.update({'list': 'list__%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        try:
            value = self.field_model.objects.get(**{name: value})
        except self.field_model.DoesNotExist:
            pass
        text_html = super(ListTextWidget, self).render(
            name, value, attrs=attrs)
        data_list = '<datalist id="list__%s">' % self._name
        for item in self._list:
            data_list += '<option value="%s">' % item
        data_list += '</datalist>'

        return (text_html + data_list)
