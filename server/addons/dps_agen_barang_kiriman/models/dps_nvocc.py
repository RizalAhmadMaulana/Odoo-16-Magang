from odoo import models, fields, api, _

class DpsNvocc(models.Model):
    _name = 'dps.nvocc'
    _description = 'Data Master NVOCC Manifest'
    _inherit = 'mail.thread'

    # Header Data (Data Manifest Utama)
    kode_kantor = fields.Char(string='Kode Kantor', size=6)
    jenis_manifes = fields.Char(string='Jenis Manifes')
    id_perusahaan = fields.Char(string='ID Perusahaan')
    nama_perusahaan = fields.Char(string='Nama Perusahaan')
    alamat_perusahaan = fields.Char(string='Alamat Perusahaan')
    nomor_aju = fields.Char(string='Nomor Aju', copy=False, index=True)
    nomor_voyage = fields.Char(string='Nomor Voyage')
    tanggal_berangkat = fields.Datetime(string='Tanggal Berangkat')
    tanggal_tiba = fields.Datetime(string='Tanggal Tiba')
    mode_pengangkut = fields.Char(string='Mode Pengangkut')
    nama_sarana_pengangkut = fields.Char(string='Nama Sarana Pengangkut')
    imo_number = fields.Char(string='IMO Number')
    kode_negara = fields.Char(string='Kode Negara')
    asal_data = fields.Char(string='Asal Data')
    fl_waktu_tempuh = fields.Integer(string='Waktu Tempuh (Jam)')

    # Relasi One2many
    data_kelompok_pos_ids = fields.One2many(
        'dps.nvocc.kelompok.pos', 
        'nvocc_id', 
        string='Kelompok Pos'
    )
    master_bl_ids = fields.One2many(
        'dps.nvocc.master.bl', 
        'nvocc_id', 
        string='Master B/L'
    )
    data_bl_ids = fields.One2many(
        'dps.nvocc.bl', 
        'nvocc_id', 
        string='Data B/L Detil'
    )
    
    # Sequence untuk Nomor Aju
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            # Pastikan 'dps.nvocc' adalah kode sequence yang benar
            vals['name'] = self.env['ir.sequence'].next_by_code('dps.nvocc') or _('New')
        return super(DpsNvocc, self).create(vals)

# -----------------------------------------------------------------------------
# SUB-MODEL 1: Kelompok Pos (dataKelompokPos)
# -----------------------------------------------------------------------------

class DpsNvoccKelompokPos(models.Model):
    _name = 'dps.nvocc.kelompok.pos'
    _description = 'Detil Kelompok Pos Manifest'
    
    nvocc_id = fields.Many2one('dps.nvocc', string='NVOCC Reference', ondelete='cascade')
    kode_kelompok_pos = fields.Char(string='Kode Kelompok Pos', default='00')
    jumlah = fields.Integer(string='Jumlah', default=0)

# -----------------------------------------------------------------------------
# SUB-MODEL 2: Master B/L (masterBls)
# -----------------------------------------------------------------------------

class DpsNvoccMasterBl(models.Model):
    _name = 'dps.nvocc.master.bl'
    _description = 'Detil Master B/L'
    _rec_name = 'master_bl'
    
    nvocc_id = fields.Many2one('dps.nvocc', string='NVOCC Reference', ondelete='cascade')
    kelompok_pos = fields.Char(string='Kelompok Pos')
    master_bl = fields.Char(string='Nomor Master B/L')
    tanggal_bl = fields.Date(string='Tanggal Master B/L')
    jumlah_pos = fields.Integer(string='Jumlah Pos')

# -----------------------------------------------------------------------------
# SUB-MODEL 3: Data B/L Detil (dataBls) - Master B/L atau Host B/L
# -----------------------------------------------------------------------------

