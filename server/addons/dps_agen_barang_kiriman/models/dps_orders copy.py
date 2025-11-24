from itertools import count
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)

class DpsOrderBarkir(models.Model):
    _name = 'dps.barkir.order'
    _description='Data Order Barang Kiriman'
    _inherit = 'mail.thread'

    name = fields.Char(string='No Resi', track_visibility=True)
    agen_id = fields.Many2one('dps.agen.barkir', string='Agen', track_visibility=True)

    jenis_id_pengirim = fields.Many2one('dps.reference.agen', string='Jenis ID Pengirim', domain=[('kode_master','=', 'JENIS_IDENTITAS')], required=True ,track_visibility=True)
    id_pengirim = fields.Char(string='ID Pengirim', required=True,track_visibility=True)
    nama_pengirim = fields.Char(string='Nama Pengirim', required=True,track_visibility=True)
    alamat_pengirim = fields.Char(string='Alamat Pengirim', required=True,track_visibility=True)
    negara_pengirim = fields.Many2one('dps.reference.agen', string='Negara Pengirim', domain=[('kode_master','=', 'NEGARA')], required=True,track_visibility=True)
    nomor_telepon_pengirim = fields.Char(string='Nomor Telepon Pengirim', required=True,track_visibility=True)
    
    jenis_id_penerima = fields.Many2one('dps.reference.agen', string='Jenis ID Penerima', domain=[('kode_master','=', 'JENIS_IDENTITAS')], required=True,track_visibility=True)
    id_penerima = fields.Char(string='ID Penerima', required=True,track_visibility=True)
    nama_penerima = fields.Char(string='Nama Penerima', required=True,track_visibility=True)
    alamat_penerima = fields.Char(string='Alamat Penerima', required=True,track_visibility=True)
    kota_penerima = fields.Many2one('dps.reference.agen', string='Kota Penerima', domain=[('kode_master','=', 'KOTA')], required=True,track_visibility=True)
    provinsi_penerima = fields.Many2one('dps.reference.agen', string='Provinsi Penerima', domain=[('kode_master','=', 'PROVINSI')], required=True,track_visibility=True)
    negara_penerima = fields.Char(string='Negara Penerima', default='Indonesia', required=True,track_visibility=True)
    nomor_telepon_penerima = fields.Char(string='Nomor Telepon Penerima', required=True,track_visibility=True)

    kemasan_ids = fields.One2many(string='Detail Kemasan',comodel_name='dps.barkir.kemasan',inverse_name='order_id', track_visibility=True)
    total_kemasan = fields.Integer(string='Total Kemasan', compute='_compute_jumlah_kemasan')

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submit', 'Submitted'),
            # ('paid', 'Lunas'),
            ('cancel', 'Canceled')
            ],default='draft',
        string='Status',
        track_visibility=True)
    

    # On Change Section
    @api.model
    def create(self, vals):
        order_seq = self.env['ir.sequence'].next_by_code('no.resi')
        vals['name'] = order_seq

        return super(DpsOrderBarkir, self).create(vals)
    
    # Compute Section
    @api.depends('kemasan_ids')
    def _compute_jumlah_kemasan(self):
        for order in self:
            order.total_kemasan = len(order.kemasan_ids)

    def action_see_kemasan(self):
        list_domain = []
        if 'active_id' in self.env.context:
            list_domain.append(('order_id', '=', self.env.context['active_id']))
        
        return {
            'name':_('Kemasan'),
            'domain':list_domain,
            'res_model':'dps.barkir.kemasan',
            'view_mode':'tree,form',
            'type':'ir.actions.act_window',
            'context': {
                'default_jenis_id_penerima':self.jenis_id_penerima.id,
                'default_id_penerima':self.id_penerima,
                'default_nama_penerima':self.nama_penerima,
                'default_alamat_penerima':self.alamat_penerima,
                'default_kota_penerima':self.kota_penerima.id,
                'default_provinsi_penerima':self.provinsi_penerima.id,
                'default_negara_penerima':self.negara_penerima,
                'default_nomor_telepon_penerima':self.nomor_telepon_penerima,
            }
        }

    def action_draft(self):
        if self.state == 'submit':

            kemasanList = self.env['dps.barkir.kemasan'].search([('order_id', '=', self.id)])
            if len(kemasanList) > 0:
                for kemasan in kemasanList:
                    kemasan.state = 'draft'
            self.state = 'draft'
        else:
            raise UserError('Order Tidak Bisa Diubah')

    # Function Section
    def action_submit(self):
        if self.state == 'draft':
            kemasanList = self.env['dps.barkir.kemasan'].search([('order_id', '=', self.id)])
            
            if len(kemasanList) > 0:
                for kemasan in kemasanList:
                    kemasan.action_submit()

            self.state = 'submit'
        else:
            raise UserError('Order Tidak Bisa Diubah')
    
    def action_cancel(self):
        if self.state == 'submit':
            
            kemasanList = self.env['dps.barkir.kemasan'].search([('order_id', '=', self.id)])
            if len(kemasanList) > 0:
                for kemasan in kemasanList:
                    kemasan.action_cancel()

            self.state = 'cancel'
        else:
            raise UserError('Order Tidak Bisa Dibatalkan')
    
    def action_paid(self):
        if self.state == 'submit':
            self.state = 'paid'
        else:
            raise UserError('Order Belum Di Konfirmasi')
        

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
            self.state = 'on_shipment'
        else:
            raise UserError('Shipment Tidak Bisa Diubah')
        
    def action_send_to_pjt(self):
        self.toggle_pjt = True
    
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
            ('stuffing', 'Stuffing'),
            ('on_shipment', 'On Shipment'),
            # ('arrived', 'Arrived'),
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
            self.state = 'stuffing'

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
            ('received', 'Received by Courier'),
            ('loaded', 'Loaded into Cargo'),
            ('on_shipment', 'Shipped to Destination'),
            ('arrived', 'Shipment Arrived'),
            ('clearance', 'Customs Clearance'),
            ('in_transit', 'On Delivery'),
            ('delivered', 'Delivered'),
            ('cancel', 'Canceled')
            ],default='draft',
        string='Status',
        track_visibility='onchange')
    
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
            self.state = 'received'
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

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submit', 'Submitted')
            ],default='draft',
        string='Status')
    
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
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name :
            args += ['|', ('kode_reff', operator, name), ('uraian', operator, name)]
        return super(DpsReferenceAgen, self).search(args, limit=limit).name_get()

class DpsAgenBarkir(models.Model):
    _name = 'dps.agen.barkir'
    _description='Data Agen Barang Kiriman'

    name = fields.Char(string='Kode Agen', required=True)
    nama_agen = fields.Char(string='Nama Agen', required=True)
    alamat_agen = fields.Char(string='Alamat Agen', required=True)
    kota_agen = fields.Char(string='Kota Agen', required=True)
    provinsi_agen = fields.Char(string='Provinsi Agen', required=True)
    negara_agen = fields.Char(string='Negara Agen', required=True)
    nomor_telepon_agen = fields.Char(string='No Telp Agen', required=True)
    email_agen = fields.Char(string='Email Agen', required=True)
    website_agen = fields.Char(string='Website Agen', required=True)
