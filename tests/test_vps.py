import unittest
import modules.vps as vps


class MyTestCase(unittest.TestCase):

    def test_update_vps_gets_different_virtio(self):
        v = vps.VMFunctions()
        v.update_vps(878)
        self.assertEqual(4, v.interface)
        v.generate_bhyve_commands()

    def test_disk_number(self):
        v = vps.VMFunctions()
        v.update_vps(878)
        self.assertEqual(3, v.disk_number)


if __name__ == '__main__':
    unittest.main()
