import inspect
import random
import sys
from collections import defaultdict
from typing import TypeVar, Generic

from ariadne import ObjectType


def computed(method):
    sig = inspect.signature(method)

    return_type = sig.return_annotation

    method._prop_meta = [
        method.__name__,
        method,
        return_type
    ]

    return method


class TableManager:
    def __init__(self):
        self.models = []
        self.queryable = []
        self.gql_objects = []

    def get_gql_objects(self):
        return self.gql_objects

    def _add_cls(self, model, queryable):
        self.models.append(model)
        if queryable:
            self.queryable.append(model)

        for name in dir(model):
            method = getattr(model, name)

            if not callable(method):
                continue

            if not hasattr(method, '_prop_meta'):
                continue

            meta = method._prop_meta
            model._computed_props[model.__name__].append(meta)

    def table(self, *func, **kwargs):

        if not func:
            def wrapper(cls):
                self._add_cls(cls, kwargs["queryable"])
                return cls
            return wrapper
        else:
            func = func[0]
            self._add_cls(func, True)
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
                return model.resolve(**fields)

            dec(resolve_thing)

        def make_resolver(gql_obj, name, prop):
            dec = gql_obj.field(name)
            dec(lambda obj, info: prop(obj))

        for model in self.queryable:
            make_handler(model)

            gql_obj = ObjectType(model.get_type_name())
            self.gql_objects.append(gql_obj)

            for name, prop, return_type in model.get_custom_resolvers():
                make_resolver(gql_obj, name, prop)


field_type_map = {
    bool: "Boolean",
    int: "Int",
    str: "String",
}


def format_typed_arg(typed_arg):
    type = typed_arg.__args__[0]

    from django.db.models import Model

    if type in field_type_map:
        return field_type_map[type]

    if issubclass(type, Model):
        return f"{type.__name__}_id"
    if issubclass(type, AbstractTable):
        return type.get_type_name()
    else:
        raise ValueError(f"Unknown type {type}")


class AbstractTable:
    _computed_props = defaultdict(list)

    @classmethod
    def create_graphql_request(cls):
        raise NotImplementedError

    @classmethod
    def resolve(cls, **fields):
        raise NotImplementedError

    @classmethod
    def get_field_name(cls):
        return cls.__name__[0].lower() + cls.__name__[1:]

    @classmethod
    def get_custom_resolvers(cls):
        print(f"calss {cls} has custom resolvers: {cls._computed_props[cls.__name__]}")
        return cls._computed_props[cls.__name__]

    @classmethod
    def get_type_name(cls):
        raise NotImplementedError

    @classmethod
    def get_model_fields(cls):
        fields = []
        for name, prop, return_type in cls.get_custom_resolvers():
            fields.append([name, return_type])

        if hasattr(cls, "__annotations__"):
            for name, type in cls.__annotations__.items():
                fields.append([name, type])

        return fields

    @classmethod
    def create_graphql_response(cls):

        from django.db.models import Model

        result = f"type {cls.get_type_name()} {{\n"

        for field, type in cls.get_model_fields():

            if hasattr(type, '__origin__') and type.__origin__ is list:
                result += f"    {field}: [{format_typed_arg(type)}]\n"
            elif inspect.isclass(type) and issubclass(type, Model):
                raise ValueError("Model in graphql object, use id instead!")
            elif inspect.isclass(type) and issubclass(type, AbstractTable):
                result += f"    {field}: {type.get_type_name()}\n"
            else:
                result += f"    {field}: {field_type_map[type]}\n"

        result += "}\n"

        return result


T = TypeVar("T")

from typing import get_args


class Table(Generic[T], AbstractTable):

    def __init_subclass__(cls) -> None:
        cls._type_T = get_args(cls.__orig_bases__[0])[0]

    @classmethod
    def create_graphql_request(cls):
        return f"        {cls.get_field_name()}(id: Int!): {cls.get_type_name()}\n"

    @classmethod
    def resolve(cls, **fields):
        print(f"resolve {cls.__name__} with {fields}")
        return cls.get_model_type().objects.filter(**fields).first()

    @classmethod
    def get_model_type(cls):
        return cls._type_T

    @classmethod
    def get_type_name(cls):
        return cls._type_T.__name__

    @classmethod
    def get_field_name(cls):
        n = cls._type_T.__name__[0].lower() + cls._type_T.__name__[1:]
        print(f"table name: {n}")
        return n


class VirtualTable(AbstractTable):
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
    def get_type_name(cls):
        return cls.__name__


    @classmethod
    def resolve(cls, **args):
        return cls(**args)


