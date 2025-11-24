from odoo import models, fields, api, _

class DpsPartner(models.Model):
    _name = 'dps.partner'
    _description = 'Data Partner Agen Barkir'
    _inherit = 'mail.thread' # Untuk fitur chatter seperti log dan pesan

    name = fields.Char(string='Nama Partner', required=True, tracking=True)
    kode_partner = fields.Char(string='Kode Partner', required=True, copy=False, readonly=True, default='New')
    agen_id = fields.Many2one(
        'dps.agen.barkir',
        string='Agen Terkait',
        required=True,
        help="Agen yang terhubung dengan partner ini",
        tracking=True
    )
    alamat = fields.Char(string='Alamat', tracking=True)
    # ===> UBAH FIELD INI <===
    kota = fields.Many2one(
        'dps.reference.agen',  # Model referensi Anda
        string='Kota',
        domain=[('kode_master', '=', 'KOTA')],  # Hanya tampilkan referensi dengan kode_master 'KOTA'
        tracking=True
    )
    # ===> UBAH FIELD INI <===
    provinsi = fields.Many2one(
        'dps.reference.agen',  # Model referensi Anda
        string='Provinsi',
        domain=[('kode_master', '=', 'PROVINSI')],  # Hanya tampilkan referensi dengan kode_master 'PROVINSI'
        tracking=True
    )
    # ===> UBAH FIELD INI <===
    negara = fields.Many2one(  # Default 'Indonesia' bisa dipindahkan ke onchange atau default value
        'dps.reference.agen',  # Model referensi Anda
        string='Negara',
        domain=[('kode_master', '=', 'NEGARA')],  # Hanya tampilkan referensi dengan kode_master 'NEGARA'
        default=lambda self: self.env['dps.reference.agen'].search(
            [('kode_master', '=', 'NEGARA'), ('uraian', '=', 'Indonesia')], limit=1).id,
        # Set default ke 'Indonesia' dari referensi
        tracking=True
    )

    nomor_telepon = fields.Char(string='Nomor Telepon', tracking=True)
    email = fields.Char(string='Email', tracking=True)

    # Field Compute untuk jumlah order
    order_count = fields.Integer(string='Jumlah Order', compute='_compute_order_count', store=True)

    pricelist_ids = fields.One2many(
        'dps.pricelist',
        'partner_id',  # Ini adalah field Many2one di model dps.pricelist yang menunjuk balik ke dps.partner
        string='Daftar Pricelist',
        readonly=True  # Ini hanya untuk melihat pricelist, bukan mengeditnya langsung di sini
    )

    order_ids = fields.One2many(
        'dps.barkir.order',  # Comodel: nama model order Anda
        'partner_id',  # Inverse field: nama field Many2one di model order yang menunjuk ke dps.partner
        string='Orders'
    )

    @api.model
    def create(self, vals):
        if vals.get('kode_partner', 'New') == 'New':
            vals['kode_partner'] = self.env['ir.sequence'].next_by_code('dps.partner.code') or 'New'
        return super(DpsPartner, self).create(vals)

    @api.depends('order_ids') # Pastikan field ini di-compute berdasarkan order_ids jika ada
    def _compute_order_count(self):
        for partner in self:
            # Menggunakan search_count untuk menghitung jumlah order yang terkait dengan partner ini
            partner.order_count = self.env['dps.barkir.order'].search_count([('partner_id', '=', partner.id)])

    def action_view_orders(self):
        # Aksi untuk menampilkan semua order yang terkait dengan partner ini
        self.ensure_one()
        return {
            'name': _('Orders by Partner'),
            'view_mode': 'tree,form',
            'res_model': 'dps.barkir.order',
            'type': 'ir.actions.act_window',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }