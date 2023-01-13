from typing import Generic, Iterable, Optional, Type, TypeVar

from pydantic import BaseModel, create_model
from pydantic.generics import GenericModel


class BaseInitialParams(BaseModel):
    pass


class BaseUpdateParams(BaseModel):
    pass


def convert_pydantic(model: Type[BaseInitialParams]) -> Type[BaseUpdateParams]:
    new_fields = {
        field.name: (Optional[field.type_], None) for field in model.__fields__.values()
    }
    return create_model(
        f"Update{model.__name__}", __base__=BaseUpdateParams, **new_fields
    )


InitialParams = TypeVar("InitialParams", bound=BaseInitialParams)
UpdateParams = TypeVar("UpdateParams", bound=BaseUpdateParams)


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


class EndgameModel(GenericModel, Generic[InitialParams, UpdateParams, ProgramParams]):
    parameters: Parameters[InitialParams, UpdateParams]
    programs: list[Program[ProgramParams]]


def reduce_parameters(
    initial: BaseInitialParams, changes: Iterable[ParameterChanges[BaseUpdateParams]]
) -> BaseInitialParams:
    current_dict = initial.dict()
    for change in changes:
        current_dict.update(change.params.dict(exclude_unset=True))
    return type(initial).parse_obj(current_dict)
