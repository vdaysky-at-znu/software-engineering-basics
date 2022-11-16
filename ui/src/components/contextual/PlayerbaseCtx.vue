<template>
  <contextual-list
    field="players"
    :listComponent="PlayerList"
    :source="players"
    :filters="[
    ]"
  >
    <template v-slot:createForm>
      <slot name="createForm"> </slot>
    </template>
  </contextual-list>
</template>

<script>
import ContextualList from "./ContextualList.vue";
import PlayerList from "@/components/lists/PlayerList.vue";

export default {
  setup() {
    return {
      PlayerList,
    };
  },
  components: { ContextualList },
  props: ["players"],
};
</script>

<style>
</style>