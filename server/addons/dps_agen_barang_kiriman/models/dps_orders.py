from itertools import count
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)

class DpsOrderBarkir(models.Model):
    _name = 'dps.barkir.order'
    _description='Data Order Barang Kiriman'
    _inherit = 'mail.thread'
    
    # =========================================================================
    # 1. FIELD DEFINITIONS (DIRAPIKAN DAN DIPASTIKAN ADA SEMUA)
    # =========================================================================

    # Field Utama / Standard Odoo
    name = fields.Char(
        string='No. Resi / Order', 
        required=True, 
        copy=False, 
        readonly=True, 
        default=lambda self: _('New'),
        tracking=True
    )

    invoice_payment_state = fields.Selection(
        related='invoice_id.payment_state', 
        string="Payment Status", 
        readonly=True, 
        store=True
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submit', 'Submitted'),
            ('paid', 'Paid')
        ],
        string='Status',
        tracking=True,
        compute='_compute_order_state',
        store=True,
        default='draft',
    )

    # Field Relasi Utama
    company_id_agen = fields.Many2one(
        'res.company',
        string='Agen (System)',
        readonly=True,
        default=lambda self: self.env.company.id, 
        tracking=True
    )
    partner_id = fields.Many2one(
        'dps.partner',
        string='Partner',
        help="Partner yang membuat order ini",
        tracking=True
    )

    # Field Data Pengirim
    jenis_id_pengirim = fields.Many2one(
        'dps.reference.agen', 
        string='Jenis ID Pengirim', 
        domain=[('kode_master','=', 'JENIS_IDENTITAS')], 
        required=True,
        tracking=True
    )
    id_pengirim = fields.Char(string='ID Pengirim', required=True, tracking=True)
    nama_pengirim = fields.Char(string='Nama Pengirim', required=True, tracking=True)
    alamat_pengirim = fields.Char(string='Alamat Pengirim', required=True, tracking=True)
    negara_pengirim = fields.Many2one('dps.reference.agen', string='Negara Pengirim', domain=[('kode_master','=', 'NEGARA')], required=True, tracking=True)
    nomor_telepon_pengirim = fields.Char(string='Nomor Telepon Pengirim', required=True, tracking=True)
    
    # Field Data Penerima
    jenis_id_penerima = fields.Many2one('dps.reference.agen', string='Jenis ID Penerima', domain=[('kode_master','=', 'JENIS_IDENTITAS')], required=True, tracking=True)
    id_penerima = fields.Char(string='ID Penerima', required=True, tracking=True)
    nama_penerima = fields.Char(string='Nama Penerima', required=True, tracking=True)
    alamat_penerima = fields.Char(string='Alamat Penerima', required=True, tracking=True)
    kota_penerima = fields.Many2one('dps.reference.agen', string='Kota Penerima', domain=[('kode_master','=', 'KOTA')], required=True, tracking=True)
    provinsi_penerima = fields.Many2one('dps.reference.agen', string='Provinsi Penerima', domain=[('kode_master','=', 'PROVINSI')], required=True, tracking=True)
    negara_penerima = fields.Char(string='Negara Penerima', default='Indonesia', required=True, tracking=True)
    nomor_telepon_penerima = fields.Char(string='Nomor Telepon Penerima', required=True, tracking=True)
    
    # Field Detil Barang & Kemasan
    ukuran_kemasan_id = fields.Many2one(
        'dps.reference.agen', 
        string='Ukuran Kemasan', 
        domain=[('kode_master','=', 'UKURAN_KEMASAN')], 
        required=True
    )
    kemasan_ids = fields.One2many(string='Detail Kemasan',comodel_name='dps.barkir.kemasan',inverse_name='order_id', tracking=True)
    total_kemasan = fields.Integer(string='Total Kemasan', compute='_compute_jumlah_kemasan', store=True)

    # Field Invoicing (Krusial)
    biaya_pengiriman = fields.Float(
        string='Biaya Pengiriman',
        compute='_compute_biaya_pengiriman',
        store=True,
        digits='Product Price'
    )
    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        readonly=True,
        copy=False,
        help="Link to the corresponding invoice."
    )

    # UNTUK MENGUBAH STATUS PAID
    @api.depends('invoice_id.payment_state', 'invoice_id')
    def _compute_order_state(self):
        for order in self:
            # Jika Invoice sudah ada dan statusnya 'paid'
            if order.invoice_id and order.invoice_id.payment_state == 'paid':
                order.state = 'paid'
            # Jika Order sudah memiliki Invoice tetapi belum Paid, status tetap Submitted
            elif order.invoice_id:
                order.state = 'submit' 
            # Jika belum ada Invoice, pertahankan status manual (Draft/Submitted dari action_submit)
            else:
                order.state = 'draft' 
                # Note: Ini akan me-reset ke draft jika tidak ada invoice.
                # Anda perlu memastikan action_submit() sudah di-run sebelumnya
    
    # =================================
    # 2. COMPUTED AND ONCHANGE METHODS
    # =================================

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            # Pastikan 'no.resi' adalah kode sequence yang benar
            vals['name'] = self.env['ir.sequence'].next_by_code('no.resi') or 'New'
        return super(DpsOrderBarkir, self).create(vals)

    @api.depends('kemasan_ids')
    def _compute_jumlah_kemasan(self):
        for order in self:
            order.total_kemasan = len(order.kemasan_ids)

    @api.depends('partner_id', 'ukuran_kemasan_id')
    def _compute_biaya_pengiriman(self):
        for rec in self:
            rec.biaya_pengiriman = 0.0
            if rec.partner_id and rec.ukuran_kemasan_id:
                # Logika Pencarian Pricelist Anda yang sebenarnya
                pricelist = self.env['dps.pricelist'].search([
                    ('agen_id', '=', rec.partner_id.agen_id.id),
                    ('partner_id', '=', rec.partner_id.id),
                ], limit=1)

                if pricelist:
                    pricelist_line = pricelist.pricelist_line_ids.filtered(
                        lambda l: l.ukuran_kemasan_id.id == rec.ukuran_kemasan_id.id
                    )
                    if pricelist_line:
                        rec.biaya_pengiriman = pricelist_line.harga
                    # Jika tidak ada pricelist line, biarkan 0.0 atau raise error
    
    # =========================================================================
    # 3. ACTION AND LOGIC METHODS (CREATE INVOICE)
    # =========================================================================
    
    def action_create_invoice(self):
        self.ensure_one()
        
        if self.invoice_id:
            raise UserError(_("Invoice has already been created for this DPS Order."))

        if not self.biaya_pengiriman or self.biaya_pengiriman == 0.0:
            raise UserError(_("Biaya pengiriman belum dimasukan. Pastikan Biaya Pengiriman > 0."))

        # 1. Siapkan daftar invoice lines (Hanya untuk produk/barang kiriman)
        invoice_line_vals = []
        
        for kemasan in self.kemasan_ids:
            # Asumsi: Setiap barang kiriman (barang_ids) memiliki product_id yang valid
            for barang in kemasan.barang_ids: 
                invoice_line_vals.append((0, 0, {
                    'name': barang.product_id.name,
                    'product_id': barang.product_id.id,
                    'quantity': barang.jumlah_barang,
                    'price_unit': barang.product_id.list_price,
                }))

        # 2. Buat Header Invoice, mengisi field dps_shipping_cost di header
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'dps_order_id': self.id,
            'invoice_line_ids': invoice_line_vals,
            
            # PENTING: MENGISI FIELD dps_shipping_cost DI HEADER
            'dps_shipping_cost': self.biaya_pengiriman, 
        }

        new_invoice = self.env['account.move'].create(invoice_vals)
        self.write({
            'invoice_id': new_invoice.id
            })
        
        self._compute_order_state()

        # Arahkan user ke invoice
        return {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': new_invoice.id,
            'target': 'current',
        }

    # =========================================================================
    # 4. STATE CHANGE METHODS (Function Section)
    # =========================================================================
    
    def action_submit(self):
        self.ensure_one()
        
        if self.state == 'draft':
            kemasanList = self.kemasan_ids
            
            if not kemasanList:
                raise UserError(_("Tidak bisa Submit Order. Detil Kemasan masih kosong."))

            # 1. CASCADING STATE CHANGE: Submit Detil Kemasan
            for kemasan in kemasanList:
                # PENTING: Panggil method action_submit() di model dps.barkir.kemasan
                if kemasan.state == 'draft':
                    # Asumsi model kemasan memiliki action_submit() yang hanya mengubah kemasan.state = 'submitted'
                    kemasan.action_submit()

            # 2. Set status Order ke Submitted
            self.state = 'submit'
        else:
            raise UserError('Order Tidak Bisa Diubah')

    def action_draft(self):
        self.ensure_one()
        
        # Hanya izinkan reset dari Submitted(sesuai logika Reset to Draft)
        if self.state not in ['submitted', 'paid']:
            raise UserError('Order hanya bisa di-reset ke Draft dari status Submitted.')

        # 1. Hapus Invoice yang Terhubung (Logika yang kita buat sebelumnya)
        if self.invoice_id:
            invoice = self.invoice_id
            
            # Cek status Invoice
            if invoice.payment_state in ('paid'):
                raise UserError(_("Tidak bisa di-reset ke Draft. Invoice sudah PAID"))
            
            # Reset Posted Invoice ke Draft dan Hapus
            if invoice.state == 'posted':
                invoice.button_draft()
            
            try:
                invoice.unlink() # Hapus Invoice
            except Exception as e:
                # Ini akan menangkap error jika Invoice masih ada rekonsiliasi yang belum terbatalkan
                raise UserError(_("Gagal menghapus Invoice. Kemungkinan ada referensi lain yang mengunci."))
                
            self.invoice_id = False 
            
        # 2. CASCADING STATE CHANGE: Reset Detil Kemasan ke Draft
        for kemasan in self.kemasan_ids:
            # PENTING: Panggil method action_draft() di model dps.barkir.kemasan
            if kemasan.state != 'draft':
                # Asumsi model kemasan memiliki action_draft() yang hanya mengubah kemasan.state = 'draft'
                kemasan.action_draft() 
            
        # 3. Set status Order ke Draft
        self.state = 'draft' 
    
    def action_paid(self):
        if self.state == 'submit':
            self.state = 'paid'
        else:
            raise UserError('Order Belum Di Konfirmasi')
        
    def print_barcode(self):
        return self.env.ref('dps_agen_barang_kiriman.barcode_report_qweb').report_action(self)

    def action_see_kemasan(self):
        # Action untuk melihat kemasan terkait
        list_domain = [('order_id', '=', self.id)]
        
        return {
            'name':_('Kemasan'),
            'domain':list_domain,
            'res_model':'dps.barkir.kemasan',
            'view_mode':'tree,form',
            'type':'ir.actions.act_window',
            'context': {
                # Menggunakan default context untuk mempercepat pembuatan kemasan baru
                'default_jenis_id_penerima':self.jenis_id_penerima.id,
                'default_id_penerima':self.id_penerima,
                'default_nama_penerima':self.nama_penerima,
                'default_alamat_penerima':self.alamat_penerima,
                'default_kota_penerima':self.kota_penerima.id,
                'default_provinsi_penerima':self.provinsi_penerima.id,
                'default_negara_penerima':self.negara_penerima,
                'default_nomor_telepon_penerima':self.nomor_telepon_penerima,
                'default_order_id': self.id,
            }
        }
    
