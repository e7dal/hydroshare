import json

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from haystack.query import SearchQuerySet


class SearchView(TemplateView):

    def get(self, request, *args, **kwargs):

        sqs = SearchQuerySet().all()
        total_results = sqs.count()

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

        resources = json.dumps(resources)
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

        if request.GET.get('mode') == 'advanced':
            return render(request, 'hs_discover/advanced_search.html')
        else:
            return render(request, 'hs_discover/search.html', {
                'resources': resources,
                'q': request.GET.get('q')
            })
