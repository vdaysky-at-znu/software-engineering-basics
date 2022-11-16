<template>
  <v-container class="pa-0">
    <v-row v-if="interactive">
      <v-col class="pa-0">
        <v-container>
          <v-row>
            <v-col class="d-flex align-end">
              <slot name="createForm"> </slot>
            </v-col>

            <v-col>
              <div class="d-flex">
                <v-text-field
                  clearable
                  v-model="filtering.query"
                  label="Search..."
                  hide-details="hide"
                >
                  <template v-slot:appendInner="{}">
                    <v-icon>mdi-magnify</v-icon>
                  </template>
                </v-text-field>
                <modal-dialog class="ms-3" icon>
                  <template v-slot:button>
                    <v-icon>mdi-filter-variant</v-icon>
                  </template>
                  <template v-slot:content>
                    <v-row>
                      <v-col v-for="filter in filters" :key="filter">
                        <v-switch
                          :label="filter.label"
                          v-if="filter.type == 'boolean'"
                          v-model="filtering[filter.name]"
                        ></v-switch>
                        <v-select
                          clearable
                          v-else-if="filter.type == 'select'"
                          item-title="title"
                          item-value="value"
                          :items="filterOptions(filter)"
                          :label="filter.label"
                          :multiple="filter.variant == 'multiple'"
                          v-model="filtering[filter.name]"
                        >
                        </v-select>
                      </v-col>
                    </v-row>
                  </template>
                  <template v-slot:actions="{ close }"
                    ><v-btn @click="close">Close</v-btn></template
                  >
                </modal-dialog>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </v-col>
    </v-row>

    <v-row>
      <v-col class="pa-0">
        <v-container>
          <v-table v-if="variant == 'table' || !variant">
            <thead>
              <tr>
                <th
                  @click="
                    () => {
                      if (header.orderable)
                        ordering[header.name] =
                          (ordering[header.name] || -1) * -1;
                    }
                  "
                  v-for="header in cleanHeaders"
                  :key="header"
                  :class="'text-' + (header.align || 'left')"
                >
                  {{ header.label }}
                  <v-icon v-if="header.orderable && interactive">
                    {{
                      ordering[header.name] == undefined
                        ? "mdi-border-none-variant"
                        : ordering[header.name] > 0
                        ? "mdi-chevron-down"
                        : "mdi-chevron-up"
                    }}
                  </v-icon>
                </th>
              </tr>
            </thead>
            <tbody v-if="source.length">
              <tr v-for="(item, i) in source" :key="item.id">
                <slot name="row" :headers="headerMap" :i="i" :row="item">
                </slot>
              </tr>
            </tbody>
            <tbody v-else>
              <tr>
                <td class="text-center" :colspan="cleanHeaders.length">
                  No results found
                </td>
              </tr>
            </tbody>
          </v-table>
          <v-row v-if="variant == 'cards'">
            <v-col class="d-flex justify-center" :cols="xs ? 12 : (sm ? 6 : (md ? 4 : 3))" v-for="(item, i) in source" :key="item.id">
              <slot name="card" :i="i" :item="item"></slot>
            </v-col>
          </v-row>
        </v-container>
      </v-col>
    </v-row>
    <v-row v-if="paginated" class="d-flex justify-end">
      <div>
        <v-pagination
          v-model="page"
          :length="pages"
          :total-visible="7"
        ></v-pagination>
      </div>
    </v-row>
  </v-container>
</template>

<script>
import ModalDialog from "../ModalDialog.vue";
import { useDisplay } from "vuetify";
export default {
  components: { ModalDialog },
  props: {
    source: null,
    propname: null,
    field: null,
    paginated: Boolean,
    listComponent: null,
    interactive: Boolean,
    filters: Array,
    headers: Array,
    exclude: Array,
    variant: String,
  },

  data: function () {
    return {
      search: "",
      page: 1,
      ordering: {},
      filtering: {},
    };
  },
  setup() {
    const { xs, sm, md, lg } = useDisplay();
    return { xs, sm, md, lg }
  },
  created() {
    // initialize filtering and ordering with null values

    this.filtering["query"] = null;

    for (let filter of this.filters || []) {
      if (filter.type == "select" && filter.variant == "multiple") {
        this.filtering[filter.name] = [];
      } else {
        this.filtering[filter.name] = null;
      }
    }
    for (let header of this.headers || []) {
      if (header.orderable) {
        this.ordering[header.name] = null;
      }
    }
  },
  methods: {
    filterOptions({ options, toOption }) {
      if (!options) return;
      if (options?.constructor?.__isPage) {
        let items = [];
        for (let model of options) {
          items.push(toOption(model));
        }
        return items;
      } else {
        return options;
      }
    },
  },
  computed: {
    pages() {
      return Math.ceil(this.source.count / 10) || 0;
    },
    cleanHeaders() {
      let exclude = this.exclude || [];
      return this.headers.filter((header) => exclude.indexOf(header.name) < 0);
    },
    headerMap() {
      let map = {};
      for (let { name } of this.cleanHeaders) {
        map[name] = true;
      }
      return map;
    },
  },
  watch: {
    filtering: {
      handler() {
        const cleanFilters = {};

        for (let [key, value] of Object.entries(this.filtering)) {
          if (value != null) {
            cleanFilters[key] = value;
          }
        }

        this.source.setFilters(cleanFilters);
      },
      deep: true,
    },
    ordering: {
      handler() {
        const cleanOrdering = {};

        for (let [key, value] of Object.entries(this.ordering)) {
          if (value != null) {
            cleanOrdering[key] = value;
          }
        }

        this.source.setFilters(cleanOrdering);
      },
      deep: true,
    },
    page: function (newPage) {
      this.source.setPage(newPage - 1);
    },
  },
};
</script>

<style>
.v-pagination__item > button {
  background: 0;
  width: 30px !important;
  height: 30px !important;
  border-radius: 0;
}
.v-pagination__item--is-active > button {
  background: 0;
  border-bottom: 1px solid #3c8dbc;
  color: #3c8dbc;
  border-radius: 0 !important;
}

.v-pagination__item--is-active button > v-btn__overlay {
  background: 0;
}
</style>