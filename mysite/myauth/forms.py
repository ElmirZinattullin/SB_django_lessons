from django.forms import ModelForm, Form
from django.forms.fields import ImageField, URLField, FileField

from myauth.models import Profile


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = 'bio', 'agreement_accepted', 'avatar'
        field_classes = {'avatar': ImageField}
        labels = {'avatar': 'Аватар'}




