{
    "name" : "DPM FIK UDINUS",
    "version" : "1.0",
    "description" : """Managemen Organisasi Dewan Perwakilan Mahasiswa Fakultas Ilmu Komputer Universitas Dian Nuswantoro""",
    "author" : "Rizal",
    "website" : "https://dpmfikudinus.com/",
    "category" : "Productivity",
    "installable" : True,
    "application" : True,
    "depends" : ["base"],
    "data" : [
        'security/ir.model.access.csv',
        'views/status.xml',
        'views/komisi.xml',
        'views/proker.xml',
        'views/periode.xml',
        'views/sie.xml',
        'views/kepengurusan.xml',
        'views/proposal.xml',
        'views/lpj.xml',
        'views/menu_items.xml',
        # FIle Data
        #'data/status.xml',
        'data/status.dpm.csv'
    ],
    "license" : "LGPL-3",
}