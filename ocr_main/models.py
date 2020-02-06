from django.db import models
from jsonfield import JSONField


class AmazonLink(models.Model):
    Img_ID = models.IntegerField(null=True)

    # Img_ID = models.ForeignKey(Image, related_name="GV_Histories")
    '''
    img = Image.objects.all()[0]
    img.amazonlink_set.all()
    img.GV_Histories.all()
    '''
    # Img_ID = models.OneToOneField(Image, db_column='Img_ID', primary_key=True)

    # Img_ID = models.ForeignKey(Image, to_field='Img_ID', db_column="Img_ID")
    # 在 Django中是 多對一(many-to-one)的關聯，而前方的參數代表的意思就是對應到哪一個類別

    # Img_File = models.URLField(null=True)

    # Tmp_File = models.CharField(max_length=100, null=True)

    Img_File = models.ImageField()

    GV_Result = JSONField(null=True)

    GV_Text_Logo_Json = JSONField(null=True)

    GV_Text = models.TextField(null=True, help_text="The OCRed text")

    Website = models.URLField(null=True)

    Created_Time = models.DateTimeField(auto_now=True)

    Match_URL = models.CharField(max_length=300, null=True)

    Match_Number = models.IntegerField(null=True)

    Last_Update_Time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ocr_gv_result"

    # list_display也可以寫在這,tuple() or list[]都可以


class Choice(models.Model):
    Img_ID = models.IntegerField()

    Match_URL = models.CharField(max_length=300, null=True)

    Match_Number = models.IntegerField(null=True)

    Last_Update_Time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ocr_match_choice"
