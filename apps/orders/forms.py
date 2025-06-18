from django import forms
from .models import Order, OrderItem
from apps.menu.models import MenuItem
from apps.restaurants.models import Restaurant


class OrderForm(forms.ModelForm):
    """Форма для создания заказа"""

    class Meta:
        model = Order
        fields = ['restaurant', 'table_number']
        widgets = {
            'restaurant': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'table_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Номер стола'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Если пользователь - менеджер, показываем только его ресторан
        if user and hasattr(user, 'employee') and user.employee.restaurant:
            self.fields['restaurant'].queryset = Restaurant.objects.filter(
                id=user.employee.restaurant.id
            )
            self.fields['restaurant'].initial = user.employee.restaurant


class OrderItemForm(forms.ModelForm):
    """Форма для добавления блюда в заказ"""

    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity']
        widgets = {
            'menu_item': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            })
        }

    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)

        # Показываем только доступные блюда
        self.fields['menu_item'].queryset = MenuItem.objects.filter(
            is_available=True
        ).order_by('category__name', 'name')

        if restaurant:
            # Можно добавить фильтрацию по ресторану если нужно
            pass