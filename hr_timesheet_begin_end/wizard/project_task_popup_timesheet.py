from datetime import timedelta
from datetime import datetime

from odoo import _, api, exceptions, fields, models
from odoo.tools.float_utils import float_compare
from odoo.tools import pytz


class HelpdeskTicketCreateTimesheetExt(models.TransientModel):
    _name = 'helpdesk.ticket.popup.timesheet'
    _description = "Create Timesheet from ticket popup"

    wiz_time_start = fields.Datetime(string="Start Time")
    wiz_time_stop = fields.Datetime(string="End Time")
    

    time_spent = fields.Float('Time')
    description = fields.Char('Description')
    ticket_id = fields.Many2one(
        'helpdesk.ticket', "Ticket", required=True,
        default=lambda self: self.env.context.get('active_id', None),
        help="Ticket for which we are creating a timer",
    )

        
    def action_generate_timesheet(self):
        
        user = self.env['res.users'].browse([2])
        tz = pytz.timezone(user.tz) or pytz.utc
        user_tz_date = pytz.utc.localize(fields.Datetime.now()).astimezone(tz)

        values = {
            'project_id': self.ticket_id.project_id.id,
            'date': user_tz_date,
            'name': self.description,
            'user_id': self.env.uid,
            'unit_amount': self.time_spent,
            'time_start': self.wiz_time_start,
            'time_stop': self.wiz_time_stop
        }

        timesheet = self.env['account.analytic.line'].create(values)

        self.ticket_id.write({
            'timer_start': False,
            'timer_pause': False
        })
        self.ticket_id.timesheet_ids = [(4, timesheet.id, None)]
        self.ticket_id.user_timer_id.unlink()
        return timesheet

    def action_delete_timesheet(self):
         self.ticket_id.user_timer_id.unlink()
