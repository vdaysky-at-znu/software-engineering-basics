<template>
  <div>
    <code class="text-no-wrap">
      {{ value }}
    </code>
    <div class="icon">
        <v-icon @click="copy" :color="color" >{{ icon }}</v-icon>
    </div>
    
  </div>
</template>

<script>
export default {
  props: ["value"],
  data() {
    return {
      icon: "mdi-content-copy",
      color: ''
    };
  },
  methods: {
    copy() {
      navigator.clipboard.writeText(this.value);
      this.icon = "mdi-check";
      this.color = "green";
      setTimeout(() => {
        this.icon = "mdi-content-copy";
        this.color = "";
      }, 1000);
    },
  },
};
</script>

<style scoped>
    code {
        padding: 5px 10px;
        border-radius: 5px 0px 0px 5px;
        background-color: rgb(205, 205, 205);
        color: #be0729;
    }
    div {
        display: inline-flex;
        align-items: center;
        background-color: #eee;
        border-radius: 5px;
    }
    .icon {
        padding: 5px;
        cursor: pointer;

    }
</style>