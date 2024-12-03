import logging
import mimetypes
import re
from pathlib import Path

from config import Settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest, MediaIoBaseDownload

gdrive_fields = ",".join(
    [
        "id",
        "name",
        "mimeType",
        "description",
        "starred",
        "trashed",
        "explicitlyTrashed",
        "trashingUser",
        "trashedTime",
        "parents",
        "properties",
        "appProperties",
        "spaces",
        "version",
        "webContentLink",
        "webViewLink",
        "iconLink",
        "hasThumbnail",
        "thumbnailLink",
        "thumbnailVersion",
        "viewedByMe",
        "viewedByMeTime",
        "createdTime",
        "modifiedTime",
        "modifiedByMeTime",
        "modifiedByMe",
        "sharedWithMeTime",
        "sharingUser",
        "owners",
        "teamDriveId",
        "driveId",
        "lastModifyingUser",
        "shared",
        "ownedByMe",
        "capabilities",
        "viewersCanCopyContent",
        "copyRequiresWriterPermission",
        "writersCanShare",
        "permissions",
        "hasAugmentedPermissions",
        "folderColorRgb",
        "originalFilename",
        "fullFileExtension",
        "fileExtension",
        "md5Checksum",
        "size",
        "quotaBytesUsed",
        "headRevisionId",
        "contentHints",
        "imageMediaMetadata",
        "videoMediaMetadata",
        "isAppAuthorized",
    ]
)


def get_file_id(gdrive_url: str) -> str:
    return gdrive_url.split("/")[5]


def name_sanitizer(name: str) -> str:
    # Replace Unicode dashes (e.g., en dash, em dash, and others) with underscores
    # name = re.sub(r"[–—]", "_", name)

    # Remove characters not safe or meaningful in filenames, and replace spaces/hyphens with underscores
    sanitized = re.sub(r"[^a-zA-Z0-9_. \u0600-\u06FF]", "", name)

    # Replace spaces and hyphens with underscores
    sanitized = re.sub(r"[ \-]", "_", sanitized)

    # Remove multiple consecutive underscores
    sanitized = re.sub(r"_+", "_", sanitized)

    # Optionally, remove leading or trailing underscores
    sanitized = sanitized.strip("_")

    return sanitized


def g_credentials():
    scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    credentials = service_account.Credentials.from_service_account_file(
        Settings.base_dir / "gdrive.json", scopes=scopes
    )
    return credentials


def download(file_handler, request: HttpRequest):
    downloader = MediaIoBaseDownload(file_handler, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        logging.info(f"Download {int(status.progress() * 100)}% complete.")


# Function to download file from Google Drive
def download_google_drive_file(gdrive_url: str) -> Path:
    service = build("drive", "v3", credentials=g_credentials())
    request = service.files().get_media(fileId=get_file_id(gdrive_url))
    file_metadata = (
        service.files()
        .get(fileId=get_file_id(gdrive_url), fields=gdrive_fields)
        .execute()
    )
    filename = name_sanitizer(file_metadata.get("name"))
    ext = mimetypes.guess_extension(file_metadata.get("mimeType"))
    filename = f"{filename}{ext}"
    file_path = Settings.base_dir / filename

    with open(file_path, "wb") as fh:
        download(fh, request)
    logging.info("Download completed!")
    return file_path
