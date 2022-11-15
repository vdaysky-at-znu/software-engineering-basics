from typing import Type


class GetterProxy(type):

    def __getattribute__(self, item):

        if item in ['children', 'path'] or item.startswith('_'):
            return super().__getattribute__(item)

        print(f"Looking for {self} {item}")
        cls_name = self.__name__

        if cls_name == 'Permission':
            path = []
        else:
            path = self.path

        if path and path[-1] == '*':
            path = path[:-1]

        next_path = path + [item]

        if hasattr(self, '_origclass') and hasattr(self._origclass, '__annotations__'):
            ans = self._origclass.__annotations__

            if item in ans:
                o = new_perm_obj()
                setattr(o, 'path', next_path)
                return o

        cls = super().__getattribute__(item)

        if isinstance(cls, type):
            next_path += ['*']
            o = new_perm_obj(cls)
            print(f"Create copy of {cls}: {o} {o._origname}")
            setattr(o, 'path', next_path)
            return o

        raise AttributeError(f'No such attribute {item} on {cls_name}')


class PType(metaclass=GetterProxy):
    _origname: str
    _origclass: Type
    path: list

    @classmethod
    def str(cls):
        return ".".join(cls.path)


def new_perm_obj(cls=None) -> Type[PType]:

    if cls:
        class Copy(cls, PType):
            pass

        setattr(Copy, '_origname', cls.__name__)
        setattr(Copy, '_origclass', cls)

        return Copy
    else:
        class Copy(PType):
            pass
        return Copy


class Permission(PType):

    class Game(PType):
        class Ranked(PType):
            Create: PType

        Create: PType

    class Permission(PType):
        Create: PType
        Grant: PType
        Revoke: PType

    class Match(PType):
        Create: PType
