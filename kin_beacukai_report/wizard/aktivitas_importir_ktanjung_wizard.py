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


class AktivitasImportirKtanjungExportSummary(models.TransientModel):
    _name = "aktivitas.importir.ktanjung.export.summary"

    file = fields.Binary(
        "Click On Save As Button To Download File", readonly=True)
    name = fields.Char("Name", size=32, default='laporan_aktivitas_importir_ktanjung.xls')


class AktivitasImportirKtanjungWizard(models.TransientModel):
    _name = 'aktivitas.importir.ktanjung.wizard'

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


    def print_inventory_export_report(self):
        data = self.read()[0]

        start_date = data.get('date_start', False)
        end_date = data.get('date_end', False)
        if start_date and end_date and end_date < start_date:
            raise Warning(_("End date should be greater than start date!"))

        # Create Inventory Export report in Excel file.
        workbook = xlwt.Workbook(style_compression=2)
        worksheet = workbook.add_sheet('Sheet 1')
        font = xlwt.Font()
        font.bold = True

        style = xlwt.easyxf('align: wrap yes')
        worksheet.row(0).height = 500
        worksheet.row(1).height = 500
        for x in range(0, 41):
            worksheet.col(x).width = 6000
        borders = xlwt.Borders()
        borders.top = xlwt.Borders.MEDIUM
        borders.bottom = xlwt.Borders.MEDIUM
        border_style = xlwt.XFStyle()  # Create Style
        border_style.borders = borders
        border_style1 = xlwt.easyxf('font: bold 1')
        border_style1.borders = borders

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
        self._cr.execute(query)
        vals = self._cr.fetchall()

        company = self.env.user.company_id.name
        start_date_format = start_date.strftime('%d/%m/%Y')
        end_date_format = end_date.strftime('%d/%m/%Y')

        worksheet.write_merge(2, 2, 0, 4, "" + str(company).upper(
        ), xls_format.font_style(position='left', bold=1, fontos='black', font_height=300))
        worksheet.write_merge(3, 3, 0, 4, "LAPORAN AKTIVITAS IMPORTIR", xls_format.font_style(position='left', bold=1, fontos='black', font_height=300))
        worksheet.write_merge(5, 5, 0, 1, "PERIODE : " + str(start_date_format) + " S.D " + str(
            end_date_format), xls_format.font_style(position='left', bold=1, fontos='black', font_height=200))

        row = 7
        worksheet.write_merge(7, 8, 0, 0, "NO", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write_merge(7, 7, 1, 5, "DOKUMEN PEMASUKAN", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write_merge(7, 7, 6, 9, "DOKUMEN PENGELUARAN", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write(8, 1, "Jenis", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write(8, 2, "Nama Importir", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write(8, 3, "Nomor", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write(8, 4, "Tanggal", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write(8, 5, "No. Bukti", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write(8, 6, "Tgl. Bukti", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write(8, 7, "Jenis", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write(8, 8, "Nomor", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write(8, 9, "Tanggal", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))

        row += 2
        no = 1
        for val in vals:
            jenis_dokumen = val[0]
            nomor_pabean = val[1]
            tanggal_pabean = val[2]
            nomor_penerimaan_barang = val[3]
            tanggal_penerimaan_barang = val[4]
            pemasok_pengirim = val[5]
            jenis_dok_out = val[6]
            no_dok_out = val[7]
            tgl_dok_out = val[8]

            worksheet.write(row, 0, no, xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 1, jenis_dokumen, xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 2, pemasok_pengirim, xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 3, nomor_pabean, xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 4, str(tanggal_pabean.strftime('%d/%m/%Y')), xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 5, nomor_penerimaan_barang, xls_format.font_style(
                position='centerexport', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 6, str(tanggal_penerimaan_barang.strftime('%d/%m/%Y')), xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 7, jenis_dok_out, xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 8, no_dok_out, xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 9, str(tgl_dok_out.strftime('%d/%m/%Y')), xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            row += 1
            no += 1

        fp = BytesIO()
        workbook.save(fp)

        res = base64.encodestring(fp.getvalue())
        res_id = self.env['aktivitas.importir.ktanjung.export.summary'].create(
            {'name': 'Laporan Aktivitas Importir (Kuala Tanjung).xls', 'file': res})

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=aktivitas.importir.ktanjung.export.summary&field=file&id=%s&filename=Laporan Aktivitas Importir (Kuala Tanjung).xls' % (res_id.id),
            'target': 'new',
        }