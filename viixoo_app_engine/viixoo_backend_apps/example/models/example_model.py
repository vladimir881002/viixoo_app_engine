from datetime import datetime, date
from viixoo_core.models.postgres import PostgresModel
from pydantic import Field
from typing import Optional, Annotated as Ann
from dataclasses import field


class ExampleModel(PostgresModel):
    """Modelo de ejemplo usando PostgreSQL."""

    __tablename__ = "example"  # Define la tabla en PostgreSQL

    id: int = Field(json_schema_extra=dict(primary_key=True))
    name: str    
    extra_field: int
    is_float: Optional[float] = None
    is_bool: Optional[bool] = None
    is_date: Optional[date] = None
    is_datetime: Optional[datetime] = None
    str_field: Optional[str] = Field(max_length=255, default_factory=lambda: None, json_schema_extra=dict(track_changes=True))
    str_unique_field: Optional[str] = Field(max_length=255, default_factory=lambda: None, json_schema_extra=dict(unique=True))
    str_default_field: Optional[str] = Field(default="default_value")
    foreign_key: Optional[int] = Field( default_factory=lambda: None, json_schema_extra=dict(foreign_key="example(id)", on_delete="SET NULL", on_update="CASCADE"))
