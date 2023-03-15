from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from . import models
from django.core.paginator import Paginator
from django.db.models import Q


def home(request):
    products = models.Product.objects.filter(status='available').order_by('name')
    categories = models.Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'handmade_watercolors/home.html', context)


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


class ProductDetailView(generic.DeleteView):
    model = models.Product
    template_name = 'handmade_watercolors/product_detail.html'
    context_object_name = 'product'

    def product_detail(request, product_id):
        product = get_object_or_404(models.Product, id=product_id)
        return render(request, 'handmade_watercolors/product_detail.html', {
            'product': product,
        })


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
