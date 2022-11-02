<template>
  <v-container>
    <v-card>
      <v-card-title class="flex-column text-center">
        <span class="headline"> Map Pick </span>
        <h5>{{ status }}</h5>
      </v-card-title>

      <v-divider></v-divider>
      <v-card-content>
        <div :class="{ overlay: disabled }"></div>

        <v-container>
          <v-row class="my-1 map" v-for="map in mapPickProcess.maps" :key="map">
            <v-col cols="6">
              <div class="d-flex">
                <p
                  :class="{
                    banned: map.isBanned(),
                    picked: map.isPicked(),
                  }"
                  class="text-no-wrap"
                  style="font-size: larger"
                >
                  {{ map.map_name }}
                </p>
                <p class="ms-2" color="gray" v-if="map.isSelected()">
                  ({{ map.selected_by.short_name }})
                </p>
                <p class="ms-2" v-else-if="map.isBanned() || map.isPicked()">
                    (DEFAULT)
                </p>
              </div>
            </v-col>
            <v-col cols="6" v-if="map && !map.isSelected()" class="text-end">
              <v-btn
                @click="selectMap(map)"
                class="ms-4 text-primary"
                v-if="!isEnded"
                :disabled="map.selected_by || !canSelect"
              >
                {{ isPick ? "Pick" : "Ban" }}
              </v-btn>
            </v-col>
          </v-row>
        </v-container>
      </v-card-content>
    </v-card>
  </v-container>
</template>

<script>
export default {
  props: ["mapPickProcess", "disabled"],

  computed: {
    player() {
      return this.$store.state.player;
    },
    isParticipating() {
      if (!this.mapPickProcess?.match) return false;
      return (
        this.player &&
        (this.player.isInTeam(this.mapPickProcess.match.team_one) ||
          this.player.isInTeam(this.mapPickProcess.match.team_two))
      );
    },
    canSelect() {
      return this?.player && this.player?.id == this?.mapPickProcess?.turn?.id;
    },
    isPick() {
      return this.mapPickProcess.next_action == 2;
    },
    isBan() {
      return this.mapPickProcess.next_action == 1;
    },
    isEnded() {
      return this.mapPickProcess.finished;
    },
    status() {
      if (this.disabled) {
        return "Map Pick is disabled";
      }

      if (this.isEnded) return "Map pick ended";
      if (this.isParticipating && !this.canSelect)
        return "Waiting for opponent...";
      if (this.isParticipating && this.canSelect) return "Your turn";
      return "Map pick in progress";
    },
  },
  methods: {
    async selectMap(map) {
      await this.$api.mapPickAction(map);
    },
  },
};
</script>

<style scoped>
.map {
  border: 1px solid #d9d9d9;
}
.banned {
  color: #6a6a6a;
  text-decoration: line-through;
}
.picked {
  color: #06ad06
}
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #bababa99;
  z-index: 1;
}
</style>