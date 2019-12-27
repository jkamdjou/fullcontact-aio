import json
import logging
import aiohttp
import sys
import urllib.parse as urllib


log = logging.getLogger(__name__)

class FullContactRespoonse(object):
    def __init__(self, status_code, rate_limit_remaining, json_response):
        self.status_code = status_code
        self.rate_limit_remaining = rate_limit_remaining
        self.json_response = json_response


class FullContact(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.fullcontact.com/v3/'
        self.post_endpoints = {
            'person': 'person.enrich',
            'company': 'company.enrich'
        }
        for endpoint in self.post_endpoints:
            method = lambda endpoint=endpoint, **kwargs: self.api_post(endpoint, **kwargs)
            setattr(self, endpoint, method)

    async def api_post(self, endpoint, **kwargs):
        """ Makes a FullContact API call

        Formats and submits a request to the specified endpoint, passing
        any key-value pairs passed in kwargs as json body parameters.

        Args:
            endpoint: shortname of the API endpoint to use.
            strict: if True, throw an error
            **kwargs: a dict of query parameters to append to the request.

        Returns:
            A Requests object containing the result of the API call. Interact
            with the return value of this function as you would with any
            other Requests object.

        Raises:
            KeyError: the specified endpoint was not recognized. Check the
                docs.
            Requests.Exceptions.*: an error was raised by the Requests
                module.
        """

        headers = {'Authorization': 'Bearer {}'.format(self.api_key)}
        headers['Content-Type'] = 'application/json'
        endpoint = self.base_url + self.post_endpoints[endpoint]
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=kwargs, headers=headers) as request:
                try:
                    rate_limit_remaining = request.headers["x-rate-limit-remaining"]
                except KeyError:
                    rate_limit_remaining = "Failed to get the remaining rate"
                status_code = request.status
                to_json = await request.json()
                return FullContactRespoonse(status_code, rate_limit_remaining, to_json)
