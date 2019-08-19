from django import forms

class AggregateForm(forms.Form):
    Latitude = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'style': 'border-color: blue;',
                'placeholder': 'Write your name here'
            }
        )
    )
    Longitude = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'style': 'border-color: blue;',
                'placeholder': 'Write your name here'
            }
        )
    )
    Address = forms.CharField(
        required=False,
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'style': 'border-color: blue;',
                'placeholder': 'Write your name here'
            }
        )
    )
    City = forms.CharField(
        required= False,
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'style': 'border-color: blue;',
                'placeholder': 'Write your name here'
            }
        )
    )
    Zip = forms.CharField(
        required=False,
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'style': 'border-color: blue;',
                'placeholder': 'Write your name here'
            }
        )
    )



    def clean(self):
        cleaned_data = super(AggregateForm, self).clean()
        Latitude = cleaned_data.get('Latitude')
        Longitude = cleaned_data.get('Longitude')
        Address = cleaned_data.get('Address')
        City = cleaned_data.get('City')
        Zip = cleaned_data.get('Zip')

        if not Latitude and not Longitude :
            raise forms.ValidationError('Cannot be left Blank!')

class WhatsappForm(forms.Form):
    ID = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'style': 'border-color: blue;',
                'placeholder': 'Write your name here'
            }
        )
    )
    Whatsapp = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'style': 'border-color: blue;',
                'placeholder': 'Write your name here'
            }
        )
    )




    def clean(self):
        cleaned_data = super(WhatsappForm, self).clean()
        ID = cleaned_data.get('ID')
        Whatsapp = cleaned_data.get('Whatsapp')

        if not ID and not Whatsapp :
            raise forms.ValidationError('Cannot be left Blank!')