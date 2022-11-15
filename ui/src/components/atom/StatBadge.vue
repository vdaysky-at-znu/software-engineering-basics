<template>
  <v-sheet class="badge text-center">
    <div class="d-flex flex-column justify-space-between" style="height: 100%">
        <h2><slot name="value"></slot></h2>
        <div style="height: 100%;" class="d-flex justify-center flex-column">
            <h5 class="text-center"><slot name="metric"></slot></h5>
        </div>
    </div>
    
  </v-sheet>
</template>

<script>
export default {
};
</script>

<style scoped>
.badge {
    background: #f4f4f4;
    padding: .5rem .5rem;
    border-radius: 5px;
    width: 100px;
}
h5 {
    font-weight: 400;
}
</style>