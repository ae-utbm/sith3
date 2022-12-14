# -*- coding:utf-8 -*
#
# Copyright 2019
# - Sli <antoine@bartuccio.fr>
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

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.management import call_command

from core.models import User, Notification

from pedagogy.models import UV, UVComment, UVCommentReport


def create_uv_template(user_id, code="IFC1", exclude_list=[]):
    """
    Factory to help UV creation/update in post requests
    """
    uv = {
        "code": code,
        "author": user_id,
        "credit_type": "TM",
        "semester": "SPRING",
        "language": "FR",
        "department": "TC",
        "credits": 3,
        "hours_CM": 10,
        "hours_TD": 28,
        "hours_TP": 0,
        "hours_THE": 37,
        "hours_TE": 0,
        "manager": "Gilles BERTRAND",
        "title": "Algorithmique et programmation : niveau I, initiés - partie I",
        "objectives": """* Introduction à l'algorithmique et à la programmation pour initiés.
* Pratiques et développement en langage C.""",
        "program": """* Découverte des outils élémentaires utilisés pour écrire, compiler et exécuter un programme écrit en langage C
* Règles de programmation : normes en cours, règles de présentation du code, commentaires
* Initiation à l'algorithmique et découverte des bases du langage C :
    * les conditions
    * les boucles
    * les types de données
    * les tableaux à une dimension
    * manipulations des chaînes de caractères
    * les fonctions et procédures""",
        "skills": "* D'écrire un algorithme et de l'implémenter en C",
        "key_concepts": """* Algorithme
* Variables scalaires et vectorielles
* Structures alternatives, répétitives
* Fonctions, procédures
* Chaînes de caractères""",
    }
    for excluded in exclude_list:
        uv.pop(excluded)
    return uv


# UV class tests


class UVCreation(TestCase):
    """
    Test uv creation
    """

    def setUp(self):
        call_command("populate")
        self.bibou = User.objects.filter(username="root").first()
        self.tutu = User.objects.filter(username="tutu").first()
        self.sli = User.objects.filter(username="sli").first()
        self.guy = User.objects.filter(username="guy").first()

    def test_create_uv_admin_success(self):
        self.client.login(username="root", password="plop")
        response = self.client.post(
            reverse("pedagogy:uv_create"), create_uv_template(self.bibou.id)
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UV.objects.filter(code="IFC1").exists())

    def test_create_uv_pedagogy_admin_success(self):
        self.client.login(username="tutu", password="plop")
        response = self.client.post(
            reverse("pedagogy:uv_create"), create_uv_template(self.tutu.id)
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UV.objects.filter(code="IFC1").exists())

    def test_create_uv_unauthorized_fail(self):
        # Test with anonymous user
        response = self.client.post(
            reverse("pedagogy:uv_create"), create_uv_template(0)
        )
        self.assertEqual(response.status_code, 403)

        # Test with subscribed user
        self.client.login(username="sli", password="plop")
        response = self.client.post(
            reverse("pedagogy:uv_create"), create_uv_template(self.sli.id)
        )
        self.assertEqual(response.status_code, 403)

        # Test with non subscribed user
        self.client.login(username="guy", password="plop")
        response = self.client.post(
            reverse("pedagogy:uv_create"), create_uv_template(self.guy.id)
        )
        self.assertEqual(response.status_code, 403)

        # Check that the UV has never been created
        self.assertFalse(UV.objects.filter(code="IFC1").exists())

    def test_create_uv_bad_request_fail(self):
        self.client.login(username="tutu", password="plop")

        # Test with wrong user id (if someone cheats on the hidden input)
        response = self.client.post(
            reverse("pedagogy:uv_create"), create_uv_template(self.bibou.id)
        )
        self.assertNotEqual(response.status_code, 302)
        self.assertEqual(response.status_code, 200)

        # Remove a required field
        response = self.client.post(
            reverse("pedagogy:uv_create"),
            create_uv_template(self.tutu.id, exclude_list=["title"]),
        )
        self.assertNotEqual(response.status_code, 302)
        self.assertEqual(response.status_code, 200)

        # Check that the UV hase never been created
        self.assertFalse(UV.objects.filter(code="IFC1").exists())


