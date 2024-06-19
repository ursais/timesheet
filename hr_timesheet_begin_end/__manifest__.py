# Copyright 2015 Camptocamp SA - Guewen Baconnier
# Copyright 2017 Tecnativa, S.L. - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Timesheet - Begin/End Hours",
    "version": "17.0.1.0.0",
    "author": "Camptocamp, Tecnativa, Odoo Community Association (OCA) - Modified by SurfThing",
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": ["hr_timesheet", "timer", "helpdesk", "helpdesk_timesheet"],
    "website": "https://github.com/OCA/timesheet",
    "data": [
        "security/ir.model.access.csv",
        "views/hr_analytic_timesheet.xml",
        "views/project_task.xml"
        "wizard/project_task_popup_timesheet_view.xml"        ],
    "installable": True,
    "auto_install": False,
}