class DpsShipmentBarkir(models.Model):
    _name = 'dps.barkir.shipment'
    _description='Data Pengiriman Barang Kiriman'
    _inherit = 'mail.thread'

    name = fields.Char(string='No Master BL/AWB', required=True)
    tgl_master = fields.Date(string='Tanggal Master BL/AWB')
    nama_pengangkut = fields.Char(string='Nama Pengangkut')
    no_voy_flight = fields.Char(string='No Voy/Flight')

    estimated_arrival = fields.Date(string='Estimated Arrival')
    estimated_departure = fields.Date(string='Estimated Departure')

    callsign = fields.Char(string='Callsign')
    negara_asal_id = fields.Many2one('dps.reference.agen', string='Negara Asal', domain=[('kode_master','=', 'NEGARA')], required=True)
    pelabuhan_muat_id = fields.Many2one('dps.reference.agen', string='Pelabuhan Muat', domain=[('kode_master','=', 'PELABUHAN')], required=True)
    pelabuhan_transit_id = fields.Many2one('dps.reference.agen', string='Pelabuhan Transit', domain=[('kode_master','=', 'PELABUHAN')], required=True)
    pelabuhan_bongkar_id = fields.Many2one('dps.reference.agen', string='Pelabuhan Bongkar', domain=[('kode_master','=', 'PELABUHAN')], required=True)

    container_ids = fields.One2many('dps.barkir.container', 'shipment_id', string='Container Barang Kiriman')
    kemasan_ids = fields.One2many('dps.barkir.kemasan', 'shipment_id', string='Kemasan Barang Kiriman')

    toggle_pjt = fields.Boolean(string='Pjt ?', default=False)

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submit', 'Submitted'),
            ('on_shipment', 'On Shipment'),
            ('arrived', 'Arrived'),
            ('cancel', 'Canceled')
            ],default='draft',
        string='Status', )
    
    # On Change Section
    @api.model
    def create(self, vals):
        return super(DpsShipmentBarkir, self).create(vals)

    # Function Section
    def action_submit(self):
        if self.state == 'draft':
            self.state = 'submit'
        else:
            raise UserError('Shipment Tidak Bisa Diubah')
        
    def action_send_to_pjt(self):
        self.toggle_pjt = True

    def action_shipment(self):
        self.state = 'on_shipment'
    
    def action_cancel(self):
        if self.state == 'submit':
            self.state = 'cancel'
        else:
            raise UserError('Shipment Tidak Bisa Dibatalkan')
    
