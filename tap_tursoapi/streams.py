"""Stream type classes for tap-tursoapi."""

from __future__ import annotations

import typing as t

from singer_sdk import typing as th
from singer_sdk.pagination import BasePageNumberPaginator

from tap_tursoapi.client import TursoAPIStream

if t.TYPE_CHECKING:
    from requests import Response


class Organizations(TursoAPIStream[None]):
    """Organizations stream."""

    name = "organizations"
    path = "/v1/organizations"
    primary_keys = ("slug",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property("blocked_reads", th.BooleanType),
        th.Property("blocked_writes", th.BooleanType),
        th.Property("name", th.StringType),
        th.Property("overages", th.BooleanType),
        th.Property("slug", th.StringType),
        th.Property("type", th.StringType, allowed_values=["personal", "team"]),
        th.Property("plan_id", th.StringType),
        th.Property("plan_timeline", th.StringType),
        th.Property("memory", th.IntegerType),
    ).to_dict()

    def get_child_context(
        self,
        record: dict[str, t.Any],
        context: dict[str, t.Any] | None,  # noqa: ARG002
    ) -> dict[str, t.Any] | None:
        """Get the child context for a record.

        Args:
            record: The record.
            context: The current context.

        Returns:
            The child context.
        """
        return {
            "organization_name": record["slug"],
        }


class Groups(TursoAPIStream[None]):
    """Groups stream."""

    parent_stream_type = Organizations

    name = "groups"
    path = "/v1/organizations/{organization_name}/groups"
    primary_keys = ("uuid",)
    replication_key = None
    records_jsonpath = "$.groups[*]"

    schema = th.PropertiesList(
        th.Property("archived", th.BooleanType),
        th.Property("locations", th.ArrayType(th.StringType)),
        th.Property("name", th.StringType),
        th.Property("primary", th.StringType),
        th.Property("uuid", th.UUIDType),
        th.Property("organization_name", th.StringType),
    ).to_dict()


class Databases(TursoAPIStream[None]):
    """Databases stream."""

    parent_stream_type = Organizations

    name = "databases"
    path = "/v1/organizations/{organization_name}/databases"
    primary_keys = ("DbId",)
    replication_key = None
    records_jsonpath = "$.databases[*]"

    schema = th.PropertiesList(
        th.Property("DbId", th.StringType),
        th.Property("Hostname", th.StringType),
        th.Property("hostname", th.StringType),
        th.Property("Name", th.StringType),
        th.Property("group", th.StringType),
        th.Property("primaryRegion", th.StringType),
        th.Property("regions", th.ArrayType(th.StringType)),
        th.Property("type", th.StringType),
        th.Property("version", th.StringType),
        th.Property("sleeping", th.BooleanType),
        th.Property("organization_name", th.StringType),
    ).to_dict()


class Locations(TursoAPIStream[None]):
    """Locations stream."""

    name = "locations"
    path = "/v1/locations"
    primary_keys = ("code",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property("name", th.StringType),
        th.Property("code", th.StringType),
    ).to_dict()

    def parse_response(self, response: Response) -> t.Iterable[dict[str, t.Any]]:
        """Parse the response and yield records.

        Args:
            response: The response.

        Yields:
            The records.
        """
        for code, name in response.json().get("locations", {}).items():
            yield {"code": code, "name": name}


class AuditLogs(TursoAPIStream[int]):
    """AuditLogs stream."""

    parent_stream_type = Organizations
    _page_size = 500

    name = "audit_logs"
    path = "/v1/organizations/{organization_name}/audit-logs"
    primary_keys = ()
    replication_key = "created_at"
    records_jsonpath = "$.audit_logs[*]"

    schema = th.PropertiesList(
        th.Property("author", th.StringType),
        th.Property("code", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("data", th.ObjectType()),
        th.Property("message", th.StringType),
        th.Property("origin", th.StringType),
    ).to_dict()

    def get_new_paginator(self) -> BasePageNumberPaginator:
        """Get a new paginator."""
        return BasePageNumberPaginator(1)

    def get_url_params(
        self,
        context: dict[str, t.Any] | None,
        next_page_token: int | None,
    ) -> dict[str, t.Any]:
        """Get URL query parameters."""
        params = super().get_url_params(context, next_page_token)
        params["page_size"] = self._page_size
        params["page"] = next_page_token

        return params