class UVListTest(TestCase):
    """
    Test guide display rights
    """

    def setUp(self):
        call_command("populate")

    def test_uv_list_display_success(self):
        # Display for root
        self.client.login(username="root", password="plop")
        response = self.client.get(reverse("pedagogy:guide"))
        self.assertContains(response, text="PA00")

        # Display for pedagogy admin
        self.client.login(username="tutu", password="plop")
        response = self.client.get(reverse("pedagogy:guide"))
        self.assertContains(response, text="PA00")

        # Display for simple subscriber
        self.client.login(username="sli", password="plop")
        response = self.client.get(reverse("pedagogy:guide"))
        self.assertContains(response, text="PA00")

    def test_uv_list_display_fail(self):
        # Don't display for anonymous user
        response = self.client.get(reverse("pedagogy:guide"))
        self.assertEqual(response.status_code, 403)

        # Don't display for none subscribed users
        self.client.login(username="guy", password="plop")
        response = self.client.get(reverse("pedagogy:guide"))
        self.assertEqual(response.status_code, 403)


class UVDeleteTest(TestCase):
    """
    Test UV deletion rights
    """

    def setUp(self):
        call_command("populate")

    def test_uv_delete_root_success(self):
        self.client.login(username="root", password="plop")
        self.client.post(
            reverse(
                "pedagogy:uv_delete", kwargs={"uv_id": UV.objects.get(code="PA00").id}
            )
        )
        self.assertFalse(UV.objects.filter(code="PA00").exists())

    def test_uv_delete_pedagogy_admin_success(self):
        self.client.login(username="tutu", password="plop")
        self.client.post(
            reverse(
                "pedagogy:uv_delete", kwargs={"uv_id": UV.objects.get(code="PA00").id}
            )
        )
        self.assertFalse(UV.objects.filter(code="PA00").exists())

    def test_uv_delete_pedagogy_unauthorized_fail(self):
        # Anonymous user
        response = self.client.post(
            reverse(
                "pedagogy:uv_delete", kwargs={"uv_id": UV.objects.get(code="PA00").id}
            )
        )
        self.assertEqual(response.status_code, 403)

        # Not subscribed user
        self.client.login(username="guy", password="plop")
        response = self.client.post(
            reverse(
                "pedagogy:uv_delete", kwargs={"uv_id": UV.objects.get(code="PA00").id}
            )
        )
        self.assertEqual(response.status_code, 403)

        # Simply subscribed user
        self.client.login(username="sli", password="plop")
        response = self.client.post(
            reverse(
                "pedagogy:uv_delete", kwargs={"uv_id": UV.objects.get(code="PA00").id}
            )
        )
        self.assertEqual(response.status_code, 403)

        # Check that the UV still exists
        self.assertTrue(UV.objects.filter(code="PA00").exists())


class UVUpdateTest(TestCase):
    """
    Test UV update rights
    """

    def setUp(self):
        call_command("populate")
        self.bibou = User.objects.filter(username="root").first()
        self.tutu = User.objects.filter(username="tutu").first()
        self.uv = UV.objects.get(code="PA00")

    def test_uv_update_root_success(self):
        self.client.login(username="root", password="plop")
        self.client.post(
            reverse("pedagogy:uv_update", kwargs={"uv_id": self.uv.id}),
            create_uv_template(self.bibou.id, code="PA00"),
        )
        self.uv.refresh_from_db()
        self.assertEqual(self.uv.credit_type, "TM")

    def test_uv_update_pedagogy_admin_success(self):
        self.client.login(username="tutu", password="plop")
        self.client.post(
            reverse("pedagogy:uv_update", kwargs={"uv_id": self.uv.id}),
            create_uv_template(self.bibou.id, code="PA00"),
        )
        self.uv.refresh_from_db()
        self.assertEqual(self.uv.credit_type, "TM")

    def test_uv_update_original_author_does_not_change(self):
        self.client.login(username="tutu", password="plop")
        response = self.client.post(
            reverse("pedagogy:uv_update", kwargs={"uv_id": self.uv.id}),
            create_uv_template(self.tutu.id, code="PA00"),
        )

        self.uv.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.uv.author, self.bibou)

    def test_uv_update_pedagogy_unauthorized_fail(self):
        # Anonymous user
        response = self.client.post(
            reverse("pedagogy:uv_update", kwargs={"uv_id": self.uv.id}),
            create_uv_template(self.bibou.id, code="PA00"),
        )
        self.assertEqual(response.status_code, 403)

        # Not subscribed user
        self.client.login(username="guy", password="plop")
        response = self.client.post(
            reverse("pedagogy:uv_update", kwargs={"uv_id": self.uv.id}),
            create_uv_template(self.bibou.id, code="PA00"),
        )
        self.assertEqual(response.status_code, 403)

        # Simply subscribed user
        self.client.login(username="sli", password="plop")
        response = self.client.post(
            reverse("pedagogy:uv_update", kwargs={"uv_id": self.uv.id}),
            create_uv_template(self.bibou.id, code="PA00"),
        )
        self.assertEqual(response.status_code, 403)

        # Check that the UV has not changed
        self.uv.refresh_from_db()
        self.assertEqual(self.uv.credit_type, "OM")


