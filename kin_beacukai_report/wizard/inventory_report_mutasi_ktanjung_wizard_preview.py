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


class InventoryPreviewMutasiKtanjungReportWizard(models.TransientModel):
    _inherit = 'inventory.export.mutasi.ktanjung.report.wizard'

    date_start = fields.Date(
        'Date Start', default=lambda *a: datetime.today().date() + relativedelta(day=1))
    date_end = fields.Date(
        'Date End', default=lambda *a: datetime.today().date() + relativedelta(day=31))
    location_ids = fields.Many2many('stock.location', 'mutasi_ktanjung_location_rel', 'stock_mutasi_id',
                                    'location_id', 'Lokasi', copy=False, domain=[('usage', '=', 'internal')])
    categ_ids = fields.Many2many('product.category', 'mutasi_ktanjung_categ_rel', 'stock_mutasi_id',
                                 'categ_id', 'Kategori Produk', copy=False)
    product_ids = fields.Many2many('product.product', 'mutasi_ktanjung_product_rel', 'stock_mutasi_id',
                                   'product_id', 'Produk', copy=False, domain=[('type', '=', 'product')])

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
        res_user = self.env["res.users"].browse(self._uid)

        # Create Inventory Export report in Excel file.
        workbook = xlwt.Workbook()
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

        where_end_date_opn = " 1=1 "
        if end_date:
            where_end_date_opn = " si.date::text LIKE '%s%s'" % (end_date, "%")

        where_location = " 1=1 "
        if ids_location:
            where_location = """(sm.location_id in %s 
            or sm.location_dest_id in %s)""" % (str(tuple(ids_location)).replace(',)', ')'),
                                                str(tuple(ids_location)).replace(',)', ')'))
        where_location_opn = " sil.location_id = 29 "

        where_categ = " 1=1 "
        if ids_categ:
            where_categ = "pt.categ_id in %s" % str(
                tuple(ids_categ)).replace(',)', ')')
        where_product = " 1=1 "
        if ids_product:
            where_product = "pp.id in %s" % str(
                tuple(ids_product)).replace(',)', ')')
        query = """
                select 	pp.id as prod_id, 
				pt.default_code as prod_code, 
				pt.name as prod_name,
				pu.name as uom,
				sum(coalesce(awal.qty,0)) as saldo_awal, 
                sum(coalesce(saldo_masuk.qty,0)) as masuk, 
                sum(coalesce(saldo_keluar.qty,0)) as keluar,
                sum(coalesce(prod_adj.qty,0)) as adjusment,
                sum(coalesce(opn.qty,0)) as opname
                    
                from product_product pp
                    left join
                        (
                            select sm.product_id, 
                            sum(case when sl.complete_name = 'KTJ/Stock' and dl.complete_name != 'KTJ/Stock'
                                then sm.product_qty*-1 
                            when sl.complete_name != 'KTJ/Stock' and dl.complete_name = 'KTJ/Stock'
                                then sm.product_qty else 0 end) as qty
                            
                            from stock_move sm
                            left join stock_location sl on sl.id = sm.location_id
                            left join stock_location dl on dl.id = sm.location_dest_id
                            left join product_product pp on pp.id=sm.product_id
                            left join product_template pt on pt.id=pp.product_tmpl_id
                            left join uom_uom pu on pu.id= sm.product_uom
                            where """ + where_end_date_awal + """ and """ + where_location + """ 
                            and sm.state = 'done'
                            group by sm.product_id
                        ) awal on awal.product_id=pp.id
                        
                    left join 
                        (
                            select sm.product_id, 
                            sum(sm.product_qty) as qty 
                            from stock_move sm
                            left join stock_location sl on sl.id = sm.location_id
                            left join stock_location dl on dl.id = sm.location_dest_id
                            left join product_product pp on pp.id=sm.product_id
                            left join product_template pt on pt.id=pp.product_tmpl_id
                            left join uom_uom pu on pu.id= sm.product_uom
                            where sl.complete_name != 'KTJ/Stock' and dl.complete_name = 'KTJ/Stock' and sm.state = 'done' and sm.inventory_id is null
                            and """ + where_start_date + """ and """ + where_end_date + """ and """ + where_location + """  
                            group by sm.product_id
                        ) saldo_masuk on saldo_masuk.product_id=pp.id
                        
                    left join 
                        (
                            select sm.product_id, sum(sm.product_qty) as qty 
                            from stock_move sm 
                            left join stock_location sl on sl.id = sm.location_id 
                            left join stock_location dl on dl.id = sm.location_dest_id
                            left join product_product pp on pp.id=sm.product_id
                            left join product_template pt on pt.id=pp.product_tmpl_id	
                            left join uom_uom pu on pu.id= sm.product_uom 
                            where sl.complete_name = 'KTJ/Stock' and dl.complete_name != 'KTJ/Stock' and sm.state = 'done' and sm.inventory_id is null
                            and """ + where_start_date + """ and """ + where_end_date + """ and """ + where_location + """
                            group by sm.product_id
                        ) saldo_keluar on saldo_keluar.product_id=pp.id
                
                    left join
                        (
                            select sm.product_id, 
                            sum(case when sl.complete_name LIKE 'KTJ/Stock%' and dl.complete_name NOT LIKE 'KTJ/Stock%' and inventory_id is not null
                                then sm.product_qty*-1 
                            when sl.complete_name NOT LIKE 'KTJ/Stock%' and dl.complete_name LIKE 'KTJ/Stock%' and inventory_id is not null
                                then sm.product_qty else 0 end ) as qty
                            
                            from stock_move sm
                            left join stock_location sl on sl.id = sm.location_id
                            left join stock_location dl on dl.id = sm.location_dest_id
                            left join product_product pp on pp.id=sm.product_id
                            left join product_template pt on pt.id=pp.product_tmpl_id
                            left join uom_uom pu on pu.id= sm.product_uom
                            where """ + where_start_date + """ and """ + where_end_date + """ and """ + where_location + """ and sm.state = 'done'
                            group by sm.product_id
                        ) prod_adj on prod_adj.product_id=pp.id

                    left join
                        (
                            select sil.product_id,
                            sum(sil.product_qty) as qty
                            
                            from stock_inventory_line sil
                            INNER JOIN stock_inventory si on sil.inventory_id = si.id
                            INNER JOIN stock_location sl on sl.id = sil.location_id
                            left join product_product pp on pp.id=sil.product_id
                            left join product_template pt on pt.id=pp.product_tmpl_id
                            left join uom_uom pu on pu.id= sil.product_uom_id
                            where """ + where_end_date_opn + """ and """ + where_location_opn + """ and si.state = 'done'
                            group by sil.product_id
                        ) opn on opn.product_id=pp.id
                
                
                left join product_template pt on pt.id=pp.product_tmpl_id
                left join uom_uom pu on pt.uom_id=pu.id
                left join product_category pc on pt.categ_id=pc.id
                where """ + where_categ + """ and """ + where_product + """ 
                    and pc.report_type IN ('bahan_baku','barang_jadi')
                    and pp.active = 't'
                    and (coalesce(awal.qty,0) != 0 
                    or coalesce(saldo_masuk.qty,0) != 0 
                    or coalesce(saldo_keluar.qty,0) != 0
                    or coalesce(opn.qty,0) != 0) 
                    
                group by pt.default_code, pt.name, pp.id , pu.name 
                    order by pt.name asc
            """
        list_data = []
        company = self.env.user.company_id.name
        start_date_format = start_date.strftime('%d/%m/%Y')
        end_date_format = end_date.strftime('%d/%m/%Y')

        self._cr.execute(query)
        vals = self._cr.fetchall()

        no = 1
        for val in vals:
            saldo_akhir = float(val[4]) + float(val[5]) - \
                float(val[6]) + float(val[7])
            selisih = saldo_akhir - float(val[8])
            list_data.append({
                'no': val[0],
                'kode_barang': val[1],
                'nama_barang': val[2],
                'satuan': val[3],
                'saldo_awal': val[4],
                'pemasukan': val[5],
                'pengeluaran': val[6],
                'penyesuaian': val[7],
                'saldo_akhir': saldo_akhir,
                'stock_opname': val[8],
                'selisih': selisih,
                'keterangan': ""
            })
            no += 1
        hasil = list_data
        return hasil


    def print_inventory_preview_report(self):
        return self.env.ref('kin_beacukai_report.report_inventory_mutasi_ktanjung').report_action(self)
