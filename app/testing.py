import app
import unittest


class BasicTestCase(unittest.TestCase):

	def testing(self):
		self.assertEqual(app.testing("user"), 4)

if __name__ == '__main__':
    unittest.main()