class DpsContainerBarkir(models.Model):
    _name = 'dps.barkir.container'
    _description='Data Container Barang Kiriman'
    _inherit = 'mail.thread'
    
    shipment_id = fields.Many2one('dps.barkir.shipment', string='Shipment ID')

    name = fields.Char(string='No Container', required=True)
    ukuran_container = fields.Many2one('dps.reference.agen', string='Ukuran Container', domain=[('kode_master','=', 'UKURAN_CONTAINER')], required=True)
    jenis_container = fields.Many2one('dps.reference.agen', string='Jenis Container', domain=[('kode_master','=', 'JENIS_CONTAINER')], required=True)
    no_segel = fields.Char(string='No Segel')
    agen_id = fields.Many2many('dps.agen.barkir', string='Agen')
    note = fields.Char(string='Note')

    kemasan_ids = fields.One2many(string='Detail Kemasan',comodel_name='dps.barkir.kemasan',inverse_name='container_id' )
    
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('loading', 'Loading'),
            ('on_shipment', 'On Shipment'),
            ('arrived', 'Arrived'),
            # ('partial_delivered', 'Partial Delivered'),
            # ('delivered', 'Delivered'),
            ('cancel', 'Canceled')
            ],default='draft',
        string='Status',
        )
    
    # On Change Section
    @api.model
    def create(self, vals):
        return super(DpsContainerBarkir, self).create(vals)
    
    #Set State Loading On Change kemasan_ids
    @api.onchange('kemasan_ids')
    def _onchange_kemasan_ids(self):
        if self.state == 'draft':
            self.state = 'loading'

    # Function Section
    def action_loading(self):
        if self.state == 'draft':
            self.state = 'loading'
        else:
            raise UserError('Container Tidak Bisa Diubah')

    def action_shipment(self):
        if self.state == 'loading':
            self.state = 'on_shipment'
        else:
            raise UserError('Container Tidak Bisa Diubah')
        
    def add_kemasan_req(self, kemasan_id):
        if self.state == 'loading':
            kemasan = self.env['dps.barkir.kemasan'].search([('id', '=', kemasan_id)])
            kemasan.write({'container_id': self.id})
        else:
            raise UserError('Container Tidak Bisa Diubah')
    
    def remove_kemasan_req(self, kemasan_id):
        if self.state == 'loading':
            kemasan = self.env['dps.barkir.kemasan'].search([('id', '=', kemasan_id)])
            kemasan.write({'container_id': None})
        else:
            raise UserError('Container Tidak Bisa Diubah')

        
     
