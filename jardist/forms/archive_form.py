from django import forms
from django.forms import inlineformset_factory
from jardist.models.contract_models import Document, PKArchiveDocument, PK

class PKSelectForm(forms.Form):
    pk_instance = forms.ModelChoiceField(queryset=PK.objects.all(), label='No. PK', widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pk_instance'].empty_label = 'Pilih No. PK'

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['pickup_file', 'pickup_description', 'proof_file', 'proof_description']
        widgets = {
            'pickup_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg, .jpeg, .png, .pdf', 'required': True}),
            'pickup_description': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Reservasi atau Kode 7'}),
            'proof_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg, .jpeg, .png, .pdf'}),
            'proof_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Faktur Pengambilan'}),
        }
        labels = {
            'pickup_file': 'Dokumen Pengambilan Barang',
            'pickup_description': 'Keterangan',
            'proof_file': 'Bukti Pengambilan Barang',
            'proof_description': 'Keterangan',
        }

DocumentFormSet = inlineformset_factory(
    parent_model=PKArchiveDocument,
    model=Document,
    form=DocumentForm,
    extra=1,
    can_delete=True,
)