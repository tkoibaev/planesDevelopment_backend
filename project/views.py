from django.shortcuts import render 
from rest_framework.response import Response 
from django.shortcuts import get_object_or_404 
from rest_framework import status 
from .serializers import * 
from .models import * 
from rest_framework.decorators import api_view 
from minio import Minio

user= Users.objects.get(id=1)


#GET - получить список всех опций 
@api_view(['Get']) 
def get_options(request, format=None): 
    
    options = Options.objects.all()
    serializer = OptionSerializer(options, many=True)
    
    # Retrieve the application with customer user and status equal to 1
    application = Applications.objects.filter(customer=user, status=1).first()
    if application:
        application_serializer = ApplicationSerializer(application)
        apps_data = [application_serializer.data]
    else:
        apps_data = []
    
    response_data = {
        'apps': apps_data,
        'options': serializer.data,
    }
    
    return Response(response_data)
 
#POST - добавить новую опцию 
@api_view(['Post']) 
def post_option(request, format=None):     
    serializer = OptionSerializer(data=request.data) 
    if not serializer.is_valid(): 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    new_option = serializer.save() 
        # return Response(serializer.data, status=status.HTTP_201_CREATED)
    client = Minio(endpoint="localhost:9000",
               access_key='minioadmin',
               secret_key='minioadmin',
               secure=False)
    i=new_option.id-1
    try:
        i = new_option.id
        img_obj_name = f"{i}.png"
        file_path = f"assets/img/{request.data.get('image')}"  
        client.fput_object(bucket_name='img',
                           object_name=img_obj_name,
                           file_path=file_path)
        new_option.image = f"minio://localhost:9000/img/{img_obj_name}"
        new_option.save()
    except Exception as e:
        return Response({"error": str(e)})
    
    
    option = Options.objects.filter(available=True)
    serializer = OptionSerializer(option, many=True)
    return Response(serializer.data)




#GET - получить одну опцию 
@api_view(['Get']) 
def get_option(request, pk, format=None): 
    option = get_object_or_404(Options, pk=pk) 
    if request.method == 'GET': 
        serializer = OptionSerializer(option) 
        return Response(serializer.data) 
 
#PUT - обновить одну опцию 
@api_view(['Put']) 
def put_option(request, pk, format=None): 
    option = get_object_or_404(Options, pk=pk) 
    serializer = OptionSerializer(option, data=request.data) 
    if serializer.is_valid(): 
        serializer.save() 
        return Response(serializer.data) 
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
 
#PUT - удалить одну опцию 
@api_view(['Put']) 
def delete_option(request, pk, format=None):     
    if not Options.objects.filter(pk=pk).exists():
        return Response(f"Опции с таким id не существует!") 
    option = Options.objects.get(pk=pk)
    option.available = False
    option.save()

    options = Options.objects.filter(available=True)
    serializer = OptionSerializer(options, many=True)
    return Response(serializer.data)
    # return Response(status=status.HTTP_204_NO_CONTENT) 
 
#POST - добавить опцию в заявку(если нет открытых заявок, то создать)
@api_view(['POST'])
def add_to_application(request, pk):
    if not Options.objects.filter(id=pk).exists():
        return Response(f"Опции с таким id не существует!")

    option = Options.objects.get(id=pk)

    application = Applications.objects.filter(status=1).last()

    if application is None:
        application = Applications.objects.create(customer_id=user.id)

    amount = request.data.get("amount",1)

    application_option = Applicationsoptions.objects.create(
        option=option,
        amount=amount  # Сохранение количества опций
    )

    application_option.application = application  # Устанавливаем связь с объектом Applications
    application_option.save()  # Сохраняем объект Applicationsoptions

    serializer = OptionSerializer(application_option)
    return Response(serializer.data, status=status.HTTP_201_CREATED)





 
