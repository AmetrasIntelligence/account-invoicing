from odoo import fields, models

ACCOUNT_MOVE_SORTING_DIRECTION = [
    ("asc", "Ascending"),
    ("desc", "Descending"),
]


class ResCompany(models.Model):
    _inherit = "res.company"

    default_cus_inv_line_order = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Line Order",
        help="Select a sorting criteria for customer invoice/credit note lines.",
        domain="[('model', '=', 'account.move.line')]",
    )
    default_cus_inv_line_order_2 = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Line Order 2",
        help="Select a second sorting criteria for customer invoice/credit note lines.",
        domain="[('model', '=', 'account.move.line')]",
    )
    default_cus_inv_line_direction = fields.Selection(
        selection=ACCOUNT_MOVE_SORTING_DIRECTION,
        string="Sort Direction",
        help="Select a sorting direction for customer invoice/credit note lines.",
    )

    default_vend_bill_line_order = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Line Order",
        help="Select a sorting criteria for vendor bill/refund bill lines.",
        domain="[('model', '=', 'account.move.line')]",
    )
    default_vend_bill_line_order_2 = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Line Order 2",
        help="Select a second sorting criteria for vendor bill/refund bill lines.",
        domain="[('model', '=', 'account.move.line')]",
    )
    default_vend_bill_line_direction = fields.Selection(
        selection=ACCOUNT_MOVE_SORTING_DIRECTION,
        string="Sort Direction",
        help="Select a sorting direction for vendor bill/refund bill lines.",
    )
