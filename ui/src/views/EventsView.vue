<template>
  <v-container>
    <v-row>
      <v-col class="">
        <h1>Events</h1><code>{{events.count}} event found</code>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="pa-0">
        <contextual-list :source="events" :listComponent="EventsList" propname="events" interactive paginated>
            <template v-slot:createForm>
                <assert-permission permission="*">
                <ModalDialog
                  title="Create new event"
                  button="Create"
                  ref="evtModal"
                  @submit="createEvent"
                  :style="{
                    background: $vuetify.theme.themes.light.colors.primary,
                    color: $vuetify.theme.themes.light.colors['on-primary'],
                  }"
                >
                  <template v-slot:content>
                    <custom-form
                      ref="evtForm"
                      v-model="createEventForm"
                      :fields="[
                        {
                          name: 'name',
                          label: 'Event Name',
                          type: 'text',
                          required: true,
                          validators: [
                            (v) => v.length > 5 || 'Event name is too short',
                            (v) => v.length <= 32 || 'Event name is too long',
                          ],
                        },
                        {
                          name: 'date',
                          label: 'Event Date',
                          type: 'date',
                          required: true,
                          validators: [
                            (v) =>
                              v > new Date() ||
                              'Event date must be in the future',
                          ],
                        },
                      ]"
                    >
                    </custom-form>
                  </template>
                </ModalDialog>
              </assert-permission>
            </template>
        </contextual-list>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { Event } from "@/api/model/models";
import EventsList from "@/components/lists/EventsList.vue";
import ModalDialog from "@/components/ModalDialog.vue";
import AssertPermission from "@/components/AssertPermission.vue";
import CustomForm from "@/components/common/CustomForm.vue";
import ContextualList from "@/components/contextual/ContextualList.vue";
export default {
  components: {
    ModalDialog,
    AssertPermission,
    CustomForm,
    ContextualList,
  },
  setup() {
    return {
      EventsList,
    };
  },
  data() {
    return {
      events: Event.all(),
      createEventForm: {},
      search: "",
    };
  },

  watch: {
    search: function () {
      // this.events.applyFilter("search", val);
    },
  },

  created() {
    console.log("all events", this.events.constructor.name);
  },

  methods: {
    async createEvent() {
      await this.$api.createEvent({
        name: this.createEventForm.name,
        start_date: this.createEventForm.date,
      });

      this.$refs.evtForm.reset();
      this.$refs.evtModal.close();
    },
  },
};
</script>

<style>
</style>