# UVComment class tests


def create_uv_comment_template(user_id, uv_code="PA00", exclude_list=[]):
    """
    Factory to help UVComment creation/update in post requests
    """
    comment = {
        "author": user_id,
        "uv": UV.objects.get(code=uv_code).id,
        "grade_global": 4,
        "grade_utility": 4,
        "grade_interest": 4,
        "grade_teaching": -1,
        "grade_work_load": 2,
        "comment": "Superbe UV qui fait vivre la vie associative de l'école",
    }
    for excluded in exclude_list:
        comment.pop(excluded)
    return comment


class UVCommentCreationAndDisplay(TestCase):
    """
    Test UVComment creation and it's display
    Display and creation are the same view
    """

    def setUp(self):
        call_command("populate")
        self.bibou = User.objects.filter(username="root").first()
        self.tutu = User.objects.filter(username="tutu").first()
        self.sli = User.objects.filter(username="sli").first()
        self.guy = User.objects.filter(username="guy").first()
        self.uv = UV.objects.get(code="PA00")

    def test_create_uv_comment_admin_success(self):
        self.client.login(username="root", password="plop")
        response = self.client.post(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id}),
            create_uv_comment_template(self.bibou.id),
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.get(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id})
        )
        self.assertContains(response, text="Superbe UV")

    def test_create_uv_comment_pedagogy_admin_success(self):
        self.client.login(username="tutu", password="plop")
        response = self.client.post(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id}),
            create_uv_comment_template(self.tutu.id),
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.get(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id})
        )
        self.assertContains(response, text="Superbe UV")

    def test_create_uv_comment_subscriber_success(self):
        self.client.login(username="sli", password="plop")
        response = self.client.post(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id}),
            create_uv_comment_template(self.sli.id),
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.get(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id})
        )
        self.assertContains(response, text="Superbe UV")

    def test_create_uv_comment_unauthorized_fail(self):
        # Test with anonymous user
        response = self.client.post(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id}),
            create_uv_comment_template(0),
        )
        self.assertEqual(response.status_code, 403)

        # Test with non subscribed user
        self.client.login(username="guy", password="plop")
        response = self.client.post(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id}),
            create_uv_comment_template(self.guy.id),
        )
        self.assertEqual(response.status_code, 403)

        # Check that the comment has never been created
        self.client.login(username="root", password="plop")
        response = self.client.get(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id})
        )
        self.assertNotContains(response, text="Superbe UV")

    def test_create_uv_comment_bad_form_fail(self):
        self.client.login(username="root", password="plop")
        response = self.client.post(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id}),
            create_uv_comment_template(self.bibou.id, exclude_list=["grade_global"]),
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id})
        )
        self.assertNotContains(response, text="Superbe UV")

    def test_create_uv_comment_twice_fail(self):
        # Checks that the has_user_already_commented method works proprely
        self.assertFalse(self.uv.has_user_already_commented(self.bibou))

        # Create a first comment
        self.client.login(username="root", password="plop")
        self.client.post(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id}),
            create_uv_comment_template(self.bibou.id),
        )

        # Checks that the has_user_already_commented method works proprely
        self.assertTrue(self.uv.has_user_already_commented(self.bibou))

        # Create the second comment
        comment = create_uv_comment_template(self.bibou.id)
        comment["comment"] = "Twice"
        response = self.client.post(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id}), comment
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            UVComment.objects.filter(comment__contains="Superbe UV").exists()
        )
        self.assertFalse(UVComment.objects.filter(comment__contains="Twice").exists())
        self.assertContains(
            response,
            _(
                "You already posted a comment on this UV. If you want to comment again, please modify or delete your previous comment."
            ),
        )

        # Ensure that there is no crash when no uv or no author is given
        self.client.post(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id}),
            create_uv_comment_template(self.bibou.id, exclude_list=["uv"]),
        )
        self.assertEqual(response.status_code, 200)
        self.client.post(
            reverse("pedagogy:uv_detail", kwargs={"uv_id": self.uv.id}),
            create_uv_comment_template(self.bibou.id, exclude_list=["author"]),
        )
        self.assertEqual(response.status_code, 200)


