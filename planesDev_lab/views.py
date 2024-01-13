from django.shortcuts import render
from django.shortcuts import render

from datetime import date

planes = [
    {
        'id':1,
        'title': 'Boeing',
        'description': 'Boeing 747',
        'image':'images/first.jpg',
        'capacity': 'Вместимость: 416-660 пассажиров',
        'range': 'Дальность полета: 13,450 км',
        'engines': 'Количество двигателей: 4',
        'cabin_layout': 'Конфигурация салона: 2-проходной',
        'features': ['Просторный салон', 'Варианты классов обслуживания', 'Высокая проходимость']
    },
    {
        'id':2,
        'title': 'Airbus',
        'description': 'Boeing 787 Dreamliner',
        'image': 'images/second.jpeg',
        'capacity': 'Вместимость: 242-330 пассажиров',
        'range': 'Дальность полета: 14,140-15,200 км',
        'engines': 'Количество двигателей: 2',
        'cabin_layout': 'Конфигурация салона: 2-проходной',
        'features': ['Просторный салон', 'Современные материалы', 'Экономичность']
    },
    {
        'id':3,
        'title': 'Super',
        'description': 'Boeing 737 MAX',
        'image': 'images/third.jpg',
        'capacity': 'Вместимость: 130-230 пассажиров',
        'range': 'Дальность полета: 6,510-7,130 км',
        'engines': 'Количество двигателей: 2',
        'cabin_layout': 'Конфигурация салона: 1-проходной',
        'features': ['Современная авионика', 'Экономичность', 'Бесшумность']
    }
]

# MY WAY
# def GetPlanes(request):
#     data = {
#         'planes': planes
#     }
#     return render(request, 'mainPage.html', data)

# def GetPlane(request, id):
#     for plane in planes:
#         if plane['id'] == id:
#             return render(request, 'planePage.html', {'plane': plane})
    
# def sendText(request):
#     if request.method == 'POST':
#         input_text = request.POST.get('text')
#         filtered_planes = [plane for plane in planes if input_text.lower() in plane['title'].lower()]
#         context = {'planes': filtered_planes}
#         return render(request, 'mainPage.html', context)




def GetData(id):
    options = {'data':{
        'vars': [
        {
        'id':1,
        'title': 'ПС90-А',
        'category': 'Двигатели',
        'description': 'Поршневые двигатели типа ИРКУТ ПС90-А обычно используются в небольших самолетах авиации общего назначения.',
        'image':'images/porsh.jpeg',
        'features': ['Высокая ремонтопригодность', 'Меньшие риски для полета в случае отказов', 'Низкая стоимость']
        },
        {
        'id':2,
        'title': 'Эконом-класс на 200 мест',
        'category': 'Салоны',
        'description': 'Эконом занимает большую часть салона — среднюю и хвост. Точные условия перелета в эконом-классе различаются в зависимости от авиакомпании, но, как правило, это минимальный (базовый) набор услуг и стандартные условия перелета.',
        'image': 'images/econom.jpg',
        'features': ['Эконом-отсек находится в хвостовой части самолета, которая считается наиболее безопасной', 'Постоянная заполняемость', 'Низкая стоимость']
        },
        {
        'id':3,
        'title': 'ПД-35',
        'category': 'Двигатели',
        'description': 'Турбовинтовые двигатели типа Иркут Б похожи на поршневые двигатели, но вместо того, чтобы непосредственно приводить в движение пропеллер, они приводят в действие турбину, которая приводит в движение пропеллер.',
        'image': 'images/turbvint.jpeg',
        'features': ['Высокая ремонтопригодность', 'Меньшие риски для полета в случае отказов', 'Низкая стоимость']
        },
        ]
    }}
    if id != 0:
        return options['data']['vars'][id-1]
    else:
        return options['data']

def GetOptions(request):
    input_text = request.GET.get('text')
    if input_text:
        options = GetData(0)
        filtered_options = [var for var in options['vars'] if input_text in var['category'].lower()]
        context = {'vars': filtered_options, 'find': input_text}
        return render(request, 'mainPage.html', context)
    else:
        return render(request, 'mainPage.html', GetData(0))

def GetOption(request, id):
    return render(request, 'planePage.html',GetData(id))

# def sendText(request):
#     input_text = request.GET.get('text')  
#     options = GetData(0)
#     filtered_options = [var for var in options['vars'] if input_text in var['category'].lower()]
#     context = {'vars':  filtered_options, 'find': input_text}
#     return render(request, 'mainPage.html', context)
