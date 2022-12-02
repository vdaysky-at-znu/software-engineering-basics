import functools
import inspect
import logging
import random
import sys
import traceback
from collections import defaultdict
from typing import TypeVar, Generic, List, get_args, Tuple, Type, Optional, Union, Callable
from starlette.requests import Request

from ariadne import ObjectType

from api.services.auth import get_player


def _parse_signature(function):
    sig = inspect.signature(function)
    params = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue

        if param.annotation == inspect._empty:
            continue

        params.append({
            "type": param.annotation,
            "name": name,
            "required": param.default == inspect.Parameter.empty
        })
    return params


def _register_computed_method(callable, paginate, filters):
    from api.graphql.query import Page

    # get args needed by raw computed prop itself
    sig = inspect.signature(callable)

    return_type = sig.return_annotation
    param_sig = _parse_signature(callable)

    # add pagination props if needed
    if paginate:
        param_sig.append({
            "type": int,
            "name": "page",
            "required": False
        })
        param_sig.append({
            "type": int,
            "name": "size",
            "required": False
        })
        if return_type.__origin__ != Page:
            if return_type.__origin__ == list:
                return_type = Page[return_type.__args__[0]]
            else:
                raise ValueError("Paginate can only be used with Page/List return types.")

    # add filter props if needed
    if filters:
        for filter in filters:
            filter_sig = _parse_signature(filter)
            param_sig.extend(filter_sig)

    def wrapped_handler(self, **kwargs):

        callable_args = {}
        for orig_param in _parse_signature(callable):
            arg_name = orig_param['name']
            if arg_name in kwargs:
                callable_args[arg_name] = kwargs[arg_name]

        result = callable(self, **callable_args)

        if filters:
            for filter in filters:
                filter_args = {}
                for orig_param in _parse_signature(filter):
                    arg_name = orig_param['name']
                    if arg_name in kwargs:
                        filter_args[arg_name] = kwargs[arg_name]

                result = filter(result, **filter_args)

        if paginate:
            page = kwargs['page']
            size = kwargs['size']
            if isinstance(result, list):
                result = Page(len(result), result[page * size: (page + 1) * size])
            else:
                result = Page(result.count(), result.values_list('id', flat=True)[page * size:page * size + size])

        return result

    callable._prop_meta = [
        callable.__name__,
        wrapped_handler,
        return_type,
        param_sig
    ]


def computed(method=None, *, paginate=False, filters: List[Callable] = None):

    # called as function
    if not method:
        def real_decorator(method):
            _register_computed_method(method, paginate, filters)
            return method

        return real_decorator

    # called as decorator
    _register_computed_method(method, paginate, filters)
    return method


class TableManager:
    def __init__(self):
        self.models = []

        self.queryable = []
        self.gql_objects = []

        # list of models that have to be converted
        # to string type representation
        self.models_to_process = {}

    def get_gql_objects(self):
        return self.gql_objects

    def _add_cls(self, model, queryable):

        self.models.append(model)
        print(f"Adding model to process {model.__name__}")
        self.models_to_process[model.__name__] = model

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

    def type(self, cls):
        """ GraphQL type. Difference from table is that type is not queryable.
            Also type can ge generic, which means multiple GraphQL types will be created.
        """
        # map table manager to type class, because we will need to create helper type
        # inside same manager as this type
        cls._table_mgr = self
        return cls

    def get_graphql_requests(self):
        requests = []
        for model in self.queryable:
            try:
                requests.append(model.create_graphql_request())
            except Exception as e:
                print(f"Error while generating graphql request for {model.__name__}")
                raise e

        return "\n".join(requests)

    def get_graphql_responses(self):
        typedefs = ""
        compiled = set()
        print(f"compile graphql")
        while self.models_to_process:
            key = self.models_to_process.keys().__iter__().__next__()

            if key in compiled:
                continue

            compiled.add(key)

            print(f"compile model {key}")
            model = self.models_to_process.pop(key)
            typedefs += model.create_graphql_response()

        return typedefs

    def define_resolvers(self, query):

        # Oh, no! python's closures are broken!
        def make_handler(model):
            dec = query.field(model.get_field_name())

            def resolve_thing(_, info, **fields):
                return model.resolve_with_context(info, **fields)

            dec(resolve_thing)

        def make_resolver(gql_obj, name, prop, args):
            dec = gql_obj.field(name)

            def test(obj, **kwargs):
                return prop(obj, **kwargs)

            dec(lambda obj, info, **kwargs: test(obj, **kwargs))

        for model in self.queryable:
            make_handler(model)

            gql_obj = ObjectType(model.get_type_name())
            self.gql_objects.append(gql_obj)

            for name, prop, return_type, args in model.get_custom_resolvers():
                make_resolver(gql_obj, name, prop, args)


