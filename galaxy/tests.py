# -*- coding:utf-8 -*-
#
# Copyright 2023 © AE UTBM
# ae@utbm.fr / ae.info@utbm.fr
# All contributors are listed in the CONTRIBUTORS file.
#
# This file is part of the website of the UTBM Student Association (AE UTBM),
# https://ae.utbm.fr.
#
# You can find the whole source code at https://github.com/ae-utbm/sith3
#
# LICENSED UNDER THE GNU GENERAL PUBLIC LICENSE VERSION 3 (GPLv3)
# SEE : https://raw.githubusercontent.com/ae-utbm/sith3/master/LICENSE
# OR WITHIN THE LOCAL FILE "LICENSE"
#
# PREVIOUSLY LICENSED UNDER THE MIT LICENSE,
# SEE : https://raw.githubusercontent.com/ae-utbm/sith3/master/LICENSE.old
# OR WITHIN THE LOCAL FILE "LICENSE.old"
#

from django.test import TestCase
from django.core.management import call_command

from core.models import User
from galaxy.models import Galaxy


class GalaxyTest(TestCase):
    def setUp(self):
        call_command("populate")
        self.root = User.objects.get(username="root")
        self.skia = User.objects.get(username="skia")
        self.sli = User.objects.get(username="sli")
        self.krophil = User.objects.get(username="krophil")
        self.richard = User.objects.get(username="rbatsbak")
        self.subscriber = User.objects.get(username="subscriber")
        self.public = User.objects.get(username="public")
        self.com = User.objects.get(username="comunity")

    def test_user_self_score(self):
        with self.assertNumQueries(8):
            self.assertEqual(Galaxy.compute_user_score(self.root), 9)
            self.assertEqual(Galaxy.compute_user_score(self.skia), 10)
            self.assertEqual(Galaxy.compute_user_score(self.sli), 8)
            self.assertEqual(Galaxy.compute_user_score(self.krophil), 2)
            self.assertEqual(Galaxy.compute_user_score(self.richard), 10)
            self.assertEqual(Galaxy.compute_user_score(self.subscriber), 8)
            self.assertEqual(Galaxy.compute_user_score(self.public), 8)
            self.assertEqual(Galaxy.compute_user_score(self.com), 1)

    def test_users_score(self):
        expected_scores = {
            "krophil": {
                "comunity": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
                "public": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
                "rbatsbak": {"clubs": 100, "family": 0, "pictures": 0, "score": 100},
                "subscriber": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
            },
            "public": {
                "comunity": {"clubs": 0, "family": 0, "pictures": 0, "score": 0}
            },
            "rbatsbak": {
                "comunity": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
                "public": {"clubs": 0, "family": 366, "pictures": 0, "score": 366},
                "subscriber": {"clubs": 0, "family": 366, "pictures": 0, "score": 366},
            },
            "root": {
                "comunity": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
                "krophil": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
                "public": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
                "rbatsbak": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
                "skia": {"clubs": 0, "family": 732, "pictures": 0, "score": 732},
                "sli": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
                "subscriber": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
            },
            "skia": {
                "comunity": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
                "krophil": {"clubs": 114, "family": 0, "pictures": 2, "score": 116},
                "public": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
                "rbatsbak": {"clubs": 100, "family": 0, "pictures": 0, "score": 100},
                "sli": {"clubs": 0, "family": 366, "pictures": 4, "score": 370},
                "subscriber": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
            },
            "sli": {
                "comunity": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
                "krophil": {"clubs": 17, "family": 0, "pictures": 2, "score": 19},
                "public": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
                "rbatsbak": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
                "subscriber": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
            },
            "subscriber": {
                "comunity": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
                "public": {"clubs": 0, "family": 0, "pictures": 0, "score": 0},
            },
        }
        computed_scores = {}
        users = [
            self.root,
            self.skia,
            self.sli,
            self.krophil,
            self.richard,
            self.subscriber,
            self.public,
            self.com,
        ]

        with self.assertNumQueries(100):
            while len(users) > 0:
                user1 = users.pop(0)
                for user2 in users:
                    score, family, pictures, clubs = Galaxy.compute_users_score(
                        user1, user2
                    )
                    u1 = computed_scores.get(user1.username, {})
                    u1[user2.username] = {
                        "score": score,
                        "family": family,
                        "pictures": pictures,
                        "clubs": clubs,
                    }
                    computed_scores[user1.username] = u1

        self.maxDiff = None  # Yes, we want to see the diff if any
        self.assertDictEqual(expected_scores, computed_scores)

    def test_page_is_citizen(self):
        Galaxy.rule()
        self.client.login(username="root", password="plop")
        response = self.client.get("/galaxy/1/")
        self.assertContains(
            response,
            '<a onclick="focus_node(get_node_from_id(8))">Locate</a>',
            status_code=200,
        )

    def test_page_not_citizen(self):
        Galaxy.rule()
        self.client.login(username="root", password="plop")
        response = self.client.get("/galaxy/2/")
        self.assertEquals(response.status_code, 404)
