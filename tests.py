import unittest
import server
import utilities
import doctest


def load_tests(loader, tests, ignore):
    """Also run our doctests and file-based doctests."""

    tests.addTests(doctest.DocTestSuite(server))
    # tests.addTests(doctest.DocFileSuite("tests.txt"))
    return tests


class UtilitiesParserFunctionsTestCase(unittest.TestCase):

    def test_to_clean_string_from_input(self):

        # Case for string already clean
        test_in = 'foo13ar'
        expect_out = 'foo13ar'
        self.assertEqual(utilities.to_clean_string_from_input(test_in, 100),
                         expect_out)

        # Case for string not clean
        test_in = 'fo*o13!ar; droptables'
        expect_out = 'foo13ardroptables'
        self.assertEqual(utilities.to_clean_string_from_input(test_in, 100),
                         expect_out)

        # Case for string only unclean
        test_in = '&*#%;+'
        self.assertIsNone(utilities.to_clean_string_from_input(test_in, 100))

        # Case for string empty
        test_in = ''
        self.assertIsNone(utilities.to_clean_string_from_input(test_in, 100))

        # Case for string unclean and too long
        test_in = 'fo*o13!ar; droptables'
        expect_out = 'foo'
        self.assertEqual(utilities.to_clean_string_from_input(test_in, 3),
                         expect_out)

    def test_to_float_from_input(self):

        # Case for spaces
        test_in = '  13 '
        expect_out = 13.0
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for other characters arround
        test_in = 'foo13*ar'
        expect_out = 13.0
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for decimals
        test_in = '13.14'
        expect_out = 13.14
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for zero pad
        test_in = '00013'
        expect_out = 13.0
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for empty
        test_in = ''
        self.assertIsNone(utilities.to_float_from_input(test_in))

        # Case for all unclean
        test_in = 'juihiuhr&&*@'
        self.assertIsNone(utilities.to_float_from_input(test_in))

        # Case for negative
        test_in = '-13.0 '
        expect_out = -13.0
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for fractional
        test_in = '0.13'
        expect_out = 0.13
        self.assertEqual(utilities.to_float_from_input(test_in),
                         expect_out)

        # Case for zero
        test_in = '-0.0 '
        expect_out = 0.0
        self.assertAlmostEqual(utilities.to_float_from_input(test_in),
                               expect_out)


class ServerRoutesTestCase(unittest.TestCase):

    def setUp(self):
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True

    def test_navigation_logged_out(self):

        result = self.client.get('/navigation')
        self.assertIn('Galleries', result.data)
        self.assertIn('Walls', result.data)
        self.assertNotIn('Curate', result.data)
        self.assertNotIn('Upload', result.data)

    # def test_navigation_logged_in(self):

    #     server.app.session['user_id'] = 13
    #     server.app.session['username'] = 'foo'

    #     result = self.client.get('/navigation')
    #     self.assertIn('Galleries', result.data)
    #     self.assertIn('Walls', result.data)
    #     self.assertNotIn('Curate', result.data)
    #     self.assertNotIn('Upload', result.data)


    # def navigations while not logged in

    # tear down by logging out

if __name__ == "__main__":
    unittest.main()
