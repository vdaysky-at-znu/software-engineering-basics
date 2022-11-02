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
                    <v-table theme="light">
                        <thead>
                        <tr>
                            <th class="text-left">
                                FFT Players
                            </th>
                            <th class="text-left">
                            
                            </th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr
                            v-for="player in filteredPlayerView" 
                            :key="player"
                        >
                            <td><player-widget :player="player"></player-widget></td>
                            <td> 
                                <v-btn :disabled="player.invited" @click="sendInvite(player)">
                                    {{ player.invited ? 'Invited' : 'Invite' }}
                                </v-btn>
                            </td>
                        </tr>
                        </tbody>
                    </v-table>
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
import PlayerWidget from '../widgets/PlayerWidget.vue';
export default {
  components: { CustomForm, PlayerWidget },

    // prevent inheritance because we want attrs 
    // to only be inherited by button activator
    // and not modal itself
    inheritAttrs: false,    

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
                console.log("fftView changed",newVal,  newVal.players);

                this.playerData = {};
                for (let player of newVal.players) {
                    this.playerData[player.id] = {
                        invited: false,
                    };
                }
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