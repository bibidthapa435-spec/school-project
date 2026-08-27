from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import AdmissionApplication, ContactMessage
import re


class AdmissionApplicationForm(forms.ModelForm):
    class Meta:
        model = AdmissionApplication
        fields = [
            'student_name', 'dob', 'gender', 'father_name', 'mother_name',
            'address', 'phone', 'email', 'class_applying', 'previous_school',
            'photo', 'documents'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Remove form-control from file inputs
        self.fields['photo'].widget.attrs.update({'class': 'form-control'})
        self.fields['documents'].widget.attrs.update({'class': 'form-control'})
    
    def clean_student_name(self):
        name = self.cleaned_data.get('student_name')
        if len(name.strip()) < 3:
            raise ValidationError("Student name must be at least 3 characters long.")
        return name.strip()
    
    def clean_father_name(self):
        name = self.cleaned_data.get('father_name')
        if len(name.strip()) < 3:
            raise ValidationError("Father's name must be at least 3 characters long.")
        return name.strip()
    
    def clean_mother_name(self):
        name = self.cleaned_data.get('mother_name')
        if len(name.strip()) < 3:
            raise ValidationError("Mother's name must be at least 3 characters long.")
        return name.strip()
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Remove any spaces or dashes
        phone_clean = re.sub(r'[\s-]', '', phone)
        
        # Validate phone number format (Nepal format: 9XXXXXXXXX or +9779XXXXXXXXX)
        if not re.match(r'^(\+977)?9\d{9}$', phone_clean):
            raise ValidationError("Please enter a valid Nepal mobile number (e.g., 98XXXXXXXX or +97798XXXXXXXX)")
        
        return phone_clean
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Basic email validation
            if '@' not in email or '.' not in email.split('@')[-1]:
                raise ValidationError("Please enter a valid email address.")
        return email
    
    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # Validate file size (max 2MB)
            if photo.size > 2 * 1024 * 1024:
                raise ValidationError("Photo size must be less than 2MB.")
            
            # Validate file type
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
            ext = photo.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise ValidationError("Photo must be a JPG, PNG, or GIF image.")
        return photo
    
    def clean_documents(self):
        documents = self.cleaned_data.get('documents')
        if documents:
            # Validate file size (max 5MB)
            if documents.size > 5 * 1024 * 1024:
                raise ValidationError("Document size must be less than 5MB.")
            
            # Validate file type
            valid_extensions = ['pdf', 'jpg', 'jpeg', 'png']
            ext = documents.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise ValidationError("Document must be a PDF or Image file.")
        return documents


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name.strip()) < 2:
            raise ValidationError("Name must be at least 2 characters long.")
        return name.strip()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email address is required.")
        
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise ValidationError("Please enter a valid email address.")
        
        return email.strip()
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any spaces or dashes
            phone_clean = re.sub(r'[\s-]', '', phone)
            
            # Validate phone number format (more flexible for international)
            if not re.match(r'^\+?[\d\s-]{10,15}$', phone_clean):
                raise ValidationError("Please enter a valid phone number.")
            
            return phone_clean
        return phone
    
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if len(subject.strip()) < 5:
            raise ValidationError("Subject must be at least 5 characters long.")
        return subject.strip()
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message.strip()) < 10:
            raise ValidationError("Message must be at least 10 characters long.")
        return message.strip()