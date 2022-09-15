
export const EventType = {
    UPDATE: 'update',
    DELETE: 'delete',
    INITIALIZE: 'initialize',
    CREATE: 'create',
}

export const SyncType = {
    SYNC_LIST: 1, // sync all items of model (objects.all())
    SYNC_ITEM: 2, // sync concrete item with id
    SYNC_REVERSE: 3 // sync reverse relation on parent model
}

export const PacketType = {
    PING: 19,

    SUBSCRIBE_GROUP: 'subscribe',
    SUBBED_EVENT: 'subbed-event',
    UNSUBSCRIBE_GROUP: 'unsubscribe',

    DB_REL_UPDATE: 'DB_REL_UPDATE',

}

export const NameStatus = {
    NAME_INVALID: 1,
    NAME_TAKEN: 2,
    NAME_AVAILABLE: 3,
}

export class SocketConnection {

    constructor() {
        this.handlersByEvtType = {};
        this.connected = false;
        this.queue = [];
        this.try_connect();
    }

    onEvent(event, handler) {
        this.handlersByEvtType[event] = this.handlersByEvtType[event] || [];
        this.handlersByEvtType[event].push(handler);
    }

    send(packetType, data) {
        let packet = {
            type: packetType,
            payload: data,
            session_id: localStorage.sesion_id || 'noSessionId'
        }

        if (!this.connected) {
            this.queue.push(packet);
            return;
        }
        this.sock.send(JSON.stringify(packet));
    }

    try_connect() {
        this.sock = new WebSocket("ws://127.0.0.1:8000/ws/connect");
        
        let _this = this;

        this.sock.onopen = () => {
            console.log("Socket opened");
            _this.sock_delay = 1;
            _this.connected = true;
            _this.queue.forEach(packet => {
                _this.sock.send(JSON.stringify(packet));
            });
            _this.queue = [];
        }

        this.sock.onclose = () => {
            console.log(`socket closed, trying to reconnect after ${this.sock_delay} seconds`);
            _this.sock = null;

            setTimeout(
                ()=>_this.try_connect(),
                _this.sock_delay * 1000
            );

            _this.sock_delay = Math.min(this.sock_delay + 5, 30);
        }

        this.sock.onmessage = (e) => {
            let data = JSON.parse(e.data);
            let received_message = new WsEvent(data);
            console.log("received message", received_message);
            for (let handler of this.handlersByEvtType[received_message.type] || []) {
                handler(received_message);
            }
        }
    }

    async unsubscribe(subscription_id) {
        /** TODO */
        return subscription_id;
    }
}

/** Go through payload and identify all model objects in it */
class WsEvent {
    constructor({type, payload, message, status, session_key}) {
     
        if (session_key) {
            localStorage.sesion_id = session_key;
        }

        this.type = type;
        this.message = message;
        this.status = status;
        this.payload = payload;
        
        this.success = status == 200;
        this.not_found = status == 404;
        this.forbidden = status == 400;
        this.error = status == 500;

        if (!this.success) {
            console.error(this.message);
        }
    }
}