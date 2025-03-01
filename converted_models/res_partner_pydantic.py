from datetime import date
from enum import Enum
from pydantic import Field
from typing import Any, ForwardRef, List, Optional
from viixoo_core.models.postgres import PostgresModel

FormatAddressMixinModel = ForwardRef('FormatAddressMixinModel')
PartnerCategoryModel = ForwardRef('PartnerCategoryModel')
PartnerTitleModel = ForwardRef('PartnerTitleModel')
PartnerModel = ForwardRef('PartnerModel')
ResPartnerIndustryModel = ForwardRef('ResPartnerIndustryModel')



class FormatAddressMixinModel(PostgresModel):
    """Address Format"""
    __description__ = "Address Format"
    __tablename__ = "format_address_mixin"




class PartnerCategoryModel(PostgresModel):
    """Partner Tags"""
    __description__ = "Partner Tags"
    __tablename__ = "res_partner_category"
    __order__ = "name"


    _complete_name: str
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
        

    class Config:
        underscore_attrs_are_private = True


    @property
    def complete_name(self) -> str:
        '''
        Computed field from Odoo method: _compute_display_name
        '''
        pass

    @complete_name.setter
    def complete_name(self, value: str) -> None:
        self._complete_name = value


class PartnerTitleModel(PostgresModel):
    """Partner Title"""
    __description__ = "Partner Title"
    __tablename__ = "res_partner_title"
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
    __tablename__ = "res_partner"
    __order__ = "complete_name ASC, id DESC"


    name: Optional[str]
    _complete_name: str
    date: Optional[date]
    title: Optional[Optional[PartnerTitleModel]]
    parent_id: Optional[Optional[PartnerModel]] = Field(description="Related Company")
    parent_name: Optional[str] = Field(description="Parent name")
    child_ids: List[PartnerModel] = Field(description="Contact", default_factory=list)
    ref: Optional[str] = Field(description="Reference")
    lang: Optional[str] = Field(description="Language")
    tz: Optional[str] = Field(description="Timezone", default_factory=None)
    _user_id: Optional[Any] = Field(description="Salesperson")
    vat: Optional[str] = Field(description="Tax ID")
    _company_registry: str = Field(description="Company ID")
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
    phone: Optional[str]
    mobile: Optional[str]
    is_company: Optional[bool] = Field(description="Is a Company")
    industry_id: Optional[Optional[ResPartnerIndustryModel]]
    company_id: Optional[Optional[Any]]
    color: Optional[int] = Field(description="Color Index")
    user_ids: List[Any] = Field(description="Users", default_factory=list)
    _partner_share: bool
    _commercial_partner_id: Optional[PartnerModel] = Field(description="Commercial Entity")
    _commercial_company_name: str
    company_name: Optional[str]
    barcode: Optional[str]


    @classmethod
    def _default_category(cls) -> Any:
        '''
        TODO: Implement this default method
        This is a placeholder for the original Odoo method: _default_category
        '''
        # Original Odoo method name: _default_category
        # use as default for field category_id
        return None  # Replace with actual default value
        

    class Config:
        underscore_attrs_are_private = True


    @property
    def complete_name(self) -> str:
        '''
        Computed field from Odoo method: _compute_complete_name
        '''
        pass

    @complete_name.setter
    def complete_name(self, value: str) -> None:
        self._complete_name = value

    @property
    def active_lang_count(self) -> int:
        '''
        Computed field from Odoo method: _compute_active_lang_count
        '''
        pass

    @property
    def tz_offset(self) -> str:
        '''
        Computed field from Odoo method: _compute_tz_offset
        '''
        pass

    @property
    def user_id(self) -> Optional[Any]:
        '''
        Computed field from Odoo method: _compute_user_id
        '''
        pass

    @user_id.setter
    def user_id(self, value: Optional[Any]) -> None:
        self._user_id = value

    @property
    def same_vat_partner_id(self) -> Optional[PartnerModel]:
        '''
        Computed field from Odoo method: _compute_same_vat_partner_id
        '''
        pass

    @property
    def same_company_registry_partner_id(self) -> Optional[PartnerModel]:
        '''
        Computed field from Odoo method: _compute_same_vat_partner_id
        '''
        pass

    @property
    def company_registry(self) -> str:
        '''
        Computed field from Odoo method: _compute_company_registry
        '''
        pass

    @company_registry.setter
    def company_registry(self, value: str) -> None:
        self._company_registry = value

    @property
    def email_formatted(self) -> str:
        '''
        Computed field from Odoo method: _compute_email_formatted
        '''
        pass

    @property
    def is_public(self) -> bool:
        '''
        Computed field from Odoo method: _compute_is_public
        '''
        pass

    @property
    def company_type(self) -> Any:
        '''
        Computed field from Odoo method: _compute_company_type
        '''
        pass

    @property
    def partner_share(self) -> bool:
        '''
        Computed field from Odoo method: _compute_partner_share
        '''
        pass

    @partner_share.setter
    def partner_share(self, value: bool) -> None:
        self._partner_share = value

    @property
    def contact_address(self) -> str:
        '''
        Computed field from Odoo method: _compute_contact_address
        '''
        pass

    @property
    def commercial_partner_id(self) -> Optional[PartnerModel]:
        '''
        Computed field from Odoo method: _compute_commercial_partner
        '''
        pass

    @commercial_partner_id.setter
    def commercial_partner_id(self, value: Optional[PartnerModel]) -> None:
        self._commercial_partner_id = value

    @property
    def commercial_company_name(self) -> str:
        '''
        Computed field from Odoo method: _compute_commercial_company_name
        '''
        pass

    @commercial_company_name.setter
    def commercial_company_name(self, value: str) -> None:
        self._commercial_company_name = value

    @property
    def self(self) -> Any:
        '''
        Computed field from Odoo method: _compute_get_ids
        '''
        pass


class ResPartnerIndustryModel(PostgresModel):
    """Industry"""
    __description__ = "Industry"
    __tablename__ = "res_partner_industry"
    __order__ = "name"


    name: Optional[str]
    full_name: Optional[str]
    active: Optional[bool]

# Update forward references
FormatAddressMixinModel.update_forward_refs()
PartnerCategoryModel.update_forward_refs()
PartnerTitleModel.update_forward_refs()
PartnerModel.update_forward_refs()
ResPartnerIndustryModel.update_forward_refs()
