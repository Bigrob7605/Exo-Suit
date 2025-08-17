import unittest
from SampleClass import *

class TestSAMPLECLASS (unittest.TestCase):
    def setUp(self):
        pass
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        self.assertTrue(True)  # Placeholder test
        
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
