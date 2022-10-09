class FieldType { 
    constructor(type, isArray, config) {
        this.config = config || {};
        this.type = type;
        this.isArray = isArray || false;
    }

    isModel() {
        return this.type.prototype instanceof GraphQlQuery;
    }

    hasComplexId() {
        return !!this.type.__virtualId;
    }

    toGraphQl(fieldName) {
        console.log("toGraphQl", fieldName);

        if (this.isModel()) {
            if (this.hasComplexId()) {
                return fieldNameMap(fieldName) + "{" + this.type.getobjectIdSchema() + "}"
            }
            else {
                if (this.type.__isExplicit) {
                    console.log("explicit type " + this.type.getModelName(), " to graphql " + this.type.toGraphQl());
                    return fieldNameMap(fieldName) + this.type.toGraphQl();
                }
                
                if (this.config.explicit) {
                    return fieldName;
                }

                return fieldName + "_id"
            }
        } else {
            return fieldNameMap(fieldName);
        }
    }
}

const newModelInstance = (type, value) => {
    let model;
    if (type.__isExplicit) {
        model = new type();
        model.loadFromData(value);
    } else {
        model = new type(value);
    }
    return model;
}

export class ModelManager {

    constructor() {
        this.models = {};
    }

    makeReactive(model, id) {
        console.log("make model reactive: ",model);

        let modelName = model.constructor.__modelname || model.constructor.name;
        modelName = modelName.toLowerCase();

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

        if (typeof modelName != 'string') {
            throw new Error("ModelManager.get: modelName is not a string");
        }
        modelName = modelName.toLowerCase();

        let models_of_type = this.models[modelName] || {};

        let model = models_of_type[id];
        
        if (!model && modelName == 'all') {
            models_of_type[id] = []
        }

        this.models[modelName] = models_of_type;
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
        games: "game_ids",
    }

    if (mapping[field]) {
        return mapping[field];
    }
    return field;
}

export default function GraphQlQuery(id, fieldIds, config) {

    config = config || {};
    const { defer } = config;

    if (typeof id == 'string' && !isNaN(id)) {
        id = Number(id);
    }

    if (!id) {
        throw new Error("Model id is required");
    }

    const isView = typeof id === "object";
    const modelName = this.constructor.__modelname || this.constructor.name;

    // views are unique and independant.
    if (!isView) {
        

        let existingModel = window.$models.get(modelName, id);

        if (existingModel) {
            return existingModel;
        }
    
        if (!window.$models) {
            throw new Error("Model objects can't be constructed inside store module");
        }
    }

    if (isView) {
        this.objectId = id;
    } else {
        this.id = id;
    }

    // ids for computed fields
    // example: {
    //    team {
    //      id
    //      player_ids(active: true)
    //    }
    // }
    this.fieldIds = fieldIds;

    if (isView) {
        window.$socket.onEvent("ModelUpdateEvent", (data) => {
            let modelName = data.payload.model_name;
            let modelId = data.payload.model_pk;
            
            for (let idPiece of Object.keys(this.constructor.__virtualId || {})) {

                if (idPiece != modelName + "_id") { 
                    continue;
                }

                if (this.objectId[idPiece] == modelId) {
                    this.load();
                    return;
                }
            }
        });
    }
    
    let reactive;

    if (isView) {
        // since views are unique, ids are generated randomly
        reactive = window.$models.makeReactive(this, (this.objectId.model || "") + "-" + ("" + Math.random()).slice(2));
    } else {
        reactive = window.$models.makeReactive(this, id);
    }

    this.getModelName = function() {
        return this.constructor.__modelname || this.constructor.name
    }

    this.loadFromData = (data) => {
        let fieldData = this.constructor.getGraphqlFields(isView);
        console.log("load ", this.getModelName(), "from data", data, "fields", fieldData);
        for (let fieldName of Object.keys(fieldData)) {

            let field = fieldData[fieldName];
            console.log(field);
            if (!field.isArray && field.isModel()) {
                let value;
                if (field.type.__isExplicit) {
                    value = data[fieldNameMap(fieldName)];
                } else {
                    value = data[fieldNameMap(fieldName) + "_id"];
                }
                
                console.log("field is not array but is model", fieldName, value);

                if (!value) {
                    reactive[fieldName] = null;
                    continue;
                }

                reactive[fieldName] = newModelInstance(field.type, value);
            }
            
            // only paginated model will be loading lists
            else if (field.isArray && field.isModel()) {
                let value = data[fieldNameMap(fieldName)];

                // skip any array fields that are not part of page model 
                if (!this.constructor.__isPage) {
                    continue;
                }

                if (fieldName != "items") {
                    throw new Error("Only items field is supported for paginated models");
                }
                
                console.log("Load list from values: ", value);
                while (reactive[fieldName].length) {
                    reactive[fieldName].pop();
                }
                reactive[fieldName].push(...value.map(x => newModelInstance(field.type, x)));
            }

            else {
                let value = data[fieldNameMap(fieldName)];

                reactive[fieldName] = value;
            }
        }
    }

    this.load = async () => {

        let fieldData = this.constructor.getGraphqlFields(isView);

        // init empty arrays that don't use pagination
        // for (let fieldName of Object.keys(fieldData)) {
        //     let field = fieldData[fieldName];

        //     if (field.isArray && field.isModel()) {
                
        //         // paginated model can't use paginated model to recursively load fields
        //         if (this.constructor.__isPaginatedModel) {
        //             continue;
        //         }

        //         if (!reactive[fieldName]) {
        //             console.log("Init array field", fieldName);
        //             const pageType = Page(field.type);
        //             reactive[fieldName] = new pageType();
        //         }
        //     }
        // }

        // init empty pages
        for (let fieldName of Object.keys(fieldData)) {
            let field = fieldData[fieldName];

            if (field.type.__isPage) {
                if (!reactive[fieldName]) {
                    reactive[fieldName] = new field.type();
                }
            }
        }

        let fieldNames = Object.keys(fieldData).filter(field => {          
            return !!field;
        }).map(field => fieldData[field].toGraphQl(field));

        
        let modelName = this.constructor.__modelname || this.constructor.name;
        
        let data = {};
        
        console.log("field names to query", fieldNames);
        if (fieldNames.length) {
            data = await window.$api.graphql(modelName, this.objectId || this.id, fieldNames, this.fieldIds);
        }

        this.loadFromData(data);
    }
    
    if (!defer) {
        this.load();
    }

    return reactive;
    
}

