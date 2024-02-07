"""TursoAPI tap class."""

from __future__ import annotations

import typing as t

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_tursoapi import streams

if t.TYPE_CHECKING:
    from singer_sdk.streams import RESTStream

STREAM_TYPES: list[type[RESTStream[t.Any]]] = [
    streams.Organizations,
    streams.Groups,
    streams.Databases,
    streams.Locations,
]


class TapTursoAPI(Tap):
    """Singer tap for Turso API."""

    name = "tap-tursoapi"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "token",
            th.StringType,
            required=True,
            description="API Token for Turso API",
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams.

        Returns:
            A list of TursoAPI streams.
        """
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