#GET - получить список всех заявок 
@api_view(['Get']) 
def get_applications(request, format=None): 
    print('get') 
    applications = Applications.objects.all() 
    serializer = ApplicationSerializer(applications, many=True) 
    return Response(serializer.data) 
 
#GET - получить одну заявку 
@api_view(['GET'])
def get_application(request, pk, format=None):
    application = get_object_or_404(Applications, pk=pk)
    if request.method == 'GET':
        serializer = ApplicationSerializer(application)
        application_data = serializer.data

        # Получить связанные опции для заявки с полными данными из таблицы Options
        application_options = Applicationsoptions.objects.filter(application=application)
        options_data = []
        for app_option in application_options:
            option_serializer = OptionSerializer(app_option.option)
            option_data = option_serializer.data
            option_data['amount'] = app_option.amount
            options_data.append(option_data)
        
        # Добавить данные об опциях в данные о заявке
        application_data['options'] = options_data
        
        return Response(application_data)


@api_view(["PUT"])
def update_by_user(request, pk):
    if not Applications.objects.filter(pk=pk).exists():
        return Response(f"Заявки с таким id не существует!")

    request_status = request.data["status"]

    if request_status not in [2, 3]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    application = Applications.objects.get(pk=pk)
    app_status = application.status

    # if app_status == 5:
    #     return Response("Статус изменить нельзя")

    application.status = request_status
    application.save()

    serializer = ApplicationSerializer(application, many=False)
    return Response(serializer.data)

@api_view(["PUT"])
def update_by_admin(request, pk):
    if not Applications.objects.filter(pk=pk).exists():
        return Response(f"Заявки с таким id не существует!")

    request_status = request.data["status"]

    if request_status not in [4, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    application = Applications.objects.get(pk=pk)
    # app_status = application.status

    # if app_status == 5:
    #     return Response("Статус изменить нельзя")

    application.status = request_status
    application.save()

    serializer = ApplicationSerializer(application, many=False)
    return Response(serializer.data)


#DELETE - удалить одну заявку
@api_view(['Delete']) 
def delete_application(request, pk, format=None):     
    application = get_object_or_404(Applications, pk=pk) 
    print(application.status)
    if application.status == '1':
        application.delete() 
        return Response("Заявка успешно удалена.")
    else:
        return Response("Невозможно изменить статус заявки. Текущий статус не равен 1.", status=status.HTTP_400_BAD_REQUEST)



#DELETE - удалить конкретную опцию из конкретной заявки
@api_view(["DELETE"])
def delete_option_from_application(request, application_id, option_id):
    if not Applications.objects.filter(pk=application_id).exists():
        return Response("Заявки с таким id не существует", status=status.HTTP_404_NOT_FOUND)

    if not Options.objects.filter(pk=option_id).exists():
        return Response("Опции с таким id не существует", status=status.HTTP_404_NOT_FOUND)

    application = Applications.objects.get(pk=application_id)
    option = Options.objects.get(pk=option_id)

    application.applicationsoptions_set.filter(option=option).delete()
    application.save()

    return Response("Опция успешно удалена из заявки", status=status.HTTP_204_NO_CONTENT)


#PUT - изменить кол-во конкретной опции в заявке
@api_view(["PUT"])
def update_option_amount(request, application_id, option_id):
    if not Applications.objects.filter(pk=application_id).exists() or not Options.objects.filter(pk=option_id).exists():
        return Response("Заявки или опции с такими id не существует", status=status.HTTP_404_NOT_FOUND)

    application_option = Applicationsoptions.objects.filter(application_id=application_id, option_id=option_id).first()

    if not application_option:
        return Response("В этой заявке нет такой опции", status=status.HTTP_404_NOT_FOUND)

    new_amount = request.data.get("amount",1)
    application_option.amount = new_amount
    application_option.save()
    return Response("Amount успешно обновлен", status=status.HTTP_200_OK)
    # if new_amount is not None:

    # else:
    #     return Response("Неверные данные для обновления amount", status=status.HTTP_400_BAD_REQUEST)