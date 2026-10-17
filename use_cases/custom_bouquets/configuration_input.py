from schemas.custom_bouquet_schema import BouquetCreate

def configuration_input(row):
    snapshot=row.recipe_snapshot
    return BouquetCreate(name=row.name,customer_reference=row.customer_reference,description=row.description,image_reference=row.image_reference,personalization=row.personalization,flowers=[{"flower_id":line["flower_id"],"quantity":line["quantity"]} for line in snapshot.get("flowers",[])],options=[{"bouquet_option_id":line["bouquet_option_id"],"quantity":line["quantity"]} for line in snapshot.get("options",[])],additional_materials=snapshot.get("additional_materials",[]))