GraphQlQuery.getGraphqlFields = function(isView) {

    console.log("get fields of ", this.name);
    if (this.fields) {
        return this.fields;
    }

    let fields = {};
    
    for (let fieldName of Object.keys(this)) {
        
        if (fieldName.startsWith("__")) {
            continue;
        }

        let field = this[fieldName];
        
        if (field instanceof FieldType) {
            fields[fieldName] = field;
            continue;
        }
        
        // resolve model dynamically by name
        if (typeof field == 'string') {
            field = window.$registeredModels[field.toLowerCase()];
        }

        if (
            field instanceof Function && 
            !(field.prototype instanceof GraphQlQuery) &&
            !(Array.isArray(field)) &&
            !(field == String) && 
            !(field == Number) &&
            !(field == Boolean)
        ) {
            continue;
        }


        if (field.prototype instanceof GraphQlQuery) {
            fields[fieldName] = new FieldType(field, false);
            continue;
        }

        if (Array.isArray(field)) {
            
            let arrayItemType = field[0];

            // resolve model dynamically by name
            if (typeof arrayItemType == 'string') {
                arrayItemType = window.$registeredModels[arrayItemType.toLowerCase()];
            }

            if (this.__isPage) {
                fields[fieldName] = new FieldType(
                    arrayItemType,
                    true,
                    {explicit: true} // make sure 'items' field on page stays the same without id suffix
                );
                continue;
            } 

            let pageType = Page(arrayItemType);
            
            console.log("set page type on", this.name, "for field", fieldName);
            fields[fieldName] = new FieldType(
                pageType,
                false,
            );
            continue;
        }

        fields[fieldName] = new FieldType(
            field,
            false,
        );
    }
    
    if (this.__proto__ != GraphQlQuery) {
        fields = {...fields, ...this.__proto__.getGraphqlFields(isView)};
    }

    console.log("fields of ", this.name, fields);
    this.fields = fields;
    return fields;
}

GraphQlQuery.getobjectIdSchema = function() {
    let result = "";
    for (let fieldName of Object.keys(this.__virtualId)) {
        result += fieldName + " ";
    }
    return result;
}

