from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cus_inv_line_order_default = fields.Many2one(
        related="company_id.default_cus_inv_line_order",
        string="Line Order 1",
        readonly=False,
    )
    cus_inv_line_order_2_default = fields.Many2one(
        related="company_id.default_cus_inv_line_order_2",
        string="Line Order 2",
        readonly=False,
    )
    cus_inv_line_direction_default = fields.Selection(
        related="company_id.default_cus_inv_line_direction",
        string="Sort Direction",
        readonly=False,
    )

    vend_bill_line_order_default = fields.Many2one(
        related="company_id.default_vend_bill_line_order",
        string="Line Order 1",
        readonly=False,
    )
    vend_bill_line_order_2_default = fields.Many2one(
        related="company_id.default_vend_bill_line_order_2",
        string="Line Order 2",
        readonly=False,
    )
    vend_bill_line_direction_default = fields.Selection(
        related="company_id.default_vend_bill_line_direction",
        string="Sort Direction",
        readonly=False,
    )

    @api.onchange("cus_inv_line_order_default", "cus_inv_line_order_2_default")
    def onchange_cus_inv__line_order_default(self):
        """Reset direction line order when user
        remove order field value-customer invoice/credit note"""
        if (
            not self.cus_inv_line_order_default
            and not self.cus_inv_line_order_2_default
        ):
            self.cus_inv_line_direction_default = False

    @api.onchange("vend_bill_line_order_default", "vend_bill_line_order_2_default")
    def onchange_vend_bill_line_order_default(self):
        """Reset direction line order when user
        remove order field value-vendor bill/refund bill"""
        if (
            not self.vend_bill_line_order_default
            and not self.vend_bill_line_order_2_default
        ):
            self.vend_bill_line_direction_default = False
