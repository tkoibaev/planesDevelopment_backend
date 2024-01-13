from django.shortcuts import render
from django.shortcuts import render
from pD.models import *
from django.db import connection
from django.shortcuts import redirect


from datetime import date



# import psycopg2

# # Создание подключения к базе данных
# conn = psycopg2.connect(
#     dbname='planesdevelopment',
#     user='admin',
#     host='localhost',
#     port='5432',
#     password='123'
# )

# # Создание курсора
# cursor = conn.cursor()

# # Выполнение SQL-запроса
# cursor.execute("SELECT * FROM options")

# # Получение результатов
# results = cursor.fetchall()

# # Получение метаданных о результатах запроса
# columns = [desc[0] for desc in cursor.description]

# # Создание массива объектов
# objects = []
# for row in results:
#     obj = {}
#     for i, column in enumerate(columns):
#         obj[column] = row[i]
#     objects.append(obj)

# print(objects)

# cursor.close()
# conn.close()



# def GetData(id, temp='1'):
#     options = Options.objects.filter(available=True)
#     context = {'vars': options}
#     if id != 0:
#         selected_option = options.filter(option_id=id).first()
#         context['selected_option'] = selected_option
#     return context

def GetOption(request, id):
    options = Options.objects.filter(available=True).filter(option_id=id).first()
    # context['selected_option'] = options
    context = {'selected_option': options}
    # context = GetData(id)
    return render(request, 'planePage.html', context)

def GetOptions(request):
    input_text = request.GET.get('text')
    if input_text:
        # options = GetData(0)
        options = Options.objects.filter(available=True).filter(category__icontains=input_text)
        context = {'vars': options, 'find': input_text}
        return render(request, 'mainPage.html', context)
    else:
        return render(request, 'mainPage.html', {'vars': Options.objects.filter(available=True)})
    

def DeleteRecord(request, record_id):
    with connection.cursor() as cursor:
        sql = "UPDATE options SET available = false WHERE option_id = %s"
        cursor.execute(sql, [record_id])
    return redirect('options_url')


# def GetOptions(request):
#     return render(request, 'mainPage.html',GetData(0))

# def GetOption(request, id):
#     return render(request, 'planePage.html',GetData(id))


# def sendText(request):
#     input_text = request.GET.get('text')
#     options = GetData(0)
#     filtered_options = options['vars'].filter(category__icontains=input_text)
#     context = {'vars': filtered_options}
#     return render(request, 'mainPage.html', context)