GraphQlQuery.getModelName = function() {
    return this.__modelname || this.name;
}

GraphQlQuery.toGraphQl = function() {
    /** 
     * Turns complex model into selection of fields {...}
    */

    console.log("model to graphql", this.getModelName());

    let fields = this.getGraphqlFields();
    let result = "{";
    for (let fieldName of Object.keys(fields)) {
        console.log("field to graphql", fieldName, fields[fieldName]);
        result += fields[fieldName].toGraphQl(fieldName) + " ";
    }
    return result + "}";
}

export function Page(T) {

    class Page extends GraphQlQuery {

        static __isPage = true;
        static __isExplicit = true;

        static items = [T]
        static count = Number

        constructor(data) {
            console.log("construct page from", data);
            super(Math.random(), undefined, {defer: true});
            this.items = [];
        }

        [Symbol.iterator]() {
            return this.items[Symbol.iterator]();
        }

        map(f) {
            return this.items.map(f);
        }

        filter(f) {
            return this.items.filter(f);
        }
    }

    // dirty hack to make sure page is not recursing into list item type
    // Page.toGraphQl = function() {
    //     return "{items count}";
    // }

    return Page;
}

// export function FieldWithArgs(fieldType) {

//     class PaginatedField extends GraphQlQuery {

//         constructor(id, fieldIds) {

//             let typeName = (type.__modelname || type.name).toLowerCase(); 

//             super(id, fieldIds, {defer: true});

//             // dynamically add requested field
//             this.constructor[fieldname] = [type];

//             this.items = [];
            

//             // perform initial load, since we deferred it
//             this.load();

//             window.$socket.onEvent("ModelCreateEvent", (data) => {
//                 let modelName = data.payload.model_name;
//                 let modelId = data.payload.model_pk;
                                
//                 if (typeName == modelName) {
//                     this.load();
//                     return;
//                 }

//                 for (let name of Object.keys(this.objectId)) {
//                     if (this.objectId[name] == modelName + "_id" && this.objectId[name] == modelId) {
//                         this.load();
//                         return;
//                     }
//                 }
//             });
//         }

//         // make iterable
//         [Symbol.iterator]() {
//             return this.items[Symbol.iterator]();
//         }

//         map(f) { 
//             return this.items.map(f);
//         }
        
//         filter(f) {
//             return this.items.filter(f);
//         }

//         applyFilter(name, value) {
//             this.fieldIds = this.fieldIds || {};
//             this.fieldIds[this.__fieldname] = this.fieldIds[this.__fieldname] || {};
//             this.fieldIds[this.__fieldname][name] = value;
//             this.load();
//         }
//         setPageSize(c) {
//             this.applyFilter('size', c);
//             this.load();
//         }
    
//         setPage(o) {
//             this.applyFilter('page', o);
//             this.load();
//         }
//     }
//     return PaginatedField;
// }



GraphQlQuery.all = function () {

    const getAll = (model) => {

        class ManyToOne extends GraphQlQuery {

            static __isPage = true;

            static count = Number
            static items = [model]        

            constructor(x) {
                super(x);
                this.items = [];

                window.$socket.onEvent("ModelCreateEvent", (data) => {
                  let modelName = data.payload.model_name;

                  if (modelName.toLowerCase() == model.getModelName().toLowerCase()) {
                    console.log("Update ALL view", model.getModelName());
                    this.load();
                  }
                });
            }

            [Symbol.iterator]() {
                return this.items[Symbol.iterator]();
            }
            
            setFilter(name, value) {
                this.objectId[name] = value;
                this.load();
            }

            setPage(p) {
                this.setFilter("page", p)
            }
            setSize(s) {
                this.setFilter("size", s)
            }
        }

        // AllView[model.getModelName().toLowerCase()] = [model];

        let v = new ManyToOne({model: model.getModelName().toLowerCase(), page: 0, size: 10});
        return v;

        // let modelName = model.__modelname || model.name;
        // let genericField = GenericPaginatedField(model, 'ManyToOne.items');
        // return new genericField(
        //     {model: modelName}, 
        //     {items: {
        //         page: 0, 
        //         size: 10
        //     }
        // });
    }
    
    return getAll(this);
}