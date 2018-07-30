#!/usr/bin/env python
# coding: utf-8
from __future__ import (absolute_import,
    division, print_function, unicode_literals)

import requests

from .oclc_exceptions import CollectionNotFound, NoKbart


class KB:
    """
    Read and represent data from OCLC's knowledge base.

    Requires a WSKey from here:
    https://platform.worldcat.org/wskey/
    Documentation for Knowledge Base API:
    https://www.oclc.org/developer/develop/web-services/worldcat-knowledge-base-api.en.html
    Documentation for OCLC Developer Tools:
    https://www.oclc.org/developer/develop.en.html
    """
    def __init__(self, wskey):
        """Set the default parameters for KB API requests."""
        self._defaults = {'alt': 'json', 'wskey': wskey}

    @property
    def collection_search_url(self):
        return '{0}search?'.format(self.collection_base_url)

    @property
    def collection_base_url(self):
        return 'http://worldcat.org/webservices/kb/rest/collections/'

    @property
    def entry_search_url(self):
        return '{0}search?'.format(self.entry_base_url)

    @property
    def entry_base_url(self):
        return 'http://worldcat.org/webservices/kb/rest/entries/'

    def search_collections(self, search_term, options=None):
        """
        Search the knowledge base for a specific collection.

        Args:
            search_term: Main search term to search by
            options: Dict of secondary options

        Returns:
            A dict containing the search results
        """
        payload = self._get_payload(options)
        payload['q'] = search_term

        return requests.get(self.collection_search_url, params=payload).json()

    def get_collection(self, collection_id, options=None):
        """
        Return a dict representing a knowledge base collection.

        Args:
            collection_id: OCLC collection id as a string
            options: Dict of secondary options
        Returns:
            Dict representing the collection
        Raises:
            CollectionNotFound: If no collection with collection_id exists
        """
        payload = self._get_payload(options)
        url = '{0}{1}'.format(self.collection_base_url, collection_id)
        r = requests.get(url, params=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise CollectionNotFound

    def get_all_entries(self, collection_id, options=None):
        """
        Retrieve all entries from a given collection.
        'collection_uid' and 'itemsPerPage' are set automatically,
        adjusting through in the options dict is not advises.
        Args:
            collection_id: OCLC collection id as a string
            options: Dict of secondary options
        Returns:
            A list of dicts of the collection entries
        """
        start_index = 1
        records = []
        payload = self._get_payload(options)
        payload.update({'collection_uid': collection_id,
                        'itemsPerPage': 50})
        while True:
            payload.update({'startIndex': start_index})
            r = requests.get(self.entry_search_url, params=payload).json()
            for entry in r['entries']:
                records.append(entry)

            if len(r['entries']) < 50:
                break
            start_index += 50

        return records

    def download_collection_kbart(self,
                                  collection_id,
                                  filename):
        """
        Download a copy of a collection's KBART file.
        Files will (should) be saved as a UTF-8 encoded tsv file.
        Args:
            collection_id: OCLC collection id as a string
            filename: Path and name with which to save the file
        Raises:
            NoKbart: If a link to the KBART file is not found
        """
        collection = self.get_collection(collection_id)
        for link in collection['links']:
            if link['rel'] == 'enclosure':
                url = link['href']
                break
        else:
            raise NoKbart
        kbart_file = requests.get(url, params=self._defaults, stream=True)
        with open(filename, 'wb') as f:
            for chunk in kbart_file.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    def _get_payload(self, options):
        """
        Set extra options for a request to the KB API.
        Options information can be found at:
        https://www.oclc.org/developer/develop/web-services/worldcat-knowledge-base-api.en.html
        Args:
            options: Dict of options to set. If none, return copy of the defaults.
        """
        payload = self._defaults.copy()
        try:
            payload.update(options)
        except TypeError:
            # Options is None by default
            pass
        return payload
