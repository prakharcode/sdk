"""Abstract base class for API-type streams."""

import abc
from typing import Any, Iterable, Optional

import requests

from singer_sdk.streams.rest import RESTStream


class GraphQLStream(RESTStream, metaclass=abc.ABCMeta):
    """Abstract base class for API-type streams.

    GraphQL streams inherit from the class `GraphQLStream`, which in turn inherits from
    the `RESTStream` class. GraphQL streams are very similar to REST API-based streams,
    but instead of specifying a `path` and `url_params`, developers override the
    GraphQL query text.
    """

    __module__ = "singer_sdk"

    path = ""
    rest_method = "POST"

    @property
    def query(self) -> str:
        """Set or return the GraphQL query string.

        Raises:
            NotImplementedError: If the derived class doesn't define this property.
        """
        raise NotImplementedError("GraphQLStream `query` is not defined.")

    def prepare_request_payload(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Optional[dict]:
        """Prepare the data payload for the GraphQL API request.

        Developers generally should generally not need to override this method.
        Instead, developers set the payload by properly configuring the `query`
        attribute.

        Args:
            context: Stream partition or context dictionary.
            next_page_token: Token, page number or any request argument to request the
                next page of data.

        Returns:
            Dictionary with the body to use for the request.

        Raises:
            ValueError: If the `query` property is not set in the request body.
        """
        params = self.get_url_params(context, next_page_token)
        if self.query is None:
            raise ValueError("Graphql `query` property not set.")
        else:
            query = self.query
        if not query.lstrip().startswith("query"):
            # Wrap text in "query { }" if not already wrapped
            query = "query { " + query + " }"
        query = query.lstrip()
        request_data = {
            "query": (" ".join([line.strip() for line in query.splitlines()])),
            "variables": params,
        }
        self.logger.debug(f"Attempting query:\n{query}")
        return request_data

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows.

        Args:
            response: A raw `requests.Response`_ object.

        Yields:
            One item for every item found in the response.

        .. _requests.Response:
            https://docs.python-requests.org/en/latest/api/#requests.Response
        """
        resp_json = response.json()
        for row in resp_json["data"][self.name]:
            yield row
