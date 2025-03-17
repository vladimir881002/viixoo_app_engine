from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Component(BaseModel):
    move_raw_id: int
    product: str
    quantity: float
    product_uom_qty: float


class Time(BaseModel):
    time_id: int
    employee_id: int
    employee: str
    duration: float
    date_start: str
    date_end: str
    loss: str


class WorkOrder(BaseModel):
    workorder_id: int
    name: str
    product: str
    workcenter: str
    production_state: str
    working_state: str
    is_user_working: bool
    quality_state: str | None
    test_type: str | None
    qty_production: float | None
    qty_produced: float | None
    qty_producing: float | None
    qty_remaining: float
    duration_expected: float
    duration: float | None
    state: str
    date_start: str
    date_finished: str | None
    url_document_instructions: str | None
    urls_plans: str | None
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

class ProductionOrders(BaseModel):
    data: list[ProductionOrder]
    count: int

class WorkOrders(BaseModel):
    data: list[WorkOrder]
    count: int

class ReasonLoss(BaseModel):
    label: str = Field(max_length=255)
    value: int

class ReasonsLoss(BaseModel):
    data: list[ReasonLoss]

class ChangeStateWorkOrder(BaseModel):
    workorder_id: int

class BlockWorkOrder(BaseModel):
    workorder_id: int
    loss_id: int
    description: str | None
