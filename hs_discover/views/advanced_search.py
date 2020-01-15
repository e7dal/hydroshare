from __future__ import absolute_import

from django.shortcuts import render
import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.html import mark_safe, escapejs
from django.views.generic import TemplateView

from hs_access_control.management.utilities import community_from_name_or_id
from hs_access_control.models.community import Community
from hs_access_control.models.privilege import UserCommunityPrivilege, PrivilegeCodes
from hs_communities.models import Topic
from django.views.generic import TemplateView


class AdvancedSearchView(TemplateView):
    # def dispatch(self, *args, **kwargs):
    #     return super(DiscoverView, self).dispatch(*args, **kwargs)

    # def get_context_data(self, **kwargs):
    #     grpfilter = self.request.GET.get('grp')
    #     u = User.objects.get(pk=self.request.user.id)

    def get(self, request, *args, **kwargs):
        u = User.objects.get(pk=self.request.user.id)

        sample_data = "sample data"

        return render(request, 'hs_discover/advanced_search.html', {
            'user': u,
            'sample_data': sample_data
        })

    def post(self, request, *args, **kwargs):
        u = User.objects.get(pk=self.request.user.id)

        # perform haystack search
        print("hello world", request.POST.get('q'))

        return render(request, 'hs_discover/results.html', {
            'hits': "sample results"
        })
