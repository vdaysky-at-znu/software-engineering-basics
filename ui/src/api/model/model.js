export class ModelManager {

    constructor() {
        this.models = {};
    }

    makeReactive(model, id) {
        console.log("make model reactive: ", model);
        /** Make object reactive by adding it to vuex */
        let models_of_type = this.models[model.constructor.name] || {};
        models_of_type[id] = model;
        this.models[model.constructor.name] = models_of_type;
        let reactive = window.$models.models[model.constructor.name][id];
        return reactive;
    }
    
    makeObejctReactive(name, object, id) {
        console.log("make model reactive: ", object);
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
        return models_of_type[id];
    }
}


export default function Model(id) {


    let existingModel = window.$models.get(this.constructor, id);

    if (existingModel) {
        return existingModel;
    }

    if (!window.$models) {
        throw new Error("Model objects can't be constructed inside store module");
    }

    this.id = id;

    let reactive = window.$models.makeReactive(this, id);


    const fieldNameMap = (field) => {
        let mapping = {
            members: "member_ids",
            permissions: "permission_ids",
        }

        if (mapping[field]) {
            return mapping[field];
        }
        return field;
    }

    this.getGraphqlFields = function() {
        

        if (this.constructor.fields) {
            return this.constructor.fields;
        }

        let fields = [];
        
        for (let fieldName of Object.keys(this.constructor)) {
            
            
            if (fieldName.startsWith("__")) {
                continue;
            }

            let field = this.constructor[fieldName];

            if (
                field instanceof Function && 
                !(field.prototype instanceof Model) &&
                !(Array.isArray(field)) &&
                !(field == String) && 
                !(field == Number)
            ) {
                continue;
            }


            if (field.prototype instanceof Model) {
                fields[fieldName] = {
                    type: "model",
                    class: field,
                    graphqlField: fieldName + "_id",
                }
            }
            else if (Array.isArray(field)) {
                fields[fieldName] = {
                    type: "array",
                    class: field[0],
                    isModel: field[0].prototype instanceof Model,
                    graphqlField: fieldNameMap(fieldName),
                }
            }
            else {
                fields[fieldName] = {
                    type: "primitive",
                    graphqlField: fieldName,
                }
            }
        }
        this.constructor.fields = fields;
        return fields;
    }

    this.load = async () => {


        let fieldData = this.getGraphqlFields();

        // init empty arrays
        for (let fieldName of Object.keys(fieldData)) {
            let field = fieldData[fieldName];
            if (field.type === "array" && field.isModel) {
                if (!reactive[fieldName]) reactive[fieldName] = []
            }
        }

        let fieldNames = Object.keys(fieldData).map(x => fieldData[x].graphqlField);
        
        let modelName = this.constructor.__modelname || this.constructor.name;

        let data = await window.$api.graphql(modelName, this.id, fieldNames);

        for (let fieldName of Object.keys(fieldData)) {
            let field = fieldData[fieldName];
            let value = data[field.graphqlField];

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

Model.all = function () {

    const getAll = async (model, name) => {
        let data = await window.$api.graphql(name);
        return data.map((item) => new model(item));
    }

    if (this.__all) {
        return this.__all;
    }

    this.__all = window.$models.makeObejctReactive("all", [], this.name.toLowerCase());

    getAll(this, this.name.toLowerCase() + "_ids").then(
        x => this.__all.push(...x)
    );

    return this.__all;
}