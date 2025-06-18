from django import forms
from .models import StockItem, Ingredient, Recipe
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuItem


class StockItemForm(forms.ModelForm):
    """Форма для добавления товара на склад"""

    class Meta:
        model = StockItem
        fields = ['ingredient', 'restaurant', 'quantity']
        widgets = {
            'ingredient': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'restaurant': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.001',
                'placeholder': 'Введите количество'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].queryset = Ingredient.objects.all().order_by('name')
        self.fields['restaurant'].queryset = Restaurant.objects.all().order_by('name')
        self.fields['ingredient'].empty_label = "Выберите ингредиент..."
        self.fields['restaurant'].empty_label = "Выберите ресторан..."


class QuickIngredientForm(forms.ModelForm):
    """Быстрая форма для создания ингредиента"""

    UNIT_CHOICES = [
        ('кг', 'Килограммы (кг)'),
        ('г', 'Граммы (г)'),
        ('л', 'Литры (л)'),
        ('мл', 'Миллилитры (мл)'),
        ('шт', 'Штуки (шт)'),
        ('уп', 'Упаковки (уп)'),
    ]

    unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Ingredient
        fields = ['name', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название ингредиента'
            })
        }


class RecipeForm(forms.ModelForm):
    """Форма для создания рецептов блюд"""

    class Meta:
        model = Recipe
        fields = ['menu_item', 'ingredient', 'quantity']
        widgets = {
            'menu_item': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'ingredient': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.001',
                'placeholder': 'Количество на 1 порцию'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['menu_item'].queryset = MenuItem.objects.all().order_by('category__name', 'name')
        self.fields['ingredient'].queryset = Ingredient.objects.all().order_by('name')