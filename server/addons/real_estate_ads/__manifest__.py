{
    "name": "Real Estate Ads",
    "version": "1.0",
    "website": "http://www.belajarodoo.com",
    "author": "Rizal",
    "description": """
        Modul Real Estate untuk menampilkan property yang tersedia
    """,
    "category": "Sales",
    "depends": ["base"],
    "data": [
        'security/ir.model.access.csv',
        'views/property_partner_view.xml',
        'views/property_view.xml',
        'views/property_type_view.xml',
        'views/property_tag_view.xml',
        'views/menu_items.xml',

        # Data Type
        #'data/property_type.xml' # cara dengan menuliskan data di file.xml dalam folder data
        'data/estate.property.type.csv' # cara dengan menuliskan data di file.csv dalam folder data
    ],
    "demo": [
        'demo/property_tag.xml' # akan tampil ketika pertama download modul dan mengaktifkan data demo
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}