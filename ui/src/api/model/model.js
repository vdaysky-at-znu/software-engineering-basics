export class ModelManager {

    constructor() {
        this.models = {};
    }

    makeReactive(model, id) {
        console.log("make model reactive: ",model);

        let modelName = model.constructor.__modelname || model.constructor.name;
        /** Make object reactive by adding it to vuex */
        let models_of_type = this.models[modelName] || {};
        models_of_type[id] = model;
        this.models[modelName] = models_of_type;
        let reactive = window.$models.models[modelName][id];
        return reactive;
    }
    
    makeObejctReactive(name, object, id) {
        console.log("make object reactive: ", object);
        /** Make object reactive by adding it to vuex */
        let models_of_type = this.models[name] || {};
        models_of_type[id] = object;
        this.models[name] = models_of_type;
        let reactive = window.$models.models[name][id];
        return reactive;
    }

    get(type /** Class */, id /** Int */) {
        /** Get model by type and id */
        let modelName;

        if (type instanceof Function) {
            modelName = type.name;
        } else {
            modelName = type;
        }

        let models_of_type = this.models[modelName] || {};

        let model = models_of_type[id];
        
        console.log("get type", modelName, "with id", id);
        if (!model && modelName == 'all') {
            console.log("its all, set to empty list");
            models_of_type[id] = []
        }

        this.models[modelName] = models_of_type;
        console.log("return all", models_of_type[id]);
        return models_of_type[id];
    }
}

const fieldNameMap = (field) => {
    let mapping = {
        members: "member_ids",
        permissions: "permission_ids",
        players: "player_ids",
        matches: "match_ids",
        maps: "map_ids",
    }

    if (mapping[field]) {
        return mapping[field];
    }
    return field;
}

export default function Model(id) {

    if (!id) {
        throw new Error("Model id is required");
    }

    const isView = typeof id === "object";
    
    // views are unique and independant.
    if (!isView) {
        let existingModel = window.$models.get(this.constructor, id);

        if (existingModel) {
            return existingModel;
        }
    
        if (!window.$models) {
            throw new Error("Model objects can't be constructed inside store module");
        }
    }

    if (isView) {
        this.obejctId = id;
    } else {
        this.id = id;
    }

    if (isView) {
        window.$socket.onEvent("ModelUpdateEvent", (data) => {
            let modelName = data.payload.model_name;
            let modelId = data.payload.model_pk;
            
            for (let idPiece of Object.keys(this.constructor.__virtualId || {})) {

                if (idPiece != modelName + "_id") { 
                    continue;
                }

                if (this.obejctId[idPiece] == modelId) {
                    this.load();
                    return;
                }
            }
        });
    }
    
    let reactive;

    if (isView) {
        // since views are unique, ids are generated randomly
        reactive = window.$models.makeReactive(this, Math.random());
    } else {
        reactive = window.$models.makeReactive(this, id);
    }

    this.load = async () => {


        let fieldData = this.constructor.getGraphqlFields(isView);

        // init empty arrays
        for (let fieldName of Object.keys(fieldData)) {
            let field = fieldData[fieldName];
            if (field.type === "array" && field.isModel) {
                if (!reactive[fieldName]) reactive[fieldName] = []
            }
        }

        let fieldNames = Object.keys(fieldData).map(x => fieldData[x].graphqlField);
        
        let modelName = this.constructor.__modelname || this.constructor.name;

        let data = await window.$api.graphql(modelName, this.obejctId || this.id, fieldNames);

        for (let fieldName of Object.keys(fieldData)) {
            let field = fieldData[fieldName];
            let value = data[field.graphqlFieldName];

            if (field.type === "model") {

                if (!value) {
                    reactive[fieldName] = null;
                    continue;
                }

                reactive[fieldName] = new field.class(value);
            }

            else if (field.type === "array" && field.isModel) {
                while (reactive[fieldName].length)reactive[fieldName].pop();
                reactive[fieldName].push(...value.map(x => new field.class(x)));
            }

            else {
                reactive[fieldName] = value;
            }
        }
    }
    
    this.load();

    return reactive;
    
}

Model.getGraphqlFields = function(isView) {

    if (this.fields) {
        return this.fields;
    }

    let fields = [];
    
    for (let fieldName of Object.keys(this)) {
        
        
        if (fieldName.startsWith("__")) {
            continue;
        }

        let field = this[fieldName];

        if (
            field instanceof Function && 
            !(field.prototype instanceof Model) &&
            !(Array.isArray(field)) &&
            !(field == String) && 
            !(field == Number) &&
            !(field == Boolean)
        ) {
            continue;
        }


        if (field.prototype instanceof Model) {
            fields[fieldName] = {
                type: "model",
                class: field,
                graphqlField: fieldName + "_id",
                graphqlFieldName: fieldName + "_id",
            }
        }
        else if (Array.isArray(field)) {
            fields[fieldName] = {
                type: "array",
                class: field[0],
                isModel: field[0].prototype instanceof Model,
                // views have object ids
                graphqlField: isView ? fieldNameMap(fieldName) + "{" + field[0].getObejctIdSchema() + "}" : fieldNameMap(fieldName),
                graphqlFieldName: fieldNameMap(fieldName)
            }
        }
        else {
            fields[fieldName] = {
                type: "primitive",
                graphqlField: fieldName,
                graphqlFieldName: fieldName
            }
        }
    }
    this.fields = fields;
    return fields;
}

Model.getObejctIdSchema = function() {
    let result = "";
    console.log("get object id schema", this.__virtualId, Object.keys(this.__virtualId));
    for (let fieldName of Object.keys(this.__virtualId)) {
        result += fieldName + " ";
    }
    console.log(result);
    return result;
}

Model.all = function () {

    const getAll = async (model, name) => {
        let data = await window.$api.graphql(name);
        return data.map((item) => new model(item));
    }

    if (this.__all) {
        return this.__all;
    }

    let modelName = this.__modelname || this.name;
    this.__all = window.$models.makeObejctReactive("all", [], modelName.toLowerCase());

    getAll(this, modelName.toLowerCase() + "_ids").then(
        x => this.__all.push(...x)
    );

    return this.__all;
}