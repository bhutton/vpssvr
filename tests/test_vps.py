import unittest
import modules.vps as vps


class MyTestCase(unittest.TestCase):

    def test_disk_number(self):
        v = vps.VMFunctions()
        v.update_vps(878)
        self.assertEqual(3, v.disk_number)

    def test_interface_number(self):
        v = vps.VMFunctions()
        v.update_vps(878)
        self.assertEqual(2, v.interface_number)


if __name__ == '__main__':
    unittest.main()
