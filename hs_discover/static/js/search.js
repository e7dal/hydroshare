Vue.component('resource-listing', {
    props:
        ['sample', 'itemcount', 'columns', 'resources', 'filterKey'],
    template: `
        <div>
<!--            <p class="items-counter">-->
<!--                {{ numItems }} items-->
<!--            </p>-->
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
                <td>
                    <a v-bind:href="entry.link">{{ entry.name }}</a>
                </td>
                <td></td>  <!-- temporary placeholder for link column, until header display approach is refactored -->
                <td>{{ entry.type }}</td>
                <td>{{ entry.availability }}</td>
                <td>
                    <a v-bind:href="entry.author_link">{{ entry.author }}</a>
                </td>
                <td></td>  <!-- temporary placeholder for link column, until header display approach is refactored -->
                <td>{{ entry.created }}</td>
                <td>{{ entry.modified }}</td>
            </tr>
            </tbody>
        </table>
        </div>`,
    data: function () {
        this.itemcount ? this.numItems = this.itemcount : this.numItems = 0;
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
            let resources = JSON.parse(this.sample);  // TODO validation, security, error handling
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
            // Vue.set('numItems', 2);
            this.numItems = resources.length;
            return resources
        }
    },
    filters: {
        capitalize: function (str) {
            if (str !== "link" && str !== "author_link") {  // TODO instead of iterating through headings, explicitly choose and display
                return str.charAt(0).toUpperCase() + str.slice(1)
            }
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
        gridColumns: ['name', 'link', 'type', 'availability', 'author', 'author_link', 'created', 'modified'],
    },
    components: {
        VueBootstrapTypeahead
    },
    beforeMount: function() {
        this.$data.searchQuery = q;
    },
    methods: {
        searchClick: function (csrf_token) {
            window.location="/search/?q="+this.$data.searchQuery  // TODO validation or complete refactor anyway
            // console.log(this)
            // let formData = new FormData();
            // formData.append("csrfmiddlewaretoken", csrf_token);
            // formData.append("q", this.searchQuery);
            // $.ajax({
            //     type: "POST",
            //     data: formData,
            //     processData: false,
            //     contentType: false,
            //     url: "/search/",
            //     success: function (response) {
            //         console.log("Successful post")
            //     },
            //     error: function (response) {
            //         console.log(response.responseText);
            //     }
            // });
        }
    }
});
