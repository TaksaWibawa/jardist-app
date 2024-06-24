from django import forms
from jardist.models.contract_models import SPK

class SPKForm(forms.ModelForm):
    class Meta:
        model = SPK
        fields = ['spk_number', 'start_date', 'end_date', 'execution_time', 'maintenance_time', 'is_without_pk']
        widgets = {
            'spk_number': forms.TextInput(attrs={'class': 'form-control', 'id': 'spk_number', 'placeholder': 'Isi No. SPK'}), 
            'start_date': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date', 'id': 'start_date', 'placeholder': 'Pilih Tanggal SPK'}),
            'end_date': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date', 'id': 'end_date', 'placeholder': 'Pilih Tanggal Berakhir SPK'}),
            'execution_time': forms.NumberInput(attrs={'class': 'form-control', 'id': 'execution_time', 'min': 0, 'placeholder': 'Isi Waktu Pelaksanaan Dalam Hari Kalender'}),
            'maintenance_time': forms.NumberInput(attrs={'class': 'form-control', 'id': 'maintenance_time', 'min': 0, 'placeholder': 'Isi Masa Pemeliharaan Dalam Hari Kalender'}),
            'is_without_pk': forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': 'checkbox', 'id': 'is_without_pk'})
        }
        labels = {
            'spk_number': 'No. SPK',
            'start_date': 'Tanggal SPK',
            'end_date': 'Tanggal Berakhir SPK',
            'execution_time': 'Waktu Pelaksanaan',
            'maintenance_time': 'Waktu Pemeliharaan',
            'is_without_pk': 'Centang jika SPK tanpa PK'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.is_create_page = kwargs.pop('is_create_page', False)
        super(SPKForm, self).__init__(*args, **kwargs)

    def clean_spk_number(self):
        spk_number = self.cleaned_data.get('spk_number')

        if self.is_create_page and SPK.objects.filter(spk_number=spk_number).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('No. SPK sudah ada')

        return spk_number

    def clean_execution_time(self):
        execution_time = self.cleaned_data['execution_time']
        if execution_time < 0:
            raise forms.ValidationError('Waktu Pelaksanaan tidak boleh minus')
        return execution_time
    
    def clean_maintenance_time(self):
        maintenance_time = self.cleaned_data['maintenance_time']
        if maintenance_time < 0:
            raise forms.ValidationError('Waktu Pemeliharaan tidak boleh minus')
        return maintenance_time
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and (start_date >= end_date):
            self.add_error('end_date', 'Tanggal Berakhir harus lebih besar dari Tanggal SPK')
            raise forms.ValidationError('Tanggal Berakhir harus lebih besar dari Tanggal SPK')
        return cleaned_data