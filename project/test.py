import unittest

class TestJWTAuthentication(unittest.TestCase): #Ambrose
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

class SecurityCheckTests(teststhing): #Thomas

    def test_viewComments(self):
        #testing to see if XSS protection is working

        #one test with XSSesque script
        #normal comment check
        #check that all sanitation efforts are working

        #most important is XSS
        pass
   
    def test_addComments(self):
        #should be testing if someone is logged in and then
        # if comment is added, sanitised and logged who made it
        #aswell as for CRSF token checking
        
        #check if user is logged in
        #add a comment with valid input
        #add a comment thats too long or empty
        #add a comment that checks for validation / sanitising the input
        #check for a log of the comment
        #check for proper CSRF token

        #most important is validation and sanitation
        pass


    
    def test_deleteCommentAuthCheck(self):
        #check to see if an admin or commenter is attempting and check for CRSF token

        #check for user or admin
        #attempt to delete as a 'random' user / someone with no auth
        #check for the validation of the CSRF token

        #most important that 'random' user cannot delete
        pass
    
    def test_createAlbum(self):
        #should be testing if someone is logged in and then
        # if comment is added, sanitised and logged who made it
        #aswell as for CRSF token checking

        #check to see if user is logged in
        #create a 'valid' album
        #check for an 'invalid' album (name too long or empty) and proper validation
        #check for logging
        #check for valid CSRF token

        #most important is valid imput and sanitisation
        pass
    
    def test_addPhotoToAlbum(self):
        #check for auth and for CRSF token

        #attempt to add as owner
        #attempt to add as 'random-user'
        #check for CRSF token

        #most important that 'random' user cannot add
        pass


    def test_deleteAlbum(self):
        #check for auth of admin or album maker is attempting and check for CRSF token

        #attempt as owner / admin
        #attempt to add as 'random-user'
        #check for CSRF token
        #check for logging

        #most important is that 'random' user cannot delete
        pass

