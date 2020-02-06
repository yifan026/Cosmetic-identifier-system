from django.contrib import admin
from ocr_main.models import AmazonLink, Choice


# class ImageModelAdmin(admin.ModelAdmin):
#     list_display = ['Img_File', 'Created_Time']
#
#     class Meta:
#         model = AmazonLink


class AmazonLinkModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'Img_File', 'Website', 'GV_Text', 'Created_Time', 'GV_Result', 'GV_Text_Logo_Json']

    # list_display = [field.name for field in AmazonLink._meta.fields]

    # 可以增加過濾的欄位
    # list_filter = ('column name',)

    class Meta:
        model = AmazonLink


class ChoiceModelAdmin(admin.ModelAdmin):
    list_display = ['Img_ID', 'Match_URL', 'Match_Number', 'Last_Update_Time']

    class Meta:
        model = Choice


# admin.site.register(Image, ImageModelAdmin)
admin.site.register(AmazonLink, AmazonLinkModelAdmin)
admin.site.register(Choice, ChoiceModelAdmin)
