Vue.component('resource-listing', {
    props:
        ['sample', 'columns', 'resources', 'filterKey'],
    template: `
        <div>
        <table class="table-hover table-striped resource-custom-table" id="items-discovered">
            <thead>
            <tr>
                <th v-for="key in columns"
                    @click="sortBy(key)"
                    :class="{ active: sortKey == key }">
                    {{ key | capitalize }}
                    <span class="arrow" :class="sortOrders[key] > 0 ? 'asc' : 'dsc'"></span>
                </th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="entry in filteredResources">
                <td v-for="key in columns">
                    {{ entry[key] }}
                </td>
            </tr>
            </tbody>
        </table>
        </div>`,
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
            let resources = JSON.parse(this.sample);
            // console.log(resources);
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
        gridColumns: ['name', 'type', 'author', 'created', 'modified'],

    },
    methods: {
        searchClick: function (csrf_token) {
            let formData = new FormData();
            formData.append("csrfmiddlewaretoken", csrf_token);
            formData.append("q", this.searchQuery);
            $.ajax({
                type: "POST",
                data: formData,
                processData: false,
                contentType: false,
                url: "/search/",
                success: function (response) {
                    console.log("Successful post")
                },
                error: function (response) {
                    console.log(response.responseText);
                }
            });
        }
    }
});
