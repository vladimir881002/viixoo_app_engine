import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from viixoo_core.app import app
from datetime import timedelta
import json
import random
import string
from mrp.services import security

client = TestClient(app)

class TestMrpEndpoints(unittest.TestCase):
    def setUp(self):
        self.valid_token = security.create_access_token(
                        1, expires_delta=timedelta(minutes=600)
                    )
        self.work_order = {
            "workorder_id": 1,
            "name": "op1",
            "product": "prod1",
            "workcenter": "workcenter1",
            "production_state": "done",
            "working_state": "done",
            "is_user_working": True,
            "quality_state": "state1",
            "test_type": "type1",
            "qty_production": None,
            "qty_produced": None,
            "qty_producing": None,
            "qty_remaining": 10,
            "duration_expected": 10,
            "duration": None,
            'state': 'ready',
            'date_start': "2025-03-12 01:47:56",
            "date_finished": None,
            "url_document_instructions": "",
            "urls_plans": "",
            "time_ids": []
            }
        
    @patch('requests.post')
    def test_authenticate_user_success(self, mock_post):
        mock_response = type('MockResponse', (), {'text': '{"employee": {"id": 1}}'})
        mock_post.return_value = mock_response

        response = client.post(
            "/login/access-token",
            data={"username": "test", "password": "valid"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

    @patch('requests.post')
    def test_authenticate_user_invalid_credentials(self, mock_post):
        mock_post.side_effect = Exception("Simulated error")
        
        response = client.post(
            "/login/access-token",
            data={"username": "test", "password": "wrong"}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Usuario o contraseña incorrecto", response.json()["detail"])

    @patch('requests.get')
    def test_get_user_success(self, mock_get):
        mock_get.return_value.text = '{"employee": {"name": "Test User", "email": "test@example.com"}}'
        
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {self.valid_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["full_name"], "Test User")

    @patch('requests.get')
    def test_get_production_orders(self, mock_get):
        mock_data = {
            "status": "success",
            "production_order_ids": [{
                    'production_id': 1,
                    'name': 'test',
                    'product': 'product test',
                    'state': 'confirmed',
                    'date_start': "2025-03-12 01:47:56",
                    'product_qty': 1,
                    'date_finished': "",
                    'bom': "",
                    'workorder_ids': [],
                    'move_raw_ids': [],
                }],
            "count": 1
        }
        mock_get.return_value.text = json.dumps(mock_data)
        
        response = client.get(
            "/production-orders/?skip=0&limit=3",
            headers={"Authorization": f"Bearer {self.valid_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 1)
        self.assertEqual(response.json()["count"], 1)

    def test_invalid_token_handling(self):
        response = client.get(
            "/users/me/",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Usuario no encontrado", response.json()["detail"])

    @patch('requests.get')
    def test_get_workorders(self, mock_get):
        mock_data = {
            "status": "success",
            "workorder_ids": [self.work_order],
            "count": 1
        }
        mock_get.return_value.text = json.dumps(mock_data)
        
        response = client.get(
            "/work-orders/?skip=0&limit=3",
            headers={"Authorization": f"Bearer {self.valid_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 1)
        self.assertEqual(response.json()["count"], 1)

    @patch('requests.post')
    @patch('jwt.decode')
    def test_start_workorder_success(self, mock_jwt_decode, mock_post):
        mock_data = {
            "status": "success"
        }
        mock_post.return_value.text = json.dumps(mock_data)
        mock_jwt_decode.return_value = {"sub": "employee_id_1"}
        
        response = client.patch(
            "/workorder/start",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json={"workorder_id": 1}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), "Orden de trabajo iniciada satisfactoriamente")

    @patch('requests.post')
    @patch('jwt.decode')
    def test_start_workorder_odoo_failure(self, mock_jwt_decode, mock_post):
        mock_post.side_effect = Exception("Simulated error")
        mock_jwt_decode.return_value = {"sub": "employee_id_1"}
        
        response = client.patch(
            "/workorder/start",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json={"workorder_id": 1}
        )
        self.assertEqual(response.status_code, 400)

    @patch('requests.post')
    @patch('jwt.decode')
    def test_pause_workorder_success(self, mock_jwt_decode, mock_post):
        mock_data = {
            "status": "success"
        }
        mock_post.return_value.text = json.dumps(mock_data)
        mock_jwt_decode.return_value = {"sub": "employee_id_1"}
        
        response = client.patch(
            "/workorder/pause",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json={"workorder_id": 1}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), "Orden de trabajo pausada satisfactoriamente")

    @patch('requests.post')
    @patch('jwt.decode')
    def test_pause_workorder_odoo_failure(self, mock_jwt_decode, mock_post):
        mock_post.side_effect = Exception("Simulated error")
        mock_jwt_decode.return_value = {"sub": "employee_id_1"}
        
        response = client.patch(
            "/workorder/pause",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json={"workorder_id": 1}
        )
        self.assertEqual(response.status_code, 400)

    @patch('requests.post')
    @patch('jwt.decode')
    def test_finish_workorder_success(self, mock_jwt_decode, mock_post):
        mock_data = {
            "status": "success"
        }
        mock_post.return_value.text = json.dumps(mock_data)
        mock_jwt_decode.return_value = {"sub": "employee_id_1"}
        
        response = client.patch(
            "/workorder/finish",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json={"workorder_id": 1}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), "Orden de trabajo finalizada satisfactoriamente")

    @patch('requests.post')
    @patch('jwt.decode')
    def test_finish_workorder_odoo_failure(self, mock_jwt_decode, mock_post):
        mock_post.side_effect = Exception("Simulated error")
        mock_jwt_decode.return_value = {"sub": "employee_id_1"}
        
        response = client.patch(
            "/workorder/finish",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json={"workorder_id": 1}
        )
        self.assertEqual(response.status_code, 400)

    @patch('requests.post')
    @patch('jwt.decode')
    def test_unblock_workorder_success(self, mock_jwt_decode, mock_post):
        mock_data = {
            "status": "success"
        }
        mock_post.return_value.text = json.dumps(mock_data)
        mock_jwt_decode.return_value = {"sub": "employee_id_1"}
        
        response = client.patch(
            "/workorder/unblock",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json={"workorder_id": 1}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), "Orden de trabajo desbloqueada satisfactoriamente")

    @patch('requests.post')
    @patch('jwt.decode')
    def test_unblock_workorder_odoo_failure(self, mock_jwt_decode, mock_post):
        mock_post.side_effect = Exception("Simulated error")
        mock_jwt_decode.return_value = {"sub": "employee_id_1"}
        
        response = client.patch(
            "/workorder/unblock",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json={"workorder_id": 1}
        )
        self.assertEqual(response.status_code, 400)

    @patch('requests.post')
    @patch('jwt.decode')
    def test_block_workorder_success(self, mock_jwt_decode, mock_post):
        mock_data = {
            "status": "success"
        }
        mock_post.return_value.text = json.dumps(mock_data)
        mock_jwt_decode.return_value = {"sub": "employee_id_1"}
        
        response = client.patch(
            "/workorder/block",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json={"workorder_id": 1, "loss_id": 1, "description": ""}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), "Orden de trabajo bloqueada satisfactoriamente")

    @patch('requests.post')
    @patch('jwt.decode')
    def test_block_workorder_odoo_failure(self, mock_jwt_decode, mock_post):
        mock_post.side_effect = Exception("Simulated error")
        mock_jwt_decode.return_value = {"sub": "employee_id_1"}
        
        response = client.patch(
            "/workorder/block",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json={"workorder_id": 1, "loss_id": 1, "description": ""}
        )
        self.assertEqual(response.status_code, 400)

    @patch('requests.get')
    def test_get_reasons_loss(self, mock_get):
        mock_data = {
            "status": "success",
            "loss_ids": [{'value':1, 'label':'loss test'}]
        }
        mock_get.return_value.text = json.dumps(mock_data)
        
        response = client.get(
            "/reasons-loss",
            headers={"Authorization": f"Bearer {self.valid_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 1)

    @patch('requests.post')
    @patch('jwt.decode')
    def test_reset_password_failure(self, mock_jwt_decode, mock_post):
        mock_post.side_effect = Exception("Simulated error")
        mock_jwt_decode.return_value = {"sub": "employee_id_1"}
        
        response = client.patch(
            "/users/me/password",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json={"new_password": self.generate_test_password(), "current_password": self.generate_test_password()}
        )
        self.assertEqual(response.status_code, 400)

    @patch('requests.post')
    @patch('jwt.decode')
    def test_reset_password_success(self, mock_jwt_decode, mock_post):
        mock_data = {
            "status": "success"
        }
        mock_post.return_value.text = json.dumps(mock_data)
        mock_jwt_decode.return_value = {"sub": "employee_id_1"}
        
        response = client.patch(
            "/users/me/password",
            headers={"Authorization": f"Bearer {self.valid_token}"},
            json={"new_password": self.generate_test_password(), "current_password": self.generate_test_password()}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), "Contraseña cambiada satisfactoriamente")

    def generate_test_password(self):
        characters = string.ascii_letters + string.digits        
        password = ''.join(random.choice(characters) for _ in range(15))     
        return password


if __name__ == '__main__':
    unittest.main()
