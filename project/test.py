import unittest

class TestJWTAuthentication(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_login_no_auth(self):
        # Test login without authentication credentials
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 401)
    
    def test_login_bad_auth(self):
        # Test login with incorrect credentials
        headers = {
            'Authorization': 'Basic ' + b64encode(b"admin:wrongpassword").decode('utf-8')
        }
        response = self.app.get('/login', headers=headers)
        self.assertEqual(response.status_code, 401)
    
    def test_login_success(self):
        # Test successful login
        headers = {
            'Authorization': 'Basic ' + b64encode(b"admin:password").decode('utf-8')
        }
        response = self.app.get('/login', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)
    
    def test_protected_route_no_token(self):
        # Test access to a protected route without token
        response = self.app.get('/protected')
        self.assertEqual(response.status_code, 403)
    
    def test_protected_route_invalid_token(self):
        # Test access to a protected route with an invalid token
        headers = {'x-access-token': 'invalidToken'}
        response = self.app.get('/protected', headers=headers)
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()
