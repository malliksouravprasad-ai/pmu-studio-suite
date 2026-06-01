"""
Google Integration Service — shared authentication and Google API operations.

Provides:
  - OAuth2 authentication (single credentials.json at PMU_Tools/credentials/)
  - Google Sheets: read, append, overwrite
  - Google Drive: upload, share, get link
  - Google Forms: create (delegates to app-level builders)

All apps should import auth and operations from here instead of implementing
their own credential flows.
"""
from __future__ import annotations
from pathlib import Path
from typing import Union

_CREDS_PATH = Path(__file__).parent.parent / "credentials" / "credentials.json"
_TOKEN_PATH = Path(__file__).parent.parent / "credentials" / "token.json"

SCOPES_SHEETS = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SCOPES_FORMS = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive",
]
SCOPES_ALL = list(set(SCOPES_SHEETS + SCOPES_FORMS))


# ── Authentication ────────────────────────────────────────────────────────────

def credentials_available() -> bool:
    """True if credentials.json exists at the shared credentials folder."""
    return _CREDS_PATH.exists()


def get_credentials(scopes: list[str] = None):
    """
    Return valid OAuth2 credentials.
    Opens browser for first-time authorization.
    Caches token in credentials/token.json.
    """
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    scopes = scopes or SCOPES_ALL
    creds = None

    if _TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(_TOKEN_PATH), scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(_CREDS_PATH), scopes)
            creds = flow.run_local_server(port=0)
        _TOKEN_PATH.write_text(creds.to_json())

    return creds


def build_service(api: str, version: str, scopes: list[str] = None):
    """Build and return a Google API service client."""
    from googleapiclient.discovery import build
    return build(api, version, credentials=get_credentials(scopes))


# ── Google Sheets ─────────────────────────────────────────────────────────────

def read_sheet(sheet_id_or_url: str, sheet_name: str = "Sheet1") -> "pd.DataFrame":
    """
    Read a Google Sheet into a pandas DataFrame.

    sheet_id_or_url: full URL or bare spreadsheet ID
    sheet_name:      tab name (default: Sheet1)
    """
    import pandas as pd

    sheet_id = _extract_sheet_id(sheet_id_or_url)
    svc = build_service("sheets", "v4", SCOPES_SHEETS)
    result = svc.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=sheet_name,
    ).execute()
    rows = result.get("values", [])
    if not rows:
        return pd.DataFrame()
    headers = rows[0]
    data = rows[1:]
    padded = [r + [""] * (len(headers) - len(r)) for r in data]
    return pd.DataFrame(padded, columns=headers)


def append_rows(sheet_id_or_url: str, sheet_name: str, rows: list[list]) -> int:
    """
    Append rows to a Google Sheet.
    rows: list of lists (each inner list = one row of values)
    Returns number of rows appended.
    """
    sheet_id = _extract_sheet_id(sheet_id_or_url)
    svc = build_service("sheets", "v4", SCOPES_SHEETS)
    body = {"values": rows}
    result = svc.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=sheet_name,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()
    return result.get("updates", {}).get("updatedRows", 0)


def clear_and_write(sheet_id_or_url: str, sheet_name: str, df) -> None:
    """
    Clear a Google Sheet tab and write a DataFrame to it (with headers).
    """
    sheet_id = _extract_sheet_id(sheet_id_or_url)
    svc = build_service("sheets", "v4", SCOPES_SHEETS)
    svc.spreadsheets().values().clear(
        spreadsheetId=sheet_id, range=sheet_name
    ).execute()
    rows = [df.columns.tolist()] + df.fillna("").values.tolist()
    svc.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"{sheet_name}!A1",
        valueInputOption="USER_ENTERED",
        body={"values": rows},
    ).execute()


def create_spreadsheet(title: str) -> dict:
    """
    Create a new blank Google Spreadsheet.
    Returns dict with 'sheet_id' and 'sheet_url'.
    """
    svc = build_service("sheets", "v4", SCOPES_SHEETS)
    result = svc.spreadsheets().create(body={"properties": {"title": title}}).execute()
    sheet_id = result["spreadsheetId"]
    return {
        "sheet_id": sheet_id,
        "sheet_url": f"https://docs.google.com/spreadsheets/d/{sheet_id}",
    }


# ── Google Drive ──────────────────────────────────────────────────────────────

def upload_to_drive(
    local_path: Union[str, Path],
    folder_id: str = None,
    filename: str = None,
) -> dict:
    """
    Upload a local file to Google Drive.
    Returns dict with 'file_id' and 'web_url'.
    """
    from googleapiclient.http import MediaFileUpload

    path = Path(local_path)
    name = filename or path.name
    mime = _mime_type(path.suffix)

    svc = build_service("drive", "v3", SCOPES_SHEETS)
    metadata = {"name": name}
    if folder_id:
        metadata["parents"] = [folder_id]

    media = MediaFileUpload(str(path), mimetype=mime, resumable=True)
    result = svc.files().create(
        body=metadata, media_body=media, fields="id, webViewLink"
    ).execute()
    return {"file_id": result["id"], "web_url": result.get("webViewLink", "")}


def share_file(file_id: str, email: str = None, role: str = "reader") -> None:
    """
    Share a Drive file. If email is None, makes it viewable by anyone with the link.
    role: 'reader' | 'commenter' | 'writer'
    """
    svc = build_service("drive", "v3", SCOPES_SHEETS)
    if email:
        svc.permissions().create(
            fileId=file_id,
            body={"type": "user", "role": role, "emailAddress": email},
        ).execute()
    else:
        svc.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": role},
        ).execute()


