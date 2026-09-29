# Copyright (c) 2019-2020 John Elder All Rights Reserved

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Stock
from .forms import StockForm
import requests
import json

# Define your Alpha Vantage API configuration globally
API_KEY = "kh9o49b4hs9za6n0"
BASE_URL = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE"

def home(request):
    if request.method == 'POST':
        ticker = request.POST['ticker']
        url = f"{BASE_URL}&symbol={ticker}&apikey={API_KEY}"
        api_request = requests.get(url)
        
        try:
            api_data = json.loads(api_request.content)
            # Re-map Alpha Vantage structure to match IEX keys used in your home.html
            if "Global Quote" in api_data and api_data["Global Quote"]:
                quote = api_data["Global Quote"]
                api = {
                    'companyName': quote.get('01. symbol', ticker), # AV doesn't provide full names in Quote endpoint
                    'latestPrice': quote.get('05. price', 'N/A'),
                    'previousClose': quote.get('08. previous close', 'N/A'),
                    'ytdChange': quote.get('09. change', 'N/A'),
                    
                }
            else:
                api = "Error..."
        except Exception as e:
            api = "Error..."
            
        return render(request, 'home.html', {'api': api})
    else:
        return render(request, 'home.html', {'ticker': "Enter a Ticker Symbol Above..."})


def add_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, ("Stock Has Been Added!"))
            return redirect('add_stock')
    else:   
        ticker = Stock.objects.all()
        output = []
        
        for ticker_item in ticker:
            url = f"{BASE_URL}&symbol={str(ticker_item)}&apikey={API_KEY}"
            api_request = requests.get(url)
            try:
                api_data = json.loads(api_request.content)
                if "Global Quote" in api_data and api_data["Global Quote"]:
                    quote = api_data["Global Quote"]
                    # Re-map attributes cleanly for loop extraction
                    mapped_data = {
                        'id': ticker_item.id,
                        'ticker': quote.get('01. symbol'),
                        'latestPrice': quote.get('05. price'),
                        'previousClose': quote.get('08. previous close'),
                        'ytdChange': quote.get('09. change'),
                    }
                    output.append(mapped_data)
                else:
                    output.append({'ticker': str(ticker_item), 'latestPrice': 'API Limit/Error'})
            except Exception as e:
                output.append({'ticker': str(ticker_item), 'latestPrice': 'Error'})
        
        return render(request, 'add_stock.html', {'ticker': ticker, 'output': output})


def delete(request, stock_id):
    item = Stock.objects.get(pk=stock_id)
    item.delete()
    messages.success(request, ("Stock Has Been Deleted!"))
    return redirect('delete_stock') # Added quotes around redirect name string


def delete_stock(request):
    ticker = Stock.objects.all()
    return render(request, 'delete_stock.html', {'ticker': ticker})