class DpsKemasanBarkir(models.Model):
    _name = 'dps.barkir.kemasan'
    _description='Data Kemasan Barang Kiriman'
    _inherit = 'mail.thread'

    order_id = fields.Many2one('dps.barkir.order', string='Order ID')
    container_id = fields.Many2one('dps.barkir.container', string='Container ID')
    shipment_id = fields.Many2one('dps.barkir.shipment', string='Shipment ID')

    name = fields.Char(string='No Kemasan / No Resi')
    ukuran_kemasan = fields.Many2one('dps.reference.agen', string='Ukuran Kemasan', domain=[('kode_master','=', 'UKURAN_KEMASAN')], required=True)
    bruto = fields.Float(string='Bruto')
    netto = fields.Float(string='Netto')

    jenis_id_penerima = fields.Many2one('dps.reference.agen', string='Jenis ID Penerima', domain=[('kode_master','=', 'JENIS_IDENTITAS')], required=True)
    id_penerima = fields.Char(string='ID Penerima', required=True)
    nama_penerima = fields.Char(string='Nama Penerima', required=True)
    alamat_penerima = fields.Char(string='Alamat Penerima', required=True)
    kota_penerima = fields.Many2one('dps.reference.agen', string='Kota Penerima', domain=[('kode_master','=', 'KOTA')], required=True)
    provinsi_penerima = fields.Many2one('dps.reference.agen', string='Provinsi Penerima', domain=[('kode_master','=', 'PROVINSI')], required=True)
    negara_penerima = fields.Char(string='Negara Penerima', default='Indonesia', required=True)
    nomor_telepon_penerima = fields.Char(string='No Telp Penerima', required=True)   
    note = fields.Char(string='Note') 

    barang_ids = fields.One2many('dps.barkir.barang', 'kemasan_id', string='Detil Barang Kiriman')

    tracking_detail = fields.Char(string='Tracking Detail')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submit', 'Submitted'),
            ('loading', 'Loading'),
            ('on_shipment', 'On Shipment'),
            ('arrived', 'Shipment Arrived'),
            ('on_customs', 'On Customs'),
            # ('partial_delivered', 'Partially Delivered'),
            ('delivered', 'Delivered'),
            ('cancel', 'Canceled')
            ],default='draft',
        string='Status',
        tracking = True)
    
    # On Change Section
    @api.model
    def create(self, vals):
        obj = super(DpsKemasanBarkir, self).create(vals)
        number = self.env['ir.sequence'].get('no.kemasan') or ''
        obj.write({'name': number})
        return obj
    
    # Function Section
    def action_submit(self):
        if self.state == 'draft':
            self.state = 'submit'
        else:
            raise UserError('Kemasan Tidak Bisa Diubah')

