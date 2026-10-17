from tests.helpers.expenses import ExpenseEndpointTestCase


class ListExpenseEndpointTests(ExpenseEndpointTestCase):
    def test_auth_filters_sort_pagination_and_literal_search(self):
        self.assertEqual(self.client.get("/expenses").status_code,401)
        self.login_as("staff")
        first = self.create_record(material_name="Ribbon 100%",store_name="Toko A")
        second = self.create_record(material_name="Pipe Cleaner",store_name="Toko B")
        old=self.create_expense(first["id"],price_per_pack="100",purchase_date="2020-01-01",reference_number="INV_1")
        new=self.create_expense(second["id"],price_per_pack="200",purchase_date="2020-02-01")
        page=self.client.get("/expenses?sort=total_asc&limit=1").json()
        self.assertEqual(page["total"],2)
        self.assertEqual(page["items"][0]["id"],old["id"])
        page=self.client.get(f"/expenses?supplier_id={second['id']}&date_from=2020-02-01&date_to=2020-02-01&min_total=400&max_total=400").json()
        self.assertEqual([x["id"] for x in page["items"]],[new["id"]])
        for q in ("%","INV_1"):
            self.assertEqual(self.client.get("/expenses",params={"q":q}).json()["total"],1)
        self.assertEqual(self.client.get("/expenses?sort=oldest&offset=1").json()["items"][0]["id"],new["id"])

    def test_invalid_ranges_bounds_and_query_fields(self):
        self.login_as()
        for query in ("limit=101", "offset=-1", "offset=1000001", "q=", "sort=unsafe", "unused=x",
                      "date_from=2020-02-01&date_to=2020-01-01", "min_total=100&max_total=10"):
            self.assertEqual(self.client.get("/expenses?"+query).status_code,422)
