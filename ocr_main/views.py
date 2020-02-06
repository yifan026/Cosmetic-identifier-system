from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from ocr_main.models import AmazonLink, Choice
from ocr_main.serializers import ImageSerializer, AmazonLinkSerializer, ChoiceSerializer
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from gv_api.gv_api import *

from django.views.generic.base import TemplateView
from django.contrib.auth.forms import UserCreationForm  # 新增

q_id = 0

result_list = {}

main_html_name = 'ocr_main/upload_pic_list.html'
product_img_html = 'ocr_main/product_pic_list.html'
result_list_key = 'result_list'


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        print("Errors", form.errors)
        if form.is_valid():
            form.save()
            return redirect('/accounts/login')
        else:
            return render(request, 'registration/register.html', {'form': form})
    else:
        form = UserCreationForm()
        context = {'form': form}
        return render(request, 'registration/register.html', context)


class ImageViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = AmazonLink.objects.all().order_by('-Created_Time')
    serializer_class = ImageSerializer
    permission_classes = (IsAuthenticated,)


class AmazonLinkViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    queryset = AmazonLink.objects.all().order_by('-Created_Time')
    serializer_class = AmazonLinkSerializer
    permission_classes = (IsAuthenticated,)


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all().order_by('-Last_Update_Time')
    serializer_class = ChoiceSerializer
    permission_classes = (IsAuthenticated,)


class HomePage(TemplateView):
    template_name = 'home.html'


# web版本-分頁顯示
def main_list(request, num):
    ip = request.get_host()

    if request.method == 'GET':
        q = get_object_or_404(AmazonLink, Img_ID=num)

        upload_pic = 'http://' + ip + '/media/' + str(q.Img_File)
        result_list = q.GV_Result

        return render(request, product_img_html, {
            result_list_key: result_list, 'upload_pic': upload_pic, 'num': num, 'gv_text': q.GV_Text,
            'file_name': q.Img_File
        })


# web版本
def multi_file(request):
    global result_list

    ip = request.get_host()

    upload_pic_list = []

    try:
        upload = request.FILES.getlist('img_files')
    except Exception:

        return render(request, main_html_name, {
            result_list_key: ''
        })

    if request.method == 'POST' and upload:

        gv_file_list = request.FILES.getlist('img_files')

        for gv_file in gv_file_list:
            q = AmazonLink.objects.create(Img_File=gv_file)

            qid = q.id

            uploaded_file_url = str(q.Img_File)

            prd_img_url = 'http://' + ip + '/media/' + uploaded_file_url

            # time.sleep(1)

            ori_text, result_list, spend_time, text_logo_json = get_gv_file.get_gv('./media/' + uploaded_file_url)

            # ori_text, result_list, spend_time, text_logo_json = "", [], 1, {}

            print('\n****************web version*******************\n')

            website = "http://" + ip + '/img/' + str(qid)

            AmazonLink.objects.filter(id=qid).update(GV_Text=ori_text, GV_Result=result_list, Img_ID=qid,
                                                     Website=website, GV_Text_Logo_Json=text_logo_json)

            upload_pic_list.append(
                {'number': int(qid), 'prd_img': prd_img_url, 'gv_file': gv_file, 'spend_time': spend_time,
                 'gv_text': ori_text, 'ip': ip})

        return render(request, main_html_name, {
            result_list_key: upload_pic_list
        })

    else:
        print('F5')

        return render(request, main_html_name, {
            result_list_key: upload_pic_list
        })


def choice(request):
    if request.method == "POST":
        qid = int(list(request.POST.keys())[-1].split('_')[-1])

        q = get_object_or_404(AmazonLink, Img_ID=qid)

        choice_list = q.GV_Result

        i = int(list(request.POST.keys())[-1].split('_')[-2])
        Choice.objects.create(Img_ID=qid, Match_URL=choice_list[i - 1]['result_url'], Match_Number=i)

    return render(request, 'ocr_main/choice.html')
