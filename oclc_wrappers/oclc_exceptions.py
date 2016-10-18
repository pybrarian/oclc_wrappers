#!/usr/bin/env python


class NoKbart(Exception):
    def __str__(self):
        return 'No KBART found. Please check your Knowledge Base.'


class CollectionNotFound(Exception):
    def __str__(self):
        return 'Collection not found. Please check your spelling.'


class RequestError(Exception):

    def __init__(self, request, attempt=''):
        self.r = request
        self.attempt = attempt

    def __str__(self):
        return '{} - {}'.format(self.r, self.attempt)