def get_file_link(file_id: str) -> str:
    """Return the webViewLink for a Drive file."""
    svc = build_service("drive", "v3", SCOPES_SHEETS)
    result = svc.files().get(fileId=file_id, fields="webViewLink").execute()
    return result.get("webViewLink", "")


# ── Google Forms ─────────────────────────────────────────────────────────────

def create_form(title: str, description: str = "") -> dict:
    """
    Create a new Google Form.
    Returns dict with form_id, edit_url, responder_url.
    """
    svc = build_service("forms", "v1", SCOPES_FORMS)
    body = {"info": {"title": title, "documentTitle": title}}
    form = svc.forms().create(body=body).execute()
    form_id = form["formId"]

    if description:
        svc.forms().batchUpdate(formId=form_id, body={
            "requests": [{
                "updateFormInfo": {
                    "info": {"description": description},
                    "updateMask": "description",
                }
            }]
        }).execute()

    return {
        "form_id":       form_id,
        "edit_url":      f"https://docs.google.com/forms/d/{form_id}/edit",
        "responder_url": form.get("responderUri", f"https://docs.google.com/forms/d/{form_id}/viewform"),
    }


def add_form_items(form_id: str, sections: list) -> None:
    """
    Add sections and questions to a Google Form.

    sections: list of dicts:
        {
            title:       str,
            description: str (optional),
            questions:   list of {type, title, required, choices, description}
        }

    question types: short_text | paragraph | number | date |
                    single_choice | multi_choice | dropdown | scale
    """
    svc = build_service("forms", "v1", SCOPES_FORMS)
    requests = []
    index    = 0

    for section in sections:
        # Page break = section header in Forms
        requests.append({
            "createItem": {
                "item": {
                    "title":       section.get("title", "Section"),
                    "description": section.get("description", ""),
                    "pageBreakItem": {},
                },
                "location": {"index": index},
            }
        })
        index += 1

        for q in section.get("questions", []):
            item = _build_question_item(q)
            requests.append({
                "createItem": {"item": item, "location": {"index": index}}
            })
            index += 1

    if requests:
        svc.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()


def get_form(form_id: str) -> dict:
    """Return the raw form metadata and item list from the Forms API."""
    svc = build_service("forms", "v1", SCOPES_FORMS)
    return svc.forms().get(formId=form_id).execute()


def get_form_responses(form_id: str) -> list:
    """
    Return all form responses as a list of dicts.
    Each dict maps question text → answer value.
    """
    svc = build_service("forms", "v1", SCOPES_FORMS)
    response = svc.forms().responses().list(formId=form_id).execute()
    raw_responses = response.get("responses", [])

    # Build a question index: questionId → title
    form_info = get_form(form_id)
    q_index   = {}
    for item in form_info.get("items", []):
        qi = item.get("questionItem", {}).get("question", {})
        if qi:
            q_index[qi.get("questionId", "")] = item.get("title", "")

    records = []
    for r in raw_responses:
        row = {"response_id": r.get("responseId", ""), "created_time": r.get("createTime", "")}
        for q_id, answer in r.get("answers", {}).items():
            title = q_index.get(q_id, q_id)
            tv    = answer.get("textAnswers", {}).get("answers", [])
            row[title] = "; ".join(a.get("value", "") for a in tv)
        records.append(row)
    return records


def _build_question_item(q: dict) -> dict:
    q_type   = q.get("type", "short_text")
    title    = q.get("title", "Question")
    required = q.get("required", False)
    choices  = q.get("choices", [])
    desc     = q.get("description", "")

    item = {"title": title}
    if desc:
        item["description"] = desc

    question = {"required": required}

    if q_type in ("short_text", "text", "number", "integer", "email"):
        question["textQuestion"] = {"paragraph": False}
    elif q_type == "paragraph":
        question["textQuestion"] = {"paragraph": True}
    elif q_type == "date":
        question["dateQuestion"] = {"includeTime": False, "includeYear": True}
    elif q_type == "single_choice":
        question["choiceQuestion"] = {
            "type": "RADIO",
            "options": [{"value": c} for c in choices] or [{"value": "Option 1"}],
        }
    elif q_type == "multi_choice":
        question["choiceQuestion"] = {
            "type": "CHECKBOX",
            "options": [{"value": c} for c in choices] or [{"value": "Option 1"}],
        }
    elif q_type == "dropdown":
        question["choiceQuestion"] = {
            "type": "DROP_DOWN",
            "options": [{"value": c} for c in choices] or [{"value": "Option 1"}],
        }
    elif q_type == "scale":
        question["scaleQuestion"] = {"low": 1, "high": 5, "lowLabel": "Poor", "highLabel": "Excellent"}
    else:
        question["textQuestion"] = {"paragraph": False}

    item["questionItem"] = {"question": question}
    return item


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_sheet_id(url_or_id: str) -> str:
    if "spreadsheets/d/" in url_or_id:
        return url_or_id.split("spreadsheets/d/")[1].split("/")[0]
    return url_or_id


def _mime_type(suffix: str) -> str:
    return {
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".pdf": "application/pdf",
        ".csv": "text/csv",
        ".json": "application/json",
    }.get(suffix.lower(), "application/octet-stream")
