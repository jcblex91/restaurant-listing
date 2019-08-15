from django import forms

class AggregateForm(forms.Form):
    lat = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'style': 'border-color: blue;',
                'placeholder': 'Write your name here'
            }
        )
    )
    long = forms.CharField(
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
        lat = cleaned_data.get('lat')
        long = cleaned_data.get('long')
        if not lat and not long:
            raise forms.ValidationError('Cannot be left Blank!')