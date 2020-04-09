from student.models import user
from django import forms

class userform(forms.ModelForm):
    class Meta:
        model=user
        fields=("barcode_no","password")