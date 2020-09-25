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


class InventoryExcelPengeluaranKtanjungExportSummary(models.TransientModel):
    _name = "inventory.excel.pengeluaran.ktanjung.export.summary"

    file = fields.Binary(
        "Click On Save As Button To Download File", readonly=True)
    name = fields.Char("Name", size=32, default='laporan_pengeluaran_ktanjung.xls')


class InventoryExportPengeluaranKtanjungReportWizard(models.TransientModel):
    _name = 'inventory.export.pengeluaran.ktanjung.report.wizard'

    date_start = fields.Date(
        'Date Start', default=lambda *a: datetime.today().date() + relativedelta(day=1))
    date_end = fields.Date(
        'Date End', default=lambda *a: datetime.today().date() + relativedelta(day=31))
    location_ids = fields.Many2many('stock.location', 'pengeluaran_ktanjung_locaton_rel', 'stock_card_id',
                                    'location_id', 'Lokasi', copy=False, domain=[('usage', '=', 'internal')])
    categ_ids = fields.Many2many('product.category', 'pengeluaran_ktanjung_categ_rel', 'stock_card_id',
                                 'categ_id', 'Kategori Produk', copy=False)
    product_ids = fields.Many2many('product.product', 'pengeluaran_ktanjung_product_rel', 'stock_card_id',
                                   'product_id', 'Produk', copy=False, domain=[('type', '=', 'product')])
    export_report = fields.Selection([('BC 2.5', 'BC 2.5'), ('BC 2.6.1', 'BC 2.6.1'), (
        'BC 2.7', 'BC 2.7'), ('BC 3.0', 'BC 3.0'), ('BC 4.1', 'BC 4.1')], "Report Type", default='')

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
        res_user = self.env["res.users"].browse(self._uid)
        export = data.get('export_report', False)

        # Create Inventory Export report in Excel file.
        workbook = xlwt.Workbook(style_compression=2)
        worksheet = workbook.add_sheet('Sheet 1')
        font = xlwt.Font()
        font.bold = True
        header = xlwt.easyxf('font: bold 1, height 280')
        # start_date = datetime.strptime(str(context.get("date_from")), DEFAULT_SERVER_DATE_FORMAT)
        # start_date_formate = start_date.strftime('%d/%m/%Y')
        # end_date = datetime.strptime(str(context.get("date_to")), DEFAULT_SERVER_DATE_FORMAT)
        # end_date_formate = end_date.strftime('%d/%m/%Y')
        # start_date_to_end_date = tools.ustr(start_date_formate) + ' To ' + tools.ustr(end_date_formate)

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
        style = xlwt.easyxf('align: wrap yes', style)

        ids_location = []
        ids_categ = []
        ids_product = []
        where_end_date_awal = " sm.date is null "
        where_start_date = " 1=1 "
        if start_date:
            where_start_date = " sm.date + interval '7 hour' >= '%s 00:00:00' " % start_date
            where_end_date_awal = " sm.date + interval '7 hour' < '%s 00:00:00' " % start_date
        where_end_date = " 1=1 "
        if end_date:
            where_end_date = " sm.date + interval '7 hour' <= '%s 23:59:59'" % end_date
        where_location = " 1=1 "
        if ids_location:
            where_location = """(sm.location_id in %s 
            or sm.location_dest_id in %s)""" % (str(tuple(ids_location)).replace(',)', ')'),
                                                str(tuple(ids_location)).replace(',)', ')'))
        where_categ = " 1=1 "
        if ids_categ:
            where_categ = "pt.categ_id in %s" % str(
                tuple(ids_categ)).replace(',)', ')')
        where_product = " 1=1 "
        if ids_product:
            where_product = "pp.id in %s" % str(
                tuple(ids_product)).replace(',)', ')')

        where_export = "AND sp.jenis_dokumen NOT IN ('', 'Non BC')"
        if export == "AND sp.jenis_dokumen = 'BC 2.5'":
            where_export = "BC 2.5"
        elif export == "AND sp.jenis_dokumen = 'BC 2.6.1'":
            where_export = "BC 2.6.1"
        elif export == "BC 2.7":
            where_export = "AND sp.jenis_dokumen = 'BC 2.7'"
        elif export == "BC 3.0":
            where_export = "AND sp.jenis_dokumen = 'BC 3.0'"
        elif export == "BC 3.3":
            where_export = "AND sp.jenis_dokumen = 'BC 3.3'"
        elif export == "BC 4.1":
            where_export = "AND sp.jenis_dokumen = 'BC 4.1'"

        query = """
                SELECT 
                    sp.jenis_dokumen, sp.no_dokumen AS no_dokumen_pabean, sp.tanggal_dokumen AS tanggal_dokumen_pabean, sp.name AS no_dokumen, 
                    sp.date_done AS tanggal_dokumen, rp.name AS nama_mitra, pp.default_code AS kode_barang, pt.name AS nama_barang, uu.name, 
                    sm.product_uom_qty, coalesce(sm.subtotal_price,0) AS nilai_barang, spt.code AS status_type, rc.symbol,
                    sp.no_aju 
                FROM stock_move sm 
                INNER JOIN stock_picking sp ON sm.picking_id=sp.id 
                LEFT JOIN res_partner rp ON sp.partner_id=rp.id
                LEFT JOIN product_product pp ON pp.id=sm.product_id
                LEFT JOIN uom_uom uu ON uu.id=sm.product_uom
                LEFT JOIN product_template pt ON pt.id=pp.product_tmpl_id
                LEFT JOIN stock_picking_type spt ON spt.id=sm.picking_type_id
                LEFT JOIN sale_order_line sol ON sol.id=sm.sale_line_id
                LEFT JOIN res_currency rc ON rc.id = sp.currency_id
                WHERE sm.state = 'done' 
                AND (sm.location_id = '29' AND sm.location_dest_id != '29')
                AND """ + where_start_date + """ 
                AND """ + where_end_date + """                  
                """ + where_export + """
                ORDER BY sp.tanggal_dokumen ASC, sp.no_dokumen ASC 
            """
        self._cr.execute(query)
        hasil = self._cr.fetchall()

        company = self.env.user.company_id.name
        start_date_format = start_date.strftime('%d/%m/%Y')
        end_date_format = end_date.strftime('%d/%m/%Y')
        # date_format = xlwt.XFStyle()
        # date_format.num_format_str = 'dd/mm/yyyy'

        worksheet.write_merge(1, 1, 0, 4, "LAPORAN PENGELUARAN BARANG PER DOKUMEN " + export + " (Kuala Tanjung)",
                              xls_format.font_style(position='left', bold=1, fontos='black', font_height=300))
        worksheet.write_merge(2, 2, 0, 4, "" + str(company).upper(
        ), xls_format.font_style(position='left', bold=1, fontos='black', font_height=300))
        worksheet.write_merge(3, 3, 0, 4, "LAPORAN PENGELUARAN BARANG PER DOKUMEN " + export,
                              xls_format.font_style(position='left', bold=1, fontos='black', font_height=300))
        worksheet.write_merge(5, 5, 0, 1, "PERIODE : " + str(start_date_format) + " S.D " + str(
            end_date_format), xls_format.font_style(position='left', bold=1, fontos='black', font_height=200))

        row = 7
        worksheet.write_merge(7, 8, 0, 0, "No", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write_merge(7, 8, 1, 1, "Jenis Dokumen", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write_merge(7, 8, 2, 2, "No Aju", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write_merge(7, 7, 3, 4, "Dokumen Pabean", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write(8, 3, "Nomor", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write(8, 4, "Tanggal", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write_merge(7, 7, 5, 6, "Bukti/Dokumen Pengeluaran", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write(8, 5, "Nomor", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write(8, 6, "Tanggal", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write_merge(7, 8, 7, 7, "Pembeli/Penerima", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write_merge(7, 8, 8, 8, "Kode Barang", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write_merge(7, 8, 9, 9, "Nama Barang", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write_merge(7, 8, 10, 10, "Sat", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write_merge(7, 8, 11, 11, "Jumlah", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write_merge(7, 8, 12, 12, "Currency", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))
        worksheet.write_merge(7, 8, 13, 13, "Nilai Barang", xls_format.font_style(
            position='center', bold=1, border=1, fontos='black', font_height=200, color='grey'))

        row += 2
        no = 1
        for val in hasil:
            worksheet.write(row, 0, no, xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 1, val[0], xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 2, val[13], xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 3, val[1], xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 4, str(val[2].strftime('%d/%m/%Y')), xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 5, val[3], xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 6, str(val[4].strftime('%d/%m/%Y')), xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 7, val[5], xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 8, val[6], xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 9, val[7], xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 10, val[8], xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 11, val[9], xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 12, val[12], xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            worksheet.write(row, 13, val[10], xls_format.font_style(
                position='center', border=1, fontos='black', font_height=200, color='false'))
            row += 1
            no += 1

        fp = BytesIO()
        workbook.save(fp)
        res = base64.encodestring(fp.getvalue())
        res_id = self.env['inventory.excel.pengeluaran.ktanjung.export.summary'].create(
            {'name': 'Laporan Pengeluaran Barang (Kuala Tanjung).xls', 'file': res})

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=inventory.excel.pengeluaran.ktanjung.export.summary&field=file&id=%s&filename=Laporan Pengeluaran Barang (Kuala Tanjung).xls' % (res_id.id),
            'target': 'new',
        }