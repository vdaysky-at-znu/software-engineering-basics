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

    async graphql(model, id, fields) {
        let query;

        const isView = typeof id === "object";
        
        // lowercase first letter
        let normalizedModelName = model[0].toLowerCase() + model.slice(1);
        
        if (isView) { // views may have miltiple ids
            let queryId = Object.keys(id).map(k => `${k}: ${typeof id[k] === 'string' ? '"' + id[k] + '"' : id[k] }`).join(", ");

            query = `query {
                ${normalizedModelName}(${queryId}) {
                    ${fields.join(" ")}
                }
            }`;
            console.log(query);
        }
        else if (id && fields) {
            query = `query { ${normalizedModelName}(id: ${id}) { ${fields.join(", ")} } }`;
        } else {
            query = `query { ${normalizedModelName} }`; // request to get all entries
        }

        let response = await fetch(BASSE_URL + '/graphql/', {
            method: 'post', 
            body: JSON.stringify({query: query}), 
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        });

        return (await response.json()).data[normalizedModelName];
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

    async mapPickAction({is_picked, map}) {
        return await this.post("match/map-pick", {is_picked, map});
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

}

const API = new MsApi();

window.$api = API;
export default API;