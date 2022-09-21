import inspect
import random


class VirtualTableManager:
    def __init__(self):
        self.models = []
        self.queryable = []

    def table(self, *func, **kwargs):

        if not func:
            def wrapper(cls):
                self.models.append(cls)
                if kwargs["queryable"]:
                    self.queryable.append(cls)
                return cls
            return wrapper
        else:
            func = func[0]
            self.models.append(func)
            self.queryable.append(func)
            return func

    def get_graphql_requests(self):
        return "".join([x.create_graphql_request() for x in self.queryable])

    def get_graphql_responses(self):
        return "".join([x.create_graphql_response() for x in self.models])

    def define_resolvers(self, query):

        # Oh, no! python's closures are broken!
        def make_handler(model):
            dec = query.field(model.get_field_name())

            def resolve_thing(_, info, **fields):
                return model(**fields)

            dec(resolve_thing)

        for model in self.queryable:
            make_handler(model)


field_type_map = {
    bool: "Boolean",
    int: "Int",
    str: "String",
}


class VirtualTable:
    """
        Virtual tables are tables that are not stored in the database, but are instead generated from other tables.
        They can have similar interface to a normal table, but they might have multiple primary keys defining them.
    """

    @classmethod
    def create_graphql_request(cls):
        name = cls.__name__[0].lower() + cls.__name__[1:]

        result = f"{name}("

        constructor = inspect.signature(cls.__init__)
        params = constructor.parameters
        for i, (name, param) in enumerate(params.items()):
            if name == 'self':
                continue

            type = param.annotation

            is_last = i == len(params) - 1
            comma = "," if not is_last else ""
            result += f"{name}: {field_type_map[type]}{comma}"

        result += "): " + cls.__name__ + "\n"
        return result

    @classmethod
    def create_graphql_response(cls):

        from django.db.models import Model

        annotations = cls.__annotations__

        result = f"type {cls.__name__} {{\n"

        for field, type in annotations.items():

            if hasattr(type, '__origin__') and type.__origin__ is list:
                result += f"    {field}: [{type.__args__[0].__name__}]\n"
            elif inspect.isclass(type) and issubclass(type, Model):
                result += f"    {field}: {type.__name__}\n"
            else:
                result += f"    {field}: {field_type_map[type]}!\n"

        result += "}\n"

        return result

    @classmethod
    def resolve(cls, **args):
        return cls(**args)

    @classmethod
    def get_field_name(cls):
        return cls.__name__[0].lower() + cls.__name__[1:]
