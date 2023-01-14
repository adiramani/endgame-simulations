import warnings
from typing import Generic, Iterable, Optional, Type, TypeVar

from pydantic import BaseModel, PrivateAttr, create_model
from pydantic.generics import GenericModel

from .get_warnings import get_warnings

__all__ = [
    "EndgameModel",
    "create_update_model",
    "apply_incremental_param_changes",
    "BaseInitialParams",
    "BaseProgramParams",
]


class BaseEndgame(BaseModel):
    def __init__(self, **data) -> None:
        super().__init__(**data)
        new_data = {}
        for k, v in data.items():
            if isinstance(v, BaseModel):
                new_data[k] = v.dict()
            else:
                new_data[k] = v
        output = get_warnings(new_data, self.dict(), prefix=self.__class__.__name__)
        for w in output:
            warnings.warn(w, stacklevel=9999)


class BaseInitialParams(BaseModel):
    pass


class _BaseUpdateParams(BaseModel):
    pass


def create_update_model(
    initial_model: Type[BaseInitialParams],
) -> Type[_BaseUpdateParams]:
    new_fields = {
        field.name: (Optional[field.type_], None)
        for field in initial_model.__fields__.values()
    }
    return create_model(
        f"Update{initial_model.__name__}", __base__=_BaseUpdateParams, **new_fields
    )


InitialParams = TypeVar("InitialParams", bound=BaseInitialParams)
UpdateParams = TypeVar("UpdateParams", bound=_BaseUpdateParams)


class ParameterChanges(GenericModel, Generic[UpdateParams]):
    year: int
    month: int = 1
    params: UpdateParams


class Parameters(GenericModel, Generic[InitialParams, UpdateParams]):
    initial: InitialParams
    changes: list[ParameterChanges[UpdateParams]]


class BaseProgramParams(BaseModel):
    treatment_interval: float


ProgramParams = TypeVar("ProgramParams", bound=BaseProgramParams)


class Program(GenericModel, Generic[ProgramParams]):
    first_year: int
    first_month: int = 1
    last_year: int
    last_month: int = 12
    interventions: ProgramParams | list[ProgramParams]


class EndgameModel(
    GenericModel, Generic[InitialParams, UpdateParams, ProgramParams], BaseEndgame
):
    __top__ = PrivateAttr()
    parameters: Parameters[InitialParams, UpdateParams]
    programs: list[Program[ProgramParams]]


def apply_incremental_param_changes(
    initial: BaseInitialParams, changes: Iterable[ParameterChanges[_BaseUpdateParams]]
) -> BaseInitialParams:
    current_dict = initial.dict()
    for change in changes:
        current_dict.update(change.params.dict(exclude_unset=True))
    return type(initial).parse_obj(current_dict)


def make_endgame_model(
    name: str,
    initial_model: Type[BaseInitialParams],
    treatment_model: Type[BaseProgramParams],
) -> Type[EndgameModel]:
    NewModel = EndgameModel[
        initial_model, create_update_model(initial_model), treatment_model
    ]
    NewModel.__name__ = name
    return NewModel
