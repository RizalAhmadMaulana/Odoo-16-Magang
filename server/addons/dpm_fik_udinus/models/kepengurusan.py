from odoo import fields, models, api
from datetime import timedelta
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class Kepengurusan(models.Model):
    _name = 'kepengurusan.dpm'
    _description = 'Kepengurusan DPM FIK'

    nama_lengkap = fields.Many2one('res.partner', string="Nama Lengkap", required=True)
    email = fields.Char(string="Email", related='nama_lengkap.email')
    jabatan = fields.Text(string="Jabatan")
    nim_anggota = fields.Char(string="NIM")
    id_periode = fields.Many2one('periode.dpm', string="Periode Kepengurusan")
    id_komisi = fields.Many2one('komisi.dpm', string="Komisi")
    id_status = fields.Many2one('status.dpm', string="Status Kepengurusan")

    def write(self, vals):
        _logger.info("Nilai yang ditulis: %s", vals)
        res_partner_ids = self.env['res.partner'].browse(10)
        _logger.info("ID res.partner yang dicari: %s", res_partner_ids)
        return super(Kepengurusan, self).write(vals)

class Status (models.Model):
    _name = 'status.dpm'
    _description = 'Status Keanggotaan'
    _rec_name = 'status'

    status = fields.Char(string="Status Keanggotaan")

class Komisi (models.Model):
    _name = 'komisi.dpm'
    _description = 'Komisi DPM'
    _rec_name = 'komisi'

    komisi = fields.Text(string="Komisi")

class Proker (models.Model):
    _name = 'proker.dpm'
    _description = 'Program Kerja DPM'
    _rec_name = 'proker'
    
    proker = fields.Text(string="Program Kerja")
    komisi_id = fields.Many2one('komisi.dpm', string="Komisi")

class Periode (models.Model):
    _name = 'periode.dpm'
    _description = 'Periode Kepengurusan'
    _rec_name = 'periode'

    periode = fields.Char(string="Periode")

class Sie (models.Model):
    _name = 'sie.dpm'
    _description = 'Struktur Sie'

    struktur_sie = fields.Char(string="Struktur Sie")



class Proposal(models.Model):
    _name = 'proposal.dpm'
    _description = 'Proposal DPM FIK'

    tempat = fields.Text(string="Tempat")
    id_proker = fields.Many2one('proker.dpm', string="Program Kerja")
    id_komisi = fields.Many2one('komisi.dpm', string="Komisi")

    @api.model
    def _set_create_date(self):
        return fields.Date.today()
    
    tgl_mulai = fields.Date(string="Tanggal Mulai", default=_set_create_date)
    tgl_selesai = fields.Date(string="Tanggal Selesai", compute='_compute_tgl_selesai', inverse='_inverse_tgl_selesai')
    
    @api.onchange('tgl_mulai')
    def _onchange_tgl_mulai(self):
        if self.tgl_mulai:
            self.waktu_mulai = self.tgl_mulai
            
    waktu_mulai = fields.Datetime(string="Waktu Mulai")
    tema = fields.Text(string="Tema Kegiatan")
    maksud_tujuan = fields.Text(string="Maksud dan Tujuan")
    latarBelakang = fields.Text(string="Latar Belakang")
    dasarPenyelenggaraan = fields.Text(string="Dasar Penyelenggaraan")
    penutup = fields.Text(string="Penutup")
    lama_pelaksanaan = fields.Integer(string="Lama Pelaksanaan (Hari)")
    angka_pertama = fields.Integer(string="Angka Pertama")
    angka_kedua = fields.Integer(string="Angka Kedua")

    @api.depends('angka_pertama', 'angka_kedua')
    def _compute_total_perjumlahan(self):
        for rec in self:
            rec.total = rec.angka_pertama + rec.angka_kedua
    total = fields.Integer(string="Total Perjumlahan", compute ='_compute_total_perjumlahan')

    @api.depends('tgl_mulai','lama_pelaksanaan')
    def _compute_tgl_selesai(self):
        for rec in self:
            if rec.tgl_mulai and rec.lama_pelaksanaan:
                rec.tgl_selesai = rec.tgl_mulai + timedelta(days=rec.lama_pelaksanaan)
            else:
                rec.tgl_selesai = False
    def _inverse_tgl_selesai(self):
        for rec in self:
            rec.lama_pelaksanaan = (rec.tgl_selesai - rec.tgl_mulai).days

    @api.constrains('lama_pelaksanaan')
    def _check_lama_pelaksanaan(self):
        for rec in self:
            if rec.tgl_selesai < rec.tgl_mulai:
                raise ValidationError("tanggal selesai tidak boleh sebelum tanggal mulai")

class LPJ(models.Model):
    _name = 'lpj.dpm'
    _description = 'LPJ DPM FIK'

    hasil = fields.Text(string="Hasil Kegiatan")
    waktu_realisasi = fields.Text(string="Waktu")
    keterangan_acara = fields.Char(string="Keterangan")
    realisasi_dana = fields.Integer(string="Realisasi Dana Pengeluaran")
    dana = fields.Integer(string="Dana Akademik")
    item = fields.Text(string="Nama Item")
    jumlah = fields.Integer(string="Jumlah")
    harga = fields.Integer(string="Harga")
