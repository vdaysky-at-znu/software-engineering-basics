<template>
  <v-container>
    
    <assert-permission permission="*">
      <v-row class="bg-red"> 
        <v-col cols="10"></v-col>
        <v-col cols="2">
          <ModalDialog title="Create new event" button="Create">
            <template v-slot:content>
                <v-form>
                  <v-text-field label="Event name">
                  </v-text-field>
                </v-form>
            </template>
          </ModalDialog>
        </v-col>
      </v-row>
    </assert-permission>
    
    <v-row>
      <EventsList :events="events"></EventsList>
    </v-row>
  </v-container>
</template>

<script>
import { Event } from "@/api/model/models";
import EventsList from "@/components/lists/EventsList.vue";
import ModalDialog from '@/components/ModalDialog.vue';
import AssertPermission from '@/components/AssertPermission.vue';
export default {
  components: { EventsList, ModalDialog, AssertPermission },
  data() {
    return {
      events: Event.all(),
    };
  },
};
</script>

<style>
</style>