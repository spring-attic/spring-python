"""
   Copyright 2006-2008 SpringSource (http://springsource.com), All Rights Reserved

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       https://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.       
"""
import unittest
from springpython.security.userdetails import User
from springpython.security.userdetails import UserDetailsService

class UserDetailsInterfacesTestCase(unittest.TestCase):
    def testUserDetailsServiceInterface(self):
        user_details_service = UserDetailsService()
        self.assertRaises(NotImplementedError, user_details_service.load_user, None)
        
class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User("user1", "testPassword", True)
        
    def testUserString(self):
        self.assertTrue(str(self.user).startswith("Username: %s Password: [PROTECTED]" % self.user.username))
