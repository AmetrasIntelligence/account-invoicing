from odoo import models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def _prepare_default_reversal(self, move):
        res = super(AccountMoveReversal, self)._prepare_default_reversal(move)
        if move.move_type in ("out_invoice", "out_refund"):
            default_cus_inv_line_order = move.company_id.default_cus_inv_line_order
            default_cus_inv_line_order_2 = move.company_id.default_cus_inv_line_order_2
            default_cus_inv_line_direction = (
                move.company_id.default_cus_inv_line_direction or False
            )
            res.update(
                {
                    "cus_inv_line_order": default_cus_inv_line_order
                    and default_cus_inv_line_order.id
                    or False,
                    "cus_inv_line_order_2": default_cus_inv_line_order_2
                    and default_cus_inv_line_order_2.id
                    or False,
                    "cus_inv_line_direction": default_cus_inv_line_direction,
                }
            )
        elif move.move_type in ("in_invoice", "in_refund"):
            default_vend_bill_line_order = move.company_id.default_vend_bill_line_order
            default_vend_bill_line_order_2 = (
                move.company_id.default_vend_bill_line_order_2
            )
            default_vend_bill_line_direction = (
                move.company_id.default_vend_bill_line_direction or False
            )
            res.update(
                {
                    "vend_bill_line_order": default_vend_bill_line_order
                    and default_vend_bill_line_order.id
                    or False,
                    "vend_bill_line_order_2": default_vend_bill_line_order_2
                    and default_vend_bill_line_order_2.id
                    or False,
                    "vend_bill_line_direction": default_vend_bill_line_direction,
                }
            )

        return res