class UVCommentDeleteTest(TestCase):
    """
    Test UVComment deletion rights
    """

    def setUp(self):
        call_command("populate")
        comment_kwargs = create_uv_comment_template(
            User.objects.get(username="krophil").id
        )
        comment_kwargs["author"] = User.objects.get(id=comment_kwargs["author"])
        comment_kwargs["uv"] = UV.objects.get(id=comment_kwargs["uv"])
        self.comment = UVComment(**comment_kwargs)
        self.comment.save()

    def test_uv_comment_delete_root_success(self):
        self.client.login(username="root", password="plop")
        self.client.post(
            reverse("pedagogy:comment_delete", kwargs={"comment_id": self.comment.id})
        )
        self.assertFalse(UVComment.objects.filter(id=self.comment.id).exists())

    def test_uv_comment_delete_pedagogy_admin_success(self):
        self.client.login(username="tutu", password="plop")
        self.client.post(
            reverse("pedagogy:comment_delete", kwargs={"comment_id": self.comment.id})
        )
        self.assertFalse(UVComment.objects.filter(id=self.comment.id).exists())

    def test_uv_comment_delete_author_success(self):
        self.client.login(username="krophil", password="plop")
        self.client.post(
            reverse("pedagogy:comment_delete", kwargs={"comment_id": self.comment.id})
        )
        self.assertFalse(UVComment.objects.filter(id=self.comment.id).exists())

    def test_uv_comment_delete_unauthorized_fail(self):
        # Anonymous user
        response = self.client.post(
            reverse("pedagogy:comment_delete", kwargs={"comment_id": self.comment.id})
        )
        self.assertEqual(response.status_code, 403)

        # Unsbscribed user
        self.client.login(username="guy", password="plop")
        response = self.client.post(
            reverse("pedagogy:comment_delete", kwargs={"comment_id": self.comment.id})
        )
        self.assertEqual(response.status_code, 403)

        # Subscribed user (not author of the comment)
        self.client.login(username="sli", password="plop")
        response = self.client.post(
            reverse("pedagogy:comment_delete", kwargs={"comment_id": self.comment.id})
        )
        self.assertEqual(response.status_code, 403)

        # Check that the comment still exists
        self.assertTrue(UVComment.objects.filter(id=self.comment.id).exists())


class UVCommentUpdateTest(TestCase):
    """
    Test UVComment update rights
    """

    def setUp(self):
        call_command("populate")

        self.krophil = User.objects.get(username="krophil")

        # Prepare a comment
        comment_kwargs = create_uv_comment_template(self.krophil.id)
        comment_kwargs["author"] = self.krophil
        comment_kwargs["uv"] = UV.objects.get(id=comment_kwargs["uv"])
        self.comment = UVComment(**comment_kwargs)
        self.comment.save()

        # Prepare edit of this comment for post requests
        self.comment_edit = create_uv_comment_template(self.krophil.id)
        self.comment_edit["comment"] = "Edited"

    def test_uv_comment_update_root_success(self):
        self.client.login(username="root", password="plop")
        response = self.client.post(
            reverse("pedagogy:comment_update", kwargs={"comment_id": self.comment.id}),
            self.comment_edit,
        )
        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment, self.comment_edit["comment"])

    def test_uv_comment_update_pedagogy_admin_success(self):
        self.client.login(username="tutu", password="plop")
        response = self.client.post(
            reverse("pedagogy:comment_update", kwargs={"comment_id": self.comment.id}),
            self.comment_edit,
        )
        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment, self.comment_edit["comment"])

    def test_uv_comment_update_author_success(self):
        self.client.login(username="krophil", password="plop")
        response = self.client.post(
            reverse("pedagogy:comment_update", kwargs={"comment_id": self.comment.id}),
            self.comment_edit,
        )
        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.comment, self.comment_edit["comment"])

    def test_uv_comment_update_unauthorized_fail(self):
        # Anonymous user
        response = self.client.post(
            reverse("pedagogy:comment_update", kwargs={"comment_id": self.comment.id}),
            self.comment_edit,
        )
        self.assertEqual(response.status_code, 403)

        # Unsbscribed user
        response = self.client.post(
            reverse("pedagogy:comment_update", kwargs={"comment_id": self.comment.id}),
            self.comment_edit,
        )
        self.assertEqual(response.status_code, 403)

        # Subscribed user (not author of the comment)
        response = self.client.post(
            reverse("pedagogy:comment_update", kwargs={"comment_id": self.comment.id}),
            self.comment_edit,
        )
        self.assertEqual(response.status_code, 403)

        # Check that the comment hasn't change
        self.comment.refresh_from_db()
        self.assertNotEqual(self.comment.comment, self.comment_edit["comment"])

    def test_uv_comment_update_original_author_does_not_change(self):
        self.client.login(username="root", password="plop")
        self.comment_edit["author"] = User.objects.get(username="root").id

        response = self.client.post(
            reverse("pedagogy:comment_update", kwargs={"comment_id": self.comment.id}),
            self.comment_edit,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.comment.author, self.krophil)


