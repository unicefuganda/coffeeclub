from django.forms.models import ModelForm
from django import forms
from .models import CoffeeOrder, Customer, CustomerPref, MenuItem, EmailAlert, MessageContent

class MenuItemForm(ModelForm):
    class Meta:
        model = MenuItem


#TODO forms for managing groups e.g. departments, clubs, etc. (something generic)

class OrderForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['customer'].widget.attrs['class'] = 'autocomplete'
        self.fields['customer'].help_text = "start typing to see available customers"
        self.fields['coffee_name'].widget.attrs['class'] = 'autocomplete'
        self.fields['coffee_name'].help_text = "start typing to see available Menu Items"

    class Meta:
        model = CoffeeOrder
        exclude = ('date')
        fields = ('customer', 'coffee_name', 'num_cups', 'deliver_to')

class CustomerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['groups'].widget.attrs['class'] = 'autocomplete'
        self.fields['groups'].label = "Group"
        self.fields['groups'].help_text = "start typing to see available groups"
    class Meta:
        model = Customer
        exclude = ('language', 'user', 'user_permissions', 'reporting_location', 'preferences')
    def clean(self):
        cleaned_data = self.cleaned_data
        if self._errors and 'email' in self._errors:
            raise forms.ValidationError("Email already exists")
        else:
            return cleaned_data


class PrefrencesForm(ModelForm):
    class Meta:
        model = CustomerPref

class UploadForm(forms.Form):
    excel_file = forms.FileField(label="Excel File", required=True)
    def clean(self):
        excel = self.cleaned_data.get('excel_file', None)
        if excel and excel.name.rsplit('.')[1] != 'xls':
                msg = u'Upload valid excel file !!!'
                self._errors["excel_file"] = ErrorList([msg])
                return ''
        return self.cleaned_data

class PrefrencesForm(ModelForm):
    class Meta:
        model = CustomerPref

class EmailForm(ModelForm):
    class Meta:
        model = EmailAlert

class NewsletterForm(forms.Form):
    customers = forms.MultipleChoiceField(choices=(('', 'All Members'),) + tuple(Customer.objects.values_list('email', 'name').order_by('name')))
    subject = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size': 20, 'title': 'Newsletter Title', }))
    message = forms.Textarea()
