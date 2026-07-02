from django import forms
from .models import OrganDonationConsent

ORGANS = [
    ('heart', 'Heart'),
    ('lungs', 'Lungs'),
    ('kidneys', 'Kidneys'),
    ('liver', 'Liver'),
    ('pancreas', 'Pancreas'),
    ('corneas', 'Corneas'),
    ('skin', 'Skin'),
    ('bone_marrow', 'Bone Marrow'),
]

class OrganDonationForm(forms.ModelForm):
    organs = forms.MultipleChoiceField(
        choices=ORGANS,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = OrganDonationConsent
        fields = [
            'full_name', 'age', 'blood_group', 'address',
            'organs', 'emergency_contact_name',
            'emergency_contact_phone', 'consent'
        ]
