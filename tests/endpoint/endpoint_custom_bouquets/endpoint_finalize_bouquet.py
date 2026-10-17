from tests.endpoint.endpoint_custom_bouquets.support import BouquetEndpointCase

class FinalizeBouquetTests(BouquetEndpointCase):
    def test_finalized_immutable_override_archive_and_reprice_duplicate(self):
        row=self.create_bouquet()
        url=f"/bouquet-test/custom-bouquets/{row['id']}"
        self.assertEqual(self.client.post(url+"/finalize",json={"final_price":1,"reason":"Deal"}).status_code,403)
        self.login_as("superadmin")
        self.assertEqual(self.client.post(url+"/finalize",json={"final_price":1}).status_code,422)
        response=self.client.post(url+"/finalize",json={"final_price":1,"reason":"Deal"})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["estimated_hpp"],"54.00000000")
        self.assertEqual(self.client.put(url,json=self.payload).status_code,409)
        from sqlalchemy.orm import Session
        from models.flower_model import Flower
        from uuid import UUID
        with Session(self.engine) as db:
            db.get(Flower,UUID(self.flower_id)).selling_price=20000
            db.commit()
        copied=self.client.post(url+"/duplicate")
        self.assertEqual(copied.status_code,201,copied.text)
        self.assertEqual(copied.json()["proposed_price"],60000)
        self.assertIsNone(copied.json()["final_price"])
        self.assertEqual(self.client.post(url+"/archive").status_code,200)
        self.assertEqual(self.client.get(url).json()["final_price"],1)

    def test_empty_draft_cannot_finalize(self):
        row=self.client.post("/bouquet-test/custom-bouquets",json={}).json()
        self.assertEqual(self.client.post(f"/bouquet-test/custom-bouquets/{row['id']}/finalize",json={}).status_code,422)
