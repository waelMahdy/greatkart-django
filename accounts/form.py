from django import forms

from accounts.models import Account

class RegisterationForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Enter password','class' : 'form-control'}))
    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Enter password','class' : 'form-control'}))

    class Meta:
        model=Account
        fields=['first_name','last_name','phone_number','email']
    def __init__(self,*args,**kwargs): 
        super(RegisterationForm,self).__init__(*args,**kwargs) 
        self.fields['first_name'].widget.attrs['placeholder']='Enter first name'  
        self.fields['last_name'].widget.attrs['placeholder']='Enter last name'
        self.fields['email'].widget.attrs['placeholder']='Enter your email address'  
        self.fields['phone_number'].widget.attrs['placeholder']='Enter your phone number' 
        self.fields['password'].widget.attrs['placeholder']='Enter password'
        self.fields['confirm_password'].widget.attrs['placeholder']='Confirm password'  
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'

    def clean(self):
        cleaned_data=super(RegisterationForm,self).clean()  
        password=cleaned_data.get('password')  
        confirm_password=cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Password and Confirm Password Field do not match !") 
            
