# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class StockMoveInh(models.Model):
    _inherit = 'stock.move'

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.picking_id.state == 'draft' and self.picking_id.picking_type_id.code == 'incoming':
            raise UserError('You cannot add Product in this state')


# class StockMoveLineInh(models.Model):
#     _inherit = 'stock.move.line'
#
#     @api.onchange('product_id')
#     def onchange_product_id(self):
#         if self.picking_id.state == 'draft' and self.picking_id.picking_type_id.code == 'incoming':
#             raise UserError('You cannot add Product in this Stage')


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('qc_inspection', 'QC Inspection'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")

    document_1 = fields.Boolean()
    document_2 = fields.Boolean()
    document_3 = fields.Boolean()
    is_receipt = fields.Boolean()



    def action_ready(self):
        print(self.check_ids[0].name)
        for rec in self.check_ids:
            if rec.quality_state != 'pass':
                raise UserError('Quality Checks Are not Passed.')
        record = super(StockPickingInh, self).action_assign()
        return record

    def action_qc_confirm(self):
        if self.document_1 and self.document_2 and self.document_3:
            self.state = 'qc_inspection'
        else:
            raise UserError('All documents should be checked to CONFIRM."')


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    def button_approved(self):
        record = super(PurchaseOrderInh, self).button_approved()
        for order in self:
            for picking in order.picking_ids:
                picking.do_unreserve()
                picking.is_receipt = True
        return record