class UVSearchTest(TestCase):
    """
    Test UV guide rights for view and API
    Test that the API is working well
    """

    def setUp(self):
        call_command("populate")
        call_command("update_index", "pedagogy")

    def test_get_page_authorized_success(self):
        # Test with root user
        self.client.login(username="root", password="plop")
        response = self.client.get(reverse("pedagogy:guide"))
        self.assertEqual(response.status_code, 200)

        # Test with pedagogy admin
        self.client.login(username="tutu", password="plop")
        response = self.client.get(reverse("pedagogy:guide"))
        self.assertEqual(response.status_code, 200)

        # Test with subscribed user
        self.client.login(username="sli", password="plop")
        response = self.client.get(reverse("pedagogy:guide"))
        self.assertEqual(response.status_code, 200)

    def test_get_page_unauthorized_fail(self):
        # Test with anonymous user
        response = self.client.get(reverse("pedagogy:guide"))
        self.assertEqual(response.status_code, 403)

        # Test with not subscribed user
        self.client.login(username="guy", password="plop")
        response = self.client.get(reverse("pedagogy:guide"))
        self.assertEqual(response.status_code, 403)

    def test_search_pa00_success(self):
        self.client.login(username="sli", password="plop")

        # Search with UV code
        response = self.client.get(reverse("pedagogy:guide"), {"search": "PA00"})
        self.assertContains(response, text="PA00")

        # Search with first letter of UV code
        response = self.client.get(reverse("pedagogy:guide"), {"search": "P"})
        self.assertContains(response, text="PA00")

        # Search with first letter of UV code in lowercase
        response = self.client.get(reverse("pedagogy:guide"), {"search": "p"})
        self.assertContains(response, text="PA00")

        # Search with UV title
        response = self.client.get(
            reverse("pedagogy:guide"), {"search": "participation"}
        )
        self.assertContains(response, text="PA00")

        # Search with UV manager
        response = self.client.get(reverse("pedagogy:guide"), {"search": "HEYBERGER"})
        self.assertContains(response, text="PA00")

        # Search with department
        response = self.client.get(reverse("pedagogy:guide"), {"department": "HUMA"})
        self.assertContains(response, text="PA00")

        # Search with semester
        response = self.client.get(reverse("pedagogy:guide"), {"semester": "AUTUMN"})
        self.assertContains(response, text="PA00")

        response = self.client.get(reverse("pedagogy:guide"), {"semester": "SPRING"})
        self.assertContains(response, text="PA00")

        response = self.client.get(
            reverse("pedagogy:guide"), {"semester": "AUTUMN_AND_SPRING"}
        )
        self.assertContains(response, text="PA00")

        # Search with language
        response = self.client.get(reverse("pedagogy:guide"), {"language": "FR"})
        self.assertContains(response, text="PA00")

        # Search with credit type
        response = self.client.get(reverse("pedagogy:guide"), {"credit_type": "OM"})
        self.assertContains(response, text="PA00")

        # Search with combinaison of all
        response = self.client.get(
            reverse("pedagogy:guide"),
            {
                "search": "P",
                "department": "HUMA",
                "semester": "AUTUMN",
                "language": "FR",
                "credit_type": "OM",
            },
        )
        self.assertContains(response, text="PA00")

        # Test json briefly
        response = self.client.get(
            reverse("pedagogy:guide"),
            {
                "json": "t",
                "search": "P",
                "department": "HUMA",
                "semester": "AUTUMN",
                "language": "FR",
                "credit_type": "OM",
            },
        )
        self.assertJSONEqual(
            response.content,
            [
                {
                    "id": 1,
                    "absolute_url": "/pedagogy/uv/1",
                    "update_url": "/pedagogy/uv/1/edit",
                    "delete_url": "/pedagogy/uv/1/delete",
                    "code": "PA00",
                    "author": 0,
                    "credit_type": "OM",
                    "semester": "AUTUMN_AND_SPRING",
                    "language": "FR",
                    "credits": 5,
                    "department": "HUMA",
                    "title": "Participation dans une association \u00e9tudiante",
                    "manager": "Laurent HEYBERGER",
                    "objectives": "* Permettre aux \u00e9tudiants de r\u00e9aliser, pendant un semestre, un projet culturel ou associatif et de le valoriser.",
                    "program": "* Semestre pr\u00e9c\u00e9dent proposition d'un projet et d'un cahier des charges\n* Evaluation par un jury de six membres\n* Si accord r\u00e9alisation dans le cadre de l'UV\n* Compte-rendu de l'exp\u00e9rience\n* Pr\u00e9sentation",
                    "skills": "* G\u00e9rer un projet associatif ou une action \u00e9ducative en autonomie:\n* en produisant un cahier des charges qui -d\u00e9finit clairement le contexte du projet personnel -pose les jalons de ce projet -estime de mani\u00e8re r\u00e9aliste les moyens et objectifs du projet -d\u00e9finit exactement les livrables attendus\n    * en \u00e9tant capable de respecter ce cahier des charges ou, le cas \u00e9ch\u00e9ant, de r\u00e9viser le cahier des charges de mani\u00e8re argument\u00e9e.\n* Relater son exp\u00e9rience dans un rapport:\n* qui permettra \u00e0 d'autres \u00e9tudiants de poursuivre les actions engag\u00e9es\n* qui montre la capacit\u00e9 \u00e0 s'auto-\u00e9valuer et \u00e0 adopter une distance critique sur son action.",
                    "key_concepts": "* Autonomie\n* Responsabilit\u00e9\n* Cahier des charges\n* Gestion de projet",
                    "hours_CM": 0,
                    "hours_TD": 0,
                    "hours_TP": 0,
                    "hours_THE": 121,
                    "hours_TE": 4,
                }
            ],
        )

    def test_search_pa00_fail(self):

        # Search with UV code
        response = self.client.get(reverse("pedagogy:guide"), {"search": "IFC"})
        self.assertNotContains(response, text="PA00")

        # Search with first letter of UV code
        response = self.client.get(reverse("pedagogy:guide"), {"search": "I"})
        self.assertNotContains(response, text="PA00")

        # Search with UV manager
        response = self.client.get(reverse("pedagogy:guide"), {"search": "GILLES"})
        self.assertNotContains(response, text="PA00")

        # Search with department
        response = self.client.get(reverse("pedagogy:guide"), {"department": "TC"})
        self.assertNotContains(response, text="PA00")

        # Search with semester
        response = self.client.get(reverse("pedagogy:guide"), {"semester": "CLOSED"})
        self.assertNotContains(response, text="PA00")

        # Search with language
        response = self.client.get(reverse("pedagogy:guide"), {"language": "EN"})
        self.assertNotContains(response, text="PA00")

        # Search with credit type
        response = self.client.get(reverse("pedagogy:guide"), {"credit_type": "TM"})
        self.assertNotContains(response, text="PA00")


