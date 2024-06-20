from django import forms
from jardist.models import PK, SPK

class PKForm(forms.ModelForm):
    spk = forms.ModelChoiceField(queryset=SPK.objects.all(), empty_label='Pilih No. SPK', widget=forms.Select(attrs={'class': 'form-control', 'id': 'spk'}), label='No. SPK')

    class Meta:
        model = PK
        fields = ['spk', 'pk_number', 'start_date', 'end_date', 'execution_time', 'maintenance_time']
        widgets = {
            'pk_number': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]+', 'id': 'pk_number', 'placeholder': 'Isi No. PK (Angka saja)'}), 
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'start_date', 'placeholder': 'Pilih Tanggal PK'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'end_date', 'placeholder': 'Pilih Tanggal Berakhir PK'}),
            'execution_time': forms.NumberInput(attrs={'class': 'form-control', 'id': 'execution_time', 'min': 0, 'placeholder': 'Isi Waktu Pelaksanaan Dalam Hari Kalender'}),
            'maintenance_time': forms.NumberInput(attrs={'class': 'form-control', 'id': 'maintenance_time', 'min': 0, 'placeholder': 'Isi Masa Pemeliharaan Dalam Hari Kalender'}),
        }
        labels = {
            'pk_number': 'No. PK',
            'start_date': 'Tanggal PK',
            'end_date': 'Tanggal Berakhir PK',
            'execution_time': 'Waktu Pelaksanaan',
            'maintenance_time': 'Waktu Pemeliharaan',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        spk_id = kwargs.pop('spk_id', None)
        is_create_page = kwargs.pop('is_create_page', False)
        super(PKForm, self).__init__(*args, **kwargs)

        if is_create_page:
            self.fields['spk'].queryset = SPK.objects.filter(is_without_pk=False)

        if spk_id:
            try:
                spk = SPK.objects.get(id=spk_id)
                self.fields['spk'].initial = spk

                if spk.is_without_pk:
                    pk = PK.objects.filter(spk=spk).first()
                    self.fields['pk_number'].initial = pk.pk_number.split('-')[1]
                    self.fields['start_date'].initial = pk.start_date.strftime('%Y-%m-%d')
                    self.fields['end_date'].initial = pk.end_date.strftime('%Y-%m-%d')
                    self.fields['execution_time'].initial = pk.execution_time
                    self.fields['maintenance_time'].initial = pk.maintenance_time

            except SPK.DoesNotExist:
                pass

    def clean_pk_number(self):
        spk = self.cleaned_data.get('spk')
        pk_number = self.cleaned_data.get('pk_number')
        pk_number_db_format_spk = f'SPK-{pk_number}'
        pk_number_db_format_pk = f'PK-{pk_number}'
    
        if spk and spk.is_without_pk:
            try:
                pk = PK.objects.get(spk=spk, pk_number__in=[pk_number_db_format_spk, pk_number_db_format_pk])
                for key, value in self.cleaned_data.items():
                    setattr(pk, key, value)
                pk.save()
            except PK.DoesNotExist:
                raise forms.ValidationError("Nomor PK tidak ditemukan")
        elif spk:
            pk_exists = PK.objects.filter(spk=spk, pk_number__in=[pk_number_db_format_spk, pk_number_db_format_pk])

            if pk_exists:
                spk_with_same_pk = pk_exists.first().spk
                raise forms.ValidationError(f"Nomor PK {pk_number} sudah digunakan pada {spk_with_same_pk.spk_number}")
    
        return pk_number

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
            raise forms.ValidationError('Tanggal Berakhir harus lebih besar dari Tanggal Mulai')
        return cleaned_data
    