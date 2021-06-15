from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse

from rest_framework.generics import GenericAPIView
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework import status

from .forms import RegisterForm, LoginForm

import requests
import json
import logging


logger = logging.getLogger("pdf_extractor_log")

# Create your views here.


class RegisterAPIView(GenericAPIView):

    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        logger.info(f'User Registration process : {user}')
        register_serializer = self.serializer_class(data=user)
        if not register_serializer.is_valid():
            logger.error(f'Unable to register the user : {str(register_serializer.errors)}')
            return Response({'status': status.HTTP_412_PRECONDITION_FAILED, 'msg': 'Unable to Register',
                             'detail': register_serializer.errors},status=status.HTTP_412_PRECONDITION_FAILED)
        register_serializer.save()
        logger.info(f'User Registration process successful : {user}')
        return Response({'status': status.HTTP_201_CREATED, 'msg': 'User Registration Successful, Please Login'},
                        status=status.HTTP_201_CREATED)


class LoginAPIView(GenericAPIView):

    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data
        logger.info(f'User Login process : {user}')
        login_serializer = self.serializer_class(data=user)
        if not login_serializer.is_valid():
            logger.error(f'Unable to login : {str(login_serializer.errors)}')
            return Response({'status': status.HTTP_412_PRECONDITION_FAILED, 'msg': 'Unable to Login',
                             'detail': login_serializer.errors})

        logger.info(f'User Login successful : {user}')
        return Response({'status': status.HTTP_200_OK, 'msg': 'User Login Successfully',
                         'detail': login_serializer.data}, status=status.HTTP_200_OK)


class RegistrationView(View):
    form_class = RegisterForm
    template_name = 'register/register.html'

    def get(self, request):
        form = self.form_class()

        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            url = request.get_host()
            register_api = requests.post(url='http://' + url + '/auth/api/register', data=json.dumps(data),
                                         headers={"Content-Type": "application/json"})
            response_api = json.loads(register_api.content)

            if register_api.status_code == status.HTTP_201_CREATED:
                return HttpResponseRedirect(reverse('authentication:user_login'))

            return render(request, self.template_name, {"form": form, "error": response_api})

        return render(request, self.template_name, {"form": form, "error": {'msg': 'Registration Failed'}})


class LoginView(View):
    form_class = LoginForm
    template_name = 'login/login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            url = request.get_host()
            login_api = requests.post(url='http://' + url + '/auth/api/login', data=json.dumps(data),
                                      headers={"Content-Type": "application/json"})
            response_api = json.loads(login_api.content)
            if login_api.status_code == status.HTTP_200_OK:

                request.session['access_token'] = response_api['detail']['access_token']
                request.session['access_token'] = response_api['detail']['access_token']
                request.session['refresh_token'] = response_api['detail']['refresh_token']
                request.session['username'] = response_api['detail']['username']
                request.session['email'] = response_api['detail']['email']
                return HttpResponseRedirect(reverse('extraction:extraction_file_view'))

            return render(request, self.template_name, {"form": form, "error": response_api})

        return render(request, self.template_name, {"form": form, "error": {'msg': 'Unable to Login'}})


class LogoutView(View):

    def post(self, request):

        request.session.flush()
        logger.info(f'User Logout successful')
        return HttpResponseRedirect(reverse('authentication:user_login'))