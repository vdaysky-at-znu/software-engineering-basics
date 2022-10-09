import Model, { Page } from './model.js';
// import VirtualModel from './virtual.js';


export class Game extends Model {
    static map = String;
    static is_started = Boolean;
    static is_finished = Boolean;
    static score_a = Number;
    static score_b = Number;
    static team_a = 'InGameTeam';
    static team_b = 'InGameTeam';
    static match = 'Match';
}

export class Team extends Model {

    static short_name = String;
    static full_name = String;
    static elo = Number;
    static members = Page('Player');

}

export class Permission extends Model {

    static __modelname = "PlayerPermission";

    static name = String;
}

export class Role extends Model {

    static __modelname = "Role";

    static name = String;
    static permissions = Page(Permission)

}

export class Player extends Model {

    static team = Team;
    static uuid = String;
    static role = Role;
    static owned_team = Team;
    static username = String;
    static elo = Number;

    isAuthenticated() {
        return this.uuid != null;
    }

    isInTeam(team) {
        if (this.team == null) return false;
        if (team) {
            return this.team.id == team.id;
        }
        return true;
    }

    hasPermission(permission) {

        const testPerm = (a, b) => {

            if  (!b) return false;

            let present = b.split(".");
            let required = a.split(".");
            
            // if the present permission is more specific than the required one, it is not a match
            if (required.length < present.length) {
                return false;
            }

            // iterate over both at the same time
            for (let i = 0; i < Math.max(present.length, required.length); i++) {
                
                // present permission ended earlier, and it did not have a wildcard
                if (present.length == i + 2) {
                    return false;
                }
                

                if (present[i] != required[i]) {
                    return present[i] == "*";
                }
            }
            return true;
        }
        
        if (!this.role) return false;

        for (let perm of this.role.permissions) {
            if (testPerm(permission, perm.name)) return true;
        }

        return false;
    }
}  

export class MapPick extends Model {

    static selected_by = Team;
    static map_name = String;
    static picked = Boolean;


    isSelected() {
        return this.selected_by != null;
    }

    isBanned() {
       return this.isSelected() && !this.picked
    }

    isPicked() {
        return this.isSelected() && this.picked
    }
}

export class MapPickProcess extends Model {

    static maps = Page(MapPick);
    static turn = Team;
    // 1 = ban, 2 = pick, 3 = default, 0 = null
    static next_action = String;
    static finished = Boolean;
    static match = 'Match';

}

export class Match extends Model {

    static __modelname = "Match";

    static name = String;
    static team_one = Team;
    static team_two = Team;
    static map_pick_process = MapPickProcess;
    static games = Page(Game);
}

export class Event extends Model {

    static __modelname = "Event";

    static matches = Page(Match);
    static name = String;
    static start_date = String;
}

export class InGameTeam extends Model {
    static __modelname = "InGameTeam";
    static name = String;
    static players = Page(Player);
    static is_ct = Boolean;
    static starts_as_ct = Boolean;
}

export class Round extends Model {
    static game = Game;
    static number = Number;
    static winner = InGameTeam;
}

export class GamePlayerEvent extends Model {
    static event = String;
    static game = Game;
    static player = Player;
    static round = Round;
    static is_ct = Boolean;
}

const topLevelModels = [Game, Team, Player, MapPick, MapPickProcess, Match, Event, GamePlayerEvent, InGameTeam];

window.$registeredModels = {};

for (let model of topLevelModels) {
    model.all = Model.all.bind(model);
    let modelName = model.__modelname || model.name;
    window.$registeredModels[modelName.toLowerCase()] = model;
}

export class AnonymousPlayer {
    hasPermission() {
        return false;
    }
    isAuthenticated() {
        return false;
    }

    team = null;
    owned_team = null;

    isInTeam() {
        return false;
    }
}

export class FftPlayer extends Model {
    static __virtualId = {
        player_id: Number, 
        team_id: Number
    };

    static uuid = String;
    static username = String;
    static invited = Boolean;
    static id = Number;
}

export class FftPlayerView extends Model {
    static players = Page(FftPlayer);
}

export class TopPlayersView extends Model {
    static __virtualId = {
        criteria: String
    }

    static players = Page(Player);
}

export class PlayerPerformanceAggregatedView extends Model {
    static __virtualId = {
        player_id: Number,
        game_id: Number,
    }

    static kills = Number;
    static deaths = Number;
    static assists = Number;
    static hs = Number;
    static player = Player;
}

export class GameStatsView extends Model {

    static stats = Page(PlayerPerformanceAggregatedView);
}
