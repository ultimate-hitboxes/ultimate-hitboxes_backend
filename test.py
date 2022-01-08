from run import app
import unittest

class Index(unittest.TestCase):
    def test_index(self):
        tester=app.test_client(self)
        response=tester.get("/")
        statuscode=response.status_code
        self.assertEquals(statuscode, 200)

    def test_index_content(self):
        tester=app.test_client(self)
        response=tester.get("/")
        print(response.content_type)
        self.assertEquals(response.content_type, "text/html; charset=utf-8")

class MoveData(unittest.TestCase):
    def dataContent(self):
        tester=app.test_client(self)
        response=tester.get("/api/move/MarioFThrow")
        self.assertTrue(b'character' in response.data)

if __name__ == "__main__":
    unittest.main()