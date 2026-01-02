from django import forms 
from django.forms import Form
from student_management_app.models import Grades, AcademicYear


class DateInput(forms.DateInput):
    input_type = "date"


class AddStudentForm(forms.Form):
    first_name = forms.CharField(
        max_length=100, 
        label="First Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter First Name'})
    )
    middle_name = forms.CharField(
        max_length=100, 
        label="Middle Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter Middle Name'})
    )
    last_name = forms.CharField(
        max_length=100, 
        label="Last Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter Last Name'})
    )
    gender = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female')], 
        label="Gender",
        widget=forms.Select(attrs={'placeholder': 'Select Gender'})
    )
    date_of_birth = forms.DateField(
        widget=DateInput(attrs={'placeholder': 'Select Date of Birth'}),
        label="Date of Birth"
    )
    
    address = forms.CharField(  # Changed from residential_address
        label="Address",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter Address'
        })
    )
    
    nationality = forms.CharField(
        max_length=100, 
        label="Nationality",
        initial="Tanzanian",
        widget=forms.TextInput(attrs={'placeholder': 'Enter Nationality'})
    )
    religion = forms.CharField(
        max_length=100, 
        label="Religion",
        widget=forms.TextInput(attrs={'placeholder': 'Enter Religion'})
    )
    disability = forms.ChoiceField(
        choices=[
            ('None', 'None'),
            ('Physical', 'Physical'),
            ('Visual', 'Visual'), 
            ('Hearing', 'Hearing'),
            ('Other', 'Other')
        ],
        label="Disability",
        widget=forms.Select(attrs={'placeholder': 'Select Disability'})
    )
    grade_id = forms.ModelChoiceField(
        queryset=Grades.objects.all(),
        label="Grade",
        widget=forms.Select(attrs={'placeholder': 'Select Grade'})
    )
    stream_id = forms.ModelChoiceField(
        queryset=Grades.objects.all(),
        label="Stream",
        widget=forms.Select(attrs={'placeholder': 'Select Stream'})
    )
    academic_year_id = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all(),
        label="Academic Year",
        widget=forms.Select(attrs={'placeholder': 'Select Academic Year'})
    )
    profile_pic= forms.ImageField(
        label="Profile Picture",
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )



class EditStudentForm(forms.Form):
    first_name = forms.CharField(
        max_length=100, 
        label="First Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter First Name'})
    )
    middle_name = forms.CharField(
        max_length=100, 
        label="Middle Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter Middle Name'})
    )
    last_name = forms.CharField(
        max_length=100, 
        label="Last Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter Last Name'})
    )
    gender = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female')], 
        label="Gender",
        widget=forms.Select(attrs={'placeholder': 'Select Gender'})
    )
    date_of_birth = forms.DateField(
        widget=DateInput(attrs={'placeholder': 'Select Date of Birth'}),
        label="Date of Birth"
    )
    residential_address = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter Residential Address', 'rows': 3}),
        label="Residential Address"
    )
    nationality = forms.CharField(
        max_length=100, 
        label="Nationality",
        widget=forms.TextInput(attrs={'placeholder': 'Enter Nationality'})
    )
    religion = forms.CharField(
        max_length=100, 
        label="Religion",
        widget=forms.TextInput(attrs={'placeholder': 'Enter Religion'})
    )
    disability = forms.ChoiceField(
        choices=[
            ('None', 'None'),
            ('Physical', 'Physical'),
            ('Visual', 'Visual'), 
            ('Hearing', 'Hearing'),
            ('Other', 'Other')
        ],
        label="Disability",
        widget=forms.Select(attrs={'placeholder': 'Select Disability'})
    )
    grade_id = forms.ModelChoiceField(
        queryset=Grades.objects.all(),
        label="Grade",
        widget=forms.Select(attrs={'placeholder': 'Select Grade'})
    )
    stream_id = forms.ModelChoiceField(
        queryset=Grades.objects.all(),
        label="Stream",
        widget=forms.Select(attrs={'placeholder': 'Select Stream'})
    )
    academic_year_id = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all(),
        label="Academic Year",
        widget=forms.Select(attrs={'placeholder': 'Select Academic Year'})
    )
    profile_pic = forms.ImageField(
        label="Profile Picture",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )

   