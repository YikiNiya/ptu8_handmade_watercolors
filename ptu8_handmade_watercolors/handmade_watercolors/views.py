from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.urls import reverse
from django.views import generic
from . import models
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest


def home(request):
    products = models.Product.objects.all()
    categories = models.Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'handmade_watercolors/home.html', context)

def product_detail(request, pk):
    product = get_object_or_404(models.Product, pk=pk)
    reviews = product.reviews.all()
    context = {
        'product': product,
        'reviews': reviews,
    }
    return render(request, 'handmade_watercolors/product_detail.html', context)


class ProductListView(generic.ListView):
    model = models.Product
    template_name = 'handmade_watercolors/product_list.html'
    context_object_name = 'products'
    paginate_by = 5

    def product_list(request):
        queryset = models.Product.objects
        query = request.GET.get('search')
        if query:
            queryset = queryset.filter(
                Q(name__istartswith=query) | Q(description__istartswith=query)
            )
        paginator = Paginator(queryset, 4)
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)
        return render(request, 'handmade_watercolors/product_list.html', {
            'products': products,
            })


class ProductDetailView(generic.DetailView):
    model = models.Product
    template_name = 'handmade_watercolors/product_detail.html'
    context_object_name = 'product'


class CategoryListView(generic.ListView):
    model = models.Category
    template_name = 'handmade_watercolors/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        qs = super().get_queryset()
        subcategory_id = self.request.GET.get('subcategory_id')
        if subcategory_id:
            qs = qs.filter(subcategories__id=subcategory_id)
        query = self.request.GET.get('search')
        if query:
            qs = qs.filter(
                Q(name__istartswith=query)
            )
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subcategories = models.Subcategory.objects.all()
        context.update({'subcategories': subcategories})
        subcategory_id = self.request.GET.get('subcategory_id')
        if subcategory_id:
            subcategory = get_object_or_404(models.Subcategory, id=subcategory_id)
            context.update({'current_subcategory': subcategory})
        return context


class SubcategoryListView(generic.ListView):
    template_name = 'handmade_watercolors/subcategory_list.html'
    context_object_name = 'subcategories'


def add_to_cart(request, pk):
    product = get_object_or_404(models.Product, pk=pk)
    cart = request.session.get('cart', {})
    cart[pk] = cart.get(pk, {'quantity': 0})
    cart[pk]['quantity'] += 1
    request.session['cart'] = cart
    messages.success(request, f'{product.name} has been added to your cart!')
    return redirect(reverse('cart'))

def update_cart(request):
    cart = request.session.get('cart', {})
    for pk, item in cart.items():
        quantity = request.POST.get(f'quantity_{pk}')
        if quantity and quantity.isdigit() and int(quantity) > 0:
            item['quantity']

def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    if pk in cart:
        del cart[pk]
        request.session['cart'] = cart
        messages.success(request, 'Product removed from cart successfully')
    else:
        messages.warning(request, 'Product not found in cart.')
    return redirect('cart')

def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    for product_id, item_data in cart.items():
        product = get_object_or_404(models.Product, id=product_id)
        item_price = product.price * item_data['quantity']
        total_price += item_price
        cart_items.append({
            'product': product,
            'quantity': item_data['quantity'],
            'item_price': item_price,
        })
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }    
    return render(request, 'handmade_watercolors/cart.html', context)

@login_required
def clear_cart(request):
    if request.method == 'POST':
        cart = models.Cart.objects.get(user=request.user)
        cart.delete()
        return redirect('cart')
    return render(request, 'handmade_watercolors/clear_cart.html')