class DpsNvoccBl(models.Model):
    _name = 'dps.nvocc.bl'
    _description = 'Detil B/L / Host B/L'
    _rec_name = 'nomor_host_bl'
    
    nvocc_id = fields.Many2one('dps.nvocc', string='NVOCC Reference', ondelete='cascade')
    
    kelompok_pos_id = fields.Many2one(
        'dps.nvocc.kelompok.pos', 
        string='Pilih Kelompok Pos', 
        ondelete='restrict'
    )
    
    kode_kelompok_pos = fields.Char(
        string='Kode Kelompok Pos', 
        related='kelompok_pos_id.kode_kelompok_pos', 
        store=True,
        readonly=True
    )

    # Data Utama B/L
    # kode_kelompok_pos = fields.Many2one('dps.nvocc.kelompok.pos', string='Kode Kelompok Pos', ondelete='cascade')
    nomor_pos = fields.Char(string='Nomor Pos')
    nomor_bl = fields.Char(string='Nomor B/L (Master B/L)')
    tanggal_bl = fields.Date(string='Tanggal B/L')
    nomor_host_bl = fields.Char(string='Nomor Host B/L', index=True)
    tanggal_host_bl = fields.Date(string='Tanggal Host B/L')
    marking = fields.Text(string='Marking')

    # Pihak Terkait
    npwp_pengirim = fields.Char(string='NPWP Pengirim')
    nama_pengirim = fields.Char(string='Nama Pengirim')
    alamat_pengirim = fields.Char(string='Alamat Pengirim')
    npwp_penerima = fields.Char(string='NPWP Penerima')
    nama_penerima = fields.Char(string='Nama Penerima')
    alamat_penerima = fields.Char(string='Alamat Penerima')
    npwp_notify = fields.Char(string='NPWP Notify')
    nama_notify = fields.Char(string='Nama Notify')
    alamat_notify = fields.Char(string='Alamat Notify')
    
    # Data Kuantitas & Lokasi
    berat = fields.Float(string='Berat (Kg)')
    dimensi = fields.Float(string='Dimensi')
    jumlah_container = fields.Integer(string='Jumlah Container')
    jenis_kemasan = fields.Char(string='Jenis Kemasan (Kode)')
    jumlah_kemasan = fields.Integer(string='Jumlah Kemasan')
    mother_vessel = fields.Char(string='Mother Vessel')
    
    # Pelabuhan
    kode_pelabuhan_asal = fields.Char(string='Pelabuhan Asal (Kode)')
    kode_pelabuhan_bongkar = fields.Char(string='Pelabuhan Bongkar (Kode)')
    kode_pelabuhan_transit = fields.Char(string='Pelabuhan Transit (Kode)')
    kode_pelabuhan_akhir = fields.Char(string='Pelabuhan Akhir (Kode)')
    
    # Status Kemasan
    jumlah_container_tertinggal = fields.Integer(string='Container Tertinggal')
    jumlah_kemasan_tertinggal = fields.Integer(string='Kemasan Tertinggal')
    jumlah_kemasan_terangkut = fields.Integer(string='Kemasan Terangkut')

    # Flags
    flag_konsolidasi = fields.Char(string='Flag Konsolidasi')
    flag_parsial = fields.Char(string='Flag Parsial')
    flag_partof = fields.Char(string='Flag Part of')
    
    # Relasi One2many ke sub-detil
    bl_hs_ids = fields.One2many('dps.nvocc.bl.hs', 'bl_id', string='Detil HS Code')
    bl_petikemas_terangkut_ids = fields.One2many(
        'dps.nvocc.container', 
        'bl_id', 
        string='Petikemas Terangkut'
    )
    bl_petikemas_tertinggal_ids = fields.One2many(
        'dps.nvocc.container.tertinggal', 
        'bl_id', 
        string='Petikemas Tertinggal'
    )
    bl_dokumen_ids = fields.One2many('dps.nvocc.bl.dokumen', 'bl_id', string='Dokumen Terkait')


# -----------------------------------------------------------------------------
# SUB-MODEL 4: Detil HS Code (blHs)
# -----------------------------------------------------------------------------

class DpsNvoccBlHs(models.Model):
    _name = 'dps.nvocc.bl.hs'
    _description = 'Detil HS Code'
    _rec_name = 'kode_hs'
    
    bl_id = fields.Many2one('dps.nvocc.bl', string='B/L Reference', ondelete='cascade')
    seri_hs = fields.Integer(string='Seri HS')
    kode_hs = fields.Char(string='Kode HS')
    uraian_barang = fields.Text(string='Uraian Barang')

# -----------------------------------------------------------------------------
# SUB-MODEL 5: Detil Petikemas Terangkut (blPetikemasTerangkut)
# -----------------------------------------------------------------------------

class DpsNvoccContainer(models.Model):
    _name = 'dps.nvocc.container'
    _description = 'Detil Petikemas Terangkut'
    _rec_name = 'nomor_container'
    
    bl_id = fields.Many2one('dps.nvocc.bl', string='B/L Reference', ondelete='cascade')
    seri_container = fields.Integer(string='Seri Container')
    nomor_container = fields.Char(string='Nomor Container')
    fl_b3 = fields.Char(string='Flag B3')
    fl_terangkut = fields.Char(string='Flag Terangkut')
    status = fields.Char(string='Status Container')
    type_container = fields.Char(string='Tipe Container')
    ukuran_container = fields.Char(string='Ukuran Container')
    nomor_segel = fields.Char(string='Nomor Segel')
    nomor_polisi = fields.Char(string='Nomor Polisi')
    jenis_container = fields.Char(string='Jenis Container (Kode)')
    jenis_muat = fields.Char(string='Jenis Muat')
    driver = fields.Char(string='Nama Driver')

# -----------------------------------------------------------------------------
# SUB-MODEL 6: Detil Petikemas Tertinggal (blPetikemasTertinggals)
# -----------------------------------------------------------------------------

class DpsNvoccContainerTertinggal(models.Model):
    _name = 'dps.nvocc.container.tertinggal'
    _description = 'Detil Petikemas Tertinggal'
    _rec_name = 'nomor_container'
    
    bl_id = fields.Many2one('dps.nvocc.bl', string='B/L Reference', ondelete='cascade') 
    
    nomor_container = fields.Char(string='Nomor Container Tertinggal')
    keterangan = fields.Char(string='Keterangan')

# -----------------------------------------------------------------------------
# SUB-MODEL 7: Detil Dokumen (blDokumen)
# -----------------------------------------------------------------------------

class DpsNvoccBlDokumen(models.Model):
    _name = 'dps.nvocc.bl.dokumen'
    _description = 'Detil Dokumen B/L'
    
    bl_id = fields.Many2one('dps.nvocc.bl', string='B/L Reference', ondelete='cascade')
    # Anda dapat menambahkan field untuk detil dokumen di sini.