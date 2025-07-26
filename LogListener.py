import subprocess
import os
import sys
import argparse
import time
from datetime import datetime
import logging
import io

def setup_logger(log_file):
    """Configures the logger to write to a specified file."""
    logger = logging.getLogger("AlertMonitor")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def send_email_alert(subject, body, recipient_email, logger):
    """Sends an email alert using the system's 'sendmail' command."""
    try:
        sendmail_location = "/usr/sbin/sendmail"
        if not os.path.exists(sendmail_location):
            logger.error(f"sendmail not found at {sendmail_location}. Cannot send email.")
            return
        p = subprocess.Popen([sendmail_location, "-t", "-oi"], stdin=subprocess.PIPE)
        message = f"To: {recipient_email}\nSubject: {subject}\n\n{body}"
        p.communicate(message.encode('utf-8'))
        logger.info(f"Successfully sent alert to {recipient_email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

def follow_file(log_file, keywords, recipient_email, logger, duration_minutes, no_email_flag):
    """Opens a file and continuously yields new lines until duration is met."""
    start_time = time.time()
    duration_seconds = duration_minutes * 60 if duration_minutes > 0 else 0

    log_file.seek(0, os.SEEK_END)
    while True:
        line = log_file.readline()
        if not line:
            time.sleep(1) # Wait for new content
        else:
            line_lower = line.lower()
            for keyword in keywords:
                if keyword in line_lower:
                    # --- NEW LOGIC HERE ---
                    if no_email_flag:
                        # If --no-email is used, just write the alert to the log file
                        logger.warning(f"Keyword '{keyword}' found in alert log: {line.strip()}")
                    else:
                        # Otherwise, send the email as before
                        logger.info(f"Found keyword '{keyword}'! Sending alert...")
                        hostname = os.uname().nodename
                        subject = f"Oracle Alert on {hostname}: Found keyword '{keyword}'"
                        body = f"Alert triggered at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        body += f"Host: {hostname}\nLog File: {args.logfile}\n\n{line}"
                        send_email_alert(subject, body, recipient_email, logger)
                    break

        if duration_seconds > 0 and (time.time() - start_time) > duration_seconds:
            logger.info(f"Runtime limit of {duration_minutes} minutes reached. Shutting down.")
            break

def main():
    parser = argparse.ArgumentParser(description="Continuously monitor an Oracle alert log.")
    parser.add_argument("--logfile", required=True, help="Full path to the alert log file to monitor.")
    parser.add_argument("--keywords", required=True, help="Comma-separated list of keywords.")
    parser.add_argument("--email", help="Email address to send alerts to. Required unless --no-email is used.")
    parser.add_argument("--output-log", default="/tmp/oracle_alert_monitor.log", help="Path for the monitor's own log file.")
    parser.add_argument("--duration", type=int, default=0, help="Optional runtime limit in minutes. Runs forever if 0.")
    parser.add_argument("--no-email", action="store_true", help="Disable email alerts and log to the output file instead.")

    global args
    args = parser.parse_args()

    # Validate that an email is provided if email is not disabled
    if not args.no_email and not args.email:
        parser.error("--email is required unless --no-email is specified.")

    logger = setup_logger(args.output_log)
    keywords = [k.strip().lower() for k in args.keywords.split(',')]

    if not os.path.exists(args.logfile):
        logger.error(f"Alert log file not found at '{args.logfile}'. Exiting.")
        sys.exit(1)

    logger.info(f"Starting to monitor '{args.logfile}' for keywords: {keywords}")
    if args.duration > 0:
        logger.info(f"Script will automatically stop after {args.duration} minutes.")
    if args.no_email:
        logger.info("Email alerts are DISABLED. Found keywords will be logged here as warnings.")

    with open(args.logfile, 'r', errors='ignore') as f:
        follow_file(f, keywords, args.email, logger, args.duration, args.no_email)

    logger.info("Monitoring stopped.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")