import csv
from io import StringIO
from crud import cashflow_crud
from use_cases.cashflow.common import require_superadmin, report_query


def csv_safe(value):
    text = '' if value is None else str(value)
    return "'" + text if text.lstrip().startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else text


def export(db, actor, query):
    require_superadmin(actor)
    query = report_query(query)

    def chunks():
        output = StringIO(newline='')
        writer = csv.writer(output)
        rows = cashflow_crud.export_rows(db, query)
        try:
            writer.writerow(['Period from', 'Period to', 'Date', 'Account', 'Transaction number', 'Source type', 'Source ID', 'Category', 'Description', 'Inflow IDR', 'Outflow IDR', 'Account running balance IDR'])
            yield '\ufeff' + output.getvalue()
            for batch in rows.partitions(500):
                output.seek(0)
                output.truncate(0)
                for row in batch:
                    writer.writerow([csv_safe(value) for value in (query.date_from, query.date_to, row['transaction_date'], row['account_name'], row['transaction_number'], row['source_type'], row['source_id'], row['category'], row['description'])] + [row['amount'] if row['direction'] == 'IN' else 0, row['amount'] if row['direction'] == 'OUT' else 0, int(row['running_balance'])])
                yield output.getvalue()
        finally:
            rows.close()
    return chunks()
