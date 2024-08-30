from datetime import timedelta
from datetime import datetime, timezone

from odoo import _, api, exceptions, fields, models
from odoo.tools.float_utils import float_compare



class HelpDeskStartStopTimes(models.Model):
    _inherit = "helpdesk.ticket"
    
    def action_timer_stop(self):
        #Do the original thing
        #res = super(ChrisTesting, self).action_timer_stop()
        # timer was either running or paused
        if self.user_timer_id.timer_start and self.display_timesheet_timer:
            minutes_spent = self.user_timer_id._get_minutes_spent()
            minimum_duration = int(self.env['ir.config_parameter'].sudo().get_param('timesheet_grid.timesheet_min_duration', 0))
            rounding = int(self.env['ir.config_parameter'].sudo().get_param('timesheet_grid.timesheet_rounding', 0))
            minutes_spent = self._timer_rounding(minutes_spent, minimum_duration, rounding)

            return self._action_open_new_timesheet2(minutes_spent * 60 / 3600, minutes_spent)
        return False

    def _action_open_new_timesheet2(self, time_spent, minutes_spent):

        wiz_server_time = datetime.now(timezone.utc)
        calculated_start_time = wiz_server_time - timedelta(minutes = int(minutes_spent))

        return {
            "name": _("Confirm Time Spent"),
            "type": 'ir.actions.act_window',
            "res_model": 'helpdesk.ticket.popup.timesheet',
            "views": [[False, "form"]],
            "target": 'new',
            "context": {
                **self.env.context,
                'active_id': self.id,
                'active_model': self._name,
                'default_time_spent': time_spent,
                'default_wiz_time_start': calculated_start_time,
                'default_wiz_time_stop': wiz_server_time,
                'dialog_size': 'medium',
            },
        }
