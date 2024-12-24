import smtplib
import dns.resolver
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor

def install_module(module_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
    except Exception as e:
        print(f"Failed to install module {module_name}: {e}")

# Ensure required modules are installed
install_module("dnspython")

def check_email(email):
    domain = email.split('@')[-1]

    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_record = mx_records[0].exchange.to_text()

        server = smtplib.SMTP()
        server.connect(mx_record)

        server.helo()
        server.mail('test@example.com')
        code, message = server.rcpt(email)
        server.quit()

        if code == 250:
            return True
        else:
            return False
    except ImportError:
        print("The dns module is missing. Please install it by running: pip install dnspython")
        return False
    except Exception as e:
        print(f"Error checking {email}: {e}")
        return False

def validate_email_threaded(email):
    print(f"Checking: {email}")  # Debugging statement
    if check_email(email):
        print(f"\033[92mValid: {email}\033[0m")
        return email, None
    else:
        print(f"\033[91mInvalid: {email}\033[0m")
        return None, email

def validate_emails(email_list):
    valid_emails = []
    invalid_emails = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(validate_email_threaded, email_list))
    for valid, invalid in results:
        if valid:
            valid_emails.append(valid)
        if invalid:
            invalid_emails.append(invalid)
    return valid_emails, invalid_emails

if __name__ == "__main__":
    print("Starting email validation script...")  # Debugging statement
    if len(sys.argv) != 2:
        print("Usage:")
        print("Single email check: python3 a.py <email_address>")
        print("List check: python3 a.py <file_name>")
    else:
        input_arg = sys.argv[1]
        print(f"Input argument received: {input_arg}")  # Debugging statement
        if input_arg.endswith(".txt"):
            try:
                with open(input_arg, 'r') as file:
                    email_list = [line.strip() for line in file.readlines()]
                    print(f"Loaded {len(email_list)} emails from file")  # Debugging statement
                valid_emails, invalid_emails = validate_emails(email_list)
                print("\nValid Email Addresses:")
                for email in valid_emails:
                    print(f"\033[92m{email}\033[0m")
                print("\nInvalid Email Addresses:")
                for email in invalid_emails:
                    print(f"\033[91m{email}\033[0m")
            except FileNotFoundError:
                print(f"Error: {input_arg} file not found.")
        else:
            email = input_arg
            if check_email(email):
                print(f"\033[92mEmail is valid: {email}\033[0m")
            else:
                print(f"\033[91mEmail is invalid: {email}\033[0m")

