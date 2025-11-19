import os
import json
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .forms import RegisterForm
from .models import Order, MenuItem
from orders.llm_service import get_llm_response
from .llm_service import get_llm_response

SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY', '').strip()
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '').strip()
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'meta-llama/llama-3.3-70b-instruct')
RESTAURANT_API_URL = os.getenv('RESTAURANT_API_URL', 'https://api.spoonacular.com/recipes/complexSearch').strip()

def home(request):
    if request.user.is_authenticated:
        return redirect('menu')
    return redirect('register')


def profile_view(request):
    return render(request, 'profile.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('menu')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def api_menu(request):
    menu_items = MenuItem.objects.all().values('id', 'name', 'price')
    return JsonResponse(list(menu_items), safe=False)


@login_required
def menu_view(request):
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "query": "veg food",
        "number": 10
    }

    response = requests.get(RESTAURANT_API_URL, params=params)
    menu_items = []

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        for item in results:
            menu_items.append({
                "id": item.get("id", ""),
                "name": item.get("title", "Unnamed Dish"),
                "image": item.get("image", ""),
                "price": 120  
            })
    else:
        print("Error fetching menu:", response.text)

    return render(request, "menu.html", {"menu_items": menu_items})

@csrf_exempt
def api_cart(request):
    cart = request.session.get('cart', [])

    if request.method == 'GET':
        return JsonResponse({'cart': cart})

    payload = json.loads(request.body.decode('utf-8') or '{}')
    action = payload.get('action')
    item = payload.get('item', {})

    if action == 'add':
        found = False
        for it in cart:
            if it['id'] == item['id']:
                it['qty'] += int(item.get('qty', 1))
                found = True
                break
        if not found:
            cart.append({
                'id': item['id'],
                'name': item['name'],
                'price': float(item.get('price', 120)),
                'qty': int(item.get('qty', 1))
            })

    elif action == 'remove':
        cart = [it for it in cart if it['id'] != item['id']]

    elif action == 'update':
        for it in cart:
            if it['id'] == item['id']:
                it['qty'] = int(item.get('qty', it['qty']))

    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({'cart': cart})

@csrf_exempt
def api_order(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    cart = request.session.get('cart', [])
    if not cart:
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    total = sum(it['price'] * it['qty'] for it in cart)

    print("Final cart before order:", cart)

    order = Order.objects.create(
        user=request.user,
        order_json=json.dumps(cart),
        total_amount=total
    )

    request.session['cart'] = []
    request.session.modified = True

    return JsonResponse({'order_id': order.id, 'total': total, 'status': 'success'})

@csrf_exempt
def api_chat(request):
    data = json.loads(request.body.decode("utf-8"))
    user_message = data.get("message", "").strip()

    llm_output = get_llm_response(user_message)
    action = llm_output.get("action")
    item = llm_output.get("item")
    quantity = llm_output.get("quantity", 1)

    cart = request.session.get('cart', [])

    if action == "add_to_cart":
        found = False
        for it in cart:
            if item.lower() in it['name'].lower():
                it['qty'] += quantity
                found = True
                break
        if not found:
            cart.append({"id": len(cart)+1, "name": item.title(), "price": 120, "qty": quantity})

        request.session['cart'] = cart
        request.session.modified = True
        reply = f"Added {quantity} {item}(s) to your cart."
        return JsonResponse({"reply": reply, "cart": cart})

    elif action == "show_cart":
        if not cart:
            return JsonResponse({"reply": "Your cart is empty."})
        items = ", ".join([f"{i['qty']} x {i['name']}" for i in cart])
        total = sum(it['price'] * it['qty'] for it in cart)
        return JsonResponse({"reply": f"Your cart: {items}. Total ₹{total}", "cart": cart})

    elif action == "cancel_order":
        request.session['cart'] = []
        request.session.modified = True
        return JsonResponse({"reply": "Cart cleared.", "cart": []})

    elif action == "confirm_order":
        total = sum(it['price'] * it['qty'] for it in cart)
        request.session['cart'] = []
        request.session.modified = True
        return JsonResponse({"reply": f"Order confirmed! Total ₹{total}.", "cart": []})

    else:
        return JsonResponse({"reply": "I can help with orders. Try saying 'add 2 dosa' or 'show cart'."})

def chatbot_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)

            response_text = get_llm_response(user_message)
            return JsonResponse({'response': response_text})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)