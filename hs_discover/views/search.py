from django.shortcuts import render
import json

from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect
from django.views.generic import TemplateView


class SearchView(TemplateView):
    template_name = 'hs_discover/search.html'

    # def dispatch(self, *args, **kwargs):
    #     return super(DiscoverView, self).dispatch(*args, **kwargs)

    # def get_context_data(self, **kwargs):
    #     grpfilter = self.request.GET.get('grp')
    #     u = User.objects.get(pk=self.request.user.id)

    def get(self, request, *args, **kwargs):
        u = User.objects.get(pk=self.request.user.id)

        sample_data = json.dumps([
            {
                "name": "SSCZO - Flux Tower, Meteorology - Flux Tower Transect, Soaproot Saddle (2009-2016)",
                "type": "GenericResource",
                "author": "Kim Dailey",
                "created": "Apr 23 2019 - 7:31am",
                "modified": "Apr 23 2019 - 7:31am"
            },
            {
                "name": "LCZO - Soil Biogeochemistry - landscape-scale soil biogeochemistry and enzymes - Bisley (2012)",
                "type": "CollectionResource",
                "author": "Roger Downs",
                "created": "Apr 23 2019 - 8:31am",
                "modified": "Apr 23 2019 - 9:31am"
            },
            {
                "name": "X-CZO - Flux Tower - AmeriFlux Network data - National (2007-2018)",
                "type": "GenericResource",
                "author": "Jill Hickey",
                "created": "Apr 23 2019 - 10:31am",
                "modified": "Apr 23 2019 - 11:31am"
            },
            {
                "name": "BCCZO - Precipitation - B1 Historical Precipitation Site (B1_Hist_Precip) - B1 Historical Site (1952-1964)",
                "type": "GenericResource",
                "author": "Ed Brown",
                "created": "Apr 23 2019 - 6:31pm",
                "modified": "Apr 23 2019 - 7:31pm"
            }
        ])

        return render(request, 'hs_discover/search.html', {
            'user': u,
            'sample_data': sample_data
        })

    def post(self, request, *args, **kwargs):
        # u = User.objects.get(pk=self.request.user.id)

        # perform haystack search
        print("hello world")
        return render(request, 'hs_discover/search.html')
