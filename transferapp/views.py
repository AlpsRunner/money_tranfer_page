from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from transferapp.forms import TranferForm


class TransferPage(FormView):
    form_class = TranferForm
    template_name = 'transferapp/transfer_page.html'
    success_url = 'transfer_success_page'

    def form_valid(self, form):
        src_user = form.save()
        return HttpResponseRedirect(
            reverse(
                self.get_success_url(),
                kwargs={
                    'src_user': src_user.pk,
                }
            )
        )


class TransferSuccessPage(TemplateView):
    template_name = 'transferapp/transfer_success_page.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        data['src_user'] = get_object_or_404(get_user_model(), pk=kwargs.get('src_user'))
        return data
