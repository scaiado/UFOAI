from pydantic import BaseModel


class UAPRecord(BaseModel):
    title: str
    file_type: str
    description: str
    agency: str
    incident_date: str
    incident_location: str
    release_date: str
    document_url: str | None = None
    thumbnail_url: str | None = None
    modal_images: list[str] = []
    dvids_video_ids: list[str] = []
    video_pairing: str | None = None
    pdf_pairing: str | None = None
    video_title: str | None = None
    redacted: bool = False
    source: str = "war.gov"
    local_path: str | None = None
    video_urls: list[str] = []


class ProcessedChunk(BaseModel):
    source_file: str
    chunk_index: int
    text: str
    chunk_type: str
    agency: str = ""
    incident_date: str = ""
    incident_location: str = ""
    title: str = ""
    description: str = ""
