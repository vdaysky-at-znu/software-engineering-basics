<template>
  <v-container>
    <v-row>
      <v-col class="pa-0">
        <v-container>
          <v-row>
            <v-col class="d-flex align-end">
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
        <EventsList :events="filteredEvents"></EventsList>
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
export default {
  components: { EventsList, ModalDialog, AssertPermission, CustomForm },
  data() {
    return {
      events: Event.all(),
      createEventForm: {},
      search: "",
    };
  },

  computed: {
    filteredEvents() {
      // todo: actual advanced search making use of data views
      return this.events.filter((evt) => {
        return evt?.name
          ?.toLowerCase?.()
          ?.includes?.(this.search.toLowerCase());
      });
    },
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