field_type_map = {
    bool: "Boolean",
    int: "Int",
    str: "String",
    float: "Float",
}


def pythonic_to_graphql(type, field_owner=None):
    """ Converts a python type to a graphql type. """

    if hasattr(type, '__origin__'):
        origin = type.__origin__
        generic_args = type.__args__
    else:
        origin = None
        generic_args = None

    if origin == Union:
        return pythonic_to_graphql(generic_args[0], field_owner=field_owner)

    if origin and issubclass(origin, VirtualGenericTable):
        # we have a parametrized custom type.

        # we detected a custom type, so we need to generate a helper table.
        # example: Page[CustomIdType]

        helper_type_name = generate_helper_table_name(origin, generic_args)

        class HelperType(origin):
            # TODO: store a dictionary of generic vars here instead of single var
            #  to support multiple generic vars, like Page[CustomIdType, Int32]
            _generic_type = generic_args[0]

        HelperType.__name__ = helper_type_name

        print(f"Add helper type {helper_type_name}")
        origin._table_mgr._add_cls(HelperType, False)

        return helper_type_name

    if isinstance(type, AbstractTable):
        return type.get_type_name()

    if origin and issubclass(origin, AbstractTable):
        return origin.get_type_name()

    if origin is list:
        return f"[{format_typed_arg(type, field_owner)}]"

    if type in field_type_map:
        return field_type_map[type]

    return type.__name__


def generate_helper_table_name(base, generic_args):
    return f"GenericHelper__{base.__name__}__{generic_args[0].__name__}"


def format_typed_arg(typed_arg, field_owner=None):
    """
        Formats a typed argument for graphql considering it's content.
        List[Player] will become Player, List[int] will become Int, etc.
    """

    print(f"format_typed_arg: {typed_arg}")

    generic_arg = typed_arg.__args__[0]

    from django.db.models import Model

    if isinstance(generic_arg, TypeVar):
        # TODO: get generic var type by name from dictionary
        generic_arg = field_owner._generic_type

    if generic_arg in field_type_map:
        return field_type_map[generic_arg]

    if issubclass(generic_arg, Model):
        return f"{generic_arg.__name__}_id"
    if issubclass(generic_arg, AbstractTable):
        return generic_arg.get_type_name()
    else:
        raise ValueError(f"Unknown type {generic_arg}")


