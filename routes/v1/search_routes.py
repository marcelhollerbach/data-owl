import json

from apiflask import APIBlueprint
from flask import request, Response

from basic.annotations import login_required
from search import SearchRequest, ParsedRequest

routes = APIBlueprint('search', __name__)


@routes.route('/search/apply', methods=['POST'])
@login_required
def search():
    data = request.get_json()

    SearchRequest.schema().load(data)
    search_request = SearchRequest.from_dict(data)
    parsed_request = ParsedRequest.compile_requests(search_request)
    problems = parsed_request.verify()
    if len(problems.happenings) != 0:
        return Response(status=400, response=problems.to_json())
    else:
        result = parsed_request.apply()
        return Response(status=200, response=json.dumps(result))


@routes.route('/search/compile', methods=['POST'])
@login_required
def compile_search():
    """
    Compile a search request

    Compile and verify a search request.  
    :return:
    """
    data = request.get_json()

    SearchRequest.schema().load(data)
    search_request = SearchRequest.from_dict(data)
    parsed_request = ParsedRequest.compile_requests(search_request)
    problems = parsed_request.verify()
    return Response(status=202, response=problems.to_json())
