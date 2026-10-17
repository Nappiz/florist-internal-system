from tests.helpers.suppliers import SupplierEndpointTestCase


class ListSuppliersEndpointTests(SupplierEndpointTestCase):
    def test_authenticated_list_search_filters_total_and_pagination(self):
        self.assertEqual(self.client.get("/suppliers").status_code, 401)
        self.login_as("staff")
        self.create_record(store_name="Toko A", category="Batang", marketplace="Shopee")
        self.create_record(store_name="Toko B", category="Batang", marketplace="Shopee", price="15000")
        self.create_record(material_name="Lem", store_name="Toko C", category="Perekat")
        response = self.client.get("/suppliers?q=pipe&category=batang&marketplace=shopee&unit=PCS&limit=1&offset=1&sort=price_asc")
        self.assertEqual(response.status_code, 200, response.text)
        page = response.json()
        self.assertEqual(page["total"], 2)
        self.assertEqual(len(page["items"]), 1)
        self.assertEqual(page["items"][0]["store_name"], "Toko B")
        self.assertEqual(page["limit"], 1)
        self.assertEqual(page["offset"], 1)
        self.assertEqual(self.client.get("/suppliers?store_name=toko%20a").json()["total"], 1)
        self.assertEqual(self.client.get("/suppliers?min_price=13000&max_price=16000").json()["total"], 1)

    def test_unit_price_sort_compares_pack_contents_and_search_wildcards_are_literal(self):
        self.login_as("staff")
        expensive = self.create_record(price="10000", pack_quantity="10")
        cheap = self.create_record(price="20000", pack_quantity="100")
        self.create_record(material_name="Diskon 100%", price="30000", pack_quantity="1")
        response = self.client.get("/suppliers?unit=pcs&sort=unit_price_asc")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id"] for row in response.json()["items"]][:2], [cheap["id"], expensive["id"]])
        self.assertEqual(self.client.get("/suppliers", params={"q": "%"}).json()["total"], 1)
        self.assertEqual(self.client.get("/suppliers", params={"q": "' OR 1=1 --"}).json()["total"], 0)

    def test_invalid_filter_range_and_unbounded_pages_are_rejected(self):
        self.login_as("staff")
        for query in ("min_price=20&max_price=10", "limit=101", "offset=-1", "offset=" + str(10**30), "sort=invalid", "min_price=NaN"):
            with self.subTest(query=query):
                self.assertEqual(self.client.get("/suppliers?" + query).status_code, 422)
