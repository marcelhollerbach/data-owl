from search.api import SearchRequest, ParsedRequest, register_filter
from search.filter_contains import ContainsFilter
from search.filter_type import TypeFilter

register_filter(TypeFilter)

register_filter(ContainsFilter)
