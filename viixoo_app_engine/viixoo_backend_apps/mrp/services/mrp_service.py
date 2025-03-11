from datetime import timedelta
from ..models.models import Token, User, UpdatePassword, Message, ProductionsOrder
from typing import Any
import requests
import logging
import json
import jwt
import secrets
from viixoo_core.services.base_service import BaseService
from fastapi import Depends, HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from . import security

_logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/login/access-token"
)
SECRET_KEY = security.SECRET_KEY
URL_ODOO = "http://127.0.0.1:8017"
TOKEN_ODOO = "sdgsd324erfdfgwe4erew-fdgs5434fgr2@sda-dsfsdfsf#"

class MrpService(BaseService):
    def __init__(self):        
        super().__init__("mrp")

    def authenticate_user(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
        headers = {
            "Auth-Token": TOKEN_ODOO,
            "Content-Type": "application/json",
        }
        try:
            
            odoo_response = requests.post(
                URL_ODOO+"/hemago/authenticate_user/",
                headers=headers,
                data=json.dumps({"user_login": form_data.username, "password": form_data.password}),
                verify=True,
                timeout=100,
            )
        except Exception as e:
            error_str = str(e)
            _logger.error("Ha ocurrido un error al enviar la solicitud a Odoo")
            _logger.error(error_str)
            raise HTTPException(status_code=400, detail="Usuario o contraseña incorrecto")
        else:
            response = json.loads(odoo_response.text)
            if response.get("employee"):
                employee = response["employee"]
                access_token_expires = timedelta(minutes=600)
                return Token(
                        access_token=security.create_access_token(
                        employee['id'], expires_delta=access_token_expires
                    )
                )
            else:
                raise HTTPException(status_code=400, detail="Usuario o contraseña incorrecto")
            
    def get_user(self, token: Annotated[str, Depends(reusable_oauth2)]) -> User:
        headers = {
            "Auth-Token": TOKEN_ODOO,
            "Content-Type": "application/json",
        }
        try:
            payload = jwt.decode(
                token, SECRET_KEY, algorithms=[security.ALGORITHM]
            )
            odoo_response = requests.get(
                URL_ODOO+"/hemago/get_employee/",
                headers=headers,
                data=json.dumps({"employee_id": payload.get("sub")}),
                verify=True,
                timeout=100,
            )
        except Exception as e:
            error_str = str(e)
            _logger.error("Ha ocurrido un error al enviar la solicitud a Odoo")
            _logger.error(error_str)
            raise HTTPException(status_code=400, detail="Usuario no encontrado")
        else:
            response = json.loads(odoo_response.text)
            if response.get("employee"):
                employee = response["employee"]
                return User(
                        full_name=employee["name"],
                        email=employee["email"]
                    )
            
    def reset_password(self, token: Annotated[str, Depends(reusable_oauth2)], body: UpdatePassword) -> Any:
        headers = {
            "Auth-Token": TOKEN_ODOO,
            "Content-Type": "application/json",
        }
        try:
            payload = jwt.decode(
                token, SECRET_KEY, algorithms=[security.ALGORITHM]
            )
            data = {"employee_id": payload.get("sub"), "new_password": body.new_password, "current_password": body.current_password}
            odoo_response = requests.post(
                URL_ODOO+"/hemago/reset_password/",
                headers=headers,
                data=json.dumps(data),
                verify=True,
                timeout=100,
            )
        except Exception as e:
            error_str = str(e)
            _logger.error("Ha ocurrido un error al enviar la solicitud a Odoo")
            _logger.error(error_str)
            raise HTTPException(status_code=400, detail="Usuario no encontrado")
        else:
            response = json.loads(odoo_response.text)
            if response.get("status") == "success":
                return Message(message="Contraseña cambiada satisfactoriamente")
            else:
                raise HTTPException(status_code=500, detail="Acceso denegado")
            
    def get_production_orders(self, token: Annotated[str, Depends(reusable_oauth2)], skip: int = 0, limit: int = 100
        ) -> Any:
        headers = {
            "Auth-Token": TOKEN_ODOO,
            "Content-Type": "application/json",
        }
        try:
            payload = jwt.decode(
                token, SECRET_KEY, algorithms=[security.ALGORITHM]
            )
            data = {"employee_id": payload.get("sub"), "start": skip, "limit": limit}
            odoo_response = requests.get(
                URL_ODOO+"/hemago/get_production_order/",
                headers=headers,
                data=json.dumps(data),
                verify=True,
                timeout=100,
            )
        except Exception as e:
            error_str = str(e)
            _logger.error("Ha ocurrido un error al enviar la solicitud a Odoo")
            _logger.error(error_str)
            raise HTTPException(status_code=400, detail="Ha ocurrido un error al enviar la solicitud a Odoo")
        else:
            response = json.loads(odoo_response.text)
            if response.get("status") == "success":
                return ProductionsOrder(data=response.get("production_order_ids"), count=response.get("count"))
            else:
                raise HTTPException(status_code=500)
