from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Q
from django.http import HttpResponse
from django.utils import html
from django.utils.text import slugify
from haystack.query import SearchQuerySet
from ninja import FilterSchema, ModelSchema, Query
from ninja_extra import ControllerBase, api_controller, paginate, route
from ninja_extra.exceptions import PermissionDenied
from ninja_extra.pagination import PageNumberPaginationExtra
from ninja_extra.schemas import PaginatedResponseSchema

from club.models import Mailing
from core.api_permissions import IsLoggedInCounter, IsOldSubscriber, IsRoot
from core.models import User
from core.schemas import MarkdownSchema
from core.templatetags.renderer import markdown


@api_controller("/markdown")
class MarkdownController(ControllerBase):
    @route.post("", url_name="markdown")
    def render_markdown(self, body: MarkdownSchema):
        """Convert the markdown text into html."""
        return HttpResponse(markdown(body.text), content_type="text/html")


@api_controller("/mailings")
class MailingListController(ControllerBase):
    @route.get("", response=str)
    def fetch_mailing_lists(self, key: str):
        if key != settings.SITH_MAILING_FETCH_KEY:
            raise PermissionDenied
        mailings = Mailing.objects.filter(
            is_moderated=True, club__is_active=True
        ).prefetch_related("subscriptions")
        data = "\n".join(m.fetch_format() for m in mailings)
        return data


class UserLookupSchema(ModelSchema):
    class Meta:
        model = User
        fields = [
            "id",
        ]

    picture: str
    text: str

    @staticmethod
    def resolve_picture(obj: User) -> str:
        if obj.profile_pict:
            return obj.profile_pict.get_download_url()
        print(staticfiles_storage.url("core/img/unknown.jpg"))
        return staticfiles_storage.url("core/img/unknown.jpg")

    @staticmethod
    def resolve_text(obj: User) -> str:
        return html.escape(obj.get_display_name())


class UserFilterLookupSchema(FilterSchema):
    search: str | None = ""
    exclude: list[int] | None = []

    def filter_search(self, value: str | None) -> Q:
        if not value:
            return Q()

        value = slugify(value).replace("-", " ")
        value = html.escape(value)
        if len(value) < 1:
            return Q()

        return Q(
            id__in=list(
                SearchQuerySet()
                .models(User)
                .autocomplete(auto=value)
                .order_by("-last_update")
                .values_list("pk", flat=True)
            )
        )

    def filter_exclude(self, value: list[int] | None) -> Q:
        return ~Q(id__in=value)


CanViewLookup = [IsOldSubscriber | IsRoot | IsLoggedInCounter]


@api_controller("/lookups")
class LookupController(ControllerBase):
    @route.get(
        "/users/",
        response=PaginatedResponseSchema[UserLookupSchema],
        permissions=CanViewLookup,
    )
    @paginate(PageNumberPaginationExtra, page_size=20)
    def lookup_users(self, search: Query[UserFilterLookupSchema]):
        return search.filter(User.objects.all())
