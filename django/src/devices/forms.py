from typing import Any, Dict
from django import forms
import logging

class PluginFileForm(forms.Form):
    file = forms.FileField()

    def clean(self) -> Dict[str, Any]:
        cleaned_data=super(PluginFileForm,self).clean()
        file=cleaned_data.get("file")

        extension:str=file.name.rpartition('.')

        if extension[2] != "ztp":
            logging.error("Not a valid plugin file: "+file.name)
            raise forms.ValidationError("Not a valid plugin file")