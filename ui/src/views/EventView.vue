<template>
  <v-container>
    <v-row>
      <v-col class="">
        <h1>Matches</h1>
        <code>{{ event?.matches?.count }} matches found</code>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <match-list :matches="event.matches" interactive paginated>
          <template v-slot:createForm>
            <assert-permission permission="match.create">
              <modal-dialog @submit="createMatch" button="Create">
                <template v-slot:content>
                  <custom-form
                    ref="matchForm"
                    v-model="createMatchForm"
                    :fields="[
                      {
                        name: 'name',
                        label: 'Match Name',
                        type: 'text',
                        required: true,
                        validators: [
                          (v) => v.length > 5 || 'Match name is too short',
                          (v) => v.length <= 32 || 'Match name is too long',
                        ],
                      },
                      {
                        name: 'team_a',
                        label: 'Team A',
                        type: 'select',
                        required: true,
                        options: teamOptions,
                        validators: [(v) => v != null || 'Team A is required'],
                      },
                      {
                        name: 'team_b',
                        label: 'Team B',
                        type: 'select',
                        required: true,
                        options: teamOptions,
                        validators: [(v) => v != null || 'Team B is required'],
                      },
                      {
                        name: 'start_date',
                        label: 'Start Date',
                        type: 'date',
                        required: true,
                      },
                      {
                        name: 'map_count',
                        label: 'Map Count',
                        type: 'select',
                        required: true,
                        options: [
                          { value: 1, title: '1' },
                          { value: 3, title: '3' },
                          { value: 5, title: '5' },
                        ],
                      },
                    ]"
                  >
                  </custom-form>
                </template>
              </modal-dialog>
            </assert-permission>
          </template>
        </match-list>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { Event, Team } from "@/api/model/models";
import AssertPermission from "@/components/AssertPermission.vue";
import CustomForm from "@/components/common/CustomForm.vue";
import ModalDialog from "@/components/ModalDialog.vue";
import MatchList from "@/components/lists/MatchList.vue";
export default {
  components: {
    AssertPermission,
    CustomForm,
    ModalDialog,
    MatchList,
  },
  data() {
    return {
      event: new Event(this.$route.params.event),
      createMatchForm: {},
      teams: Team.all(),
    };
  },
  setup() {
    return {
      MatchList,
    };
  },
  methods: {
    async createMatch() {
      let valid = this.$refs.matchForm.validateAll();

      if (!valid) return;

      await this.$api.createMatch({
        name: this.createMatchForm.name,
        team_a: this.createMatchForm.team_a,
        team_b: this.createMatchForm.team_b,
        start_date: this.createMatchForm.start_date,
        map_count: this.createMatchForm.map_count,
        event: this.event.id,
      });
      this.$refs.matchForm.reset();
    },
  },
  computed: {
    teamOptions() {
      return this.teams.map((team) => {
        return {
          value: team.id,
          title: team.short_name,
        };
      });
    },
  },
};
</script>

<style>
</style>