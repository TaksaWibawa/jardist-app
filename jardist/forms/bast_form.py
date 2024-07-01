from django import forms
from jardist.models.contract_models import SPK, PK

class BASTForm(forms.ModelForm):
    spk_instance = forms.ModelChoiceField(queryset=SPK.objects.all(), empty_label='Pilih No. SPK', widget=forms.Select(attrs={'class': 'form-control', 'id': 'spk_instance'}), label='No. SPK')

    class Meta:
        model = PK
        fields = ['pk_number', 'bast_date']
        widgets = {
            'pk_number': forms.TextInput(attrs={'class': 'form-control', 'id': 'pk_number'}),
            'bast_date': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'id': 'bast_date', 'type': 'date', 'required': True}),
        }
        labels = {
            'pk_number': 'No. PK',
            'bast_date': 'Pilih Tanggal BAST I',
            'end_date': 'Tanggal Berakhir PK',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['spk_instance'].initial = self.instance.spk