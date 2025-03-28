"""Model that defines the data models for the MRP application."""

from pydantic import BaseModel, Field


class Token(BaseModel):
    """Model for an access token."""

    access_token: str
    token_type: str = "bearer"


class Component(BaseModel):
    """Model for a component."""

    move_raw_id: int
    product: str
    quantity: float
    product_uom_qty: float
    picked: bool


class Time(BaseModel):
    """Model for time monitoring."""

    time_id: int
    employee_id: int
    employee: str
    duration: float
    date_start: str
    date_end: str
    loss: str


class WorkOrder(BaseModel):
    """Model for a work order."""

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
    state_value: str
    date_start: str
    date_finished: str | None
    url_document_instructions: str | None
    urls_plans: str | None
    time_ids: list["Time"]
    move_raw_ids: list["Component"] | None


class ProductionOrder(BaseModel):
    """Model for a production order."""

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
    """Model for an user."""

    full_name: str = Field(max_length=255)
    email: str | None = Field(max_length=255)


class UpdatePassword(BaseModel):
    """Model for update password."""

    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class Message(BaseModel):
    """Model for message."""

    message: str


class ProductionOrders(BaseModel):
    """Model for production orders."""

    data: list[ProductionOrder]
    count: int


class WorkOrders(BaseModel):
    """Model for work orders."""

    data: list[WorkOrder]
    count: int


class ReasonLoss(BaseModel):
    """Model for a reason loss."""

    label: str = Field(max_length=255)
    value: int


class Product(BaseModel):
    """Model for a product."""

    label: str = Field(max_length=255)
    value: int


class Products(BaseModel):
    """Model for products."""

    data: list[Product]


class ReasonsLoss(BaseModel):
    """Model for reasons loss."""

    data: list[ReasonLoss]


class ChangeStateWorkOrder(BaseModel):
    """Template for changing the order status."""

    workorder_id: int


class BlockWorkOrder(BaseModel):
    """Template for block the order status."""

    workorder_id: int
    loss_id: int
    description: str | None


class AddComponent(BaseModel):
    """Template for add component."""

    workorder_id: int
    product_id: int
    quantity: int


class ConsumeComponent(BaseModel):
    """Template for consume components."""

    move_raw_id: int
    consumed: bool
