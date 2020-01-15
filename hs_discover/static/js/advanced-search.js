

let AdvancedSearchApp = new Vue({
    el: '#advanced-discover-search',
    data: {
        searchQuery: '',
        gridColumns: ['name', 'type', 'author'],
        gridData: [
            {
                name: 'SSCZO - Flux Tower, Meteorology - Flux Tower Transect, Soaproot Saddle (2009-2016)',
                type: 'GenericResource',
                author: 'Kim Dailey'
            },
            {
                name: 'LCZO - Soil Biogeochemistry - landscape-scale soil biogeochemistry and enzymes - Bisley (2012)',
                type: 'CollectionResource',
                author: 'Roger Downs'
            },
            {
                name: 'X-CZO - Flux Tower - AmeriFlux Network data - National (2007-2018)',
                type: 'GenericResource',
                author: 'Jill Hickey'
            },
            {
                name: 'BCCZO - Precipitation - B1 Historical Precipitation Site (B1_Hist_Precip) - B1 Historical Site (1952-1964)',
                type: 'GenericResource',
                author: 'Ed Brown'
            }
        ]
    },
    methods: {
        searchClick: function (csrf_token) {
            let formData = new FormData();
            formData.append("csrfmiddlewaretoken", csrf_token);
            console.log(this.$data.searchQuery);
            formData.append("q", this.$data.searchQuery);

            $.ajax({
                type: "POST",
                data: formData,
                processData: false,
                contentType: false,
                url: "/advanced-search/",
                success: function (response) {
                    console.log("successful query post")
                },
                error: function (response) {
                    console.log(response.responseText);
                }
            });
        }
    }
});
