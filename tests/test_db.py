import unittest
import modules.database as database


class MyTestCase(unittest.TestCase):
    def test_mysqlite_connectivity(self):
        d = database.DatabaseNetwork()
        db = d.db_connection('sqlite')
        assert db == 'connection successful'

    def test_mysqlite_network_connectivity(self):
        d = database.DatabaseVPS()
        db = d.get_vps_details(1)
        print(db)

if __name__ == '__main__':
    unittest.main()