class UVModerationFormTest(TestCase):
    """
    Test moderation view
    Assert access rights and if the form works well
    """

    def setUp(self):
        call_command("populate")

        self.krophil = User.objects.get(username="krophil")

        # Prepare a comment
        comment_kwargs = create_uv_comment_template(self.krophil.id)
        comment_kwargs["author"] = self.krophil
        comment_kwargs["uv"] = UV.objects.get(id=comment_kwargs["uv"])
        self.comment_1 = UVComment(**comment_kwargs)
        self.comment_1.save()

        # Prepare another comment
        comment_kwargs = create_uv_comment_template(self.krophil.id)
        comment_kwargs["author"] = self.krophil
        comment_kwargs["uv"] = UV.objects.get(id=comment_kwargs["uv"])
        self.comment_2 = UVComment(**comment_kwargs)
        self.comment_2.save()

        # Prepare a comment report for comment 1
        self.report_1 = UVCommentReport(
            comment=self.comment_1, reporter=self.krophil, reason="C'est moche"
        )
        self.report_1.save()
        self.report_1_bis = UVCommentReport(
            comment=self.comment_1, reporter=self.krophil, reason="C'est moche 2"
        )
        self.report_1_bis.save()

        # Prepare a comment report for comment 2
        self.report_2 = UVCommentReport(
            comment=self.comment_2, reporter=self.krophil, reason="C'est moche"
        )
        self.report_2.save()

    def test_access_authorized_success(self):
        # Test with root
        self.client.login(username="root", password="plop")
        response = self.client.get(reverse("pedagogy:moderation"))
        self.assertEqual(response.status_code, 200)

        # Test with pedagogy admin
        self.client.login(username="tutu", password="plop")
        response = self.client.get(reverse("pedagogy:moderation"))
        self.assertEqual(response.status_code, 200)

    def test_access_unauthorized_fail(self):
        # Test with anonymous user
        response = self.client.get(reverse("pedagogy:moderation"))
        self.assertEqual(response.status_code, 403)

        # Test with unsubscribed user
        self.client.login(username="guy", password="plop")
        response = self.client.get(reverse("pedagogy:moderation"))
        self.assertEqual(response.status_code, 403)

        # Test with subscribed user
        self.client.login(username="sli", password="plop")
        response = self.client.get(reverse("pedagogy:moderation"))
        self.assertEqual(response.status_code, 403)

    def test_do_nothing(self):
        self.client.login(username="root", password="plop")
        response = self.client.post(reverse("pedagogy:moderation"))
        self.assertEqual(response.status_code, 302)

        # Test that nothing has changed
        self.assertTrue(UVCommentReport.objects.filter(id=self.report_1.id).exists())
        self.assertTrue(UVComment.objects.filter(id=self.comment_1.id).exists())
        self.assertTrue(
            UVCommentReport.objects.filter(id=self.report_1_bis.id).exists()
        )
        self.assertTrue(UVCommentReport.objects.filter(id=self.report_2.id).exists())
        self.assertTrue(UVComment.objects.filter(id=self.comment_2.id).exists())

    def test_delete_comment(self):
        self.client.login(username="root", password="plop")
        response = self.client.post(
            reverse("pedagogy:moderation"), {"accepted_reports": [self.report_1.id]}
        )
        self.assertEqual(response.status_code, 302)

        # Test that the comment and it's associated report has been deleted
        self.assertFalse(UVCommentReport.objects.filter(id=self.report_1.id).exists())
        self.assertFalse(UVComment.objects.filter(id=self.comment_1.id).exists())
        # Test that the bis report has been deleted
        self.assertFalse(
            UVCommentReport.objects.filter(id=self.report_1_bis.id).exists()
        )

        # Test that the other comment and report still exists
        self.assertTrue(UVCommentReport.objects.filter(id=self.report_2.id).exists())
        self.assertTrue(UVComment.objects.filter(id=self.comment_2.id).exists())

    def test_delete_comment_bulk(self):
        self.client.login(username="root", password="plop")
        response = self.client.post(
            reverse("pedagogy:moderation"),
            {"accepted_reports": [self.report_1.id, self.report_2.id]},
        )
        self.assertEqual(response.status_code, 302)

        # Test that comments and their associated reports has been deleted
        self.assertFalse(UVCommentReport.objects.filter(id=self.report_1.id).exists())
        self.assertFalse(UVComment.objects.filter(id=self.comment_1.id).exists())
        self.assertFalse(UVCommentReport.objects.filter(id=self.report_2.id).exists())
        self.assertFalse(UVComment.objects.filter(id=self.comment_2.id).exists())
        # Test that the bis report has been deleted
        self.assertFalse(
            UVCommentReport.objects.filter(id=self.report_1_bis.id).exists()
        )

    def test_delete_comment_with_bis(self):
        # Test case if two reports targets the same comment and are both deleted
        self.client.login(username="root", password="plop")
        response = self.client.post(
            reverse("pedagogy:moderation"),
            {"accepted_reports": [self.report_1.id, self.report_1_bis.id]},
        )
        self.assertEqual(response.status_code, 302)

        # Test that the comment and it's associated report has been deleted
        self.assertFalse(UVCommentReport.objects.filter(id=self.report_1.id).exists())
        self.assertFalse(UVComment.objects.filter(id=self.comment_1.id).exists())
        # Test that the bis report has been deleted
        self.assertFalse(
            UVCommentReport.objects.filter(id=self.report_1_bis.id).exists()
        )

    def test_delete_report(self):
        self.client.login(username="root", password="plop")
        response = self.client.post(
            reverse("pedagogy:moderation"), {"denied_reports": [self.report_1.id]}
        )
        self.assertEqual(response.status_code, 302)

        # Test that the report has been deleted and that the comment still exists
        self.assertFalse(UVCommentReport.objects.filter(id=self.report_1.id).exists())
        self.assertTrue(UVComment.objects.filter(id=self.comment_1.id).exists())
        # Test that the bis report is still there
        self.assertTrue(
            UVCommentReport.objects.filter(id=self.report_1_bis.id).exists()
        )

        # Test that the other comment and report still exists
        self.assertTrue(UVCommentReport.objects.filter(id=self.report_2.id).exists())
        self.assertTrue(UVComment.objects.filter(id=self.comment_2.id).exists())

    def test_delete_report_bulk(self):
        self.client.login(username="root", password="plop")
        response = self.client.post(
            reverse("pedagogy:moderation"),
            {
                "denied_reports": [
                    self.report_1.id,
                    self.report_1_bis.id,
                    self.report_2.id,
                ]
            },
        )
        self.assertEqual(response.status_code, 302)

        # Test that every reports has been deleted
        self.assertFalse(UVCommentReport.objects.filter(id=self.report_1.id).exists())
        self.assertFalse(
            UVCommentReport.objects.filter(id=self.report_1_bis.id).exists()
        )
        self.assertFalse(UVCommentReport.objects.filter(id=self.report_2.id).exists())

        # Test that comments still exists
        self.assertTrue(UVComment.objects.filter(id=self.comment_1.id).exists())
        self.assertTrue(UVComment.objects.filter(id=self.comment_2.id).exists())

    def test_delete_mixed(self):
        self.client.login(username="root", password="plop")
        response = self.client.post(
            reverse("pedagogy:moderation"),
            {
                "accepted_reports": [self.report_2.id],
                "denied_reports": [self.report_1.id],
            },
        )
        self.assertEqual(response.status_code, 302)

        # Test that report 2 and his comment has been deleted
        self.assertFalse(UVCommentReport.objects.filter(id=self.report_2.id).exists())
        self.assertFalse(UVComment.objects.filter(id=self.comment_2.id).exists())

        # Test that report 1 has been deleted and it's comment still exists
        self.assertFalse(UVCommentReport.objects.filter(id=self.report_1.id).exists())
        self.assertTrue(UVComment.objects.filter(id=self.comment_1.id).exists())

        # Test that report 1 bis is still there
        self.assertTrue(
            UVCommentReport.objects.filter(id=self.report_1_bis.id).exists()
        )

    def test_delete_mixed_with_bis(self):
        self.client.login(username="root", password="plop")
        response = self.client.post(
            reverse("pedagogy:moderation"),
            {
                "accepted_reports": [self.report_1.id],
                "denied_reports": [self.report_1_bis.id],
            },
        )
        self.assertEqual(response.status_code, 302)

        # Test that report 1 and 1 bis has been deleted
        self.assertFalse(
            UVCommentReport.objects.filter(
                id__in=[self.report_1.id, self.report_1_bis.id]
            ).exists()
        )

        # Test that comment 1 has been deleted
        self.assertFalse(UVComment.objects.filter(id=self.comment_1.id).exists())

        # Test that report and comment 2 still exists
        self.assertTrue(UVCommentReport.objects.filter(id=self.report_2.id).exists())
        self.assertTrue(UVComment.objects.filter(id=self.comment_2.id).exists())


