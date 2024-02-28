import logging

from natsort import natsort_keygen, ns

from odoo import _, api, fields, models

from .res_company import ACCOUNT_MOVE_SORTING_DIRECTION
from .shared import resolve_account_move_line_subfields

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    cus_inv_line_order = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Sort Lines By",
        domain="[('model', '=', 'account.move.line')]",
        default=lambda self: self.env.user.company_id.default_cus_inv_line_order,
    )
    cus_inv_line_order_2 = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Sort Lines By",
        domain="[('model', '=', 'account.move.line')]",
        default=lambda self: self.env.user.company_id.default_cus_inv_line_order_2,
    )
    cus_inv_line_direction = fields.Selection(
        selection=ACCOUNT_MOVE_SORTING_DIRECTION,
        string="Sort Direction",
        default=lambda self: self.env.user.company_id.default_cus_inv_line_direction,
    )

    vend_bill_line_order = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Sort Lines By",
        domain="[('model', '=', 'account.move.line')]",
        default=lambda self: self.env.user.company_id.default_vend_bill_line_order,
    )
    vend_bill_line_order_2 = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Sort Lines By",
        domain="[('model', '=', 'account.move.line')]",
        default=lambda self: self.env.user.company_id.default_vend_bill_line_order_2,
    )
    vend_bill_line_direction = fields.Selection(
        selection=ACCOUNT_MOVE_SORTING_DIRECTION,
        string="Sort Direction",
        default=lambda self: self.env.user.company_id.default_vend_bill_line_direction,
    )

    @api.onchange("cus_inv_line_order", "cus_inv_line_order_2")
    def onchange_cus_inv_line_order(self):
        if not self.cus_inv_line_order and not self.cus_inv_line_order_2:
            self.cus_inv_line_direction = False

    @api.onchange("vend_bill_line_order", "vend_bill_line_order_2")
    def onchange_vend_bill_line_order(self):
        if not self.vend_bill_line_order and not self.vend_bill_line_order_2:
            self.vend_bill_line_direction = False

    def get_sorted_aml_lines(
        self, inv_line_ids, sorting_key, sort_param_1, sort_param_2, reverse
    ):
        """Return Sorted Account Move Lines Based on the Parameters and Key"""
        return inv_line_ids.sorted(
            key=lambda p: (
                sorting_key(resolve_account_move_line_subfields(p, sort_param_1)),
                sorting_key(resolve_account_move_line_subfields(p, sort_param_2)),
            ),
            reverse=reverse,
        )

    def get_move_line_section_product_data(self, invoice_line_ids):
        """Fetch the lines under each section as a dict form"""
        move_line_section_dict = {}
        list_lines_under_section = []
        section_list = []
        for inv_line in invoice_line_ids.sorted(
            key=lambda l: (
                l.sequence,
                l.id,
            ),
            reverse=True,
        ):
            if inv_line.display_type != "line_section":
                list_lines_under_section.append(inv_line.id)
            else:
                section_list.append(inv_line.id)

                move_line_section_dict.update(
                    dict(
                        zip(
                            list_lines_under_section,
                            section_list * len(list_lines_under_section),
                        )
                    )
                )
                section_list = []
                list_lines_under_section = []
        return move_line_section_dict

    def split_section_subline_and_without_section_line(
        self, sorted_lines, move_line_section_dict, sort_param1, sort_param2
    ):
        """Fetch the lines having section and without
        section from the sorted move lines"""
        sorted_section_lines = self.env["account.move.line"]
        sorted_lines_without_section = self.env["account.move.line"]
        section_list = list(move_line_section_dict.values())
        lines_under_section_list = list(move_line_section_dict.keys())
        acct_move_line_obj = self.env["account.move.line"]

        # Section values are stored in the name field,
        # so consider the section lines also for sorting

        if sort_param1.name == "name":
            sorted_section_lines = sorted_lines.filtered(
                lambda ml: ml.id in section_list
            )
        if sorted_section_lines:
            sorted_lines = sorted_lines.filtered(
                lambda ml: (ml.id not in sorted_section_lines.ids)
                or (ml.id not in lines_under_section_list)
            )

        for spl in sorted_lines:
            if spl.display_type == "line_section" and spl.id not in section_list:
                sorted_lines_without_section += spl
            else:
                linked_section_line = move_line_section_dict.get(spl.id, False)
                if linked_section_line:
                    linked_section_line = acct_move_line_obj.browse(linked_section_line)
                    if linked_section_line.id not in sorted_section_lines.ids:
                        sorted_section_lines += linked_section_line

                elif spl.display_type != "line_section":
                    sorted_lines_without_section += spl
        return sorted_section_lines, sorted_lines_without_section

    def update_seq_sorted_section_note_product_lines(
        self,
        sorted_lines,
        sorted_section_lines,
        sorted_lines_without_section,
        move_line_section_dict,
        sequence,
    ):

        if sorted_section_lines or sorted_lines_without_section:

            for line_id in sorted_lines.filtered(
                lambda sl: sl.id in sorted_lines_without_section.ids
            ):
                sequence += 10
                if line_id.sequence == sequence:
                    continue

                line_id.with_context(check_move_validity=False).write(
                    {"sequence": sequence}
                )

            for sn_line in sorted_section_lines:
                sequence += 10
                if sn_line.sequence != sequence:
                    sn_line.with_context(check_move_validity=False).write(
                        {"sequence": sequence}
                    )

                for line in sorted_lines.filtered(
                    lambda sl: sl.id
                    in list(
                        filter(
                            lambda x: move_line_section_dict[x] == sn_line.id,
                            move_line_section_dict,
                        )
                    )
                ):
                    sequence += 10
                    if line.sequence == sequence:
                        continue
                    line.with_context(check_move_validity=False).write(
                        {"sequence": sequence}
                    )

    def update_seq_sorted_without_section_lines(self, sorted_lines, sequence):
        for line in sorted_lines:
            sequence += 10
            if line.sequence == sequence:
                continue
            line.with_context(check_move_validity=False).write({"sequence": sequence})

    def failed_sort_message_info(self):
        if self.move_type == "out_invoice":
            return _("Customer Invoice")
        elif self.move_type == "out_refund":
            return _("Credit Note")
        elif self.move_type == "in_invoice":
            return _("Vendor Bill")
        else:
            return _("Refund Bill")

    def perform_account_move_line_sort(self):
        for move in self:
            sort_param1 = (
                move.cus_inv_line_order
                if move.move_type in ("out_invoice", "out_refund")
                else move.vend_bill_line_order
            )
            sort_param2 = (
                move.cus_inv_line_order_2
                if move.move_type in ("out_invoice", "out_refund")
                else move.vend_bill_line_order_2
            )
            sort_direction = (
                move.cus_inv_line_direction
                if move.move_type in ("out_invoice", "out_refund")
                else move.vend_bill_line_direction
            )

            if not sort_param1 and not sort_param2 and not sort_direction:
                continue

            reverse = sort_direction == "desc"
            sequence = 0
            try:
                current_invoice_line_ids = move.invoice_line_ids
                move_line_section_dict = move.get_move_line_section_product_data(
                    current_invoice_line_ids
                )
                sorting_key = natsort_keygen(alg=ns.REAL | ns.IGNORECASE)
                if current_invoice_line_ids.filtered(lambda sn: sn.display_type):

                    sorted_lines = move.get_sorted_aml_lines(
                        current_invoice_line_ids,
                        sorting_key,
                        sort_param1,
                        sort_param2,
                        reverse,
                    )

                    (
                        sorted_section_lines,
                        sorted_lines_without_section,
                    ) = move.split_section_subline_and_without_section_line(
                        sorted_lines,
                        move_line_section_dict,
                        sort_param1,
                        sort_param2,
                    )

                    if sorted_section_lines or sorted_lines_without_section:
                        move.update_seq_sorted_section_note_product_lines(
                            sorted_lines,
                            sorted_section_lines,
                            sorted_lines_without_section,
                            move_line_section_dict,
                            sequence,
                        )

                else:
                    sorted_lines = move.get_sorted_aml_lines(
                        current_invoice_line_ids,
                        sorting_key,
                        sort_param1,
                        sort_param2,
                        reverse,
                    )
                    move.update_seq_sorted_without_section_lines(sorted_lines, sequence)

            except Exception:
                message = move.failed_sort_message_info()
                _logger.warning("Could not sort %s !" % (message), exc_info=True)

    def write(self, values):
        res = super().write(values)

        if (
            "line_ids" in values
            or "invoice_line_ids" in values
            or "cus_inv_line_order" in values
            or "cus_inv_line_order_2" in values
            or "cus_inv_line_direction" in values
            or "vend_bill_line_order" in values
            or "vend_bill_line_order_2" in values
            or "vend_bill_line_direction" in values
        ):
            self.filtered(
                lambda m: m.move_type
                in ("out_invoice", "out_refund", "in_invoice", "in_refund")
            ).perform_account_move_line_sort()
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.filtered(
            lambda m: m.move_id
            and m.move_id.move_type
            in ("out_invoice", "out_refund", "in_invoice", "in_refund")
        ).mapped("move_id").perform_account_move_line_sort()
        return lines
