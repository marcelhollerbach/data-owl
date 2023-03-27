from __future__ import annotations

from dataclasses import dataclass
from typing import Type, Dict

from dataclasses_json import dataclass_json

"""
Global dict of all registered filters
"""
filters: Dict[str, Type[AbstractFilter]] = {}


class AbstractFilter:
    filter_name: str
    value: str

    def __init__(self, value: str):
        self.value = value

    def verify(self):
        """
        Verify that the value is understandable for the implementation
        :return:
        """
        raise Exception("Base Implementation")

    def apply(self, previous_state: list[str]) -> list[str]:
        """
        Apply the filter on a previous state

        Return all the items that meet the conditions of the filter, and that are part of the previous state.
        :return:
        """
        raise Exception("Base Implementation")

    def apply_base(self) -> list[str]:
        """
        Apply the filter as a start

        Return all the items that meet the conditions of the filter.
        :return:
        """
        raise Exception("Base Implementation")


@dataclass_json
@dataclass
class SearchItem:
    """
    Defines a single Item what to search for

    The
    """
    value: str
    type: str


@dataclass_json
@dataclass
class SearchLine:
    """
    A single search line

    A search item is the intersection of multiple SearchItems.
    """
    intersection_request: list[SearchItem]


@dataclass_json
@dataclass
class SearchRequest:
    """
    A complete Search Request

    The request contains of a list of search lines. The result of this request is the union of the SearchLine Result.
    """
    union_requests: list[SearchLine]


@dataclass_json
@dataclass
class VerificationException(Exception):
    def __init__(self, title, error):
        self.title = title
        self.error = error


@dataclass_json
@dataclass
class VerificationHappening:
    line_index: int
    item_index: int
    title: str
    error: str


@dataclass_json
@dataclass
class VerificationResult:
    happenings: list[VerificationHappening]


class ParsedRequest:
    def __init__(self, content: list[list[AbstractFilter]]):
        self.content = content

    def verify(self) -> VerificationResult:
        """
        Compile the parsed requests

        Compile the parsed request. Each item gets verified, if there is an error the error is returned.
        The error is annotated with the line number and item number.

        :return:
        """
        exceptions = []
        for line_index, line in enumerate(self.content):
            for item_index, item in enumerate(line):
                try:
                    item.verify()
                except VerificationException as e:
                    exceptions.append(VerificationHappening(line_index, item_index, e.title, e.error))
        return VerificationResult(exceptions)

    @staticmethod
    def compile_requests(req: SearchRequest) -> ParsedRequest:
        """
        Create parsed request

        Create a parsed request from a given search request.
        :param req:
        :return:
        """

        def compile_line(line: SearchLine) -> list[AbstractFilter]:
            return [initiate_filter(f.type, f.value) for f in line.intersection_request]

        return ParsedRequest([compile_line(line) for line in req.union_requests])

    def apply(self) -> list[str]:
        """
        Apply the set of filter according to the specification.

        :return: A list of identifiers
        """
        union_result = []
        for line in self.content:
            first = True
            intersection_result = []
            for item in line:
                """
                Calculating the union of all specified items
                
                The first is the call to initate, take everything that is provided
                """
                if first:
                    intersection_result = item.apply_base()
                else:
                    intersection_result = item.apply(previous_state=intersection_result)

                if len(intersection_result) == 0:
                    break
            union_result.extend(intersection_result)

        return union_result


class FailingFilter(AbstractFilter):
    """
    Filter representing a missing hit or missing implementation
    """
    filter_name = "FailingFilter"
    type: str

    def __init__(self, value: str, trait_type: str):
        super().__init__(value)
        self.type = trait_type

    def verify(self):
        raise VerificationException(f"Filter {self.type} is not known",
                                    f"The only known filters are: {','.join(filters.keys())}")


def register_filter(filter_type: Type[AbstractFilter]):
    """
    Register a new filter in the set of known filters
    :param filter_type: The type of the abstract filter
    """
    filters[filter_type.filter_name] = filter_type


def initiate_filter(filter_type: str, value: str) -> AbstractFilter:
    """
    Initiate a filter over the passed type.

    The function returns always a value.
    :param filter_type: The type of the filter.
    :param value: The value of the search filter.
    :return: An AbstractFilter, returned in any case, later verify calls will emit errors over not existing types
    """
    if filter_type in filters:
        ttt = filters[filter_type]
        return ttt(value)
    else:
        return FailingFilter(value, filter_type)
