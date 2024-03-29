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

import base64
import json
import sentry_sdk

from datetime import datetime
from urllib.parse import unquote
from OpenSSL import crypto
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.db import transaction, DatabaseError
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import TemplateView, View

from counter.forms import BillingInfoForm
from counter.models import Customer, Counter, Product
from eboutic.forms import BasketForm
from eboutic.models import Basket, Invoice, InvoiceItem, get_eboutic_products


@login_required
@require_GET
def eboutic_main(request: HttpRequest) -> HttpResponse:
    """
    Main view of the eboutic application.
    Return an Http response whose content is of type text/html.
    The latter represents the page from which a user can see
    the catalogue of products that he can buy and fill
    his shopping cart.

    The purchasable products are those of the eboutic which
    belong to a category of products of a product category
    (orphan products are inaccessible).

    If the session contains a key-value pair that associates "errors"
    with a list of strings, this pair is removed from the session
    and its value displayed to the user when the page is rendered.
    """
    errors = request.session.pop("errors", None)
    products = get_eboutic_products(request.user)
    context = {
        "errors": errors,
        "products": products,
        "customer_amount": request.user.account_balance,
    }
    return render(request, "eboutic/eboutic_main.jinja", context)


@require_GET
@login_required
def payment_result(request, result: str) -> HttpResponse:
    context = {"success": result == "success"}
    return render(request, "eboutic/eboutic_payment_result.jinja", context)


class EbouticCommand(TemplateView):
    template_name = "eboutic/eboutic_makecommand.jinja"

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return redirect("eboutic:main")

    @method_decorator(login_required)
    def get(self, request: HttpRequest, *args, **kwargs):
        form = BasketForm(request)
        if not form.is_valid():
            request.session["errors"] = form.get_error_messages()
            request.session.modified = True
            res = redirect("eboutic:main")
            res.set_cookie("basket_items", form.get_cleaned_cookie(), path="/eboutic")
            return res

        basket = Basket.from_session(request.session)
        if basket is not None:
            basket.clear()
        else:
            basket = Basket.objects.create(user=request.user)
            request.session["basket_id"] = basket.id
            request.session.modified = True

        items = json.loads(unquote(request.COOKIES["basket_items"]))
        items.sort(key=lambda item: item["id"])
        ids = [item["id"] for item in items]
        quantities = [item["quantity"] for item in items]
        products = Product.objects.filter(id__in=ids)
        for product, qty in zip(products, quantities):
            basket.add_product(product, qty)
        kwargs["basket"] = basket
        return self.render_to_response(self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        # basket is already in kwargs when the method is called
        default_billing_info = None
        if hasattr(self.request.user, "customer"):
            customer = self.request.user.customer
            kwargs["customer_amount"] = customer.amount
            if hasattr(customer, "billing_infos"):
                default_billing_info = customer.billing_infos
        else:
            kwargs["customer_amount"] = None
        kwargs["must_fill_billing_infos"] = default_billing_info is None
        if not kwargs["must_fill_billing_infos"]:
            # the user has already filled its billing_infos, thus we can
            # get it without expecting an error
            data = kwargs["basket"].get_e_transaction_data()
            data = {"data": [{"key": key, "value": val} for key, val in data]}
            kwargs["billing_infos"] = json.dumps(data)
        kwargs["billing_form"] = BillingInfoForm(instance=default_billing_info)
        return kwargs


@login_required
@require_GET
def e_transaction_data(request):
    basket = Basket.from_session(request.session)
    if basket is None:
        return HttpResponse(status=404, content=json.dumps({"data": []}))
    data = basket.get_e_transaction_data()
    data = {"data": [{"key": key, "value": val} for key, val in data]}
    return HttpResponse(status=200, content=json.dumps(data))


@login_required
@require_POST
def pay_with_sith(request):
    basket = Basket.from_session(request.session)
    refilling = settings.SITH_COUNTER_PRODUCTTYPE_REFILLING
    if basket is None or basket.items.filter(type_id=refilling).exists():
        return redirect("eboutic:main")
    c = Customer.objects.filter(user__id=basket.user.id).first()
    if c is None:
        return redirect("eboutic:main")
    if c.amount < basket.get_total():
        res = redirect("eboutic:payment_result", "failure")
    else:
        eboutic = Counter.objects.filter(type="EBOUTIC").first()
        sales = basket.generate_sales(eboutic, c.user, "SITH_ACCOUNT")
        try:
            with transaction.atomic():
                for sale in sales:
                    sale.save()
                basket.delete()
            request.session.pop("basket_id", None)
            res = redirect("eboutic:payment_result", "success")
        except DatabaseError as e:
            with sentry_sdk.push_scope() as scope:
                scope.user = {"username": request.user.username}
                scope.set_extra("someVariable", e.__repr__())
                sentry_sdk.capture_message(
                    f"Erreur le {datetime.now()} dans eboutic.pay_with_sith"
                )
            res = redirect("eboutic:payment_result", "failure")
    res.delete_cookie("basket_items", "/eboutic")
    return res


class EtransactionAutoAnswer(View):
    # Response documentation
    # https://www1.paybox.com/espace-integrateur-documentation/la-solution-paybox-system/gestion-de-la-reponse/
    def get(self, request, *args, **kwargs):
        required = {"Amount", "BasketID", "Error", "Sig"}
        if not required.issubset(set(request.GET.keys())):
            return HttpResponse("Bad arguments", status=400)
        key = crypto.load_publickey(crypto.FILETYPE_PEM, settings.SITH_EBOUTIC_PUB_KEY)
        cert = crypto.X509()
        cert.set_pubkey(key)
        sig = base64.b64decode(request.GET["Sig"])
        try:
            crypto.verify(
                cert,
                sig,
                "&".join(request.META["QUERY_STRING"].split("&")[:-1]).encode("utf-8"),
                "sha1",
            )
        except:
            return HttpResponse("Bad signature", status=400)
        # Payment authorized:
        # * 'Error' is '00000'
        # * 'Auto' is in the request
        if request.GET["Error"] == "00000" and "Auto" in request.GET.keys():
            try:
                with transaction.atomic():
                    b = (
                        Basket.objects.select_for_update()
                        .filter(id=request.GET["BasketID"])
                        .first()
                    )
                    if b is None:
                        raise SuspiciousOperation("Basket does not exists")
                    if int(b.get_total() * 100) != int(request.GET["Amount"]):
                        raise SuspiciousOperation(
                            "Basket total and amount do not match"
                        )
                    i = Invoice()
                    i.user = b.user
                    i.payment_method = "CARD"
                    i.save()
                    for it in b.items.all():
                        InvoiceItem(
                            invoice=i,
                            product_id=it.product_id,
                            product_name=it.product_name,
                            type_id=it.type_id,
                            product_unit_price=it.product_unit_price,
                            quantity=it.quantity,
                        ).save()
                    i.validate()
                    b.delete()
            except Exception as e:
                return HttpResponse(
                    "Basket processing failed with error: " + repr(e), status=500
                )
            return HttpResponse("Payment successful", status=200)
        else:
            return HttpResponse(
                "Payment failed with error: " + request.GET["Error"], status=202
            )