class UVCommentReportCreateTest(TestCase):
    """
    Test report creation view view
    Assert access rights and if you can create with it
    """

    def setUp(self):
        call_command("populate")

        self.krophil = User.objects.get(username="krophil")
        self.tutu = User.objects.get(username="tutu")

        # Prepare a comment
        comment_kwargs = create_uv_comment_template(self.krophil.id)
        comment_kwargs["author"] = self.krophil
        comment_kwargs["uv"] = UV.objects.get(id=comment_kwargs["uv"])
        self.comment = UVComment(**comment_kwargs)
        self.comment.save()

    def create_report_test(self, username, success):
        self.client.login(username=username, password="plop")
        response = self.client.post(
            reverse("pedagogy:comment_report", kwargs={"comment_id": self.comment.id}),
            {
                "comment": self.comment.id,
                "reporter": User.objects.get(username=username).id,
                "reason": "C'est moche",
            },
        )
        if success:
            self.assertEqual(response.status_code, 302)
        else:
            self.assertEqual(response.status_code, 403)
        self.assertEqual(UVCommentReport.objects.all().exists(), success)

    def test_create_report_root_success(self):
        self.create_report_test("root", True)

    def test_create_report_pedagogy_admin_success(self):
        self.create_report_test("tutu", True)

    def test_create_report_subscriber_success(self):
        self.create_report_test("sli", True)

    def test_create_report_unsubscribed_fail(self):
        self.create_report_test("guy", False)

    def test_create_report_anonymous_fail(self):
        response = self.client.post(
            reverse("pedagogy:comment_report", kwargs={"comment_id": self.comment.id}),
            {"comment": self.comment.id, "reporter": 0, "reason": "C'est moche"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(UVCommentReport.objects.all().exists())

    def test_notifications(self):
        self.assertFalse(
            self.tutu.notifications.filter(type="PEDAGOGY_MODERATION").exists()
        )
        # Create a comment report
        self.create_report_test("tutu", True)

        # Check that a notification has been created for pedagogy admins
        self.assertTrue(
            self.tutu.notifications.filter(type="PEDAGOGY_MODERATION").exists()
        )

        # Check that only pedagogy admins recieves this notification
        for notif in Notification.objects.filter(type="PEDAGOGY_MODERATION").all():
            self.assertTrue(
                notif.user.is_in_group(settings.SITH_GROUP_PEDAGOGY_ADMIN_ID)
            )

        # Check that notifications are not duplicated if not viewed
        self.create_report_test("tutu", True)
        self.assertEqual(
            self.tutu.notifications.filter(type="PEDAGOGY_MODERATION").count(), 1
        )

        # Check that a new notification is created when the old one has been viewed
        notif = self.tutu.notifications.filter(type="PEDAGOGY_MODERATION").first()
        notif.viewed = True
        notif.save()

        self.create_report_test("tutu", True)

        self.assertEqual(
            self.tutu.notifications.filter(type="PEDAGOGY_MODERATION").count(), 2
        )
