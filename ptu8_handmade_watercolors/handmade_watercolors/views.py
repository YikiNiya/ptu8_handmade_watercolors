from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from . import models
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . forms import OrderForm, ProductReviewForm
from .templatetags.cart_tags import get_cart_items, get_cart_total_price
from django.db.models import Avg
from django.contrib.auth.mixins import LoginRequiredMixin


def home(request):
    products = models.Product.objects.all()
    categories = models.Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'handmade_watercolors/home.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(models.Product, pk=product_id)
    average_rating = models.ProductReview.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    context = {
        'product': product,
        'average_rating': average_rating,
    }
    return render(request, 'handmade_watercolors/product_detail.html', context)

@login_required
def add_review(request, product_id):
    product = get_object_or_404(models.Product, pk=product_id)
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', pk=product.id)
    else:
        form = ProductReviewForm()
    return render(request, 'handmade_watercolors/review.html', {'form': form, 'product': product})

class ProductListView(generic.ListView):
    model = models.Product
    template_name = 'handmade_watercolors/product_list.html'
    context_object_name = 'products'
    paginate_by = None

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('search')
        if query:
            queryset = queryset.filter(
                Q(name__istartswith=query) | Q(description__istartswith=query)
            )
        queryset = queryset.annotate(avg_rating=Avg('reviews__rating'))
        return queryset

    def product_list(request):
        queryset = models.Product.objects
        query = request.GET.get('search')
        if query:
            queryset = queryset.filter(
                Q(name__istartswith=query) | Q(description__istartswith=query)
            )
        paginator = Paginator(queryset, 10)
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


class OrderView(LoginRequiredMixin, generic.ListView):
    model = models.Order
    template_name = 'handmade_watercolors/orders.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(customer__user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = context[self.context_object_name]
        order_items = []
        for order in orders:
            items = models.OrderItem.objects.filter(order=order)
            order_items.append({
                'order': order,
                'items': items,
            })
        context['order_items'] = order_items
        return context


class OrderDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Order
    template_name = 'handmade_watercolors/order_detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(customer=self.request.user.customer)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        order_items = order.orderitem_set.all()
        context['order_items'] = order_items
        context['total'] = sum(item.get_total_price() for item in order_items)
        return context


    
class CheckoutView(generic.View):
    def post(self, request):
        form = OrderForm(request.POST)
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
        if not cart:
            messages.error(self.request, ('Your cart is empty'))
            return render(request, 'handmade_watercolors/cart.html')
        
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user.customer
            order.order_total = total_price
            order.status = 'pending'
            order.save() 

            for product_id, item in cart.items():
                product = models.Product.objects.get(pk=product_id)
                order_item = models.OrderItem()
                order_item.order = order
                order_item.product = product
                order_item.quantity = item['quantity']
                order_item.price = product.price
                order_item.save()

    
            request.session['cart_items'] = {}
            messages.success(self.request, ('Your order was successfully placed. Thank you!'))
            return redirect('orders')
        else:
            messages.error(self.request, ('There was an error processing your order. Please check the form and try again.'))
            return render(request, 'handmade_watercolors/checkout.html', {'form': form, 'cart': cart, 'cart_items': cart_items, 'total_price': total_price})


class OrderCreateView(generic.CreateView):
    model = models.Order
    form_class = OrderForm
    template_name = 'handmade_watercolors/checkout.html'
    success_url = reverse_lazy('orders') 

    def form_valid(self, form):
        cart_items = self.request.session.get('cart_items', {})
        order = form.save(commit=False)
        order.customer = self.request.user
        order.order_total = sum(item['item_price'] for item in cart_items.values())
        order.status = 'pending'
        if form.is_valid():
            order.save()
            for product_id, item in cart_items.items():
                product = models.Product.objects.get(pk=product_id)
                order_item = models.OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=item['item_price'],
                )
            self.request.session['cart_items'] = {}
            messages.success(self.request, ('Your order was successfully placed. Thank you!'))
            return redirect(self.request, self.template_name, {'form': form})
        else:
            return self.form_invalid(form)
        
    def form_invalid(self, form):
        cart_items = self.request.session.get('cart_items', {})
        return render(self.request, self.template_name, {'form': form, 'cart_items': cart_items})
    
def get_cart_items(self, request):
    cart = request.session.get('cart', {})
    cart_items = []
    for product_id, item in cart.items():
        product = models.Product.objects.get(id=product_id)
        cart_items.append({
            'product': product,
            'quantity': item['quantity'],
            'price': item['price']
        })
    return cart_items
    
@staticmethod
def order_item_total(item):
    return item.quantity * item.product.price
    
def empty_cart(request):
    if not request.session.get('cart'):
        return render(request, 'handmade_watercolors/empty_cart.html')
    request.session['cart'] = {}
    return redirect('products')

@login_required
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
def add_to_cart(request, product_id):
    product = models.Product.objects.get(id=product_id)
    cart = request.session.get('cart', {})
    cart_item = cart.get(str(product_id))
    if cart_item is None:
        cart[str(product_id)] = {'quantity': 1, 'price': str(product.price)}
    else:
        cart_item['quantity'] += 1
        cart[str(product_id)] = cart_item
    request.session['cart'] = cart
    return redirect(reverse('cart'))

@login_required
def update_cart(request, product_id):
    product = models.Product.objects.get(id=product_id)
    cart = request.session.get('cart', {})
    cart_item = cart.get(str(product_id))
    if cart_item is not None:
        quantity = int(request.POST.get('quantity'))
        cart_item['quantity'] = quantity
        cart[str(product_id)] = cart_item
    request.session['cart'] = cart
    return redirect(reverse('cart'))

@login_required
def remove_from_cart(request, product_id):
    product = models.Product.objects.get(id=product_id)
    cart = request.session.get('cart', {})
    cart_item = cart.get(str(product_id))
    if cart_item is not None:
        cart_item['quantity'] -=1
        if cart_item['quantity'] <= 0:
            del cart[str(product_id)]
        else:
            cart[str(product_id)] = cart_item
        request.session['cart'] = cart
    return HttpResponseRedirect(reverse('cart'))

@login_required
def clear_cart(request):
    if request.method == 'POST':
        request.session['cart'] = {}
        return redirect('cart')
    return render(request, 'handmade_watercolors/clear_cart.html')