from django.shortcuts import render
import json

from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from haystack.generic_views import FacetedSearchView
from haystack.generic_views import FacetedSearchMixin
from hs_core.discovery_form import DiscoveryForm, FACETS_TO_SHOW
from haystack.query import SearchQuerySet
from django.conf import settings


class SearchView(TemplateView):
    template_name = 'hs_discover/search.html'

    # def dispatch(self, *args, **kwargs):
    #     return super(DiscoverView, self).dispatch(*args, **kwargs)

    # def get_context_data(self, **kwargs):
    #     grpfilter = self.request.GET.get('grp')
    #     u = User.objects.get(pk=self.request.user.id)

    def get(self, request, *args, **kwargs):
        # u = User.objects.get(pk=self.request.user.id)

        sqs = SearchQuerySet().all()

        resources = []
        # TODO error handling and try except
        for result in sqs:
            resources.append({
                "name": result.title,
                "type": result.resource_type_exact,
                "author": result.author,
                "created": str(result.created),
                "modified": str(result.modified)
            })

        sample_data = json.dumps(resources)
        # sample_data = json.dumps([
        #     {
        #         "name": "SSCZO - Flux Tower, Meteorology - Flux Tower Transect, Soaproot Saddle (2009-2016)",
        #         "type": "GenericResource",
        #         "author": "Kim Dailey",
        #         "created": "Apr 23 2019 - 7:31am",
        #         "modified": "Apr 23 2019 - 7:31am"
        #     },
        #     {
        #         "name": "LCZO - Soil Biogeochemistry - landscape-scale soil biogeochemistry and enzymes - Bisley (2012)",
        #         "type": "CollectionResource",
        #         "author": "Roger Downs",
        #         "created": "Apr 23 2019 - 8:31am",
        #         "modified": "Apr 23 2019 - 9:31am"
        #     },
        #     {
        #         "name": "X-CZO - Flux Tower - AmeriFlux Network data - National (2007-2018)",
        #         "type": "GenericResource",
        #         "author": "Jill Hickey",
        #         "created": "Apr 23 2019 - 10:31am",
        #         "modified": "Apr 23 2019 - 11:31am"
        #     },
        #     {
        #         "name": "BCCZO - Precipitation - B1 Historical Precipitation Site (B1_Hist_Precip) - B1 Historical Site (1952-1964)",
        #         "type": "GenericResource",
        #         "author": "Ed Brown",
        #         "created": "Apr 23 2019 - 6:31pm",
        #         "modified": "Apr 23 2019 - 7:31pm"
        #     }
        # ])

        return render(request, 'hs_discover/search.html', {
            # 'user': u,
            'sample_data': sample_data
        })

    def post(self, request, *args, **kwargs):
        # u = User.objects.get(pk=self.request.user.id)
        sqs = SearchQuerySet().all()

        total_results = sqs.count()
        print("hello world", total_results)
        return render(request, 'hs_discover/search.html')
