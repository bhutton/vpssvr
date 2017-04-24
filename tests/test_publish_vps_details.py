import unittest
import publish_vps_details

class TestPublicVPSDetails(unittest.TestCase):

    def test_get_and_return_ip_address(self):
        g = publish_vps_details.GetDetails()
        g.get_ip_address()
        assert(g.return_ip_address != '')

    def test_create_database_record(self):
        g = publish_vps_details.GetDetails()
        g.get_ip_address()
        g.create_database_entry()


if __name__ == '__main__':
    unittest.main()
