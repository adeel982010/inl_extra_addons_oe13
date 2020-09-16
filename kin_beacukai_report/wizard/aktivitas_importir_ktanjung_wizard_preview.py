# -*- coding: utf-8 -*-

import base64
import locale
import xlwt

from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import StringIO, BytesIO

from odoo import tools
from odoo.exceptions import Warning
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from . import xls_format


class AktivitasImportirKtanjungWizard(models.TransientModel):
    _inherit = 'aktivitas.importir.ktanjung.wizard'

    date_start = fields.Date(
        'Date Start', default=lambda *a: datetime.today().date() + relativedelta(day=1))
    date_end = fields.Date(
        'Date End', default=lambda *a: datetime.today().date() + relativedelta(day=31))

    @api.onchange('date_start', 'date_end')
    def onchange_date(self):
        """
        This onchange method is used to check end date should be greater than
        start date.
        """
        if self.date_start and self.date_end and \
                self.date_start > self.date_end:
            raise Warning(_('End date must be greater than start date'))


    def get_result(self):
        data = self.read()[0]

        start_date = data.get('date_start', False)
        end_date = data.get('date_end', False)
        if start_date and end_date and end_date < start_date:
            raise Warning(_("End date should be greater than start date!"))

        where_start_date = " 1=1 "
        if start_date:
            where_start_date = " sm.date + interval '7 hour' >= '%s 00:00:00' " % start_date
        where_end_date = " 1=1 "
        if end_date:
            where_end_date = " sm.date + interval '7 hour' <= '%s 23:59:59'" % end_date


        query = """
                SELECT 
                    MIN(sp.jenis_dokumen) AS jenis_dokumen, sp.no_dokumen, sp.tanggal_dokumen, MIN(sp.name) AS in_no, 
                    MIN(sp.date_done) AS min_date, MIN(rp.name) AS nama_mitra,
                    MIN(out.jenis_dok_out) AS jenis_out, MIN(out.no_dok_out) AS dok_no_out, MIN(out.tgl_dok_out) AS dok_date_out
                FROM stock_move_line sml
                LEFT JOIN stock_move sm ON sml.move_id = sm.id
                LEFT JOIN stock_picking sp ON sml.picking_id=sp.id 
                LEFT JOIN res_partner rp ON sp.partner_id=rp.id
                LEFT JOIN product_product pp ON pp.id=sml.product_id
                LEFT JOIN uom_uom uu ON uu.id=sml.product_uom_id
                LEFT JOIN product_template pt ON pt.id=pp.product_tmpl_id
                LEFT JOIN stock_picking_type spt ON spt.id=sm.picking_type_id
                LEFT JOIN res_currency rc ON rc.id = sp.currency_id
                LEFT JOIN (
                    SELECT sml.lot_id, MIN(sp.jenis_dokumen) AS jenis_dok_out, MIN(sp.no_dokumen) AS no_dok_out, 
                        MIN(sp.tanggal_dokumen) AS tgl_dok_out, SUM(qty_done) AS qty_out
                    FROM stock_move_line sml
                    LEFT JOIN stock_move sm ON sml.move_id = sm.id
                    LEFT JOIN stock_picking sp ON sml.picking_id = sp.id
                    WHERE  sm.state = 'done' 
                    AND (sm.location_id = '29' AND sm.location_dest_id != '29')
                    AND """ + where_start_date + """ 
                    AND """ + where_end_date + """
                    GROUP BY sml.lot_id
                ) out ON out.lot_id = sml.lot_id
                WHERE  sm.state = 'done' 
                AND sp.jenis_dokumen != ''
                AND (sm.location_id != '29' AND sm.location_dest_id = '29')
                AND """ + where_start_date + """ 
                AND """ + where_end_date + """
                GROUP BY sp.tanggal_dokumen, sp.no_dokumen
                ORDER BY sp.tanggal_dokumen ASC, sp.no_dokumen ASC
            """
        list_data = []

        self._cr.execute(query)
        vals = self._cr.fetchall()

        no = 1
        for val in vals:
            list_data.append({
                'jenis_dokumen': val[0],
                'nomor_pabean': val[1],
                'tanggal_pabean': val[2],
                'nomor_penerimaan_barang': val[3],
                'tanggal_penerimaan_barang': val[4],
                'pemasok_pengirim': val[5],
                'jenis_dok_out': val[6],
                'no_dok_out': val[7],
                'tgl_dok_out': val[8]
            })
            no += 1
        hasil = list_data
        return hasil

    def print_inventory_preview_report(self):
        return self.env.ref('kin_beacukai_report.aktivitas_importir_ktanjung').report_action(self)
