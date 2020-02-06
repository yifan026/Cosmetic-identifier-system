#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2017/11/3 下午 1:19

@author: YFC
"""

from rest_framework import serializers
from ocr_main.models import AmazonLink, Choice
from gv_api.gv_api import *
from modules.ToolKit import *

if_localhost = 0

if if_localhost == 1:
    ip = 'http://127.0.0.1:8080'
else:
    ip = 'http://{}:8000'.format(kit.config.get('ESdb', 'host'))


def dump(obj):
    for attr in dir(obj):
        if hasattr(obj, attr):
            print("obj.%s = %s" % (attr, getattr(obj, attr)))


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmazonLink

        # fields = ('id', 'amazon_link', 'image_link', 'title', 'img', 'last_modify_date', 'created')
        fields = ('id', 'Img_File', 'Created_Time')
        # read_only_fields = ('img_id',)

    def create(self, validated_data):
        q = AmazonLink.objects.create(Img_File=validated_data['Img_File'])
        validated_data["id"] = q.id
        validated_data["Created_Time"] = q.Created_Time

        website = ip + '/img/' + str(q.id)

        text_gv, result_list, spend_time = get_gv_file.get_gv('.' + q.Img_File.url)

        # text_gv, result_list, spend_time = "", [], 1

        AmazonLink.objects.filter(id=q.id).update(GV_Text=text_gv, GV_Result=result_list, Img_ID=q.id, Website=website)

        return AmazonLink(**validated_data)


class AmazonLinkSerializer(serializers.ModelSerializer):
    GV_Result = serializers.ListField()
    GV_Text_Logo_Json = serializers.JSONField()

    class Meta:
        model = AmazonLink
        # fields = '__all__'
        fields = ('Img_ID', 'Website', 'GV_Result', 'GV_Text', 'Created_Time', 'Img_File', 'GV_Text_Logo_Json')
        read_only_fields = ('Website', 'GV_Text', 'Img_File',)


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice

        fields = ('Img_ID', 'Match_URL', 'Match_Number')
