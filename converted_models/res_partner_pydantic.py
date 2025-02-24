from PartnerCategoryModel import _get_default_color
from datetime import date
from enum import Enum
from pydantic import Field
from typing import Any, ForwardRef, List, Optional
from viixoo_core.models.postgres import PostgresModel

PartnerCategoryModel = ForwardRef('PartnerCategoryModel')
PartnerTitleModel = ForwardRef('PartnerTitleModel')
PartnerModel = ForwardRef('PartnerModel')
ResPartnerIndustryModel = ForwardRef('ResPartnerIndustryModel')



class PartnerCategoryModel(PostgresModel):
    """Partner Tags"""
    __description__ = "Partner Tags"
    __tablename__ = "res.partner.category"
    __order__ = "name"


    complete_name: Optional[str]
    name: str = Field(description="Tag Name")
    color: Optional[int] = Field(description="Color", default_factory=PartnerCategoryModel._get_default_color)
    parent_id: Optional[Optional[PartnerCategoryModel]] = Field(description="Parent Category")
    child_ids: List[PartnerCategoryModel] = Field(description="Child Tags", default_factory=list)
    active: Optional[bool]
    parent_path: Optional[str]
    partner_ids: List[PartnerModel] = Field(description="Partners", default_factory=list)


    @classmethod
    def _get_default_color(cls) -> int:
        '''
        TODO: Implement this default method
        This is a placeholder for the original Odoo method: _get_default_color
        '''
        # Original Odoo method name: _get_default_color
        # use as default for field color
        return None  # Replace with actual default value
        


class PartnerTitleModel(PostgresModel):
    """Partner Title"""
    __description__ = "Partner Title"
    __tablename__ = "res.partner.title"
    __order__ = "name"


    name: str = Field(description="Title")
    shortcut: Optional[str] = Field(description="Abbreviation")

class Partner_type_enum(str, Enum):
    CONTACT = "contact"  # Contact
    INVOICE = "invoice"  # Invoice Address
    DELIVERY = "delivery"  # Delivery Address
    OTHER = "other"  # Other Address


class PartnerModel(PostgresModel):
    """Contact"""
    __description__ = "Contact"
    __tablename__ = "res.partner"
    __order__ = "complete_name ASC, id DESC"


    name: Optional[str]
    complete_name: Optional[str]
    date: Optional[date]
    title: Optional[Optional[PartnerTitleModel]]
    parent_id: Optional[Optional[PartnerModel]] = Field(description="Related Company")
    parent_name: Optional[str] = Field(description="Parent name")
    child_ids: List[PartnerModel] = Field(description="Contact", default_factory=list)
    ref: Optional[str] = Field(description="Reference")
    lang: Optional[str] = Field(description="Language")
    active_lang_count: Optional[int]
    tz: Optional[str] = Field(description="Timezone", default_factory=None)
    tz_offset: Optional[str] = Field(description="Timezone offset")
    user_id: Optional[Optional[Any]] = Field(description="Salesperson")
    vat: Optional[str] = Field(description="Tax ID")
    same_vat_partner_id: Optional[Optional[PartnerModel]] = Field(description="Partner with same Tax ID")
    same_company_registry_partner_id: Optional[Optional[PartnerModel]] = Field(description="Partner with same Company Registry")
    company_registry: Optional[str] = Field(description="Company ID")
    bank_ids: List[Any] = Field(description="Banks", default_factory=list)
    website: Optional[str]
    comment: Optional[str] = Field(description="Notes")
    category_id: List[PartnerCategoryModel] = Field(description="Tags", default_factory=list)
    active: Optional[bool]
    employee: Optional[bool]
    function: Optional[str] = Field(description="Job Position")
    type: Optional[Partner_type_enum] = Field(description="Address Type")
    street: Optional[str]
    street2: Optional[str]
    zip: Optional[str]
    city: Optional[str]
    state_id: Optional[Optional[Any]] = Field(description="State")
    country_id: Optional[Optional[Any]] = Field(description="Country")
    country_code: Optional[str] = Field(description="Country Code")
    partner_latitude: Optional[float] = Field(description="Geo Latitude")
    partner_longitude: Optional[float] = Field(description="Geo Longitude")
    email: Optional[str]
    email_formatted: Optional[str]
    phone: Optional[str]
    mobile: Optional[str]
    is_company: Optional[bool] = Field(description="Is a Company")
    is_public: Optional[bool]
    industry_id: Optional[Optional[ResPartnerIndustryModel]]
    company_type: Optional[Any] = Field(description="Company Type")
    company_id: Optional[Optional[Any]]
    color: Optional[int] = Field(description="Color Index")
    user_ids: List[Any] = Field(description="Users", default_factory=list)
    partner_share: Optional[bool]
    contact_address: Optional[str] = Field(description="Complete Address")
    commercial_partner_id: Optional[Optional[PartnerModel]] = Field(description="Commercial Entity")
    commercial_company_name: Optional[str]
    company_name: Optional[str]
    barcode: Optional[str]
    self: Optional[Any]


    @classmethod
    def _default_category(cls) -> Any:
        '''
        TODO: Implement this default method
        This is a placeholder for the original Odoo method: _default_category
        '''
        # Original Odoo method name: _default_category
        # use as default for field category_id
        return None  # Replace with actual default value
        


class ResPartnerIndustryModel(PostgresModel):
    """Industry"""
    __description__ = "Industry"
    __tablename__ = "res.partner.industry"
    __order__ = "name"


    name: Optional[str]
    full_name: Optional[str]
    active: Optional[bool]

# Update forward references
PartnerCategoryModel.update_forward_refs()
PartnerTitleModel.update_forward_refs()
PartnerModel.update_forward_refs()
ResPartnerIndustryModel.update_forward_refs()
