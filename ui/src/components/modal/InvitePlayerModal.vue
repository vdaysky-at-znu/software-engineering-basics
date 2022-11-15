<template>
    <v-dialog v-model="dialog">
    
        <template v-slot:activator="{ props }">
            <v-btn v-bind="{...props, ...$attrs}" flat> <slot></slot> </v-btn>
        </template>
    
        <v-card style="width: min(90vw, 800px)">
    
            <v-card-title>
                Invite Player
            </v-card-title>
            
            <v-card-content>

                <custom-form 
                v-model="playerForm" 
                :fields="[
                    {
                        name: 'player',
                        label: 'Player Name or UUID',
                        type: 'text',
                        required: true,
                        validators: [
                            async v => filteredPlayerView.length || 'Player not found'
                        ]
                    }
                ]"></custom-form>
                
                <div style="max-height: 500px; overflow-y: scroll">
                    <contextual-list paginated v-if="fftView?.players" :listComponent="PlayerList" :source="fftView.players" propname="players" ></contextual-list>
                </div>
            </v-card-content>
        
            <v-card-actions>
                <v-btn @click="dialog = false"> Cancel </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
import { FftPlayerView } from '@/api/model/models';
import CustomForm from '../common/CustomForm.vue';
// import PlayerWidget from '../widgets/PlayerWidget.vue';
import ContextualList from '../contextual/ContextualList.vue';
import PlayerList from '@/components/lists/PlayerList.vue';
export default {
  components: { CustomForm, ContextualList },

    // prevent inheritance because we want attrs 
    // to only be inherited by button activator
    // and not modal itself
    inheritAttrs: false,    

    setup() {
        return {
            PlayerList
        }
    },

    data: () => ({
        playerForm: {},
        dialog: false,
        fftView: null
    }),

    computed: {
        filteredPlayerView() {
            let players = this.fftView?.players || [];

            return players.filter(player => {
                return ['username', 'uuid'].some(key => {
                    return (!this.playerForm.player && !player[key]) || player[key]?.toLowerCase()?.includes(this.playerForm.player?.toLowerCase() || '');
                });
            });
        },
    },

    watch: {

        dialog(v) {
            if (v) {
                this.loadFFTView();
            }
        },

        fftView: {
            handler: function (newVal) {
                console.log("fftView changed", newVal);

                
            },
            deep: true,
        },
    },

    methods: {

        loadFFTView() {
            this.fftView = new FftPlayerView({team_id: this.$store.state.player.owned_team.id});
        },

        async sendInvite(player) {
            try {
            player.invited = true;
            await this.$api.invitePlayer(player);
            this.$emit('invited', {player}); 
            } catch (e) {
                player.invited = false;
            }
        }
    }
}
</script>

<style>

</style>