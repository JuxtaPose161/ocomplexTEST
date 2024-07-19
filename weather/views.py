from django.shortcuts import render
from weather.utils.utils import main, get_translation
import json
from datetime import datetime
import asyncio

with open('weather/utils/descriptions.json', encoding='utf-8') as f:
    desc = json.load(f)
def weather_return(request):
    params = request.GET.get('city')
    # Проверяем, есть ли город в запросе
    if params or params=='':
        city = request.GET.get('city')
    # Проверяем, есть ли запись в сессии
    elif request.session.get('last_city'):
        city = request.session['last_city']
    else:
        return render(request, 'weather/index.html', {'context': 'Введите интересующий вас город'})
    # Создаём json-файл со всеми необходимыми данными
    try:
        data_json = asyncio.run(main(city))
    except:
        return render(request, 'weather/index.html', {'context': 'Мы не нашли ваш город, убедитесь в корректности написания', 'city': city})
    # Проверяем, существует ли данные о городе из запроса
    if not data_json:
        return render(request, 'weather/index.html', {'context': 'Мы не нашли ваш город, убедитесь в корректности написания', 'city': city})

    # Записываем в сессию записанный город
    request.session['last_city'] = city

    # Представляем данные в нужном формате

    # Получаем дату и с помощью запроса переводим её на русский
    date_eng = datetime.fromisoformat(data_json[0]['hourly']['time'][0]).strftime('%d %B')
    date_ru = asyncio.run(get_translation(date_eng, 'en', 'ru'))['translation']

    # Создаём список, в который будем складывать информацию о СТРАНЕ, ШИРОТЕ, ДОЛГОТЕ и ПОГОДЕ НА КАЖДЫЙ ЧАС города
    context_list = []
    for data in data_json:
        country_ru = asyncio.run(get_translation(data['country'], 'en', 'ru'))['translation']
        weather_desc = list(map(lambda x: desc[str(x)]['night']['description'], data['hourly']['weather_code']))
        time = list(map(lambda x: datetime.fromisoformat(x).strftime('%H:%M'), data['hourly']['time']))
        context = {
            'country': country_ru,
            'lat': data['latitude'],
            'lon': data['longitude'],
            'data': list(zip(time, data['hourly']['temperature_2m'], weather_desc))
        }
        context_list.append(context)
    # Сохраняем последний город
    request.session.modified = True
    # Отрисовываем страничку
    return render(request, 'weather/main.html', {'context': context_list, 'city': city, 'date_ru': date_ru})