# Copyright (c) 2021, ritwik and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator

class Item(WebsiteGenerator):
	def validate(self):
		if not self.show_in_website:
			self.route = None
		else:
			item_base_route = frappe.get_doc("DocType", "Item").route
			self.route = item_base_route + f"/{self.name}"
