Vue.component('discover-grid', {
    template: '#grid-template',
    props: {
        resources: Array,
        columns: Array,
        filterKey: String
    },
    data: function () {
        let sortOrders = {};
        this.columns.forEach(function (key) {
          sortOrders[key] = 1
        });
        return {
            sortKey: '',
            sortOrders: sortOrders
        }
    },
    computed: {
        filteredResources: function () {
            let sortKey = this.sortKey;
            let filterKey = this.filterKey && this.filterKey.toLowerCase();
            let order = this.sortOrders[sortKey] || 1;
            let resources = this.resources;
            if (filterKey) {
                resources = resources.filter(function (row) {
                    return Object.keys(row).some(function (key) {
                        return String(row[key]).toLowerCase().indexOf(filterKey) > -1
                    })
                })
            }
            if (sortKey) {
                resources = resources.slice().sort(function (a, b) {
                    a = a[sortKey];
                    b = b[sortKey];
                    return (a === b ? 0 : a > b ? 1 : -1) * order
                })
            }
            return resources
        }
    },
    filters: {
        capitalize: function (str) {
            return str.charAt(0).toUpperCase() + str.slice(1)
        }
    },
    methods: {
        sortBy: function (key) {
            this.sortKey = key;
            this.sortOrders[key] = this.sortOrders[key] * -1
        }
    }
});

let DiscoverApp = new Vue({
    el: '#discover-search',
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
        searchClick: function (csrf_token, ev, topic) {
            let formData = new FormData();
            // Vue.set(topic, 'edit', false);
            // TODO all the querystring params
            formData.append("csrfmiddlewaretoken", csrf_token);
            formData.append("id", topic.val[0].toString());
            formData.append("name", topic.val[1].toString());
            formData.append("action", "UPDATE");
            $.ajax({
                type: "POST",
                data: formData,
                processData: false,
                contentType: false,
                url: "/the_endpoint_for_discover/",
                success: function (response) {
                    // do nothing
                },
                error: function (response) {
                    console.log(response.responseText);
                }
            });
        }
    }
});
