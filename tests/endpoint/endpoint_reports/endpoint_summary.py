import importlib.util
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from models import AuditLog, InventoryBalance, Material, Order, OrderItem, OrderPayment, ProductionRecord, Purchase, PurchaseItem, SupplierStore
from models.flower_model import Flower
from models.product_model import Product
from models.product_material_model import ProductMaterial
from tests.helpers.auth import AuthEndpointTestCase


class ReportEndpointTests(AuthEndpointTestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec("routes.reports"), "Reports are not implemented")
        super().setUp()
        from routes.reports import router as reports
        from routes.dashboard import router as dashboard
        from routes.audit import router as audit
        for router in (reports, dashboard, audit):
            self.app.include_router(router, prefix="/read-test")
        with Session(self.engine) as db:
            supplier = SupplierStore(name="Shop")
            material = Material(sku="REPORT-M", name="Stock material", minimum_stock=5)
            flower = Flower(sku="REPORT-F", name="Sale flower", selling_price=1000)
            db.add_all([supplier, material, flower])
            db.flush()
            db.add(InventoryBalance(material_id=material.id, quantity_on_hand=3, average_unit_cost=10, has_received_cost=True))
            known_product = Product(sku="REPORT-KNOWN", name="Known recipe", selling_price=100, assembly_labor_cost=5)
            missing_product = Product(sku="REPORT-MISSING", name="Missing recipe", selling_price=100)
            db.add_all([known_product, missing_product])
            db.flush()
            db.add(ProductMaterial(product_id=known_product.id, material_id=material.id, quantity_required=2, unit="pcs"))
            purchase = Purchase(purchase_number="REPORT-P", supplier_id=supplier.id, purchase_date=date(2026, 10, 15),
                subtotal=100, total_amount=100, status="received")
            db.add(purchase)
            db.add(Purchase(purchase_number="REPORT-DRAFT", supplier_id=supplier.id, purchase_date=date(2026, 10, 15),
                subtotal=900, total_amount=900, status="draft"))
            db.flush()
            db.add(PurchaseItem(purchase_id=purchase.id, material_id=material.id, material_name_snapshot=material.name,
                base_unit_snapshot="pcs", quantity=1, quantity_base=10, unit_price=100, subtotal=100))
            completed = Order(order_number="REPORT-O1", customer_name="Customer", order_date=date(2026, 9, 30),
                subtotal=1000, discount_amount=100, shipping_charge=200, total_amount=1100, status="completed",
                sales_channel="instagram", completed_at=datetime(2026, 10, 14, 17, 0, tzinfo=UTC))
            cancelled = Order(order_number="REPORT-O2", customer_name="Cancelled", order_date=date(2026, 10, 15),
                subtotal=500, total_amount=500, status="cancelled", sales_channel="other")
            outside = Order(order_number="REPORT-O3", customer_name="Outside", order_date=date(2026, 10, 15),
                subtotal=999, total_amount=999, status="completed", completed_at=datetime(2026, 10, 15, 17, 0, tzinfo=UTC))
            db.add_all([completed, cancelled, outside])
            db.flush()
            db.add(OrderItem(order_id=completed.id, flower_id=flower.id, item_name_snapshot="Sale flower",
                quantity=1, unit_price=1000, subtotal=1000))
            db.add(ProductionRecord(order_id=completed.id, actual_material_cost=300, labor_cost_snapshot=50,
                total_production_cost=350, created_at=datetime(2026, 10, 14, 18, 0, tzinfo=UTC)))
            for order, amount in ((completed, 300), (cancelled, 200)):
                db.add(OrderPayment(order_id=order.id, payment_key=uuid4(), payment_date=date(2026, 10, 15), amount=amount))
            db.add(AuditLog(actor_id=UUID(self.staff_id), action="report_fixture", entity_type="order", entity_id=completed.id,
                details={"safe": "visible", "password_hash": "DO_NOT_EXPOSE", "nested": {"session_token": "DO_NOT_EXPOSE"}},
                created_at=datetime(2026, 10, 14, 17, 0, tzinfo=UTC)))
            db.commit()

    period = "date_from=2026-10-15&date_to=2026-10-15"

    def test_sales_use_jakarta_completion_date_and_collections_use_payment_date(self):
        self.login_as("staff")
        response = self.client.get("/read-test/reports/sales?" + self.period)
        self.assertEqual(response.status_code, 200, response.text)
        report = response.json()
        self.assertEqual(report["completed_order_count"], 1)
        self.assertEqual(report["completed_sales_total"], 1100)
        self.assertEqual(report["collections_total"], 500)
        self.assertEqual(report["collections_from_cancelled_orders"], 200)
        self.assertEqual(report["period"]["timezone"], "Asia/Jakarta")
        self.assertEqual(report["by_sales_channel"][0]["sales_channel"], "instagram")

    def test_purchase_inventory_and_gross_margin_are_distinct(self):
        self.login_as("staff")
        purchases = self.client.get("/read-test/reports/purchases?" + self.period)
        self.assertEqual(purchases.status_code, 200, purchases.text)
        self.assertEqual(purchases.json()["total_amount"], 100)
        self.assertEqual(purchases.json()["purchase_count"], 1)
        inventory = self.client.get("/read-test/reports/inventory?" + self.period)
        self.assertEqual(inventory.status_code, 200, inventory.text)
        self.assertEqual(Decimal(inventory.json()["inventory_value"]), Decimal(30))
        self.assertEqual(inventory.json()["low_stock_count"], 1)
        profit = self.client.get("/read-test/reports/profitability?" + self.period)
        self.assertEqual(profit.status_code, 200, profit.text)
        self.assertEqual(profit.json()["completed_revenue_excluding_shipping"], 900)
        self.assertEqual(Decimal(profit.json()["completed_production_cost"]), Decimal(350))
        self.assertEqual(Decimal(profit.json()["gross_margin"]), Decimal(550))
        self.assertNotIn("net_profit", profit.text)
        estimates = {row["sku"]: row for row in profit.json()["estimated_product_hpp"]}
        self.assertEqual(Decimal(estimates["REPORT-KNOWN"]["estimated_hpp"]), Decimal(25))
        self.assertTrue(estimates["REPORT-KNOWN"]["cost_complete"])
        self.assertIsNone(estimates["REPORT-MISSING"]["estimated_hpp"])
        self.assertFalse(estimates["REPORT-MISSING"]["cost_complete"])

    def test_missing_costs_remain_unknown_instead_of_reporting_zero_profit_or_value(self):
        self.login_as("staff")
        with Session(self.engine) as db:
            db.query(InventoryBalance).update({"has_received_cost": False})
            db.commit()
        inventory = self.client.get("/read-test/reports/inventory?" + self.period).json()
        self.assertIsNone(inventory["inventory_value"])
        self.assertFalse(inventory["valuation_complete"])
        self.assertEqual(inventory["missing_cost_material_count"], 1)
        profit = self.client.get("/read-test/reports/profitability?date_from=2026-10-16&date_to=2026-10-16").json()
        self.assertEqual(profit["completed_order_count"], 1)
        self.assertEqual(profit["missing_production_cost_count"], 1)
        self.assertFalse(profit["cost_complete"])
        self.assertIsNone(profit["gross_margin"])
        self.assertIsNone(profit["gross_margin_percent"])

    def test_all_reads_require_login_audit_requires_superadmin_and_filters_redact_secrets(self):
        self.assertEqual(self.client.get("/read-test/reports/sales").status_code, 401)
        self.assertEqual(self.client.get("/read-test/dashboard").status_code, 401)
        self.login_as("staff")
        self.assertEqual(self.client.get("/read-test/audit").status_code, 403)
        self.login_as()
        response = self.client.get("/read-test/audit?" + self.period + "&action=report_fixture&limit=1")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["details"]["safe"], "visible")
        self.assertNotIn("DO_NOT_EXPOSE", response.text)
        self.assertEqual(self.client.get("/read-test/audit?actor_id=" + self.admin_id + "&action=report_fixture").json()["total"], 0)

    def test_date_validation_and_dashboard_limit(self):
        self.login_as("staff")
        self.assertEqual(self.client.get("/read-test/reports/sales?date_from=2026-10-16&date_to=2026-10-15").status_code, 422)
        self.assertEqual(self.client.get("/read-test/dashboard?limit=21").status_code, 422)
        response = self.client.get("/read-test/dashboard?" + self.period + "&limit=1")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(len(response.json()["recent_orders"]), 1)
        self.assertEqual(response.json()["low_stock_count"], 1)
        summary=self.client.get('/api/v1/dashboard/summary?'+self.period).json()
        self.assertEqual(summary['completed_orders'],1)
        self.assertEqual(summary['active_orders'],0)
        for path in ('recent-orders','recent-purchases'):
            recent=self.client.get('/api/v1/dashboard/'+path+'?'+self.period+'&limit=1')
            self.assertEqual(recent.status_code,200,recent.text)
            self.assertEqual(len(recent.json()['items']),1)
