//https://jsfiddle.net/Tertia/vbyon64p/6/?utm_source=website&utm_medium=embed&utm_campaign=vbyon64p
Vue.component('demo-grid', {
    template: '#grid-template',
    props: {
        heroes: Array,
        columns: Array,
        filterKey: String
    },
    data: function () {
        var sortOrders = {};
        this.columns.forEach(function (key) {
          sortOrders[key] = 1
        })
        return {
            sortKey: '',
            sortOrders: sortOrders
        }
    },
    computed: {
        filteredHeroes: function () {
            var sortKey = this.sortKey;
            var filterKey = this.filterKey && this.filterKey.toLowerCase();
            var order = this.sortOrders[sortKey] || 1;
            var heroes = this.heroes;
            if (filterKey) {
                heroes = heroes.filter(function (row) {
                    return Object.keys(row).some(function (key) {
                        return String(row[key]).toLowerCase().indexOf(filterKey) > -1
                    })
                })
            }
            if (sortKey) {
                heroes = heroes.slice().sort(function (a, b) {
                    a = a[sortKey];
                    b = b[sortKey];
                    return (a === b ? 0 : a > b ? 1 : -1) * order
                })
            }
            return heroes
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
        },
        searchClick: function () {
            console.log('asdf')
        }
    }
});

var demo = new Vue({
    el: '#demo',
    data: {
        searchQuery: '',
        gridColumns: ['name', 'author'],
        gridData: [
            {
                name: 'SSCZO - Flux Tower, Meteorology - Flux Tower Transect, Soaproot Saddle (2009-2016)',
                author: 'Kim Dailey'
            },
            {
                name: 'LCZO - Soil Biogeochemistry - landscape-scale soil biogeochemistry and enzymes - Bisley (2012)',
                author: 'Roger Downs'
            },
            {name: 'X-CZO - Flux Tower - AmeriFlux Network data - National (2007-2018)', author: 'Jill Hickey'},
            {
                name: 'BCCZO - Precipitation - B1 Historical Precipitation Site (B1_Hist_Precip) - B1 Historical Site (1952-1964)',
                author: 'Ed Brown'
            }
        ]
    }
});
