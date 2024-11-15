# Copyright 2015 Camptocamp SA - Guewen Baconnier
# Copyright 2017 Tecnativa, S.L. - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime, timedelta
from odoo.tools import pytz

from odoo import _, api, exceptions, fields, models
from odoo.tools.float_utils import float_compare



class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    _order = "date desc, time_start desc, id desc"

    time_start = fields.Datetime(string="Begin Hour")
    time_stop = fields.Datetime(string="End Hour")

    @api.constrains("time_start", "time_stop", "unit_amount")
    def _check_time_start_stop(self):
        for line in self:
            if line.time_stop and line.time_start:
                if line.time_stop < line.time_start:
                    raise exceptions.ValidationError(_("Start time must be before end time."))
            
                if line.is_timesheet:
                    if line.unit_amount:
                        hours = (line.time_stop - line.time_start).total_seconds() / 3600
                        rounding = self.env.ref("uom.product_uom_hour").rounding
                        if hours and float_compare(hours, line.unit_amount, precision_rounding=rounding):
                            # raise exceptions.ValidationError(
                            # _("The duration (" + str(line.unit_amount) + ") 
                            # must be equal to the difference between the start 
                            # (" + str(line.time_start) + ") and end time 
                            # (" + str(line.time_stop) + ") " + str(hours) + "."))
                            raise exceptions.ValidationError(
                                _("The duration does not line up with start and end times.")
                            )
                    else:
                        hours = (line.time_stop - line.time_start).total_seconds() / 3600
                        line.unit_amount = float(hours)
            else:
                minutes_spent = timedelta(minutes=line.unit_amount).total_seconds()
                minimum_duration = int(self.env['ir.config_parameter'].sudo().get_param('timesheet_grid.timesheet_min_duration', 0))
                rounding = self.env.ref("uom.product_uom_hour").rounding
                minutes_spent = self._timer_rounding(minutes_spent, minimum_duration, rounding)

                user = self.env['res.users'].browse([2])
                tz = pytz.timezone(user.tz) or pytz.utc
                
                if line.time_start and line.unit_amount and not line.time_stop:
                    line.time_stop = line.time_start + timedelta(minutes = int(minutes_spent))
                    user_tz_date = pytz.utc.localize(line.time_start).astimezone(tz)
                    line.date = datetime.date(user_tz_date)


                if line.time_stop and line.unit_amount and not line.time_start:
                    line.time_start = line.time_stop - timedelta(minutes = int(minutes_spent))
                    user_tz_date = pytz.utc.localize(line.time_start).astimezone(tz)
                    line.date = datetime.date(user_tz_date)


                if not line.time_start and not line.time_stop and line.unit_amount:
                    line.time_stop = datetime.now()
                    line.time_start = line.time_stop - timedelta(minutes = int(minutes_spent))
                else:
                    emptycount = 0
                    if not line.time_start:
                        emptycount += 1
                    if not line.time_stop:
                        emptycount += 1
                    if not line.unit_amount:
                        emptycount += 1
                    if emptycount >= 2:
                        raise exceptions.ValidationError(
                            _("There are not enough details to calculate start time, end time, and duration.")
                        )


    def button_calculate(self):
        # raise exceptions.ValidationError(_("You clicked the calculate button."))
        return True


    def merge_timesheets(self):  # pragma: no cover
        """This method is needed in case hr_timesheet_sheet is installed"""
        lines = self.filtered(lambda line: not line.time_start and not line.time_stop)
        if lines:
            return super(AccountAnalyticLine, lines).merge_timesheets()
        return self[0]
