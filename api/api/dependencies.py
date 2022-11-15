import inspect
import traceback
from typing import Optional, Type, List, Any, Callable
from uuid import UUID

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from fastapi import Request, HTTPException, Depends, params, Query, Response
from pydantic.class_validators import root_validator
from pydantic.main import create_model
from django.db.models import Model

from api.exceptions import AuthorizationError
from api.models import Team, Player, AuthSession, Event, Match, Game, Invite, InGameTeam, MapPick, PlayerQueue, Map

# Inherit str to make type serializable by openapi
from api.util import OrmBaseModel


class UndefinedType(str):
    def __eq__(self, other):
        return type(self) == type(other)

    def __new__(cls, openapi_name='abc'):
        obj = str.__new__(cls, openapi_name)
        return obj

    def __str__(self):
        return "Undefined"


UNDEFINED = UndefinedType(openapi_name='Undefined')


class QueryItem:
    def __init__(self, api_field, db_field, type, required=True, **kwargs):
        self.api_field = api_field.split('.')[0]
        self._loaded_field_path = api_field.split('.')[1:]
        self.db_field = db_field
        self.type = type
        self.required = required

        if 'default' in kwargs:
            self.default = kwargs['default']
        else:
            self.default = UNDEFINED

        if isinstance(type, params.Depends):
            self.type = Any,
            self.default = type

        if 'loc' in kwargs:
            if kwargs['loc'] == 'param':
                default = self.default
                self.default = Query(default=default)

    def get_value(self, value):
        """
            Get value that is used by query. If api_field has value of pool.chain,
            then this method will return value of nested field chain
        """

        if not self._loaded_field_path:
            return value

        field_model = type(value)

        path_to_field = self._loaded_field_path[:-1]
        searched_field = self._loaded_field_path[-1]

        for item in path_to_field:
            field_model = getattr(field_model, item).rel_model
            value = field_model.get_by_id(getattr(value, item))

        return getattr(value, searched_field)

    def __str__(self):
        if inspect.isclass(self.type):
            type_name = self.type.__name__
        else:
            type_name = type(self.type).__name__

        return f"<Query {self.api_field}:{type_name} -> " \
               f"model.{self.db_field} (default={self.default}) {'*' if self.required else ''}>"

    def __repr__(self):
        return str(self)


def get_model(model, values: List[Any], query: List[QueryItem]):
    # NOTE: this restriction does not account for joining same table on different fields
    joined_models = set()

    if not values or all([v == UNDEFINED for v in values]):
        return None

    sql_query = model.objects.all()
    for value, query_item in zip(values, query):

        # value is not required and wasn't passed
        # ignore it
        if value == UNDEFINED:
            continue

        _model = model

        path = query_item.db_field.split(".")

        # make joins for all intermediate tables
        while len(path) > 1:
            field = path.pop(0)

            _model = getattr(_model, field).rel_model

            if _model in joined_models:
                # if field already joined just switch to it,
                # so we can continue joining from there
                sql_query = sql_query.switch(_model)
                continue

            joined_models.add(_model)
            sql_query = sql_query.join(_model)

        # if query uses nested field of loaded model
        # it will be retrieved here
        value = query_item.get_value(value)

        # last item in path is actual field we will be searching by
        filter_by = path.pop(0)
        sql_query = sql_query.filter(**{getattr(_model, filter_by): value})

        # return context back to top-level model
        # to start over for the next field on the next iteration
        sql_query.switch(model)

    return sql_query.get_or_none()


class ComplexFieldModelBase(OrmBaseModel):
    """
        This model type is inherited by dynamically generated models that represent
        one complex type (like token, that is identified by address and chain id).
        this model will have __computed_value__ field after validation, which contains
        database model instance. This class will pass any get attribute calls to it,
        this way it is safe to access fields of database model from this type
    """
    pass


class BaseModelWithComplexField(OrmBaseModel):
    """
        This class can be inherited by pydantic models that contain
        complex fields. It will substitute BaseModel with actual database model.
    """

    @root_validator
    def validate_model_with_complex_field(cls, values):
        """
            Find all complex field instances and substitute them with db models
        """

        for key in values.keys():
            field = values[key]
            if isinstance(field, ComplexFieldModelBase):
                values[key] = field.__computed_value__

        return values


def complex_field_factory(
        model: Type[Model],
        query: List[QueryItem],
        required: bool,
        default: Any,
):
    """
        Dynamically create model according to expected set of fields.
        Created model will have the ability to automatically look up
        database model instance and act like it.

        @param model Database model we expect to get
        @param query mapping of expected params to database fields of model,
        consists of (
            api_field: str - field received from request body,
            db_field: str - address of db column relative to model, separated by dot if recursive
            field_type: type - expected type of value, used for annotation,
            required: whether this field is required. If not required, field has default of UNDEFINED
        )
        @param required whether end result can be None
        @param default default value in case no match found
    """

    class ComplexFieldModelType(ComplexFieldModelBase):

        def __getattribute__(self, item):
            """ Override __getattribute__ method to make this class a proxy. """

            if hasattr(super(), item):
                return super().__getattribute__(item)

            computed = super().__getattribute__('__computed_value__')

            if item == '__computed_value__':
                return computed

            # all fields (methods) that are not present on this instance will be
            # redirected to database model instance stored at __computed_value__
            return getattr(computed, item)

        @root_validator(allow_reuse=True)
        def validate_model(cls, values):
            """ Get model instance by fields, save it as __computed_value__ """

            for q_item in query:
                if q_item.api_field not in values:
                    raise ValueError(f'Field {q_item.api_field} is invalid')

            _values = [values[q_item.api_field] for q_item in query]

            instance = get_model(model, _values, query)

            if instance is None and not required:
                return default

            if instance is None:
                raise ValueError(f"{model.__name__} not found")

            values['__computed_value__'] = instance
            return values

    # fields that should be present on new model
    expected_fields = {}

    for q_item in query:
        if q_item.required:
            expected_fields[q_item.api_field] = (q_item.type, ...)
        else:
            expected_fields[q_item.api_field] = (q_item.type, q_item.default)

    # use subclass count as unique identifier
    subclass_count = len(ComplexFieldModelBase.__subclasses__())
    dynamic_model = create_model(
        f'ComplexFieldModel_{model.__name__}_{subclass_count}',
        **expected_fields,
        __base__=ComplexFieldModelType
    )

    return dynamic_model


