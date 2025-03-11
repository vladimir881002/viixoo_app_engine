from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Component(BaseModel):
    producto: str
    quantity: float
    product_uom_qty: float


class Time(BaseModel):
    employee: str
    duration: float
    date_start: str
    date_end: str
    loss: str


class WorkOrder(BaseModel):
    name: str
    producto: str
    workcenter: str
    qty_production: float
    qty_produced: float
    qty_producing: float
    qty_remaining: float
    duration_expected: float
    duration: float
    state: str
    date_start: str
    date_finished: str
    url_document_instructions: str
    urls_plans: str
    time_ids: list["Time"]


class ProductionOrder(BaseModel):
    production_id: int
    name: str
    product: str
    product_qty: float | None
    date_start: str
    date_finished: str | None
    state: str
    bom: str | None
    workorder_ids: list["WorkOrder"] | None
    move_raw_ids: list["Component"] | None


class User(BaseModel):
    full_name: str = Field(max_length=255)
    email: str


class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class Message(BaseModel):
    message: str

class ProductionsOrder(BaseModel):
    data: list[ProductionOrder]
    count: int