class AbstractTable:
    _computed_props = defaultdict(list)

    @classmethod
    def create_graphql_request(cls):
        """
            player(id: Int!): Player
        """

        name = cls.get_field_name()

        result = f"{name}"

        args = cls.get_constructor_args()

        compiled_args = ""

        for i, (name, type) in enumerate(args):
            if name == 'self':
                continue

            is_last = i == len(args) - 1
            comma = "," if not is_last else ""
            try:
                _mapped = field_type_map[type]
            except KeyError:
                raise ValueError(f"Unknown type {type} for field {name} in {cls.__name__}")
            compiled_args += f"{name}: {_mapped}{comma}"

        if compiled_args:
            result += f"({compiled_args})"

        result += ": " + cls.get_type_name() + "\n"
        return result

    @classmethod
    def get_constructor_args(cls) -> List[Tuple[str, Type]]:
        raise NotImplementedError

    @classmethod
    def resolve(cls, __parent=None, **fields):
        """ Resolve upper level of model without any recursion """
        raise NotImplementedError

    @classmethod
    def resolve_children(cls, self):
        """ Completely resolve child models on this level

            @param cls: the class of the parent model to resolve
            @param self: the parent model value. Not necessarily an instance of cls.
        """
        for name, return_type, args in cls.get_model_fields():
            if isinstance(return_type, type) and issubclass(return_type, AbstractTable):
                model = return_type.resolve_recursively(self)
                setattr(self, name, model)

    @classmethod
    def resolve_recursively(cls, __parent=None, **fields):
        model = cls.resolve(__parent, **fields)
        cls.resolve_children(model)
        return model

    @classmethod
    def resolve_with_context(cls, __info=None, **fields):
        obj = cls.resolve_recursively(None, **fields)

        if obj is not None:

            player = None
            request: Optional[Request] = None
            if __info:
                request = __info.context.get("request")
                player = get_player(request.headers.get('session_id'))

            obj.context = {
                'player': player,
                'request': request
            }

        return obj

    @classmethod
    def get_field_name(cls):
        return cls.__name__[0].lower() + cls.__name__[1:]

    @classmethod
    def get_custom_resolvers(cls):
        return cls._computed_props[cls.__name__]

    @classmethod
    def get_type_name(cls):
        raise NotImplementedError

    @classmethod
    def get_model_fields(cls):
        fields = []
        for name, prop, return_type, args in cls.get_custom_resolvers():
            fields.append([name, return_type, args])

        if hasattr(cls, "__annotations__"):
            for name, type in cls.__annotations__.items():
                fields.append([name, type, []])

        return fields

    @classmethod
    def create_graphql_response(cls):
        """
            Creates GraphQl definition of model type.
            Includes all fields and computed properties.

            type Player { username elo team_id }
        """

        from django.db.models import Model

        result = f"type {cls.get_type_name()} {{\n"

        for field, type, args in cls.get_model_fields():
            field_args = ""

            if args:
                field_args = "(" + ", ".join([f"{x['name']}: {pythonic_to_graphql(x['type'], field_owner=cls)}" for x in args]) + ")"

            if inspect.isclass(type) and issubclass(type, Model):
                raise ValueError("Model in graphql object, use id instead!")

            result += f"    {field}{field_args}: {pythonic_to_graphql(type, field_owner=cls)}\n"

        result += "}\n"

        return result


T = TypeVar("T")


class Table(Generic[T], AbstractTable):

    def __init_subclass__(cls) -> None:
        cls._type_T = get_args(cls.__orig_bases__[0])[0]

    @classmethod
    def get_constructor_args(cls) -> List[Tuple[str, Type]]:
        return [("id", int)]  # database table row has only one arg - id

    @classmethod
    def resolve(cls, __parent=None, **fields):
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
        n = cls.get_type_name()[0].lower() + cls.get_type_name()[1:]
        return n


class VirtualTable(AbstractTable):
    """
        Virtual tables are tables that are not stored in the database, but are instead generated from other tables.
        They can have similar interface to a normal table, but they might have multiple primary keys defining them.

        The main difference between a virtual table and a normal table is that virtual tables build their requests
        dynamically, based on init arguments. They are resolved just like normal tables, through constructor.
    """

    @classmethod
    def get_constructor_args(cls) -> List[Tuple[str, Type]]:
        items = []
        constructor = inspect.signature(cls.__init__)
        params = constructor.parameters
        for name, param in params.items():
            if name == "self":
                continue
            items.append((name, param.annotation))

        return items

    @classmethod
    def get_type_name(cls):
        return cls.__name__

    @classmethod
    def resolve(cls, __parent=None, **args):
        try:
            return cls(**args)
        except Exception as e:
            traceback.print_exc()
            raise ValueError(f"Could not init {cls} with **{args}")


class VirtualGenericTable(VirtualTable):
    pass


X = TypeVar("X")


class PaginatedTable(Generic[X], VirtualTable):
    count: int
    items: List[X]

    def __init_subclass__(cls) -> None:
        cls._type_T = get_args(cls.__orig_bases__[0])[0]
        # stupid hack to ensure that list type is accessible
        cls.__annotations__['items'].__args__ = [cls._type_T]

    def __init__(self, items: List[X], page: int, size: int):
        self.items = items[page * size: (page + 1) * size]
        self.count = len(items)


Y = TypeVar("Y")


class PList(Generic[Y]):

    def __init_subclass__(cls) -> None:
        cls._type_T = get_args(cls.__orig_bases__[0])[0]
