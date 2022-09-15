<template>
  <v-dialog v-model="dialog">
    <template v-slot:activator="{ props }">
      <v-btn v-bind="props" flat>Log in/Register</v-btn>
    </template>

    <v-card style="width: min(90vw, 800px)">
      <v-card-title>
        {{ mode }}
      </v-card-title>

      <v-card-text>
        <v-text-field
          v-model="username"
          :error-messages="nameError"
          hint="Your minecraft name"
          label="IGN"
        ></v-text-field>
        <v-text-field
          v-model="password"
          label="password"
          type="password"
        ></v-text-field>

        <div v-if="mode == 'Register'">
          <p>
            Join betterMS server and type in <code>/code</code> to receive a
            verification code.
          </p>
          <v-text-field
            v-model="verificationCode"
            label="verification code"
          ></v-text-field>
        </div>

        <v-btn color="primary" block @click="toggleMode">
          {{ modeText }}
        </v-btn>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-btn color="error" @click="dialog = false">Cancel</v-btn>
        <v-btn color="success" @click="submit">submit</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { NameStatus } from "@/api/utils";
import API from "../api/api";

export default {
  data: () => ({
    dialog: false,
    mode: "Register",
    username: "",
    password: "",
    verificationCode: "",
    nameError: [],
  }),
  methods: {
    toggleMode() {
      if (this.mode == "Register") {
        this.mode = "Log In";
      } else {
        this.mode = "Register";
      }
    },

    async validateName() {
      let nameStatus = await API.getNameStatus(this.username);
      if (nameStatus == NameStatus.NAME_INVALID) {
        this.nameError = ["Name invalid"];
        return false;
      }

      if (nameStatus == NameStatus.NAME_TAKEN) {
        this.nameError = ["Name is already taken"];
        return false;
      }
      return true;
    },

    async submit() {
      if (this.mode == "Register") {
        let nameValid = await this.validateName();
        if (!nameValid) {
          return;
        }
        try {
          let player = await API.register(
            this.username,
            this.password,
            this.verificationCode
          );
          this.$store.commit("setPlayer", player);
          this.dialog = false;
        } catch (e) {
          console.error(e);
        }
      } else {
        let player = await API.login(this.username, this.password);
        this.$store.commit("setPlayer", player);
        this.dialog = false;
      }
    },
  },

  computed: {
    modeText() {
      if (this.mode == "Register") {
        return "Already have an account?";
      }
      return "Don't have an account yet?";
    },
  },
};
</script>

<style>
</style>