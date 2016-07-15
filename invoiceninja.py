import requests
import json
import datetime
from dateutil.relativedelta import relativedelta


class invoiceNinja(object):
    """Class for handling Invoice Ninja API."""

    def __init__(self, token, url='https://app.invoiceninja.com/api/v1/'):
        """Add Invoice Ninja token."""

        self.token = token
        self.url = url
        self.headers = {'X-Ninja-Token': self.token}
        self.recurring_opt = {'weekly': 1, 'twoweeks': 2, 'fourweeks': 3, 
                              'monthly': 4, 'threemonths': 5, 'sixmonths': 6, 
                              'yearly': 7}

    def exists_client(self, client):
        """Return True if client exists."""
        suburl = 'clients?email=' + client['contact']['email']
        res = requests.get(self.url + suburl, json=client, headers=self.headers)
        if res.status_code == 200:
            data = res.json()
            if len(data['data']) >= 1:
                d = dict()
                d['data'] = data['data'][0]
                self.client = d
                return d
            else:
                return False
        return False

    def create_client(self, client):
        """Create a client in Invoice Ninja."""
        client_data = self.exists_client(client)
        if not client_data:
            res = requests.post(self.url + 'clients', json=client, headers=self.headers)
            if res.status_code == 200:
                self.client = res.json()
                return self.client
            else:
                return res.json()
        else:
            return client_data

    def create_invoice(self, product):
        """Create an invoice for a client."""
        product['client_id'] = self.client['data']['id']
        res = requests.post(self.url + 'invoices', json=product,
                            headers=self.headers)
        if res.status_code == 200:
            self.invoice = res.json()
            return self.invoice
        else:
            return res.json()

    def create_recurring_invoice(self, product):
        """Create a recurring invoice for a client."""

        product['is_recurring'] = True
        product['client_id'] = self.client['data']['id']
        product['auto_bill'] = True

        today = datetime.datetime.now().date()
        product['start_date'] = today.isoformat()

        if product['recurring'] == 'monthly':
            end_date = (today + datetime.timedelta(days=365)).isoformat()
            end_date = (today + relativedelta(months=1)).isoformat()
            product['end_date'] = end_date
            product['frequency_id'] = self.recurring_opt.get('monthly')

        if product['recurring'] == 'yearly':
            end_date = (today + relativedelta(years=1)).isoformat()
            product['end_date'] = end_date
            product['frequency_id'] = self.recurring_opt.get('yearly')

        del product['recurring']

        res = requests.post(self.url + 'invoices', json=product,
                            headers=self.headers)
        if res.status_code == 200:
            self.invoice = res.json()
            return self.invoice
        else:
            return res.json()


    def checkout(self, client, product):
        """Create a client and an invoice for the client."""
        self.create_client(client)
        self.create_invoice(product)