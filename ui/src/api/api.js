import { Player } from "./model/models";

const BASSE_URL = "http://127.0.0.1:8000"

class ApiError extends Error {
    constructor(message) {
        super(message)
        this.message = message;
    }
}

class ApiBase {
    async get(url, data) {
        let r = await fetch('/api/' + url + "?" + new URLSearchParams(data), {headers: {session_id: localStorage['session_id']}});
        if (r.headers.session_id)localStorage.session_id = r.headers.session_id;
        
        let content = await r.json();

        if (r.status != 200) {
            throw new ApiError(content.message);
        }

        return content;
    }
    async post(url, data) {
        let r = await fetch('/api/' + url, {method: 'post', body: JSON.stringify(data), headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                session_id: localStorage['session_id']
            }
        });

        if (r.headers.session_id) {
            localStorage.session_id = r.headers.session_id;
        }

        let content = await r.json();

        if (r.status != 200) {
            throw new ApiError(content.message);
        }

        return content;
    }

    async graphql(query) { // model, id, fields, fieldIds
        /** Make a GraphQL query to the API
         * model - string name of model to query
         * id - id of model to query, could be complex ID represented by object, or null
         * fields - array of field names to query
         * fieldIds - array of parameters to query for each field, could be undefined
         */

        //  fieldIds = fieldIds || {};

        // let query;

        // const isView = typeof id === "object";
        
        // // lowercase first letter
        // let normalizedModelName = model[0].toLowerCase() + model.slice(1);
        
        // const argKVPair = (key, value) => {
        //     if (typeof value === "string") {
        //         return `${key}: "${value}"`;
        //     } else if (typeof value === "number") {
        //         return `${key}: ${value}`;
        //     } else if (value === null) {
        //         return `${key}: null`;
        //     }
        //     return `${key}: ${value}`;
        // }

        // let queryFields = fields.map(fieldName => {
        //     let fieldArgs = fieldIds[fieldName];
            
        //     // if given field name has own args, process them. Otherwise, just return the name
        //     if (fieldArgs) {
        //         return Object.keys(fieldArgs).map(fieldArgName => argKVPair(fieldArgName, fieldArgs[fieldArgName])).join(", ");
        //     } else {
        //         return fieldName;
        //     }
        // }).join(" ");

        // if (isView) { // views may have miltiple ids
        //     let queryId = Object.keys(id).map(k => `${k}: ${typeof id[k] === 'string' ? '"' + id[k] + '"' : id[k] }`).join(", ");

        //     query = `query { ${normalizedModelName}(${queryId}) { ${queryFields} } }`;
        //     console.log(query);
        // }
        // else if (id && fields) {
        //     query = `query { ${normalizedModelName}(id: ${id}) { ${queryFields} } }`;
        // } else {
        //     query = `query { ${normalizedModelName} }`; // request to get all entries
        // }
        
        query = `query { ${query} }`;

        console.log(query);

        let response = await fetch(BASSE_URL + '/graphql/', {
            method: 'post', 
            body: JSON.stringify({query: query}), 
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'session_id': localStorage['session_id']
            }
        });

        const {errors, data} = (await response.json());
        if (errors) {
            console.error(errors);
            throw Error("GraphQL Request failed: See above");
        }
        return data[Object.keys(data)[0]];
    }
}


class MsApi extends ApiBase {
    async resolveUUID(uuid) {
        return await this.get(`player/${uuid}/name`);
    }

    async getUUID(name) {
        return await this.post("player/uuid", {name});
    }

    async getNameStatus(name) {
        let response = await this.get("auth/name/status", {name});
        return response.status;
    }

    async getMe() {
        let response = await this.get("auth/me");
        return new Player(response.player_id);
    }

    async logout() {
        return await this.post("auth/logout");
    }

    async login(username, password) {
        let response = await this.post("auth/login", {username, password});
        localStorage.session_id = response.session_key;
        return new Player(response.player_id);
    }

    async register(username, password, verification_code) {
        let response = await this.post("auth/register", {username, password, verification_code});
        localStorage.session_id = response.session_key;
        return new Player(response.player_id);
    }

    async createEvent({name, start_date}) {
        return await this.post("event/create", {name, start_date});
    }

    async createGame({match, map}) {
        return await this.post("game/create", {match, map});
    }

    async createMatch({name, start_date, event, team_a, team_b, map_count}) {
        return await this.post("match/create", {name, start_date, event, team_a, team_b, map_count});
    }

    async mapPickAction(map) {
        return await this.post("match/map-pick", {map: map.id});
    }

    async getFFTPlayers() {
        return await this.get("player/fft");
    }

    async invitePlayer(player) {
        return await this.post("player/invite", {player_id: player.id});
    }

    async acceptInvite(invite) {
        return await this.post("player/invite/" + invite + "/accept")
    }

    async declineInvite(invite) {
        return await this.post("player/invite/" + invite + "/decline")
    }

    async isTeamNameAvailable(name) {
        return (await this.get("roster/name/" + name + "/status")).available
    }

    async createTeam({name, short_name, location}) {
        return await this.post("roster/create", {name, short_name, location});
    }

    async findPlayer(query) {
        let response = await this.get("player/find/" + query)
        let playerId = response.player_id;
        if (!playerId) {
            return null;
        }
        return new Player(playerId);
    }

    async joinQueue(queue) {
        let response = await this.post("queue/join", {queue: queue.id});
        return response == true;
    }

    async leaveQueue(queue) {
        let response = await this.post("queue/leave", {queue: queue.id});
        return response == true;
    }

    async confirmRankedMatch(queue) {
        let response = await this.post("queue/confirm", {queue: queue.id});
        return response == true;
    }

    async pickPlayer(queue, player) {
        return await this.post("queue/pick", {player: player.id, queue: queue.id});
    }

    async joinGame(game) {
        return await this.post("game/join", {game: game.id});
    }

}

const API = new MsApi();

window.$api = API;
export default API;