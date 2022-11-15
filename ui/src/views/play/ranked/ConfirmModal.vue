<template>
    <v-dialog persistent v-model="show_" max-width="500px">
        <v-card>
        <v-card-title class="headline">Confirm</v-card-title>
        <v-card-text>
            <p>Queue is full, confirm to start the game</p>
            <p>{{ confirmedCount }} / 10 Confirmations</p>
            <p>{{ secondsLeft }}</p>
        </v-card-text>
        <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn v-if="!confirmedByMe" color="blue darken-1" text @click="confirm">Confirm</v-btn>
            <p v-else>
                Confirmed
            </p>
        </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
export default {
    props: ['confirmedCount', 'confirmedByMe'],
    data() {
        return {
            show_: false,
            timerId: null,
            secondsLeft: 30,
        }
    },
    methods: {
        confirm() {
            this.$emit("confirmed");
        },
        show() {
            if (this.show_) return;
            this.show_ = true;
            this.secondsLeft = 30;

            const this_ = this;
            this.timerId = setInterval(() => {
                this_.secondsLeft--;
            }, 1000);
        },
        hide() {
            if (!this.show_) return;
            this.show_ = false;
            if (this.timerId) {
                clearInterval(this.timerId);
            }
        }
    },
};
</script>

<style>

</style>