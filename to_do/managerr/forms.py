#managerr/forms.py
from django import forms  
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем минимальную дату в HTML
        today = timezone.now().date().isoformat()
        self.fields['due_date'].widget.attrs['min'] = today

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now().date():
            raise ValidationError("Deadline cannot be in the past")
        return due_date