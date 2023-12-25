from django.shortcuts import render 
from rest_framework.response import Response 
from django.shortcuts import get_object_or_404 
from rest_framework import status 
from .serializers import * 
from .models import * 
from rest_framework.decorators import api_view,parser_classes
from minio import Minio
from datetime import datetime
from django.http import HttpResponseBadRequest,HttpResponseServerError
from rest_framework import viewsets
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .permissions import *
from django.contrib.auth import get_user_model
import redis
import uuid
from django.conf import settings
from rest_framework.parsers import MultiPartParser


session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

user= Users.objects.get(id=20)


@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['Post'])
@permission_classes([AllowAny])
def create(request):
    if Users.objects.filter(email=request.data['email']).exists():
        return Response({'status': 'Exist'}, status=400)
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        Users.objects.create_user(email=serializer.data['email'],
                                    password=serializer.data['password'],
                                    is_moderator=serializer.data['is_moderator'])
        return Response({'status': 'Success'}, status=200)
    return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuth])
def user_info(request):
    try:
        access_token = request.COOKIES["access_token"]
        if session_storage.exists(access_token):
            email = session_storage.get(access_token).decode('utf-8')
            user = Users.objects.get(email=email)
            application = Applications.objects.filter(customer_id=user.id).filter(status=1).first()
            user_data = {
                "user_id": user.id,
                "email": user.email,
                "is_moderator": user.is_moderator,
                "current_cart": application.id if application else -1,
            }
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Error', 'message': 'Session does not exist'})
    except:
        return Response({'status': 'Error', 'message': 'Cookies are not transmitted'})



