# KIM-0103 Scheduler Timed Delivery Fix

Date: 2026-06-15

## Problem

Kim Live was creating and executing some scheduled actions, but timed requests that required delivery of the result were incomplete. The main action could run at the right time while the embedded delivery step stayed inert.

Observed example:

- `hostinger_mail/list_messages` ran at 08:30.
- The `follow_up_action` intended to send the result to Dr. Yehoshua by WhatsApp did not execute.
- Some generated schedules also used past `due_at` values, which made the UX confusing.

## Fix

- Added first-class `schedule_whatsapp` support.
- Added scheduled `follow_up_action` execution after the main scheduled action completes.
- Added compact result rendering before WhatsApp delivery.
- Rejected new non-recurring schedules whose due time is already in the past.
- Advanced recurring schedules to their next future occurrence when needed.

## Validation

- `SC-20260615-085939-DB3965`: scheduled WhatsApp self-test executed as `done` and queued Twilio message `SM999196601adcefa231f291fde4d2aed4`.
- `SC-20260615-090114-B583BF`: scheduled action with follow-up delivery validates the query-and-send path.

## Operating Rule

When Kim receives “haz esto a tal hora y mandamelo”, she should create a scheduler action with:

- `target_provider`
- `target_action`
- `target_parameters`
- optional `follow_up_action` for delivery, usually `twilio/send_whatsapp` to the doctor control number.
