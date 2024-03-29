# -*- coding:utf-8 -*
#
# Copyright 2023 © AE UTBM
# ae@utbm.fr / ae.info@utbm.fr
#
# This file is part of the website of the UTBM Student Association (AE UTBM),
# https://ae.utbm.fr.
#
# You can find the source code of the website at https://github.com/ae-utbm/sith3
#
# LICENSED UNDER THE GNU GENERAL PUBLIC LICENSE VERSION 3 (GPLv3)
# SEE : https://raw.githubusercontent.com/ae-utbm/sith3/master/LICENSE
# OR WITHIN THE LOCAL FILE "LICENSE"
#
#

from rest_framework import serializers

from core.models import RealGroup

from api.views import RightModelViewSet


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealGroup


class GroupViewSet(RightModelViewSet):
    """
    Manage Groups (api/v1/group/)
    """

    serializer_class = GroupSerializer
    queryset = RealGroup.objects.all()
