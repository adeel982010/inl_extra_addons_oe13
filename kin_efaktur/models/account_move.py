# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import re
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

FK_HEAD_LIST = ['FK', 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR', 'MASA_PAJAK', 'TAHUN_PAJAK', 'TANGGAL_FAKTUR', 'NPWP', 'NAMA', 'ALAMAT_LENGKAP', 'JUMLAH_DPP', 'JUMLAH_PPN', 'JUMLAH_PPNBM', 'ID_KETERANGAN_TAMBAHAN', 'FG_UANG_MUKA', 'UANG_MUKA_DPP', 'UANG_MUKA_PPN', 'UANG_MUKA_PPNBM', 'REFERENSI']

LT_HEAD_LIST = ['LT', 'NPWP', 'NAMA', 'JALAN', 'BLOK', 'NOMOR', 'RT', 'RW', 'KECAMATAN', 'KELURAHAN', 'KABUPATEN', 'PROPINSI', 'KODE_POS', 'NOMOR_TELEPON']

OF_HEAD_LIST = ['OF', 'KODE_OBJEK', 'NAMA', 'HARGA_SATUAN', 'JUMLAH_BARANG', 'HARGA_TOTAL', 'DISKON', 'DPP', 'PPN', 'TARIF_PPNBM', 'PPNBM']


def _csv_row(data, delimiter=',', quote='"'):
    return quote + (quote + delimiter + quote).join([str(x).replace(quote, '\\' + quote) for x in data]) + quote + '\n'


class AccountMove(models.Model):
    _inherit = "account.move"

    tax_date = fields.Date(string="Tax Date", required=False, )

    def _generate_efaktur_invoice(self, delimiter):
        """Generate E-Faktur for customer invoice."""
        # Invoice of Customer
        company_id = self.company_id
        dp_product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')

        output_head = '%s%s%s' % (
            _csv_row(FK_HEAD_LIST, delimiter),
            _csv_row(LT_HEAD_LIST, delimiter),
            _csv_row(OF_HEAD_LIST, delimiter),
        )

        for move in self.filtered(lambda m: m.state == 'posted'):
            if not move.tax_date:
                raise UserError(_('Tax date must be defined in invoice ' + move.name))
            eTax = move._prepare_etax()

            credit_notes = self.env['account.move'].search([
                ('state', '=', 'posted'),
                ('type', '=', 'out_refund'),
                ('ref', '=', move.name)])

            dpp_credit_notes = 0
            ppn_credit_notes = 0
            credit_notes_detail = {}
            if credit_notes:
                dpp_credit_notes = sum(credit_notes.mapped('amount_untaxed'))
                ppn_credit_notes = sum(credit_notes.mapped('amount_tax'))
                for line_cn in credit_notes.line_ids.filtered(lambda l: not l.exclude_from_invoice_tab):
                    credit_notes_detail['product_id'] = line_cn.product_id
                    credit_notes_detail['quantity'] = line_cn.quantity
                    credit_notes_detail['dpp'] = line_cn.price_subtotal
                    credit_notes_detail['ppn'] = line_cn.price_total - line_cn.price_subtotal

            nik = str(move.partner_id.l10n_id_nik) if not move.partner_id.vat else ''

            if move.l10n_id_replace_invoice_id:
                number_ref = str(move.l10n_id_replace_invoice_id.name) + " replaced by " + str(move.name) + " " + nik
            else:
                number_ref = str(move.name) + " " + nik

            street = ', '.join([x for x in (move.partner_id.street, move.partner_id.street2) if x])

            invoice_npwp = '000000000000000'
            if not move.partner_id.vat:
                if move.partner_id.vat and len(move.partner_id.vat) >= 12:
                    invoice_npwp = move.partner_id.vat
                elif (not move.partner_id.vat or len(move.partner_id.vat) < 12) and move.partner_id.l10n_id_nik:
                    invoice_npwp = move.partner_id.l10n_id_nik
                invoice_npwp = invoice_npwp.replace('.', '').replace('-', '')

            # Here all fields or columns based on eTax Invoice Third Party
            eTax['KD_JENIS_TRANSAKSI'] = move.l10n_id_tax_number[0:2] or 0
            eTax['FG_PENGGANTI'] = move.l10n_id_tax_number[2:3] or 0
            eTax['NOMOR_FAKTUR'] = move.l10n_id_tax_number[3:] or 0
            eTax['MASA_PAJAK'] = move.tax_date.month
            eTax['TAHUN_PAJAK'] = move.tax_date.year
            eTax['TANGGAL_FAKTUR'] = '{0}/{1}/{2}'.format(move.tax_date.day, move.tax_date.month, move.tax_date.year)
            eTax['NPWP'] = invoice_npwp
            eTax['NAMA'] = move.partner_id.name if eTax['NPWP'] == '000000000000000' else move.partner_id.l10n_id_tax_name or move.partner_id.name
            eTax['ALAMAT_LENGKAP'] = move.partner_id.contact_address.replace('\n', '') if eTax['NPWP'] == '000000000000000' else move.partner_id.l10n_id_tax_address or street
            eTax['JUMLAH_DPP'] = int(round((move.amount_untaxed - dpp_credit_notes), 0)) # currency rounded to the unit
            eTax['JUMLAH_PPN'] = int(round((move.amount_tax - ppn_credit_notes), 0))
            eTax['ID_KETERANGAN_TAMBAHAN'] = '1' if move.l10n_id_kode_transaksi == '07' else ''
            eTax['REFERENSI'] = number_ref

            lines = move.line_ids.filtered(lambda x: x.product_id.id == int(dp_product_id) and x.price_unit < 0)
            eTax['FG_UANG_MUKA'] = 0
            eTax['UANG_MUKA_DPP'] = int(abs(sum(lines.mapped('price_subtotal'))))
            eTax['UANG_MUKA_PPN'] = int(abs(sum(lines.mapped(lambda l: l.price_total - l.price_subtotal))))

            company_npwp = company_id.partner_id.vat or '000000000000000'

            fk_values_list = ['FK'] + [eTax[f] for f in FK_HEAD_LIST[1:]]
            eTax['JALAN'] = company_id.partner_id.l10n_id_tax_address or company_id.partner_id.street
            eTax['NOMOR_TELEPON'] = company_id.phone or ''

            lt_values_list = ['', company_npwp, company_id.name] + [eTax[f] for f in LT_HEAD_LIST[3:]]

            # HOW TO ADD 2 line to 1 line for free product
            free, sales = [], []

            for line in move.line_ids.filtered(lambda l: not l.exclude_from_invoice_tab):
                # *invoice_line_unit_price is price unit use for harga_satuan's column
                # *invoice_line_quantity is quantity use for jumlah_barang's column
                # *invoice_line_total_price is bruto price use for harga_total's column
                # *invoice_line_discount_m2m is discount price use for diskon's column
                # *line.price_subtotal is subtotal price use for dpp's column
                # *tax_line or free_tax_line is tax price use for ppn's column
                # free_tax_line =
                tax_line = bruto_total = total_discount = 0.0

                for tax in line.tax_ids:
                    if tax.amount > 0:
                        tax_line += line.price_subtotal * (tax.amount / 100.0)

                invoice_line_unit_price = line.price_unit

                invoice_line_total_price = invoice_line_unit_price * line.quantity

                # for credit notes
                quantity = line.quantity
                price_subtotal = line.price_subtotal
                if credit_notes:
                    if line.product_id == credit_notes_detail['product_id']:
                        quantity -= credit_notes_detail['quantity']
                        price_subtotal -= credit_notes_detail['dpp']
                        tax_line -= credit_notes_detail['ppn']

                line_dict = {
                    'KODE_OBJEK': line.product_id.default_code or '',
                    'NAMA': line.product_id.name or '',
                    'HARGA_SATUAN': int(invoice_line_unit_price),
                    'JUMLAH_BARANG': line.quantity,
                    'HARGA_TOTAL': int(invoice_line_total_price),
                    'DPP': int(price_subtotal),
                    'product_id': line.product_id.id,
                }

                # if price_subtotal < 0:
                #     for tax in line.tax_ids:
                #         free_tax_line += (line.price_subtotal * (tax.amount / 100.0)) * -1.0
                #
                #     # for credit notes
                #     if credit_notes:
                #         if line.product_id == credit_notes_detail['product_id']:
                #             free_tax_line -= credit_notes_detail['ppn']
                #
                #     line_dict.update({
                #         'DISKON': int(invoice_line_total_price - price_subtotal),
                #         'PPN': int(free_tax_line),
                #     })
                #     free.append(line_dict)
                # elif price_subtotal != 0.0:
                invoice_line_discount_m2m = invoice_line_total_price - price_subtotal

                line_dict.update({
                    'DISKON': int(invoice_line_discount_m2m),
                    'PPN': int(tax_line),
                })
                sales.append(line_dict)

            sub_total_before_adjustment = sub_total_ppn_before_adjustment = 0.0

            # We are finding the product that has affected
            # by free product to adjustment the calculation
            # of discount and subtotal.
            # - the price total of free product will be
            # included as a discount to related of product.
            for sale in sales:
                for f in free:
                    if f['product_id'] == sale['product_id']:
                        sale['DISKON'] = sale['DISKON'] - f['DISKON'] + f['PPN']
                        sale['DPP'] = sale['DPP'] + f['DPP']

                        tax_line = 0

                        for tax in line.tax_ids:
                            if tax.amount > 0:
                                tax_line += sale['DPP'] * (tax.amount / 100.0)

                        sale['PPN'] = int(tax_line)

                        free.remove(f)

                sub_total_before_adjustment += sale['DPP']
                sub_total_ppn_before_adjustment += sale['PPN']
                bruto_total += sale['DISKON']
                total_discount += round(sale['DISKON'], 2)

            output_head += _csv_row(fk_values_list, delimiter)
            output_head += _csv_row(lt_values_list, delimiter)
            for sale in sales:
                of_values_list = ['OF'] + [str(sale[f]) for f in OF_HEAD_LIST[1:-2]] + ['0', '0']
                output_head += _csv_row(of_values_list, delimiter)

        return output_head
