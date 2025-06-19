# apps/menu/forms.py
from django import forms
from .models import Category, MenuItem


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'sort_order', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем CSS классы
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

        # Специальные настройки для отдельных полей
        self.fields['description'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Краткое описание категории для посетителей'
        })

        self.fields['sort_order'].widget.attrs.update({
            'min': 0,
            'max': 999,
            'placeholder': '0'
        })


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = [
            'name', 'category', 'description', 'price', 'cost_price',
            'image', 'preparation_time', 'calories', 'weight',
            'is_available', 'is_spicy', 'is_vegetarian', 'is_popular'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Добавляем CSS классы
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

        # Настройки для конкретных полей
        self.fields['name'].widget.attrs.update({
            'placeholder': 'Введите название блюда'
        })

        self.fields['description'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Опишите состав, способ приготовления и особенности блюда'
        })

        self.fields['price'].widget.attrs.update({
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00'
        })

        self.fields['cost_price'].widget.attrs.update({
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00'
        })

        self.fields['preparation_time'].widget.attrs.update({
            'min': '1',
            'max': '300',
            'placeholder': '15'
        })

        self.fields['calories'].widget.attrs.update({
            'min': '0',
            'placeholder': 'Калорийность'
        })

        self.fields['weight'].widget.attrs.update({
            'min': '0',
            'placeholder': 'Вес в граммах'
        })

        # Фильтруем только активные категории
        self.fields['category'].queryset = Category.objects.filter(is_active=True)

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError('Цена должна быть больше нуля')
        return price

    def clean_cost_price(self):
        cost_price = self.cleaned_data.get('cost_price')
        if cost_price and cost_price < 0:
            raise forms.ValidationError('Себестоимость не может быть отрицательной')
        return cost_price

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        cost_price = cleaned_data.get('cost_price')

        if price and cost_price and cost_price > price:
            raise forms.ValidationError(
                'Себестоимость не может быть больше цены продажи'
            )

        return cleaned_data


class MenuItemQuickEditForm(forms.ModelForm):
    """Форма для быстрого редактирования основных параметров блюда"""

    class Meta:
        model = MenuItem
        fields = ['name', 'price', 'is_available', 'is_popular']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control form-control-sm'


class CategoryFilterForm(forms.Form):
    """Форма для фильтрации меню"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по названию блюда...'
        })
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="Все категории",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    AVAILABILITY_CHOICES = [
        ('', 'Все'),
        ('available', 'Доступные'),
        ('unavailable', 'Недоступные'),
    ]

    availability = forms.ChoiceField(
        choices=AVAILABILITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    SORT_CHOICES = [
        ('name', 'По названию'),
        ('price', 'По цене (возр.)'),
        ('-price', 'По цене (убыв.)'),
        ('category__name', 'По категории'),
        ('-created_at', 'Сначала новые'),
    ]

    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='name',
        widget=forms.Select(attrs={'class': 'form-select'})
    )