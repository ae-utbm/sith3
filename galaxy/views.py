# -*- coding:utf-8 -*
#
# Copyright 2023
# - Skia <skia@hya.sk>
#
# Ce fichier fait partie du site de l'Association des Étudiants de l'UTBM,
# http://ae.utbm.fr.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License a published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Sofware Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA 02111-1307, USA.
#
#

from django.views.generic import DetailView, View
from django.http import JsonResponse
from django.db.models import Q, Case, F, When, Value
from django.db.models.functions import Concat

from core.views import (
    CanViewMixin,
    FormerSubscriberMixin,
)
from core.models import User
from core.views import UserTabsMixin
from galaxy.models import Galaxy, GalaxyLane


class GalaxyUserView(CanViewMixin, UserTabsMixin, DetailView):
    model = User
    pk_url_kwarg = "user_id"
    template_name = "galaxy/user.jinja"
    current_tab = "galaxy"

    def get_queryset(self):
        return super(GalaxyUserView, self).get_queryset().select_related("galaxy_user")

    def get_context_data(self, **kwargs):
        kwargs = super(GalaxyUserView, self).get_context_data(**kwargs)
        kwargs["lanes"] = (
            GalaxyLane.objects.filter(
                Q(star1=self.object.galaxy_user) | Q(star2=self.object.galaxy_user)
            )
            .order_by("distance")
            .annotate(
                other_star_id=Case(
                    When(star1=self.object.galaxy_user, then=F("star2__owner__id")),
                    default=F("star1__owner__id"),
                ),
                other_star_mass=Case(
                    When(star1=self.object.galaxy_user, then=F("star2__mass")),
                    default=F("star1__mass"),
                ),
                other_star_name=Case(
                    When(
                        star1=self.object.galaxy_user,
                        then=Case(
                            When(
                                star2__owner__nick_name=None,
                                then=Concat(
                                    F("star2__owner__first_name"),
                                    Value(" "),
                                    F("star2__owner__last_name"),
                                ),
                            )
                        ),
                    ),
                    default=Case(
                        When(
                            star1__owner__nick_name=None,
                            then=Concat(
                                F("star1__owner__first_name"),
                                Value(" "),
                                F("star1__owner__last_name"),
                            ),
                        )
                    ),
                ),
            )
            .select_related("star1", "star2")
        )
        return kwargs


class GalaxyDataView(FormerSubscriberMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(Galaxy.objects.first().state)
