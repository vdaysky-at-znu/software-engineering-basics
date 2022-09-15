import Model from './model.js';


export class Game extends Model {

}

export class Team extends Model {

    // players are added later to avoid circular dependency

    static short_name = String;
    static full_name = String;

}

export class Permission extends Model {

    static __modelname = "Permission";

    static name = String;
}

export class Role extends Model {

    static __modelname = "Role";

    static name = String;
    static permissions = [Permission]

}

export class Player extends Model {

    static team = Team;
    static uuid = String;
    static role = Role;

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
                    return present[i] != "*";
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

Team.members = [Player];

export class MapPick extends Model {

    static selected_by = Team;

    get is_selected() {
        return this.selected_by != null;
    }

    get is_banned() {
        return this.is_selected && !this.picked
    }

    get is_picked() {
        return this.is_selected && this.picked
    }
}

export class MapPickProcess extends Model {

    maps = [MapPick];

}

export class Match extends Model {

    static team_one = Team;
    static team_two = Team;
    static map_pick_process = MapPickProcess;
}

export class Event extends Model {

    static matches = [Match];
}

const topLevelModels = [Game, Team, Player, MapPick, MapPickProcess, Match, Event];

window.$registeredModels = {};

for (let model of topLevelModels) {
    model.all = Model.all.bind(model);
    window.$registeredModels[model.name.toLowerCase()] = model;
}
