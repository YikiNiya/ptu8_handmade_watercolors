from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from . import models
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . forms import OrderForm, ProductReviewForm
from .templatetags.cart_tags import get_cart_items, get_cart_total_price


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
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductReviewForm()
    return render(request, 'handmade_watercolors/review.html', {'form': form, 'product': product})

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


class OrderView(generic.View):
    def get(self, request):
        customer = request.session.get('customer')
        orders = models.Order.objects.filter(customer=customer)
        return render(request, 'handmade_watercolors/orders.html', {'orders': orders})



    # def get_checkout(self, request):
    #     form = OrderForm()
    #     if request.user.is_authenticated:
    #         try:
    #             customer = models.Customer.objects.get(user=request.user)
    #         except models.Customer.DoesNotExist:
    #             # Create a new Customer model object for the request.user
    #             customer = models.Customer(user=request.user)
    #             customer.save()
    #         cart_items = models.CartItem.objects.filter(cart__customer=customer)
    #         return render(request, 'handmade_watercolors/checkout.html', {'form': form, 'cart_items': cart_items})
    #     return redirect('login')
class CheckoutView(generic.View):
    def get_checkout(self, request):
        cart_items = get_cart_items(request)
        total_price = get_cart_total_price(request.session.get('cart', {}))
        context = {'cart_items': cart_items, 'total_price': total_price}
        return render(request, 'handmade_watercolors/checkout.html', context)
        
        
        # form = OrderForm()
        # customer = models.Customer.objects.get(user=request.user)
        # cart_items = []
        # cart = request.session.get('cart', {})
        # for product_id, item_data in cart.items():
        #     product = get_object_or_404(models.Product, id=product_id)
        #     item_price = product.price * item_data['quantity']
        #     cart_items.append({
        #         'product': product,
        #         'quantity': item_data['quantity'],
        #         'item_price': item_price,
        #     })
        # return render(request, 'handmade_watercolors/checkout.html', {'form': form, 'cart_items': cart_items})

        
    
    def post(self, request):
        form = OrderForm(request.POST)
        if form.is_valid():
            cart_items = request.session.get('cart_items', {})
            order = models.Order()
            order.customer = request.user
            order.customer_email = form.cleaned_data['email']
            order.order_total = sum(item['item_price'] for item in cart_items.values())
            order.status = 'pending'
            order.save()
            for product_id, item in cart_items.items():
                product = models.Product.objects.get(pk=product_id)
                order_item = models.OrderItem()
                order_item.order = order
                order_item.product = product
                order_item.quantity = item['quantity']
                order_item.price = item['item_price']
                order_item.save()
            request.session['cart_items'] = {}
            message = 'Your order was successfully placed. Thank you!'
            return render(request, 'handmade_watercolors/checkout.html', {'form': form, 'message': message})
        else:
            cart_items = request.session.get('cart_items', {})
            return render(request, 'handmade_watercolors/checkout.html', {'form': form, 'cart_items': cart_items})
            
@staticmethod
def order_item_total(item):
    return item.quantity * item.product.price

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