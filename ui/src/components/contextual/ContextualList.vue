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
                  v-model="search"
                  label="Search..."
                  hide-details="hide"
                >
                  <template v-slot:appendInner="{}">
                    <v-icon>mdi-magnify</v-icon>
                  </template>
                </v-text-field>

                <v-btn class="ms-3" icon>
                  <v-icon>mdi-filter-variant</v-icon>
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </v-col>
    </v-row>

    <v-row>
      <v-col class="pa-0">
        <component :is="listComponent" v-bind="dynamicProps"></component>
      </v-col>
    </v-row>
    <v-row v-if="paginated" class="d-flex justify-end">
        <div >
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
import AssertPermission from "../AssertPermission.vue";
export default {
  components: { AssertPermission },
  props: {
    source: null,
    propname: null,
    field: null,
    paginated: Boolean,
    listComponent: null,
    interactive: Boolean,
  },

  data: function () {
    return {
      search: "",
      page: 1,
    };
  },
  computed: {
    dynamicProps() {
      if (!this.source) {
        return {};
      }
      return {
        [this.propname]: this.source, // returns data from view / list
        ...this.$attrs,
      };
    },
    pages() {
        return Math.ceil(this.source.count / 10) || 0;
    }
  },
  watch: {
    page: function (newPage) {
      console.log("set page on", this.source);
        this.source.setPage(newPage - 1);
    },
  }
};
</script>

<style>
.v-pagination__item > button {
    background: 0;
    width: 30px!important;
    height: 30px!important;
    border-radius: 0;
}
.v-pagination__item--is-active > button{
    background: 0;
    border-bottom: 1px solid #3c8dbc;
    color: #3c8dbc;
    border-radius: 0!important;
}

.v-pagination__item--is-active button > v-btn__overlay {
    background: 0;
}
</style>