def DatabaseModelField( # NOQA
        model: Type[Model],
        primary_field: str = 'uuid',
        model_fields: List[str] = None,
        normalizer: Callable = lambda x: x,
        type: Type = str,
        required: bool = True,
        default: bool = None,
):
    """
        Custom pydantic field type that performs database model lookup.

        :param model: model to find
        :param primary_field: name of primary field (the one this type is applied for) in database
        :param model_fields: list of names of additional fields (for example wallet requires chain besides address)
        Must be valid field of model and must be present in pydantic model containing this annotation on the top level
        :param normalizer: function to normalize this field, like .lower() for addresses
        :param type: expected primitive type
        :param required: whether field is required
        :param default: fallback value in case field is not required and model was not found
        :return: field type that can be used as annotation
    """

    if not issubclass(model, Model):
        raise ValueError(f"{model} is not a Model")

    if not hasattr(model, primary_field):
        raise ValueError(f"Model {model} does not have field {primary_field}")

    class DatabaseModelFieldInfo:

        @classmethod
        def __get_validators__(cls):
            yield cls.validate

        @classmethod
        def __modify_schema__(cls, field_schema):
            field_schema.update(examples=[])

        @classmethod
        def validate(cls, v, values):

            if v is None:
                if required:
                    raise ValueError(f"{model.__name__} is required")
                return default

            if not isinstance(v, type):
                try:
                    v = type(v)
                except:
                    raise ValueError(f"type {type.__name__} is expected")

            v = normalizer(v)

            from django.db.models.query_utils import DeferredAttribute

            field = getattr(model, primary_field)

            # primary field
            q = model.objects.filter(**{field.field.attname if isinstance(field, DeferredAttribute) else field: v})

            for field_name in model_fields or []:
                # make sure additional field is defined in model on the top level

                # NOTE: all fields this field is depending on have to be defined BEFORE
                # this field is defined.
                if field_name not in values:
                    raise ValueError(f"{field_name} is not found. {model.__name__} can't be identified.")

                # add additional field to query
                q = q.filter(**{getattr(model, field_name): values[field_name]})

            instance = q.first()

            if instance is None:
                model_fields_summary = ", ".join([f'{k} = {repr(values[k])}' for k in model_fields or []])
                raise ValueError(
                    f"{model.__name__} with {primary_field} of {v}"
                    f" and {model_fields_summary} does not exist"
                )
            else:
                return instance

        def __repr__(self):
            return f'DatabaseModelFieldInfo({model.__name__})'

    return DatabaseModelFieldInfo


def depends_factory(model, api_field, api_field_type, db_field="id", required=False):
    def inner(**kwargs):
        value = kwargs[api_field]
        if value is None:
            return None
        try:
            instance = model.objects.filter(**{db_field: value})
            if instance.exists():
                return instance.get()
        except Exception:
            traceback.print_exc()
            pass

        raise HTTPException(status_code=404, detail=f"{model.__name__} with {db_field} of {value} not found")

    param = {
        "kind": 1,
        "name": api_field,
        "annotation": api_field_type
    }

    if not required:
        param['default'] = None

    sig = inspect.Signature(
        parameters=[inspect.Parameter(**param)]
    )

    inner.__signature__ = sig
    return Depends(inner)


def RosterDependency(required=True):
    return depends_factory(Team, 'roster', int, 'id', required)


def PlayerDependency(required=True):
    return depends_factory(Player, 'player', UUID, 'uuid', required)


def get_session(request: Request, response: Response):
    """ Get session from request or create new one """

    session_id = request.headers.get('session_id')
    session = None

    if session_id:
        query = AuthSession.objects.filter(session_key=session_id)
        if query.exists():
            session = query.get()

    if not session:
        session = AuthSession.create(None)
        response.headers['session_id'] = session.session_key

    return session


SessionDependency = Depends(get_session)


def get_player(session: AuthSession = SessionDependency):
    """ Get player from session. If session does not have player, throw an error """

    player = session.player

    if player is None:
        raise AuthorizationError("Player is not found")

    return player


InviteDependency = depends_factory(Invite, 'invite', int, 'id', True)
MatchDependency = depends_factory(Match, 'match', int, 'id', True)

PlayerAuthDependency = Depends(get_player)

EventField = DatabaseModelField(model=Event, primary_field="id", type=int)
MatchField = DatabaseModelField(model=Match, primary_field="id", type=int)
GameField = DatabaseModelField(model=Game, primary_field="id", type=int)
TeamField = DatabaseModelField(model=Team, primary_field="id", type=int)
PlayerField = DatabaseModelField(model=Player, primary_field="id", type=int)
InGameTeamField = DatabaseModelField(model=InGameTeam, primary_field="id", type=int)
MapPickField = DatabaseModelField(model=MapPick, primary_field="id", type=int)
QueueField = DatabaseModelField(model=PlayerQueue, primary_field="id", type=int)
MapField = DatabaseModelField(model=Map, primary_field="id", type=int)
