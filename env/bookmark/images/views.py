import redis
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from .models import Image
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from actions.utils import create_action

# Connect to Redis (protocol=2 for RESP2 compatibility)
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    protocol=2
)


@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image', new_item)
            messages.success(request, 'Image added successfully')
            return redirect(new_item.get_absolute_url())
    else:
        # Build form with data provided by the bookmarklet via GET
        form = ImageCreateForm(data=request.GET)
    return render(
        request,
        'images/image/create.html',
        {'section': 'images', 'form': form}
    )


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # Increment total image views by 1 and increment score in sorted set
    try:
        total_views = r.incr(f'image:{image.id}:views')
        r.zincrby('image_ranking', 1, image.id)
    except (redis.exceptions.RedisError, redis.ConnectionError, redis.TimeoutError):
        total_views = None

    return render(
        request,
        'images/image/detail.html',
        {
            'section': 'images',
            'image': image,
            'total_views': total_views
        }
    )


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or (hasattr(request, 'is_ajax') and request.is_ajax()):
            # If the request is AJAX and the page is out of range return an empty response
            return HttpResponse('')
        # If page is out of range deliver last page of results
        images = paginator.page(paginator.num_pages)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or (hasattr(request, 'is_ajax') and request.is_ajax()):
        return render(
            request,
            'images/image/list_ajax.html',
            {'section': 'images', 'images': images}
        )
    return render(
        request,
        'images/image/list.html',
        {'section': 'images', 'images': images}
    )


@login_required
def image_ranking(request):
    # Get image ranking dictionary (top 10 image IDs by views)
    try:
        image_ranking = r.zrevrange('image_ranking', 0, -1)[:10]
        image_ranking_ids = [int(id) for id in image_ranking]
        most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
        # Sort objects in Python to preserve the Redis ranking order
        most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    except (redis.exceptions.RedisError, redis.ConnectionError, redis.TimeoutError):
        most_viewed = []

    return render(
        request,
        'images/image/ranking.html',
        {
            'section': 'images',
            'most_viewed': most_viewed
        }
    )
