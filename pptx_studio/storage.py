"""Supabase Storage uploads for generated presentation artifacts."""

from __future__ import annotations

import os
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

BUCKET_NAME = "files"
PPTX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


def storage_is_configured() -> bool:
    """Return whether the required Supabase Storage credentials are present."""
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))


def upload_presentation(content: bytes, storage_path: str) -> str:
    """Upload one PPTX to the private `files` bucket and return its object path."""
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_role_key:
        raise RuntimeError(
            "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY to upload presentations."
        )

    encoded_path = "/".join(quote(segment, safe="") for segment in storage_path.split("/"))
    request = Request(
        f"{supabase_url.rstrip('/')}/storage/v1/object/{BUCKET_NAME}/{encoded_path}",
        data=content,
        headers={
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": PPTX_CONTENT_TYPE,
            "x-upsert": "false",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=60) as response:
            if response.status not in (200, 201):
                raise RuntimeError(f"Supabase Storage returned HTTP {response.status}.")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Supabase Storage upload failed (HTTP {exc.code}): {detail}") from exc
    return storage_path