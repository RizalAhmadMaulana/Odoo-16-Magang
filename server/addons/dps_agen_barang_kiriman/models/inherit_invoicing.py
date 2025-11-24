from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    dps_order_id = fields.Many2one(
        'dps.barkir.order', 
        string='DPS Order', 
        readonly=True, 
        copy=False,
        help="Link to the related DPS Order."
    )
    
    # Field Biaya Pengiriman di Header
    dps_shipping_cost = fields.Monetary(
        string='Biaya Pengiriman',
        store=True,
        readonly=True, 
        tracking=True,
        currency_field='currency_id',
        help="Biaya pengiriman diambil dari pricelist DPS Order."
    )
    
    # FIELD BARU: Total Akhir Kustom (untuk ditampilkan di footer)
    amount_total_dps = fields.Monetary(
        string='Total Tagihan',
        compute='_compute_amount_dps',
        store=True,
        currency_field='currency_id'
    )

    # LOGIKA PERHITUNGAN TOTAL KUSTOM
    @api.depends('amount_untaxed', 'amount_tax', 'dps_shipping_cost')
    def _compute_amount_dps(self):
        for move in self:
            # Formula sesuai permintaan: Biaya Pengiriman + Untaxed Amount + Tax
            move.amount_total_dps = move.dps_shipping_cost + move.amount_untaxed + move.amount_tax
            
    # PENTING: HAPUS total override _compute_amount BAWAAN ODOO di sini!
    # Hanya pertahankan field amount_total_dps.


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    x_biaya_pengiriman = fields.Float(
        string='Biaya Pengiriman',
        digits='Product Price',
        help="Biaya pengiriman untuk barang ini, terpisah dari harga produk."
    )