# @authentication_classes([])
# @csrf_exempt
@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['Post'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, email=username, password=password)
    
    if user is not None:
        random_key = str(uuid.uuid4())
        application = Applications.objects.filter(customer_id=user.id).filter(status=1).first()
        user_data = {
            "user_id": user.id,
            "email": user.email,
            "is_moderator": user.is_moderator,
            "access_token": random_key,
            "current_cart": application.id if application else -1,
        }
        session_storage.set(random_key, username)
        response = Response(user_data, status=status.HTTP_201_CREATED)
        response.set_cookie("access_token", random_key)

        return response
    else:
        return Response({'status': 'Error'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Post'])
@permission_classes([IsAuth])
def logout_view(request):
    # authorization_header = request.headers.get('Authorization')
    # access_token = authorization_header.split(' ')[1] if authorization_header else None
    access_token = request.COOKIES["access_token"]
    if access_token is None:
        message = {"message": "Token is not found in cookie"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)
    session_storage.delete(access_token)
    response = Response({'message': 'Logged out successfully'})
    response.delete_cookie('access_token')

    return response









@api_view(['Get']) 
@permission_classes([AllowAny])
def get_current_cart(request, format=None):

    authorization_header = request.headers.get('Authorization')
    access_token = authorization_header.split(' ')[1] if authorization_header else None

    username = session_storage.get(access_token).decode('utf-8')

    user_id = Users.objects.filter(email=username).values_list('id', flat=True).first()

    application = get_object_or_404(Applications, customer = user_id)
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



#GET - получить список всех опций 
@api_view(['GET']) 
@permission_classes([AllowAny])
def get_options(request, format=None): 
    # access_token = request.COOKIES["access_token"]
    # username = session_storage.get(access_token).decode('utf-8')
    # # user_id = Users.objects.filter(email=username).values_list('id', flat=True).first()
    # user = Users.objects.get(email=username)

    search_query = request.GET.get('search', '')
    min_price = int(request.GET.get('min_price', 0))
    max_price = int(request.GET.get('max_price', 10000))
    category = request.GET.get('category', '')
    # if user.is_moderator:
    #     options = Options.objects.filter(title__icontains=search_query).filter(price__range=(min_price, max_price))
    # else:
    options = Options.objects.filter(available=True).filter(title__icontains=search_query).filter(price__range=(min_price, max_price))

    if category and category != 'Любая категория':
        options = options.filter(category=category)
    try:
        print('vvv')
        access_token = request.COOKIES["access_token"]
        print('aaaaaa')
        username = session_storage.get(access_token).decode('utf-8')
        user_ind = Users.objects.filter(email=username).first()
        application = Applications.objects.filter(customer_id=user_ind.id, status=1).values_list('id', flat=True).first()
        serializer = OptionSerializer(options, many=True)
        response_data = {
            'app_id': application,
            'options': serializer.data,
        }
        return Response(response_data)
    except:
        serializer = OptionSerializer(options, many=True)
        result = {
            'options': serializer.data,
        }
        return Response(result)
 
#POST - добавить новую опцию 
@api_view(['Post']) 
@permission_classes([AllowAny])
def post_option(request, format=None):     
    serializer = OptionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([AllowAny])
def postImageToOption(request, pk):
    if 'file' in request.FILES:
        file = request.FILES['file']
        subscription = Options.objects.get(pk=pk, available=True)
        
        client = Minio(endpoint="localhost:9000",
                       access_key='minioadmin',
                       secret_key='minioadmin',
                       secure=False)

        bucket_name = 'img'
        file_name = file.name
        file_path = "http://localhost:9000/img/" + file_name
        
        try:
            client.put_object(bucket_name, file_name, file, length=file.size, content_type=file.content_type)
            print("Файл успешно загружен в Minio.")
            
            serializer = OptionSerializer(instance=subscription, data={'image': file_path}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse('Image uploaded successfully.')
            else:
                return HttpResponseBadRequest('Invalid data.')
        except Exception as e:
            print("Ошибка при загрузке файла в Minio:", str(e))
            return HttpResponseServerError('An error occurred during file upload.')

    return HttpResponseBadRequest('Invalid request.')

#GET - получить одну опцию 
@api_view(['GET']) 
@permission_classes([AllowAny])
def get_option(request, pk, format=None): 
    option = get_object_or_404(Options, pk=pk) 
    if request.method == 'GET': 
        serializer = OptionSerializer(option) 
        return Response(serializer.data) 
 
#PUT - обновить одну опцию 
@api_view(['Put']) 
@permission_classes([AllowAny])
def put_option(request, pk, format=None): 
    option = get_object_or_404(Options, pk=pk) 
    serializer = OptionSerializer(option, data=request.data) 
    if serializer.is_valid(): 
        serializer.save() 
        return Response(serializer.data) 
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
 
#PUT - удалить одну опцию 
@api_view(['Put']) 
@permission_classes([IsModerator])
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
@permission_classes([IsAuth])
def add_to_application(request, pk):
    # authorization_header = request.headers.get('Authorization')
    # access_token = authorization_header.split(' ')[1] if authorization_header else None
    # print(request.COOKIES["access_token"])
    access_token = request.COOKIES["access_token"]
    username = session_storage.get(access_token).decode('utf-8')
    user = Users.objects.filter(email=username).first()
    if user is None:
        print('Не зареган')


    if not Options.objects.filter(id=pk).exists():
        return Response(f"Опции с таким id не существует!")

    option = Options.objects.get(id=pk)

    application = Applications.objects.filter(status=1,customer_id=user.id).last()

    if application is None:
        application = Applications.objects.create(customer_id=user.id)

    amount = request.data.get("amount",1)
    try:
        application_option = Applicationsoptions.objects.get(application=application, option=option)
        application_option.amount += int(amount)
        application_option.save()
    except Applicationsoptions.DoesNotExist:
        application_option = Applicationsoptions(application=application, option=option, amount=amount)
        application_option.save()

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



#GET - получить список всех заявок 
@api_view(['GET'])
@permission_classes([IsAuth])
def get_applications(request, format=None):
    
    access_token = request.COOKIES["access_token"]
    username = session_storage.get(access_token).decode('utf-8')
    user_id = Users.objects.filter(email=username).values_list('id', flat=True).first()

    if username is not None and user_id is not None:
        user = Users.objects.get(email=username)
        if user.is_moderator:
            start_day = request.GET.get('start_day')
            end_day = request.GET.get('end_day')
            category = request.GET.get('category', '')
            start_day = start_day.split(' ')[0:-5]
            end_day = end_day.split(' ')[0:-5]
            start_day = ' '.join(start_day)
            end_day = ' '.join(end_day)
            start_day = datetime.strptime(start_day, '%a %b %d %Y %H:%M:%S')
            end_day = datetime.strptime(end_day, '%a %b %d %Y %H:%M:%S')    
            applications = Applications.objects.filter(created_at__range=(start_day, end_day)).exclude(status=2).exclude(status=1)
            if category and category != '0':
                applications = applications.filter(status=category).exclude(status=2).exclude(status=1)
        else:
            applications = Applications.objects.filter(customer_id=user_id).exclude(status=2)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)
    else:
        return Response("Invalid user", status=status.HTTP_400_BAD_REQUEST)
    
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



# @cross_origin(allow_headers=['Content-Type'])
@api_view(["PUT"])
@permission_classes([AllowAny]) #need to fix for preflight
def update_by_user(request, pk):
    if not Applications.objects.filter(pk=pk).exists():
        return Response(f"Заявки с таким id не существует!")
    request_status = request.data["status"]
    if int(request.data["status"]) not in [2, 3]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    application = Applications.objects.get(pk=pk)
    app_status = application.status

    if int(request.data["status"]) in [3]:
        application.formed_at=timezone.now()
    

    application.status = request_status
    application.save()

    serializer = ApplicationSerializer(application, many=False)
    response = Response(serializer.data)
    
    return response


@swagger_auto_schema(method='put',request_body=ApplicationSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_by_admin(request, pk):
    access_token = request.COOKIES["access_token"]
    modername = session_storage.get(access_token).decode('utf-8')
    user = Users.objects.filter(email=modername).first()
    
    if not Applications.objects.filter(pk=pk).exists():
        return Response(f"Заявки с таким id не существует!")

    request_status = request.data["status"]

    if int(request.data["status"]) not in [4, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    application = Applications.objects.get(pk=pk)
    if int(request.data["status"]) in [4]:
        application.completed_at=timezone.now()
    # app_status = application.status

    # if app_status == 5:
    #     return Response("Статус изменить нельзя")
    application.moderator_id=user.id
    application.status = request_status
    application.save()

    serializer = ApplicationSerializer(application, many=False)
    response = Response(serializer.data)
    response.setHeader("Access-Control-Allow-Methods", "PUT")
    return response


#DELETE - удалить одну заявку
@api_view(['Delete']) 
def delete_application(request, pk, format=None):     
    application = get_object_or_404(Applications, pk=pk) 
    if application.status == '1':
        application.delete() 
        return Response("Заявка успешно удалена.")
    else:
        return Response("Невозможно изменить статус заявки. Текущий статус не равен 1.", status=status.HTTP_400_BAD_REQUEST)



#DELETE - удалить конкретную опцию из конкретной заявки
@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_option_from_application(request, application_id, option_id):
    if not Applications.objects.filter(pk=application_id).exists():
        return Response("Заявки с таким id не существует", status=status.HTTP_404_NOT_FOUND)

    if not Options.objects.filter(pk=option_id).exists():
        return Response("Опции с таким id не существует", status=status.HTTP_404_NOT_FOUND)

    application = Applications.objects.get(pk=application_id)
    option = Options.objects.get(pk=option_id)

    application_subscription = get_object_or_404(Applicationsoptions, application=application, option=option)
    if application_subscription is None:
        return Response("Заявка не найдена", status=404)
    application.applicationsoptions_set.filter(option=option).delete()
    application.save()

    return Response("Опция успешно удалена из заявки", status=200)


#PUT - изменить кол-во конкретной опции в заявке
@api_view(["PUT"])
@permission_classes([AllowAny])
def update_option_amount(request, application_id, option_id):
    if not Applications.objects.filter(pk=application_id).exists() or not Options.objects.filter(pk=option_id).exists():
        return Response("Заявки или опции с такими id не существует", status=status.HTTP_404_NOT_FOUND)

    application_option = Applicationsoptions.objects.filter(application_id=application_id, option_id=option_id).first()

    if not application_option:
        return Response("В этой заявке нет такой опции", status=status.HTTP_404_NOT_FOUND)
    prev_amount = application_option.amount
    if request.data["action"] ==0 and prev_amount!=1:
        application_option.amount = prev_amount-1
    elif request.data["action"] ==1 :
        application_option.amount = prev_amount+1

    
    # new_amount = request.data.get("amount",1)
    # application_option.amount = new_amount
    application_option.save()
    return Response("Amount успешно обновлен", status=status.HTTP_200_OK)
    # if new_amount is not None:

    # else:
    #     return Response("Неверные данные для обновления amount", status=status.HTTP_400_BAD_REQUEST)





