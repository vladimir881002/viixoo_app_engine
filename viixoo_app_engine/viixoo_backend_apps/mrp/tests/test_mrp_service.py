import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from viixoo_core.app import app
from datetime import timedelta
import json
from mrp.services import security

client = TestClient(app)

class TestMrpEndpoints(unittest.TestCase):
    def setUp(self):
        self.valid_token = security.create_access_token(
                        1, expires_delta=timedelta(minutes=600)
                    )
        
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

if __name__ == '__main__':
    unittest.main()
