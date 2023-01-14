from dataclasses import dataclass
from difflib import get_close_matches
from typing import Dict, Union

__all__ = ["get_warnings"]

Flat = str | float | int | bool
JSONType = Union[
    Flat,
    list["JSONType"],
    dict[str, "JSONType"],
    tuple["JSONType", ...],
]
DictType = dict[str, JSONType]
ListType = list[JSONType]
TupleType = tuple[JSONType, ...]


@dataclass
class DifferenceData:
    value: JSONType
    matches: list[str]


FlattenedDict = Dict[str, Flat | DifferenceData]


def compare_dicts(data_dict: DictType, model_dict: DictType):
    def compare_iterable(list1: ListType | TupleType, list2: ListType | TupleType):
        output_list = []
        for i, item in enumerate(list1):
            other_item = list2[i]
            if isinstance(item, dict):
                assert isinstance(other_item, dict)
                out = compare_dicts(item, other_item)
            elif isinstance(item, list):
                assert isinstance(other_item, list)
                out = compare_iterable(item, other_item)
            else:
                assert isinstance(item, tuple)
                assert isinstance(other_item, tuple)
                out = compare_iterable(item, other_item)
            output_list += [out]
        return output_list

    difference_dict = {}
    for k, v in data_dict.items():
        if k in model_dict:
            other_v = model_dict[k]
            if v != other_v:
                if isinstance(v, dict):
                    assert isinstance(other_v, dict)
                    difference_dict[k] = compare_dicts(v, other_v)
                elif isinstance(v, list):
                    assert isinstance(other_v, list)
                    difference_dict[k] = compare_iterable(v, other_v)
                elif isinstance(v, tuple):
                    assert isinstance(v, tuple)
                    assert isinstance(other_v, tuple)
                    difference_dict[k] = compare_iterable(v, other_v)
            else:
                pass
        else:
            m = get_close_matches(k, model_dict.keys())
            if len(m) != 0:
                difference_dict[k] = DifferenceData(v, m)
    return difference_dict


def outer_flatten(obj: DictType | ListType | TupleType, prefix: str = "") -> list[str]:
    def flatten(
        obj: DictType | ListType | TupleType, prefix: str = ""
    ) -> FlattenedDict:
        iterator = obj.items() if isinstance(obj, dict) else enumerate(obj)
        ret = {}
        for k, v in iterator:
            if isinstance(v, dict) or isinstance(v, list) or isinstance(v, tuple):
                update = flatten(v, prefix=f"{prefix} -> {k}")
            else:
                update = {f"Close match detected for: \n{prefix} -> {k}": v}
            ret.update(update)
        return ret

    flat = flatten(obj, prefix=prefix)

    return [
        f'{k} - Did you mean {" or ".join(v.matches)}?'
        for k, v in flat.items()
        if isinstance(v, DifferenceData)
    ]


def get_warnings(data_dict: DictType, model_dict: DictType, prefix: str):
    return outer_flatten(compare_dicts(data_dict, model_dict), prefix=prefix)
