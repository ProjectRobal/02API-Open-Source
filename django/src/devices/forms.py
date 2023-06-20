from typing import Any, Dict
from django import forms

class PluginFileForm(forms.Form):
    file = forms.FileField()

    def clean(self) -> Dict[str, Any]:
        cleaned_data=super(PluginFileForm,self).clean()
        file=cleaned_data.get("file")

        print(file)