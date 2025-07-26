This lightweight Python script helps monitor Oracle alert logs in real-time — perfect for tracking intermittent or random issues that are otherwise hard to detect.

Some of the hardest problems to solve are the ones that happen randomly or occasionally.

These types of issues are not only difficult to track but sometimes require immediate action or analysis while they’re happening.

That’s exactly what this script is for.  
- If you have `root` access, you can run it as a service.  
- Otherwise, run it using `nohup`, or limit its runtime with a specific duration.

It will continuously watch an Oracle alert log for specific keywords (like `ORA-`), save any matches to a log file, and optionally send email alerts.


`nohup python3.6 tail_alert_log.py --logfile /path/to/alert.log --keywords "ORA-" --no-email --duration 60 &` 

This runs the script in the background for 1 hour, logs matches to /tmp/oracle_alert_monitor.log, and does not send emails.



| Option         | Description                                                                 |
| -------------- | --------------------------------------------------------------------------- |
| `--logfile`    | Full path to the Oracle alert log file you want to monitor. **(Required)**  |
| `--keywords`   | Comma-separated list of keywords to search for. **(Required)**              |
| `--email`      | Email address to send alerts to (if `--no-email` is not used).              |
| `--no-email`   | Disable email alerts. Matches will only be written to the output log.       |
| `--output-log` | Path to the script’s own log file. Default: `/tmp/oracle_alert_monitor.log` |
| `--duration`   | Runtime in **minutes**. Use `0` to keep it running continuously.            |
