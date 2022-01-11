from run import app
import unittest

def test_status_code(self, route, code):
    tester=app.test_client(self)
    response=tester.get(route)
    statuscode=response.status_code
    self.assertEquals(statuscode, code)

def test_content_type(self, route, type):
    tester=app.test_client(self)
    response=tester.get(route)
    print(response.content_type)
    self.assertEquals(response.content_type, type)
class Index(unittest.TestCase):
    def test_index(self):
        test_status_code(self, "/", 200)

    def test_index_content(self):
        test_content_type(self, "/", "text/html; charset=utf-8")

class CharacterData(unittest.TestCase):
    def test_character_data_status(self):
        test_status_code(self, "/api/character/mario", 200)

    def test_all_character_data_status(self):
        test_status_code(self, "/api/character/all", 200)

    def test_include_exclude_character_status_failure(self):
        test_status_code(self, "/api/character/mario?include=test&exclude=test", 400)

    def test_include_exclude_all_character_status_failure(self):
        test_status_code(self, "/api/character/all?include=test&exclude=test", 400)

    def test_character_data_content(self):
        test_content_type(self, "/api/character/mario", "application/json")

    def test_all_character_data_content(self):
        test_content_type(self, "/api/character/all", "application/json")
if __name__ == "__main__":
    unittest.main()