class DpsBarangKemasanBarkir(models.Model):
    _name = 'dps.barkir.barang'
    _description='Data Barang Kiriman'

    kemasan_id = fields.Many2one('dps.barkir.kemasan', string='Kemasan ID')

    seri_barang = fields.Integer(string='Seri Barang')
    uraian_barang = fields.Char(string='Uraian Barang')
    kategori_barang_id = fields.Many2one('dps.reference.agen', string='Kategori Barang', domain=[('kode_master','=', 'KATEGORI_BARANG')], required=True)
    jumlah_barang = fields.Float(string='Jumlah Barang', default="1")

    product_id = fields.Many2one('product.product', string='Product', required=True)
    
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submit', 'Submitted')
            ],default='draft',
        string='Status')

    # Tambahkan metode ini untuk mengisi uraian secara otomatis saat memilih produk
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uraian_barang = self.product_id.name
    
class DpsReferenceAgen(models.Model):
    _name = 'dps.reference.agen'
    _description='Data Referensi Agen'

    kode_master = fields.Char(string='Kode Master', required=True)
    kode_reff = fields.Char(string='Kode Referensi', required=True)
    uraian = fields.Char(string='Uraian', required=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s - %s' % (rec.kode_reff,rec.uraian)))
        return result
    
    #@api.model
    #def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        #args = list(args or [])
        #if name :
            #args += ['|', ('kode_reff', operator, name), ('uraian', operator, name)]
    # return super(DpsReferenceAgen, self).search(args, limit=limit).name_get()

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += ['|', ('kode_reff', operator, name), ('uraian', operator, name)]
        records = self.search(args, limit=limit)
        return records.ids  # Kembalikan hanya list ID

class DpsAgenBarkir(models.Model):
    _name = 'dps.agen.barkir'
    _description='Data Agen Barang Kiriman'

    name = fields.Char(string='Kode Agen', required=True)
    nama_agen = fields.Char(string='Nama Agen', required=True)
    alamat_agen = fields.Char(string='Alamat Agen', required=True)
    kota_agen = fields.Many2one(
        'dps.reference.agen',
        string="Kota Agen",
        domain=[('kode_master', "=", "KOTA")],
        required=True
    )
    provinsi_agen = fields.Many2one(
        'dps.reference.agen',
        string="Provinsi Agen",
        domain=[('kode_master', "=", "PROVINSI")],
        required=True
    )
    negara_agen = fields.Many2one(
        'dps.reference.agen',
        string='Negara Agen',
        domain=[('kode_master', '=', 'NEGARA')],
        required=True
    )
    nomor_telepon_agen = fields.Char(string='No Telp Agen', required=True)
    email_agen = fields.Char(string='Email Agen', required=True)
    website_agen = fields.Char(string='Website Agen', required=True)