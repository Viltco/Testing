# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MrpInh(models.Model):
    _inherit = 'mrp.production'

    picking_for_id = fields.Many2one('stock.picking')
    transfer_count = fields.Integer(default=0, compute='compute_transfers')
    child_mo_count = fields.Integer(default=0, compute='compute_child_mos')
    is_child_mo_created = fields.Boolean()
    show_create_in = fields.Boolean()

    def compute_child_mos(self):
        count = self.env['mrp.production'].search_count([('origin', '=', self.name)])
        self.child_mo_count = count

    def action_assign(self):
        rec = super(MrpInh, self).action_assign()
        for line in self.move_raw_ids:
            if line.forecast_availability < line.product_uom_qty:
                # bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id), ('type', '=', 'normal')])
                # if bom:
                self.show_create_in = True
        if not self.is_child_mo_created:
            self.create_child_mo()
        if self.show_create_in:
            self.action_create_internal_transfer()

    def create_child_mo(self):
        product_list = []
        bom = self.env['mrp.bom'].search([])
        for rec in bom:
            product_list.append(rec.product_tmpl_id.id)

        for line in self.move_raw_ids:
            line_vals = []
            if line.product_id.product_tmpl_id.id in product_list:
                bom_id = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)])
                print(bom_id)
                if bom_id.type == 'normal':
                    for bom_line in bom_id.bom_line_ids:
                        line_vals.append((0, 0, {
                            'product_id': bom_line.product_id.id,
                            'name': bom_line.product_id.name,
                            'location_id': line.location_id.id,
                            'location_dest_id': line.location_dest_id.id,
                            'product_uom_qty': bom_line.product_qty,
                            'product_uom': bom_line.product_uom_id.id,
                        }))
                        line_vals.append(line_vals)
                    vals = {
                        # 'picking_for_id': self.id,
                        'product_id': line.product_id.id,
                        'company_id': self.env.user.company_id.id,
                        'date_planned_start': fields.Date.today(),
                        'move_raw_ids': line_vals,
                        'location_dest_id': self.location_dest_id.id,
                        'origin': self.name,
                        'product_qty': line.product_uom_qty - line.reserved_availability,
                        'product_uom_id': line.product_id.uom_id.id,
                    }
                    mrp = self.env['mrp.production'].create(vals)
        self.is_child_mo_created = True

    def compute_transfers(self):
        count = self.env['stock.picking'].search_count([('origin', '=', self.name)])
        self.transfer_count = count

    def action_view_child_mo(self):
        return {
            'name': 'Transfers',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'domain': [('origin', '=', self.name)], }

    def action_view_transfers(self):
        return {
            'name': 'Transfers',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('origin', '=', self.name)],}

    def action_create_internal_transfer(self):
        product_list = []
        bom = self.env['mrp.bom'].search([])
        for rec in bom:
            product_list.append(rec.product_tmpl_id.id)
        picking_delivery = self.env['stock.picking.type'].search([('code', '=', 'internal')], limit=1)
        vals = {
            'location_id': self.location_dest_id.id,
            'location_dest_id': self.location_src_id.id,
            'partner_id': self.user_id.partner_id.id,
            # 'product_sub_id': self.product_subcontract_id.id,
            'picking_type_id': picking_delivery.id,
            'origin': self.name,
        }
        picking = self.env['stock.picking'].create(vals)
        for line in self.move_raw_ids:
            if line.product_id.product_tmpl_id.id not in product_list and line.forecast_availability < line.product_uom_qty:
                lines = {
                    'picking_id': picking.id,
                    'product_id': line.product_id.id,
                    'name': self.name,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': self.location_dest_id.id,
                    'location_dest_id': self.location_src_id.id,
                    'product_uom_qty': line.product_uom_qty - line.forecast_availability,
                }
                stock_move = self.env['stock.move'].create(lines)
        self.show_create_in = False
            # moves = {
            #     'move_id': stock_move.id,
            #     'product_id': line.product_id.id,
            #     'location_id': self.source_loc.id,
            #     'location_dest_id': self.source_loc.id,
            #     'product_uom_id': line.product_id.uom_id.id,
            #     'product_uom_qty': line.id,
            # }
            # stock_move_line_id = self.env['stock.move.line'].create(moves)
