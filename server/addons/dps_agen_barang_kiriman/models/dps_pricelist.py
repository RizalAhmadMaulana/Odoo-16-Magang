from odoo import models, fields, api, _

class DpsPricelist(models.Model):
    _name = 'dps.pricelist'
    _description = 'Pricelist Partner Agen Barkir'
    _inherit = 'mail.thread'

    name = fields.Char(string='Nama Pricelist', required=True, tracking=True)
    agen_id = fields.Many2one(
        'dps.agen.barkir',
        string='Agen',
        required=True,
        help="Agen yang menetapkan pricelist ini",
        tracking=True
    )
    partner_id = fields.Many2one(
        'dps.partner',
        string='Partner',
        required=True,
        help="Partner yang menerima pricelist ini",
        tracking=True
    )
    # Pastikan kombinasi agen_id dan partner_id unik
    _sql_constraints = [
        ('unique_agen_partner_pricelist', 'unique(agen_id, partner_id)', 'Pricelist untuk Agen dan Partner ini sudah ada!'),
    ]

    pricelist_line_ids = fields.One2many(
        'dps.pricelist.line',
        'pricelist_id',
        string='Item Pricelist',
        copy=True # Agar baris-baris pricelist ikut tercopy saat pricelist di-duplikasi
    )
    date_start = fields.Date(string='Tanggal Mulai', tracking=True)
    date_end = fields.Date(string='Tanggal Berakhir', tracking=True)

class DpsPricelistLine(models.Model):
    _name = 'dps.pricelist.line'
    _description = 'Detail Item Pricelist Agen Barkir'

    pricelist_id = fields.Many2one('dps.pricelist', string='Pricelist', required=True, ondelete='cascade')
    # Contoh field untuk item pricelist. Sesuaikan dengan kebutuhan Anda (misal: berdasarkan rute, berat, jenis barang, dll.)
    ukuran_kemasan_id = fields.Many2one('dps.reference.agen', string='Ukuran Kemasan', domain=[('kode_master','=', 'UKURAN_KEMASAN')], required=True)
    harga = fields.Float(string='Harga', required=True, digits='Product Price')
    # Anda bisa menambahkan field lain seperti:
    # jenis_barang_id = fields.Many2one('dps.reference.agen', string='Jenis Barang', domain=[('kode_master','=', 'KATEGORI_BARANG')])
    # zona_tujuan_id = fields.Many2one('dps.reference.agen', string='Zona Tujuan', domain=[('kode_master','=', 'KOTA')])